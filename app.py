# app.py — 診斷版
from flask import Flask, request, abort, jsonify
import os, logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ---- 環境變數存在性檢查（不打印值）----
REQUIRED_ENVS = ["CHANNEL_ACCESS_TOKEN", "CHANNEL_SECRET", "OPENAI_API_KEY"]
env_status = {k: ("✅" if os.getenv(k) else "❌") for k in REQUIRED_ENVS}

@app.get("/")
def health():
    # 簡單健康檢查；也把必填環境變數是否就緒顯示出來
    return (
        "OK\n"
        + "\n".join(f"{k}: {env_status[k]}" for k in REQUIRED_ENVS)
        + "\nRoutes: /, /env, /callback(GET for verify, POST for events)"
    ), 200

@app.get("/env")
def show_env_status():
    # 更詳細的 JSON 狀態（仍不暴露值）
    return jsonify({
        "required_envs": env_status,
        "tips": "若有 ❌，請到 Vercel → Settings → Environment Variables 設定後 Redeploy。"
    })

@app.route("/callback", methods=["GET", "POST"])
def callback():
    # LINE Developers 的 Verify 會發 GET
    if request.method == "GET":
        return "OK", 200

    # 這裡先不處理 LINE 事件，只驗證到這一步 server 沒崩潰
    # 等確定環境變數都 ✅ 再換回正式版
    if not all(os.getenv(k) for k in REQUIRED_ENVS):
        abort(500, description="Server config error: some required envs are missing.")
    return "OK", 200

# 避免瀏覽器自動請求 favicon 造成噪音
@app.get("/favicon.ico")
def favicon():
    return "", 204
