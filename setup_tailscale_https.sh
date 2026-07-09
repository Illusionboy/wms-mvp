#!/usr/bin/env bash
#
# 在【NAS 主机】上运行，为 WMS 开启 HTTPS（Tailscale 内置证书）。
#
#   用法:  ./setup_tailscale_https.sh [WMS端口]
#   默认端口 8000（对应 docker-compose 里 api 发布的 API_PORT）
#
# 前提:
#   1. 这台 NAS 已安装并登录 Tailscale（`tailscale status` 能看到自己）。
#   2. Tailscale 后台已开启 MagicDNS + HTTPS Certificates
#      （https://login.tailscale.com/admin/dns → 打开 "MagicDNS" 和 "HTTPS Certificates"）。
#   3. WMS 已在本机 127.0.0.1:<端口> 上跑起来（docker compose up -d api）。
#
# 效果:  https://<机器名>.<tailnet>.ts.net/  → 反代到 http://127.0.0.1:<端口>
#        真证书、零警告，手机（含 iPhone）摄像头扫码可直接用。
#
set -euo pipefail

APP_PORT="${1:-8000}"

# 非 root 时自动加 sudo；已是 root 则直接执行
SUDO=""
if [ "$(id -u)" -ne 0 ]; then SUDO="sudo"; fi

echo "==> WMS HTTPS (Tailscale) 配置开始，目标端口: ${APP_PORT}"

# 1. 检查 tailscale 命令
if ! command -v tailscale >/dev/null 2>&1; then
  echo "✗ 未找到 tailscale 命令。请先在这台 NAS 上安装 Tailscale 后再运行本脚本。" >&2
  exit 1
fi

# 2. 检查已登录 + 取本机 MagicDNS 名称（不依赖 jq/python，纯文本解析）
DNSNAME="$(tailscale status --json 2>/dev/null | tr ',' '\n' | grep -m1 '"DNSName"' \
           | sed -E 's/.*"DNSName"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/; s/\.$//' || true)"
if [ -z "${DNSNAME}" ]; then
  echo "✗ 无法获取本机 MagicDNS 名称。请确认已登录：  ${SUDO} tailscale up" >&2
  echo "  然后再运行本脚本。" >&2
  exit 1
fi
echo "    本机 MagicDNS 名称: ${DNSNAME}"

# 3. 检查 WMS 是否在本机端口上响应（避免代理到一个没起来的服务）
if command -v curl >/dev/null 2>&1; then
  if ! curl -fsS --max-time 5 "http://127.0.0.1:${APP_PORT}/api/v1/health" -o /dev/null 2>/dev/null; then
    echo "⚠ 警告: http://127.0.0.1:${APP_PORT} 上没探测到 WMS（/api/v1/health 无响应）。"
    echo "  如果 WMS 端口不是 ${APP_PORT}，请改用:  ./setup_tailscale_https.sh <正确端口>"
    echo "  仍继续配置 serve（稍后确保 WMS 已启动即可）。"
  fi
fi

# 4. 配置 tailscale serve: HTTPS 443 → 本机 APP_PORT（--bg 持久化，重启后仍生效）
echo "==> 配置 tailscale serve: https://${DNSNAME}/  →  http://127.0.0.1:${APP_PORT}"
if ! ${SUDO} tailscale serve --bg "${APP_PORT}" 2>/tmp/ts_serve_err.log; then
  echo "  新语法失败，尝试兼容旧版 Tailscale 的写法…"
  ${SUDO} tailscale serve --bg "http://127.0.0.1:${APP_PORT}"
fi

# 5. 触发/验证证书签发（第一次访问会自动申请 Let's Encrypt 证书，可能要几秒）
echo "==> 验证 HTTPS（首次会自动申请证书，请稍候）…"
OK=0
if command -v curl >/dev/null 2>&1; then
  for i in 1 2 3 4 5 6; do
    if curl -fsS --max-time 20 "https://${DNSNAME}/api/v1/health" -o /dev/null 2>/tmp/ts_curl.log; then
      OK=1; break
    fi
    sleep 3
  done
fi

echo
if [ "${OK}" -eq 1 ]; then
  echo "✓ 成功！HTTPS 已就绪。"
else
  echo "⚠ serve 已配置，但 HTTPS 自检未通过。最常见原因是后台没开 HTTPS 证书。"
  echo "  请到 https://login.tailscale.com/admin/dns 打开：MagicDNS + HTTPS Certificates，"
  echo "  然后重新运行本脚本；或直接在手机上打开下面地址看是否可用。"
fi
echo
echo "  现在用这个地址访问 WMS（手机浏览器同样）："
echo "      https://${DNSNAME}/"
echo
echo "  当前 serve 配置："
${SUDO} tailscale serve status || true
echo
echo "  撤销/关闭 HTTPS:  ${SUDO} tailscale serve reset"
