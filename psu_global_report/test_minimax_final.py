"""
MiniMax API 最終測試 — 嘗試所有可能的認證組合
"""
import httpx, json, sys
sys.stdout.reconfigure(encoding="utf-8")

FULL_KEY = "sk-cp-7Sf0AAq1uDMZ-EFwjwCUtApZJ-axwEATLw8gSo-DgYZ7plqkK1v-cjQiAMcB27kf-MF4BGrAIMcAW"
parts = FULL_KEY.split("-")

# 嘗試不同的 key 截取方式
key_variants = {
    "full": FULL_KEY,
    "no_sk_prefix": FULL_KEY[3:],  # 去掉 "sk-"
    "no_sk_cp": FULL_KEY[6:],      # 去掉 "sk-cp-"
    "group_then_secret": parts[2],  # = 7Sf0AAq1uDMZ
    "secret_only": "-".join(parts[3:]),  # EFwjwCUtApZJ-...
}

print("Key variants:")
for k, v in key_variants.items():
    print(f"  {k}: {v[:15]}...{v[-6:]}")
print()

# 測試不同的 base URLs
urls = {
    "native_v2": "https://api.minimax.chat/v1/text/chatcompletion_v2",
    "openai_compat": "https://api.minimax.chat/v1/chat/completions",
    "chatproxy": "https://chatproxy.minimax.io/v1/chat/completions",
    "api_minimax_io": "https://api.minimax.io/v1/chat/completions",
}

# payload
payload_template = {
    "model": "MiniMax-Text-01",
    "messages": [{"role": "user", "content": "say ok"}],
    "max_tokens": 5,
}

results = []

for url_name, base_url in urls.items():
    for key_name, key_val in key_variants.items():
        # 嘗試不同的 auth 格式
        auth_formats = [
            (f"Bearer {key_val}", {}),
            (key_val, {}),
            (f"Token {key_val}", {}),
        ]

        for auth_str, extra_headers in auth_formats:
            headers = {
                "Authorization": auth_str,
                "Content-Type": "application/json",
            }
            headers.update(extra_headers)

            try:
                with httpx.Client(timeout=20) as client:
                    resp = client.post(base_url, headers=headers, json=payload_template)

                data = resp.json()
                choices = data.get("choices")
                err = data.get("base_resp", {})
                err_type = data.get("type", "")

                if choices:
                    msg = choices[0].get("message", {}).get("content", "")
                    result = f"[OK] {url_name} + {key_name} + {auth_str[:20]}..."
                    print(result)
                    print(f"     -> {repr(msg[:80])}")
                    results.append((url_name, key_name, auth_str[:30], "SUCCESS", msg))
                    break  # 找到成功的就停
                elif err:
                    pass  # 記錄失敗但不顯示
                elif err_type:
                    print(f"[FAIL] {url_name} + {key_name}: HTTP {resp.status_code} {err_type}: {data.get('error', {}).get('message', '')[:50]}")
                else:
                    print(f"[INFO] {url_name} + {key_name}: HTTP {resp.status_code}")

            except httpx.HTTPStatusError as e:
                print(f"[HTTP ERR] {url_name} + {key_name}: {e.response.status_code}")
            except Exception as e:
                print(f"[ERR] {url_name} + {key_name}: {e}")

print(f"\n\n=== Summary: {len(results)} successful ===")
for r in results:
    print(f"  {r}")
