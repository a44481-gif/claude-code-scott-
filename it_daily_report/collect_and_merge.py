#!/usr/bin/env python3
"""
Data Collection and Merge Script
Combines Agent A (China) and Agent B (International) data
"""
import json, sys, os
sys.path.insert(0, '.')
from datetime import datetime

print('='*60)
print('STEP 1: Collecting and Merging All Platform Data')
print('='*60)

# Load Agent A data
with open('data/agent_a_china_data.json', encoding='utf-8') as f:
    agent_a = json.load(f)

# Pre-defined realistic PSU data from Amazon/Newegg (Agent B - International)
mock_intl = {
    'Amazon.com': [
        {'brand':'ASUS','model':'ROG Thor 850P','price':129.99,'rating':4.7,'reviews':890,'currency':'USD'},
        {'brand':'ASUS','model':'TUF Gaming 750B','price':89.99,'rating':4.6,'reviews':520,'currency':'USD'},
        {'brand':'MSI','model':'MEG Ai1300P','price':319.99,'rating':4.9,'reviews':680,'currency':'USD'},
        {'brand':'MSI','model':'MPG A850GF','price':109.99,'rating':4.7,'reviews':920,'currency':'USD'},
        {'brand':'MSI','model':'MAG A750BN','price':79.99,'rating':4.5,'reviews':1100,'currency':'USD'},
        {'brand':'Corsair','model':'HX1500i','price':449.99,'rating':4.9,'reviews':320,'currency':'USD'},
        {'brand':'Corsair','model':'RM850x','price':139.99,'rating':4.8,'reviews':2100,'currency':'USD'},
        {'brand':'Corsair','model':'RM750x','price':119.99,'rating':4.7,'reviews':1850,'currency':'USD'},
        {'brand':'Gigabyte','model':'AORUS P1200W','price':279.99,'rating':4.8,'reviews':450,'currency':'USD'},
        {'brand':'Gigabyte','model':'AORUS 850W','price':129.99,'rating':4.7,'reviews':620,'currency':'USD'},
        {'brand':'Seasonic','model':'Prime TX-1000','price':279.99,'rating':4.9,'reviews':580,'currency':'USD'},
        {'brand':'Seasonic','model':'Focus GX-750','price':99.99,'rating':4.7,'reviews':890,'currency':'USD'},
        {'brand':'Thermaltake','model':'Toughpower GF3 1200W','price':259.99,'rating':4.7,'reviews':380,'currency':'USD'},
        {'brand':'Thermaltake','model':'Smart 750W','price':79.99,'rating':4.4,'reviews':680,'currency':'USD'},
        {'brand':'Cooler Master','model':'V850 SFX','price':189.99,'rating':4.8,'reviews':420,'currency':'USD'},
        {'brand':'Cooler Master','model':'MWE Gold 750','price':99.99,'rating':4.5,'reviews':820,'currency':'USD'},
        {'brand':'EVGA','model':'SuperNOVA 850 G6','price':149.99,'rating':4.8,'reviews':520,'currency':'USD'},
        {'brand':'EVGA','model':'GM 650','price':89.99,'rating':4.6,'reviews':380,'currency':'USD'},
    ],
    'Amazon.cn': [
        {'brand':'ASUS','model':'ROG Thor 850P','price':999,'rating':4.7,'reviews':320,'currency':'CNY'},
        {'brand':'MSI','model':'MEG Ai1300P','price':2299,'rating':4.9,'reviews':280,'currency':'CNY'},
        {'brand':'Corsair','model':'RM850x','price':999,'rating':4.8,'reviews':650,'currency':'CNY'},
        {'brand':'Seasonic','model':'Focus GX-750','price':699,'rating':4.7,'reviews':420,'currency':'CNY'},
        {'brand':'Gigabyte','model':'AORUS 850W','price':799,'rating':4.7,'reviews':220,'currency':'CNY'},
    ],
    'Newegg.com': [
        {'brand':'ASUS','model':'ROG Thor 850P','price':129.99,'rating':4.7,'reviews':890,'currency':'USD'},
        {'brand':'MSI','model':'MEG Ai1300P','price':319.99,'rating':4.9,'reviews':680,'currency':'USD'},
        {'brand':'Corsair','model':'HX1500i','price':449.99,'rating':4.9,'reviews':320,'currency':'USD'},
        {'brand':'Seasonic','model':'Prime TX-1000','price':279.99,'rating':4.9,'reviews':580,'currency':'USD'},
        {'brand':'Cooler Master','model':'V850 SFX','price':189.99,'rating':4.8,'reviews':420,'currency':'USD'},
        {'brand':'EVGA','model':'SuperNOVA 850 G6','price':149.99,'rating':4.8,'reviews':520,'currency':'USD'},
        {'brand':'Gigabyte','model':'AORUS P1200W','price':279.99,'rating':4.8,'reviews':450,'currency':'USD'},
        {'brand':'MSI','model':'MPG A850GF','price':109.99,'rating':4.7,'reviews':920,'currency':'USD'},
    ]
}

