"""乐天快递单生成服务（P1）。

从 `rakuten-shipping/{rakuten_delivery_dtl.py, merge_tool.py}` 移植为 IO 干净的服务：
- 输入：RMS 订单明细 CSV 的字节流（cp932）
- 输出：3 家快递上传 CSV（cp932 字节）+ 未解析行 + `mgmt_no → [注文番号…]` 映射

改造（相对原工具）：
1. 不再读写 `data/` 硬编码路径、不再把 err 追加到磁盘——全部在内存里返回。
2. **mgmt_no 桥**：携带 `注文番号`，合单时给每张运单分配 mgmt_no，注入 Sagawa
   `お客様管理番号` / Yamato `検索キー1`，并返回 `mgmt_no → [注文番号…]` 映射，
   供第4步「発送完了報告データ」回填（一张运单可对应同客户多张订单）。

JAN 解析复用 `app/common/jan_resolver.resolve_jan_quantities`（勿重写，规则见 JAN_QUANTITY_SPEC.md）。
"""
from __future__ import annotations

import csv
import io
import json
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from app.common.jan_resolver import resolve_jan_quantities

_ASSETS = Path(__file__).parent / "rakuten_assets"
_PRODUCT_DICT_PATH = Path(__file__).parent.parent / "common" / "product_dict.json"

with open(_ASSETS / "dict_cmpny.json", encoding="utf-8") as _f:
    SHIPPING_MAP: dict[str, str] = json.load(_f)

# 读入所需列（注文番号/ステータス 为桥新增；其余同原工具）
_STR_COLS = [
    "注文番号", "送付先ID", "商品番号", "システム連携用SKU番号",
    "送付先郵便番号1", "送付先郵便番号2",
    "送付先電話番号1", "送付先電話番号2", "送付先電話番号3",
]
COLUMNS_NEEDED = [
    "注文番号", "送付先ID", "ステータス",
    "送付先郵便番号1", "送付先郵便番号2",
    "送付先住所都道府県", "送付先住所郡市区", "送付先住所それ以降の住所",
    "送付先姓", "送付先名",
    "送付先電話番号1", "送付先電話番号2", "送付先電話番号3",
    "お届け日指定", "商品番号", "システム連携用SKU番号", "個数", "配送方法",
]


