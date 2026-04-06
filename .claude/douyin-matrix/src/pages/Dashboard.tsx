import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts'

const mockMetrics = [
  { date: '04-01', views: 12500, likes: 820, comments: 145 },
  { date: '04-02', views: 15800, likes: 1100, comments: 203 },
  { date: '04-03', views: 11200, likes: 760, comments: 98 },
  { date: '04-04', views: 18900, likes: 1350, comments: 267 },
  { date: '04-05', views: 22300, likes: 1680, comments: 312 },
  { date: '04-06', views: 19700, likes: 1420, comments: 245 },
]

const pieData = [
  { name: '抖音', value: 55, color: '#fe2c55' },
  { name: 'TikTok', value: 30, color: '#000' },
  { name: '快手', value: 15, color: '#ff4906' },
]

export default function Dashboard() {
  const [timeRange, setTimeRange] = useState('7d')

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">社交媒体矩阵 Dashboard</h1>
          <p className="text-gray-500">AI Business Intelligence Platform</p>
        </div>
        <div className="flex gap-3">
          <select
            className="rounded-lg border px-4 py-2"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="7d">近7天</option>
            <option value="30d">近30天</option>
            <option value="90d">近90天</option>
          </select>
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
            刷新数据
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="mb-6 grid grid-cols-1 gap-6 md:grid-cols-4">
        {[
          { label: '总浏览量', value: '98.5K', change: '+12.3%', up: true },
          { label: '总点赞', value: '7.1K', change: '+8.7%', up: true },
          { label: '总评论', value: '1.3K', change: '+15.2%', up: true },
          { label: '平均互动率', value: '8.2%', change: '-2.1%', up: false },
        ].map((kpi, i) => (
          <div key={i} className="rounded-xl bg-white p-6 shadow-sm">
            <p className="text-sm text-gray-500">{kpi.label}</p>
            <p className="mt-2 text-3xl font-bold">{kpi.value}</p>
            <p className={`mt-1 text-sm ${kpi.up ? 'text-green-600' : 'text-red-600'}`}>
              {kpi.change} vs 上周期
            </p>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Views Trend */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold">📈 浏览量趋势</h2>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={mockMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="views" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.1} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Platform Distribution */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold">📊 平台分布</h2>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="50%" height={200}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label>
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1">
              {pieData.map((item, i) => (
                <div key={i} className="mb-3 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span>{item.name}</span>
                  </div>
                  <span className="font-semibold">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Engagement Chart */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold">💬 互动数据 (点赞/评论)</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={mockMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="likes" stroke="#f97316" strokeWidth={2} name="点赞" />
              <Line type="monotone" dataKey="comments" stroke="#22c55e" strokeWidth={2} name="评论" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Posts */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold">📝 最新帖子</h2>
          <div className="space-y-3">
            {[
              { title: '【AI PC】 RTX 5090 深度评测...', platform: '抖音', views: '23.5K', status: '已发布' },
              { title: '【装机】 AMD Ryzen 9 9950X3D...', platform: '抖音', views: '18.2K', status: '已发布' },
              { title: '【科普】 DDR5 vs DDR4 性能差距', platform: 'TikTok', views: '12.8K', status: '已发布' },
              { title: '【新品】 MSI RTX 5080 首发...', platform: '抖音', views: '8.5K', status: '草稿' },
            ].map((post, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg bg-gray-50 p-3">
                <div>
                  <p className="font-medium">{post.title}</p>
                  <p className="text-sm text-gray-500">{post.platform} · {post.views}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs ${
                  post.status === '已发布' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {post.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
