-- Создание базы и подключение
CREATE DATABASE hospital_mis;
\c hospital_mis;

-- Таблицы
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    birth_date DATE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    specialty VARCHAR(120) NOT NULL,
    room VARCHAR(20),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    duration_minutes INT NOT NULL CHECK (duration_minutes > 0)
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INT NOT NULL REFERENCES doctors(id) ON DELETE RESTRICT,
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(30) NOT NULL CHECK (status IN ('scheduled','in_progress','done','canceled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT now()
);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_appointments_scheduled_at ON appointments(scheduled_at);

CREATE TABLE appointment_services (
    appointment_id INT NOT NULL REFERENCES appointments(id) ON DELETE CASCADE,
    service_id INT NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    PRIMARY KEY (appointment_id, service_id)
);

-- Тестовые данные
INSERT INTO patients (full_name, birth_date, phone, email) VALUES
('Иван Петров', '1985-04-12', '+70001112233', 'ivan@example.com'),
('Мария Сидорова', '1990-09-30', '+70002223344', 'maria@example.com');

INSERT INTO doctors (full_name, specialty, room, phone) VALUES
('д-р Смирнов', 'Терапевт', '101', '+70009998877'),
('д-р Кузнецова', 'Кардиолог', '202', '+70006665544');

INSERT INTO services (name, price, duration_minutes) VALUES
('Консультация терапевта', 1500, 30),
('Консультация кардиолога', 2000, 40),
('ЭКГ', 1200, 20);

INSERT INTO appointments (patient_id, doctor_id, scheduled_at, status, notes) VALUES
(1, 1, now() + interval '1 day', 'scheduled', 'Первичный приём'),
(2, 2, now() + interval '2 days', 'scheduled', 'Жалобы на боль в сердце');

INSERT INTO appointment_services (appointment_id, service_id, quantity) VALUES
(1, 1, 1),
(2, 2, 1),
(2, 3, 1);

-- Роли и привилегии
CREATE ROLE admin NOINHERIT LOGIN PASSWORD 'admin_pass';
CREATE ROLE manager NOINHERIT LOGIN PASSWORD 'manager_pass';
CREATE ROLE staff NOINHERIT LOGIN PASSWORD 'staff_pass';
CREATE ROLE readonly NOINHERIT LOGIN PASSWORD 'readonly_pass';

GRANT CONNECT ON DATABASE hospital_mis TO admin, manager, staff, readonly;
GRANT USAGE ON SCHEMA public TO admin, manager, staff, readonly;

-- Полные права админу
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Менеджер: справочники и приёмы
GRANT SELECT, INSERT, UPDATE ON patients, doctors, services, appointments, appointment_services TO manager;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO manager;

-- Staff: чтение + обновление статусов приёмов и услуг
GRANT SELECT ON patients, doctors, services, appointments, appointment_services TO staff;
GRANT UPDATE(status, notes) ON appointments TO staff;
GRANT INSERT, UPDATE ON appointment_services TO staff;

-- Только чтение
GRANT SELECT ON patients, doctors, services, appointments, appointment_services TO readonly;

-- Запрет удаления для всех, кроме admin
REVOKE DELETE ON ALL TABLES IN SCHEMA public FROM manager, staff, readonly;

