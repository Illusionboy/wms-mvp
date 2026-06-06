# WMS 项目 Git 部署手册

**架构**：Mac（开发）→ push → GitHub（中转）→ pull → NAS（运行）

NAS 地址：`100.114.28.35:5122`（Tailscale 内网）  
NAS 用户：`luoweixue_ecjt`  
NAS 项目路径：`/volume1/docker/wms-mvp/`

---

## 一次性初始化（只做一次）

### 第一步：GitHub 上创建仓库

1. 登录 GitHub → New repository
2. 建议设为 **Private**（含业务代码）
3. 不要勾选 Initialize with README（本地已有代码）
4. 创建后复制仓库地址，形如 `git@github.com:YourName/wms-mvp.git`

### 第二步：Mac 添加 GitHub remote

```bash
cd "/Users/mac/Documents/New project"

# 添加 GitHub 为 origin（替换为你的实际仓库地址）
git remote add origin git@github.com:YourName/wms-mvp.git

# 第一次推送
git push -u origin master
```

### 第三步：NAS 配置从 GitHub 拉取

```bash
# SSH 进入 NAS
ssh luoweixue_ecjt@100.114.28.35 -p 5122

# 进入项目目录
cd /volume1/docker/wms-mvp

# 添加 GitHub 为 origin（同上，替换为你的仓库地址）
git remote add origin git@github.com:YourName/wms-mvp.git

# 如果 NAS 还没有 SSH key，生成一个
ssh-keygen -t ed25519 -C "nas-wms"
cat ~/.ssh/id_ed25519.pub
# 把输出的公钥复制，添加到 GitHub → Settings → SSH and GPG keys → New SSH key

# 测试连接
ssh -T git@github.com

# 拉取代码
git pull origin master
```

---

## 日常开发流程（最常用）

### 1. Mac 上修改代码后提交

```bash
cd "/Users/mac/Documents/New project"

# 查看改了什么
git status
git diff

# 添加改动的文件（推荐按文件/目录，不要 git add .）
git add app/services/inventory.py app/static/app.html
# 或者整个 app 目录
git add app/

# 提交
git commit -m "Fix: 出库时负库存判断逻辑"
```

### 2. 推送到 GitHub

```bash
git push origin master
```

### 3. NAS 拉取并重启服务

**纯代码改动**（未改 requirements.txt / Dockerfile）：

```bash
ssh luoweixue_ecjt@100.114.28.35 -p 5122 \
  "cd /volume1/docker/wms-mvp && git pull origin master && docker compose restart api bot"
```

**有新依赖或配置变更**（改了 requirements.txt / Dockerfile / docker-compose.yml）：

```bash
ssh luoweixue_ecjt@100.114.28.35 -p 5122 \
  "cd /volume1/docker/wms-mvp && git pull origin master && docker compose up --build -d"
```

---

## 查看 NAS 服务状态

```bash
# 查看容器状态
ssh luoweixue_ecjt@100.114.28.35 -p 5122 \
  "cd /volume1/docker/wms-mvp && docker compose ps"

# 查看 API 最近日志
ssh luoweixue_ecjt@100.114.28.35 -p 5122 \
  "cd /volume1/docker/wms-mvp && docker compose logs --tail=40 api"

# 实时跟踪日志（Ctrl+C 退出）
ssh luoweixue_ecjt@100.114.28.35 -p 5122 \
  "cd /volume1/docker/wms-mvp && docker compose logs -f api"
```

---

## 不在 Git 里的文件（需手动管理）

### `.env` 文件（首次 + 每次修改后）

`.env` 被 gitignore，需要单独传到 NAS：

```bash
scp -P 5122 "/Users/mac/Documents/New project/.env" \
  luoweixue_ecjt@100.114.28.35:/volume1/docker/wms-mvp/.env
```

修改了 `.env`（如改密码、加新 key）后重复执行此命令，然后重启：

```bash
ssh luoweixue_ecjt@100.114.28.35 -p 5122 \
  "cd /volume1/docker/wms-mvp && docker compose up -d"
```

### 秦丝生意通 session（每 7 天续期一次）

`app/data/qinsi_session.json` 含敏感 cookies，不进 git。在 Mac 上运行续期脚本，自动上传到 NAS：

```bash
# 替换为 NAS 地址和你的 WMS JWT token
conda run -n wms-mvp python -m tools.refresh_qinsi_session \
  --api http://100.114.28.35:8000 \
  --token 你的JWT_TOKEN
```

JWT token 获取：打开 WMS 网页 → F12 → Console → `localStorage.getItem('token')`

---

## 常用 Git 命令速查

```bash
# 查看本地和 GitHub 的差异（哪些提交还没推）
git log origin/master..HEAD --oneline

# 查看提交历史
git log --oneline -10

# 撤销尚未 commit 的修改（危险，不可恢复）
git checkout -- app/services/inventory.py

# 查看所有 remote
git remote -v
```

---

## 文件管理对照表

| 文件/目录 | 是否在 Git | 同步方式 |
| --- | --- | --- |
| `app/` 代码 | ✅ 是 | `git push` → NAS `git pull` |
| `requirements.txt` | ✅ 是 | 同上，NAS 需 `--build` |
| `Dockerfile` | ✅ 是 | 同上，NAS 需 `--build` |
| `docker-compose.yml` | ✅ 是 | 同上，NAS 需 `--build` |
| `.env` | ❌ 否 | `scp` 手动传，改后重传 |
| `app/data/qinsi_session.json` | ❌ 否 | `refresh_qinsi_session.py` 脚本 |
| `app/data/scraper_debug/` | ❌ 否 | 调试截图，无需同步 |
| PostgreSQL 数据 | ❌ 否 | Docker volume，自动持久化 |

**何时必须用 `--build`**：改了 `requirements.txt`、`Dockerfile`、`docker-compose.yml` 时。  
纯 Python / HTML 改动只需 `docker compose restart api bot`，速度快得多。
