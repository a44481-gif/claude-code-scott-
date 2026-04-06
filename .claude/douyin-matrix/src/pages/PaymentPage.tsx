import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Alipay,
  CreditCard,
  CheckCircle,
  Clock,
  Users,
  Sparkles,
  ChevronRight,
  Copy,
  QrCode,
  Shield,
  Phone,
  MessageSquare,
  FileText,
  Zap,
  ArrowLeft
} from 'lucide-react'

// 服务产品数据
const products = [
  {
    id: 'ai-operation-basic',
    name: 'AI代运营基础版',
    price: 999,
    period: '月付',
    features: [
      '每月20条AI内容生成',
      '基础数据分析报表',
      '1对1咨询支持',
      '内容策略建议'
    ],
    popular: false
  },
  {
    id: 'ai-operation-pro',
    name: 'AI代运营进阶版',
    price: 2999,
    period: '月付',
    features: [
      '每日内容生成不限量',
      '竞品分析报告',
      'SEO优化建议',
      '优先1对1咨询',
      '平台数据监控'
    ],
    popular: true
  },
  {
    id: 'prompt-custom',
    name: 'AI提示词定制',
    price: 599,
    period: '次',
    features: [
      '按需定制提示词',
      '3次免费修改',
      '使用教程',
      '永久使用权'
    ],
    popular: false
  },
  {
    id: 'script-dev',
    name: 'AI脚本开发',
    price: 1999,
    period: '次',
    features: [
      '按场景定制脚本',
      '多版本备选',
      '5次修改机会',
      '交付文档'
    ],
    popular: false
  },
  {
    id: 'digital-human',
    name: 'AI数字人视频',
    price: 399,
    period: '条',
    features: [
      '模板数字人',
      '配音合成',
      '1080P输出',
      '24h内交付'
    ],
    popular: false
  }
]

// 固定金额选项
const fixedAmounts = [199, 399, 599, 999, 1999, 2999]