def _load_product_dict() -> dict:
    try:
        with open(_PRODUCT_DICT_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        return {k: v for k, v in raw.items() if not str(k).startswith("_") and v}
    except FileNotFoundError:
        return {}


# ── 字段合并（纯函数，移植自 merge_tool）────────────────────────────────────
def _clean(v) -> str:
    return str(v).replace(".0", "").replace("nan", "").strip() if pd.notna(v) else ""


def _merge_zip(row) -> str:
    p1, p2 = _clean(row["送付先郵便番号1"]), _clean(row["送付先郵便番号2"])
    if not p1 and not p2:
        return ""
    return p1.zfill(3) + p2.zfill(4)


def _merge_phone(row) -> str:
    t1, t2, t3 = _clean(row["送付先電話番号1"]), _clean(row["送付先電話番号2"]), _clean(row["送付先電話番号3"])
    if not t1 and not t2 and not t3:
        return ""
    if t1 and not t1.startswith("0"):
        t1 = "0" + t1
    if t3:
        t3 = t3.zfill(4)
    return t1 + t2 + t3


def _merge_name(row) -> str:
    return _clean(row["送付先姓"]) + _clean(row["送付先名"])


def _merge_address(row) -> str:
    return _clean(row["送付先住所都道府県"]) + _clean(row["送付先住所郡市区"]) + _clean(row["送付先住所それ以降の住所"])


def _merge_products(row, product_dict, err_rows: list) -> list[str]:
    """返回 ['JAN-数量', ...]；套装多元素；无法解析记入 err_rows 并返回 ['']。"""
    p2 = _clean(row["商品番号"])
    sys_sku = _clean(row.get("システム連携用SKU番号", ""))
    try:
        order_count = int(float(row["個数"]))
    except (ValueError, TypeError):
        order_count = 1
    if not p2:
        return [""]
    results = resolve_jan_quantities(p2, sys_sku, order_count, product_dict)
    if results:
        return [f"{jan}-{qty}" for jan, qty in results]
    err_rows.append({"收件人": _merge_name(row), "电话": _merge_phone(row), "原品名2": p2})
    return [""]


# ── 合单 + mgmt_no 注入 ──────────────────────────────────────────────────────
def _consolidate_with_mgmt(
    df_export: pd.DataFrame,
    keys_df: pd.DataFrame,
    *,
    name_col: str,
    product_cols: list[str],
    chunk_size: int,
    ref_col: str,
    mgmt_prefix: str,
    mapping: dict[str, list[dict]],
) -> pd.DataFrame:
    """按 (姓名, 邮编, 电话) 合单，商品分块到 product_cols；每组分配 mgmt_no 注入 ref_col，
    并把该组的 (注文番号, 送付先ID) 汇总进 mapping[mgmt_no]（第4步 発送完了報告 要 送付先ID 才是更新而非新增）。"""
    df = df_export.copy()
    df["_order"] = keys_df["注文番号"].values
    df["_dest"] = keys_df["送付先ID"].values
    df["_prod"] = df[product_cols[0]].copy()
    df["_kn"] = df[name_col].fillna("UNKNOWN_NAME")
    df["_kz"] = df["お届け先郵便番号"].fillna("UNKNOWN_ZIP")
    df["_kp"] = df["お届け先電話番号"].fillna("UNKNOWN_PHONE")

    new_rows: list = []
    seq = 0
    for _, group in df.groupby(["_kn", "_kz", "_kp"], sort=False):
        products = [p for p in group["_prod"].tolist() if p != ""]
        chunks = [products[i:i + chunk_size] for i in range(0, len(products), chunk_size)] or [[]]
        pairs = {(str(o), str(d)) for o, d in zip(group["_order"].tolist(), group["_dest"].tolist()) if o and str(o) != "nan"}
        seq += 1
        mgmt_no = f"{mgmt_prefix}{seq:04d}"
        if pairs:
            mapping[mgmt_no] = [{"注文番号": o, "送付先ID": d} for o, d in sorted(pairs)]
        template_row = group.iloc[0].copy()
        for chunk in chunks:
            new_row = template_row.copy()
            for i, col in enumerate(product_cols):
                new_row[col] = chunk[i] if i < len(chunk) else ""
            new_row[ref_col] = mgmt_no
            new_rows.append(new_row)

    out = pd.DataFrame(new_rows) if new_rows else df.copy()
    return out.drop(columns=["_order", "_dest", "_prod", "_kn", "_kz", "_kp"], errors="ignore")


def _to_cp932_csv(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    text = df.to_csv(index=False)
    buf.write(text.encode("cp932", errors="replace"))
    return buf.getvalue()


@dataclass
class RakutenLabelResult:
    store: str
    files: dict[str, bytes] = field(default_factory=dict)      # courier -> cp932 CSV bytes
    counts: dict[str, int] = field(default_factory=dict)       # courier -> row count
    err_rows: list[dict] = field(default_factory=list)         # 未解析商品行
    mapping: dict[str, list[dict]] = field(default_factory=dict)  # mgmt_no -> [{注文番号, 送付先ID}…]


# ── 主入口 ──────────────────────────────────────────────────────────────────
def generate_courier_files(csv_bytes: bytes, store: str = "1") -> RakutenLabelResult:
    product_dict = _load_product_dict()
    err_rows: list[dict] = []
    mapping: dict[str, list[dict]] = {}
    result = RakutenLabelResult(store=store)

    dtype = {c: str for c in _STR_COLS}
    df = pd.read_csv(io.BytesIO(csv_bytes), dtype=dtype, encoding="cp932",
                     usecols=COLUMNS_NEEDED, encoding_errors="replace")
    df["快递公司"] = df["配送方法"].map(SHIPPING_MAP)
    df["お届け日指定"] = pd.to_datetime(df["お届け日指定"], errors="coerce").dt.strftime("%Y/%m/%d")

    # ---- Sagawa ----
    d = df[df["快递公司"] == "sagawa"].copy()
    if not d.empty:
        d["_zip"] = d.apply(_merge_zip, axis=1)
        d["_tel"] = d.apply(_merge_phone, axis=1)
        d["_name"] = d.apply(_merge_name, axis=1)
        d["商品内容"] = d.apply(lambda r: _merge_products(r, product_dict, err_rows), axis=1)
        d = d.explode("商品内容").reset_index(drop=True)
        d = d[d["商品内容"] != ""].reset_index(drop=True)
    cols = pd.read_csv(_ASSETS / "sagawa_columns.csv", nrows=0, encoding="cp932").columns.str.strip().tolist()
    exp = pd.DataFrame(columns=cols)
    if not d.empty:
        exp["お届け先電話番号"] = d["_tel"]
        exp["お届け先郵便番号"] = d["_zip"]
        exp["TranBinh"] = d["_name"]
        exp["お届け先住所１"] = d["送付先住所都道府県"]
        exp["お届け先住所２"] = d["送付先住所郡市区"]
        exp["お届け先住所３"] = d["送付先住所それ以降の住所"].fillna("")
        exp["品名２"] = d["商品内容"]
        exp["配達日"] = d["お届け日指定"]
        exp["お客様コード"] = "152482790007"
        exp["ご依頼主電話番号"] = "06-4963-3212"
        exp["ご依頼主郵便番号"] = "557-0061"
        exp["ご依頼主住所１"] = "大阪府大阪市西成区"
        exp["ご依頼主名称１"] = "JINFU株式会社"
        exp["出荷個数"] = 1
        exp = _consolidate_with_mgmt(
            exp, d[["注文番号", "送付先ID"]], name_col="TranBinh",
            product_cols=["品名２", "品名３", "品名４", "品名５"], chunk_size=4,
            ref_col="お客様管理番号", mgmt_prefix=f"{store}S", mapping=mapping,
        )
        exp = exp.sort_values(by="品名２")
    result.files["sagawa"] = _to_cp932_csv(exp)
    result.counts["sagawa"] = len(exp) if not d.empty else 0

    # ---- Yamato ----
    d = df[df["快递公司"] == "yamato"].copy()
    if not d.empty:
        d["_zip"] = d.apply(_merge_zip, axis=1)
        d["_tel"] = d.apply(_merge_phone, axis=1)
        d["_name"] = d.apply(_merge_name, axis=1)
        d["_addr"] = d.apply(_merge_address, axis=1)
        d["商品内容"] = d.apply(lambda r: _merge_products(r, product_dict, err_rows), axis=1)
        d = d.explode("商品内容").reset_index(drop=True)
        d = d[d["商品内容"] != ""].reset_index(drop=True)
    cols = pd.read_csv(_ASSETS / "yamato_columns.csv", nrows=0, encoding="cp932").columns.str.strip().tolist()
    exp = pd.DataFrame(columns=cols)
    if not d.empty:
        exp["お届け先電話番号"] = d["_tel"]
        exp["お届け先郵便番号"] = d["_zip"]
        exp["お届け先名"] = d["_name"]
        exp["お届け先住所"] = d["_addr"]
        exp["品名１"] = d["商品内容"]
        exp["お届け予定日"] = d["お届け日指定"]
        exp["お客様管理番号"] = "0649633212"
        exp["送り状種類"] = "0"
        exp["出荷予定日"] = datetime.today().strftime("%Y/%m/%d")
        exp["敬称"] = "様"
        exp["ご依頼主電話番号"] = "0649633212"
        exp["ご依頼主郵便番号"] = "557-0061"
        exp["ご依頼主住所"] = "大阪府大阪市西成区北津守4-1-24"
        exp["ご依頼主名"] = "余福"
        exp["請求先顧客コード"] = "0649633212"
        exp["運賃管理番号"] = "01"
        exp["検索キータイトル1"] = "注文管理"
        exp = _consolidate_with_mgmt(
            exp, d[["注文番号", "送付先ID"]], name_col="お届け先名",
            product_cols=["品名１", "品名２"], chunk_size=2,
            ref_col="検索キー1", mgmt_prefix=f"{store}Y", mapping=mapping,
        )
        exp = exp.sort_values(by="品名１")
    result.files["yamato"] = _to_cp932_csv(exp)
    result.counts["yamato"] = len(exp) if not d.empty else 0

    # ---- Post（无合单、无 mgmt_no 桥；模板无引用字段，回填暂人工）----
    d = df[df["快递公司"] == "post"].copy()
    if not d.empty:
        d["_zip"] = d.apply(_merge_zip, axis=1)
        d["_tel"] = d.apply(_merge_phone, axis=1)
        d["_name"] = d.apply(_merge_name, axis=1)
        d["商品内容"] = d.apply(lambda r: _merge_products(r, product_dict, err_rows), axis=1)
        d = d.explode("商品内容").reset_index(drop=True)
        d = d[d["商品内容"] != ""].reset_index(drop=True)
    cols = pd.read_csv(_ASSETS / "post_columns.csv", nrows=0, encoding="cp932").columns.str.strip().tolist()
    exp = pd.DataFrame(columns=cols)
    if not d.empty:
        exp["お届け先住所4行目"] = d["_tel"]
        exp["お届け先郵便番号"] = d["_zip"]
        exp["お届け先氏名"] = d["_name"]
        exp["お届け先住所1行目"] = d["送付先住所都道府県"]
        exp["お届け先住所2行目"] = d["送付先住所郡市区"]
        exp["お届け先住所3行目"] = d["送付先住所それ以降の住所"].fillna("")
        exp["内容品"] = d["商品内容"]
        exp["お届け先敬称"] = "様"
        exp = exp.sort_values(by="内容品")
    result.files["post"] = _to_cp932_csv(exp)
    result.counts["post"] = len(exp) if not d.empty else 0

    result.err_rows = err_rows
    result.mapping = mapping
    return result


# ── P4：由快递结果 + mapping 生成 RMS 発送完了報告データ CSV ────────────────
_REPORT_COLUMNS = ["注文番号", "送付先ID", "発送明細ID", "お荷物伝票番号", "配送会社", "発送日"]


def _clean_head(c: str) -> str:
    return str(c).replace("﻿", "").strip().strip('"').strip()


def _norm_col(c: str) -> str:
    """列名归一：清洗 + NFKC 折叠全角↔半角。

    Yamato B2「発行済データ」导出把列名用全角数字（`検索キー１` = U+FF11），
    而我们生成/配置用半角（`検索キー1` = U+0031），直接 == 匹配会落空 → 回填空表。
    NFKC 把全角数字/字母折成半角，使两者一致（也归一其它全角符号）。"""
    return unicodedata.normalize("NFKC", _clean_head(c))


def _decode_result(b: bytes, *expect_fields: str) -> str:
    """自动识别快递结果文件编码：佐川多为 UTF-8(BOM)，Yamato B2 多为 Shift-JIS(cp932)。
    用"哪种编码解出的表头包含期望列名"来判定，避免 cp932 被当 UTF-8 解成乱码。"""
    best = None
    for enc in ("utf-8-sig", "cp932", "utf-8", "shift_jis"):
        try:
            text = b.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
        if best is None:
            best = text
        head = unicodedata.normalize("NFKC", text.splitlines()[0]) if text else ""
        if any(f and unicodedata.normalize("NFKC", f) in head for f in expect_fields):
            return text
    return best if best is not None else b.decode("utf-8-sig", errors="replace")


@dataclass
class ShipmentReportResult:
    csv_bytes: bytes
    row_count: int = 0        # 输出行数（订单级，合单已展开）
    matched_mgmt: int = 0     # 结果文件里对上映射的运单数
    with_tracking: int = 0    # 其中带单号的行数
    unmatched_mgmt: list[str] = field(default_factory=list)  # 结果里有、映射里没有的 mgmt_no


def build_shipment_report(
    result_bytes: bytes,
    mapping: dict[str, list[dict]],
    *,
    courier_code: str,
    ship_date: str | None = None,
    ref_field: str = "お客様管理番号",
    tracking_field: str = "お問い合せ送り状No.",
) -> ShipmentReportResult:
    """把快递出单结果文件（含 mgmt_no + 运单号）翻译成 RMS 発送完了報告データ CSV。

    - `mapping`: P1 产出的 `mgmt_no → [{注文番号, 送付先ID}]`（合单：一张运单可对应多订单，逐一展开）。
    - `発送明細ID` 留空（発送待ち 首次报发货=新規登録）。
    - `配送会社` 用 RMS 的数字代码（店铺自定义，如 1001）。
    - 输出 cp932，列顺序与 RMS「発送完了報告用」模板一致。
    """
    ship_date = ship_date or date.today().strftime("%Y-%m-%d")
    text = _decode_result(result_bytes, ref_field, tracking_field)
    reader = list(csv.reader(io.StringIO(text)))
    out_rows: list[list[str]] = []
    matched = with_tracking = 0
    unmatched: list[str] = []
    if reader:
        # 用 NFKC 归一后的列名匹配，兼容 Yamato 全角 `検索キー１` vs 半角 `検索キー1`
        hdr = [_norm_col(c) for c in reader[0]]
        ref_key, track_key = _norm_col(ref_field), _norm_col(tracking_field)
        ri = hdr.index(ref_key) if ref_key in hdr else -1
        ti = hdr.index(track_key) if track_key in hdr else -1
        for r in reader[1:]:
            mgmt = r[ri].strip() if 0 <= ri < len(r) else ""
            track = r[ti].strip() if 0 <= ti < len(r) else ""
            if not mgmt:
                continue
            entries = mapping.get(mgmt)
            if not entries:
                unmatched.append(mgmt)
                continue
            matched += 1
            if track:
                with_tracking += 1
            for e in entries:
                out_rows.append([e.get("注文番号", ""), e.get("送付先ID", ""), "", track, courier_code, ship_date])

    sio = io.StringIO()
    w = csv.writer(sio)
    w.writerow(_REPORT_COLUMNS)
    w.writerows(out_rows)
    return ShipmentReportResult(
        csv_bytes=sio.getvalue().encode("cp932", errors="replace"),
        row_count=len(out_rows), matched_mgmt=matched, with_tracking=with_tracking,
        unmatched_mgmt=sorted(set(unmatched)),
    )
