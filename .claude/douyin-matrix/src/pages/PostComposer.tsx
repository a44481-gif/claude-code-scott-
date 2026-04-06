import { useState } from 'react'
import { Send, Save, Eye, Image as ImageIcon, Hash, Video } from 'lucide-react'

const templates = [
  { id: 1, name: '产品评测模板', title: '【测评】{product} 深度体验...', caption: '今天来测评一下{personality}...' },
  { id: 2, name: '装机教程模板', title: '【装机】{cpu}+{gpu} 性能实测', caption: '应粉丝要求安排上了...' },
  { id: 3, name: '科普知识模板', title: '【科普】{topic} 一分钟看懂', caption: '关注我，每天涨知识...' },
  { id: 4, name: '新品速递模板', title: '【新品】{brand} 发布 {product}', caption: '刚发布就拿到了...' },
]

const platforms = ['抖音', 'TikTok', '快手']
const categories = ['AI PC', '装机', '评测', '科普', '新品']

export default function PostComposer() {
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null)
  const [platform, setPlatform] = useState('抖音')
  const [title, setTitle] = useState('')
  const [caption, setCaption] = useState('')
  const [tags, setTags] = useState('')
  const [scheduledTime, setScheduledTime] = useState('')

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-5xl">
        <h1 className="mb-6 text-2xl font-bold text-gray-800">✍️ 帖子编辑器</h1>

        <div className="grid grid-cols-3 gap-6">
          {/* Template Selector */}
          <div className="rounded-xl bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold">📋 内容模板</h2>
            <div className="space-y-2">
              {templates.map((t) => (
                <button
                  key={t.id}
                  onClick={() => {
                    setSelectedTemplate(t.id)
                    setTitle(t.title.replace('{product}', 'RTX 5090').replace('{cpu}', 'Ryzen 9').replace('{gpu}', 'RTX 5090'))
                    setCaption(t.caption.replace('{personality}', '超强的'))
                  }}
                  className={`w-full rounded-lg p-3 text-left text-sm transition ${
                    selectedTemplate === t.id
                      ? 'bg-blue-100 border-2 border-blue-500'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <p className="font-medium">{t.name}</p>
                  <p className="mt-1 text-xs text-gray-500 truncate">{t.title}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Editor */}
          <div className="col-span-2 space-y-6">
            {/* Platform */}
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">平台选择</h2>
              <div className="flex gap-3">
                {platforms.map((p) => (
                  <button
                    key={p}
                    onClick={() => setPlatform(p)}
                    className={`rounded-lg px-6 py-3 font-medium transition ${
                      platform === p
                        ? 'bg-pink-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Content */}
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">内容编辑</h2>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">标题</label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="输入视频标题..."
                    className="w-full rounded-lg border px-4 py-3 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">文案</label>
                  <textarea
                    value={caption}
                    onChange={(e) => setCaption(e.target.value)}
                    placeholder="输入视频描述..."
                    rows={5}
                    className="w-full rounded-lg border px-4 py-3 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="mb-2 flex items-center gap-2 text-sm font-medium text-gray-700">
                    <Hash size={16} /> 话题标签
                  </label>
                  <input
                    type="text"
                    value={tags}
                    onChange={(e) => setTags(e.target.value)}
                    placeholder="#AI #PC #装机 #显卡..."
                    className="w-full rounded-lg border px-4 py-3 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">定时发布</label>
                  <input
                    type="datetime-local"
                    value={scheduledTime}
                    onChange={(e) => setScheduledTime(e.target.value)}
                    className="rounded-lg border px-4 py-3 focus:border-blue-500 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* Media */}
            <div className="rounded-xl bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold">媒体素材</h2>
              <div className="flex gap-4">
                <button className="flex flex-1 items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-300 py-8 text-gray-500 hover:border-blue-500 hover:text-blue-500">
                  <Video size={24} />
                  <span>上传视频</span>
                </button>
                <button className="flex flex-1 items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-300 py-8 text-gray-500 hover:border-blue-500 hover:text-blue-500">
                  <ImageIcon size={24} />
                  <span>上传封面</span>
                </button>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3">
              <button className="flex items-center gap-2 rounded-lg bg-gray-100 px-6 py-3 text-gray-700 hover:bg-gray-200">
                <Eye size={18} /> 预览
              </button>
              <button className="flex items-center gap-2 rounded-lg bg-gray-100 px-6 py-3 text-gray-700 hover:bg-gray-200">
                <Save size={18} /> 保存草稿
              </button>
              <button className="flex items-center gap-2 rounded-lg bg-pink-600 px-6 py-3 text-white hover:bg-pink-700">
                <Send size={18} /> {scheduledTime ? '确认排程' : '立即发布'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
