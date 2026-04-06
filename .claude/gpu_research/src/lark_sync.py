# -*- coding: utf-8 -*-
"""
飛書同步工具
Lark Sync Module

同步數據到飛書文檔和多維表格
"""

import json
import time
from typing import List, Dict, Optional
from .config import config


class LarkSync:
    """
    飛書同步工具
    """

    def __init__(self):
        self.app_id = config.lark.app_id
        self.app_secret = config.lark.app_secret
        self.doc_token = config.lark.doc_token
        self.access_token = None
        self.token_expires_at = 0

    def _get_access_token(self) -> Optional[str]:
        """
        獲取飛書 access_token

        Returns:
            str: access_token 或 None
        """
        if not self.app_id or not self.app_secret:
            print("❌ 錯誤: 飛書 App ID 或 Secret 未設置")
            return None

        # 檢查是否需要刷新 token
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        try:
            import urllib.request
            import urllib.parse

            url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
            data = json.dumps({
                'app_id': self.app_id,
                'app_secret': self.app_secret
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))

                if result.get('code') == 0:
                    self.access_token = result['data']['tenant_access_token']
                    # 設置過期時間（提前5分鐘過期以確保安全）
                    self.token_expires_at = time.time() + result['data']['expire'] - 300
                    return self.access_token
                else:
                    print(f"❌ 獲取 access_token 失敗: {result.get('msg')}")
                    return None

        except Exception as e:
            print(f"❌ 網路請求失敗: {e}")
            return None

    def create_document(self, title: str, content: str = '') -> Optional[str]:
        """
        創建飛書文檔

        Args:
            title: 文檔標題
            content: 文檔內容

        Returns:
            str: 文檔 URL 或 None
        """
        token = self._get_access_token()
        if not token:
            return None

        try:
            import urllib.request
            import urllib.parse

            # 1. 創建文檔
            url = 'https://open.feishu.cn/open-apis/docx/v1/documents'
            data = json.dumps({
                'title': title
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {token}')

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))

                if result.get('code') == 0:
                    doc_token = result['data']['document']['document_id']

                    # 2. 如果有內容，添加到文檔
                    if content:
                        self._add_content_to_doc(doc_token, content)

                    doc_url = f"https://www.feishu.cn/docx/{doc_token}"
                    print(f"✅ 文檔創建成功: {doc_url}")
                    return doc_url
                else:
                    print(f"❌ 文檔創建失敗: {result.get('msg')}")
                    return None

        except Exception as e:
            print(f"❌ 創建文檔失敗: {e}")
            return None

    def _add_content_to_doc(self, doc_token: str, content: str):
        """
        向文檔添加內容

        Args:
            doc_token: 文檔 token
            content: 內容（HTML 或 Markdown）
        """
        token = self._get_access_token()
        if not token:
            return

        try:
            import urllib.request

            # 將 HTML 轉換為飛書 Block 格式
            blocks = self._html_to_feishu_blocks(content)

            url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks'
            data = json.dumps({
                'children': blocks,
                'index': -1  # 添加到末尾
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {token}')

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))

                if result.get('code') == 0:
                    print("✅ 內容添加成功")
                else:
                    print(f"⚠️ 內容添加失敗: {result.get('msg')}")

        except Exception as e:
            print(f"⚠️ 添加內容失敗: {e}")

    def _html_to_feishu_blocks(self, html: str) -> List[Dict]:
        """
        將 HTML 轉換為飛書 Block 格式

        Args:
            html: HTML 內容

        Returns:
            List[Dict]: 飛書 Block 列表
        """
        blocks = []

        # 簡單的 HTML 解析
        import re
        # 去除 HTML 標籤，獲取純文字
        text = re.sub(r'<[^>]+>', '', html)
        text = text.strip()

        if text:
            # 創建段落 Block
            blocks.append({
                'block_type': 2,  # paragraph
                'paragraph': {
                    'elements': [
                        {
                            'type': 'text_run',
                            'text_run': {
                                'content': text,
                                'text_element_style': {}
                            }
                        }
                    ],
                    'style': {}
                }
            })

        return blocks

    def create_spreadsheet(self, title: str) -> Optional[str]:
        """
        創建飛書電子表格

        Args:
            title: 表格標題

        Returns:
            str: 表格 URL 或 None
        """
        token = self._get_access_token()
        if not token:
            return None

        try:
            import urllib.request

            url = 'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets'
            data = json.dumps({
                'title': title
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {token}')

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))

                if result.get('code') == 0:
                    spreadsheet_token = result['data']['spreadsheet']['spreadsheet_token']
                    sheet_id = result['data']['spreadsheet']['sheets'][0]['sheet_id']
                    sheet_url = f"https://www.feishu.cn/sheets/{spreadsheet_token}"
                    print(f"✅ 電子表格創建成功: {sheet_url}")
                    return spreadsheet_token
                else:
                    print(f"❌ 電子表格創建失敗: {result.get('msg')}")
                    return None

        except Exception as e:
            print(f"❌ 創建電子表格失敗: {e}")
            return None

    def write_to_sheet(self, spreadsheet_token: str, cases: List) -> bool:
        """
        寫入數據到電子表格

        Args:
            spreadsheet_token: 表格 token
            cases: 案例數據列表

        Returns:
            bool: 是否成功
        """
        token = self._get_access_token()
        if not token:
            return False

        try:
            import urllib.request

            # 準備數據
            values = [
                ['案例ID', '平台', '地區', 'GPU型號', '問題類型', '描述', '原因', '解決方案', '狀態', '日期', '嚴重程度']
            ]

            for case in cases:
                values.append([
                    case.case_id,
                    case.platform,
                    case.region,
                    case.gpu_model,
                    case.issue_type,
                    case.description,
                    case.root_cause,
                    case.solution,
                    case.status,
                    case.date,
                    case.severity
                ])

            url = f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values'
            data = json.dumps({
                'valueRange': {
                    'range': 'A1:K' + str(len(values)),
                    'values': values
                }
            }).encode('utf-8')

            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', f'Bearer {token}')

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

                if result.get('code') == 0:
                    print(f"✅ 數據寫入成功 ({len(cases)} 條記錄)")
                    return True
                else:
                    print(f"❌ 數據寫入失敗: {result.get('msg')}")
                    return False

        except Exception as e:
            print(f"❌ 寫入數據失敗: {e}")
            return False

    def sync_report(self, report_html: str, title: str = None) -> Optional[str]:
        """
        同步報告到飛書

        Args:
            report_html: HTML 報告
            title: 文檔標題

        Returns:
            str: 文檔 URL 或 None
        """
        if title is None:
            from datetime import datetime
            title = f"顯卡電源線燒毀研究報告 {datetime.now().strftime('%Y年%m月%d日')}"

        return self.create_document(title, report_html)


def test_lark_sync():
    """測試飛書同步功能"""
    sync = LarkSync()

    if not sync.app_id:
        print("⚠️ 飛書 App ID 未設置，跳過測試")
        return

    # 測試獲取 token
    token = sync._get_access_token()
    if token:
        print("✅ 飛書連接測試成功")
    else:
        print("❌ 飛書連接測試失敗")


if __name__ == '__main__':
    test_lark_sync()
