# API Documentation

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Authentication

#### POST /auth/register

Register a new user

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "agent",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### POST /auth/login

Login with email and password

**Request Body:**

```form-data
username: user@example.com
password: securepassword123
```

**Response:**

```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

#### POST /auth/refresh

Refresh access token

**Request Body:**

```json
{
  "refresh_token": "eyJhbGc..."
}
```

#### GET /auth/me

Get current user info (requires authentication)

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "agent"
}
```

### Businesses

#### GET /businesses

Get all businesses for current user

#### POST /businesses

Create a new business

#### GET /businesses/{id}

Get business details

#### PUT /businesses/{id}

Update business

#### DELETE /businesses/{id}

Delete business

### WhatsApp Numbers

#### GET /whatsapp

List all WhatsApp numbers

#### POST /whatsapp

Connect a new WhatsApp number

#### GET /whatsapp/{id}

Get WhatsApp number details

#### DELETE /whatsapp/{id}

Disconnect WhatsApp number

### Bots

#### GET /bots

List all bots

#### POST /bots

Create a new bot

#### GET /bots/{id}

Get bot details

#### PUT /bots/{id}

Update bot

#### DELETE /bots/{id}

Delete bot

#### GET /bots/{id}/scenarios

Get bot scenarios

#### POST /bots/{id}/scenarios

Create bot scenario

### Customers

#### GET /customers

List all customers

#### POST /customers

Create customer

#### GET /customers/{id}

Get customer details

#### PUT /customers/{id}

Update customer

#### DELETE /customers/{id}

Delete customer

### Conversations

#### GET /conversations

List all conversations

#### GET /conversations/{id}

Get conversation details

#### POST /conversations/{id}/messages

Send message

#### PUT /conversations/{id}/assign

Assign conversation to agent

### Deals

#### GET /deals

List all deals

#### POST /deals

Create deal

#### GET /deals/{id}

Get deal details

#### PUT /deals/{id}

Update deal

#### DELETE /deals/{id}

Delete deal

### Broadcasts

#### GET /broadcasts

List all broadcasts

#### POST /broadcasts

Create broadcast campaign

#### GET /broadcasts/{id}

Get broadcast details

#### POST /broadcasts/{id}/send

Send broadcast

#### DELETE /broadcasts/{id}

Delete broadcast

### Webhooks

#### GET /webhooks/whatsapp

Verify WhatsApp webhook

#### POST /webhooks/whatsapp

Receive WhatsApp messages

## WebSocket Events

Connect to WebSocket:

```javascript
const socket = io("ws://localhost:8000");
```

### Events

#### connect

Client connected to server

#### join_room

Join a conversation room

```javascript
socket.emit("join_room", { room: "conversation_123" });
```

#### new_message

Receive new message

```javascript
socket.on("new_message", (data) => {
  console.log(data);
});
```

#### send_message

Send message to room

```javascript
socket.emit("send_message", {
  room: "conversation_123",
  message: "Hello",
});
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:

- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## Rate Limiting

API requests are limited to 60 requests per minute per IP address.

## Pagination

List endpoints support pagination:

```
GET /customers?skip=0&limit=20
```

Response includes total count:

```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```
