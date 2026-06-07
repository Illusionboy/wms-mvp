#!/bin/bash
# 一键续期秦丝生意通 session
# NAS_API_URL 和 NAS_JWT_TOKEN 从项目根目录的 .env 读取
# 每 7 天运行一次即可

set -e
cd "$(dirname "$0")"

/Users/mac/anaconda3/bin/conda run -n wms-mvp python -m tools.refresh_qinsi_session "$@"
