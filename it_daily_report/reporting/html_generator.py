"""
HTML Report Generator for IT Hardware Daily Report
Generates beautiful HTML reports with CSS styling
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class HTMLReportGenerator:
    """Generate精美的HTML daily report"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

    def generate(
        self,
        products: List[Dict],
        analysis: Dict,
        date_str: Optional[str] = None
    ) -> str:
        """Generate complete HTML report"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        today_full = datetime.now().strftime('%Y年%m月%d日 %H:%M')

        # Calculate summary stats
        stats = self._calc_stats(products)
        platform_counts = self._count_by_platform(products)
        brand_counts = self._count_by_brand(products)

        # Build HTML
        html = self._html_header()
        html += self._html_head(date_str)
        html += self._html_body(stats, analysis, products, platform_counts, brand_counts, today_full)
        html += self._html_footer()
        return html

    def _calc_stats(self, products: List[Dict]) -> Dict:
        prices = [p['price'] for p in products if p.get('price')]
        ratings = [p['rating'] for p in products if p.get('rating')]
        reviews = [p['reviews'] for p in products if p.get('reviews')]

        return {
            'total': len(products),
            'avg_price': round(sum(prices) / len(prices), 2) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'avg_rating': round(sum(ratings) / len(ratings), 1) if ratings else 0,
            'total_reviews': sum(reviews) if reviews else 0,
            'brands': len(set(p.get('brand') for p in products)),
            'platforms': len(set(p.get('platform') for p in products)),
        }

    def _count_by_platform(self, products: List[Dict]) -> Dict[str, int]:
        counts = {}
        for p in products:
            plat = p.get('platform', 'Unknown')
            counts[plat] = counts.get(plat, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _count_by_brand(self, products: List[Dict]) -> Dict[str, int]:
        counts = {}
        for p in products:
            brand = p.get('brand', 'Unknown')
            counts[brand] = counts.get(brand, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def _html_header(self) -> str:
        return '<!DOCTYPE html>\n<html lang="zh-TW">\n'

    def _html_head(self, date_str: str) -> str:
        return f"""
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IT Hardware Daily Report - {date_str}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #f0f2f5;
    color: #1a1a2e;
    line-height: 1.6;
  }}

  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }}

  /* Header */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 40px 30px;
    border-radius: 16px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }}
  .header::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
  }}
  .header h1 {{
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
  }}
  .header .subtitle {{
    font-size: 14px;
    opacity: 0.8;
  }}
  .header .date-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.15);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    margin-top: 10px;
  }}

  /* Summary Cards */
  .summary-cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }}
  .card {{
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.2s;
  }}
  .card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  }}
  .card .label {{
    font-size: 12px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }}
  .card .value {{
    font-size: 24px;
    font-weight: 700;
    color: #1a1a2e;
  }}
  .card .value.primary {{ color: #e94560; }}
  .card .value.success {{ color: #0f9b6e; }}
  .card .value.info {{ color: #0f3460; }}
  .card .sub {{ font-size: 12px; color: #aaa; margin-top: 4px; }}

  /* Section */
  .section {{
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .section h2 {{
    font-size: 18px;
    color: #1a1a2e;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f0f0f0;
  }}
  .section h2 .icon {{
    margin-right: 8px;
  }}

  /* Brand Rankings */
  .brand-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
  }}
  .brand-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    background: #f8f9fa;
    border-left: 4px solid #e94560;
  }}
  .brand-item.gold {{ border-left-color: #ffd700; background: #fffdf0; }}
  .brand-item.silver {{ border-left-color: #c0c0c0; background: #f9f9f9; }}
  .brand-item.bronze {{ border-left-color: #cd7f32; background: #fdf8f5; }}
  .brand-rank {{
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #e94560;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 13px;
    flex-shrink: 0;
  }}
  .brand-rank.gold {{ background: #ffd700; color: #333; }}
  .brand-rank.silver {{ background: #c0c0c0; color: #333; }}
  .brand-rank.bronze {{ background: #cd7f32; color: white; }}
  .brand-info {{ flex: 1; }}
  .brand-name {{ font-weight: 600; font-size: 14px; }}
  .brand-detail {{ font-size: 12px; color: #888; }}
  .brand-score {{
    font-weight: 700;
    font-size: 16px;
    color: #e94560;
  }}

  /* Top Products Table */
  .products-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  .products-table th {{
    text-align: left;
    padding: 10px 12px;
    font-size: 12px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 2px solid #f0f0f0;
  }}
  .products-table td {{
    padding: 12px;
    font-size: 14px;
    border-bottom: 1px solid #f5f5f5;
  }}
  .products-table tr:hover {{
    background: #fafafa;
  }}
  .rating-stars {{
    color: #f5a623;
    font-weight: 700;
  }}
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
  }}
  .badge.hot {{ background: #fff3e0; color: #e65100; }}
  .badge.new {{ background: #e3f2fd; color: #1565c0; }}
  .badge.normal {{ background: #f5f5f5; color: #666; }}

  /* AI Insights */
  .insight-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 12px;
  }}
  .insight-item {{
    display: flex;
    gap: 10px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
  }}
  .insight-icon {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: linear-gradient(135deg, #e94560, #0f3460);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 14px;
  }}
  .insight-text {{
    font-size: 13px;
    color: #444;
    line-height: 1.5;
  }}

  /* Recommendations */
  .recommendation-list {{
    list-style: none;
  }}
  .recommendation-list li {{
    padding: 10px 14px;
    margin-bottom: 8px;
    background: linear-gradient(90deg, #f8f9fa, transparent);
    border-left: 3px solid #e94560;
    border-radius: 0 6px 6px 0;
    font-size: 14px;
  }}
  .recommendation-list li::before {{
    content: '✓ ';
    color: #e94560;
    font-weight: 700;
  }}

  /* Platform Chart (CSS bar) */
  .platform-chart {{
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .platform-bar {{
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .platform-name {{
    width: 100px;
    font-size: 13px;
    flex-shrink: 0;
  }}
  .bar-track {{
    flex: 1;
    height: 20px;
    background: #f0f0f0;
    border-radius: 10px;
    overflow: hidden;
  }}
  .bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #0f3460, #e94560);
    border-radius: 10px;
    display: flex;
    align-items: center;
    padding-left: 10px;
    color: white;
    font-size: 11px;
    font-weight: 600;
    transition: width 0.6s ease;
  }}
  .platform-count {{
    width: 40px;
    font-size: 13px;
    color: #888;
    text-align: right;
  }}

  /* Price Distribution */
  .price-range {{
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }}
  .price-chip {{
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
  }}
  .price-chip.low {{ background: #e8f5e9; color: #2e7d32; }}
  .price-chip.mid {{ background: #fff8e1; color: #f57c00; }}
  .price-chip.high {{ background: #ffebee; color: #c62828; }}

  /* Footer */
  .footer {{
    text-align: center;
    padding: 20px;
    color: #aaa;
    font-size: 12px;
  }}

  /* Responsive */
  @media (max-width: 768px) {{
    .container {{ padding: 12px; }}
    .header h1 {{ font-size: 22px; }}
    .summary-cards {{ grid-template-columns: repeat(2, 1fr); }}
    .products-table {{ font-size: 12px; }}
  }}
</style>
</head>
"""

    def _html_body(self, stats: Dict, analysis: Dict, products: List[Dict],
                    platform_counts: Dict, brand_counts: Dict, today_full: str) -> str:
        # Get top products
        top_products = analysis.get('top_products', [])[:8]

        # Brand rankings
        brand_rankings = analysis.get('brand_rankings', [])[:8]

        # Get top 3 brands for CSS rank classes
        rank_classes = ['gold', 'silver', 'bronze'] + [''] * 10

        # Platform max for bar chart
        max_count = max(platform_counts.values()) if platform_counts else 1

        return f"""
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>IT Hardware Daily Report</h1>
    <div class="subtitle">電源供應器 · 顯示卡 · 遊戲筆電 市場每日監測</div>
    <div class="date-badge">📅 {today_full}</div>
  </div>

  <!-- Summary Cards -->
  <div class="summary-cards">
    <div class="card">
      <div class="label">監測產品</div>
      <div class="value primary">{stats['total']}</div>
      <div class="sub">{stats['brands']} 品牌 / {stats['platforms']} 平台</div>
    </div>
    <div class="card">
      <div class="label">平均價格</div>
      <div class="value">${stats['avg_price']:.0f}</div>
      <div class="sub">${stats['min_price']:.0f} ~ ${stats['max_price']:.0f}</div>
    </div>
    <div class="card">
      <div class="label">平均評分</div>
      <div class="value success">{stats['avg_rating']} ★</div>
      <div class="sub">總評論 {stats['total_reviews']:,} 條</div>
    </div>
    <div class="card">
      <div class="label">市場概覽</div>
      <div class="value info">{analysis.get('summary', 'N/A')[:30]}...</div>
      <div class="sub">AI 智能分析</div>
    </div>
  </div>

  <!-- AI Insights -->
  <div class="section">
    <h2><span class="icon">🤖</span>AI 市場洞察</h2>
    <div class="insight-grid">
      {self._render_insights(analysis.get('key_insights', []))}
    </div>
  </div>

  <!-- Brand Rankings -->
  <div class="section">
    <h2><span class="icon">🏆</span>品牌競爭力排名</h2>
    <div class="brand-grid">
      {self._render_brand_rankings(brand_rankings, rank_classes)}
    </div>
  </div>

  <!-- Top Products -->
  <div class="section">
    <h2><span class="icon">⭐</span>重點產品推薦</h2>
    <table class="products-table">
      <thead>
        <tr>
          <th>#</th>
          <th>品牌型號</th>
          <th>價格</th>
          <th>評分</th>
          <th>評論</th>
          <th>平台</th>
          <th>評價</th>
        </tr>
      </thead>
      <tbody>
        {self._render_product_rows(top_products)}
      </tbody>
    </table>
  </div>

  <!-- Price Analysis -->
  <div class="section">
    <h2><span class="icon">💰</span>價格區間分析</h2>
    <p style="margin-bottom: 16px; color: #666; font-size: 14px;">{analysis.get('price_analysis', '價格數據不足')}</p>
    <div class="price-range">
      <span class="price-chip low">💚 入門級 ${stats['avg_price']*0.6:.0f} 以下</span>
      <span class="price-chip mid">🧡 主流級 ${stats['avg_price']*0.6:.0f} - ${stats['avg_price']*1.5:.0f}</span>
      <span class="price-chip high">❤ 高端級 ${stats['avg_price']*1.5:.0f} 以上</span>
    </div>
  </div>

  <!-- Platform Distribution -->
  <div class="section">
    <h2><span class="icon">🌐</span>平台分佈</h2>
    <div class="platform-chart">
      {self._render_platform_bars(platform_counts, max_count)}
    </div>
  </div>

  <!-- Recommendations -->
  <div class="section">
    <h2><span class="icon">📋</span>行動建議</h2>
    <ul class="recommendation-list">
      {self._render_recommendations(analysis.get('recommendations', []))}
    </ul>
  </div>

  <!-- Market Trends -->
  {self._render_market_trends(analysis.get('market_trends', []))}

  <!-- Footer -->
  <div class="footer">
    IT Hardware Daily Report · 自動生成 · {today_full}<br>
    數據來源：京東 · 天貓 · Amazon · Newegg
  </div>

</div>
</body>
</html>
"""

    def _render_insights(self, insights: List[str]) -> str:
        if not insights:
            return '<div class="insight-item"><div class="insight-icon">💡</div><div class="insight-text">暫無洞察數據</div></div>'
        icons = ['📊', '🔍', '🎯', '💡', '⚡', '📈']
        return '\n'.join(
            f'<div class="insight-item"><div class="insight-icon">{icons[i % len(icons)]}</div>'
            f'<div class="insight-text">{text}</div></div>'
            for i, text in enumerate(insights)
        )

    def _render_brand_rankings(self, rankings: List[Dict], rank_classes: List[str]) -> str:
        if not rankings:
            return '<div class="brand-item"><div class="brand-info">暫無排名數據</div></div>'
        html_parts = []
        for i, brand in enumerate(ratings := rankings):
            cls = rank_classes[i] if i < len(rank_classes) else ''
            rank_label = {0: '🥇', 1: '🥈', 2: '🥉'}.get(i, str(i + 1))
            html_parts.append(f"""
      <div class="brand-item {cls}">
        <div class="brand-rank {'gold' if i==0 else 'silver' if i==1 else 'bronze' if i==2 else ''}">{rank_label}</div>
        <div class="brand-info">
          <div class="brand-name">{brand.get('brand', 'N/A')}</div>
          <div class="brand-detail">均價 ${brand.get('avg_price', 0):.0f} · 評分 {brand.get('avg_rating', 0):.1f}★</div>
        </div>
        <div class="brand-score">{brand.get('score', 0):.1f}</div>
      </div>""")
        return '\n'.join(html_parts)

    def _render_product_rows(self, products: List[Dict]) -> str:
        if not products:
            return '<tr><td colspan="7" style="text-align:center;color:#aaa;padding:20px;">暫無產品數據</td></tr>'
        rows = []
        for i, p in enumerate(products):
            rating = p.get('rating', 0)
            stars = '★' * int(rating) + '☆' * (5 - int(rating)) if rating else 'N/A'
            badge = 'hot' if rating >= 4.8 else 'new' if i < 3 else 'normal'
            badge_text = {0: '🔥 熱銷', 1: '✨ 新銳', 2: '👍 人氣'}.get(i, '推薦')
            rows.append(f"""
        <tr>
          <td>{i + 1}</td>
          <td><strong>{p.get('brand', '')}</strong> {p.get('model', '')}</td>
          <td><strong>{p.get('currency', '$')}{p.get('price', 0):.2f}</strong></td>
          <td><span class="rating-stars">{stars}</span> {rating:.1f}</td>
          <td>{p.get('reviews', 0):,}</td>
          <td>{p.get('platform', 'N/A')}</td>
          <td><span class="badge {badge}">{badge_text}</span></td>
        </tr>""")
        return '\n'.join(rows)

    def _render_platform_bars(self, counts: Dict, max_count: int) -> str:
        if not counts:
            return '<div class="platform-bar"><div class="platform-name">無數據</div></div>'
        return '\n'.join(
            f'<div class="platform-bar">'
            f'<div class="platform-name">{platform}</div>'
            f'<div class="bar-track">'
            f'<div class="bar-fill" style="width:{count/max_count*100:.0f}%">{count}</div>'
            f'</div>'
            f'<div class="platform-count">{count}</div>'
            f'</div>'
            for platform, count in counts.items()
        )

    def _render_recommendations(self, recs: List[str]) -> str:
        if not recs:
            return '<li>暫無建議</li>'
        return '\n'.join(f'<li>{r}</li>' for r in recs)

    def _render_market_trends(self, trends: List[str]) -> str:
        if not trends:
            return ''
        items = '\n'.join(f'<li>{t}</li>' for t in trends)
        return f"""
  <div class="section">
    <h2><span class="icon">📈</span>市場趨勢</h2>
    <ul style="padding-left: 20px; color: #555; font-size: 14px;">
      {items}
    </ul>
  </div>"""

    def _html_footer(self) -> str:
        return ''

    def save_report(self, html: str, date_str: Optional[str] = None) -> str:
        """Save HTML report to file"""
        if not date_str:
            date_str = datetime.now().strftime('%Y%m%d')
        base_dir = os.path.dirname(os.path.dirname(__file__))
        reports_dir = os.path.join(base_dir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, f'it_daily_report_{date_str}.html')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath


def main():
    """Test the HTML generator"""
    from analysis.ai_analyzer import MiniMaxAnalyzer

    mock_products = [
        {"brand": "ASUS", "model": "ROG Thor 850P", "price": 189.99, "rating": 4.7, "reviews": 890, "platform": "Amazon", "currency": "USD"},
        {"brand": "MSI", "model": "MEG Ai1300P", "price": 319.99, "rating": 4.9, "reviews": 680, "platform": "Newegg", "currency": "USD"},
        {"brand": "MSI", "model": "MAG A750BN", "price": 89.99, "rating": 4.5, "reviews": 1100, "platform": "JD", "currency": "CNY"},
        {"brand": "Corsair", "model": "RM850x", "price": 139.99, "rating": 4.8, "reviews": 2100, "platform": "Amazon", "currency": "USD"},
        {"brand": "Gigabyte", "model": "AORUS 850W", "price": 159.99, "rating": 4.7, "reviews": 620, "platform": "Tmall", "currency": "CNY"},
        {"brand": "Seasonic", "model": "Focus GX-750", "price": 129.99, "rating": 4.7, "reviews": 890, "platform": "Amazon", "currency": "USD"},
    ]

    analyzer = MiniMaxAnalyzer()
    analysis = analyzer.get_analysis_dict(mock_products)

    generator = HTMLReportGenerator()
    html = generator.generate(mock_products, analysis)
    filepath = generator.save_report(html)

    print(f"Report saved to: {filepath}")


if __name__ == '__main__':
    main()
