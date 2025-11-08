import { useState, useEffect } from 'react';
import { Copy, Check, RefreshCw, ExternalLink, Globe, AlertTriangle, CheckCircle } from 'lucide-react';

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
      const response = await fetch('http://localhost:8000/api/v1/webhooks/config');
      
      if (!response.ok) {
        throw new Error('Backend not responding');
      }
      
      const data = await response.json();
      
      if (data.webhook_url) {
        setWebhookUrl(data.webhook_url);
        setVerifyToken(data.verify_token || 'my_secure_verify_token_12345');
        setTunnelRunning(true);
      } else {
        setWebhookUrl('');
        setTunnelRunning(false);
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
        <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border-2 border-red-300 dark:border-red-700 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertTriangle className="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" size={24} />
            <div className="flex-1">
              <h4 className="font-bold text-red-800 dark:text-red-300 mb-2">
                ⚠️ Туннель не запущен
              </h4>
              <p className="text-sm text-red-700 dark:text-red-400 mb-3">
                Для получения Webhook URL необходимо запустить туннель. Выполните одну из команд:
              </p>
              <div className="space-y-2">
                <div className="bg-red-100 dark:bg-red-900/40 p-3 rounded border border-red-200 dark:border-red-800">
                  <p className="text-xs text-red-600 dark:text-red-400 font-semibold mb-1">
                    LocalTunnel (рекомендуется):
                  </p>
                  <code className="text-sm text-red-800 dark:text-red-200 font-mono">
                    .\start-with-localtunnel.ps1
                  </code>
                </div>
                <div className="bg-red-100 dark:bg-red-900/40 p-3 rounded border border-red-200 dark:border-red-800">
                  <p className="text-xs text-red-600 dark:text-red-400 font-semibold mb-1">
                    Cloudflare Tunnel:
                  </p>
                  <code className="text-sm text-red-800 dark:text-red-200 font-mono">
                    .\start-with-cloudflare.ps1
                  </code>
                </div>
              </div>
              <p className="text-xs text-red-600 dark:text-red-400 mt-3">
                После запуска нажмите кнопку "Обновить" выше
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
            value={webhookUrl || 'Туннель не запущен - запустите start-with-localtunnel.ps1'}
            readOnly
            className={`flex-1 px-4 py-3 border rounded-lg font-mono text-sm ${
              tunnelRunning
                ? 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white'
                : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700 text-red-700 dark:text-red-400'
            }`}
          />
          <button
            onClick={() => copyToClipboard(webhookUrl)}
            disabled={!tunnelRunning}
            className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
            title={tunnelRunning ? "Копировать URL" : "Туннель не запущен"}
          >
            {copied ? <Check size={20} /> : <Copy size={20} />}
          </button>
        </div>
        {tunnelRunning && webhookUrl && (
          <p className="text-xs text-green-600 dark:text-green-400 mt-2 flex items-center gap-1">
            <CheckCircle size={14} />
            Туннель активен - URL готов к использованию
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

      {/* Note about tunnel URL */}
      <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg">
        <p className="text-sm text-blue-700 dark:text-blue-400">
          <strong>💡 Совет:</strong> Для постоянного URL используйте Cloudflare Tunnel.
          LocalTunnel генерирует новый URL при каждом запуске.
          Страница автоматически обновляет URL каждые 30 секунд.
        </p>
      </div>
    </div>
  );
}
