"""
MiniMax API 連線測試腳本
使用方法：python test_minimax.py
"""

import httpx
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def test_minimax():
    config = load_config()
    mm_cfg = config.get("minimax", {})

    api_key = mm_cfg.get("api_key", "")
    base_url = mm_cfg.get("base_url", "https://api.minimax.chat/v1")
    model = mm_cfg.get("model", "MiniMax-Text-01")

    if not api_key:
        print("[ERROR] API Key not found in config.json")
        return

    masked = f"{api_key[:12]}...{api_key[-4:]}"
    print(f"[OK] API Key loaded: {masked}")
    print(f"     Model: {model}")
    print(f"     API URL: {base_url}")
    print()

    url = f"{base_url}/text/chatcompletion_v2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": "請用繁體中文回覆：你好，簡單介紹一下你自己。"}
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }

    print("[TESTING] Connecting to MiniMax API...")
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        choices = data.get("choices", [])
        if choices:
            content = choices[0].get("message", {}).get("content", "")
            print()
            print("=" * 50)
            print("[SUCCESS] MiniMax API connected!")
            print("=" * 50)
            print()
            print("[MiniMax Reply]:")
            print(content)
        else:
            print("[ERROR] Unexpected response format")
            print("Raw response:", json.dumps(data, ensure_ascii=False, indent=2))

    except httpx.HTTPStatusError as e:
        print(f"[HTTP ERROR] Status: {e.response.status_code}")
        print("Response:", e.response.text)
    except httpx.RequestError as e:
        print(f"[CONNECTION ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    test_minimax()
