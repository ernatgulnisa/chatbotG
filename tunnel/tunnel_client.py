"""
Custom Tunnel Client
Подключается к серверу и перенаправляет запросы на локальный backend
Запускается на вашем локальном компьютере
"""
import asyncio
import aiohttp
import logging
from aiohttp import ClientSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TunnelClient:
    def __init__(self, server_url, local_port=8000):
        """
        Args:
            server_url: URL сервера (например: ws://your-vps-ip:8080/ws)
            local_port: Порт локального backend (по умолчанию 8000)
        """
        self.server_url = server_url
        self.local_url = f"http://localhost:{local_port}"
        self.tunnel_url = None
        
    async def process_request(self, request_data, ws):
        """Обработать запрос от сервера и отправить в локальный backend"""
        request_id = request_data['request_id']
        method = request_data['method']
        path = request_data['path']
        headers = request_data['headers']
        body = request_data.get('body', '')
        
        logger.info(f"Processing {method} {path}")
        
        try:
            # Отправить запрос на локальный backend
            async with ClientSession() as session:
                url = self.local_url + path
                
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=body.encode('utf-8') if body else None
                ) as response:
                    response_body = await response.text()
                    response_headers = dict(response.headers)
                    
                    # Отправить ответ обратно на сервер
                    await ws.send_json({
                        'type': 'response',
                        'request_id': request_id,
                        'status': response.status,
                        'headers': response_headers,
                        'body': response_body
                    })
                    
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            # Отправить ошибку на сервер
            await ws.send_json({
                'type': 'response',
                'request_id': request_id,
                'status': 502,
                'headers': {},
                'body': f"Error connecting to local server: {str(e)}"
            })
    
    async def connect(self):
        """Подключиться к серверу"""
        logger.info(f"Connecting to tunnel server: {self.server_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.server_url) as ws:
                logger.info("Connected to tunnel server")
                
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = msg.json()
                        
                        if data['type'] == 'connected':
                            self.tunnel_url = data['url']
                            logger.info("=" * 60)
                            logger.info("🎉 TUNNEL ACTIVE!")
                            logger.info(f"📡 Public URL: {self.tunnel_url}")
                            logger.info(f"🔗 Webhook URL: {self.tunnel_url}/api/v1/webhooks/whatsapp")
                            logger.info("=" * 60)
                            
                        elif data['type'] == 'request':
                            # Обработать входящий запрос
                            await self.process_request(data, ws)
                            
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f'WebSocket error: {ws.exception()}')
                        break
                        
                logger.info("Disconnected from tunnel server")
    
    async def start(self):
        """Запустить клиент с автоматическим переподключением"""
        while True:
            try:
                await self.connect()
            except Exception as e:
                logger.error(f"Connection error: {e}")
                logger.info("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tunnel_client.py ws://SERVER_IP:8080/ws [LOCAL_PORT]")
        print("Example: python tunnel_client.py ws://123.456.789.0:8080/ws 8000")
        sys.exit(1)
    
    server_url = sys.argv[1]
    local_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    
    client = TunnelClient(server_url, local_port)
    asyncio.run(client.start())
