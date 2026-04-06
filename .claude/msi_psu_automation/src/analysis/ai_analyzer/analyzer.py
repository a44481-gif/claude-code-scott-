"""
AI分析器 - 對收集的MSI電源銷售數據進行深度分析
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum

# 機器學習庫
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

# 自然語言處理
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """分析類型枚舉"""
    SALES_TREND = "sales_trend"
    PRICE_ANALYSIS = "price_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    CUSTOMER_SENTIMENT = "customer_sentiment"
    MARKET_INSIGHT = "market_insight"
    PRODUCT_PERFORMANCE = "product_performance"


@dataclass
class AnalysisResult:
    """分析結果數據結構"""
    analysis_type: AnalysisType
    insights: List[str]
    metrics: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float
    data_points: int
    time_range: str
    generated_at: str


class AIAnalyzer:
    """AI分析器主類"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data = None
        self.results = []
        
        # 初始化NLTK
        try:
            nltk.download('vader_lexicon', quiet=True)
            self.sia = SentimentIntensityAnalyzer()
        except Exception as e:
            logger.warning(f"NLTK初始化失敗: {e}")
            self.sia = None
        
        # AI模型配置
        self.models = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        self.scaler = StandardScaler()
    
    def analyze(self, data: List[Dict[str, Any]]) -> List[AnalysisResult]:
        """執行所有分析"""
        logger.info("開始AI數據分析...")
        self.data = pd.DataFrame(data)
        
        if self.data.empty:
            logger.warning("沒有數據可用於分析")
            return []
        
        # 1. 銷售趨勢分析
        sales_result = self._analyze_sales_trends()
        if sales_result:
            self.results.append(sales_result)
        
        # 2. 價格分析
        price_result = self._analyze_pricing()
        if price_result:
            self.results.append(price_result)
        
        # 3. 競爭分析
        competitive_result = self._analyze_competition()
        if competitive_result:
            self.results.append(competitive_result)
        
        # 4. 客戶情感分析
        sentiment_result = self._analyze_customer_sentiment()
        if sentiment_result:
            self.results.append(sentiment_result)
        
        # 5. 市場洞察
        market_result = self._analyze_market_insights()
        if market_result:
            self.results.append(market_result)
        
        # 6. 產品性能分析
        product_result = self._analyze_product_performance()
        if product_result:
            self.results.append(product_result)
        
        logger.info(f"AI分析完成，生成 {len(self.results)} 個分析結果")
        return self.results
    
    def _analyze_sales_trends(self) -> Optional[AnalysisResult]:
        """分析銷售趨勢"""
        try:
            if 'collection_timestamp' not in self.data.columns:
                return None
            
            # 準備時間序列數據
            self.data['timestamp'] = pd.to_datetime(self.data['collection_timestamp'])
            self.data['date'] = self.data['timestamp'].dt.date
            
            # 按日期分組銷售數據
            if 'price_usd' in self.data.columns:
                daily_revenue = self.data.groupby('date')['price_usd'].sum()
                daily_sales = self.data.groupby('date').size()
            else:
                daily_sales = self.data.groupby('date').size()
                daily_revenue = daily_sales * 100  # 假設平均價格
            
            insights = []
            metrics = {}
            
            # 計算趨勢
            if len(daily_sales) > 1:
                # 銷售增長率
                sales_growth = self._calculate_growth_rate(daily_sales)
                metrics['sales_growth_rate'] = sales_growth
                
                if sales_growth > 0.1:
                    insights.append("銷售呈現強勁增長趨勢")
                elif sales_growth < -0.1:
                    insights.append("銷售呈現下降趨勢")
                else:
                    insights.append("銷售保持穩定")
                
                # 收入趨勢
                if len(daily_revenue) > 1:
                    revenue_growth = self._calculate_growth_rate(daily_revenue)
                    metrics['revenue_growth_rate'] = revenue_growth
                    
                    if revenue_growth > sales_growth:
                        insights.append("平均銷售價格上升，推動收入增長")
                    elif revenue_growth < sales_growth:
                        insights.append("平均銷售價格下降，影響收入增長")
                
                # 預測未來趨勢
                forecast = self._forecast_sales(daily_sales)
                if forecast:
                    metrics['next_week_forecast'] = forecast.get('next_week', {})
                    metrics['trend_direction'] = forecast.get('trend', 'stable')
                    
                    if forecast.get('trend') == 'up':
                        insights.append("預計下周銷售將繼續增長")
                    elif forecast.get('trend') == 'down':
                        insights.append("預計下周銷售可能下降")
            
            recommendations = self._generate_sales_recommendations(insights, metrics)
            
            return AnalysisResult(
                analysis_type=AnalysisType.SALES_TREND,
                insights=insights,
                metrics=metrics,
                recommendations=recommendations,
                confidence_score=0.85,
                data_points=len(self.data),
                time_range=f"{self.data['date'].min()} 至 {self.data['date'].max()}",
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"銷售趨勢分析失敗: {e}")
            return None
    
    def _analyze_pricing(self) -> Optional[AnalysisResult]:
        """分析價格策略"""
        try:
            if 'price_usd' not in self.data.columns:
                return None
            
            insights = []
            metrics = {}
            
            # 價格分布分析
            price_stats = self.data['price_usd'].describe()
            metrics['price_statistics'] = {
                'mean': float(price_stats['mean']),
                'median': float(self.data['price_usd'].median()),
                'min': float(price_stats['min']),
                'max': float(price_stats['max']),
                'std': float(price_stats['std'])
            }
            
            # 價格段分析
            price_bins = [0, 100, 200, 300, 500, 1000, float('inf')]
            price_labels = ['<100', '100-200', '200-300', '300-500', '500-1000', '>1000']
            
            self.data['price_range'] = pd.cut(self.data['price_usd'], bins=price_bins, labels=price_labels)
            price_distribution = self.data['price_range'].value_counts().to_dict()
            metrics['price_distribution'] = price_distribution
            
            # 識別暢銷價格段
            max_price_range = max(price_distribution, key=price_distribution.get)
            insights.append(f"最暢銷的價格段是: {max_price_range}美元")
            
            # 價格與功率關係
            if 'power_watts' in self.data.columns:
                # 計算每瓦價格
                self.data['price_per_watt'] = self.data['price_usd'] / self.data['power_watts']
                avg_price_per_watt = self.data['price_per_watt'].mean()
                metrics['avg_price_per_watt'] = float(avg_price_per_watt)
                
                if avg_price_per_watt < 1.0:
                    insights.append("產品具有競爭力的價格性能比")
                else:
                    insights.append("產品定位高端，價格性能比較高")
            
            # 價格趨勢分析
            if 'collection_timestamp' in self.data.columns:
                self.data['timestamp'] = pd.to_datetime(self.data['collection_timestamp'])
                price_trend = self.data.groupby(self.data['timestamp'].dt.date)['price_usd'].mean()
                
                if len(price_trend) > 1:
                    price_change = (price_trend.iloc[-1] - price_trend.iloc[0]) / price_trend.iloc[0]
                    metrics['price_change_rate'] = float(price_change)
                    
                    if price_change > 0.05:
                        insights.append("近期價格有上升趨勢")
                    elif price_change < -0.05:
                        insights.append("近期價格有下降趨勢")
            
            # 生成推薦
            recommendations = [
                "考慮調整價格段分布，優化產品組合",
                "監控競爭對手的價格策略",
                "分析不同地區的價格敏感性"
            ]
            
            # 根據分析結果調整推薦
            if 'avg_price_per_watt' in metrics and metrics['avg_price_per_watt'] > 1.2:
                recommendations.append("考慮推出更具價格競爭力的產品")
            
            return AnalysisResult(
                analysis_type=AnalysisType.PRICE_ANALYSIS,
                insights=insights,
                metrics=metrics,
                recommendations=recommendations,
                confidence_score=0.80,
                data_points=len(self.data),
                time_range="當前數據周期",
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"價格分析失敗: {e}")
            return None
    
    def _analyze_competition(self) -> Optional[AnalysisResult]:
        """分析競爭環境"""
        try:
            insights = []
            metrics = {}
            
            # 市場份額分析
            if 'source' in self.data.columns:
                source_distribution = self.data['source'].value_counts()
                metrics['source_distribution'] = source_distribution.to_dict()
                
                # 識別主要銷售渠道
                top_sources = source_distribution.head(3)
                insights.append(f"主要銷售渠道: {', '.join(top_sources.index.tolist())}")
            
            # 地區競爭分析
            if 'region' in self.data.columns:
                region_distribution = self.data['region'].value_counts()
                metrics['region_distribution'] = region_distribution.to_dict()
                
                top_regions = region_distribution.head(3)
                insights.append(f"主要銷售地區: {', '.join(top_regions.index.tolist())}")
            
            # 產品組合分析
            if 'model_name' in self.data.columns:
                product_popularity = self.data['model_name'].value_counts()
                metrics['top_products'] = product_popularity.head(10).to_dict()
                
                top_product = product_popularity.index[0]
                insights.append(f"最暢銷產品: {top_product}")
            
            # 競爭強度評估
            if 'rating' in self.data.columns and 'review_count' in self.data.columns:
                avg_rating = self.data['rating'].mean()
                total_reviews = self.data['review_count'].sum()
                
                metrics['avg_rating'] = float(avg_rating)
                metrics['total_reviews'] = int(total_reviews)
                
                if avg_rating > 4.0:
                    insights.append("產品評價優秀，具有競爭優勢")
                elif avg_rating < 3.0:
                    insights.append("產品評價有待提升，競爭力不足")
            
            recommendations = [
                "加強在主要銷售渠道的市場推廣",
                "針對熱門地區制定本地化策略",
                "優化暢銷產品的供應鏈管理"
            ]
            
            return AnalysisResult(
                analysis_type=AnalysisType.COMPETITIVE_ANALYSIS,
                insights=insights,
                metrics=metrics,
                recommendations=recommendations,
                confidence_score=0.75,
                data_points=len(self.data),
                time_range="當前數據周期",
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"競爭分析失敗: {e}")
            return None
    
    def _analyze_customer_sentiment(self) -> Optional[AnalysisResult]:
        """分析客戶情感"""
        try:
            insights = []
            metrics = {}
            
            # 檢查是否有評價數據
            if 'rating' not in self.data.columns:
                return None
            
            # 評分分布分析
            rating_distribution = self.data['rating'].value_counts().sort_index()
            metrics['rating_distribution'] = rating_distribution.to_dict()
            
            # 平均評分
            avg_rating = self.data['rating'].mean()
            metrics['average_rating'] = float(avg_rating)
            
            if avg_rating >= 4.5:
                insights.append("客戶滿意度極高")
            elif avg_rating >= 4.0:
                insights.append("客戶滿意度良好")
            elif avg_rating >= 3.0:
                insights.append("客戶滿意度一般")
            else:
                insights.append("客戶滿意度較低，需要改進")
            
            # 評分趨勢分析
            if 'collection_timestamp' in self.data.columns:
                self.data['timestamp'] = pd.to_datetime(self.data['collection_timestamp'])
                rating_trend = self.data.groupby(self.data['timestamp'].dt.date)['rating'].mean()
                
                if len(rating_trend) > 1:
                    rating_change = rating_trend.iloc[-1] - rating_trend.iloc[0]
                    metrics['rating_trend'] = float(rating_change)
                    
                    if rating_change > 0.1:
                        insights.append("客戶滿意度呈上升趨勢")
                    elif rating_change < -0.1:
                        insights.append("客戶滿意度呈下降趨勢")
            
            # 生成推薦
            recommendations = []
            
            if avg_rating < 4.0:
                recommendations.extend([
                    "收集客戶反饋，識別改進點",
                    "加強售後服務和技術支持",
                    "考慮推出產品改進計劃"
                ])
            else:
                recommendations.extend([
                    "利用客戶好評進行市場推廣",
                    "建立客戶忠誠度計劃",
                    "收集成功案例和推薦"
                ])
            
            return AnalysisResult(
                analysis_type=AnalysisType.CUSTOMER_SENTIMENT,
                insights=insights,
                metrics=metrics,
                recommendations=recommendations,
                confidence_score=0.70,
                data_points=len(self.data[~self.data['rating'].isna()]),
                time_range="當前數據周期",
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"客戶情感分析失敗: {e}")
            return None
    
    def _analyze_market_insights(self) -> Optional[AnalysisResult]:
        """分析市場洞察"""
        try:
            insights = []
            metrics = {}
            
            # 市場動態分析
            if 'availability' in self.data.columns:
                availability_dist = self.data['availability'].value_counts()
                metrics['availability_distribution'] = availability_dist.to_dict()
                
                in_stock_rate = availability_dist.get('In Stock', 0) / len(self.data)
                if in_stock_rate < 0.8:
                    insights.append("部分產品庫存緊張，需要優化供應鏈")
            
            # 產品特性分析
            if 'features' in self.data.columns:
                # 統計熱門特性
                all_features = []
                for features in self.data['features'].dropna():
                    if isinstance(features, list):
                        all_features.extend(features)
                
                if all_features:
                    from collections import Counter
                    feature_counter = Counter(all_features)
                    top_features = dict(feature_counter.most_common(10))
                    metrics['top_features'] = top_features
                    
                    # 識別關鍵特性
                    if len(top_features) > 0:
                        most_common_feature = list(top_features.keys())[0]
                        insights.append(f"最受關注的產品特性: {most_common_feature}")
            
            # 季節性分析
            if 'collection_timestamp' in self.data.columns:
                self.data['month'] = pd.to_datetime(self.data['collection_timestamp']).dt.month
                monthly_sales = self.data.groupby('month').size()
                
                if len(monthly_sales) > 0:
                    peak_month = monthly_sales.idxmax()
                    metrics['peak_sales_month'] = int(peak_month)
                    
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    insights.append(f"銷售高峰期在: {month_names[peak_month-1]}")
            
            recommendations = [
                "根據市場需求調整產品組合",
                "關注庫存變化，優化供應鏈",
                "利用季節性趨勢制定營銷策略"
            ]
            
            return AnalysisResult(
                analysis_type=AnalysisType.MARKET_INSIGHT,
                insights=insights,
                metrics=metrics,
                recommendations=recommendations,
                confidence_score=0.78,
                data_points=len(self.data),
                time_range="當前數據周期",
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"市場洞察分析失敗: {e}")
            return None
    
    def _analyze_product_performance(self) -> Optional[AnalysisResult]:
        """分析產品性能"""
        try:
            insights = []
            metrics = {}
            
            # 功率段分析
            if 'power_watts' in self.data.columns:
                # 功率分布
                power_bins = [0, 500, 750, 1000, 1250, 1500, float('inf')]
                power_labels = ['<500W', '500-750W', '750-1000W', '1000-1250W', '1250-1500W', '>1500W']
                
                self.data['power_range'] = pd.cut(self.data['power_watts'], bins=power_bins, labels=power_labels)
                power_distribution = self.data['power_range'].value_counts().to_dict()
                metrics['power_distribution'] = power_distribution
                
                # 識別熱門功率段
                max_power_range = max(power_distribution, key=power_distribution.get)
                insights.append(f"最受歡迎的功率段: {max_power_range}")
            
            # 效率等級分析
            if 'efficiency_rating' in self.data.columns:
                efficiency_dist = self.data['efficiency_rating'].value_counts()
                metrics['efficiency_distribution'] = efficiency_dist.to_dict()
                
                # 識別主流效率等級
                if len(efficiency_dist) > 0:
                    top_efficiency = efficiency_dist.index[0]
                    insights.append(f"主流效率等級: {top_efficiency}")
            
            # 價格性能比分析
            if 'price_usd' in self.data.columns and 'power_watts' in self.data.columns:
                self.data['price_performance'] = self.data['price_usd'] / self.data['power_watts']
                avg_price_performance = self.data['price_performance'].mean()
                metrics['avg_price_performance'] = float(avg_price_performance)
                
                # 識別性價比最佳的產品
                if 'model_name' in self.data.columns:
                    best_value = self.data.loc[self.data['price_performance'].idxmin(), 'model_name']
                    insights.append(f"性價比最高的產品: {best_value}")
            
            recommendations = [
                "根據市場需求調整功率段分布",
                "關注效率等級的市場趨勢",
                "優化產品性價比，提高競爭力"
            ]
            
            return AnalysisResult(
                analysis_type=AnalysisType.PRODUCT_PERFORMANCE,
                insights=insights,
                metrics=metrics,
                recommendations=recommendations,
                confidence_score=0.82,
                data_points=len(self.data),
                time_range="當前數據周期",
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"產品性能分析失敗: {e}")
            return None
    
    def _calculate_growth_rate(self, series: pd.Series) -> float:
        """計算增長率"""
        if len(series) < 2:
            return 0.0
        
        return (series.iloc[-1] - series.iloc[0]) / series.iloc[0]
    
    def _forecast_sales(self, sales_data: pd.Series) -> Optional[Dict[str, Any]]:
        """預測銷售趨勢"""
        try:
            if len(sales_data) < 5:
                return None
            
            # 準備數據
            X = np.arange(len(sales_data)).reshape(-1, 1)
            y = sales_data.values
            
            # 訓練模型
            model = self.models['linear_regression']
            model.fit(X, y)
            
            # 預測未來7天
            future_days = 7
            X_future = np.arange(len(sales_data), len(sales_data) + future_days).reshape(-1, 1)
            y_pred = model.predict(X_future)
            
            # 計算趨勢
            last_actual = y[-1]
            next_pred = y_pred[0]
            
            trend = 'stable'
            if next_pred > last_actual * 1.05:
                trend = 'up'
            elif next_pred < last_actual * 0.95:
                trend = 'down'
            
            return {
                'next_week': {
                    'predicted_sales': float(np.mean(y_pred)),
                    'confidence_interval': [float(np.min(y_pred)), float(np.max(y_pred))]
                },
                'trend': trend
            }
            
        except Exception as e:
            logger.error(f"銷售預測失敗: {e}")
            return None
    
    def _generate_sales_recommendations(self, insights: List[str], metrics: Dict[str, Any]) -> List[str]:
        """生成銷售推薦"""
        recommendations = []
        
        # 基於增長率推薦
        if 'sales_growth_rate' in metrics:
            growth_rate = metrics['sales_growth_rate']
            
            if growth_rate > 0.15:
                recommendations.append("考慮增加庫存和生產能力以滿足增長需求")
            elif growth_rate < -0.1:
                recommendations.append("分析銷售下降原因，調整市場策略")
        
        # 基於季節性推薦
        if 'peak_sales_month' in metrics:
            current_month = datetime.now().month
            peak_month = metrics['peak_sales_month']
            
            if abs(current_month - peak_month) <= 1:
                recommendations.append("銷售高峰期即將到來，準備營銷活動")
        
        # 通用推薦
        recommendations.extend([
            "監控市場趨勢，及時調整產品策略",
            "加強數據分析，優化決策過程",
            "建立預警機制，應對市場變化"
        ])
        
        return recommendations
    
    def generate_summary_report(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """生成總結報告"""
        try:
            if not results:
                return {}
            
            summary = {
                'executive_summary': '',
                'key_findings': [],
                'critical_metrics': {},
                'recommended_actions': [],
                'overall_confidence': 0.0,
                'report_generated_at': datetime.now().isoformat()
            }
            
            # 提取關鍵發現
            all_insights = []
            for result in results:
                all_insights.extend(result.insights)
            
            # 提取關鍵指標
            critical_metrics = {}
            for result in results:
                for key, value in result.metrics.items():
                    if isinstance(value, (int, float)):
                        critical_metrics[key] = value
            
            # 提取推薦行動
            all_recommendations = []
            for result in results:
                all_recommendations.extend(result.recommendations)
            
            # 計算總體置信度
            confidence_scores = [r.confidence_score for r in results]
            overall_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            # 生成執行摘要
            if all_insights:
                top_insights = all_insights[:3]
                executive_summary = f"分析顯示: {', '.join(top_insights)}。建議採取相應行動以優化業務表現。"
                summary['executive_summary'] = executive_summary
            
            summary['key_findings'] = all_insights[:5]
            summary['critical_metrics'] = critical_metrics
            summary['recommended_actions'] = list(set(all_recommendations))[:5]
            summary['overall_confidence'] = float(overall_confidence)
            
            return summary
            
        except Exception as e:
            logger.error(f"生成總結報告失敗: {e}")
            return {}