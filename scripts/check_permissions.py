"""
Проверка прав доступа без psql, через psycopg2.
Запуск: python scripts/check_permissions.py --host localhost --db hospital_mis
Параметры ролей/паролей берутся из init.sql.
"""

import argparse
import sys
import os
import psycopg2

ROLES = {
    "admin": "admin_pass",
    "manager": "manager_pass",
    "staff": "staff_pass",
    "readonly": "readonly_pass",
}

# По умолчанию не декодируем проблемные байты
ENCODING = "SQL_ASCII"


def run_query(conn_info, label, sql, fetch=False):
    print(f"=== {label} ({conn_info['user']}) ===")
    try:
        with psycopg2.connect(**conn_info) as conn:
            try:
                conn.set_client_encoding(ENCODING)
            except Exception as e:
                print(f"WARNING: cannot set client_encoding {ENCODING}: {e}")
            with conn.cursor() as cur:
                cur.execute(sql)
                if fetch and cur.description:
                    try:
                        rows = cur.fetchall()
                        print(rows)
                    except Exception as fe:
                        print(f"FETCH ERROR (codec?): {fe!r}")
                conn.commit()
            print("OK")
    except Exception as e:
        print(f"ERROR: {e!r}")
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=5432, type=int)
    parser.add_argument("--db", default="hospital_mis")
    parser.add_argument("--encoding", default="SQL_ASCII", help="client encoding, e.g. SQL_ASCII, UTF8, WIN1251")
    args = parser.parse_args()

    global ENCODING
    ENCODING = args.encoding
    os.environ["PGCLIENTENCODING"] = ENCODING

    def conn_info(user):
        return {
            "host": args.host,
            "port": args.port,
            "dbname": args.db,
            "user": user,
            "password": ROLES[user],
            "options": f"-c client_encoding={ENCODING}",
        }

    # admin
    run_query(conn_info("admin"), "SELECT patients", "SELECT 1;")
    run_query(
        conn_info("admin"),
        "INSERT patient",
        "INSERT INTO patients(full_name,birth_date,phone) VALUES ('Админ Тест','1991-01-01','+79990000001');",
    )
    run_query(conn_info("admin"), "DELETE patient", "DELETE FROM patients WHERE phone='+79990000001';")
    run_query(conn_info("admin"), "DDL create/drop", "CREATE TABLE tmp_check(id int); DROP TABLE tmp_check;")

    # manager
    run_query(conn_info("manager"), "SELECT patients", "SELECT 1;")
    run_query(
        conn_info("manager"),
        "INSERT patient",
        "INSERT INTO patients(full_name,birth_date,phone) VALUES ('Менеджер Тест','1992-02-02','+79990000002');",
    )
    run_query(conn_info("manager"), "UPDATE status", "UPDATE appointments SET status='canceled' WHERE id=1;")
    run_query(
        conn_info("manager"),
        "DELETE patient (ожидается отказ)",
        "DELETE FROM patients WHERE phone='+79990000002';",
    )
    run_query(conn_info("manager"), "DDL create (ожидается отказ)", "CREATE TABLE tmp_mgr(id int);")

    # staff
    run_query(conn_info("staff"), "SELECT appointments", "SELECT 1;")
    run_query(conn_info("staff"), "UPDATE status", "UPDATE appointments SET status='in_progress' WHERE id=1;")
    run_query(
        conn_info("staff"),
        "UPDATE doctor_id (ожидается отказ)",
        "UPDATE appointments SET doctor_id=2 WHERE id=1;",
    )
    run_query(
        conn_info("staff"),
        "INSERT appointment_service",
        "INSERT INTO appointment_services(appointment_id,service_id,quantity) VALUES (1,1,2);",
    )
    run_query(
        conn_info("staff"),
        "DELETE appointment (ожидается отказ)",
        "DELETE FROM appointments WHERE id=1;",
    )

    # readonly
    run_query(conn_info("readonly"), "SELECT services", "SELECT 1;")
    run_query(
        conn_info("readonly"),
        "INSERT patient (ожидается отказ)",
        "INSERT INTO patients(full_name,birth_date,phone) VALUES ('RO','1993-03-03','+79990000003');",
    )
    run_query(
        conn_info("readonly"),
        "UPDATE status (ожидается отказ)",
        "UPDATE appointments SET status='done' WHERE id=1;",
    )
    run_query(
        conn_info("readonly"),
        "DELETE patient (ожидается отказ)",
        "DELETE FROM patients WHERE phone='+79990000003';",
    )


if __name__ == "__main__":
    sys.exit(main())

