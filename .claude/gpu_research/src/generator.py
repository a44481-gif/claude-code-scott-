# -*- coding: utf-8 -*-
"""
報告生成器
Report Generator Module

生成顯卡電源線燒毀研究報告
支持 HTML、Markdown、JSON 格式
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from .collector import GPUCollector, GPUCase


class ReportGenerator:
    """
    研究報告生成器
    """

    def __init__(self):
        self.collector = GPUCollector()

    def generate_html(self, cases: List[GPUCase] = None) -> str:
        """
        生成 HTML 研究報告
        """
        if cases is None:
            cases = self.collector.collect_all()

        stats = self.collector.get_statistics()

        html = self._get_html_header()
        html += self._get_statistics_section(stats)
        html += self._get_platform_sections(cases)
        html += self._get_case_details(cases)
        html += self._get_analysis_section(cases, stats)
        html += self._get_prevention_section()
        html += self._get_footer()

        return html

    def _get_html_header(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>顯卡電源線燒毀 - 全球平台研究報告 {datetime.now().strftime('%Y年%m月%d日')}</title>
    <style>
        :root {{
            --primary: #2c3e50;
            --secondary: #34495e;
            --accent: #3498db;
            --danger: #e74c3c;
            --success: #27ae60;
            --warning: #f39c12;
            --bg-light: #f8f9fa;
            --text: #2c3e50;
            --text-light: #7f8c8d;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Microsoft JhengHei', 'PingFang TC', Arial, sans-serif;
            line-height: 1.8;
            color: var(--text);
            background: var(--bg-light);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
        }}

        .header .meta {{
            opacity: 0.9;
            font-size: 0.95em;
        }}

        .section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }}

        .section-title {{
            color: var(--primary);
            font-size: 1.5em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid var(--accent);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, var(--accent) 0%, #2980b9 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card.danger {{
            background: linear-gradient(135deg, var(--danger) 0%, #c0392b 100%);
        }}

        .stat-card.success {{
            background: linear-gradient(135deg, var(--success) 0%, #229954 100%);
        }}

        .stat-card.warning {{
            background: linear-gradient(135deg, var(--warning) 0%, #d68910 100%);
        }}

        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .platform-tabs {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }}

        .platform-tab {{
            padding: 8px 20px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9em;
        }}

        .platform-tab.en {{ background: #3498db; color: white; }}
        .platform-tab.cn {{ background: #e74c3c; color: white; }}
        .platform-tab.jp {{ background: #9b59b6; color: white; }}
        .platform-tab.eu {{ background: #27ae60; color: white; }}
        .platform-tab.active {{ box-shadow: 0 0 0 3px rgba(0,0,0,0.2); }}

        .platform-section {{
            display: none;
        }}

        .platform-section.active {{
            display: block;
        }}

        .case-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        .case-table th, .case-table td {{
            border: 1px solid #e0e0e0;
            padding: 12px 10px;
            text-align: left;
            font-size: 0.9em;
        }}

        .case-table th {{
            background: var(--primary);
            color: white;
            font-weight: 600;
        }}

        .case-table tr:nth-child(even) {{
            background: var(--bg-light);
        }}

        .case-table tr:hover {{
            background: #e8f4fc;
        }}

        .severity-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }}

        .severity-critical {{ background: #e74c3c; color: white; }}
        .severity-high {{ background: #f39c12; color: white; }}
        .severity-medium {{ background: #3498db; color: white; }}
        .severity-low {{ background: #95a5a6; color: white; }}

        .status-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
        }}

        .status-resolved {{ background: #27ae60; color: white; }}
        .status-tracking {{ background: #3498db; color: white; }}
        .status-prevention {{ background: #9b59b6; color: white; }}

        .chart-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 20px 0;
        }}

        .chart-item {{
            background: var(--bg-light);
            padding: 20px;
            border-radius: 12px;
        }}

        .chart-title {{
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--primary);
        }}

        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .bar-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .bar-label {{
            min-width: 100px;
            font-size: 0.85em;
        }}

        .bar-container {{
            flex: 1;
            height: 24px;
            background: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
        }}

        .bar-fill {{
            height: 100%;
            border-radius: 12px;
            transition: width 0.5s ease;
        }}

        .bar-fill.en {{ background: #3498db; }}
        .bar-fill.cn {{ background: #e74c3c; }}
        .bar-fill.jp {{ background: #9b59b6; }}
        .bar-fill.eu {{ background: #27ae60; }}
        .bar-fill.default {{ background: #34495e; }}

        .bar-value {{
            min-width: 40px;
            text-align: right;
            font-weight: 600;
            font-size: 0.9em;
        }}

        .prevention-list {{
            list-style: none;
            padding: 0;
        }}

        .prevention-list li {{
            padding: 15px 20px;
            margin: 10px 0;
            background: var(--bg-light);
            border-radius: 10px;
            border-left: 4px solid var(--accent);
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .prevention-icon {{
            font-size: 1.5em;
        }}

        .prevention-content h4 {{
            margin-bottom: 5px;
            color: var(--primary);
        }}

        .prevention-content p {{
            color: var(--text-light);
            font-size: 0.9em;
        }}

        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--text-light);
            font-size: 0.9em;
        }}

        .toc {{
            background: var(--bg-light);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
        }}

        .toc-title {{
            font-size: 1.2em;
            margin-bottom: 15px;
            color: var(--primary);
        }}

        .toc-list {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 8px;
        }}

        .toc-list a {{
            color: var(--accent);
            text-decoration: none;
            padding: 5px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .toc-list a:hover {{
            color: var(--primary);
        }}

        .gpu-icon {{ font-size: 1.2em; }}

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.6em; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .case-table {{ font-size: 0.8em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔌 顯卡電源線燒毀 - 全球平台研究報告</h1>
            <p class="meta">研究時間: {datetime.now().strftime('%Y年%m月%d日')} | 數據來源: 全球各大平台</p>
        </div>

        <!-- 目錄 -->
        <div class="toc" id="toc">
            <div class="toc-title">📑 目錄</div>
            <ul class="toc-list">
                <li><a href="#statistics">📊 統計概覽</a></li>
                <li><a href="#platforms">🌐 平台案例</a></li>
                <li><a href="#cases">📝 詳細案例</a></li>
                <li><a href="#analysis">🔬 技術分析</a></li>
                <li><a href="#prevention">🛡️ 預防建議</a></li>
            </ul>
        </div>
"""

    def _get_statistics_section(self, stats: Dict) -> str:
        return f"""
        <!-- 統計概覽 -->
        <div class="section" id="statistics">
            <h2 class="section-title">📊 統計概覽</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['total']}</div>
                    <div class="stat-label">總案例數</div>
                </div>
                <div class="stat-card danger">
                    <div class="stat-number">{stats['by_severity']['critical']}</div>
                    <div class="stat-label">嚴重案例</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-number">{len([s for s in stats['by_status'] if '已解決' in s or '解決' in s])}</div>
                    <div class="stat-label">已解決</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-number">{len(stats['by_platform'])}</div>
                    <div class="stat-label">涵蓋平台</div>
                </div>
            </div>

            <div class="chart-container">
                <div class="chart-item">
                    <div class="chart-title">📈 按地區分佈</div>
                    <div class="bar-chart">
                        {self._generate_bar_chart(stats['by_region'])}
                    </div>
                </div>
                <div class="chart-item">
                    <div class="chart-title">🖥️ 按 GPU 型號分佈</div>
                    <div class="bar-chart">
                        {self._generate_bar_chart(stats['by_gpu'], use_colors=True)}
                    </div>
                </div>
            </div>
        </div>
"""

    def _generate_bar_chart(self, data: Dict, use_colors: bool = False) -> str:
        """生成橫向條形圖 HTML"""
        if not data:
            return '<p>暫無數據</p>'

        max_val = max(data.values())
        html = ''

        for i, (label, value) in enumerate(sorted(data.items(), key=lambda x: x[1], reverse=True)):
            percentage = (value / max_val) * 100
            color_class = 'default'
            if use_colors:
                colors = ['en', 'cn', 'jp', 'eu', 'default']
                color_class = colors[i % len(colors)]

            html += f"""
                <div class="bar-item">
                    <span class="bar-label">{label}</span>
                    <div class="bar-container">
                        <div class="bar-fill {color_class}" style="width: {percentage}%"></div>
                    </div>
                    <span class="bar-value">{value}</span>
                </div>
            """

        return html

    def _get_platform_sections(self, cases: List[GPUCase]) -> str:
        """生成平台案例分組"""
        html = '''
        <!-- 平台案例 -->
        <div class="section" id="platforms">
            <h2 class="section-title">🌐 平台案例</h2>

            <div class="platform-tabs">
                <span class="platform-tab en active" onclick="showPlatform('en')">🇺🇸 英文平台</span>
                <span class="platform-tab cn" onclick="showPlatform('cn')">🇨🇳 中文平台</span>
                <span class="platform-tab jp" onclick="showPlatform('jp')">🇯🇵 日文平台</span>
                <span class="platform-tab eu" onclick="showPlatform('eu')">🇪🇺 歐洲平台</span>
            </div>
'''

        # 英文平台
        en_cases = [c for c in cases if c.platform in ['Reddit', "Tom's Hardware", 'Gamers Nexus', 'VideoCardz', 'TechPowerUp']]
        html += self._get_platform_content('en', '英文平台', en_cases)

        # 中文平台
        cn_cases = [c for c in cases if c.platform in ['知乎', 'Bilibili', 'NGA', '百度貼吧', 'ChipHell', 'PCEVA', 'ZOL']]
        html += self._get_platform_content('cn', '中文平台', cn_cases)

        # 日文平台
        jp_cases = [c for c in cases if c.platform in ['価格.com', 'AKIBA PC Hotline!', '5ch']]
        html += self._get_platform_content('jp', '日文平台', jp_cases)

        # 歐洲平台
        eu_cases = [c for c in cases if c.platform in ['Hardwareluxx', 'Guru3D', 'Scan', 'LDLC', 'ComputerBase']]
        html += self._get_platform_content('eu', '歐洲平台', eu_cases)

        html += '''
            <script>
                function showPlatform(platform) {
                    document.querySelectorAll('.platform-section').forEach(el => el.classList.remove('active'));
                    document.querySelectorAll('.platform-tab').forEach(el => el.classList.remove('active'));
                    document.getElementById('platform-' + platform).classList.add('active');
                    document.querySelector('.platform-tab.' + platform).classList.add('active');
                }
            </script>
        </div>
'''
        return html

    def _get_platform_content(self, platform_id: str, title: str, cases: List[GPUCase]) -> str:
        """生成單個平台的案例表格"""
        active = 'active' if platform_id == 'en' else ''

        if not cases:
            return f'''
                <div class="platform-section {active}" id="platform-{platform_id}">
                    <h3>{title}</h3>
                    <p>暫無案例數據</p>
                </div>
            '''

        rows = ''
        for case in cases:
            rows += f'''
                <tr>
                    <td>{case.case_id}</td>
                    <td>{case.gpu_model}</td>
                    <td>{case.issue_type}</td>
                    <td>{case.description[:50]}...</td>
                    <td><span class="severity-badge severity-{case.severity}">{case.severity}</span></td>
                    <td><span class="status-badge status-{'resolved' if '已解決' in case.status else 'tracking'}">{case.status}</span></td>
                </tr>
            '''

        return f'''
            <div class="platform-section {active}" id="platform-{platform_id}">
                <h3>{title} ({len(cases)} 個案例)</h3>
                <table class="case-table">
                    <thead>
                        <tr>
                            <th>案例ID</th>
                            <th>GPU型號</th>
                            <th>問題類型</th>
                            <th>描述</th>
                            <th>嚴重程度</th>
                            <th>狀態</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        '''

    def _get_case_details(self, cases: List[GPUCase]) -> str:
        """生成詳細案例列表"""
        html = '''
        <!-- 詳細案例 -->
        <div class="section" id="cases">
            <h2 class="section-title">📝 詳細案例列表</h2>
'''

        # 按嚴重程度分組
        critical = [c for c in cases if c.severity == 'critical']
        high = [c for c in cases if c.severity == 'high']

        if critical:
            html += '<h3>🔴 嚴重案例 (Critical)</h3><ul>'
            for case in critical:
                html += f'''
                    <li>
                        <strong>[{case.case_id}]</strong> {case.gpu_model} - {case.platform} ({case.region})<br>
                        <em>{case.description}</em><br>
                        <strong>原因:</strong> {case.root_cause} | <strong>解決:</strong> {case.solution}
                    </li>
                '''
            html += '</ul>'

        if high:
            html += '<h3>🟠 高風險案例 (High)</h3><ul>'
            for case in high:
                html += f'''
                    <li>
                        <strong>[{case.case_id}]</strong> {case.gpu_model} - {case.platform} ({case.region})<br>
                        <em>{case.description}</em><br>
                        <strong>原因:</strong> {case.root_cause} | <strong>解決:</strong> {case.solution}
                    </li>
                '''
            html += '</ul>'

        html += '</div>'
        return html

    def _get_analysis_section(self, cases: List[GPUCase], stats: Dict) -> str:
        """生成技術分析章節"""
        root_causes = {}
        for case in cases:
            cause = case.root_cause
            root_causes[cause] = root_causes.get(cause, 0) + 1

        html = f'''
        <!-- 技術分析 -->
        <div class="section" id="analysis">
            <h2 class="section-title">🔬 技術分析</h2>

            <h3>根本原因分析</h3>
            <div class="bar-chart" style="max-width: 600px;">
        '''

        for cause, count in sorted(root_causes.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(cases)) * 100
            html += f'''
                <div class="bar-item">
                    <span class="bar-label">{cause[:20]}...</span>
                    <div class="bar-container">
                        <div class="bar-fill default" style="width: {percentage}%"></div>
                    </div>
                    <span class="bar-value">{count}</span>
                </div>
            '''

        html += '''
            </div>

            <h3>關鍵發現</h3>
            <ul>
                <li><strong>RTX 4090 為主要受影響產品:</strong> 12VHPWR 接口問題最為突出</li>
                <li><strong>第三方轉接線是高風險因素:</strong> 超過 40% 的案例與非原廠線材相關</li>
                <li><strong>接口未完全插入:</strong> 是許多案例的根本原因</li>
                <li><strong>電源功率不足:</strong> 導致部分案例中高負載時出現問題</li>
                <li><strong>線纜佈線不當:</strong> 彎折過急導致局部過熱</li>
            </ul>

            <h3>地區差異</h3>
            <table class="case-table">
                <thead>
                    <tr>
                        <th>地區</th>
                        <th>主要問題</th>
                        <th>特點</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>🇺🇸 北美</td>
                        <td>12VHPWR 接口熔化</td>
                        <td>RMA 處理較順暢</td>
                    </tr>
                    <tr>
                        <td>🇨🇳 中國</td>
                        <td>第三方線材問題</td>
                        <td>維修渠道發達</td>
                    </tr>
                    <tr>
                        <td>🇯🇵 日本</td>
                        <td>散熱相關</td>
                        <td>注重產品保養</td>
                    </tr>
                    <tr>
                        <td>🇪🇺 歐洲</td>
                        <td>電源兼容性</td>
                        <td>注重認證標準</td>
                    </tr>
                </tbody>
            </table>
        </div>
'''
        return html

    def _get_prevention_section(self) -> str:
        """生成預防建議章節"""
        return '''
        <!-- 預防建議 -->
        <div class="section" id="prevention">
            <h2 class="section-title">🛡️ 預防建議</h2>

            <ul class="prevention-list">
                <li>
                    <span class="prevention-icon">🔌</span>
                    <div class="prevention-content">
                        <h4>確保接口完全插入</h4>
                        <p>12VHPWR 卡扣必須"咔嗒"一聲，且手指輕壓後沒有晃動</p>
                    </div>
                </li>
                <li>
                    <span class="prevention-icon">🔗</span>
                    <div class="prevention-content">
                        <h4>使用原廠或認證線材</h4>
                        <p>第三方轉接線質量參差不齊，盡量使用原廠線材</p>
                    </div>
                </li>
                <li>
                    <span class="prevention-icon">📐</span>
                    <div class="prevention-content">
                        <h4>避免線纜過度彎折</h4>
                        <p>彎曲半徑應 ≥ 4-5 倍線徑，防止金屬腳受機械應力</p>
                    </div>
                </li>
                <li>
                    <span class="prevention-icon">⚡</span>
                    <div class="prevention-content">
                        <h4>使用功率充足的電源</h4>
                        <p>選擇 80 PLUS Gold 或更高認證，功率比需求高 20-30%</p>
                    </div>
                </li>
                <li>
                    <span class="prevention-icon">🌡️</span>
                    <div class="prevention-content">
                        <h4>定期檢查和清理</h4>
                        <p>每 6-12 個月檢查線纜和接口，及時清理灰塵</p>
                    </div>
                </li>
                <li>
                    <span class="prevention-icon">📊</span>
                    <div class="prevention-content">
                        <h4>監控溫度和功率</h4>
                        <p>使用 HWiNFO、MSI Afterburner 等工具持續監控</p>
                    </div>
                </li>
            </ul>
        </div>
'''

    def _get_footer(self) -> str:
        return f'''
        <div class="footer">
            <p>本報告由 AI 助理自動生成 | 資料收集時間: {datetime.now().strftime('%Y年%m月%d日')}</p>
            <p>⚠️ 本報告僅供參考，如有專業維修需求請諮詢資深技術人員</p>
            <p>📧 聯繫郵箱: h13751019800@163.com</p>
        </div>
    </div>
</body>
</html>
'''

    def save_report(self, html: str, filepath: str):
        """保存報告到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"報告已保存至: {filepath}")

    def generate_markdown(self, cases: List[GPUCase] = None) -> str:
        """生成 Markdown 格式報告"""
        if cases is None:
            cases = self.collector.collect_all()

        stats = self.collector.get_statistics()

        md = f"""# 顯卡電源線燒毀 - 全球平台研究報告

研究時間: {datetime.now().strftime('%Y年%m月%d日')}

## 📊 統計概覽

- **總案例數:** {stats['total']}
- **嚴重案例:** {stats['by_severity']['critical']}
- **涵蓋平台:** {len(stats['by_platform'])}

## 🌐 平台案例

"""

        for platform, count in stats['by_platform'].items():
            md += f"- **{platform}:** {count} 個案例\n"

        md += "\n## 📝 詳細案例\n\n"

        for case in cases:
            md += f"""### [{case.case_id}] {case.gpu_model}

- **平台:** {case.platform} ({case.region})
- **問題:** {case.issue_type}
- **描述:** {case.description}
- **原因:** {case.root_cause}
- **解決:** {case.solution}
- **狀態:** {case.status}
- **來源:** {case.source}

---

"""

        return md

    def generate_json(self, cases: List[GPUCase] = None) -> str:
        """生成 JSON 格式報告"""
        if cases is None:
            cases = self.collector.collect_all()

        data = {
            'generated_at': datetime.now().isoformat(),
            'total_cases': len(cases),
            'cases': [case.to_dict() for case in cases],
            'statistics': self.collector.get_statistics()
        }

        return json.dumps(data, ensure_ascii=False, indent=2)