export default function PaymentPage() {
  const [step, setStep] = useState(1)
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [customAmount, setCustomAmount] = useState('')
  const [paymentAmount, setPaymentAmount] = useState<number | null>(null)
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    phone: '',
    email: '',
    remark: ''
  })
  const [orderResult, setOrderResult] = useState<any>(null)
  const [qrCodeUrl, setQrCodeUrl] = useState('')
  const [isCreatingOrder, setIsCreatingOrder] = useState(false)
  const [paymentStatus, setPaymentStatus] = useState<'pending' | 'paid' | 'checking'>('pending')

  // 创建订单
  const createOrder = async () => {
    setIsCreatingOrder(true)
    try {
      const res = await fetch('/api/create-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: selectedProduct?.id || 'custom',
          amount: paymentAmount,
          customer: customerInfo
        })
      })
      const data = await res.json()
      setOrderResult(data)
      setQrCodeUrl(data.qr_code)
      setStep(3)
    } catch (error) {
      console.error('创建订单失败:', error)
    } finally {
      setIsCreatingOrder(false)
    }
  }

  // 查询订单状态
  const checkOrderStatus = async (orderId: string) => {
    try {
      const res = await fetch(`/api/order-status/${orderId}`)
      const data = await res.json()
      if (data.status === 'paid') {
        setPaymentStatus('paid')
        setStep(4)
      }
      return data.status
    } catch (error) {
      console.error('查询订单失败:', error)
      return 'pending'
    }
  }

  // 轮询订单状态
  useEffect(() => {
    if (step === 3 && orderResult?.order_id) {
      const interval = setInterval(async () => {
        const status = await checkOrderStatus(orderResult.order_id)
        if (status === 'paid') {
          clearInterval(interval)
        }
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [step, orderResult])

  const selectProduct = (product: typeof products[0]) => {
    setSelectedProduct(product)
    setPaymentAmount(product.price)
  }

  const selectFixedAmount = (amount: number) => {
    setSelectedProduct(null)
    setPaymentAmount(amount)
  }

  const handleCustomAmount = (value: string) => {
    setCustomAmount(value)
    const num = parseInt(value)
    if (num > 0) {
      setPaymentAmount(num)
      setSelectedProduct(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      {/* 头部导航 */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                豆包运营代理人
              </span>
            </div>
            <div className="flex items-center gap-4">
              <a href="#services" className="text-gray-600 hover:text-blue-600 transition">服务项目</a>
              <a href="#pricing" className="text-gray-600 hover:text-blue-600 transition">价格方案</a>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
                联系我们
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* 步骤指示器 */}
        <div className="flex items-center justify-center mb-12">
          {[1, 2, 3, 4].map((s, i) => (
            <div key={s} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                step >= s
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-500'
              }`}>
                {step > s ? <CheckCircle className="w-5 h-5" /> : s}
              </div>
              <span className={`ml-2 text-sm ${step >= s ? 'text-blue-600' : 'text-gray-400'}`}>
                {s === 1 ? '选择服务' : s === 2 ? '填写信息' : s === 3 ? '扫码支付' : '完成'}
              </span>
              {i < 3 && <div className={`w-16 h-1 mx-2 rounded ${step > s ? 'bg-blue-600' : 'bg-gray-200'}`} />}
            </div>
          ))}
        </div>

        {/* 步骤1: 选择服务 */}
        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              {/* 产品展示 */}
              <section id="services" className="mb-12">
                <h2 className="text-3xl font-bold text-center mb-2">专业AI服务解决方案</h2>
                <p className="text-gray-500 text-center mb-8">选择适合您的服务，开启智能运营新时代</p>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {products.map((product) => (
                    <motion.div
                      key={product.id}
                      whileHover={{ scale: 1.02 }}
                      className={`bg-white rounded-2xl shadow-lg overflow-hidden border-2 transition ${
                        selectedProduct?.id === product.id ? 'border-blue-500' : 'border-transparent'
                      }`}
                    >
                      {product.popular && (
                        <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-center py-1 text-sm font-medium">
                          最受欢迎
                        </div>
                      )}
                      <div className="p-6">
                        <h3 className="text-xl font-bold mb-2">{product.name}</h3>
                        <div className="mb-4">
                          <span className="text-3xl font-bold text-blue-600">¥{product.price}</span>
                          <span className="text-gray-400">/{product.period}</span>
                        </div>
                        <ul className="space-y-2 mb-6">
                          {product.features.map((f, i) => (
                            <li key={i} className="flex items-center text-gray-600">
                              <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                              {f}
                            </li>
                          ))}
                        </ul>
                        <button
                          onClick={() => selectProduct(product)}
                          className={`w-full py-3 rounded-xl font-medium transition ${
                            selectedProduct?.id === product.id
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {selectedProduct?.id === product.id ? '已选择' : '选择此服务'}
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </section>

              {/* 自定义金额 */}
              <section id="pricing" className="bg-white rounded-2xl shadow-lg p-8">
                <h3 className="text-xl font-bold mb-4">自定义支付金额</h3>
                <div className="grid grid-cols-3 md:grid-cols-6 gap-3 mb-4">
                  {fixedAmounts.map((amount) => (
                    <button
                      key={amount}
                      onClick={() => selectFixedAmount(amount)}
                      className={`py-3 rounded-xl font-medium transition ${
                        paymentAmount === amount && !selectedProduct
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      ¥{amount}
                    </button>
                  ))}
                </div>
                <div className="flex gap-4">
                  <input
                    type="number"
                    placeholder="输入自定义金额（最低99元）"
                    value={customAmount}
                    onChange={(e) => handleCustomAmount(e.target.value)}
                    className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition"
                  />
                  <button
                    onClick={() => setStep(2)}
                    disabled={!paymentAmount || paymentAmount < 99}
                    className="px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-medium hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    下一步
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </section>

              {/* 服务优势 */}
              <section className="grid md:grid-cols-4 gap-6">
                {[
                  { icon: Zap, title: '快速响应', desc: '24小时内开始服务' },
                  { icon: Shield, title: '合规透明', desc: '支付宝官方支付' },
                  { icon: FileText, title: '正规合同', desc: '电子合同保障' },
                  { icon: MessageSquare, title: '专属客服', desc: '1对1全程服务' }
                ].map((item, i) => (
                  <div key={i} className="bg-white rounded-xl shadow p-6 text-center">
                    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                      <item.icon className="w-6 h-6 text-blue-600" />
                    </div>
                    <h4 className="font-bold mb-1">{item.title}</h4>
                    <p className="text-gray-500 text-sm">{item.desc}</p>
                  </div>
                ))}
              </section>
            </motion.div>
          )}

          {/* 步骤2: 填写信息 */}
          {step === 2 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-xl mx-auto"
            >
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <div className="flex items-center mb-6">
                  <button onClick={() => setStep(1)} className="p-2 hover:bg-gray-100 rounded-lg transition">
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                  <h2 className="text-2xl font-bold ml-4">填写联系信息</h2>
                </div>

                {selectedProduct && (
                  <div className="bg-blue-50 rounded-xl p-4 mb-6">
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="font-medium">{selectedProduct.name}</span>
                        <span className="text-gray-500 ml-2">({selectedProduct.period})</span>
                      </div>
                      <span className="text-2xl font-bold text-blue-600">¥{selectedProduct.price}</span>
                    </div>
                  </div>
                )}

                {!selectedProduct && paymentAmount && (
                  <div className="bg-blue-50 rounded-xl p-4 mb-6">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">自定义金额</span>
                      <span className="text-2xl font-bold text-blue-600">¥{paymentAmount}</span>
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">姓名 *</label>
                    <input
                      type="text"
                      value={customerInfo.name}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, name: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition"
                      placeholder="请输入您的姓名"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">手机号码 *</label>
                    <input
                      type="tel"
                      value={customerInfo.phone}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, phone: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition"
                      placeholder="请输入手机号码"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">邮箱（选填）</label>
                    <input
                      type="email"
                      value={customerInfo.email}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, email: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition"
                      placeholder="用于接收服务文件"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">备注（选填）</label>
                    <textarea
                      value={customerInfo.remark}
                      onChange={(e) => setCustomerInfo({ ...customerInfo, remark: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition resize-none"
                      rows={3}
                      placeholder="请描述您的需求或问题"
                    />
                  </div>
                </div>

                <button
                  onClick={createOrder}
                  disabled={!customerInfo.name || !customerInfo.phone || isCreatingOrder}
                  className="w-full mt-6 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-medium hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isCreatingOrder ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      生成支付订单...
                    </>
                  ) : (
                    <>
                      <Alipay className="w-5 h-5" />
                      生成支付宝支付
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          )}

          {/* 步骤3: 扫码支付 */}
          {step === 3 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-xl mx-auto"
            >
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <div className="flex items-center mb-6">
                  <button onClick={() => setStep(2)} className="p-2 hover:bg-gray-100 rounded-lg transition">
                    <ArrowLeft className="w-5 h-5" />
                  </button>
                  <h2 className="text-2xl font-bold ml-4">扫码支付</h2>
                </div>

                <div className="text-center mb-6">
                  <div className="text-sm text-gray-500">应付金额</div>
                  <div className="text-4xl font-bold text-blue-600">¥{orderResult?.amount || paymentAmount}</div>
                </div>

                {/* 二维码区域 */}
                <div className="bg-gray-50 rounded-2xl p-6 mb-6">
                  {qrCodeUrl ? (
                    <div className="flex justify-center">
                      <img src={qrCodeUrl} alt="支付宝收款码" className="w-64 h-64" />
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-64">
                      <QrCode className="w-16 h-16 text-gray-300 mb-4" />
                      <p className="text-gray-500">正在生成收款码...</p>
                    </div>
                  )}
                </div>

                {/* 操作指引 */}
                <div className="space-y-3 mb-6">
                  <div className="flex items-center gap-3 text-gray-600">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-medium">1</div>
                    <span>打开手机支付宝</span>
                  </div>
                  <div className="flex items-center gap-3 text-gray-600">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-medium">2</div>
                    <span>扫一扫上方二维码</span>
                  </div>
                  <div className="flex items-center gap-3 text-gray-600">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-medium">3</div>
                    <span>完成支付后页面自动跳转</span>
                  </div>
                </div>

                {/* 订单号 */}
                <div className="border-t pt-4 text-center text-sm text-gray-500">
                  订单号: {orderResult?.order_id || '---'}
                </div>

                {/* 支付状态 */}
                <div className="mt-4 flex items-center justify-center gap-2 text-cyan-600">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" />
                  <span>等待支付中...</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* 步骤4: 支付成功 */}
          {step === 4 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-xl mx-auto text-center"
            >
              <div className="bg-white rounded-2xl shadow-lg p-12">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="w-10 h-10 text-green-500" />
                </div>
                <h2 className="text-3xl font-bold text-green-600 mb-4">支付成功！</h2>
                <p className="text-gray-600 mb-8">
                  感谢您的信任，我们将在24小时内与您联系
                </p>

                <div className="bg-gray-50 rounded-xl p-6 mb-8 text-left">
                  <h3 className="font-bold mb-4">您的订单信息</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">订单号</span>
                      <span className="font-mono">{orderResult?.order_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">支付金额</span>
                      <span className="font-bold text-blue-600">¥{orderResult?.amount}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">联系人</span>
                      <span>{customerInfo.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">联系电话</span>
                      <span>{customerInfo.phone}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 rounded-xl p-6 mb-8">
                  <h3 className="font-bold mb-4 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-600" />
                    下一步流程
                  </h3>
                  <ul className="text-left text-sm space-y-2 text-gray-600">
                    <li className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      我们的客服将在24小时内联系您
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      服务合同将在24小时内发送至您的邮箱
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      服务启动前会有专人对接需求
                    </li>
                  </ul>
                </div>

                <button
                  onClick={() => {
                    setStep(1)
                    setSelectedProduct(null)
                    setPaymentAmount(null)
                    setCustomerInfo({ name: '', phone: '', email: '', remark: '' })
                    setOrderResult(null)
                  }}
                  className="px-8 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition"
                >
                  返回首页
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* 底部 */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Sparkles className="w-5 h-5" />
            <span className="font-bold">豆包运营代理人</span>
          </div>
          <p className="text-gray-400 text-sm mb-4">
            专业AI代运营服务 | 支付宝官方认证商家
          </p>
          <p className="text-gray-500 text-xs">
            © 2024 豆包运营代理人 版权所有 | 支付宝合作伙伴
          </p>
        </div>
      </footer>
    </div>
  )
}
