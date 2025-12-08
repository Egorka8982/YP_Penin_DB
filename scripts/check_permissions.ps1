# Проверка прав доступа для ролей admin, manager, staff, readonly
# Требуется установленный psql в PATH или укажите полный путь в $PsqlPath.

Param(
    [string]$DbName = "hospital_mis",
    [string]$DbHost = "localhost",
    [string]$PsqlPath = "psql"  # можно указать полный путь к psql.exe
)

function Run-Test {
    param([string]$User, [string]$Password, [string]$Sql, [string]$Label)
    Write-Host "=== $Label ($User) ==="
    $cmd = "$PsqlPath -h $DbHost -U $User -d $DbName -c `"$Sql`""
    $env:PGPASSWORD = $Password
    try {
        Invoke-Expression $cmd
    } catch {
        Write-Host "ERROR: $_"
    }
    Write-Host ""
}

# Admin: всё должно работать
Run-Test -User "admin" -Password "admin_pass" -Sql "SELECT count(*) FROM patients;" -Label "SELECT patients"
Run-Test -User "admin" -Password "admin_pass" -Sql "INSERT INTO patients(full_name,birth_date,phone) VALUES ('Админ Тест','1991-01-01','+79990000001');" -Label "INSERT patient"
Run-Test -User "admin" -Password "admin_pass" -Sql "DELETE FROM patients WHERE phone='+79990000001';" -Label "DELETE patient"
Run-Test -User "admin" -Password "admin_pass" -Sql "CREATE TABLE tmp_check(id int); DROP TABLE tmp_check;" -Label "DDL create/drop"

# Manager: INSERT/UPDATE разрешены, DELETE/DDL запрещены
Run-Test -User "manager" -Password "manager_pass" -Sql "SELECT count(*) FROM patients;" -Label "SELECT patients"
Run-Test -User "manager" -Password "manager_pass" -Sql "INSERT INTO patients(full_name,birth_date,phone) VALUES ('Менеджер Тест','1992-02-02','+79990000002');" -Label "INSERT patient"
Run-Test -User "manager" -Password "manager_pass" -Sql "UPDATE appointments SET status='canceled' WHERE id=1;" -Label "UPDATE status"
Run-Test -User "manager" -Password "manager_pass" -Sql "DELETE FROM patients WHERE phone='+79990000002';" -Label "DELETE patient (ожидается отказ)"
Run-Test -User "manager" -Password "manager_pass" -Sql "CREATE TABLE tmp_mgr(id int);" -Label "DDL create (ожидается отказ)"

# Staff: чтение; UPDATE только status/notes; INSERT/UPDATE в appointment_services; DELETE/DDL запрещены
Run-Test -User "staff" -Password "staff_pass" -Sql "SELECT count(*) FROM appointments;" -Label "SELECT appointments"
Run-Test -User "staff" -Password "staff_pass" -Sql "UPDATE appointments SET status='in_progress' WHERE id=1;" -Label "UPDATE status"
Run-Test -User "staff" -Password "staff_pass" -Sql "UPDATE appointments SET doctor_id=2 WHERE id=1;" -Label "UPDATE doctor_id (ожидается отказ)"
Run-Test -User "staff" -Password "staff_pass" -Sql "INSERT INTO appointment_services(appointment_id,service_id,quantity) VALUES (1,1,2);" -Label "INSERT appointment_service"
Run-Test -User "staff" -Password "staff_pass" -Sql "DELETE FROM appointments WHERE id=1;" -Label "DELETE appointment (ожидается отказ)"

# Readonly: только SELECT
Run-Test -User "readonly" -Password "readonly_pass" -Sql "SELECT count(*) FROM services;" -Label "SELECT services"
Run-Test -User "readonly" -Password "readonly_pass" -Sql "INSERT INTO patients(full_name,birth_date,phone) VALUES ('RO','1993-03-03','+79990000003');" -Label "INSERT patient (ожидается отказ)"
Run-Test -User "readonly" -Password "readonly_pass" -Sql "UPDATE appointments SET status='done' WHERE id=1;" -Label "UPDATE status (ожидается отказ)"
Run-Test -User "readonly" -Password "readonly_pass" -Sql "DELETE FROM patients WHERE phone='+79990000003';" -Label "DELETE patient (ожидается отказ)"
