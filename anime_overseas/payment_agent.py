"""
动漫出海运营代理人 · 支付收款系统
anime_overseas/payment_agent.py

功能：
1. 多币种收款管理（USD → 人民币自动结汇）
2. 微信/支付宝收款通道对接
3. YouTube/TikTok 国际收益结汇
4. 客户订单收款（人民币）
5. 自动对账 + 收益报表
6. 合规结汇方案

用法:
    agent = PaymentAgent()
    agent.receive_alipay(order_id="C001", amount=299, customer="客户名")
    agent.reconcile_youtube_revenue(month="2026-04")
    agent.settle_to_wechat(amount=5000)
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime

from anime_ops_config import LOG_DIR, OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "payment.log", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger("PaymentAgent")


# ============ 支付平台配置 ============

class PaymentConfig:
    """支付配置"""

    # ---- 国际收款（美元）----
    PAYONEER = {
        "name": "Payoneer派安盈",
        "website": "payoneer.com",
        "min_payout": 100,
        "fee": "0",  # 提现到国内银行手续费1-2%
        "register_url": "https://www.payoneer.com",
        "优势": "YouTube/TikTok官方合作，最稳定",
        "到账速度": "1-3工作日",
    }

    PINGPONG = {
        "name": "PingPong乒乓",
        "website": "pingpongx.com",
        "min_payout": 50,
        "fee": "1%封顶",
        "register_url": "https://www.pingpongx.com",
        "优势": "费率低，到账快，中国本土品牌",
        "到账速度": "1-2工作日",
    }

    WISE = {
        "name": "Wise（原TransferWise）",
        "website": "wise.com",
        "min_payout": 50,
        "fee": "约0.5-1%",
        "register_url": "https://wise.com",
        "优势": "汇率最优，支持多币种",
        "到账速度": "1-2工作日",
    }

    # ---- 国内收款（人民币）----
    ALIPAY = {
        "name": "支付宝",
        "types": ["个人收款码", "商家收款码", "当面付"],
        "fee": "0",
        "best_for": "粉丝打赏、私单收款、代付",
    }

    WECHAT_PAY = {
        "name": "微信支付",
        "types": ["个人收款码", "商家码", "Native支付"],
        "fee": "0",
        "best_for": "粉丝打赏、私单收款、电商",
    }

    # ---- 第三方聚合支付（推荐用于规模化）----
    PAYJS = {
        "name": "PAYJS（蚂/AWS合付）",
        "website": "payjs.cn",
        "alipay_rate": "0.38%",
        "wechat_rate": "0.38%",
        "特点": "接入简单，费率低，适合个人",
        "register_url": "https://payjs.cn",
    }

    # 沙箱环境测试
    SANDBOX = {
        "alipay_sandbox": "https://openhome.alipay.com/develop/sandbox",
        "wechat_sandbox": "https://pay.weixin.qq.com/wiki/doc/apiv3_partner/wechatpay.php",
    }


# ============ 收益记录 ============

class PaymentRecord:
    def __init__(
        self,
        order_id: str,
        channel: str,  # youtube/payoneer/pingpong/alipay/wechat/manual
        currency: str,  # USD/CNY
        gross_amount: float,
        net_amount: float = None,
        category: str = "广告分成",
        description: str = "",
        source_ip: str = None,
        customer_name: str = None,
        payment_method: str = None,
        exchange_rate: float = None,
        date_str: str = None,
        status: str = "pending",  # pending/settled/cancelled
    ):
        self.order_id = order_id
        self.channel = channel
        self.currency = currency
        self.gross_amount = float(gross_amount)
        self.net_amount = net_amount if net_amount is not None else gross_amount
        self.category = category
        self.description = description
        self.source_ip = source_ip
        self.customer_name = customer_name
        self.payment_method = payment_method
        self.exchange_rate = exchange_rate or self._get_exchange_rate()
        self.date = date_str or datetime.now().strftime("%Y-%m-%d")
        self.status = status
        self.settled_at = None

    def _get_exchange_rate(self) -> float:
        """获取默认汇率（简单模拟）"""
        return 7.25  # 1 USD ≈ 7.25 CNY（2026年4月参考值）

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "channel": self.channel,
            "currency": self.currency,
            "gross_amount": self.gross_amount,
            "net_amount": self.net_amount,
            "category": self.category,
            "description": self.description,
            "source_ip": self.source_ip,
            "customer_name": self.customer_name,
            "payment_method": self.payment_method,
            "exchange_rate": self.exchange_rate,
            "date": self.date,
            "status": self.status,
        }


# ============ 支付代理人核心 ============

class PaymentAgent:
    """
    动漫出海运营 · 支付收款代理人

    核心职责：
    1. 接收国际平台广告收益（YouTube/TikTok → Payoneer/PingPong）
    2. 结汇成人民币，转入国内账户
    3. 接收国内客户付款（微信/支付宝）
    4. 管理多个支付渠道的资金流
    5. 自动对账 + 生成财务报表
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or OUTPUT_DIR)
        self.data_dir.mkdir(exist_ok=True)
        self.records_file = self.data_dir / "payment_records.json"
        self.records: list[PaymentRecord] = []
        self._load()

        # 支付渠道配置
        self.channels = {
            "youtube": {"currency": "USD", "platform": "YouTube Partner"},
            "tiktok": {"currency": "USD", "platform": "TikTok Creator Fund"},
            "payoneer": {"currency": "USD", "platform": "Payoneer"},
            "pingpong": {"currency": "USD", "platform": "PingPong"},
            "wise": {"currency": "USD", "platform": "Wise"},
            "alipay": {"currency": "CNY", "platform": "支付宝"},
            "wechat": {"currency": "CNY", "platform": "微信支付"},
            "bank": {"currency": "CNY", "platform": "国内银行转账"},
            "manual": {"currency": "CNY", "platform": "手动入账"},
        }

    def _load(self):
        if self.records_file.exists():
            try:
                data = json.loads(self.records_file.read_text(encoding="utf-8"))
                for r in data.get("records", []):
                    # backward compat: rename 'date' key
                    if "date" in r and "date_str" not in r:
                        r["date_str"] = r.pop("date")
                    self.records.append(PaymentRecord(**r))
                logger.info(f"已加载 {len(self.records)} 条支付记录")
            except Exception as e:
                logger.error(f"加载支付记录失败: {e}")

    def _save(self):
        data = {
            "records": [r.to_dict() for r in self.records],
            "last_updated": datetime.now().isoformat(),
        }
        self.records_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _generate_order_id(self, prefix: str = "PAY") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        rand = str(int(time.time() * 1000))[-4:]
        return f"{prefix}{ts}{rand}"

    # ============ 收款入口 ============

    def receive_youtube_revenue(self, gross_usd: float, month: str = None,
                                 description: str = "") -> PaymentRecord:
        """
        记录 YouTube 广告收益

        Args:
            gross_usd: YouTube 支付的美元金额（毛收入）
            month: 收益所属月份 "YYYY-MM"
            description: 描述，如 "斗罗大陆 EP5 广告分成"
        """
        # YouTube 平台抽成45%，到手约55%
        net_usd = gross_usd * 0.55

        record = PaymentRecord(
            order_id=self._generate_order_id("YT"),
            channel="youtube",
            currency="USD",
            gross_amount=gross_usd,
            net_amount=net_usd,
            category="广告分成",
            description=description or f"YouTube广告收益 {month or '当月'}",
            payment_method="YouTube AdSense",
            status="received",  # 已到账
        )

        self.records.append(record)
        self._save()
        logger.info(f"YouTube收益入账: ${gross_usd:.2f} (净额${net_usd:.2f})")
        return record

    def receive_tiktok_revenue(self, gross_usd: float, description: str = "") -> PaymentRecord:
        """记录 TikTok Creator Fund 收益"""
        # TikTok 抽成50%
        net_usd = gross_usd * 0.50

        record = PaymentRecord(
            order_id=self._generate_order_id("TT"),
            channel="tiktok",
            currency="USD",
            gross_amount=gross_usd,
            net_amount=net_usd,
            category="Creator Fund",
            description=description or "TikTok Creator Fund",
            payment_method="TikTok Creator Fund",
            status="received",
        )

        self.records.append(record)
        self._save()
        logger.info(f"TikTok收益入账: ${gross_usd:.2f} (净额${net_usd:.2f})")
        return record

    def receive_payoneer_transfer(self, gross_usd: float, description: str = "",
                                    source: str = "youtube") -> PaymentRecord:
        """
        记录 Payoneer 到账（从YouTube/PingPong等转入）

        注意：Payoneer接收时不扣手续费，但提现到国内银行会扣1-2%
        """
        fee = gross_usd * 0.015  # 提现手续费约1.5%
        net_cny = (gross_usd - fee) * 7.25  # 换汇后人民币

        record = PaymentRecord(
            order_id=self._generate_order_id("PP"),
            channel="payoneer",
            currency="USD",
            gross_amount=gross_usd,
            net_amount=gross_usd - fee,
            category="国际收款",
            description=description or f"Payoneer收款 来源:{source}",
            payment_method=f"Payoneer({source})",
            status="pending_settlement",
        )

        self.records.append(record)
        self._save()
        logger.info(f"Payoneer收款: ${gross_usd:.2f} → 预计到账 ¥{net_cny:.2f}")
        return record

    def receive_alipay(
        self,
        amount: float,
        customer_name: str = None,
        description: str = "",
        order_id: str = None,
    ) -> PaymentRecord:
        """
        记录支付宝收款（人民币）

        场景：
        - 粉丝打赏
        - 客户私单付款
        - 代办服务费
        - 动漫周边销售
        """
        record = PaymentRecord(
            order_id=order_id or self._generate_order_id("ALI"),
            channel="alipay",
            currency="CNY",
            gross_amount=amount,
            net_amount=amount,  # 支付宝收款不扣手续费
            category="国内收款",
            description=description,
            customer_name=customer_name,
            payment_method="支付宝转账",
            status="received",
        )

        self.records.append(record)
        self._save()
        logger.info(f"支付宝收款: ¥{amount:.2f} ({customer_name or '匿名'}) - {description}")
        return record

    def receive_wechat(
        self,
        amount: float,
        customer_name: str = None,
        description: str = "",
        order_id: str = None,
    ) -> PaymentRecord:
        """
        记录微信支付收款（人民币）
        """
        record = PaymentRecord(
            order_id=order_id or self._generate_order_id("WX"),
            channel="wechat",
            currency="CNY",
            gross_amount=amount,
            net_amount=amount,
            category="国内收款",
            description=description,
            customer_name=customer_name,
            payment_method="微信转账",
            status="received",
        )

        self.records.append(record)
        self._save()
        logger.info(f"微信收款: ¥{amount:.2f} ({customer_name or '匿名'}) - {description}")
        return record

    def receive_bank_transfer(
        self,
        amount: float,
        bank_name: str = "国内银行",
        description: str = "",
        order_id: str = None,
    ) -> PaymentRecord:
        """记录银行转账收款"""
        record = PaymentRecord(
            order_id=order_id or self._generate_order_id("BANK"),
            channel="bank",
            currency="CNY",
            gross_amount=amount,
            net_amount=amount,
            category="国内收款",
            description=description,
            payment_method=f"银行转账({bank_name})",
            status="received",
        )

        self.records.append(record)
        self._save()
        logger.info(f"银行收款: ¥{amount:.2f} ({bank_name})")
        return record

    # ============ 收款二维码生成 ============

    def generate_alipay_qr(
        self,
        amount: float = None,
        note: str = "动漫出海运营收款",
    ) -> str:
        """
        生成支付宝收款码链接

        方式1: 使用支付宝「向支付宝转账」功能生成链接
        方式2: 使用第三方聚合码服务（如PAYJS）

        推荐：直接用支付宝App生成「转账码」给客户扫码付

        这里生成的是一个展示用的收款信息文件
        """
        qr_info = {
            "type": "alipay",
            "amount": amount,
            "note": note,
            "qr_url": f"https://qr.alipay.com/{self._generate_order_id('AX')}",
            "direct_link": f"https://personaltransfer.alipay.com/render?amount={amount or ''}&memo={note}",
            "how_to": "1. 打开支付宝 → 右上角+ → 收款 → 收款码\n2. 保存收款码发给客户\n3. 或者直接生成转账链接",
            "tip": "推荐使用「商家收钱码」开通后支持信用卡支付，费率0.6%",
        }

        info_file = self.data_dir / f"alipay_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        info_file.write_text(json.dumps(qr_info, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(f"支付宝收款信息已生成: {info_file}")
        return str(info_file)

    def generate_wechat_qr(
        self,
        amount: float = None,
        note: str = "动漫出海运营收款",
    ) -> str:
        """
        生成微信收款码指引

        微信支付个人收款码无法API直接生成，需要：
        1. 商家二维码（已认证商户）
        2. 第三方聚合支付（如PAYJS）
        """
        qr_info = {
            "type": "wechatpay",
            "amount": amount,
            "note": note,
            "how_to": "1. 打开微信 → 我 → 服务 → 收付款\n2. 向下滚动 → 二维码收款\n3. 保存收款码发给客户\n4. 或者使用「微信收款商业版」开通商家码",
            "tip": "推荐开通「微信小商店」或「微店」，支持自动发货+信用卡",
            "note2": "微信个人码每年限额20万，超额需升级商家码",
        }

        info_file = self.data_dir / f"wechat_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        info_file.write_text(json.dumps(qr_info, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(f"微信收款信息已生成: {info_file}")
        return str(info_file)

    # ============ 结汇（美元→人民币）============

    def settle_usd_to_cny(
        self,
        amount_usd: float,
        via: str = "pingpong",  # payoneer / pingpong / wise / manual
        target_account: str = "支付宝/微信",
    ) -> dict:
        """
        发起结汇（美元兑换人民币）

        Args:
            amount_usd: 要结汇的美元金额
            via: 通过哪个平台结汇
            target_account: 目标账户（支付宝/微信/银行卡）
        """
        fees = {
            "payoneer": amount_usd * 0.02,  # ~2%
            "pingpong": amount_usd * 0.01,  # ~1%
            "wise": amount_usd * 0.01,      # ~1%
            "manual": 0,
        }

        rates = {
            "payoneer": 7.20,  # 实际汇率（略低）
            "pingpong": 7.23,  # PingPong汇率较优
            "wise": 7.24,      # Wise汇率最优
            "manual": 7.25,    # 参考汇率
        }

        fee = fees.get(via, 0)
        rate = rates.get(via, 7.25)
        net_usd = amount_usd - fee
        cny_amount = net_usd * rate

        record = PaymentRecord(
            order_id=self._generate_order_id("SETTLE"),
            channel=via,
            currency="USD→CNY",
            gross_amount=amount_usd,
            net_amount=cny_amount,
            category="结汇",
            description=f"美元结汇 → {target_account} via {via}",
            payment_method=via,
            exchange_rate=rate,
            status="settling",
        )

        self.records.append(record)
        self._save()

        result = {
            "original_usd": amount_usd,
            "fee_usd": fee,
            "exchange_rate": rate,
            "net_cny": cny_amount,
            "via": via,
            "target": target_account,
            "arrival_estimate": "1-3个工作日",
            "order_id": record.order_id,
        }

        logger.info(f"结汇发起: ${amount_usd:.2f} → ¥{cny_amount:.2f} via {via}")
        return result

    # ============ 对账与统计 ============

    def get_balance(self, currency: str = None) -> dict:
        """查询各渠道余额"""
        balance = {"USD": 0.0, "CNY": 0.0}

        for r in self.records:
            if r.status in ["received", "pending_settlement"]:
                if currency is None or r.currency == currency:
                    if r.currency == "USD":
                        balance["USD"] += r.net_amount
                    elif r.currency == "CNY":
                        balance["CNY"] += r.net_amount
                    elif "CNY" in r.currency:
                        balance["CNY"] += r.net_amount

        return balance

    def get_monthly_summary(self, year: int = None, month: int = None) -> dict:
        """月度收支汇总"""
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month

        start = f"{year}-{month:02d}-01"
        if month == 12:
            end = f"{year+1}-01-01"
        else:
            end = f"{year}-{month+1:02d}-01"

        entries = [r for r in self.records if start <= r.date < end]

        summary = {
            "year": year,
            "month": month,
            "period": f"{year}年{month}月",
            "total_usd_gross": sum(r.gross_amount for r in entries if r.currency == "USD"),
            "total_usd_net": sum(r.net_amount for r in entries if r.currency == "USD"),
            "total_cny_gross": sum(r.gross_amount for r in entries if r.currency == "CNY"),
            "total_cny_net": sum(r.net_amount for r in entries if r.currency == "CNY"),
            "usd_to_cny_settled": sum(r.net_amount for r in entries if r.currency == "CNY" and r.category == "结汇"),
            "by_channel": {},
            "by_category": {},
            "record_count": len(entries),
        }

        for r in entries:
            summary["by_channel"][r.channel] = summary["by_channel"].get(r.channel, 0.0) + r.net_amount
            summary["by_category"][r.category] = summary["by_category"].get(r.category, 0.0) + r.net_amount

        # 换算总资产（折合人民币）
        summary["total_assets_cny"] = (
            summary["total_usd_net"] * 7.25 + summary["total_cny_net"]
        )

        return summary

    # ============ 收款报告生成 ============

    def generate_payment_report(self, year: int = None, month: int = None) -> str:
        """生成收款报告"""
        summary = self.get_monthly_summary(year, month)
        balance = self.get_balance()

        report = f"""
{'='*60}
动漫出海运营 · 收款报告 {summary['period']}
{'='*60}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 资产概览
───────────────────────────
  💵 美元余额 (USD):  ${balance['USD']:.2f}
  💰 人民币余额 (CNY): ¥{balance['CNY']:.2f}
  📍 总资产(折合):     ¥{balance['USD']*7.25 + balance['CNY']:.2f}

💵 本月收入
───────────────────────────
  国际收益:
    YouTube (USD):   ${summary['total_usd_gross']:.2f} (净额${summary['total_usd_net']:.2f})
    结汇入账:        ¥{summary['usd_to_cny_settled']:.2f}

  国内收益:
    人民币收款:       ¥{summary['total_cny_gross']:.2f} (净额¥{summary['total_cny_net']:.2f})

  总收入(折合CNY):   ¥{summary['total_assets_cny']:.2f}

📦 渠道分布（净额）
───────────────────────────
"""
        for channel, amount in sorted(summary["by_channel"].items(), key=lambda x: x[1], reverse=True):
            ch_info = self.channels.get(channel, {})
            ch_name = ch_info.get("platform", channel)
            symbol = "$" if ch_info.get("currency") == "USD" else "¥"
            report += f"  {ch_name:18s} {symbol}{amount:10.2f}\n"

        report += f"""
📋 收款渠道说明
───────────────────────────
  ✅ YouTube/TikTok 收益 → Payoneer/PingPong（美元账户）
  ✅ 国际收款结汇 → ¥人民币 → 转入支付宝/微信/银行卡
  ✅ 国内客户付款 → 支付宝/微信收款码（人民币）
  ⚠️  微信/支付宝个人码年度限额20万，需升级商家码

💡 推荐配置
───────────────────────────
  日常收款: 支付宝/微信收款码（零手续费）
  大额收款: 银行转账（更正式、可开发票）
  国际结汇: PingPong（费率低、到账快）

{'='*60}
"""
        return report

    def export_receipt(self, order_id: str, output_path: str = None) -> str:
        """导出收款凭证"""
        record = next((r for r in self.records if r.order_id == order_id), None)
        if not record:
            return f"未找到订单: {order_id}"

        if output_path is None:
            output_path = self.data_dir / f"receipt_{order_id}.txt"

        receipt = f"""
{'='*50}
         动漫出海运营 · 收款凭证
{'='*50}
订单编号:    {record.order_id}
收款渠道:    {record.channel}
支付方式:    {record.payment_method}
币种:       {record.currency}
收款金额:    {record.gross_amount}
净额:       {record.net_amount}
汇率:       {record.exchange_rate}
收款日期:    {record.date}
收款类型:    {record.category}
商品描述:    {record.description}
客户名称:    {record.customer_name or 'N/A'}
状态:       {record.status}
{'='*50}
"""
        Path(output_path).write_text(receipt, encoding="utf-8")
        return str(output_path)


