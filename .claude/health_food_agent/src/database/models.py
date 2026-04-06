"""
SQLAlchemy 数据库模型 - 健康食品扩客系统
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ProductCategory(enum.Enum):
    SELENIUM_RICE = "富硒米"
    FUNCTIONAL_RICE = "功能米"
    FUNCTIONAL_NOODLES = "功能面"
    LOW_SUGAR_FOOD = "降糖食品"
    HEALTHY_STAPLE = "健康主食"
    NUTRITIONAL_MEAL = "营养代餐"


class SupplierStatus(enum.Enum):
    PENDING = "待审核"
    APPROVED = "已认证"
    REJECTED = "不合格"
    MONITORING = "观察中"


class ChannelType(enum.Enum):
    ONLINE_SHOPEE = "虾皮"
    ONLINE_RAKUTEN = "乐天"
    ONLINE_PCHOME = "PChome"
    ONLINE_FB = "Facebook"
    ONLINE_IG = "Instagram"
    OFFLINE_SUPERMARKET = "超市"
    OFFLINE_HEALTH_STORE = "健康食品店"
    OFFLINE_CONVENIENCE = "便利店"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    category = Column(SQLEnum(ProductCategory), nullable=False)
    source_platform = Column(String(50))  # 淘宝/1688/京东
    source_url = Column(String(500))
    source_price_cny = Column(Float)  # 源头采购价(人民币)
    target_price_twd = Column(Float)  # 台湾售价(台币)
    estimated_shipping = Column(Float, default=0)  # 预估运费
    estimated_tariff = Column(Float, default=0)  # 预估关税
    weight_kg = Column(Float)  # 重量(公斤)
    min_order_qty = Column(Integer, default=1)  # 最小起订量
    shelf_life = Column(String(50))  # 保质期
    storage_requirements = Column(String(100))  # 存储要求
    nutrition_info = Column(Text)  # 营养成分(JSON)
    packaging_notes = Column(Text)  # 包装说明
    compliance_notes = Column(Text)  # 合规说明
    status = Column(String(20), default="pending")  # pending/approved/rejected
    ai_recommendation_score = Column(Float)  # AI推荐分数 0-100
    ai_recommendation_reason = Column(Text)  # AI推荐理由
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    supplier = relationship("Supplier", back_populates="products")
    sales_records = relationship("SalesRecord", back_populates="product")
    pricing_history = relationship("PricingHistory", back_populates="product")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # 1688/淘宝/京东
    store_url = Column(String(500))
    contact_person = Column(String(100))
    contact_phone = Column(String(50))
    rating = Column(Float)  # 店铺评分 0-5
    total_orders = Column(Integer, default=0)  # 总订单数
    response_rate = Column(Float)  # 回复率 %
    last_delivery_days = Column(Integer)  # 最近发货天数
    certification = Column(String(200))  # 资质认证
    main_products = Column(Text)  # 主营产品
    location = Column(String(100))  # 所在地
    status = Column(SQLEnum(SupplierStatus), default=SupplierStatus.PENDING)
    overall_score = Column(Float)  # 综合评分 0-100
    strengths = Column(Text)  # 优势分析
    weaknesses = Column(Text)  # 劣势分析
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = relationship("Product", back_populates="supplier")
    quotes = relationship("SupplierQuote", back_populates="supplier")


class SupplierQuote(Base):
    __tablename__ = "supplier_quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    product_name = Column(String(200), nullable=False)
    unit_price_cny = Column(Float)
    moq = Column(Integer, default=1)
    quoted_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    notes = Column(Text)

    supplier = relationship("Supplier", back_populates="quotes")


class PricingHistory(Base):
    __tablename__ = "pricing_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    product_cost_cny = Column(Float)
    shipping_cny = Column(Float)
    tariff_twd = Column(Float)
    platform_fee_twd = Column(Float)
    final_price_twd = Column(Float)
    profit_margin = Column(Float)
    competitor_avg_price = Column(Float)
    price_competitive_score = Column(Float)
    decided_at = Column(DateTime, default=datetime.utcnow)
    decided_by = Column(String(50), default="ai")  # ai/manager

    product = relationship("Product", back_populates="pricing_history")


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    channel_type = Column(SQLEnum(ChannelType), nullable=False)
    platform = Column(String(50))
    account_id = Column(String(100))
    status = Column(String(20), default="planned")  # planned/active/suspended
    monthly_fee = Column(Float, default=0)
    commission_rate = Column(Float)  # 佣金率 %
    target_monthly_sales = Column(Integer)
    actual_monthly_sales = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class SalesRecord(Base):
    __tablename__ = "sales_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    order_date = Column(DateTime, default=datetime.utcnow)
    quantity = Column(Integer, default=0)
    unit_price_twd = Column(Float)
    total_revenue_twd = Column(Float)
    platform_fee_twd = Column(Float)
    net_revenue_twd = Column(Float)
    customer_region = Column(String(50))  # 台湾地区
    fulfillment_status = Column(String(20))  # pending/shipped/delivered

    product = relationship("Product", back_populates="sales_records")
    channel = relationship("Channel")


class MarketAnalysis(Base):
    __tablename__ = "market_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    target_category = Column(String(50))
    market_size_twd = Column(Float)  # 市场规模
    growth_rate = Column(Float)  # 增长率 %
    top_players = Column(Text)  # 主要玩家(JSON)
    avg_price_range = Column(String(50))  # 价格区间
    consumer_trends = Column(Text)  # 消费趋势
    opportunity_score = Column(Float)  # 机会评分 0-100
    risk_factors = Column(Text)  # 风险因素
    ai_insights = Column(Text)  # AI分析洞察
    report_file = Column(String(200))  # 报告文件路径


class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(100), nullable=False)
    task_type = Column(String(50))  # crawling/analysis/reporting/email
    status = Column(String(20), default="running")  # running/success/failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    records_collected = Column(Integer, default=0)
    error_message = Column(Text)
    output_file = Column(String(200))
