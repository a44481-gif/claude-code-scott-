"""
MiniMax API 格式測試
嘗試不同的端點和認證格式
"""
import httpx, json, sys
sys.stdout.reconfigure(encoding="utf-8")

api_key = "sk-cp-7Sf0AAq1uDMZ-EFwjwCUtApZJ-axwEATLw8gSo-DgYZ7plqkK1v-cjQiAMcB27kf-MF4BGrAIMcAW"
parts = api_key.split("-")
group_id = parts[2]  # = 7Sf0AAq1uDMZ
secret = "-".join(parts[3:])  # = EFwjwCUtApZJ-axwEATLw8gSo-DgYZ7plqkK1v-cjQiAMcB27kf-MF4BGrAIMcAW

url_base = "https://api.minimax.chat/v1"

# 測試組合
tests = [
    # (name, endpoint, auth_header_value, extra_headers, payload_model)
    ("Native /text/chatcompletion_v2 + Bearer full",
     f"{url_base}/text/chatcompletion_v2", f"Bearer {api_key}", {}, "MiniMax-Text-01"),
    ("Native + Bearer secret only",
     f"{url_base}/text/chatcompletion_v2", f"Bearer {secret}", {}, "MiniMax-Text-01"),
    ("Native + secret only (no Bearer)",
     f"{url_base}/text/chatcompletion_v2", secret, {}, "MiniMax-Text-01"),
    ("OpenAI compat /v1/chat/completions",
     f"{url_base}/chat/completions", f"Bearer {api_key}", {}, "MiniMax-Text-01"),
    ("Native + GroupId header",
     f"{url_base}/text/chatcompletion_v2", f"Bearer {api_key}", {"X-Group-Id": group_id}, "MiniMax-Text-01"),
    ("abab6.5s model + Bearer full",
     f"{url_base}/text/chatcompletion_v2", f"Bearer {api_key}", {}, "abab6.5s-chat"),
    ("Native + extra header GroupId in auth",
     f"{url_base}/text/chatcompletion_v2", f"Bearer {group_id}:{secret}", {}, "MiniMax-Text-01"),
]

payload_base = {"messages": [{"role": "user", "content": "hi"}], "max_tokens": 5}

for name, endpoint, auth_val, extra, model in tests:
    headers = {
        "Authorization": auth_val,
        "Content-Type": "application/json",
    }
    headers.update(extra)

    payload = {**payload_base, "model": model}

    try:
        with httpx.Client(timeout=20) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
        data = resp.json()

        choices = data.get("choices")
        err = data.get("base_resp", {})

        if choices:
            msg = choices[0].get("message", {}).get("content", "")
            print(f"[OK] {name}")
            print(f"     -> {repr(msg[:80])}")
        elif err:
            print(f"[FAIL] {name}")
            print(f"     -> code={err.get('status_code')}: {err.get('status_msg', '')[:70]}")
        else:
            print(f"[INFO] {name}: HTTP {resp.status_code}, keys={list(data.keys())[:5]}")
    except httpx.HTTPStatusError as e:
        print(f"[HTTP ERR] {name}: {e.response.status_code}")
    except Exception as e:
        print(f"[ERR] {name}: {type(e).__name__}: {e}")

print("\n--- Done ---")
print(f"API Key (masked): {api_key[:12]}...{api_key[-6:]}")
print(f"Group ID: {group_id}")
print(f"Secret (first 20): {secret[:20]}")
