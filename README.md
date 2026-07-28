# Payment Processing Service

Сервис обработки операций оплаты через внешний провайдер.

Особенности:

* асинхронная отправка платежей через worker;
* сохранение намерения отправки до вызова внешнего провайдера;
* идемпотентность запросов;
* обработка повторных и конкурентных submit;
* обработка квитанций от провайдера;
* восстановление незавершённых операций после перезапуска.

## Технологии

* Python 3.14
* FastAPI
* PostgreSQL
* SQLAlchemy Async
* Alembic
* Docker Compose
* poetry

## Запуск проекта

### 1. Клонирование

```bash
git clone https://github.com/marich1983/ModuleBankTest
cd ModuleBankTest
```

### 2. Запуск через Docker Compose

```bash
docker compose up --build
```

После запуска:

API доступен по адресу:

```
http://localhost:8080
```

Проверка состояния сервиса:

```bash
curl http://localhost:8080/health
```

Ожидаемый ответ:

```json
{
  "status": "ok"
}
```

## Миграции базы данных

Миграции применяются автоматически при запуске контейнера через entrypoint.

При старте сервиса выполняется:

```bash
alembic upgrade head
```

После успешного применения миграций запускается API-сервис.

Для запуска проекта достаточно выполнить:

```bash
docker compose up --build
```


## API

### Создание операции

```http
POST /operations
Content-Type: application/json
```

Пример запроса:

```bash
curl -X POST http://localhost:8080/operations \
-H "Content-Type: application/json" \
-d '{
  "operationId": "operation-123",
  "amount": "1000.00",
  "currency": "RUB",
  "description": "Оплата заказа"
}'
```

Пример тела запроса:

```json
{
  "operationId": "operation-123",
  "amount": "1000.00",
  "currency": "RUB",
  "description": "Оплата заказа"
}
```

Ответ:

```json
{
  "operationId": "operation-123",
  "amount": "1000.00",
  "currency": "RUB",
  "description": "Оплата заказа",
  "status": "CREATED",
  "providerPaymentId": null
}
```

`operationId` является уникальным идентификатором операции и используется для:

* формирования `Idempotency-Key` при вызове внешнего провайдера;
* формирования `X-Correlation-ID`;
* защиты от повторной отправки одного платежа.


---

### Подтверждение операции

```
POST /operations/{id}/submit
```

Пример:

```bash
curl -X POST \
http://localhost:8080/operations/{id}/submit
```

После submit:

1. операция блокируется от конкурентных изменений;
2. сохраняется событие отправки;
3. worker отправляет запрос внешнему провайдеру.

---

### Получение операции

```
GET /operations/{id}
```

Пример:

```bash
curl http://localhost:8080/operations/{id}
```

---

### Получение истории событий

```
GET /operations/{id}/events
```

Пример:

```bash
curl http://localhost:8080/operations/{id}/events
```

---

### Приём квитанции провайдера

```
POST /receipts
```

Пример:

```bash
curl -X POST http://localhost:8080/receipts \
-H "Content-Type: application/json" \
-d '{
  "operationId": "operation-123",
  "amount": "1000.00",
  "currency": "RUB"
}'
```

## Полный сценарий

### 1. Создать операцию

```bash
POST /operations
```


### 2. Отправить операцию на обработку

```bash
POST /operations/{id}/submit
```

Сервис сохраняет намерение отправки.

До вызова провайдера создаётся событие:

```
REQUESTED
```

---

### 3. Worker вызывает провайдера

При вызове используются заголовки:

```
Idempotency-Key: {operationId}
X-Correlation-ID: {operationId}
```

Повторная отправка использует тот же `Idempotency-Key`.

---

### 4. Получить квитанцию

Провайдер отправляет:

```
POST /receipts
```

Сервис:

* проверяет операцию;
* проверяет повтор квитанции;
* обновляет статус;
* сохраняет событие.

---

### 5. Проверить результат

```bash
GET /operations/{id}
```

и

```bash
GET /operations/{id}/events
```

---

## Идемпотентность

Гарантии сервиса:

* повторный `submit` не создаёт новый платёж;
* одинаковый `Idempotency-Key` используется для повторных вызовов провайдера;
* сетевые ошибки не приводят к созданию второго платежа;
* повторная квитанция не изменяет уже завершённую операцию;
* конфликтующие квитанции фиксируются отдельно.

## Восстановление после перезапуска

При старте worker проверяет незавершённые события в базе данных и продолжает обработку.

PostgreSQL используется как постоянное хранилище, поэтому состояние операций сохраняется после перезапуска контейнеров.

## Остановка проекта

```bash
docker compose down
```

Удаление контейнеров вместе с данными:

```bash
docker compose down -v
```
