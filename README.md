# AI Brief Decoder Lite

Chrome-расширение + FastAPI-бэкенд, превращающие вставленный бриф клиента в структурированное summary (цели, результаты, риски, уточняющие вопросы).

## Что это такое

Пользователь вставляет бриф в попап расширения, попап отправляет его на локальный FastAPI-бэкенд, бэкенд прогоняет текст через LLM-провайдера и валидирует вывод по фиксированной схеме, попап рендерит структурированный результат (либо безопасную ошибку). Пайплайн: текст → LLM-провайдер → структурированный JSON (валидируется Pydantic) → UI Chrome-расширения.

Бэкенд сохраняет каждый run (входной текст, сырой вывод провайдера, структурированный результат или безопасную ошибку, статус, таймстампы) в Postgres, поэтому run можно повторно получить по id через `GET /v1/briefs/runs/{run_id}`. По умолчанию используется детерминированный `FakeProvider` - весь проект запускается локально без платного API-ключа; он существует, чтобы каждая ветка успеха/ошибки была воспроизводима по требованию, а не зависела от случайности. Дополнительно реализован `RealProvider` на базе `pydantic_ai` и Gemini (см. "Переход на реальный LLM-провайдер").

## Технологический стек

**Backend**
- FastAPI + Pydantic v2 (валидация запросов/ответов)
- SQLAlchemy (async) + asyncpg + Alembic (Postgres, миграции)
- pytest + pytest-asyncio + httpx (тесты, ASGI transport)
- Docker Compose (postgres, migrate, api)

**Frontend**
- React 18 + TypeScript 5
- WXT (Manifest V3, только popup - без background и content script)
- Tailwind CSS v4
- lucide-react (иконки)
- pnpm

## Предварительные требования

- Docker + Docker Compose
- Node.js LTS + pnpm
- Chrome

## Быстрый старт

### Backend

1. Из корня репозитория скопируйте env-файл, если ещё не сделали: `cp .env.example .env` (дефолты уже настроены для локального Docker, `LLM_PROVIDER=fake`).
2. Поднимите всё: `docker compose up -d`
   Это запустит Postgres, применит Alembic-миграции и поднимет API на `http://localhost:8000`.
3. Проверьте, что всё работает: `curl http://localhost:8000/health` → `{"status":"ok"}`

### Frontend

1. `cd brief-decoder-extension`
2. `pnpm install`
3. `pnpm dev` - запускает dev-сервер WXT и собирает в `.output/chrome-mv3`. Оставьте его работающим.
4. В Chrome откройте `chrome://extensions`, включите **Developer mode**, нажмите **Load unpacked** и выберите `brief-decoder-extension/.output/chrome-mv3`.
5. Кликните по иконке расширения, вставьте бриф, нажмите **Run**.

Для прод-сборки вместо dev: `pnpm build` (тоже кладёт результат в `.output/chrome-mv3`, перезаписывая dev-сборку - после этого нужно перезагрузить расширение в Chrome, чтобы подхватить изменения).

## Тестирование

**Backend** (из корня репозитория; Postgres должен быть поднят — `docker compose up -d postgres`, если ещё не запущен):
```bash
docker compose run --rm --entrypoint pytest migrate -v
```
Запускает тесты в том же Docker-образе, что и API, переопределяя entrypoint сервиса `migrate` на `pytest` — так не нужно настраивать локальное Python-окружение отдельно от контейнеров. Покрывает ветки отказа fake-провайдера, эндпоинты `/v1/briefs/decode` и `/v1/briefs/runs/{id}`, логику Pydantic-валидации и классификации ошибок.

**Frontend** (из `brief-decoder-extension/`):
```bash
pnpm typecheck   # tsc --noEmit
pnpm build       # прод-сборка, падает при ошибках сборки
```
Автоматических тестов для фронтенда в этой версии нет (см. "Что ещё можно было реализовать").

## Переход на реальный LLM-провайдер

По умолчанию `LLM_PROVIDER=fake` - `FakeProvider` покрывает все требуемые сценарии (успех, невалидный JSON, отсутствующее поле, невалидный severity, ошибка провайдера, таймаут), триггерится детерминированно через литеральные маркеры во входном тексте (`__FAKE_PROVIDER_ERROR__` и т.д.), без сети и без API-ключа.

