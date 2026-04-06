# -*- coding: utf-8 -*-
"""
SCOTT豆包賺錢代理人 - Flask Web服务
支持支付宝收款、订单管理、自动化运营
"""

# 品牌配置
BRAND_NAME = "SCOTT豆包賺錢代理人"
BRAND_TAGLINE = "AI代运营 · 自动变现 · 轻松赚钱"

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from datetime import datetime

from config import get_config, print_config_guide
from alipay_service import AlipayService, AlipayConfig
from order_service import OrderService, PRODUCTS
from notification import NotificationService, AutomationService

# 加载配置
config = get_config()

# 验证配置
errors = config.validate()
if errors:
    print("\n⚠️  配置警告:")
    for error in errors:
        print(f"   - {error}")
    print_config_guide()

# 确保数据目录存在
os.makedirs(os.path.dirname(config.db_path) if os.path.dirname(config.db_path) else './data', exist_ok=True)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'douyin-agent-secret-key-change-in-production'
CORS(app)

# 初始化服务
alipay_config = AlipayConfig(
    mode=config.alipay_mode,
    app_id=config.alipay_app_id,
    private_key=config.alipay_private_key,
    alipay_public_key=config.alipay_public_key,
    personal_qr_url=config.personal_alipay_account,
    notify_url=config.alipay_notify_url,
    return_url=config.alipay_return_url
)
alipay_service = AlipayService(alipay_config)
order_service = OrderService(config.db_path)
notification_service = NotificationService()
automation_service = AutomationService()


# ==================== API接口 ====================

@app.route('/api/create-order', methods=['POST'])
def create_order():
    """创建支付订单"""
    try:
        data = request.get_json()
        product_id = data.get('product_id', 'custom')
        amount = float(data.get('amount', 0))
        customer = data.get('customer', {})

        # 验证金额
        if amount < config.min_amount:
            return jsonify({
                'success': False,
                'message': f'金额不能低于{config.min_amount}元'
            }), 400

        # 获取产品信息
        product_info = PRODUCTS.get(product_id, PRODUCTS['custom'])
        product_name = product_info['name']

        # 如果金额为0，使用产品定价
        if amount == 0:
            amount = product_info['price']

        # 创建订单
        order = order_service.create_order(
            product_id=product_id,
            product_name=product_name,
            amount=amount,
            customer_name=customer.get('name', ''),
            customer_phone=customer.get('phone', ''),
            customer_email=customer.get('email', ''),
            customer_remark=customer.get('remark', '')
        )

        # 生成支付二维码
        qr_result = alipay_service.create_qr_code(
            amount=amount,
            subject=f"SCOTT豆包賺錢-{product_name}",
            out_trade_no=order.order_id
        )

        return jsonify({
            'success': True,
            'order_id': order.order_id,
            'amount': amount,
            'qr_code': qr_result.get('qr_code', ''),
            'pay_url': qr_result.get('pay_url', ''),
            'instructions': qr_result.get('instructions', []),
            'message': '订单创建成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建订单失败: {str(e)}'
        }), 500