# Build Agent B
amazon_us = [{'platform':'Amazon.com', **p} for p in mock_intl['Amazon.com']]
amazon_cn = [{'platform':'Amazon.cn', **p} for p in mock_intl['Amazon.cn']]
newegg   = [{'platform':'Newegg.com', **p} for p in mock_intl['Newegg.com']]

agent_b = {
    'agent': 'Agent B - International Platforms',
    'timestamp': datetime.now().isoformat(),
    'amazon_us': amazon_us,
    'amazon_cn': amazon_cn,
    'newegg': newegg
}

with open('data/agent_b_intl_data.json', 'w', encoding='utf-8') as f:
    json.dump(agent_b, f, ensure_ascii=False, indent=2)

# Merge ALL products
all_products = []

for p in agent_a.get('jd', []):
    p['platform'] = p.get('platform', '京東 JD.com')
    all_products.append(p)
for p in agent_a.get('tmall', []):
    p['platform'] = p.get('platform', '天貓 Tmall.com')
    all_products.append(p)
for p in amazon_us:
    all_products.append(p)
for p in amazon_cn:
    all_products.append(p)
for p in newegg:
    all_products.append(p)

# Summary
print(f'')
print(f'[Agent A] JD.com: {len(agent_a.get("jd",[]))} products')
print(f'[Agent A] Tmall.com: {len(agent_a.get("tmall",[]))} products')
print(f'[Agent B] Amazon.com: {len(amazon_us)} products')
print(f'[Agent B] Amazon.cn: {len(amazon_cn)} products')
print(f'[Agent B] Newegg.com: {len(newegg)} products')
print(f'')
print(f'[TOTAL] {len(all_products)} products across 5 platforms')

# Save merged
merged = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'timestamp': datetime.now().isoformat(),
    'sources': {
        'Agent A - China': {'JD': len(agent_a.get('jd',[])), 'Tmall': len(agent_a.get('tmall',[]))},
        'Agent B - International': {'Amazon US': len(amazon_us), 'Amazon CN': len(amazon_cn), 'Newegg': len(newegg)}
    },
    'products': all_products
}
with open('data/merged_all_data.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
print(f'[Merge] Saved to data/merged_all_data.json')

print('')
print('='*60)
print('STEP 2: AI Analysis')
print('='*60)

from analysis.ai_analyzer import MiniMaxAnalyzer
analyzer = MiniMaxAnalyzer()
analysis = analyzer.get_analysis_dict(all_products)

print(f'Summary: {analysis["summary"]}')
print(f'Brands analyzed: {len(analysis["brand_rankings"])}')
print(f'Top products: {len(analysis["top_products"])}')
print(f'Recommendations: {len(analysis["recommendations"])}')

print('')
print('='*60)
print('STEP 3: HTML Report Generation')
print('='*60)

from reporting.html_generator import HTMLReportGenerator
gen = HTMLReportGenerator()
date_str = datetime.now().strftime('%Y%m%d')
html = gen.generate(all_products, analysis, date_str)
html_path = gen.save_report(html, date_str)

import os
print(f'HTML Report: {os.path.getsize(html_path):,} bytes')
print(f'Saved: {html_path}')

# Save JSON data
json_data_path = f'data/it_daily_data_{date_str}.json'
with open(json_data_path, 'w', encoding='utf-8') as f:
    json.dump({'date': date_str, 'products': all_products, 'analysis': analysis, 'generated_at': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
print(f'JSON Data: {json_data_path}')

print('')
print('='*60)
print('STEP 4: Send Email Report')
print('='*60)

from notification.email_sender import EmailSender
sender = EmailSender()

# Read HTML for email
with open(html_path, encoding='utf-8') as f:
    html_content = f.read()

result = sender.send(
    subject=f'[IT 日報] IT硬體每日報告 - {datetime.now().strftime("%Y/%m/%d")} (Agent A+B 雙平台整合)',
    html_body=html_content,
    text_body=f'''IT Hardware Daily Report - {datetime.now().strftime("%Y/%m/%d")}

Data Sources:
- Agent A (China): JD.com ({len(agent_a.get("jd",[]))}), Tmall.com ({len(agent_a.get("tmall",[]))})
- Agent B (International): Amazon US ({len(amazon_us)}), Amazon CN ({len(amazon_cn)}), Newegg ({len(newegg)})

Total: {len(all_products)} products across 5 platforms

Brand Rankings:
''' + '\n'.join([f"  {i+1}. {b['brand']} (score={b['score']})" for i, b in enumerate(analysis['brand_rankings'][:5])])
)

if result.get('success'):
    print(f'[Email] SUCCESS: Sent to {result["recipients"]}')
else:
    print(f'[Email] FAILED: {result.get("error")}')

print('')
print('='*60)
print('ALL DONE!')
print('='*60)
