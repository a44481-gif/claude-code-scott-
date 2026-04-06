import { useState } from 'react'
import {
  Users,
  Video,
  BarChart3,
  MessageSquare,
  Zap,
  TrendingUp,
  Eye,
  Heart,
  Share2,
  UserPlus,
  Clock,
  CheckCircle,
  AlertCircle,
  DollarSign,
  Target,
  Megaphone,
  Settings,
  Bell,
  Search,
  Plus,
  MoreVertical,
  ChevronRight,
  Play,
  Star,
  TrendingDown,
  Instagram,
  Youtube,
  Twitter
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts'

// 模拟数据
const accountData = [
  { id: 1, name: '美妆种草酱', platform: 'douyin', followers: 125000, views: 890000, likes: 45000, comments: 3200, leads: 156, status: 'active' },
  { id: 2, name: '数码科技控', platform: 'douyin', followers: 89000, views: 560000, likes: 28000, comments: 1800, leads: 98, status: 'active' },
  { id: 3, name: '美食探店王', platform: 'douyin', followers: 67000, views: 420000, likes: 21000, comments: 1400, leads: 67, status: 'active' },
  { id: 4, name: '穿搭日记', platform: 'douyin', followers: 45000, views: 320000, likes: 16000, comments: 980, leads: 45, status: 'inactive' },
  { id: 5, name: '家居生活家', platform: 'douyin', followers: 78000, views: 480000, likes: 24000, comments: 1600, leads: 89, status: 'active' },
]

const dailyStats = [
  { date: '03-26', views: 420000, leads: 89, engagement: 4.2 },
  { date: '03-27', views: 480000, leads: 102, engagement: 4.5 },
  { date: '03-28', views: 520000, leads: 118, engagement: 4.8 },
  { date: '03-29', views: 460000, leads: 95, engagement: 4.3 },
  { date: '03-30', views: 580000, leads: 134, engagement: 5.1 },
  { date: '03-31', views: 620000, leads: 145, engagement: 5.3 },
  { date: '04-01', views: 680000, leads: 162, engagement: 5.6 },
]

const leadFunnel = [
  { name: '曝光量', value: 680000, color: '#FF4757' },
  { name: '互动数', value: 34000, color: '#5352ED' },
  { name: '私域获客', value: 162, color: '#2ED573' },
]

const platformDistribution = [
  { name: '抖音', value: 65, color: '#FF4757' },
  { name: '小红书', value: 20, color: '#FF6B81' },
  { name: '快手', value: 10, color: '#3742FA' },
  { name: '其他', value: 5, color: '#CED6E0' },
]

const topContent = [
  { id: 1, title: '这款面霜用了皮肤真的变好了！', views: 125000, likes: 8900, comments: 456, shares: 234, leads: 45, date: '04-01' },
  { id: 2, title: 'iPhone 15 真实体验测评', views: 98000, likes: 7200, comments: 389, shares: 178, leads: 38, date: '03-31' },
  { id: 3, title: '探店｜这家火锅店太绝了', views: 86000, likes: 6100, comments: 312, shares: 156, leads: 32, date: '03-30' },
  { id: 4, title: '春季穿搭分享｜学生党也能轻松get', views: 72000, likes: 5400, comments: 278, shares: 123, leads: 28, date: '03-29' },
  { id: 5, title: '智能家居好物推荐', views: 65000, likes: 4800, comments: 234, shares: 98, leads: 24, date: '03-28' },
]

const recentLeads = [
  { id: 1, name: '李女士', phone: '138****2345', source: '美妆种草酱', interest: '护肤品套装', time: '10分钟前', status: 'new' },
  { id: 2, name: '王先生', phone: '139****8762', source: '数码科技控', interest: '手机以旧换新', time: '25分钟前', status: 'contacted' },
  { id: 3, name: '张女士', phone: '136****4532', source: '美食探店王', interest: '火锅底料', time: '1小时前', status: 'new' },
  { id: 4, name: '刘先生', phone: '135****9876', source: '家居生活家', interest: '智能音箱', time: '2小时前', status: 'following' },
  { id: 5, name: '陈女士', phone: '137****2341', source: '穿搭日记', interest: '春季新款', time: '3小时前', status: 'new' },
]

const automationRules = [
  { id: 1, name: '新粉丝自动回复', trigger: '新关注', action: '发送欢迎语+优惠券', status: 'active', executions: 1256 },
  { id: 2, name: '关键词自动回复', trigger: '评论含"价格"', action: '回复产品链接', status: 'active', executions: 892 },
  { id: 3, name: '定时发布任务', trigger: '每日 20:00', action: '发布预存视频', status: 'active', executions: 56 },
  { id: 4, name: '爆款自动投放', trigger: '点赞>5000', action: '开启DOU+投放', status: 'paused', executions: 23 },
]

const navItems = [
  { id: 'dashboard', label: '工作台', icon: BarChart3 },
  { id: 'accounts', label: '账号管理', icon: Users },
  { id: 'content', label: '内容中心', icon: Video },
  { id: 'leads', label: '线索管理', icon: Target },
  { id: 'automation', label: '自动化', icon: Zap },
]

type TabType = 'dashboard' | 'accounts' | 'content' | 'leads' | 'automation'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard')
  const [searchQuery, setSearchQuery] = useState('')

  const totalFollowers = accountData.reduce((sum, acc) => sum + acc.followers, 0)
  const totalViews = accountData.reduce((sum, acc) => sum + acc.views, 0)
  const totalLeads = accountData.reduce((sum, acc) => sum + acc.leads, 0)
  const avgEngagement = (dailyStats.reduce((sum, d) => sum + d.engagement, 0) / dailyStats.length).toFixed(1)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
                <Video className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">抖音矩阵获客</h1>
                <p className="text-xs text-gray-500">企业级解决方案</p>
              </div>
            </div>

            <div className="flex-1 max-w-md mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="搜索账号、内容、线索..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-100 border-0 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-pink-500 transition-all"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="relative p-2 rounded-xl hover:bg-gray-100 transition-colors">
                <Bell className="w-5 h-5 text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>
              <button className="p-2 rounded-xl hover:bg-gray-100 transition-colors">
                <Settings className="w-5 h-5 text-gray-600" />
              </button>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center text-white font-bold">
                A
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 侧边栏 + 主内容 */}
        <div className="flex gap-6">
          {/* 侧边导航 */}
          <nav className="w-56 shrink-0">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-3 sticky top-24">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id as TabType)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all ${
                    activeTab === item.id
                      ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-lg shadow-pink-500/25'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}

              <div className="mt-6 pt-4 border-t border-gray-100">
                <div className="px-4 py-2">
                  <p className="text-xs text-gray-400 uppercase tracking-wider mb-2">今日概览</p>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">新增线索</span>
                      <span className="font-semibold text-green-500">+162</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">待跟进</span>
                      <span className="font-semibold text-orange-500">23</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">转化率</span>
                      <span className="font-semibold text-pink-500">5.6%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </nav>

          {/* 主内容区 */}
          <main className="flex-1 min-w-0">
            {activeTab === 'dashboard' && (
              <div className="space-y-6">
                {/* 核心指标卡片 */}
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-12 h-12 rounded-xl bg-pink-100 flex items-center justify-center">
                        <Users className="w-6 h-6 text-pink-500" />
                      </div>
                      <span className="text-xs font-medium text-green-500 bg-green-50 px-2 py-1 rounded-full">+12.5%</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-1">总粉丝数</p>
                    <p className="text-2xl font-bold text-gray-900">{(totalFollowers / 10000).toFixed(1)}万</p>
                  </div>

                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
                        <Eye className="w-6 h-6 text-purple-500" />
                      </div>
                      <span className="text-xs font-medium text-green-500 bg-green-50 px-2 py-1 rounded-full">+18.2%</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-1">总曝光量</p>
                    <p className="text-2xl font-bold text-gray-900">{(totalViews / 10000).toFixed(1)}万</p>
                  </div>

                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                        <Target className="w-6 h-6 text-green-500" />
                      </div>
                      <span className="text-xs font-medium text-green-500 bg-green-50 px-2 py-1 rounded-full">+24.8%</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-1">线索总数</p>
                    <p className="text-2xl font-bold text-gray-900">{totalLeads}</p>
                  </div>

                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-orange-500" />
                      </div>
                      <span className="text-xs font-medium text-green-500 bg-green-50 px-2 py-1 rounded-full">+0.5%</span>
                    </div>
                    <p className="text-sm text-gray-500 mb-1">平均互动率</p>
                    <p className="text-2xl font-bold text-gray-900">{avgEngagement}%</p>
                  </div>
                </div>

                {/* 图表区域 */}
                <div className="grid grid-cols-3 gap-6">
                  {/* 趋势图 */}
                  <div className="col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">数据趋势</h3>
                        <p className="text-sm text-gray-500">近7天核心指标走势</p>
                      </div>
                      <div className="flex gap-2">
                        <button className="px-3 py-1.5 text-xs font-medium bg-pink-50 text-pink-500 rounded-lg">曝光量</button>
                        <button className="px-3 py-1.5 text-xs font-medium bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors">线索数</button>
                      </div>
                    </div>
                    <ResponsiveContainer width="100%" height={280}>
                      <AreaChart data={dailyStats}>
                        <defs>
                          <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#FF4757" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#FF4757" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                        <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: '#94A3B8', fontSize: 12 }} />
                        <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94A3B8', fontSize: 12 }} tickFormatter={(v) => `${(v/1000).toFixed(0)}k`} />
                        <Tooltip
                          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
                          formatter={(value: number) => [`${value.toLocaleString()}`, '曝光量']}
                        />
                        <Area type="monotone" dataKey="views" stroke="#FF4757" strokeWidth={2} fill="url(#colorViews)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  {/* 漏斗图 */}
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-6">获客漏斗</h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={leadFunnel}
                          cx="50%"
                          cy="50%"
                          innerRadius={50}
                          outerRadius={80}
                          paddingAngle={2}
                          dataKey="value"
                        >
                          {leadFunnel.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
                          formatter={(value: number) => [value.toLocaleString(), '']}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="space-y-2 mt-4">
                      {leadFunnel.map((item) => (
                        <div key={item.name} className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                            <span className="text-gray-600">{item.name}</span>
                          </div>
                          <span className="font-semibold text-gray-900">{item.value.toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 底部内容 */}
                <div className="grid grid-cols-2 gap-6">
                  {/* 热门内容 */}
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-gray-900">热门内容</h3>
                      <button className="text-sm text-pink-500 hover:text-pink-600 font-medium flex items-center gap-1">
                        查看全部 <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="space-y-4">
                      {topContent.slice(0, 4).map((content) => (
                        <div key={content.id} className="flex gap-4 p-3 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer">
                          <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center shrink-0">
                            <Play className="w-8 h-8 text-gray-400" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 mb-1 truncate">{content.title}</p>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span className="flex items-center gap-1"><Eye className="w-3 h-3" />{(content.views / 1000).toFixed(1)}k</span>
                              <span className="flex items-center gap-1"><Heart className="w-3 h-3" />{(content.likes / 1000).toFixed(1)}k</span>
                              <span className="flex items-center gap-1"><Share2 className="w-3 h-3" />{content.shares}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="inline-block px-2 py-1 text-xs font-medium text-green-600 bg-green-50 rounded-lg">+{content.leads}线索</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 近期线索 */}
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-gray-900">近期线索</h3>
                      <button className="text-sm text-pink-500 hover:text-pink-600 font-medium flex items-center gap-1">
                        查看全部 <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="space-y-3">
                      {recentLeads.map((lead) => (
                        <div key={lead.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 transition-colors">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center text-white font-medium">
                              {lead.name.charAt(0)}
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900">{lead.name}</p>
                              <p className="text-xs text-gray-500">{lead.source} · {lead.interest}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className={`inline-block px-2 py-1 text-xs font-medium rounded-lg ${
                              lead.status === 'new' ? 'text-blue-600 bg-blue-50' :
                              lead.status === 'contacted' ? 'text-orange-600 bg-orange-50' :
                              'text-green-600 bg-green-50'
                            }`}>
                              {lead.status === 'new' ? '新线索' : lead.status === 'contacted' ? '已联系' : '跟进中'}
                            </span>
                            <p className="text-xs text-gray-400 mt-1">{lead.time}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'accounts' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">账号管理</h2>
                    <p className="text-gray-500 mt-1">管理所有矩阵账号，统一运营</p>
                  </div>
                  <button className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl font-medium shadow-lg shadow-pink-500/25 hover:shadow-pink-500/40 transition-all">
                    <Plus className="w-5 h-5" />
                    添加账号
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {accountData.map((account) => (
                    <div key={account.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-400 to-rose-500 flex items-center justify-center text-white text-xl font-bold">
                            {account.name.charAt(0)}
                          </div>
                          <div>
                            <h3 className="font-bold text-gray-900">{account.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                                account.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
                              }`}>
                                {account.status === 'active' ? '运营中' : '已停用'}
                              </span>
                              <span className="text-xs text-gray-400 flex items-center gap-1">
                                <Video className="w-3 h-3" /> 抖音
                              </span>
                            </div>
                          </div>
                        </div>
                        <button className="p-2 rounded-xl hover:bg-gray-100 transition-colors">
                          <MoreVertical className="w-5 h-5 text-gray-400" />
                        </button>
                      </div>

                      <div className="grid grid-cols-4 gap-3 mb-4">
                        <div className="text-center p-2 bg-gray-50 rounded-xl">
                          <p className="text-lg font-bold text-gray-900">{(account.followers / 10000).toFixed(1)}万</p>
                          <p className="text-xs text-gray-500">粉丝</p>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded-xl">
                          <p className="text-lg font-bold text-gray-900">{(account.views / 10000).toFixed(1)}万</p>
                          <p className="text-xs text-gray-500">曝光</p>
                        </div>
                        <div className="text-center p-2 bg-gray-50 rounded-xl">
                          <p className="text-lg font-bold text-gray-900">{(account.likes / 1000).toFixed(1)}k</p>
                          <p className="text-xs text-gray-500">获赞</p>
                        </div>
                        <div className="text-center p-2 bg-pink-50 rounded-xl">
                          <p className="text-lg font-bold text-pink-500">{account.leads}</p>
                          <p className="text-xs text-pink-500">线索</p>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <button className="flex-1 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors">
                          编辑
                        </button>
                        <button className="flex-1 py-2 text-sm font-medium text-white bg-gradient-to-r from-pink-500 to-rose-500 rounded-xl hover:opacity-90 transition-opacity">
                          数据
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'content' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">内容中心</h2>
                    <p className="text-gray-500 mt-1">管理所有视频内容，分析表现</p>
                  </div>
                  <button className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl font-medium shadow-lg shadow-pink-500/25 hover:shadow-pink-500/40 transition-all">
                    <Plus className="w-5 h-5" />
                    发布内容
                  </button>
                </div>

                {/* 内容筛选 */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                  <div className="flex items-center gap-4">
                    <div className="flex gap-2">
                      <button className="px-4 py-2 text-sm font-medium bg-pink-500 text-white rounded-xl">全部</button>
                      <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">已发布</button>
                      <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">草稿</button>
                      <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">定时发布</button>
                    </div>
                    <div className="flex-1" />
                    <select className="px-4 py-2 text-sm bg-gray-100 border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500">
                      <option>按时间排序</option>
                      <option>按曝光排序</option>
                      <option>按线索排序</option>
                    </select>
                  </div>
                </div>

                {/* 内容列表 */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">内容</th>
                        <th className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">账号</th>
                        <th className="text-right px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">曝光</th>
                        <th className="text-right px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">获赞</th>
                        <th className="text-right px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">评论</th>
                        <th className="text-right px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">线索</th>
                        <th className="text-right px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {topContent.map((content) => (
                        <tr key={content.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                                <Play className="w-6 h-6 text-gray-400" />
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900 max-w-xs truncate">{content.title}</p>
                                <p className="text-xs text-gray-500 mt-1">{content.date}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">美妆种草酱</td>
                          <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">{(content.views / 1000).toFixed(1)}k</td>
                          <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">{(content.likes / 1000).toFixed(1)}k</td>
                          <td className="px-6 py-4 text-right text-sm font-medium text-gray-900">{content.comments}</td>
                          <td className="px-6 py-4 text-right">
                            <span className="inline-block px-2 py-1 text-xs font-medium text-green-600 bg-green-50 rounded-lg">+{content.leads}</span>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button className="p-2 rounded-xl hover:bg-gray-100 transition-colors">
                              <MoreVertical className="w-4 h-4 text-gray-400" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'leads' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">线索管理</h2>
                    <p className="text-gray-500 mt-1">统一管理所有客户线索，提高转化率</p>
                  </div>
                  <div className="flex gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                      <Share2 className="w-4 h-4" />
                      导出
                    </button>
                    <button className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl font-medium shadow-lg shadow-pink-500/25 hover:shadow-pink-500/40 transition-all">
                      <Plus className="w-5 h-5" />
                      添加线索
                    </button>
                  </div>
                </div>

                {/* 线索统计 */}
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                        <UserPlus className="w-6 h-6 text-blue-500" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">新增线索</p>
                        <p className="text-2xl font-bold text-gray-900">162</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
                        <Clock className="w-6 h-6 text-orange-500" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">待跟进</p>
                        <p className="text-2xl font-bold text-gray-900">23</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                        <CheckCircle className="w-6 h-6 text-green-500" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">已转化</p>
                        <p className="text-2xl font-bold text-gray-900">45</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
                        <DollarSign className="w-6 h-6 text-purple-500" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">转化率</p>
                        <p className="text-2xl font-bold text-gray-900">27.8%</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 线索列表 */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                  <div className="p-4 border-b border-gray-100 flex items-center gap-4">
                    <div className="flex gap-2">
                      <button className="px-4 py-2 text-sm font-medium bg-pink-500 text-white rounded-xl">全部</button>
                      <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">新线索</button>
                      <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">跟进中</button>
                      <button className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-xl transition-colors">已转化</button>
                    </div>
                    <div className="flex-1" />
                    <select className="px-4 py-2 text-sm bg-gray-100 border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500">
                      <option>按时间排序</option>
                      <option>按来源排序</option>
                    </select>
                  </div>

                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">客户信息</th>
                        <th className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">来源</th>
                        <th className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">意向</th>
                        <th className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">状态</th>
                        <th className="text-left px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">时间</th>
                        <th className="text-right px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">操作</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {recentLeads.map((lead) => (
                        <tr key={lead.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center text-white font-medium">
                                {lead.name.charAt(0)}
                              </div>
                              <div>
                                <p className="text-sm font-medium text-gray-900">{lead.name}</p>
                                <p className="text-xs text-gray-500">{lead.phone}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">{lead.source}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{lead.interest}</td>
                          <td className="px-6 py-4">
                            <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                              lead.status === 'new' ? 'bg-blue-100 text-blue-600' :
                              lead.status === 'contacted' ? 'bg-orange-100 text-orange-600' :
                              'bg-green-100 text-green-600'
                            }`}>
                              {lead.status === 'new' ? '新线索' : lead.status === 'contacted' ? '已联系' : '跟进中'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">{lead.time}</td>
                          <td className="px-6 py-4">
                            <div className="flex justify-end gap-2">
                              <button className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                                跟进
                              </button>
                              <button className="px-3 py-1.5 text-xs font-medium text-white bg-pink-500 rounded-lg hover:bg-pink-600 transition-colors">
                                转化
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'automation' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">自动化规则</h2>
                    <p className="text-gray-500 mt-1">配置自动化流程，提高运营效率</p>
                  </div>
                  <button className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl font-medium shadow-lg shadow-pink-500/25 hover:shadow-pink-500/40 transition-all">
                    <Plus className="w-5 h-5" />
                    创建规则
                  </button>
                </div>

                {/* 自动化统计 */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900">今日执行</h3>
                      <span className="text-xs text-green-500 font-medium bg-green-50 px-2 py-1 rounded-full">+156</span>
                    </div>
                    <p className="text-3xl font-bold text-gray-900">2,267</p>
                    <p className="text-sm text-gray-500 mt-1">次自动化操作</p>
                  </div>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900">节省时间</h3>
                      <span className="text-xs text-blue-500 font-medium bg-blue-50 px-2 py-1 rounded-full">+8h</span>
                    </div>
                    <p className="text-3xl font-bold text-gray-900">32.5h</p>
                    <p className="text-sm text-gray-500 mt-1">本周节省人力</p>
                  </div>
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900">线索转化</h3>
                      <span className="text-xs text-pink-500 font-medium bg-pink-50 px-2 py-1 rounded-full">+12%</span>
                    </div>
                    <p className="text-3xl font-bold text-gray-900">45.6%</p>
                    <p className="text-sm text-gray-500 mt-1">自动化线索转化率</p>
                  </div>
                </div>

                {/* 规则列表 */}
                <div className="space-y-4">
                  {automationRules.map((rule) => (
                    <div key={rule.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                            rule.status === 'active' ? 'bg-green-100' : 'bg-gray-100'
                          }`}>
                            <Zap className={`w-6 h-6 ${rule.status === 'active' ? 'text-green-500' : 'text-gray-400'}`} />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 mb-1">{rule.name}</h3>
                            <div className="flex items-center gap-4 text-sm text-gray-500">
                              <span className="flex items-center gap-1">
                                <AlertCircle className="w-4 h-4" />
                                触发: {rule.trigger}
                              </span>
                              <span className="flex items-center gap-1">
                                <ChevronRight className="w-4 h-4" />
                                {rule.action}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">{rule.executions.toLocaleString()}</p>
                            <p className="text-xs text-gray-500">执行次数</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                              rule.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
                            }`}>
                              {rule.status === 'active' ? '运行中' : '已暂停'}
                            </span>
                            <button className="p-2 rounded-xl hover:bg-gray-100 transition-colors">
                              <MoreVertical className="w-5 h-5 text-gray-400" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* 快捷模板 */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">快捷模板</h3>
                  <div className="grid grid-cols-4 gap-4">
                    <button className="p-4 border border-gray-200 rounded-xl hover:border-pink-300 hover:bg-pink-50 transition-all text-center group">
                      <div className="w-12 h-12 rounded-xl bg-pink-100 flex items-center justify-center mx-auto mb-3 group-hover:bg-pink-200 transition-colors">
                        <MessageSquare className="w-6 h-6 text-pink-500" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">自动回复</p>
                      <p className="text-xs text-gray-500 mt-1">关键词触发</p>
                    </button>
                    <button className="p-4 border border-gray-200 rounded-xl hover:border-pink-300 hover:bg-pink-50 transition-all text-center group">
                      <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center mx-auto mb-3 group-hover:bg-purple-200 transition-colors">
                        <Clock className="w-6 h-6 text-purple-500" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">定时发布</p>
                      <p className="text-xs text-gray-500 mt-1">自动定时任务</p>
                    </button>
                    <button className="p-4 border border-gray-200 rounded-xl hover:border-pink-300 hover:bg-pink-50 transition-all text-center group">
                      <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center mx-auto mb-3 group-hover:bg-green-200 transition-colors">
                        <UserPlus className="w-6 h-6 text-green-500" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">新粉欢迎</p>
                      <p className="text-xs text-gray-500 mt-1">自动发送欢迎</p>
                    </button>
                    <button className="p-4 border border-gray-200 rounded-xl hover:border-pink-300 hover:bg-pink-50 transition-all text-center group">
                      <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center mx-auto mb-3 group-hover:bg-orange-200 transition-colors">
                        <TrendingUp className="w-6 h-6 text-orange-500" />
                      </div>
                      <p className="text-sm font-medium text-gray-900">爆款投放</p>
                      <p className="text-xs text-gray-500 mt-1">DOU+自动投放</p>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}

export default App