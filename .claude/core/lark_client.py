"""
Lark (飞书) Client - Direct HTTP API calls to 飞书 Open Platform.
Provides: 云文档、电子表格、云空间文件管理、消息发送。

Uses 飞书 Open API v1:
  https://open.feishu.cn/document/server-docs/docs/docs-introduction
"""
import json
import os
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger


class LarkClient:
    """
    飞书 API 客户端。
    支持: 云文档、电子表格、云空间文件管理、消息发送。
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.app_id = self.config.get("app_id", os.environ.get("LARK_APP_ID", ""))
        self.app_secret = self.config.get("app_secret", os.environ.get("LARK_APP_SECRET", ""))
        self.api_base = "https://open.feishu.cn"
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0

    # ── Authentication ───────────────────────────────────────────

    def _get_token(self) -> Optional[str]:
        """Get (and cache) tenant access token."""
        import time
        if self._tenant_access_token and time.time() < self._token_expires_at - 60:
            return self._tenant_access_token

        try:
            resp = httpx.post(
                f"{self.api_base}/open-apis/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                },
                timeout=30,
            )
            data = resp.json()
            if data.get("code") == 0:
                self._tenant_access_token = data["tenant_access_token"]
                self._token_expires_at = time.time() + data.get("expire", 7200)
                return self._tenant_access_token
            else:
                logger.error(f"获取 tenant_access_token 失败: {data}")
        except Exception as e:
            logger.error(f"获取 token 异常: {e}")
        return None

    def _headers(self) -> Dict[str, str]:
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, data: Dict) -> Optional[Dict]:
        try:
            resp = httpx.post(
                f"{self.api_base}{path}",
                headers=self._headers(),
                json=data,
                timeout=30,
            )
            result = resp.json()
            if result.get("code") == 0:
                return result.get("data", {})
            else:
                logger.error(f"飞书 API 错误: {result}")
            return result
        except Exception as e:
            logger.error(f"飞书 API 请求异常: {e}")
        return None

    def _get(self, path: str, params: Optional[Dict] = None) -> Optional[Dict]:
        try:
            resp = httpx.get(
                f"{self.api_base}{path}",
                headers=self._headers(),
                params=params,
                timeout=30,
            )
            result = resp.json()
            if result.get("code") == 0:
                return result.get("data", {})
            else:
                logger.error(f"飞书 API 错误: {result}")
            return result
        except Exception as e:
            logger.error(f"飞书 API 请求异常: {e}")
        return None

    # ── Cloud Docs (云文档) ─────────────────────────────────────

    def create_doc(self, title: str, folder_token: Optional[str] = None) -> Optional[str]:
        """
        创建飞书云文档，返回 doc token。
        POST /open-apis/docx/v1/documents
        """
        data = {"title": title}
        if folder_token:
            data["folder_token"] = folder_token

        result = self._post("/open-apis/docx/v1/documents", data)
        if result:
            doc_token = result.get("document", {}).get("document_id")
            if doc_token:
                logger.info(f"云文档创建成功: {title} -> {doc_token}")
                return doc_token
        return None

    def add_doc_block(
        self,
        doc_token: str,
        block_id: str,
        block_type: int,
        text: str,
    ) -> bool:
        """在云文档中添加文本块。"""
        data = {
            "children": [
                {
                    "block_type": block_type,  # 2 = text
                    "text": {
                        "elements": [{"text_run": {"content": text}}],
                        "style": {},
                    }
                }
            ],
            "index": -1,
        }
        result = self._post(
            f"/open-apis/docx/v1/documents/{doc_token}/blocks/{block_id}/children",
            data,
        )
        return result is not None

    def batch_add_doc_blocks(self, doc_token: str, blocks: List[Dict]) -> bool:
        """批量添加文档块。"""
        data = {"children": blocks, "index": -1}
        result = self._post(
            f"/open-apis/docx/v1/documents/{doc_token}/blocks/root/children",
            data,
        )
        if result:
            logger.info(f"文档块添加成功: {len(blocks)} 个")
            return True
        return False

    def update_doc_title(self, doc_token: str, title: str) -> bool:
        """更新云文档标题。"""
        result = self._post(
            f"/open-apis/docx/v1/documents/{doc_token}/",
            {"title": title},
        )
        return result is not None

    # ── Sheets (电子表格) ────────────────────────────────────────

    def create_sheet(self, title: str) -> Optional[str]:
        """
        创建飞书电子表格，返回 sheet token。
        POST /open-apis/sheets/v3/spreadsheets
        """
        result = self._post(
            "/open-apis/sheets/v3/spreadsheets",
            {"title": title},
        )
        if result:
            sheet_token = result.get("spreadsheet", {}).get("spreadsheet_token")
            if sheet_token:
                logger.info(f"电子表格创建成功: {title} -> {sheet_token}")
                return sheet_token
        return None

    def write_sheet_values(
        self,
        sheet_token: str,
        range_str: str,
        values: List[List[Any]],
    ) -> bool:
        """
        写入电子表格数据。
        PUT /open-apis/sheets/v2/sheets/{sheetToken}/values
        """
        try:
            resp = httpx.put(
                f"{self.api_base}/open-apis/sheets/v2/sheets/{sheet_token}/values",
                headers=self._headers(),
                json={
                    "valueRange": {
                        "range": range_str,
                        "values": values,
                    }
                },
                timeout=30,
            )
            result = resp.json()
            if result.get("code") == 0:
                logger.info(f"电子表格写入成功: {sheet_token}!{range_str}")
                return True
            else:
                logger.error(f"写入电子表格失败: {result}")
        except Exception as e:
            logger.error(f"写入电子表格异常: {e}")
        return False

    def write_sheet_df(
        self,
        sheet_token: str,
        sheet_id: str,
        df_data,  # pandas DataFrame
        start_cell: str = "A1",
    ) -> bool:
        """写入 pandas DataFrame 到电子表格。"""
        try:
            import pandas as pd
            if not isinstance(df_data, pd.DataFrame):
                return False

            values = [df_data.columns.tolist()] + df_data.values.tolist()
            range_str = f"{sheet_id}!{start_cell}:{start_cell[0]}{len(values) + ord(start_cell[0]) - ord('A')}"
            return self.write_sheet_values(sheet_token, range_str, values)
        except ImportError:
            logger.error("pandas 未安装，无法写入 DataFrame")
            return False

    # ── IM (消息) ────────────────────────────────────────────────

    def send_text_message(
        self,
        receive_id: str,
        receive_id_type: str = "open_id",
        text: str = "",
    ) -> bool:
        """
        发送文本消息。
        POST /open-apis/im/v1/messages?receive_id_type=open_id
        """
        data = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text}),
        }
        result = self._post(
            f"/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
            data,
        )
        if result:
            logger.info(f"消息发送成功: {receive_id}")
            return True
        return False

    def send_post_message(
        self,
        receive_id: str,
        receive_id_type: str = "open_id",
        post_content: Dict = None,
    ) -> bool:
        """发送富文本消息 (post)。"""
        data = {
            "receive_id": receive_id,
            "msg_type": "post",
            "content": json.dumps(post_content or {
                "zh_cn": {
                    "title": "AI Agent 报告",
                    "content": [[{"tag": "text", "text": "请查看附件报告。"}]]
                }
            }),
        }
        result = self._post(
            f"/open-apis/im/v1/messages?receive_id_type={receive_id_type}",
            data,
        )
        return result is not None

    # ── Drive (云空间) ───────────────────────────────────────────

    def create_folder(self, name: str, parent_token: Optional[str] = None) -> Optional[str]:
        """在云空间创建文件夹。"""
        data = {"name": name, "folder_token": parent_token}
        result = self._post("/open-apis/drive/v1/files/create_folder", data)
        if result:
            return result.get("token")
        return None

    def upload_file(
        self,
        file_path: str,
        parent_type: str = "docx",
        parent_node: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Optional[str]:
        """
        上传文件到飞书云空间。
        POST /open-apis/drive/v1/files/upload_all
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None

        file_name = name or os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        try:
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f, "application/octet-stream")}
                data = {
                    "file_name": file_name,
                    "parent_type": parent_type,
                    "size": str(file_size),
                }
                if parent_node:
                    data["parent_node"] = parent_node

                resp = httpx.post(
                    f"{self.api_base}/open-apis/drive/v1/files/upload_all",
                    headers={
                        "Authorization": f"Bearer {self._get_token()}",
                    },
                    data=data,
                    files=files,
                    timeout=120,
                )
                result = resp.json()
                if result.get("code") == 0:
                    token = result.get("data", {}).get("file_token")
                    logger.info(f"文件上传成功: {file_name} -> {token}")
                    return token
                else:
                    logger.error(f"上传文件失败: {result}")
        except Exception as e:
            logger.error(f"上传文件异常: {e}")
        return None

    # ── Batch Import ────────────────────────────────────────────

    def create_doc_from_html(self, title: str, html_content: str, folder_token: Optional[str] = None) -> Optional[str]:
        """从 HTML 内容创建飞书云文档（简化版）。"""
        doc_token = self.create_doc(title, folder_token)
        if not doc_token:
            return None

        # Convert HTML to simple text blocks
        import re
        text_blocks = re.sub(r'<[^>]+>', '', html_content)
        paragraphs = [p.strip() for p in text_blocks.split('\n') if p.strip()]

        blocks = [
            {
                "block_type": 2,  # text
                "text": {
                    "elements": [{"text_run": {"content": p[:2000]}}],
                    "style": {},
                }
            }
            for p in paragraphs[:50] if p
        ]

        if blocks:
            self.batch_add_doc_blocks(doc_token, blocks)

        return doc_token
