from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def admin_home() -> str:
    return """
<!doctype html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>WMS Admin</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 32px; max-width: 760px; }
    section { margin-bottom: 32px; }
    label { display: block; margin: 12px 0 6px; }
    input, button { font: inherit; padding: 8px; }
    input[type="text"] { width: 320px; }
    pre { background: #f5f5f5; padding: 12px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <h1>WMS Admin</h1>

  <section>
    <h2>添加仓库</h2>
    <form id="warehouse-form">
      <label for="warehouse-name">仓库名</label>
      <input id="warehouse-name" name="name" type="text" required>
      <button type="submit">添加</button>
    </form>
  </section>

  <section>
    <h2>上传盘点数据</h2>
    <form id="count-form">
      <input id="count-file" name="file" type="file" accept=".xlsx,.xls,.csv" required>
      <button type="submit">上传</button>
    </form>
  </section>

  <pre id="result"></pre>

  <script>
    const result = document.getElementById("result");

    document.getElementById("warehouse-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const name = document.getElementById("warehouse-name").value;
      const response = await fetch("/api/v1/warehouses", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name})
      });
      result.textContent = JSON.stringify(await response.json(), null, 2);
    });

    document.getElementById("count-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData();
      formData.append("file", document.getElementById("count-file").files[0]);
      const response = await fetch("/api/v1/inventory/imports/monthly-count", {
        method: "POST",
        body: formData
      });
      result.textContent = JSON.stringify(await response.json(), null, 2);
    });
  </script>
</body>
</html>
"""
