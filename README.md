# Курсовой проект: Система медицинского учёта для больницы (PostgreSQL + FastAPI)

## Структура
- `db/init.sql` — создание БД, таблиц, индексов, ролей, тестовых данных.
- `app/` — каркас FastAPI (SQLAlchemy модели, схемы Pydantic, CRUD, эндпоинты).
- `requirements.txt` — зависимости.
- `scripts/` — примеры бэкапа/восстановления (bash, адаптируйте под Windows или cron/systemd).

## Быстрый старт
1) Установите PostgreSQL 14+ и создайте пользователя `postgres` (или измените строки подключения).
2) Выполните скрипт:
```bash
psql -U postgres -f db/init.sql
```
3) Установите зависимости и запустите API:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
4) Проверьте:
```bash
curl http://localhost:8000/patients
```

## ER и бизнес-процессы
- Сущности: `patients`, `doctors`, `appointments`, `services`, `appointment_services` (M:N), аудит/авторизация можно расширить.
- Связи: patient 1:N appointments; doctor 1:N appointments; appointments M:N services через appointment_services.
- Процессы: регистрация пациента, запись на приём, добавление услуг, изменение статуса, просмотр истории и фильтрация по врачу/пациенту/дате.

## Роли и права (GRANT/REVOKE)
- `admin` — все привилегии, в т.ч. DELETE/DDL.
- `manager` — SELECT/INSERT/UPDATE по справочникам и приёмам.
- `staff` — SELECT всего, UPDATE статуса/заметок приёмов, INSERT/UPDATE услуг приёма.
- `readonly` — только SELECT.
Удаление запрещено для всех, кроме admin.

## Проверка API (curl)
```bash
curl -X GET http://localhost:8000/patients
curl -X POST http://localhost:8000/patients -H "Content-Type: application/json" \
  -d '{"full_name":"Тест","birth_date":"1995-01-01","phone":"+70005556677"}'
curl -X POST http://localhost:8000/appointments -H "Content-Type: application/json" \
  -d '{"patient_id":1,"doctor_id":1,"scheduled_at":"2025-12-10T09:00:00","status":"scheduled","services":[{"service_id":1,"quantity":1}]}'
curl -X GET "http://localhost:8000/appointments?doctor_id=1"
```

## Бэкапы
- Полный (ежедневно): `pg_dump -U postgres -F c -d hospital_mis -f /backups/full_$(date +%F).dump`
- Инкрементный (каждые 4 ч) через WAL-архив (`archive_mode=on`, `archive_command='test ! -f /backups/wal/%f && cp %p /backups/wal/%f'`).
- Восстановление: `pg_restore -U postgres -d hospital_mis_restored /backups/full_YYYY-MM-DD.dump` и при необходимости WAL для PITR.

## Репликация (streaming master-slave)
- На мастере: `wal_level=replica`, `max_wal_senders=10`, `hot_standby=on`; `pg_hba.conf` разрешает роль `replica`.
- Роль: `CREATE ROLE replica WITH REPLICATION LOGIN ENCRYPTED PASSWORD 'replica_pass';`
- На слейве: `pg_basebackup -h master_host -D /var/lib/postgresql/data -U replica -P -R`
- Проверка задержки: `SELECT now() - pg_last_xact_replay_timestamp();`
- Чтение со слейва: подключаться к узлу-реплике под `readonly`.

## Структура отчёта (шаблон)
- Титульный лист.
- Введение: цель, задачи, предметная область.
- Проектирование БД: ER-диаграмма, нормализация до 3НФ, схема, `db/init.sql`.
- Права доступа: роли, GRANT/REVOKE, сценарии проверки.
- API: код (`app/`), CRUD, примеры запросов/ответов.
- Тестирование: статусы, валидация, фильтрация, ошибки.
- Бэкапы и репликация: конфигурация, команды, проверка восстановления/задержки.
- Заключение: выводы, проблемы, решения.
- Приложения: исходники, конфиги.

