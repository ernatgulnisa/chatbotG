"""
Custom Tunnel Server
Принимает HTTP запросы и перенаправляет их через WebSocket на клиент
Запускается на сервере с публичным IP
"""
import asyncio
import uuid
from aiohttp import web, WSMsgType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TunnelServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.clients = {}  # {tunnel_id: websocket}
        self.pending_requests = {}  # {request_id: future}
        
    async def websocket_handler(self, request):
        """Обработка WebSocket соединения от клиента"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        tunnel_id = str(uuid.uuid4())[:8]
        self.clients[tunnel_id] = ws
        
        logger.info(f"Client connected: {tunnel_id}")
        logger.info(f"Tunnel URL: http://{request.host}/{tunnel_id}")
        
        # Отправить клиенту его tunnel_id
        await ws.send_json({
            'type': 'connected',
            'tunnel_id': tunnel_id,
            'url': f"http://{request.host}/{tunnel_id}"
        })
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    data = msg.json()
                    
                    if data['type'] == 'response':
                        # Получен ответ от клиента
                        request_id = data['request_id']
                        if request_id in self.pending_requests:
                            future = self.pending_requests.pop(request_id)
                            future.set_result(data)
                            
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f'WebSocket error: {ws.exception()}')
                    
        finally:
            if tunnel_id in self.clients:
                del self.clients[tunnel_id]
            logger.info(f"Client disconnected: {tunnel_id}")
            
        return ws
    
    async def http_handler(self, request):
        """Обработка HTTP запросов и перенаправление через WebSocket"""
        # Получить tunnel_id из пути
        path_parts = request.path.strip('/').split('/')
        if not path_parts or not path_parts[0]:
            return web.Response(text="Tunnel Server Running\nConnect client to /ws", status=200)
            
        tunnel_id = path_parts[0]
        
        if tunnel_id not in self.clients:
            return web.Response(text=f"Tunnel {tunnel_id} not found", status=404)
        
        # Получить оригинальный путь (без tunnel_id)
        original_path = '/' + '/'.join(path_parts[1:])
        if request.query_string:
            original_path += '?' + request.query_string
        
        # Прочитать тело запроса
        body = await request.read()
        
        # Создать уникальный ID для запроса
        request_id = str(uuid.uuid4())
        
        # Подготовить данные для отправки клиенту
        request_data = {
            'type': 'request',
            'request_id': request_id,
            'method': request.method,
            'path': original_path,
            'headers': dict(request.headers),
            'body': body.decode('utf-8') if body else ''
        }
        
        # Создать Future для ожидания ответа
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        # Отправить запрос клиенту
        ws = self.clients[tunnel_id]
        await ws.send_json(request_data)
        
        try:
            # Ждать ответ от клиента (таймаут 30 секунд)
            response_data = await asyncio.wait_for(future, timeout=30.0)
            
            # Вернуть ответ
            return web.Response(
                body=response_data.get('body', ''),
                status=response_data.get('status', 200),
                headers=response_data.get('headers', {})
            )
            
        except asyncio.TimeoutError:
            return web.Response(text="Request timeout", status=504)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return web.Response(text="Internal server error", status=500)
    
    async def start(self):
        """Запуск сервера"""
        app = web.Application()
        app.router.add_get('/ws', self.websocket_handler)
        app.router.add_route('*', '/{tail:.*}', self.http_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"Tunnel Server started on {self.host}:{self.port}")
        logger.info(f"Clients connect to: ws://{self.host}:{self.port}/ws")
        
        # Держать сервер запущенным
        await asyncio.Event().wait()


if __name__ == '__main__':
    server = TunnelServer(host='0.0.0.0', port=8080)
    asyncio.run(server.start())
