"""乐天快递单生成端点（P1）：上传 RMS 订单 CSV → 返回打包 ZIP。"""
import csv as _csv
import io
import json
import zipfile
from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from fastapi import HTTPException

from app.api.deps import require_auth
from app.services.rakuten_label import build_shipment_report, generate_courier_files

router = APIRouter()

_MAX_BYTES = 30 * 1024 * 1024
_COURIER_LABEL = {"sagawa": "佐川", "yamato": "yamato", "post": "郵便"}


@router.post("/labels", dependencies=[Depends(require_auth)])
async def generate_labels(
    file: UploadFile = File(..., description="RMS 订单明细 CSV（全カラムダウンロード用, cp932）"),
    store: str = Query("1", description="店铺标识（用于文件名与 mgmt_no 前缀）"),
) -> StreamingResponse:
    content = await file.read(_MAX_BYTES + 1)
    result = generate_courier_files(content, store)
    ts = datetime.now().strftime("%Y%m%d_%H%M")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for courier, data in result.files.items():
            z.writestr(f"{ts}-store{store}-{_COURIER_LABEL[courier]}.csv", data)
        # mgmt_no → [(注文番号, 送付先ID)] 桥映射，第4步 発送完了報告 回填要用
        z.writestr("mapping.json", json.dumps(result.mapping, ensure_ascii=False, indent=2))
        if result.err_rows:
            sio = io.StringIO()
            w = _csv.DictWriter(sio, fieldnames=["收件人", "电话", "原品名2"])
            w.writeheader()
            w.writerows(result.err_rows)
            z.writestr("err_export.csv", sio.getvalue())

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="rakuten_labels_{ts}_store{store}.zip"',
            "X-Counts": json.dumps(result.counts),
            "X-Err-Count": str(len(result.err_rows)),
        },
    )


@router.post("/shipment-report", dependencies=[Depends(require_auth)])
async def shipment_report(
    result_file: UploadFile = File(..., description="快递出单结果文件（如佐川 出荷履歴，含 お客様管理番号 + お問い合せ送り状No.）"),
    mapping_file: UploadFile = File(..., description="P1 下载包里的 mapping.json"),
    courier_code: str = Query(..., description="RMS 配送会社 数字代码（如 1001）"),
    ship_date: str | None = Query(None, description="発送日 YYYY-MM-DD（默认今天）"),
    ref_field: str = Query("お客様管理番号", description="结果文件里承载 mgmt_no 的列名"),
    tracking_field: str = Query("お問い合せ送り状No.", description="结果文件里运单号列名"),
) -> StreamingResponse:
    """把快递结果文件 + mapping.json → 生成 RMS 発送完了報告データ CSV（cp932，人工上传 RMS）。"""
    try:
        mapping = json.loads((await mapping_file.read(_MAX_BYTES + 1)).decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=422, detail=f"mapping.json 解析失败：{exc}") from exc
    res = build_shipment_report(
        await result_file.read(_MAX_BYTES + 1), mapping,
        courier_code=courier_code, ship_date=ship_date,
        ref_field=ref_field, tracking_field=tracking_field,
    )
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    fname = quote(f"発送完了報告_{ts}.csv")
    return StreamingResponse(
        io.BytesIO(res.csv_bytes),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"shipment_report_{ts}.csv\"; filename*=UTF-8''{fname}",
            "X-Row-Count": str(res.row_count),
            "X-Matched": str(res.matched_mgmt),
            "X-With-Tracking": str(res.with_tracking),
            "X-Unmatched": json.dumps(res.unmatched_mgmt, ensure_ascii=False),
        },
    )