@app.route('/api/order-status/<order_id>', methods=['GET'])
def get_order_status(order_id):
    """查询订单状态"""
    try:
        order = order_service.get_order(order_id)

        if not order:
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404

        return jsonify({
            'success': True,
            'order_id': order.order_id,
            'status': order.status,
            'amount': order.amount,
            'product_name': order.product_name,
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'paid_at': order.paid_at,
            'created_at': order.created_at
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/alipay-notify', methods=['POST'])
def alipay_notify():
    """支付宝异步回调通知"""
    try:
        data = request.form.to_dict()

        # 验证签名
        if not alipay_service.verify_notification(data):
            return jsonify({'success': False, 'message': '签名验证失败'}), 400

        # 处理回调
        out_trade_no = data.get('out_trade_no', '')
        trade_status = data.get('trade_status', '')
        trade_no = data.get('trade_no', '')

        if trade_status == 'TRADE_SUCCESS':
            order_service.update_order_status(
                order_id=out_trade_no,
                status='paid',
                trade_no=trade_no,
                paid_at=datetime.now().isoformat()
            )

            # 触发后续交付流程
            order = order_service.get_order(out_trade_no)
            if order:
                trigger_delivery(order)

        return jsonify({'success': True, 'msg': 'success'})

    except Exception as e:
        return jsonify({'success': False, 'msg': str(e)}), 500


@app.route('/api/manual-pay/<order_id>', methods=['POST'])
def manual_pay(order_id):
    """手动确认付款（个人模式使用）"""
    try:
        order = order_service.get_order(order_id)
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404

        if order.status == 'paid':
            return jsonify({'success': True, 'message': '订单已是已支付状态'})

        # 更新为已支付
        order_service.update_order_status(
            order_id=order_id,
            status='paid',
            trade_no=f'MANUAL_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            paid_at=datetime.now().isoformat()
        )

        # 触发交付流程
        order = order_service.get_order(order_id)
        if order:
            trigger_delivery(order)

        return jsonify({
            'success': True,
            'message': '手动确认付款成功'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/daily-stats', methods=['GET'])
def get_daily_stats():
    """获取每日统计"""
    date = request.args.get('date')
    stats = order_service.get_daily_stats(date)
    return jsonify({'success': True, 'data': stats})


@app.route('/api/weekly-stats', methods=['GET'])
def get_weekly_stats():
    """获取本周统计"""
    stats = order_service.get_weekly_stats()
    return jsonify({'success': True, 'data': stats})


@app.route('/api/export-orders', methods=['GET'])
def export_orders():
    """导出订单数据"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')

    orders = order_service.export_orders(start_date, end_date, status)
    return jsonify({
        'success': True,
        'data': orders,
        'total': len(orders)
    })


@app.route('/api/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    return jsonify({'success': True, 'data': PRODUCTS})


@app.route('/api/config-info', methods=['GET'])
def get_config_info():
    """获取配置信息（不包含敏感数据）"""
    return jsonify({
        'success': True,
        'data': {
            'alipay_mode': config.alipay_mode,
            'domain': config.domain,
            'min_amount': config.min_amount,
            'enable_email': config.enable_email,
            'enable_sms': config.enable_sms
        }
    })


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """首页/支付落地页"""
    return render_template_string(PAYMENT_PAGE_HTML)


@app.route('/payment/<order_id>')
def payment_page(order_id):
    """订单支付页面"""
    order = order_service.get_order(order_id)
    if not order:
        return "订单不存在", 404
    return render_template_string(PAYMENT_PAGE_HTML, order=order)


@app.route('/success/<order_id>')
def payment_success(order_id):
    """支付成功页面"""
    order = order_service.get_order(order_id)
    if not order:
        return "订单不存在", 404
    return render_template_string(SUCCESS_PAGE_HTML, order=order)


@app.route('/admin')
def admin():
    """管理后台"""
    return render_template_string(ADMIN_PAGE_HTML)


# ==================== 辅助函数 ====================

# ==================== n8n 集成接口 ====================

@app.route('/api/n8n-webhook', methods=['POST'])
def n8n_webhook():
    """
    n8n Webhook 端点
    当收到支付成功通知时，触发 n8n 工作流
    """
    try:
        data = request.get_json()
        event_type = data.get('event', 'payment_completed')

        if event_type == 'payment_completed':
            order_data = data.get('order', {})
            customer_data = data.get('customer', {})

            # 触发自动化流程
            automation_service.on_payment_received({
                'order_id': order_data.get('order_id'),
                'customer_name': customer_data.get('name'),
                'customer_phone': customer_data.get('phone'),
                'customer_email': customer_data.get('email'),
                'product_name': order_data.get('product_name'),
                'amount': order_data.get('amount')
            })

            return jsonify({'success': True, 'message': 'Webhook processed'})

        return jsonify({'success': False, 'message': 'Unknown event type'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/get-orders', methods=['GET'])
def get_orders_for_n8n():
    """
    获取所有订单（供 n8n 轮询使用）
    """
    try:
        orders = order_service.get_all_orders()
        return jsonify({
            'success': True,
            'orders': [
                {
                    'order_id': o.order_id,
                    'product_name': o.product_name,
                    'amount': o.amount,
                    'status': o.status,
                    'customer_name': o.customer_name,
                    'customer_phone': o.customer_phone,
                    'customer_email': o.customer_email,
                    'paid_at': o.paid_at,
                    'created_at': o.created_at
                }
                for o in orders
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/trigger-automation', methods=['POST'])
def trigger_automation():
    """
    手动触发自动化流程（用于 n8n 调用）
    """
    try:
        data = request.get_json()
        order_id = data.get('order_id')

        if order_id:
            order = order_service.get_order(order_id)
            if order:
                trigger_delivery(order)
                return jsonify({'success': True, 'message': 'Automation triggered'})

        return jsonify({'success': False, 'message': 'Order not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def trigger_delivery(order):
    """触发服务交付流程"""
    print(f"[交付触发] 订单 {order.order_id} 支付成功，开始交付流程")

    # 更新订单状态为处理中
    order_service.update_order_status(order.order_id, 'processing')

    # 发送邮件通知
    if config.enable_email and order.customer_email:
        from notification import Customer
        customer = Customer(
            name=order.customer_name,
            phone=order.customer_phone,
            email=order.customer_email
        )
        order_dict = {
            'order_id': order.order_id,
            'product_name': order.product_name,
            'amount': order.amount
        }
        notification_service.send_order_confirmation(customer, order_dict)

    # 发送短信通知
    if config.enable_sms:
        notification_service.send_order_notification_sms(
            order.customer_phone,
            order.order_id
        )

    # 触发自动化流程
    automation_service.on_payment_received({
        'order_id': order.order_id,
        'customer_name': order.customer_name,
        'customer_phone': order.customer_phone,
        'customer_email': order.customer_email,
        'product_name': order.product_name,
        'amount': order.amount
    })

    print(f"[交付完成] 订单 {order.order_id} 交付流程已触发")


# ==================== HTML模板 ====================

PAYMENT_PAGE_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCOTT豆包賺錢代理人 - 支付宝收款</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-blue-50 via-white to-cyan-50 min-h-screen">
    <div id="app" class="max-w-md mx-auto p-6">
        <div class="text-center mb-8">
            <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span class="text-white text-2xl font-bold">AI</span>
            </div>
            <h1 class="text-2xl font-bold text-gray-800">SCOTT豆包賺錢代理人</h1>
            <p class="text-gray-500 mt-2">专业AI代运营服务</p>
        </div>

        <!-- 步骤1: 选择金额 -->
        <div id="step1" class="bg-white rounded-2xl shadow-lg p-6">
            <h2 class="text-lg font-bold mb-4">选择或输入金额</h2>

            <div class="grid grid-cols-3 gap-3 mb-4">
                <button onclick="selectAmount(199)" class="py-3 bg-gray-100 rounded-xl hover:bg-blue-100 transition">¥199</button>
                <button onclick="selectAmount(399)" class="py-3 bg-gray-100 rounded-xl hover:bg-blue-100 transition">¥399</button>
                <button onclick="selectAmount(599)" class="py-3 bg-gray-100 rounded-xl hover:bg-blue-100 transition">¥599</button>
                <button onclick="selectAmount(999)" class="py-3 bg-gray-100 rounded-xl hover:bg-blue-100 transition">¥999</button>
                <button onclick="selectAmount(1999)" class="py-3 bg-gray-100 rounded-xl hover:bg-blue-100 transition">¥1999</button>
                <button onclick="selectAmount(2999)" class="py-3 bg-gray-100 rounded-xl hover:bg-blue-100 transition">¥2999</button>
            </div>

            <div class="mb-6">
                <label class="block text-sm text-gray-600 mb-2">自定义金额（最低99元）</label>
                <input type="number" id="customAmount" placeholder="输入金额" min="99"
                    class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none">
            </div>

            <button onclick="goToStep2()" id="nextBtn" disabled
                class="w-full py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-medium disabled:opacity-50">
                下一步：填写信息
            </button>
        </div>

        <!-- 步骤2: 填写信息 -->
        <div id="step2" class="bg-white rounded-2xl shadow-lg p-6 hidden">
            <button onclick="goToStep1()" class="text-blue-600 mb-4">← 返回</button>

            <div class="text-center mb-6">
                <span class="text-3xl font-bold text-blue-600">¥<span id="showAmount">0</span></span>
            </div>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm text-gray-600 mb-1">姓名 *</label>
                    <input type="text" id="customerName" placeholder="请输入姓名"
                        class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm text-gray-600 mb-1">手机号码 *</label>
                    <input type="tel" id="customerPhone" placeholder="请输入手机号"
                        class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm text-gray-600 mb-1">邮箱（选填）</label>
                    <input type="email" id="customerEmail" placeholder="用于接收服务文件"
                        class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm text-gray-600 mb-1">备注（选填）</label>
                    <textarea id="customerRemark" rows="2" placeholder="请描述您的需求"
                        class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none resize-none"></textarea>
                </div>
            </div>

            <button onclick="createOrder()" id="createBtn"
                class="w-full mt-6 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-medium flex items-center justify-center gap-2">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 22c-5.523 0-10-4.477-10-10S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-1-15v6H7l5 5 5-5h-4V7h-2z"/></svg>
                <span>生成支付宝支付</span>
            </button>
        </div>

        <!-- 步骤3: 扫码支付 -->
        <div id="step3" class="bg-white rounded-2xl shadow-lg p-6 hidden">
            <button onclick="goToStep2()" class="text-blue-600 mb-4">← 返回修改</button>

            <div class="text-center mb-4">
                <span class="text-3xl font-bold text-blue-600">¥<span id="payAmount">0</span></span>
            </div>

            <div class="bg-gray-50 rounded-xl p-4 mb-4">
                <img id="qrCode" src="" alt="支付二维码" class="w-48 h-48 mx-auto">
                <p class="text-center text-gray-500 mt-4">请使用支付宝扫描二维码支付</p>
            </div>

            <div class="text-sm text-gray-500 space-y-2">
                <p>1. 打开手机支付宝</p>
                <p>2. 扫一扫上方二维码</p>
                <p>3. 完成支付</p>
            </div>

            <div class="mt-4 flex items-center justify-center gap-2 text-cyan-600">
                <div class="w-2 h-2 bg-cyan-500 rounded-full animate-pulse"></div>
                <span id="orderStatus">等待支付...</span>
            </div>

            <p class="text-center text-sm text-gray-400 mt-4">订单号: <span id="orderId" class="font-mono"></span></p>
        </div>

        <!-- 步骤4: 支付成功 -->
        <div id="step4" class="bg-white rounded-2xl shadow-lg p-6 text-center hidden">
            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
            </div>
            <h2 class="text-2xl font-bold text-green-600 mb-2">支付成功！</h2>
            <p class="text-gray-600 mb-4">感谢您的信任，我们将在24小时内与您联系</p>

            <div class="text-left bg-gray-50 rounded-xl p-4 text-sm">
                <p><span class="text-gray-500">订单号:</span> <span id="successOrderId" class="font-mono"></span></p>
                <p><span class="text-gray-500">金额:</span> ¥<span id="successAmount"></span></p>
            </div>

            <button onclick="location.reload()" class="mt-6 px-8 py-3 bg-gray-100 rounded-xl">返回首页</button>
        </div>

        <!-- 底部信息 -->
        <div class="mt-8 text-center text-sm text-gray-400">
            <p>支付宝官方认证商家 | 安全支付保障</p>
        </div>
    </div>

    <script>
        let selectedAmount = 0;

        function selectAmount(amount) {
            selectedAmount = amount;
            document.getElementById('customAmount').value = '';
            document.getElementById('nextBtn').disabled = false;
        }

        document.getElementById('customAmount').addEventListener('input', function(e) {
            const val = parseInt(e.target.value);
            if (val >= 99) {
                selectedAmount = val;
                document.getElementById('nextBtn').disabled = false;
            } else {
                selectedAmount = 0;
                document.getElementById('nextBtn').disabled = true;
            }
        });

        function goToStep1() {
            document.getElementById('step1').classList.remove('hidden');
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step3').classList.add('hidden');
            document.getElementById('step4').classList.add('hidden');
        }

        function goToStep2() {
            document.getElementById('step1').classList.add('hidden');
            document.getElementById('step2').classList.remove('hidden');
            document.getElementById('step3').classList.add('hidden');
            document.getElementById('step4').classList.add('hidden');
            document.getElementById('showAmount').textContent = selectedAmount;
        }

        async function createOrder() {
            const name = document.getElementById('customerName').value.trim();
            const phone = document.getElementById('customerPhone').value.trim();
            const email = document.getElementById('customerEmail').value.trim();
            const remark = document.getElementById('customerRemark').value.trim();

            if (!name || !phone) {
                alert('请填写姓名和手机号');
                return;
            }

            const btn = document.getElementById('createBtn');
            btn.disabled = true;
            btn.innerHTML = '<span>生成中...</span>';

            try {
                const res = await fetch('/api/create-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        product_id: 'custom',
                        amount: selectedAmount,
                        customer: {name, phone, email, remark}
                    })
                });

                const data = await res.json();

                if (data.success) {
                    document.getElementById('step2').classList.add('hidden');
                    document.getElementById('step3').classList.remove('hidden');
                    document.getElementById('payAmount').textContent = data.amount;
                    document.getElementById('qrCode').src = data.qr_code;
                    document.getElementById('orderId').textContent = data.order_id;
                    localStorage.setItem('currentOrderId', data.order_id);
                    checkPaymentStatus(data.order_id);
                } else {
                    alert(data.message || '创建订单失败');
                }
            } catch (err) {
                alert('网络错误，请重试');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>生成支付宝支付</span>';
            }
        }

        async function checkPaymentStatus(orderId) {
            const interval = setInterval(async () => {
                try {
                    const res = await fetch(`/api/order-status/${orderId}`);
                    const data = await res.json();

                    if (data.status === 'paid') {
                        clearInterval(interval);
                        document.getElementById('step3').classList.add('hidden');
                        document.getElementById('step4').classList.remove('hidden');
                        document.getElementById('successOrderId').textContent = orderId;
                        document.getElementById('successAmount').textContent = data.amount;
                    }
                } catch (err) {
                    console.error('查询失败');
                }
            }, 3000);
        }
    </script>
</body>
</html>
'''

SUCCESS_PAGE_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>支付成功 - SCOTT豆包賺錢代理人</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-green-50 via-white to-cyan-50 min-h-screen flex items-center justify-center">
    <div class="text-center">
        <div class="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        </div>
        <h1 class="text-3xl font-bold text-green-600 mb-4">支付成功！</h1>
        <p class="text-gray-600 mb-8">感谢您的信任，我们将在24小时内与您联系</p>

        <div class="bg-white rounded-2xl shadow-lg p-6 text-left max-w-md mx-auto">
            <h3 class="font-bold mb-4">订单信息</h3>
            <div class="space-y-2 text-sm">
                <p><span class="text-gray-500">订单号:</span> {{ order.order_id }}</p>
                <p><span class="text-gray-500">服务:</span> {{ order.product_name }}</p>
                <p><span class="text-gray-500">金额:</span> ¥{{ order.amount }}</p>
                <p><span class="text-gray-500">联系人:</span> {{ order.customer_name }}</p>
            </div>
        </div>

        <a href="/" class="inline-block mt-8 px-8 py-3 bg-gray-100 rounded-xl">返回首页</a>
    </div>
</body>
</html>
'''

ADMIN_PAGE_HTML = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理后台 - SCOTT豆包賺錢代理人</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <nav class="bg-white shadow-sm p-4">
        <div class="max-w-6xl mx-auto flex justify-between items-center">
            <h1 class="text-xl font-bold">SCOTT豆包賺錢代理人 - 管理后台</h1>
            <a href="/" class="text-blue-600">返回首页</a>
        </div>
    </nav>

    <main class="max-w-6xl mx-auto p-6">
        <!-- 统计卡片 -->
        <div class="grid grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl p-6">
                <p class="text-gray-500 text-sm">今日订单</p>
                <p class="text-3xl font-bold" id="todayOrders">-</p>
            </div>
            <div class="bg-white rounded-xl p-6">
                <p class="text-gray-500 text-sm">今日收款</p>
                <p class="text-3xl font-bold text-green-600" id="todayAmount">-</p>
            </div>
            <div class="bg-white rounded-xl p-6">
                <p class="text-gray-500 text-sm">本周收款</p>
                <p class="text-3xl font-bold text-blue-600" id="weekAmount">-</p>
            </div>
            <div class="bg-white rounded-xl p-6">
                <p class="text-gray-500 text-sm">新客户</p>
                <p class="text-3xl font-bold" id="newCustomers">-</p>
            </div>
        </div>

        <!-- 最近订单 -->
        <div class="bg-white rounded-xl p-6">
            <h2 class="text-lg font-bold mb-4">最近订单</h2>
            <table class="w-full">
                <thead>
                    <tr class="text-left text-gray-500 text-sm">
                        <th class="pb-3">订单号</th>
                        <th class="pb-3">客户</th>
                        <th class="pb-3">服务</th>
                        <th class="pb-3">金额</th>
                        <th class="pb-3">状态</th>
                        <th class="pb-3">时间</th>
                        <th class="pb-3">操作</th>
                    </tr>
                </thead>
                <tbody id="orderTable">
                    <tr><td colspan="7" class="text-center py-8 text-gray-400">加载中...</td></tr>
                </tbody>
            </table>
        </div>
    </main>

    <script>
        async function loadStats() {
            const res = await fetch('/api/daily-stats');
            const data = await res.json();
            if (data.success) {
                document.getElementById('todayOrders').textContent = data.data.total_orders;
                document.getElementById('todayAmount').textContent = '¥' + data.data.total_amount;
                document.getElementById('newCustomers').textContent = data.data.new_customers;
            }

            const weekRes = await fetch('/api/weekly-stats');
            const weekData = await weekRes.json();
            if (weekData.success) {
                document.getElementById('weekAmount').textContent = '¥' + weekData.data.total_amount;
            }
        }

        async function loadOrders() {
            const res = await fetch('/api/export-orders?limit=20');
            const data = await res.json();
            if (data.success && data.data.length > 0) {
                document.getElementById('orderTable').innerHTML = data.data.map(order => `
                    <tr class="border-t">
                        <td class="py-3 font-mono text-sm">${order.order_id}</td>
                        <td class="py-3">${order.customer_name}<br><span class="text-gray-400 text-sm">${order.customer_phone}</span></td>
                        <td class="py-3">${order.product_name}</td>
                        <td class="py-3 font-bold">¥${order.amount}</td>
                        <td class="py-3"><span class="px-2 py-1 rounded text-sm ${order.status === 'paid' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'}">${order.status === 'paid' ? '已支付' : '待支付'}</span></td>
                        <td class="py-3 text-gray-400 text-sm">${new Date(order.created_at).toLocaleDateString()}</td>
                        <td class="py-3">
                            ${order.status !== 'paid' ? `<button onclick="manualPay('${order.order_id}')" class="text-blue-600 hover:underline text-sm">确认收款</button>` : '-'}
                        </td>
                    </tr>
                `).join('');
            }
        }

        async function manualPay(orderId) {
            if (!confirm('确认已收到该订单的付款？')) return;
            const res = await fetch(`/api/manual-pay/${orderId}`, {method: 'POST'});
            const data = await res.json();
            if (data.success) {
                alert('已确认收款');
                loadOrders();
                loadStats();
            } else {
                alert(data.message || '操作失败');
            }
        }

        loadStats();
        loadOrders();
        setInterval(loadStats, 30000);
    </script>
</body>
</html>
'''


# ==================== 启动 ====================

if __name__ == '__main__':
    print("=" * 60)
    print("    SCOTT豆包賺錢代理人 - 支付服务")
    print("=" * 60)
    print(f"    支付模式: {config.alipay_mode}")
    print(f"    服务地址: http://127.0.0.1:5000")
    print(f"    管理后台: http://127.0.0.1:5000/admin")
    print("=" * 60)
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False
    )
