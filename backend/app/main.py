"""
FastAPI Main Application
WhatsApp Bot & CRM Platform
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import socketio
import time

from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.api.v1 import api_router

# Create database tables
base.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="WhatsApp Bot & CRM Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (production)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Socket.IO for real-time communication
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.CORS_ORIGINS,
    logger=True,
    engineio_logger=True
)
socket_app = socketio.ASGIApp(sio, app)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "WhatsApp Bot & CRM Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('connection_response', {'data': 'Connected'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join_room(sid, data):
    """Join a chat room"""
    room = data.get('room')
    await sio.enter_room(sid, room)
    await sio.emit('joined_room', {'room': room}, room=sid)

@sio.event
async def leave_room(sid, data):
    """Leave a chat room"""
    room = data.get('room')
    await sio.leave_room(sid, room)
    await sio.emit('left_room', {'room': room}, room=sid)

@sio.event
async def send_message(sid, data):
    """Send message to room"""
    room = data.get('room')
    message = data.get('message')
    await sio.emit('new_message', {
        'room': room,
        'message': message,
        'sender': sid
    }, room=room)

# Startup event
@app.on_event("startup")
async def startup_event():
    print(f" {settings.PROJECT_NAME} v{settings.VERSION} started")
    print(f" Documentation: {settings.BACKEND_URL}/docs")
    print(f" WebSocket enabled")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print(f" {settings.PROJECT_NAME} shutting down")

# Export socket_app for uvicorn
app = socket_app
