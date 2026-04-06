import { useState } from 'react'
import { Plus, Calendar, ChevronLeft, ChevronRight } from 'lucide-react'

const hours = Array.from({ length: 24 }, (_, i) => i)
const platforms = ['全部', '抖音', 'TikTok', '快手']

const scheduledPosts = [
  { id: 1, title: '【AI PC】 RTX 5090 vs RTX 4090 对比', time: '10:00', platform: '抖音', status: 'scheduled' },
  { id: 2, title: '【装机】 AMD Ryzen 9950X3D 首测', time: '14:00', platform: 'TikTok', status: 'scheduled' },
  { id: 3, title: '【科普】 NVMe SSD 选购指南', time: '18:00', platform: '抖音', status: 'draft' },
]

export default function ContentCalendar() {
  const [selectedPlatform, setSelectedPlatform] = useState('全部')
  const [currentWeek, setCurrentWeek] = useState(new Date())

  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">📅 内容排程日历</h1>
          <p className="text-gray-500">管理社交媒体发帖计划</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Platform Filter */}
          <div className="flex gap-2 rounded-lg bg-white p-1">
            {platforms.map((p) => (
              <button
                key={p}
                onClick={() => setSelectedPlatform(p)}
                className={`rounded-md px-4 py-2 text-sm transition ${
                  selectedPlatform === p
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
          <button className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
            <Plus size={18} /> 新建帖子
          </button>
        </div>
      </div>

      {/* Calendar */}
      <div className="rounded-xl bg-white shadow-sm">
        {/* Week Navigation */}
        <div className="flex items-center justify-between border-b px-6 py-4">
          <button onClick={() => setCurrentWeek(new Date(currentWeek.getTime() - 7 * 24 * 60 * 60 * 1000))} className="rounded-lg p-2 hover:bg-gray-100">
            <ChevronLeft size={20} />
          </button>
          <span className="text-lg font-semibold">2026年4月 第1周</span>
          <button onClick={() => setCurrentWeek(new Date(currentWeek.getTime() + 7 * 24 * 60 * 60 * 1000))} className="rounded-lg p-2 hover:bg-gray-100">
            <ChevronRight size={20} />
          </button>
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 border-b">
          {weekDays.map((day) => (
            <div key={day} className="border-r p-3 text-center text-sm font-medium text-gray-600 last:border-r-0">
              {day}
            </div>
          ))}
        </div>

        {/* Time Grid */}
        <div className="max-h-[600px] overflow-y-auto">
          {hours.map((hour) => (
            <div key={hour} className="flex border-b hover:bg-gray-50">
              <div className="w-16 border-r px-2 py-2 text-right text-xs text-gray-400">
                {hour.toString().padStart(2, '0')}:00
              </div>
              <div className="flex-1">
                {/* Placeholder cells for posts */}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Scheduled Posts Sidebar */}
      <div className="mt-6 rounded-xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold">📋 排程中的帖子</h2>
        <div className="space-y-3">
          {scheduledPosts.map((post) => (
            <div key={post.id} className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">{post.title}</p>
                <p className="mt-1 text-sm text-gray-500">
                  <Calendar size={14} className="mr-1 inline" />
                  {post.time} · {post.platform}
                </p>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs ${
                post.status === 'scheduled' ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {post.status === 'scheduled' ? '已排程' : '草稿'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
