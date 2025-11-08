import { Save, Play } from 'lucide-react'

export default function BotBuilder() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Bot Builder</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Create conversation flows with drag-and-drop interface
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="btn-secondary flex items-center gap-2">
            <Play className="w-5 h-5" />
            Test Bot
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Save className="w-5 h-5" />
            Save
          </button>
        </div>
      </div>

      {/* Bot Builder Canvas */}
      <div className="card h-[calc(100vh-250px)]">
        <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
          <div className="text-center">
            <p className="text-lg mb-2">React Flow Bot Builder</p>
            <p className="text-sm">Will be implemented with React Flow library</p>
          </div>
        </div>
      </div>
    </div>
  )
}
