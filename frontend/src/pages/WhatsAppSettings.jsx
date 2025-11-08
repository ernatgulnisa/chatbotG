import { useState, useEffect } from 'react';
import { Plus, Phone, Trash2, Edit2, Check, X, ExternalLink, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import WebhookInfo from '../components/WebhookInfo';

export default function WhatsAppSettings() {
  const navigate = useNavigate();
  const [numbers, setNumbers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    display_name: '',
    phone_number: '',
    phone_number_id: '',
    waba_id: '',
    api_token: '',
    is_active: true
  });

  useEffect(() => {
    loadNumbers();
  }, []);

  const loadNumbers = async () => {
    try {
      const response = await api.get('/whatsapp/numbers');
      setNumbers(response.data);
    } catch (error) {
      console.error('Failed to load WhatsApp numbers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/whatsapp/numbers/${editingId}`, formData);
      } else {
        await api.post('/whatsapp/numbers', formData);
      }
      
      resetForm();
      loadNumbers();
    } catch (error) {
      console.error('Failed to save WhatsApp number:', error);
      alert(error.response?.data?.detail || 'Failed to save');
    }
  };

  const handleEdit = (number) => {
    setEditingId(number.id);
    setFormData({
      display_name: number.display_name,
      phone_number: number.phone_number,
      phone_number_id: number.phone_number_id,
      waba_id: number.waba_id,
      api_token: '***************', // Don't show actual token
      is_active: number.is_active
    });
    setShowAddForm(true);
  };

  const handleDelete = async (id) => {
    const confirmed = confirm(
      'Внимание! При удалении номера будут удалены:\n\n' +
      '• Все боты, привязанные к этому номеру\n' +
      '• Все разговоры через этот номер\n' +
      '• Все рассылки с этого номера\n\n' +
      'Вы уверены, что хотите удалить этот номер?'
    );
    
    if (!confirmed) return;
    
    try {
      await api.delete(`/whatsapp/numbers/${id}`);
      alert('✓ Номер успешно удален');
      loadNumbers();
    } catch (error) {
      console.error('Failed to delete number:', error);
      const errorMessage = error.response?.data?.detail || 'Не удалось удалить номер';
      alert(`❌ Ошибка удаления:\n${errorMessage}`);
    }
  };

  const toggleActive = async (id, isActive) => {
    try {
      await api.patch(`/whatsapp/numbers/${id}/toggle`, { is_active: !isActive });
      loadNumbers();
    } catch (error) {
      console.error('Failed to toggle status:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      display_name: '',
      phone_number: '',
      phone_number_id: '',
      waba_id: '',
      api_token: '',
      is_active: true
    });
    setEditingId(null);
    setShowAddForm(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">WhatsApp Номера</h1>
          <p className="text-gray-600 mt-1">Управление номерами WhatsApp Business API</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/whatsapp/setup')}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-lg hover:from-green-600 hover:to-blue-700 shadow-lg"
          >
            <Zap size={20} />
            Быстрая настройка
          </button>
          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            <Plus size={20} />
            Добавить вручную
          </button>
        </div>
      </div>

      {/* Webhook Info Component */}
      <WebhookInfo />

      {/* Setup Guide */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">📘 Как получить данные для подключения:</h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
          <li>
            Перейдите в{' '}
            <a 
              href="https://developers.facebook.com/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="underline hover:text-blue-600"
            >
              Meta for Developers
            </a>
          </li>
          <li>Создайте приложение с типом "Business"</li>
          <li>Добавьте продукт "WhatsApp"</li>
          <li>Настройте тестовый номер или подключите свой бизнес-аккаунт</li>
          <li>Получите <strong>Phone Number ID</strong> и <strong>Access Token</strong> в разделе "API Setup"</li>
          <li>Установите Webhook URL: <code className="bg-blue-100 px-2 py-1 rounded">https://your-domain.com/api/v1/webhooks/whatsapp</code></li>
          <li>Verify Token: проверьте в настройках проекта (файл .env)</li>
        </ol>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">
              {editingId ? 'Редактировать номер' : 'Добавить номер'}
            </h2>
            <button onClick={resetForm} className="text-gray-500 hover:text-gray-700">
              <X size={24} />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Название
              </label>
              <input
                type="text"
                value={formData.display_name}
                onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="Салон красоты - основной"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Номер телефона
              </label>
              <input
                type="text"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="+79001234567"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number ID
                <span className="text-gray-500 text-xs ml-2">(из Meta Dashboard)</span>
              </label>
              <input
                type="text"
                value={formData.phone_number_id}
                onChange={(e) => setFormData({ ...formData, phone_number_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="123456789012345"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                WhatsApp Business Account ID
                <span className="text-gray-500 text-xs ml-2">(опционально)</span>
              </label>
              <input
                type="text"
                value={formData.waba_id}
                onChange={(e) => setFormData({ ...formData, waba_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="123456789012345"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Access Token
                <span className="text-gray-500 text-xs ml-2">(будет зашифрован)</span>
              </label>
              <input
                type="password"
                value={formData.api_token}
                onChange={(e) => setFormData({ ...formData, api_token: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                placeholder="EAAxxxxxxxxxx..."
                required={!editingId}
              />
              {editingId && (
                <p className="text-xs text-gray-500 mt-1">
                  Оставьте пустым, чтобы не менять токен
                </p>
              )}
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
              />
              <label htmlFor="is_active" className="text-sm text-gray-700">
                Активировать номер
              </label>
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 font-medium"
              >
                {editingId ? 'Сохранить изменения' : 'Добавить номер'}
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Numbers List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {numbers.length === 0 ? (
          <div className="text-center py-16 px-4">
            <div className="max-w-md mx-auto">
              <Phone size={64} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Нет подключенных номеров
              </h3>
              <p className="text-gray-600 mb-6">
                Подключите WhatsApp Business номер, чтобы начать отправлять и получать сообщения от клиентов
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <button
                  onClick={() => navigate('/whatsapp/setup')}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-lg hover:from-green-600 hover:to-blue-700 shadow-lg font-semibold"
                >
                  <Zap size={20} />
                  Пошаговая настройка
                </button>
                <button
                  onClick={() => setShowAddForm(true)}
                  className="flex items-center justify-center gap-2 px-6 py-3 border-2 border-green-600 text-green-600 rounded-lg hover:bg-green-50 font-semibold"
                >
                  <Plus size={20} />
                  Добавить вручную
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-6">
                💡 Рекомендуем использовать пошаговую настройку, если подключаете WhatsApp впервые
              </p>
            </div>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Название
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Номер
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Phone Number ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Статус
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {numbers.map((number) => (
                <tr key={number.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{number.display_name}</div>
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {number.phone_number}
                  </td>
                  <td className="px-6 py-4">
                    <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {number.phone_number_id}
                    </code>
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => toggleActive(number.id, number.is_active)}
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        number.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {number.is_active ? 'Активен' : 'Неактивен'}
                    </button>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(number)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                        title="Редактировать"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button
                        onClick={() => handleDelete(number.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded"
                        title="Удалить"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Webhook Info */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-2">🔗 Webhook URL для Meta Dashboard:</h3>
        <div className="flex items-center gap-2">
          <code className="flex-1 bg-white px-4 py-2 rounded border border-gray-300 text-sm">
            {window.location.origin.replace(':3001', ':8000')}/api/v1/webhooks/whatsapp
          </code>
          <button
            onClick={() => {
              navigator.clipboard.writeText(
                `${window.location.origin.replace(':3001', ':8000')}/api/v1/webhooks/whatsapp`
              );
              alert('URL скопирован в буфер обмена');
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            Копировать
          </button>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Используйте этот URL при настройке webhook в Meta for Developers
        </p>
      </div>
    </div>
  );
}
