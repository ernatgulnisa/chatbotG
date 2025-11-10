import { useState, useEffect } from 'react';
import { Copy, Check, RefreshCw, ExternalLink, Globe, AlertTriangle, CheckCircle } from 'lucide-react';
import api from '../services/api';

export default function WebhookInfo() {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [verifyToken, setVerifyToken] = useState('my_secure_verify_token_12345');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [tunnelRunning, setTunnelRunning] = useState(false);

  const fetchWebhookUrl = async () => {
    setLoading(true);
    try {
      // Get webhook URL from .env via backend
      const response = await api.get('/webhooks/config');
      
      const data = response.data;
      
      if (data.webhook_url) {
        setWebhookUrl(data.webhook_url);
        setVerifyToken(data.verify_token || 'my_secure_verify_token_12345');
        setTunnelRunning(true);
      } else {
        // Fallback to auto-generated URL for local development
        const backendUrl = window.location.origin.includes('localhost')
          ? 'http://localhost:8000'
          : window.location.origin;
        setWebhookUrl(`${backendUrl}/api/v1/webhooks/whatsapp`);
        setVerifyToken(data.verify_token || 'my_secure_token_12345');
        setTunnelRunning(true);
      }
    } catch (error) {
      console.error('Failed to fetch webhook URL:', error);
      setWebhookUrl('');
      setTunnelRunning(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWebhookUrl();
    // Refresh every 30 seconds
    const interval = setInterval(fetchWebhookUrl, 30000);
    return () => clearInterval(interval);
  }, []);

  const copyToClipboard = (text) => {
    if (!text || text.trim() === '') return;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const openMetaDashboard = () => {
    window.open('https://developers.facebook.com/apps', '_blank');
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 rounded-lg p-6 shadow-lg border border-blue-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Globe className="text-blue-600 dark:text-blue-400" size={24} />
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            Webhook Configuration
          </h3>
          {!loading && (
            tunnelRunning ? (
              <CheckCircle className="text-green-500" size={20} title="Туннель запущен" />
            ) : (
              <AlertTriangle className="text-red-500" size={20} title="Туннель не запущен" />
            )
          )}
        </div>
        <button
          onClick={fetchWebhookUrl}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 text-sm bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Обновить
        </button>
      </div>

      {/* Tunnel Not Running Warning */}
      {!loading && !tunnelRunning && (
        <div className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" size={24} />
            <div className="flex-1">
              <h4 className="font-bold text-yellow-800 dark:text-yellow-300 mb-2">
                ℹ️ Не удалось получить Webhook URL из переменных окружения
              </h4>
              <p className="text-sm text-yellow-700 dark:text-yellow-400 mb-2">
                Используется автоматически сгенерированный URL. Если вы деплоите на продакшен, убедитесь что в .env файле установлена переменная WEBHOOK_URL.
              </p>
              <p className="text-xs text-yellow-600 dark:text-yellow-400">
                Для локальной разработки используется: http://localhost:8000/api/v1/webhooks/whatsapp
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Webhook URL */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Webhook URL для Meta Dashboard
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={webhookUrl || 'Загрузка...'}
            readOnly
            className={`flex-1 px-4 py-3 border rounded-lg font-mono text-sm ${
              tunnelRunning
                ? 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white'
                : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700 text-yellow-700 dark:text-yellow-400'
            }`}
          />
          <button
            onClick={() => copyToClipboard(webhookUrl)}
            disabled={!webhookUrl}
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
            title={webhookUrl ? "Копировать URL" : "URL не загружен"}
          >
            {copied ? <Check size={20} /> : <Copy size={20} />}
          </button>
        </div>
        {tunnelRunning && webhookUrl && (
          <p className="text-xs text-green-600 dark:text-green-400 mt-2 flex items-center gap-1">
            <CheckCircle size={14} />
            Webhook URL готов к использованию
          </p>
        )}
      </div>

      {/* Verify Token */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Verify Token
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={verifyToken}
            readOnly
            className="flex-1 px-4 py-3 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg font-mono text-sm text-gray-900 dark:text-white"
          />
          <button
            onClick={() => copyToClipboard(verifyToken)}
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            title="Копировать токен"
          >
            <Copy size={20} />
          </button>
        </div>
      </div>

      {/* Quick Actions */}
      {tunnelRunning && (
        <div className="flex flex-wrap gap-2 mt-6">
          <button
            onClick={openMetaDashboard}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            <ExternalLink size={16} />
            Meta Dashboard
          </button>
        </div>
      )}

      {/* Instructions - Only show when tunnel is running */}
      {tunnelRunning && (
        <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg">
          <h4 className="font-semibold text-yellow-800 dark:text-yellow-300 mb-2">
            📝 Инструкция по настройке
          </h4>
          <ol className="text-sm text-yellow-700 dark:text-yellow-400 space-y-1 list-decimal list-inside">
            <li>Скопируйте <strong>Webhook URL</strong> выше</li>
            <li>Откройте Meta Dashboard (кнопка выше)</li>
            <li>WhatsApp → Configuration → Webhook</li>
            <li>Нажмите "Edit"</li>
            <li>Вставьте Webhook URL и Verify Token</li>
            <li>Нажмите "Verify and Save"</li>
            <li>Подпишитесь на события: <code>messages</code> и <code>message_status</code></li>
          </ol>
        </div>
      )}

      {/* Note about webhook URL */}
      <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
        <p className="text-sm text-blue-700 dark:text-blue-400">
          <strong>💡 Продакшен:</strong> Если вы деплоите на Render, Railway или другой платформе, убедитесь что в Environment Variables установлена переменная <code>WEBHOOK_URL</code> с вашим доменом.
        </p>
        <p className="text-xs text-blue-600 dark:text-blue-500 mt-2">
          Пример: <code>WEBHOOK_URL=https://your-app.onrender.com/api/v1/webhooks/whatsapp</code>
        </p>
      </div>
    </div>
  );
}
