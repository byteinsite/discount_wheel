# Deploy on Railway

Пошаговая настройка проекта **Discount Wheel** на [Railway](https://railway.com).

## Архитектура на Railway

| Сервис | Root Directory | Описание |
|--------|----------------|----------|
| **backend** | `backend/` | FastAPI API |
| **frontend** | `frontend/` | React + Nginx (проксирует API) |
| **PostgreSQL** | plugin | База пользователей и спинов |
| **Redis** | plugin (опц.) | Кэш (зарезервировано) |

Mini App в Telegram открывает **публичный URL frontend-сервиса**. Nginx проксирует `/auth`, `/me`, `/spin`, `/result` на backend.

```
Telegram Mini App
       ↓
frontend (HTTPS, Railway)
       ↓ proxy
backend (FastAPI)
       ↓
PostgreSQL
```

## 1. Создать проект

1. [railway.com](https://railway.com) → **New Project** → **Deploy from GitHub repo**
2. Подключите репозиторий `discount_wheel`

## 2. PostgreSQL

1. В проекте: **+ New** → **Database** → **PostgreSQL**
2. Railway автоматически создаст переменную `DATABASE_URL`
3. Backend при старте сам приведёт URL к формату `postgresql+asyncpg://…`

## 3. Backend-сервис

1. **+ New** → **GitHub Repo** → тот же репозиторий
2. **Settings** → **Source** → **Root Directory**: `backend` ← **обязательно**
3. **Settings** → **Build** → убедитесь, что используется **Dockerfile** (config-as-code: `backend/railway.json`)
4. **Settings** → **Networking** → **Generate Domain**
5. **Variables**:

| Переменная | Значение |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | токен от [@BotFather](https://t.me/BotFather) |
| `ALLOW_DEV_AUTH` | `false` |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (Reference) |
| `CORS_ORIGINS` | `https://<ваш-frontend-домен>.up.railway.app` |

> **Reference variables**: в Railway Variables нажмите **Add Reference** и выберите PostgreSQL → `DATABASE_URL`.

5. **Deploy** — healthcheck: `GET /health`

В логах сборки должно быть: **Using Detected Dockerfile** (не Railpack).

Файлы `backend/railway.json` и `backend/railway.toml` принудительно включают Dockerfile builder.

## 4. Frontend-сервис

1. **+ New** → **GitHub Repo** → тот же репозиторий
2. **Settings** → **Source** → **Root Directory**: `frontend` ← **обязательно**
3. **Settings** → **Build** → Dockerfile (`frontend/railway.json`)
4. **Networking** → **Generate Domain** — это URL для Mini App в BotFather
5. **Variables**:

| Переменная | Значение |
|------------|----------|
| `BACKEND_URL` | `https://${{backend.RAILWAY_PUBLIC_DOMAIN}}` |
| `PORT` | `${{PORT}}` (обычно уже есть; Railway подставляет сам) |

> Используйте **Reference** на сервис `backend` → `RAILWAY_PUBLIC_DOMAIN`.  
> Для трафика внутри проекта можно private URL:  
> `http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}`

5. **Deploy** — healthcheck: `GET /`

## 5. Telegram Bot

1. BotFather → **Bot Settings** → **Menu Button** / **Web App**
2. URL: `https://<frontend-домен>.up.railway.app`
3. Убедитесь, что `TELEGRAM_BOT_TOKEN` на backend совпадает с ботом

## 6. Проверка

```bash
# Backend
curl https://<backend>.up.railway.app/health

# Frontend (статика)
curl -I https://<frontend>.up.railway.app/

# API через frontend proxy
curl -X POST https://<frontend>.up.railway.app/auth \
  -H "Content-Type: application/json" \
  -d '{"initData":"..."}'
```

## Переменные окружения (сводка)

### Backend

| Variable | Обязательно | Описание |
|----------|-------------|----------|
| `PORT` | авто (Railway) | Порт uvicorn |
| `DATABASE_URL` | да | Reference на PostgreSQL |
| `TELEGRAM_BOT_TOKEN` | да | Токен бота |
| `ALLOW_DEV_AUTH` | нет | `false` в production |
| `CORS_ORIGINS` | рекомендуется | URL frontend |
| `REDIS_URL` | нет | Reference на Redis |
| `CAMPAIGN_START` | нет | ISO datetime |
| `CAMPAIGN_END` | нет | ISO datetime |

### Frontend

| Variable | Обязательно | Описание |
|----------|-------------|----------|
| `PORT` | авто (Railway) | Порт nginx |
| `BACKEND_URL` | да | URL backend без trailing `/` |

## Локальная разработка

`docker-compose.yml` остаётся для локального запуска и **не используется** Railway напрямую.

```bash
docker compose up --build
# UI: http://localhost:8080
```

## CLI (опционально)

```bash
npm i -g @railway/cli
railway login
railway link

# Backend
cd backend
railway up

# Frontend
cd frontend
railway up
```

## Troubleshooting

### `Railpack could not determine how to build` / `Script start.sh not found`

Railway пытается собрать **весь репозиторий** через Railpack, а не через Dockerfile.

**Исправление:**

1. Откройте сервис → **Settings** → **Source**
2. **Root Directory**:
   - backend-сервис → `backend`
   - frontend-сервис → `frontend`
3. Сохраните и нажмите **Redeploy**
4. В логах сборки должно появиться: `Using Detected Dockerfile`

Если Root Directory уже верный, но Railpack всё равно запускается:

1. Добавьте переменную `NO_CACHE=1` на сервис
2. **Redeploy** ещё раз
3. Проверьте, что в репозитории есть `backend/railway.json` (или `frontend/railway.json`)

> В UI Builder может отображаться «Railpack (Default)» — это нормально.  
> При деплое `railway.json` в Root Directory **переопределяет** UI.

### Прочие проблемы

| Проблема | Решение |
|----------|---------|
| Backend не стартует | Проверьте `DATABASE_URL` reference и логи deploy |
| 502 на `/spin` | Проверьте `BACKEND_URL` на frontend |
| Invalid initData | `TELEGRAM_BOT_TOKEN` и URL Mini App должны быть от одного бота |
| Healthcheck failed | Backend: `/health`; Frontend: `/` — дождитесь cold start (~30–60 с) |

## Стоимость

- Backend + Frontend — два compute-сервиса
- PostgreSQL — отдельный plugin
- Redis — опционально

На бесплатном/trial-плане следите за лимитами Railway.
