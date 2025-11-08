import { Plus, Bot, MoreVertical, Play, Pause, Edit } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Bots() {
  const bots = [
    { id: 1, name: 'Booking Assistant', status: 'active', conversations: 127, messages: 1542 },
    { id: 2, name: 'FAQ Bot', status: 'active', conversations: 84, messages: 912 },
    { id: 3, name: 'Sales Bot', status: 'paused', conversations: 56, messages: 673 },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Bots</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Create and manage your WhatsApp bots
          </p>
        </div>
        <Link to="/bots/new/builder" className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Create Bot
        </Link>
      </div>

      {/* Bots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {bots.map((bot) => (
          <div key={bot.id} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">{bot.name}</h3>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    bot.status === 'active' 
                      ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                  }`}>
                    {bot.status === 'active' ? 'Active' : 'Paused'}
                  </span>
                </div>
              </div>
              <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
                <MoreVertical className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Conversations</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">{bot.conversations}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Messages</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">{bot.messages}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link to={`/bots/${bot.id}/builder`} className="flex-1 btn-secondary text-center">
                <Edit className="w-4 h-4 inline mr-2" />
                Edit
              </Link>
              <button className="btn-secondary">
                {bot.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
