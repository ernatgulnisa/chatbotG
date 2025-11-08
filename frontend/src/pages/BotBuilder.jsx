import { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useParams, useNavigate } from 'react-router-dom';
import { getBot, createBot, updateBot, getBotScenarios, createBotScenario, updateBotScenario } from '../services/botService';

// Кастомные узлы для разных типов шагов бота
const nodeTypes = {
  welcome: WelcomeNode,
  message: MessageNode,
  question: QuestionNode,
  buttons: ButtonsNode,
  condition: ConditionNode,
  action: ActionNode,
};

function WelcomeNode({ data }) {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white border-2 border-blue-700">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">👋</span>
        <div className="font-bold">Приветствие</div>
      </div>
      <div className="text-sm opacity-90">{data.message || 'Добро пожаловать!'}</div>
    </div>
  );
}

function MessageNode({ data }) {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">💬</span>
        <div className="font-bold">Сообщение</div>
      </div>
      <div className="text-sm text-gray-600 dark:text-gray-300">{data.message || 'Текст сообщения'}</div>
    </div>
  );
}

function QuestionNode({ data }) {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-purple-50 dark:bg-purple-900 border-2 border-purple-400">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">❓</span>
        <div className="font-bold text-purple-700 dark:text-purple-200">Вопрос</div>
      </div>
      <div className="text-sm text-purple-600 dark:text-purple-300">{data.question || 'Ваш вопрос?'}</div>
    </div>
  );
}

function ButtonsNode({ data }) {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-green-50 dark:bg-green-900 border-2 border-green-400">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">🔘</span>
        <div className="font-bold text-green-700 dark:text-green-200">Кнопки</div>
      </div>
      <div className="text-sm text-green-600 dark:text-green-300">
        {data.buttons?.length || 0} кнопок
      </div>
    </div>
  );
}

function ConditionNode({ data }) {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-yellow-50 dark:bg-yellow-900 border-2 border-yellow-400">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">⚡</span>
        <div className="font-bold text-yellow-700 dark:text-yellow-200">Условие</div>
      </div>
      <div className="text-sm text-yellow-600 dark:text-yellow-300">{data.condition || 'Условие'}</div>
    </div>
  );
}

function ActionNode({ data }) {
  return (
    <div className="px-4 py-3 shadow-lg rounded-lg bg-red-50 dark:bg-red-900 border-2 border-red-400">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">⚙️</span>
        <div className="font-bold text-red-700 dark:text-red-200">Действие</div>
      </div>
      <div className="text-sm text-red-600 dark:text-red-300">{data.action || 'Действие'}</div>
    </div>
  );
}

// Начальные узлы и связи
const initialNodes = [
  {
    id: '1',
    type: 'welcome',
    position: { x: 250, y: 50 },
    data: { message: 'Здравствуйте! Добро пожаловать в наш сервис!' },
  },
];

const initialEdges = [];

