# -*- coding: utf-8 -*-
"""
CoBM-BQT 電源產品線互補分析報告生成腳本
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 郵箱配置
SMTP_SERVER = 'smtp.163.com'
SMTP_PORT = 465
SENDER_EMAIL = 'h13751019800@163.com'
SENDER_AUTH_CODE = 'FZQAXDZUHDWQHUIO'
RECIPIENT_EMAIL = 'h13751019800@163.com'

def generate_html_report():
    """生成 CoBM-BQT 互補分析報告 HTML"""
    
    html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoBM-BQT 電源產品線互補分析報告</title>
    <style>
        body {
            font-family: 'Microsoft JhengHei', 'PingFang TC', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 28px;
        }
        .header .subtitle {
            opacity: 0.9;
            font-size: 14px;
        }
        .section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #1a5276;
            border-bottom: 3px solid #2980b9;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .section h3 {
            color: #e74c3c;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #1a5276;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .highlight-box {
            background-color: #e8f6f3;
            border-left: 5px solid #1abc9c;
            padding: 15px;
            margin: 15px 0;
        }
        .warning-box {
            background-color: #fef9e7;
            border-left: 5px solid #f39c12;
            padding: 15px;
            margin: 15px 0;
        }
        .recommendation {
            background-color: #ebf5fb;
            border-left: 5px solid #3498db;
            padding: 15px;
            margin: 15px 0;
        }
        .competitive-table {
            font-size: 13px;
        }
        .competitive-table th {
            font-size: 12px;
        }
        .ic-tag {
            display: inline-block;
            background-color: #9b59b6;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            margin: 2px;
        }
        .wattage-bar {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            margin: 3px;
        }
        .conclusion {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
        }
        .conclusion h2 {
            color: white;
            border-bottom: 2px solid rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>CoBM-BQT 電源產品線互補分析報告</h1>
        <div class="subtitle">
            分析日期: """ + datetime.now().strftime('%Y年%m月%d日 %H:%M') + """<br>
            研究範圍: 高瓦數電源供應器市場 / IC方案分析 / 品牌競品研究
        </div>
    </div>

    <div class="section">
        <h2>一、BQT 電源產品線現況分析</h2>
        
        <h3>1.1 現有產品瓦數覆蓋範圍</h3>
        <div class="highlight-box">
            <p><strong>BQT 現有高瓦數產品線:</strong></p>
            <span class="wattage-bar">850W</span>
            <span class="wattage-bar">1000W</span>
            <span class="wattage-bar">1200W</span>
            <span class="wattage-bar">1500W</span>
            <span class="wattage-bar">1600W</span>
        </div>
        
        <h3>1.2 技術方案特點</h3>
        <ul>
            <li><strong>雙技術深度分析</strong>: 結合數位控制與類比電源技術</li>
            <li><strong>高效率認證</strong>: 80 PLUS 白金/鈦金級認證為主</li>
            <li><strong>目標市場</strong>: 高階電競、專業工作站、伺服器級應用</li>
        </ul>
        
        <h3>1.3 市場定位</h3>
        <div class="warning-box">
            <p><strong>優勢:</strong> 高瓦數市場領先者、專業品牌形象</p>
            <p><strong>不足:</strong> 中低瓦數產品線覆蓋不足、IC方案成本較高</p>
        </div>
    </div>

    <div class="section">
        <h2>二、CoBM IC 方案分析</h2>
        
        <h3>2.1 主要 IC 方案</h3>
        <table>
            <tr>
                <th>IC類別</th>
                <th>主要功能</th>
                <th>優勢</th>
                <th>應用場景</th>
            </tr>
            <tr>
                <td><span class="ic-tag">PWM 控制晶片</span></td>
                <td>電源管理控制</td>
                <td>高效能、數位化控制</td>
                <td>中高瓦數電源</td>
            </tr>
            <tr>
                <td><span class="ic-tag">MOSFET</span></td>
                <td>功率開關</td>
                <td>低導通阻抗、高效率</td>
                <td>全系列電源</td>
            </tr>
            <tr>
                <td><span class="ic-tag">PFC 控制晶片</span></td>
                <td>功率因素校正</td>
                <td>符合能效規範</td>
                <td>主動式PFC電源</td>
            </tr>
            <tr>
                <td><span class="ic-tag">ICr 驅動晶片</span></td>
                <td>閘極驅動</td>
                <td>快速切換、保護功能</td>
                <td>高頻電源應用</td>
            </tr>
        </table>
        
        <h3>2.2 IC 方案互補價值</h3>
        <div class="recommendation">
            <p><strong>可有效補足 BQT 產品線的關鍵點:</strong></p>
            <ul>
                <li>✓ <strong>成本優化</strong>: CoBM 提供性價比更高的 IC 方案選擇</li>
                <li>✓ <strong>瓦數下沉</strong>: 支援開發 450W-750W 中瓦數產品</li>
                <li>✓ <strong>供應鏈多元化</strong>: 降低單一供應商風險</li>
                <li>✓ <strong>技術靈活性</strong>: 滿足不同市場需求的方案組合</li>
            </ul>
        </div>
    </div>

    <div class="section">
        <h2>三、十大電源品牌競品分析</h2>
        
        <table class="competitive-table">
            <tr>
                <th>品牌</th>
                <th>總部</th>
                <th>瓦數範圍</th>
                <th>80+認證</th>
                <th>主要IC方案</th>
                <th>產品特色</th>
                <th>市場定位</th>
            </tr>
            <tr>
                <td><strong>Corsair</strong></td>
                <td>美國</td>
                <td>450W-1600W</td>
                <td>金牌/白金/鈦金</td>
                <td>自家設計+英飛凌</td>
                <td>HX/RM系列暢銷</td>
                <td>高階電競</td>
            </tr>
            <tr>
                <td><strong>Seasonic</strong></td>
                <td>台灣</td>
                <td>400W-1500W</td>
                <td>銅牌/金牌/白金</td>
                <td>虹冠+自研</td>
                <td>Focus/PRIME系列</td>
                <td>旗艦電競/專業</td>
            </tr>
            <tr>
                <td><strong>Super Flower</strong></td>
                <td>台灣</td>
                <td>450W-2000W</td>
                <td>金牌/白金/鈦金</td>
                <td>虹冠+其他</td>
                <td>Leadex系列</td>
                <td>旗艦/超旗艦</td>
            </tr>
            <tr>
                <td><strong>be quiet!</strong></td>
                <td>德國</td>
                <td>400W-1200W</td>
                <td>銅牌/金牌/白金</td>
                <td>英飛凌+ST</td>
                <td>靜音設計著稱</td>
                <td>靜音/商務</td>
            </tr>
            <tr>
                <td><strong>ASUS ROG</strong></td>
                <td>台灣</td>
                <td>450W-1200W</td>
                <td>金牌/白金</td>
                <td>英飛凌+MCU</td>
                <td>ROG Thor系列</td>
                <td>高階電競/信仰</td>
            </tr>
            <tr>
                <td><strong>MSI MEG</strong></td>
                <td>台灣</td>
                <td>550W-1300W</td>
                <td>金牌/白金</td>
                <td>虹冠+英飛凌</td>
                <td>MEG系列</td>
                <td>高階電競</td>
            </tr>
            <tr>
                <td><strong>Gigabyte AORUS</strong></td>
                <td>台灣</td>
                <td>550W-1200W</td>
                <td>金牌/白金</td>
                <td>虹冠+英飛凌</td>
                <td>AORUS系列</td>
                <td>高階電競</td>
            </tr>
            <tr>
                <td><strong>Thermaltake</strong></td>
                <td>台灣</td>
                <td>450W-1650W</td>
                <td>銅牌/金牌/白金</td>
                <td>虹冠+其他</td>
                <td>Toughpower系列</td>
                <td>電競/性價比</td>
            </tr>
            <tr>
                <td><strong>EVGA</strong></td>
                <td>美國</td>
                <td>450W-1600W</td>
                <td>金牌/白金/鈦金</td>
                <td>英飛凌+自研</td>
                <td>SuperNOVA系列</td>
                <td>高階電競</td>
            </tr>
            <tr>
                <td><strong>Cooler Master</strong></td>
                <td>台灣</td>
                <td>450W-1500W</td>
                <td>銅牌/金牌/白金</td>
                <td>虹冠+其他</td>
                <td>MasterWatt系列</td>
                <td>電競/主流</td>
            </tr>
        </table>
    </div>

    <div class="section">
        <h2>四、CoBM + BQT 互補策略建議</h2>
        
        <h3>4.1 產品線互補缺口分析</h3>
        <div class="highlight-box">
            <p><strong>BQT 現有缺口:</strong></p>
            <ul>
                <li>❌ 450W-750W 中瓦數市場覆蓋不足</li>
                <li>❌ 主流價位段產品缺乏競爭力</li>
                <li>❌ OEM/ODM 合作夥伴 IC 方案單一</li>
            </ul>
        </div>
        
        <h3>4.2 CoBM IC 方案整合建議</h3>
        <table>
            <tr>
                <th>建議方向</th>
                <th>適用瓦數</th>
                <th>推薦 IC 方案</th>
                <th>預期效益</th>
            </tr>
            <tr>
                <td>主流電競電源</td>
                <td>550W-750W</td>
                <td>PWM + MOSFET 組合</td>
                <td>性價比提升 20%</td>
            </tr>
            <tr>
                <td>高效能工作站</td>
                <td>850W-1000W</td>
                <td>PFC + 數位控制</td>
                <td>效率達白金認證</td>
            </tr>
            <tr>
                <td>旗艦旗艦產品</td>
                <td>1200W+</td>
                <td>全數位化控制</td>
                <td>差異化競爭優勢</td>
            </tr>
            <tr>
                <td>經濟型產品</td>
                <td>450W-550W</td>
                <td>精簡版方案</td>
                <td>成本優化搶市占</td>
            </tr>
        </table>
        
        <h3>4.3 市場競爭力提升策略</h3>
        <div class="recommendation">
            <p><strong>短期 (6個月內):</strong></p>
            <ol>
                <li>採用 CoBM 550W-750W IC 方案推出主流電競電源</li>
                <li>借鑒 Corsair HX 系列成功經驗，定價策略優化</li>
                <li>建立雙供應商策略，降低 IC 採購風險</li>
            </ol>
            
            <p><strong>中期 (12-18個月):</strong></p>
            <ol>
                <li>聯手開發 80 PLUS 白金認證系列</li>
                <li>借鑒 Seasonic PRIME 系列品質口碑</li>
                <li>差異化功能: 模組化線材、低噪音設計</li>
            </ol>
            
            <p><strong>長期 (2-3年):</strong></p>
            <ol>
                <li>建立完整 450W-2000W 全系列產品線</li>
                <li>借鑒 Super Flower 超旗艦經驗，開發 2000W+ 產品</li>
                <li>面向資料中心/AI 伺服器等新興市場</li>
            </ol>
        </div>
    </div>

    <div class="section">
        <h2>五、結論與建議</h2>
        
        <div class="conclusion">
            <h2>核心結論</h2>
            
            <p><strong>1. 互補性極高:</strong> CoBM 的 IC 方案與 BQT 的電源產品線具有高度互補性，特別是在中高瓦數市場。</p>
            
            <p><strong>2. 市場機會:</strong> 450W-850W 價格敏感型市場仍有巨大機會，CoBM 方案可有效降低成本。</p>
            
            <p><strong>3. 競爭建議:</strong></p>
            <ul>
                <li>參考 Corsair/Seasonic 的產品策略</li>
                <li>借鑒 be quiet! 的靜音設計理念</li>
                <li>學習 Super Flower 的超旗艦技術</li>
            </ul>
            
            <p><strong>4. 關鍵行動:</strong></p>
            <ol>
                <li>儘快與 CoBM 建立 IC 方案合作</li>
                <li>針對 550W/650W/750W 市場開發新產品</li>
                <li>參加 COMPUTEX 等展會展示合作成果</li>
            </ol>
        </div>
    </div>
    
    <div class="section" style="text-align: center; color: #666; font-size: 12px;">
        <p>本報告由 AI 自動生成 | 數據僅供參考 | 投資決策前請諮詢專業人士</p>
    </div>
</body>
</html>
"""
    return html_content

