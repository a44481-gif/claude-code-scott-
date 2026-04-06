# -*- coding: utf-8 -*-
"""
GPU 電源線燒毀研究 Skill - 增強版
Enhanced GPU Power Cable Burn Research Skill

功能:
- 收集全球平台的顯卡電源線燒毀案例
- 生成完整研究報告 (HTML/Markdown/JSON)
- 發送郵件通知
- 同步到飛書

使用方式:
    /gpu-research                    # 執行完整流程
    /gpu-research --collect         # 只收集數據
    /gpu-research --generate        # 只生成報告
    /gpu-research --stats          # 顯示統計
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from gpu_research.src.collector import GPUCollector
from gpu_research.src.generator import ReportGenerator
from gpu_research.src.sender import EmailSender
from gpu_research.src.config import config


class GPURESEARCHSkill:
    """
    GPU 電源線燒毀研究 Skill 主類
    """

    def __init__(self):
        self.collector = GPUCollector()
        self.generator = ReportGenerator()
        self.sender = EmailSender()
        self.cases = []
        self.report = ''

    def run(self, mode: str = 'all', **kwargs) -> dict:
        """
        執行研究任務

        Args:
            mode: 執行模式 ('all', 'collect', 'generate', 'stats', 'send')
            **kwargs: 其他參數

        Returns:
            dict: 執行結果
        """
        result = {
            'success': False,
            'message': '',
            'data': {}
        }

        try:
            if mode == 'all':
                result = self._run_all()
            elif mode == 'collect':
                result = self._collect()
            elif mode == 'generate':
                result = self._generate()
            elif mode == 'stats':
                result = self._stats()
            elif mode == 'send':
                result = self._send()
            else:
                result['message'] = f'未知模式: {mode}'

        except Exception as e:
            result['message'] = f'執行失敗: {str(e)}'

        return result

    def _run_all(self) -> dict:
        """執行完整流程"""
        output = []

        # 1. 收集數據
        output.append("📊 收集數據...")
        collect_result = self._collect()
        if not collect_result['success']:
            return collect_result

        # 2. 生成報告
        output.append("📝 生成報告...")
        generate_result = self._generate()
        if not generate_result['success']:
            return generate_result

        # 3. 發送郵件
        output.append("📧 發送郵件...")
        send_result = self._send()
        # 郵件發送失敗不影響整體流程

        output.append("✅ 完整流程執行完成!")

        return {
            'success': True,
            'message': '\n'.join(output),
            'data': {
                'cases_count': len(self.cases),
                'report_size': len(self.report),
                'stats': self.collector.get_statistics()
            }
        }

    def _collect(self) -> dict:
        """收集數據"""
        try:
            self.cases = self.collector.collect_all()
            stats = self.collector.get_statistics()

            return {
                'success': True,
                'message': f'✅ 收集到 {len(self.cases)} 個案例\n📈 統計: {stats}',
                'data': {
                    'cases': self.cases,
                    'stats': stats
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ 數據收集失敗: {str(e)}'
            }

    def _generate(self) -> dict:
        """生成報告"""
        try:
            if not self.cases:
                self.cases = self.collector.collect_all()

            self.report = self.generator.generate_html(self.cases)

            # 保存報告
            output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'gpu_research', 'docs')
            os.makedirs(output_dir, exist_ok=True)
            report_path = os.path.join(output_dir, 'gpu_report_skill.html')
            self.generator.save_report(self.report, report_path)

            return {
                'success': True,
                'message': f'✅ 報告已生成並保存\n📄 路徑: {report_path}',
                'data': {
                    'report_path': report_path,
                    'report_size': len(self.report)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ 報告生成失敗: {str(e)}'
            }

    def _stats(self) -> dict:
        """顯示統計"""
        try:
            if not self.cases:
                self.cases = self.collector.collect_all()

            stats = self.collector.get_statistics()

            stats_text = f"""
📊 統計概覽
=============
總案例數: {stats['total']}

按地區:
"""
            for region, count in stats['by_region'].items():
                stats_text += f"  • {region}: {count}\n"

            stats_text += "\n按平台:\n"
            for platform, count in stats['by_platform'].items():
                stats_text += f"  • {platform}: {count}\n"

            stats_text += "\n按 GPU 型號:\n"
            for gpu, count in stats['by_gpu'].items():
                stats_text += f"  • {gpu}: {count}\n"

            stats_text += "\n按嚴重程度:\n"
            for severity, count in stats['by_severity'].items():
                stats_text += f"  • {severity}: {count}\n"

            return {
                'success': True,
                'message': stats_text,
                'data': {'stats': stats}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ 統計失敗: {str(e)}'
            }

    def _send(self) -> dict:
        """發送郵件"""
        try:
            if not config.email.sender_auth_code:
                return {
                    'success': False,
                    'message': '⚠️ 郵箱授權碼未設置，跳過發送'
                }

            if not self.report:
                self.report = self.generator.generate_html(self.cases)

            success = self.sender.send_report(
                report_html=self.report,
                recipients=['h13751019800@163.com']
            )

            if success:
                return {
                    'success': True,
                    'message': '✅ 郵件發送成功'
                }
            else:
                return {
                    'success': False,
                    'message': '❌ 郵件發送失敗'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ 郵件發送失敗: {str(e)}'
            }


# Skill 入口函數
def gpu_research_skill(mode: str = 'all', **kwargs) -> dict:
    """
    GPU 研究 Skill 入口函數

    用法:
        result = gpu_research_skill()           # 完整流程
        result = gpu_research_skill('stats')    # 只顯示統計
        result = gpu_research_skill('collect')  # 只收集數據
    """
    skill = GPURESEARCHSkill()
    return skill.run(mode, **kwargs)


if __name__ == '__main__':
    # 測試
    print("🧪 測試 GPU 研究 Skill...")
    result = gpu_research_skill('stats')
    print(result['message'])