export default function BotBuilder() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(null);
  const [botName, setBotName] = useState('Новый бот');
  const [botData, setBotData] = useState(null);
  const [scenarioId, setScenarioId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Загрузка данных бота при монтировании
  useEffect(() => {
    if (id && id !== 'new') {
      loadBot();
    }
  }, [id]);

  const loadBot = async () => {
    try {
      setLoading(true);
      const bot = await getBot(id);
      setBotData(bot);
      setBotName(bot.name);

      // Загружаем сценарии
      const scenarios = await getBotScenarios(id);
      if (scenarios.length > 0) {
        const defaultScenario = scenarios.find(s => s.is_default) || scenarios[0];
        setScenarioId(defaultScenario.id);
        
        // Загружаем flow_data из сценария
        if (defaultScenario.flow_data && defaultScenario.flow_data.nodes) {
          setNodes(defaultScenario.flow_data.nodes);
          setEdges(defaultScenario.flow_data.edges || []);
        }
      }
    } catch (error) {
      console.error('Failed to load bot:', error);
      alert('Ошибка загрузки бота');
    } finally {
      setLoading(false);
    }
  };

  const onConnect = useCallback(
    (params) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            markerEnd: { type: MarkerType.ArrowClosed },
            style: { strokeWidth: 2 },
          },
          eds
        )
      ),
    [setEdges]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const addNode = (type) => {
    const newNode = {
      id: `${nodes.length + 1}`,
      type,
      position: {
        x: Math.random() * 400 + 50,
        y: Math.random() * 400 + 100,
      },
      data: getDefaultNodeData(type),
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const getDefaultNodeData = (type) => {
    switch (type) {
      case 'welcome':
        return { message: 'Приветственное сообщение' };
      case 'message':
        return { message: 'Новое сообщение' };
      case 'question':
        return { question: 'Ваш вопрос?' };
      case 'buttons':
        return { buttons: ['Кнопка 1', 'Кнопка 2'] };
      case 'condition':
        return { condition: 'Если условие выполнено' };
      case 'action':
        return { action: 'Выполнить действие' };
      default:
        return {};
    }
  };

  const updateNodeData = (nodeId, newData) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...newData } } : node
      )
    );
  };

  const saveBot = async () => {
    try {
      setSaving(true);
      
      const scenarioData = {
        name: botName,
        description: `Сценарий для ${botName}`,
        flow_data: {
          nodes,
          edges,
        },
        is_default: true,
        is_active: true,
      };

      if (id === 'new') {
        // Создаем новый бот - требуется whatsapp_number_id
        // TODO: Добавить выбор WhatsApp номера в UI
        alert('Для создания нового бота необходимо выбрать WhatsApp номер. Функция в разработке.');
        return;
      } else {
        // Обновляем существующий бот
        await updateBot(id, { name: botName });
        
        if (scenarioId) {
          // Обновляем существующий сценарий
          await updateBotScenario(id, scenarioId, scenarioData);
        } else {
          // Создаем новый сценарий
          const newScenario = await createBotScenario(id, scenarioData);
          setScenarioId(newScenario.id);
        }
      }
      
      alert('✅ Бот успешно сохранен!');
    } catch (error) {
      console.error('Failed to save bot:', error);
      alert('❌ Ошибка сохранения бота: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/bots')}
              className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
            >
              ← Назад
            </button>
            {loading ? (
              <div className="text-xl font-bold">Загрузка...</div>
            ) : (
              <input
                type="text"
                value={botName}
                onChange={(e) => setBotName(e.target.value)}
                className="text-2xl font-bold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2"
              />
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={saveBot}
              disabled={saving || loading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? '⏳ Сохранение...' : '💾 Сохранить'}
            </button>
            <button
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              👁️ Предпросмотр
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - Палитра узлов */}
        <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4 overflow-y-auto">
          <h3 className="font-bold text-lg mb-4">Элементы бота</h3>
          <div className="space-y-2">
            <NodeButton
              icon="👋"
              label="Приветствие"
              onClick={() => addNode('welcome')}
            />
            <NodeButton
              icon="💬"
              label="Сообщение"
              onClick={() => addNode('message')}
            />
            <NodeButton
              icon="❓"
              label="Вопрос"
              onClick={() => addNode('question')}
            />
            <NodeButton
              icon="🔘"
              label="Кнопки"
              onClick={() => addNode('buttons')}
            />
            <NodeButton
              icon="⚡"
              label="Условие"
              onClick={() => addNode('condition')}
            />
            <NodeButton
              icon="⚙️"
              label="Действие"
              onClick={() => addNode('action')}
            />
          </div>

          {/* Информация о выбранном узле */}
          {selectedNode && (
            <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="font-bold text-lg mb-4">Настройки узла</h3>
              <NodeEditor
                node={selectedNode}
                onUpdate={(data) => updateNodeData(selectedNode.id, data)}
              />
            </div>
          )}
        </div>

        {/* Canvas - React Flow */}
        <div className="flex-1 bg-gray-50 dark:bg-gray-900">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
          >
            <Controls />
            <MiniMap />
            <Background variant="dots" gap={12} size={1} />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}

function NodeButton({ icon, label, onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-4 py-3 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
    >
      <span className="text-2xl">{icon}</span>
      <span className="font-medium">{label}</span>
    </button>
  );
}

function NodeEditor({ node, onUpdate }) {
  const [localData, setLocalData] = useState(node.data);

  const handleChange = (field, value) => {
    const newData = { ...localData, [field]: value };
    setLocalData(newData);
    onUpdate(newData);
  };

  switch (node.type) {
    case 'welcome':
    case 'message':
      return (
        <div>
          <label className="block text-sm font-medium mb-2">Текст сообщения</label>
          <textarea
            value={localData.message || ''}
            onChange={(e) => handleChange('message', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700"
            rows={4}
          />
        </div>
      );
    case 'question':
      return (
        <div>
          <label className="block text-sm font-medium mb-2">Вопрос</label>
          <textarea
            value={localData.question || ''}
            onChange={(e) => handleChange('question', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700"
            rows={3}
          />
        </div>
      );
    case 'buttons':
      return (
        <div>
          <label className="block text-sm font-medium mb-2">Кнопки (по одной на строку)</label>
          <textarea
            value={localData.buttons?.join('\n') || ''}
            onChange={(e) => handleChange('buttons', e.target.value.split('\n'))}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700"
            rows={4}
          />
        </div>
      );
    case 'condition':
      return (
        <div>
          <label className="block text-sm font-medium mb-2">Условие</label>
          <input
            type="text"
            value={localData.condition || ''}
            onChange={(e) => handleChange('condition', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700"
          />
        </div>
      );
    case 'action':
      return (
        <div>
          <label className="block text-sm font-medium mb-2">Действие</label>
          <input
            type="text"
            value={localData.action || ''}
            onChange={(e) => handleChange('action', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700"
          />
        </div>
      );
    default:
      return null;
  }
}