# ============ 快捷收款链接生成 ============

class QuickPaymentLinks:
    """快速生成收款链接"""

    @staticmethod
    def alipay_transfer_link(
        amount: float = None,
        note: str = "动漫出海运营收款",
    ) -> str:
        """
        生成支付宝转账链接

        完整URL格式：
        https://personaltransfer.alipay.com/render?amount=XXX&memo=XXX
        """
        from urllib.parse import quote
        memo = quote(note)
        base = "https://personaltransfer.alipay.com/render"
        if amount:
            return f"{base}?amount={amount}&memo={memo}"
        return f"{base}?memo={memo}"

    @staticmethod
    def generate_payment_page(
        title: str,
        amount_cny: float,
        description: str = "",
        wechat_url: str = None,
        alipay_url: str = None,
    ) -> str:
        """
        生成一个简单的收款引导页面（HTML）

        用途：发给客户，让对方选择微信或支付宝支付
        """
        html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>支付页面 - {title}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          max-width: 480px; margin: 0 auto; padding: 40px 20px;
          background: #f5f5f5; }}
  .card {{ background: white; border-radius: 16px; padding: 30px;
           box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px; }}
  h2 {{ text-align: center; color: #1a1a2e; margin-bottom: 5px; }}
  .amount {{ text-align: center; font-size: 2.5em; font-weight: bold;
             color: #e94560; margin: 20px 0; }}
  .desc {{ text-align: center; color: #888; margin-bottom: 30px; }}
  .method {{ display: block; width: 100%; padding: 16px; border-radius: 12px;
             font-size: 16px; font-weight: 600; text-align: center;
             text-decoration: none; margin: 12px 0; color: white; }}
  .alipay {{ background: #1677ff; }}
  .wechat {{ background: #07c160; }}
  .note {{ text-align: center; color: #aaa; font-size: 0.85em; margin-top: 20px; }}
</style>
</head>
<body>
<div class="card">
  <h2>动漫出海运营</h2>
  <div class="amount">¥{amount_cny:.2f}</div>
  <div class="desc">{description or title}</div>

  <a href="{alipay_url or '#'}" class="method alipay">
    🟠 支付宝支付
  </a>
  <a href="{wechat_url or '#'}" class="method wechat">
    🟢 微信支付
  </a>

  <div class="note">
    支付完成后请联系确认收款<br>
    24小时内到账确认
  </div>
</div>
</body>
</html>"""
        output_path = OUTPUT_DIR / f"payment_page_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        output_path.write_text(html, encoding="utf-8")
        return str(output_path)


if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    print("=" * 60)
    print("动漫出海运营 · 支付收款代理人")
    print("=" * 60)

    agent = PaymentAgent()

    # 演示：模拟收款
    print("\n[1] 模拟 YouTube 收益到账...")
    agent.receive_youtube_revenue(125.50, "2026-04", "斗罗大陆 EP5 广告分成")

    print("\n[2] 模拟 TikTok 收益到账...")
    agent.receive_tiktok_revenue(45.00, "凡人修仙传 EP3")

    print("\n[3] 模拟客户支付宝付款...")
    agent.receive_alipay(299, "王先生", "动漫解说商单-1条", "粉丝商单")

    print("\n[4] 模拟客户微信付款...")
    agent.receive_wechat(599, "李小姐", "动漫解说商单-全套3条", "商单全款")

    print("\n[5] 模拟结汇操作...")
    result = agent.settle_usd_to_cny(100, via="pingpong", target_account="支付宝")
    print(f"    结汇结果: USD {result['original_usd']:.2f} -> CNY {result['net_cny']:.2f}")
    print(f"    手续费: USD {result['fee_usd']:.2f} | 汇率: {result['exchange_rate']}")

    print("\n[6] 生成收款报告...")
    report = agent.generate_payment_report()
    print(report)

    print("\n[7] 当前余额...")
    balance = agent.get_balance()
    print(f"    USD: {balance['USD']:.2f}")
    print(f"    CNY: {balance['CNY']:.2f}")

    print("\n[8] 生成收款页面...")
    page = QuickPaymentLinks.generate_payment_page(
        title="动漫解说商单",
        amount_cny=599,
        description="动漫解说商单-全套3条",
        alipay_url=QuickPaymentLinks.alipay_transfer_link(599, note="动漫商单"),
    )
    print(f"    收款页面已生成: {page}")