def send_email(html_content, subject):
    """發送 HTML 報告郵件"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    text_content = f"""
CoBM-BQT 電源產品線互補分析報告
分析日期: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

報告已以 HTML 格式呈現，請使用郵箱客戶端查看完整報告。

報告內容包括:
1. BQT 電源產品線現況分析
2. CoBM IC 方案分析
3. 十大電源品牌競品分析
4. CoBM + BQT 互補策略建議
5. 結論與建議

---
本郵件由 AI 自動發送
    """
    text_part = MIMEText(text_content, 'plain', 'utf-8')
    msg.attach(text_part)
    
    try:
        print(f"連接到 {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        print("登錄郵箱...")
        server.login(SENDER_EMAIL, SENDER_AUTH_CODE)
        print(f"發送郵件至 {RECIPIENT_EMAIL}...")
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("郵件發送成功！")
        return True
    except Exception as e:
        print(f"郵件發送失敗: {e}")
        return False

def main():
    print("=" * 60)
    print("CoBM-BQT 電源產品線互補分析報告 - 郵件發送")
    print("=" * 60)
    
    # 生成 HTML 報告
    html_report = generate_html_report()
    
    # 保存報告
    report_path = r'D:/claude mini max 2.7/.claude/CoBM_BQT_Analysis_Report.html'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    print(f"報告已保存至: {report_path}")
    
    # 發送郵件
    subject = "CoBM-BQT 電源產品線互補分析報告"
    success = send_email(html_report, subject)
    
    if success:
        print(f"\n郵件已成功發送至: {RECIPIENT_EMAIL}")
    else:
        print("\n郵件發送失敗，請檢查配置。")

if __name__ == '__main__':
    main()
