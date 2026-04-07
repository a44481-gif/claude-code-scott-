"""
MiniMax API 連接測試
測試 MiniMax-Text-01（M2.7）是否正常運作
使用方法：
  python test_minimax_api.py
"""
import sys, json, logging
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)

import yaml
from pathlib import Path

cfg_file = Path("config.yaml")
if not cfg_file.exists():
    print("ERROR: config.yaml not found")
    sys.exit(1)

with open(cfg_file, encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

api_key = cfg.get("minimax", {}).get("api_key", "")
model = cfg.get("minimax", {}).get("model", "MiniMax-Text-01")
base_url = cfg.get("minimax", {}).get("base_url", "https://api.minimax.chat/v1")

print(f"Model: {model}")
print(f"API Key: {'*' * 20}{api_key[-4:] if api_key and len(api_key) > 4 else '未設定'}")

if not api_key or api_key == "":
    print("\n[ERROR] MiniMax API Key 未設定！")
    print("請到 https://platform.minimax.chat/ 申請 API Key")
    print("然後打開 config.yaml，填入 minimax.api_key")
    sys.exit(1)

# Test API
import httpx

url = f"{base_url}/text/chatcompletion_v2"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": "請用一句話介紹 MiniMax-Text-01 模型的核心優勢。請用繁體中文回答。"
        }
    ],
    "max_tokens": 200,
    "temperature": 0.7,
}

print(f"\n[TEST] 連接 {url} ...")
with httpx.Client(timeout=60) as client:
    resp = client.post(url, headers=headers, json=payload)

print(f"[HTTP] {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    print(f"\n[SUCCESS] MiniMax M2.7 回應：")
    print("-" * 40)
    print(content)
    print("-" * 40)
    print("\n[OK] MiniMax API 設定正確！")
else:
    print(f"[ERROR] HTTP {resp.status_code}")
    print(resp.text[:500])
