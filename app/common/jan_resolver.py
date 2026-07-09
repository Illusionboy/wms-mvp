# JAN / 数量解析核心逻辑。
# 纯函数，不依赖 pandas 或文件 IO，供乐天快递子项目（rakuten-shipping）与本
# WMS 项目的乐天出库 / 乐天采购模块共同复用。规则详见 Shipping-tools/JAN_QUANTITY_SPEC.md。
#
# 同步说明：本文件与 rakuten-shipping 项目下的 jan_resolver.py 内容应保持一致。
# 若解析规则有变更（尤其是 -0 / 套装规则），需同步修改两边的 jan_resolver.py 和
# product_dict.json（详见 CLAUDE.md）。
import json
from functools import lru_cache
from pathlib import Path

_PRODUCT_DICT_PATH = Path(__file__).with_name("product_dict.json")


@lru_cache(maxsize=1)
def load_product_dict() -> dict:
    """加载兜底字典 {商品番号barcode: {sku_jan: 13位JAN}}。"""
    with open(_PRODUCT_DICT_PATH, encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_comment", None)
    return data


def resolve_jan_quantities(
    product_no: str,
    sys_sku_raw: str,
    order_count: int,
    product_dict: dict | None = None,
) -> list[tuple[str, int]]:
    """
    输入：
      product_no   商品番号，如 "4954835290142-3"
      sys_sku_raw  システム連携用SKU番号，如 "4971710376227-7002-2"（可为空字符串）
      order_count  個数（订购数量）
      product_dict 兜底字典 {barcode: {sku_jan: JAN}}，缺省时自动加载 product_dict.json

    返回：[(JAN, 数量), ...]；无法解析返回 []。
    """
    if product_dict is None:
        product_dict = load_product_dict()

    p2 = (product_no or "").strip()
    sys_sku_raw = (sys_sku_raw or "").strip()

    if not p2:
        return []

    # --- 解析商品番号：拆出 barcode 和 set_count ---
    # 套数后缀规则：最后一个 '-' 后为 1~3 位纯数字才视为套数，否则整体视为 barcode。
    # 特殊规则：后缀为 0 时，表示该商品有多种套装/选项，实际数量需以 システム連携用SKU番号 为准，
    # 不能直接当作 set_count=1 输出，需进入下方 システム連携用SKU番号 解析流程。
    barcode = p2
    set_count = 1
    is_variable_set = False
    if "-" in p2:
        parts = p2.rsplit("-", 1)
        suffix = parts[1].strip()
        if suffix.isdigit() and 1 <= len(suffix) <= 3:
            barcode = parts[0].strip()
            if int(suffix) == 0:
                is_variable_set = True
            else:
                set_count = int(suffix)

    # --- 标准13位JAN，且非可变套装（后缀非0），直接输出 ---
    if barcode.isdigit() and len(barcode) == 13 and not is_variable_set:
        return [(barcode, set_count * order_count)]

    # --- 非标准商品番号（旧文本代码 / 7位系列商品 / 可变套装）---
    if sys_sku_raw:
        sys_parts = sys_sku_raw.split("-")

        # 套装检测："完整JAN(13位) - 局部JAN(4位)... - 件数"
        # 例：4971710376227-7002-2 → [4971710376227, 7002, 2]
        # 重建规则：后续JAN = 第一个JAN的前9位 + 4位局部代码
        if (
            len(sys_parts) >= 3
            and sys_parts[0].isdigit() and len(sys_parts[0]) == 13
            and all(p.isdigit() and len(p) == 4 for p in sys_parts[1:-1])
            and sys_parts[-1].isdigit()
        ):
            first_jan = sys_parts[0]
            prefix9 = first_jan[:9]
            all_jans = [first_jan] + [prefix9 + p for p in sys_parts[1:-1]]
            return [(jan, order_count) for jan in all_jans]

        # 普通单品：解析 sku_jan + sku_qty（没有 '-' 时 sku_qty 按 1 处理）
        sku_jan = sys_sku_raw
        sku_qty = 1
        if "-" in sys_sku_raw:
            parts = sys_sku_raw.rsplit("-", 1)
            suffix = parts[1].strip()
            if suffix.isdigit() and 1 <= len(suffix) <= 3:
                sku_jan = parts[0].strip()
                sku_qty = int(suffix) if int(suffix) > 0 else 1

        if sku_jan.isdigit() and len(sku_jan) == 13:
            return [(sku_jan, sku_qty * order_count)]

        # product_dict 两键联查（兜底）
        resolved_jan = product_dict.get(barcode, {}).get(sku_jan) or product_dict.get(p2, {}).get(sku_jan)
        if resolved_jan:
            return [(resolved_jan, sku_qty * order_count)]

    return []
