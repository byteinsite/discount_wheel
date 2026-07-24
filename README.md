# Discount Wheel — Telegram Mini App

Mini App с колесом скидок: пользователь открывает приложение в Telegram, крутит колесо один раз и получает персональную скидку с промокодом. Результат всегда считает **сервер**.

## Стек

| Слой | Технологии |
|------|------------|
| Frontend | React, TypeScript, Vite, Telegram WebApp SDK, CSS |
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL |
| Infra | Docker Compose, Nginx, Redis (опционально), Railway |

## Структура

```
project/
  backend/
    app/
      api/          # HTTP-роуты
      auth/         # проверка Telegram initData
      db/           # SQLAlchemy session
      models/       # User, Spin
      services/     # призы, spin
      main.py
  frontend/
    src/
      components/   # Wheel, Button
      pages/        # Home
      api.ts
  docker-compose.yml
```

## API

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/auth` | Проверка `initData`, создание пользователя |
| `GET` | `/me` | Профиль и флаг `spinned` |
| `POST` | `/spin` | Одно вращение → `discount`, `promo`, `angle` |
| `GET` | `/result` | Результат, если уже крутил |
| `GET` | `/health` | Healthcheck |

Авторизация защищённых эндпоинтов: заголовок

```http
Authorization: tma <initData>
```

или `X-Telegram-Init-Data`.

Пример ответа `POST /spin`:

```json
{
  "discount": 20,
  "promo": "WELCOME20-A1B2C3",
  "angle": 2010
}
```

`angle` нужен только для анимации на клиенте. Приз выбирается на сервере по весам:

| Скидка | Вес |
|--------|-----|
| 5% | 30% |
| 10% | 25% |
| 15% | 20% |
| 20% | 12% |
| 25% | 8% |
| 30% | 5% |

Повторный `POST /spin` → `409 Already spun`. Уникальный constraint на `spins.user_id` защищает от гонок.

## Быстрый старт (Docker)

1. Скопируйте env:

```bash
cp .env.example .env
```

2. Укажите `TELEGRAM_BOT_TOKEN` от [@BotFather](https://t.me/BotFather).

3. Запустите:

```bash
docker compose up --build
```

- Mini App: http://localhost:8080  
- API docs: http://localhost:8000/docs  

## Деплой на Railway

Production-деплой: два сервиса (`backend/`, `frontend/`) + PostgreSQL plugin.

Подробная инструкция: **[RAILWAY.md](./RAILWAY.md)**

Кратко:

1. PostgreSQL plugin → `DATABASE_URL` через Reference на backend
2. Сервис **backend** (Root Directory: `backend`) — `TELEGRAM_BOT_TOKEN`, `ALLOW_DEV_AUTH=false`
3. Сервис **frontend** (Root Directory: `frontend`) — `BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}`
4. Публичный URL frontend → Web App URL в BotFather

Docker-образы слушают `$PORT` (Railway) и готовы к healthcheck.

## Локальная разработка

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# PostgreSQL должен быть доступен
set DATABASE_URL=postgresql+asyncpg://wheel:wheel@localhost:5432/discount_wheel
set TELEGRAM_BOT_TOKEN=...
set ALLOW_DEV_AUTH=true
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite проксирует API на `localhost:8000`. При `ALLOW_DEV_AUTH=true` можно открыть UI в браузере без Telegram (создаётся dev-пользователь).

## Настройка бота в Telegram

1. Создайте бота в BotFather, скопируйте token в `.env`.
2. Разверните приложение на **HTTPS** (Telegram требует HTTPS для Mini App).
3. В BotFather → Bot Settings → Menu Button / Web App укажите URL, например `https://your-domain.com`.
4. Либо отправьте кнопку через Bot API:

```json
{
  "text": "Крутить колесо",
  "web_app": { "url": "https://your-domain.com" }
}
```

Для локальной отладки внутри Telegram удобны туннели ([ngrok](https://ngrok.com/), Cloudflare Tunnel) с HTTPS на порт `8080`.

## Модели

**User** — `id`, `telegram_id`, `username`, `first_name`, `last_name`, `created_at`  
**Spin** — `id`, `user_id` (unique), `discount`, `promo_code`, `angle`, `created_at`

## Дальнейшие шаги

- Окно акции: `CAMPAIGN_START` / `CAMPAIGN_END` в `.env`
- Админ-панель для весов призов
- Интеграция промокодов с CRM / магазином
- Аналитика запусков и использованных скидок
- TLS-терминация (Let's Encrypt / reverse proxy перед Compose)
