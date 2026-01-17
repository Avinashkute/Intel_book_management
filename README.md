# Book Management System - Setup & Run Guide

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** (to clone the repository)

## Quick Start

### 1. Clone & Navigate
```bash
git clone <repository-url>
cd Intel_book_management/backend
```

### 2. Configure Environment
Update `.env` file with your settings:
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://book_app_user:admin@db:5432/book_management
DATABASE_URL_SYNC=postgresql://book_app_user:admin@db:5432/book_management
POSTGRES_USER=book_app_user
POSTGRES_PASSWORD=admin
POSTGRES_DB=book_management

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Model Configuration
LLM_MODEL=groq/llama-3.1-8b-instant
GROQ_API_KEY=your-groq-api-key-here

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

### 3. Run Application
```bash
docker-compose up --build
```

### 4. Access API
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Usage

### Authentication

#### 1. Register User
```bash
POST /auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "user",
  "preferred_genre": "fiction"
}
```

#### 2. Login
```bash
POST /auth/login
{
  "email": "john@example.com",
  "password": "password123"
}
```
Returns: `{"access_token": "...", "token_type": "bearer"}`

#### 3. Use Token
Add to headers: `Authorization: Bearer <access_token>`

### Book Management (Admin Only)

#### Create Book
```bash
POST /books
Authorization: Bearer <admin_token>
{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "genre": "fiction",
  "year_published": "1925"
}
```

#### Get Books
```bash
GET /books
Authorization: Bearer <token>
```

#### Update Book
```bash
PUT /books/{book_id}
Authorization: Bearer <admin_token>
{
  "title": "Updated Title"
}
```

#### Delete Book
```bash
DELETE /books/{book_id}
Authorization: Bearer <admin_token>
```

### Reviews (All Users)

#### Create Review
```bash
POST /books/{book_id}/reviews
Authorization: Bearer <token>
{
  "review_text": "Great book!",
  "rating": 4.5
}
```

#### Get Reviews
```bash
GET /books/{book_id}/reviews
Authorization: Bearer <token>
```

### AI Features

#### Generate Summary
```bash
POST /books/generate-summary
Authorization: Bearer <token>
{
  "title": "Book Title",
  "author": "Author Name",
  "genre": "fiction",
  "year_published": "2023"
}
```

#### Get Book Analytics
```bash
GET /books/{book_id}/analytics
Authorization: Bearer <token>
```
Returns aggregated ratings, sentiment analysis, and rating distribution.

## Configuration Options

### LLM Providers
Change `LLM_MODEL` in `.env`:
- **Groq**: `groq/llama-3.1-8b-instant`
- **OpenAI**: `gpt-4` (requires `OPENAI_API_KEY`)
- **Anthropic**: `claude-3-sonnet-20240229` (requires `ANTHROPIC_API_KEY`)

### Database
- **Host**: Configurable via `DATABASE_URL`
- **User/Password**: Set via `POSTGRES_USER`/`POSTGRES_PASSWORD`
- **Database Name**: Set via `POSTGRES_DB`

### Application
- **Host/Port**: Configurable via `APP_HOST`/`APP_PORT`
- **Log Level**: Set via `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR)

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change APP_PORT in .env
   APP_PORT=8001
   ```

2. **Database Connection Failed**
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up --build
   ```

3. **Permission Denied**
   ```bash
   # On Linux/Mac
   sudo docker-compose up --build
   ```

### Logs
```bash
# View logs
docker-compose logs app
docker-compose logs db

# Follow logs
docker-compose logs -f app
```

### Reset Everything
```bash
# Complete reset
docker-compose down -v
docker system prune -f
docker-compose up --build
```

## Development

### File Structure
```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Configuration & security
│   ├── db/           # Database setup
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── .env              # Environment variables
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

#### Get Recommendations
```bash
GET /books/recommendations/?genre=fiction
Authorization: Bearer <token>
```