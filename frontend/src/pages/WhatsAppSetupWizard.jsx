import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { debugAuth, checkTokenValidity } from '../utils/authDebug';

export default function WhatsAppSetupWizard() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    display_name: '',
    phone_number: '',
    phone_number_id: '',
    waba_id: '',
    api_token: '',
    is_active: true
  });

  const steps = [
    {
      id: 1,
      title: 'Регистрация в Meta',
      description: 'Создайте приложение в Meta for Developers'
    },
    {
      id: 2,
      title: 'Получение данных',
      description: 'Скопируйте Phone Number ID и Access Token'
    },
    {
      id: 3,
      title: 'Добавление номера',
      description: 'Введите данные в форму'
    },
    {
      id: 4,
      title: 'Готово!',
      description: 'Ваш WhatsApp номер подключен'
    }
  ];

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Debug: проверка токена перед отправкой
    console.log('=== Submitting WhatsApp Number ===');
    debugAuth();
    const tokenValid = await checkTokenValidity();
    console.log('Token valid:', tokenValid);

    try {
      await api.post('/whatsapp/numbers', formData);
      
      setCurrentStep(4);
      setTimeout(() => {
        navigate('/whatsapp');
      }, 3000);
    } catch (err) {
      console.error('Error adding WhatsApp number:', err);
      console.error('Error response:', err.response);
      
      // Более детальная обработка ошибок
      if (err.response?.status === 401) {
        setError('Сессия истекла. Пожалуйста, войдите снова.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else if (err.response?.status === 400) {
        setError(err.response?.data?.detail || 'Неверные данные. Проверьте заполнение полей.');
      } else if (err.response?.status === 500) {
        setError('Ошибка сервера. Проверьте логи backend.');
      } else {
        setError(err.response?.data?.detail || err.message || 'Ошибка при добавлении номера');
      }
      
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Скопировано!');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                      currentStep >= step.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-300 text-gray-600'
                    }`}
                  >
                    {currentStep > step.id ? '✓' : step.id}
                  </div>
                  <div className="text-xs mt-2 text-center">
                    <div className="font-semibold">{step.title}</div>
                    <div className="text-gray-500 hidden sm:block">{step.description}</div>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`h-1 flex-1 mx-2 ${
                      currentStep > step.id ? 'bg-blue-600' : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Step 1: Регистрация */}
          {currentStep === 1 && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Шаг 1: Регистрация в Meta for Developers</h2>
              
              <div className="space-y-6">
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                  <p className="text-sm text-blue-700">
                    📱 Meta предоставляет бесплатный тестовый номер для разработки с лимитом 250 сообщений в день
                  </p>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Что нужно сделать:</h3>
                  
                  <ol className="list-decimal list-inside space-y-3">
                    <li>
                      Откройте{' '}
                      <a
                        href="https://developers.facebook.com/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline font-semibold"
                      >
                        Meta for Developers →
                      </a>
                    </li>
                    <li>Войдите с вашим аккаунтом Facebook</li>
                    <li>Нажмите <strong>"My Apps"</strong> → <strong>"Create App"</strong></li>
                    <li>Выберите тип: <strong>"Business"</strong></li>
                    <li>Заполните информацию:
                      <ul className="ml-6 mt-2 space-y-1 text-gray-600">
                        <li>• App Name: Название вашего бизнеса</li>
                        <li>• App Contact Email: Ваш email</li>
                      </ul>
                    </li>
                    <li>В панели приложения нажмите <strong>"Add Product"</strong></li>
                    <li>Найдите <strong>"WhatsApp"</strong> и нажмите <strong>"Set Up"</strong></li>
                  </ol>
                </div>

                <div className="bg-green-50 border-l-4 border-green-500 p-4 mt-6">
                  <p className="text-sm text-green-700">
                    ✅ После добавления WhatsApp продукта, переходите к следующему шагу
                  </p>
                </div>

                <div className="flex justify-end mt-6">
                  <button
                    onClick={() => setCurrentStep(2)}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold"
                  >
                    Я создал приложение →
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Получение данных */}
          {currentStep === 2 && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Шаг 2: Получение учетных данных</h2>
              
              <div className="space-y-6">
                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
                  <p className="text-sm text-yellow-700">
                    🔑 Эти данные нужны для подключения вашего номера к платформе
                  </p>
                </div>

                <div className="space-y-6">
                  {/* Phone Number ID */}
                  <div className="border rounded-lg p-4 bg-gray-50">
                    <h4 className="font-semibold mb-2">1. Phone Number ID</h4>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
                      <li>В Meta Dashboard перейдите: <strong>WhatsApp → Getting Started</strong></li>
                      <li>Найдите раздел <strong>"Test number"</strong></li>
                      <li>Скопируйте <strong>Phone Number ID</strong> (15-16 цифр)</li>
                    </ol>
                    <div className="mt-3 p-2 bg-white border rounded font-mono text-xs">
                      Пример: 1234567890123456
                    </div>
                  </div>

                  {/* Access Token */}
                  <div className="border rounded-lg p-4 bg-gray-50">
                    <h4 className="font-semibold mb-2">2. Temporary Access Token</h4>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
                      <li>На той же странице найдите <strong>"Temporary access token"</strong></li>
                      <li>Нажмите <strong>"Copy"</strong> (токен начинается с "EAA...")</li>
                    </ol>
                    <div className="mt-3 p-2 bg-white border rounded font-mono text-xs break-all">
                      Пример: EAAxxxxxxxxxxxxxxxxxx...
                    </div>
                    <p className="text-xs text-orange-600 mt-2">
                      ⚠️ Временный токен действует 24 часа. Для production создайте постоянный токен.
                    </p>
                  </div>

                  {/* WABA ID (опционально) */}
                  <div className="border rounded-lg p-4 bg-gray-50">
                    <h4 className="font-semibold mb-2">3. WhatsApp Business Account ID (опционально)</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      На странице Getting Started также указан WABA ID (можно пропустить)
                    </p>
                  </div>

                  {/* Тестовый номер получателя */}
                  <div className="border rounded-lg p-4 bg-blue-50">
                    <h4 className="font-semibold mb-2">4. Добавьте тестовый номер (ВАЖНО!)</h4>
                    <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
                      <li>На странице Getting Started найдите <strong>"To"</strong></li>
                      <li>Нажмите <strong>"Add phone number"</strong></li>
                      <li>Введите ваш личный номер WhatsApp (например: +77711919140)</li>
                      <li>Подтвердите через SMS код</li>
                    </ol>
                    <p className="text-xs text-blue-600 mt-2">
                      💡 Тестовый номер может отправлять сообщения только на добавленные номера!
                    </p>
                  </div>
                </div>

                <div className="flex justify-between mt-6">
                  <button
                    onClick={() => setCurrentStep(1)}
                    className="bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300"
                  >
                    ← Назад
                  </button>
                  <button
                    onClick={() => setCurrentStep(3)}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold"
                  >
                    Я скопировал данные →
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Форма */}
          {currentStep === 3 && (
            <div>
              <h2 className="text-2xl font-bold mb-4">Шаг 3: Добавление номера</h2>
              
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border-l-4 border-red-500 p-4">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                )}

                {/* Display Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Название номера *
                  </label>
                  <input
                    type="text"
                    name="display_name"
                    value={formData.display_name}
                    onChange={handleInputChange}
                    placeholder="Например: Основной номер"
                    required
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">Для вашего удобства, не видно клиентам</p>
                </div>

                {/* Phone Number */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Номер телефона *
                  </label>
                  <input
                    type="text"
                    name="phone_number"
                    value={formData.phone_number}
                    onChange={handleInputChange}
                    placeholder="+77711919140"
                    required
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">В международном формате с +</p>
                </div>

                {/* Phone Number ID */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number ID *
                  </label>
                  <input
                    type="text"
                    name="phone_number_id"
                    value={formData.phone_number_id}
                    onChange={handleInputChange}
                    placeholder="1234567890123456"
                    required
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  />
                  <p className="text-xs text-gray-500 mt-1">Из Meta Dashboard (15-16 цифр)</p>
                </div>

                {/* Access Token */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Access Token *
                  </label>
                  <textarea
                    name="api_token"
                    value={formData.api_token}
                    onChange={handleInputChange}
                    placeholder="EAAxxxxxxxxxxxxxxxxxx..."
                    required
                    rows="3"
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    🔒 Будет автоматически зашифрован при сохранении
                  </p>
                </div>

                {/* WABA ID (optional) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    WhatsApp Business Account ID (опционально)
                  </label>
                  <input
                    type="text"
                    name="waba_id"
                    value={formData.waba_id}
                    onChange={handleInputChange}
                    placeholder="1234567890"
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                  />
                  <p className="text-xs text-gray-500 mt-1">Можно оставить пустым</p>
                </div>

                {/* Active Toggle */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <label className="ml-2 text-sm font-medium text-gray-700">
                    Активировать номер сразу
                  </label>
                </div>

                <div className="flex justify-between mt-6">
                  <button
                    type="button"
                    onClick={() => setCurrentStep(2)}
                    className="bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300"
                  >
                    ← Назад
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold disabled:bg-gray-400"
                  >
                    {loading ? 'Сохранение...' : 'Добавить номер →'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Step 4: Успех */}
          {currentStep === 4 && (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🎉</div>
              <h2 className="text-3xl font-bold mb-4 text-green-600">Готово!</h2>
              <p className="text-gray-600 mb-6">
                WhatsApp номер успешно подключен к вашей платформе
              </p>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6 max-w-md mx-auto">
                <h3 className="font-semibold mb-3">Что дальше?</h3>
                <ul className="text-left space-y-2 text-sm">
                  <li>✅ Создайте бота в разделе "Bots"</li>
                  <li>✅ Настройте сценарий в Bot Builder</li>
                  <li>✅ Настройте Webhook (опционально)</li>
                  <li>✅ Отправьте тестовое сообщение</li>
                </ul>
              </div>

              <div className="space-x-4">
                <button
                  onClick={() => navigate('/whatsapp')}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-semibold"
                >
                  Перейти к номерам
                </button>
                <button
                  onClick={() => navigate('/bots')}
                  className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-semibold"
                >
                  Создать бота
                </button>
              </div>

              <p className="text-xs text-gray-500 mt-6">
                Перенаправление через 3 секунды...
              </p>
            </div>
          )}
        </div>

        {/* Help Section */}
        {currentStep < 4 && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold mb-3 flex items-center">
              <span className="text-xl mr-2">💡</span>
              Нужна помощь?
            </h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p>
                📚 Подробная инструкция:{' '}
                <a href="/WHATSAPP_SETUP.md" className="text-blue-600 hover:underline">
                  WHATSAPP_SETUP.md
                </a>
              </p>
              <p>
                🔧 Настройка туннеля:{' '}
                <a href="/TUNNELING_METHODS.md" className="text-blue-600 hover:underline">
                  TUNNELING_METHODS.md
                </a>
              </p>
              <p className="font-semibold text-gray-700 mt-2">
                🌐 Текущий Webhook URL:{' '}
              </p>
              <div className="mt-1 flex items-center gap-2">
                <button
                  onClick={() => copyToClipboard('https://funny-parents-slide.loca.lt/api/v1/webhooks/whatsapp')}
                  className="text-blue-600 hover:underline font-mono text-xs bg-white border rounded px-2 py-1"
                >
                  https://funny-parents-slide.loca.lt/api/v1/webhooks/whatsapp
                </button>
                <span className="text-xs text-green-600">← Нажмите чтобы скопировать</span>
              </div>
              <p className="font-semibold text-gray-700 mt-2">
                🔑 Verify Token:{' '}
              </p>
              <div className="mt-1 flex items-center gap-2">
                <button
                  onClick={() => copyToClipboard('HUcyCWK3WswmeK3PAqJknLKnHnfbOdEJgR_LYq8_YaI')}
                  className="text-blue-600 hover:underline font-mono text-xs bg-white border rounded px-2 py-1"
                >
                  HUcyCWK3WswmeK3PAqJknLKnHnfbOdEJgR_LYq8_YaI
                </button>
                <span className="text-xs text-green-600">← Нажмите чтобы скопировать</span>
              </div>
              <p className="text-xs text-orange-600 mt-2">
                ⚠️ Webhook URL меняется при каждом перезапуске туннеля. Для production используйте постоянный домен.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
