import api from './api';

/**
 * Сервис для работы с ботами
 */

// Получить список всех ботов
export const getBots = async (params = {}) => {
  const response = await api.get('/bots/', { params });
  return response.data;
};

// Получить конкретного бота
export const getBot = async (botId) => {
  const response = await api.get(`/bots/${botId}`);
  return response.data;
};

// Создать нового бота
export const createBot = async (botData) => {
  const response = await api.post('/bots/', botData);
  return response.data;
};

// Обновить бота
export const updateBot = async (botId, botData) => {
  const response = await api.put(`/bots/${botId}`, botData);
  return response.data;
};

// Удалить бота
export const deleteBot = async (botId) => {
  await api.delete(`/bots/${botId}`);
};

// Переключить статус бота (активен/неактивен)
export const toggleBotStatus = async (botId) => {
  const response = await api.post(`/bots/${botId}/toggle`);
  return response.data;
};

// === Сценарии ===

// Получить все сценарии бота
export const getBotScenarios = async (botId) => {
  const response = await api.get(`/bots/${botId}/scenarios`);
  return response.data;
};

// Получить конкретный сценарий
export const getBotScenario = async (botId, scenarioId) => {
  const response = await api.get(`/bots/${botId}/scenarios/${scenarioId}`);
  return response.data;
};

// Создать новый сценарий
export const createBotScenario = async (botId, scenarioData) => {
  const response = await api.post(`/bots/${botId}/scenarios`, scenarioData);
  return response.data;
};

// Обновить сценарий
export const updateBotScenario = async (botId, scenarioId, scenarioData) => {
  const response = await api.put(`/bots/${botId}/scenarios/${scenarioId}`, scenarioData);
  return response.data;
};

// Удалить сценарий
export const deleteBotScenario = async (botId, scenarioId) => {
  await api.delete(`/bots/${botId}/scenarios/${scenarioId}`);
};

export default {
  getBots,
  getBot,
  createBot,
  updateBot,
  deleteBot,
  toggleBotStatus,
  getBotScenarios,
  getBotScenario,
  createBotScenario,
  updateBotScenario,
  deleteBotScenario,
};
