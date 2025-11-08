import { useState, useEffect, useRef } from 'react';
import { Send, Search, User, Bot, Phone, MoreVertical, Archive } from 'lucide-react';
import { io } from 'socket.io-client';
import api from '../services/api';

export default function LiveChat() {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    loadConversations();
    initializeSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation.id);
      joinConversationRoom(selectedConversation.id);
    }
  }, [selectedConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeSocket = () => {
    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    socketRef.current = io(backendUrl, {
      transports: ['websocket', 'polling']
    });

    socketRef.current.on('connect', () => {
      console.log('Socket connected');
    });

    socketRef.current.on('new_message', (data) => {
      console.log('New message received:', data);
      if (selectedConversation && data.room === `conversation_${selectedConversation.id}`) {
        setMessages(prev => [...prev, data.message]);
      }
      // Update conversation list
      loadConversations();
    });

    socketRef.current.on('disconnect', () => {
      console.log('Socket disconnected');
    });
  };

  const joinConversationRoom = (conversationId) => {
    if (socketRef.current) {
      socketRef.current.emit('join_room', { room: `conversation_${conversationId}` });
    }
  };

  const loadConversations = async () => {
    try {
      const response = await api.get('/conversations', {
        params: { status: 'active', limit: 50 }
      });
      setConversations(response.data.conversations || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const response = await api.get(`/conversations/${conversationId}/messages`);
      setMessages(response.data || []);
    } catch (error) {
      console.error('Failed to load messages:', error);
      setMessages([]);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;

    try {
      const response = await api.post(
        `/conversations/${selectedConversation.id}/messages`,
        {
          content: newMessage,
          message_type: 'text'
        }
      );

      setMessages(prev => [...prev, response.data]);
      setNewMessage('');

      // Emit socket event
      if (socketRef.current) {
        socketRef.current.emit('send_message', {
          room: `conversation_${selectedConversation.id}`,
          message: response.data
        });
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Не удалось отправить сообщение');
    }
  };

  const takeover = async (conversationId) => {
    try {
      await api.post(`/conversations/${conversationId}/takeover`);
      loadConversations();
      alert('Вы взяли диалог в обработку');
    } catch (error) {
      console.error('Failed to takeover:', error);
    }
  };

  const archiveConversation = async (conversationId) => {
    if (!confirm('Архивировать этот диалог?')) return;
    
    try {
      await api.patch(`/conversations/${conversationId}`, { status: 'closed' });
      setSelectedConversation(null);
      loadConversations();
    } catch (error) {
      console.error('Failed to archive:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const filteredConversations = conversations.filter(conv =>
    conv.customer?.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    conv.customer?.phone?.includes(searchQuery)
  );

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins}м назад`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}ч назад`;
    
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] bg-white rounded-lg shadow-md overflow-hidden">
      {/* Conversations List */}
      <div className="w-80 border-r border-gray-200 flex flex-col">
        {/* Search */}
        <div className="p-4 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Поиск диалогов..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="text-center py-12 px-4">
              <p className="text-gray-500">Нет активных диалогов</p>
            </div>
          ) : (
            filteredConversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => setSelectedConversation(conv)}
                className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 ${
                  selectedConversation?.id === conv.id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white flex-shrink-0">
                    <User size={20} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {conv.customer?.name || 'Без имени'}
                      </h3>
                      {conv.bot_active && (
                        <Bot size={16} className="text-purple-600 flex-shrink-0" title="Обрабатывается ботом" />
                      )}
                    </div>
                    <p className="text-sm text-gray-600 flex items-center gap-1">
                      <Phone size={14} />
                      {conv.customer?.phone}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatTime(conv.last_message_at || conv.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedConversation ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
              <div>
                <h2 className="font-semibold text-gray-900">
                  {selectedConversation.customer?.name || 'Без имени'}
                </h2>
                <p className="text-sm text-gray-600">
                  {selectedConversation.customer?.phone}
                </p>
              </div>
              <div className="flex gap-2">
                {selectedConversation.bot_active && (
                  <button
                    onClick={() => takeover(selectedConversation.id)}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
                  >
                    Перехватить у бота
                  </button>
                )}
                <button
                  onClick={() => archiveConversation(selectedConversation.id)}
                  className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                  title="Архивировать"
                >
                  <Archive size={20} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((msg, index) => (
                <div
                  key={msg.id || index}
                  className={`flex ${msg.direction === 'outbound' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[70%] px-4 py-2 rounded-lg ${
                      msg.direction === 'outbound'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-gray-200 text-gray-900'
                    }`}
                  >
                    <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        msg.direction === 'outbound' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {new Date(msg.timestamp || msg.created_at).toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <form onSubmit={sendMessage} className="p-4 border-t border-gray-200 bg-white">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Введите сообщение..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  disabled={selectedConversation.bot_active}
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim() || selectedConversation.bot_active}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Send size={20} />
                  Отправить
                </button>
              </div>
              {selectedConversation.bot_active && (
                <p className="text-sm text-gray-500 mt-2">
                  Диалог обрабатывается ботом. Нажмите "Перехватить у бота" для ручного управления.
                </p>
              )}
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <User size={64} className="mx-auto mb-4 text-gray-300" />
              <p>Выберите диалог для начала общения</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