Дополнительно реализован `RealProvider` (`app/providers/real.py`) на базе `pydantic_ai.Agent` с моделью Gemini (`google:gemini-2.5-flash`), выдающий структурированный вывод напрямую в `BriefDecodeResult`. Чтобы включить его:

1. В `.env` установите `LLM_PROVIDER=real` и `GOOGLE_API_KEY=<ваш ключ>`.
2. Пересоберите и перезапустите бэкенд: `docker compose up -d --build api`.
3. Проверьте: `curl -X POST http://localhost:8000/v1/briefs/decode -H "Content-Type: application/json" -d '{"text": "..."}'`

Любое исключение из `agent.run()` (сетевой сбой, невалидный ключ, rate limit) перехватывается и заворачивается в тот же `ProviderError`, что использует `FakeProvider`, - `decode_service` не отличает поведение реального и фейкового провайдера.

## Структура проекта

```
ai_brief_decoder_lite/
├── app/                          # FastAPI-бэкенд
│   ├── api/v1/briefs.py          # роуты
│   ├── services/decode_service.py# оркестрация: вызов провайдера -> валидация -> сохранение
│   ├── providers/                # LLMProvider protocol + FakeProvider + RealProvider
│   ├── repositories/             # доступ к БД для decode runs
│   ├── schemas/brief.py          # Pydantic-модели запросов/ответов
│   └── models/decode_run.py      # SQLAlchemy-модель
├── migrations/                   # Alembic
├── tests/                        # pytest
├── docker-compose.yml
├── Dockerfile
└── brief-decoder-extension/      # Chrome-расширение (WXT + React + Tailwind)
    └── entrypoints/popup/
        ├── App.tsx               # стейт-машина (idle/loading/success/error)
        ├── components/           # BriefForm, ResultView, ErrorView
        └── lib/                  # api.ts (fetch), types.ts (контракт с бэкендом)
```

## Допущения и компромиссы

- **`LLM_PROVIDER=fake` - дефолт, не опция.** Задание требует, чтобы проект запускался локально без платного API-ключа; `docker compose up -d` из Quick start поднимает рабочий end-to-end стек на `FakeProvider` без какой-либо настройки. `RealProvider`/`GOOGLE_API_KEY` - отдельный, необязательный шаг.

- **Бэкенд всегда возвращает HTTP 200 для `/v1/briefs/decode`**, даже при доменных ошибках (невалидный вывод LLM, ошибка провайдера, таймаут). Источник истины - `status`/`error` в теле ответа, не HTTP-статус.
- **`invalid_severity` не может дойти до фронтенда как необработанный случай.** Если бэкенд вернул `status: "succeeded"`, `BriefDecodeResult` уже прошёл Pydantic-валидацию на сервере, поэтому `risks[].severity` гарантированно один из `low`/`medium`/`high`. Фронтенд не обрабатывает неизвестные значения severity.
- **Расширение не имеет персистентности.** `text`/`status`/`response` живут в `useState` внутри компонента попапа и теряются при закрытии попапа - нет `chrome.storage`, нет истории runs в UI, хотя бэкенд их и сохраняет.
- **Нет background или content script.** Попап выполняет fetch напрямую, пока открыт; если пользователь закроет попап посреди запроса, запрос оборвётся вместе с JS-контекстом попапа.
- **Единственный фиксированный URL бэкенда** (`http://localhost:8000`), захардкожен в `lib/api.ts`, а не берётся из переменной окружения.

## Что ещё можно было реализовать

- Добавить rate limiting, авторизацию и поддержку многопользовательского режима.
- Покрыть `RealProvider` тестами и проверить его на реальных ответах модели за пределами happy path (сейчас весь тесты проверяют поведение только через `FakeProvider`).
- Добавить автоматические тесты для фронтенда (Vitest).
- Вынести URL бэкенда в переменную окружения вместо константы.
- Показывать историю runs или список в UI расширения - `GET /runs/{run_id}` есть на бэкенде, но фронтенд его не использует.
