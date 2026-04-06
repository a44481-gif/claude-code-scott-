"""
MSI官方渠道爬蟲 - 專用於收集MSI官方渠道的數據
"""

import logging
import time
import json
from typing import List, Dict, Any
from datetime import datetime
import re
from .base_crawler import BaseCrawler, ProductData

logger = logging.getLogger(__name__)


class MSICrawler(BaseCrawler):
    """MSI官方渠道爬蟲"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # MSI官方網站的特定配置
        self.base_url = "https://www.msi.com"
        self.product_category = "Power-Supply"
        self.regions = self.config.get('regions', ['global', 'us', 'cn', 'eu'])
        
        # 已知的MSI電源產品關鍵字
        self.msi_psu_keywords = [
            'MEG', 'MPG', 'MAG', 
            'Ai1300P', 'Ai1000P', 'Ai850P',
            'A1000G', 'A850G', 'A750G', 'A650G',
            'A750GF', 'A650GF', 'A550GF',
            'MAG A650BN', 'MAG A550BN'
        ]
    
    def crawl(self) -> List[ProductData]:
        """爬取MSI官方網站的電源產品數據"""
        logger.info("開始爬取MSI官方網站數據...")
        self.products = []
        
        try:
            # 1. 獲取產品列表頁面
            product_list = self._get_product_list()
            
            # 2. 遍歷產品詳情頁
            for product_url in product_list[:20]:  # 限制爬取數量
                try:
                    product_data = self._parse_product_page(product_url)
                    if product_data:
                        self.products.append(product_data)
                        logger.info(f"成功收集產品: {product_data.model_name}")
                    
                    # 隨機延遲，避免過快請求
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"解析產品頁面時發生錯誤: {e}")
                    continue
            
            # 3. 檢查是否有其他地區的網站
            region_products = self._crawl_regional_sites()
            self.products.extend(region_products)
            
        except Exception as e:
            logger.error(f"爬取MSI數據時發生錯誤: {e}")
        
        logger.info(f"MSI爬蟲完成，共收集 {len(self.products)} 個產品")
        return self.products
    
    def _get_product_list(self) -> List[str]:
        """獲取MSI電源產品列表"""
        product_urls = []
        
        # 構建MSI電源產品頁面URL
        ps_category_urls = [
            f"{self.base_url}/Power-Supply",
            f"{self.base_url}/Power-Supplies",
            f"{self.base_url}/Power-Supply-units",
            f"{self.base_url}/Components/Power-Supply"
        ]
        
        for category_url in ps_category_urls:
            try:
                html = self.fetch_page(category_url)
                if not html:
                    continue
                    
                soup = self.parse_html(html)
                if not soup:
                    continue
                
                # 查找產品鏈接
                product_links = soup.find_all('a', href=True)
                
                for link in product_links:
                    href = link['href']
                    text = self.extract_text(link).lower()
                    
                    # 檢查是否為電源相關鏈接
                    if any(keyword in text for keyword in ['power', 'psu', 'supply']):
                        # 確保是完整URL
                        if href.startswith('/'):
                            full_url = f"{self.base_url}{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            full_url = f"{self.base_url}/{href}"
                        
                        # 添加到產品列表
                        product_urls.append(full_url)
                        
                # 如果找到產品，跳出循環
                if product_urls:
                    break
                    
            except Exception as e:
                logger.error(f"獲取產品列表時發生錯誤: {e}")
                continue
        
        # 去重
        return list(set(product_urls))
    
    def _parse_product_page(self, url: str) -> Optional[ProductData]:
        """解析單個產品頁面"""
        try:
            html = self.fetch_page(url)
            if not html:
                return None
                
            soup = self.parse_html(html)
            if not soup:
                return None
            
            # 1. 提取產品型號
            model_name = self._extract_model_name(soup)
            if not model_name:
                logger.warning(f"無法提取產品型號: {url}")
                return None
            
            # 2. 提取產品編號
            model_number = self._extract_model_number(soup, model_name)
            
            # 3. 提取功率
            power_watts = self._extract_power(soup, model_name)
            if not power_watts:
                logger.warning(f"無法提取功率: {model_name}")
            
            # 4. 提取效率等級
            efficiency_rating = self._extract_efficiency(soup)
            
            # 5. 提取價格信息
            price_data = self._extract_price(soup)
            
            # 6. 提取產品特性
            features = self._extract_features(soup)
            
            # 7. 提取規格參數
            specifications = self._extract_specifications(soup)
            
            # 8. 獲取評價信息
            rating, review_count = self._extract_reviews(soup)
            
            # 構建產品數據對象
            product_data = ProductData(
                model_name=model_name,
                model_number=model_number,
                power_watts=power_watts,
                efficiency_rating=efficiency_rating,
                price_usd=price_data.get('price_usd', 0.0),
                price_original=price_data.get('price_original', 0.0),
                currency=price_data.get('currency', 'USD'),
                availability=price_data.get('availability', 'Unknown'),
                rating=rating,
                review_count=review_count,
                source='msi_official',
                region='global',
                url=url,
                collection_timestamp=datetime.now().isoformat(),
                features=features,
                specifications=specifications
            )
            
            return product_data
            
        except Exception as e:
            logger.error(f"解析產品頁面時發生錯誤: {e}")
            return None
    
    def _extract_model_name(self, soup) -> Optional[str]:
        """提取產品型號名稱"""
        # 嘗試從多個位置提取
        selectors = [
            'h1.product-name',
            'h1.product-title',
            'div.product-info h1',
            'title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = self.extract_text(element)
                    if text and any(keyword in text for keyword in self.msi_psu_keywords):
                        # 清理文本
                        cleaned = re.sub(r'[\r\n\t]+', ' ', text)
                        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                        return cleaned
            except Exception:
                continue
        
        return None
    
    def _extract_model_number(self, soup, model_name: str) -> str:
        """提取產品編號"""
        # 從模型名稱中提取可能的編號
        model_number_patterns = [
            r'[A-Z]{2,}\s?\d+[A-Z]*',
            r'\b[A-Z]+\-\d+[A-Z]*\b',
            r'\b\d+[A-Z]+\b'
        ]
        
        for pattern in model_number_patterns:
            matches = re.findall(pattern, model_name)
            if matches:
                return matches[0]
        
        # 嘗試從頁面中尋找
        selectors = [
            'div.model-number',
            'span.sku',
            'meta[itemprop="sku"]',
            'div.product-sku'
        ]
        
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = self.extract_text(element)
                    if text:
                        return text.strip()
            except Exception:
                continue
        
        return ""
    
    def _extract_power(self, soup, model_name: str) -> Optional[int]:
        """提取功率信息"""
        # 從模型名稱中提取
        watt_patterns = [
            r'(\d+)\s*[Ww][Aa][Tt][Tt]',
            r'(\d+)\s*[Ww]',
            r'\b(\d{3,4})\b'
        ]
        
        for pattern in watt_patterns:
            matches = re.findall(pattern, model_name)
            if matches:
                try:
                    return int(matches[0])
                except ValueError:
                    continue
        
        # 從頁面內容中提取
        page_text = soup.get_text()
        power_keywords = ['功率', '额定功率', '最大功率', 'watt', 'w']
        
        for keyword in power_keywords:
            pattern = f'{keyword}\\s*[:：]?\\s*(\\d{{3,4}})'
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                try:
                    return int(matches[0])
                except ValueError:
                    continue
        
        return None
    
    def _extract_efficiency(self, soup) -> str:
        """提取效率等級"""
        efficiency_patterns = [
            r'80\s*[Pp][Ll][Uu][Ss]\s*([A-Za-z]+)',
            r'效率等级[：:]\s*([^\s,]+)',
            r'efficiency[：:]\s*([^\s,]+)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in efficiency_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                efficiency = matches[0].strip()
                return f"80 PLUS {efficiency}"
        
        return "未知"
    
    def _extract_price(self, soup) -> Dict[str, Any]:
        """提取價格信息"""
        price_data = {
            'price_usd': 0.0,
            'price_original': 0.0,
            'currency': 'USD',
            'availability': 'Unknown'
        }
        
        # 價格選擇器
        price_selectors = [
            'span.price',
            'div.product-price',
            'meta[property="product:price:amount"]',
            'span[itemprop="price"]'
        ]
        
        for selector in price_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    price_text = self.extract_text(element)
                    
                    # 提取數字
                    price_match = re.search(r'[\d,.]+', price_text)
                    if price_match:
                        price_str = price_match.group()
                        price_str = price_str.replace(',', '')
                        
                        try:
                            price = float(price_str)
                            price_data['price_original'] = price
                            price_data['price_usd'] = price  # 假設為美元
                            
                            # 檢測貨幣
                            if '¥' in price_text or '￥' in price_text or 'CNY' in price_text:
                                price_data['currency'] = 'CNY'
                            elif '€' in price_text or 'EUR' in price_text:
                                price_data['currency'] = 'EUR'
                            elif '£' in price_text or 'GBP' in price_text:
                                price_data['currency'] = 'GBP'
                            elif '$' in price_text:
                                price_data['currency'] = 'USD'
                            
                            break
                        except ValueError:
                            continue
            except Exception:
                continue
        
        # 檢查庫存狀態
        availability_selectors = [
            'span.stock-status',
            'div.availability',
            'button.add-to-cart'
        ]
        
        for selector in availability_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    text = self.extract_text(element).lower()
                    if '缺貨' in text or 'out of stock' in text:
                        price_data['availability'] = 'Out of Stock'
                    elif '有貨' in text or 'in stock' in text:
                        price_data['availability'] = 'In Stock'
                    break
            except Exception:
                continue
        
        return price_data
    
    def _extract_features(self, soup) -> List[str]:
        """提取產品特性"""
        features = []
        
        # 常見的特性關鍵詞
        feature_keywords = [
            '模組化', '全模組', '半模組', '扁平線材',
            'RGB燈光', '靜音風扇', '零轉速模式',
            '10年保固', 'OCP', 'OVP', 'SCP', 'OPP',
            '高效率', '低噪音', '智能控制'
        ]
        
        # 查找特性列表
        feature_selectors = [
            'ul.product-features li',
            'div.features ul li',
            'span.feature-item'
        ]
        
        for selector in feature_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    text = self.extract_text(element)
                    if text and len(text) > 3:
                        features.append(text)
            except Exception:
                continue
        
        # 如果沒有找到，嘗試從描述中提取
        if not features:
            description_selectors = [
                'div.product-description',
                'meta[name="description"]',
                'div.product-details'
            ]
            
            for selector in description_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        text = self.extract_text(element)
                        for keyword in feature_keywords:
                            if keyword in text:
                                features.append(keyword)
                except Exception:
                    continue
        
        return list(set(features))
    
    def _extract_specifications(self, soup) -> Dict[str, str]:
        """提取規格參數"""
        specifications = {}
        
        # 查找規格表格
        spec_selectors = [
            'table.specifications tr',
            'div.specs table tr',
            'ul.spec-list li'
        ]
        
        for selector in spec_selectors:
            try:
                rows = soup.select(selector)
                for row in rows:
                    # 嘗試提取key-value對
                    cells = row.find_all(['td', 'th', 'span'])
                    if len(cells) >= 2:
                        key = self.extract_text(cells[0]).strip(':').strip()
                        value = self.extract_text(cells[1]).strip()
                        if key and value:
                            specifications[key] = value
            except Exception:
                continue
        
        return specifications
    
    def _extract_reviews(self, soup) -> (Optional[float], Optional[int]):
        """提取評價信息"""
        rating = None
        review_count = None
        
        # 查找評分
        rating_selectors = [
            'span.rating-score',
            'div.rating',
            'meta[itemprop="ratingValue"]'
        ]
        
        for selector in rating_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    rating_text = self.extract_text(element)
                    rating_match = re.search(r'[\d.]+', rating_text)
                    if rating_match:
                        try:
                            rating = float(rating_match.group())
                            break
                        except ValueError:
                            continue
            except Exception:
                continue
        
        # 查找評價數量
        review_selectors = [
            'span.review-count',
            'div.reviews',
            'meta[itemprop="reviewCount"]'
        ]
        
        for selector in review_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    review_text = self.extract_text(element)
                    review_match = re.search(r'\d+', review_text)
                    if review_match:
                        try:
                            review_count = int(review_match.group())
                            break
                        except ValueError:
                            continue
            except Exception:
                continue
        
        return rating, review_count
    
    def _crawl_regional_sites(self) -> List[ProductData]:
        """爬取地區性MSI網站"""
        regional_products = []
        
        # 地區網站URL
        regional_sites = {
            'us': 'https://us.msi.com/Power-Supply',
            'cn': 'https://cn.msi.com/Power-Supply',
            'eu': 'https://eu.msi.com/Power-Supply',
            'tw': 'https://tw.msi.com/Power-Supply',
            'jp': 'https://jp.msi.com/Power-Supply'
        }
        
        for region, url in regional_sites.items():
            if region not in self.regions:
                continue
                
            try:
                logger.info(f"爬取{region}地區網站: {url}")
                
                html = self.fetch_page(url)
                if not html:
                    continue
                    
                soup = self.parse_html(html)
                if not soup:
                    continue
                
                # 獲取產品鏈接
                product_selectors = [
                    'a.product-link',
                    'div.product-item a',
                    'h3.product-title a'
                ]
                
                for selector in product_selectors:
                    elements = soup.select(selector)
                    for element in elements:
                        if element.has_attr('href'):
                            product_url = element['href']
                            if product_url.startswith('/'):
                                product_url = f"{self.base_url}{product_url}"
                            
                            # 解析產品頁面
                            product_data = self._parse_product_page(product_url)
                            if product_data:
                                # 更新地區信息
                                product_data.region = region
                                regional_products.append(product_data)
                
                # 隨機延遲
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                logger.error(f"爬取{region}地區網站時發生錯誤: {e}")
                continue
        
        return regional_products