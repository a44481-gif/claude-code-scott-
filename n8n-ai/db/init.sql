-- PC電源營銷系統數據庫初始化腳本
-- Created: 2026-04-06

-- ==================== 客戶管理 ====================
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    market VARCHAR(100),
    website VARCHAR(255),
    employee_count INTEGER,
    annual_revenue DECIMAL(15,2),
    credit_rating VARCHAR(50),
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(100),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'prospect',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 競品情報 ====================
CREATE TABLE IF NOT EXISTS competitor_intel (
    id SERIAL PRIMARY KEY,
    competitor VARCHAR(100) NOT NULL,
    product_model VARCHAR(255),
    wattage VARCHAR(50),
    certification VARCHAR(50),
    price DECIMAL(10,2),
    source VARCHAR(50),
    data JSONB,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_competitor ON competitor_intel(competitor);
CREATE INDEX idx_collected_at ON competitor_intel(collected_at DESC);

-- ==================== 銷售訂單 ====================
CREATE TABLE IF NOT EXISTS sales_orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    product VARCHAR(255),
    wattage VARCHAR(50),
    certification VARCHAR(50),
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    total_price DECIMAL(15,2),
    margin DECIMAL(5,2),
    status VARCHAR(50),
    order_date DATE,
    delivery_date DATE,
    payment_terms VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer ON sales_orders(customer_id);
CREATE INDEX idx_order_date ON sales_orders(order_date DESC);
CREATE INDEX idx_status ON sales_orders(status);

-- ==================== 潛在客戶 ====================
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255),
    market VARCHAR(100),
    requirement TEXT,
    company_size VARCHAR(50),
    website VARCHAR(255),
    email VARCHAR(255),
    priority VARCHAR(20),
    score INTEGER,
    strategy TEXT,
    status VARCHAR(50) DEFAULT 'new',
    assigned_to VARCHAR(100),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_priority ON leads(priority);
CREATE INDEX idx_status ON leads(status);

-- ==================== 客戶培育序列 ====================
CREATE TABLE IF NOT EXISTS lead_nurture (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    company VARCHAR(255),
    market VARCHAR(100),
    requirement TEXT,
    priority VARCHAR(20),
    score INTEGER,
    strategy TEXT,
    stage INTEGER DEFAULT 1,
    next_action DATE,
    email_sent_count INTEGER DEFAULT 0,
    last_email_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 報價單 ====================
CREATE TABLE IF NOT EXISTS quotations (
    id SERIAL PRIMARY KEY,
    quote_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    lead_id INTEGER REFERENCES leads(id),
    products JSONB,
    subtotal DECIMAL(15,2),
    discount DECIMAL(10,2),
    total DECIMAL(15,2),
    margin DECIMAL(5,2),
    incoterms VARCHAR(50),
    payment_terms VARCHAR(100),
    delivery_weeks INTEGER,
    validity_days INTEGER,
    status VARCHAR(50) DEFAULT 'draft',
    sent_at TIMESTAMP,
    approved_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quote_status ON quotations(status);
CREATE INDEX idx_sent_at ON quotations(sent_at DESC);

-- ==================== 每週報告 ====================
CREATE TABLE IF NOT EXISTS weekly_reports (
    id SERIAL PRIMARY KEY,
    week VARCHAR(20) NOT NULL,
    report JSONB,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_week ON weekly_reports(week);

-- ==================== 產品目錄 ====================
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    model VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255),
    wattage VARCHAR(50),
    certification VARCHAR(50),
    modular VARCHAR(50),
    fan_size VARCHAR(50),
    length VARCHAR(50),
    warranty_years INTEGER,
    bom_cost DECIMAL(10,2),
    suggested_price DECIMAL(10,2),
    min_price DECIMAL(10,2),
    moq INTEGER,
    in_production BOOLEAN DEFAULT true,
    specs JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 競品產品數據 ====================
CREATE TABLE IF NOT EXISTS competitor_products (
    id SERIAL PRIMARY KEY,
    competitor VARCHAR(100) NOT NULL,
    model VARCHAR(255),
    wattage VARCHAR(50),
    certification VARCHAR(50),
    price DECIMAL(10,2),
    specs JSONB,
    strengths TEXT,
    weaknesses TEXT,
    source_url VARCHAR(500),
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_competitor_product ON competitor_products(competitor);
CREATE INDEX idx_wattage ON competitor_products(wattage);

-- ==================== 任務跟踪 ====================
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50),
    priority VARCHAR(20),
    status VARCHAR(50) DEFAULT 'pending',
    assigned_to VARCHAR(100),
    due_date DATE,
    completed_at TIMESTAMP,
    related_id INTEGER,
    related_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 插入示例數據 ====================
INSERT INTO products (model, name, wattage, certification, modular, warranty_years, bom_cost, suggested_price, min_price, moq) VALUES
('PSU-550BR', '550W Bronze', '550W', '80+ Bronze', 'Non-modular', 3, 28.00, 55.00, 45.00, 500),
('PSU-650BR', '650W Bronze', '650W', '80+ Bronze', 'Non-modular', 3, 32.00, 62.00, 52.00, 500),
('PSU-750GD', '750W Gold', '750W', '80+ Gold', 'Semi-modular', 5, 42.00, 85.00, 72.00, 300),
('PSU-850GD', '850W Gold', '850W', '80+ Gold', 'Full-modular', 5, 48.00, 98.00, 82.00, 300),
('PSU-1000PL', '1000W Platinum', '1000W', '80+ Platinum', 'Full-modular', 7, 62.00, 135.00, 115.00, 200),
('PSU-1200PL', '1200W Platinum', '1200W', '80+ Platinum', 'Full-modular', 7, 72.00, 158.00, 135.00, 200),
('PSU-1600TI', '1600W Titanium', '1600W', '80+ Titanium', 'Full-modular', 10, 105.00, 245.00, 210.00, 100),
('PSU-2000TI', '2000W Titanium', '2000W', '80+ Titanium', 'Full-modular', 10, 135.00, 320.00, 280.00, 50);

-- ==================== 示例競品數據 ====================
INSERT INTO competitor_products (competitor, model, wattage, certification, price, specs, strengths, weaknesses) VALUES
('Seasonic', 'SSR-1000TR', '1000W', '80+ Titanium', 289.99, '{"efficiency": 94, "warranty": 12, "fan": "135mm"}', '最高質量, 12年質保', '價格最高, 交期長'),
('Corsair', 'RM1000x', '1000W', '80+ Gold', 189.99, '{"efficiency": 90, "warranty": 10, "fan": "135mm"}', '品牌強, 渠道廣', '性價比一般'),
('Super Flower', 'SF-1000F14HT', '1000W', '80+ Titanium', 219.99, '{"efficiency": 93, "warranty": 10, "fan": "140mm"}', '性價比高, 交期快', '品牌知名度低'),
('be quiet!', 'Dark Power 13', '1000W', '80+ Platinum', 249.99, '{"efficiency": 92, "warranty": 10, "fan": "135mm"}', '靜音最好, 德國品質', '價格偏高');
