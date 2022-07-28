import secrets
from functools import wraps
import sqlite3
import datetime


def create_connect(func):
    """Decorator create/commit/close connection to database """

    @wraps(func)
    def _con(*args, **kwargs):
        connect = sqlite3.connect('modules/database.db', check_same_thread=False)
        cursor = connect.cursor()
        result = func(cursor, *args, **kwargs)
        connect.commit()
        connect.close()
        return result

    return _con


# Create tables in database
@create_connect
def create_table_all_users(cursor):
    """Create table all_users in database"""
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS all_users (
     id INTEGER PRIMARY KEY,
     mail TEXT UNIQUE,
     password_hash TEXT,
     nickname TEXT,
     account_status TEXT DEFAULT active,
     salt TEXT,
     first_reg DATETIME,
     lust_activity DATETIME)''')
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS users_data (
         id INTEGER PRIMARY KEY,
         users_id INTEGER UNIQUE,
         email_confirm_cod INTEGER,
         email_confirm_dead_time DATETIME)''')


@create_connect
def create_table_tokens(cursor):
    """Create table all_users in database"""
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS tokens (
     id INTEGER PRIMARY KEY,
     user_id INTEGER,
     secret_hash TEXT, 
     token TEXT,
     status TEXT,
     dead_time DATETIME,
     create_time DATETIME)''')


# Work with user database methods
@create_connect
def get_id_by_auth(cursor, auth_token: str):
    """Get account id by auth token"""
    if ':' not in auth_token:
        return '[]', '[]'
    _secret = str(auth_token.split(':')[0])
    user_auth = str(auth_token.split(':')[1])
    cursor.execute(f'SELECT * FROM tokens WHERE "token" = (?) AND "status" = "active"', (user_auth,))
    data = cursor.fetchall()
    if str(data) != '[]':
        cursor.execute(f'SELECT * FROM all_users WHERE "id" = (?)', (data[0][1],))
        user_data = cursor.fetchall()
        return data[0][1], user_data[0][4]
    else:
        return '[]', '[]'


@create_connect
def get_token_status(cursor, auth_token: str):
    """Get infor about token actuality"""
    cursor.execute(f'SELECT id FROM all_users WHERE "auth_token" = "{auth_token}"')
    data = cursor.fetchall()
    return data


@create_connect
def get_user_by_token(cursor, user_id: int):
    """Get infor about token actuality"""
    cursor.execute(f'SELECT mail, nickname FROM all_users WHERE "id" = {user_id}')
    data = cursor.fetchall()
    return data


@create_connect
def get_user_status(cursor, users_id: int):
    """Get infor about token actuality"""
    cursor.execute(f'SELECT email_confirm_cod FROM users_data WHERE "users_id" = (?)', (users_id,))
    data = cursor.fetchall()
    return data


@create_connect
def create_table_user_log(cursor, user_id: int):
    """Create user log table in database"""
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS log{user_id} (
     id INTEGER PRIMARY KEY,
     log_text TEXT,
     data DATETIME)''')


@create_connect
def create_table_user_projects(cursor, user_id: int):
    """Create user's all projects table in database by user id"""
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS all_projects{user_id} (
     id INTEGER PRIMARY KEY,
     project_name TEXT DEFAULT Project,
     description TEXT,
     work_time INTEGER DEFAULT 0,
     money INTEGER DEFAULT 0,
     currency TEXT DEFAULT "USD",
     create_data DATETIME,
     lust_active DATETIME)''')


@create_connect
def create_table_users_tasks(cursor, user_id: int):
    """Create user's all projects table in database by user id"""
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS project_task{user_id} (
     id INTEGER PRIMARY KEY,
     main_project_id INTEGER,
     name TEXT,
     description TEXT,
     work_time INTEGER DEFAULT 0,
     money INTEGER DEFAULT 0,
     money_type TEXT DEFAULT "part",
     create_data DATETIME,
     lust_active DATETIME)''')


@create_connect
def create_user_project_timework_table(cursor, user_id: int):
    """Create user's all projects table in database by user id"""
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS timework{user_id} (
     id INTEGER PRIMARY KEY,
     project_id INTEGER,
     task_id INTEGER,
     start DATETIME,
     finish DATETIME,
     time_delta INTEGER,
     data DATETIME)''')


@create_connect
def get_user_auth(cursor, mail: str, password: str):
    """Get user auth token"""
    cursor.execute(f'SELECT auth_token FROM all_users WHERE "mail" = "{mail}" AND "password" = "{password}"')
    data = cursor.fetchall()
    if str(data) == "[]":
        return False
    return data


@create_connect
def get_user_id_by_email(cursor, email: str, password: str):
    """Get user id by email and password"""
    cursor.execute(f'SELECT * FROM all_users WHERE "mail" = "{email}" AND "password_hash" = "{password}"')
    data = cursor.fetchall()
    if str(data) == "[]":
        return False
    return data[0][0]


@create_connect
def find_email(cursor, mail: str):
    """Find user mail in database"""
    try:
        cursor.execute(f'SELECT id FROM all_users WHERE "mail" = "{mail}"')
        data = cursor.fetchall()
        return data
    except:
        return '[]'


def create_user_account(mail: str, hash_password: str, salt: str, nickname: str):
    """Create a new account by """
    connect = sqlite3.connect('modules/database.db', check_same_thread=False)
    cursor = connect.cursor()
    date = datetime.datetime.now()
    try:
        cursor.execute(f"INSERT OR IGNORE INTO all_users VALUES (?,?,?,?,?,?,?,?)",
                       (None, mail, hash_password, nickname, "need_email", salt, date, date))
        connect.commit()
        cursor.execute(f'SELECT id FROM all_users WHERE "first_reg" = (?)', (date,))
        data = cursor.fetchall()
        if str(data) == '[]':
            return False
        else:
            email_cod = str(secrets.token_hex(2))
            cursor.execute(f"INSERT OR IGNORE INTO users_data VALUES (?,?,?,?)",
                           (None, data[0][0], email_cod, date))
            connect.commit()
            return True, data[0][0], email_cod
    except Exception as _ex:
        print("[INFORMATION] ERROR in db", _ex)
        return False, False, False
    finally:
        connect.close()


def user_create_project(user_id: int, name: str, description: str):
    """User create a new project"""
    connect = sqlite3.connect('modules/database.db', check_same_thread=False)
    cursor = connect.cursor()
    data = datetime.datetime.now()
    try:
        cursor.execute(f"INSERT OR IGNORE INTO all_projects{user_id} VALUES (?,?,?,?,?,?,?,?)",
                       (None, name, description, '0', 0, "USD", data, data))
        connect.commit()
        cursor.execute(f'SELECT id FROM all_projects{user_id} WHERE "create_data" = "{data}"')
        data = cursor.fetchall()[0][0]
        connect.close()
        return data
    except Exception as _ex:
        print("[INFORMATION] ERROR in db", _ex)
        return False


def user_create_project_task(user_id: int, project_id: int, name: str, description: str):
    """User create a new project task with main project with id"""
    connect = sqlite3.connect('modules/database.db', check_same_thread=False)
    cursor = connect.cursor()
    data = datetime.datetime.now()
    try:
        cursor.execute(f"INSERT OR IGNORE INTO project_task{user_id} VALUES (?,?,?,?,?,?,?,?,?)",
                       (None, project_id, name, description, 0, 0, 'part', data, data))
        connect.commit()
        cursor.execute(f'SELECT id FROM project_task{user_id} WHERE "create_data" = "{data}"')
        data = cursor.fetchall()[0][0]
        connect.close()
        return data
    except Exception as _ex:
        print("[INFORMATION] ERROR in db", _ex)
        return False


def create_task_worktime_session(user_id: int, project_id: int, task_id: int, start: str, end: str,
                                 time_delta: int):
    """User create a new worktime session log with task id and main project id"""
    connect = sqlite3.connect('modules/database.db', check_same_thread=False)
    cursor = connect.cursor()
    data = datetime.datetime.now()
    try:
        cursor.execute(f"INSERT OR IGNORE INTO timework{user_id} VALUES (?,?,?,?,?,?,?)",
                       (None, project_id, task_id, start, end, time_delta, data))

        cursor.execute(f"UPDATE all_projects{user_id} SET lust_active=(?) WHERE id=(?)",
                       (data, project_id))
        connect.commit()
        cursor.execute(f'SELECT id FROM timework{user_id} WHERE "data" = "{data}"')

        data = cursor.fetchall()[0][0]
        # connect.close()
        return data
    except Exception as _ex:
        print("[INFORMATION] ERROR in db", _ex)
        return False


@create_connect
def create_auth_token(cursor, user_id: int, auth_token: str, secret_hash: str, status: str, dead_time: str,
                      creat_time: str):
    """Create user's token"""
    cursor.execute(f"INSERT OR IGNORE INTO tokens VALUES (?,?,?,?,?,?,?)",
                   (None, user_id, secret_hash, auth_token, status, dead_time, creat_time))


@create_connect
def grab_all_my_projects(cursor, user_id: int):
    """Get all user's projects"""
    cursor.execute(f'SELECT * FROM all_projects{user_id}')
    data = cursor.fetchall()
    return data


@create_connect
def grab_my_projects_offset(cursor, user_id: int, offset: int = 0, limit: int = 3):
    """Get all user's projects"""
    cursor.execute(f'SELECT * FROM all_projects{user_id} ORDER BY id LIMIT {limit} OFFSET {offset}')
    data = cursor.fetchall()
    return data


@create_connect
def get_project_by_id(cursor, user_id: int, project_id: int):
    """Get user's project data by id"""
    cursor.execute(f'SELECT * FROM all_projects{user_id} WHERE id=(?)', (project_id,))
    data = cursor.fetchall()
    return data


@create_connect
def get_project_task_by_id(cursor, user_id: int, project_task_id: int):
    """Get user's project task data by id"""
    cursor.execute(f'SELECT * FROM project_task{user_id} WHERE id=(?)', (project_task_id,))
    data = cursor.fetchall()
    return data


@create_connect
def grab_all_my_project_tasks(cursor, user_id: int):
    """Get all user's project tasks"""
    cursor.execute(f'SELECT * FROM project_task{user_id}')
    data = cursor.fetchall()
    return data


@create_connect
def all_tasks_of_one_project(cursor, user_id: int, project_id: int):
    """Find All tasks of one project with id"""
    cursor.execute(f'SELECT * FROM project_task{user_id} WHERE main_project_id=(?)', (project_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_project_worktime_logs(cursor, user_id: int, project_id: int):
    """Find All worktime sessions logs of one project with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE project_id=(?)', (project_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_task_worktime_logs(cursor, user_id: int, task_id: int):
    """Find All worktime sessions logs of one task with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE task_id=(?)', (task_id,))
    data = cursor.fetchall()
    return data


@create_connect
def get_worktime_log_by_id(cursor, user_id: int, session_log_id: int):
    """Get worktime sessions log with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE id=(?)', (session_log_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_worktime_logs_of_project(cursor, user_id: int, project_id: int):
    """Get worktime sessions log of project with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE project_id=(?)', (project_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_project_tasks_separately_price(cursor, user_id: int, project_id: int):
    """Get tasks with money type "separately" of project with id"""
    cursor.execute(f'SELECT * FROM project_task{user_id} WHERE main_project_id=(?) AND money_type="separately"',
                   (project_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_project_tasks_part_price(cursor, user_id: int, project_id: int):
    """Get all tasks with money type "part" of project with id"""
    cursor.execute(f'SELECT * FROM project_task{user_id} WHERE main_project_id=(?) AND money_type="part"',
                   (project_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_worktime_logs_of_project_in_time(cursor, user_id: int, project_id: int, start: str, end: str):
    """Get worktime sessions log of project with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE project_id=(?) AND '
                   f'(start BETWEEN "{start}" AND "{end}")', (project_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_worktime_logs_of_task(cursor, user_id: int, task_id: int):
    """Get worktime sessions log of task with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE task_id=(?)', (task_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_worktime_logs_of_task_in_time(cursor, user_id: int, task_id: int, start: str, end: str):
    """Get worktime sessions log of task with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE task_id=(?) AND '
                   f'(start BETWEEN "{start}" AND "{end}")', (task_id,))
    data = cursor.fetchall()
    return data


@create_connect
def all_users_worktime_logs_in_time(cursor, user_id: int, start: str, end: str):
    """Get worktime sessions log of task with id"""
    cursor.execute(f'SELECT * FROM timework{user_id} WHERE (start BETWEEN "{start}" AND "{end}")')
    data = cursor.fetchall()
    return data


@create_connect
def update_project(cursor, user_id: int, name: str, description: str, project_id: int):
    """Change name and description in project with id"""
    cursor.execute(f"UPDATE all_projects{user_id} SET project_name=(?), description=(?) WHERE id=(?)",
                   (name, description, project_id))


@create_connect
def update_project_worktime(cursor, user_id: int, worktime: int, project_id: int):
    """Change worktime in project with id"""
    cursor.execute(f"UPDATE all_projects{user_id} SET work_time=(?) WHERE id=(?)",
                   (worktime, project_id))


@create_connect
def update_project_price(cursor, user_id: int, price: int, project_id: int):
    """Change price in project with id"""
    cursor.execute(f"UPDATE all_projects{user_id} SET money=(?) WHERE id=(?)",
                   (price, project_id))


@create_connect
def update_user_status(cursor, user_id: int, status: str = 'active'):
    """Change price in project with id"""
    cursor.execute(f"UPDATE all_users SET account_status=(?) WHERE id=(?)",
                   (status, user_id))


@create_connect
def update_task_price(cursor, user_id: int, price: int, task_id: int, money_type: str = 'separately'):
    """Change price in project with id"""
    cursor.execute(f"UPDATE project_task{user_id} SET money=(?), money_type=(?) WHERE id=(?)",
                   (price, money_type, task_id))


@create_connect
def update_project_currency(cursor, user_id: int, currency: str, project_id: int):
    """Change currency in project with id"""
    cursor.execute(f"UPDATE all_projects{user_id} SET currency=(?) WHERE id=(?)",
                   (currency, project_id))


@create_connect
def update_project_task(cursor, user_id: int, name: str, description: str, project_task_id: int):
    """Change name and description in project task with id"""
    cursor.execute(f"UPDATE project_task{user_id} SET name=(?), description=(?) WHERE id=(?)",
                   (name, description, project_task_id))


@create_connect
def update_project_task_worktime(cursor, user_id: int, work_time: int, project_task_id: int):
    """Change worktime in project task with id"""
    cursor.execute(f"UPDATE project_task{user_id} SET work_time=(?) WHERE id=(?)",
                   (work_time, project_task_id))


@create_connect
def update_session_log(cursor, user_id: int, start: str, end: str, time_delta: int, log_id: int):
    """Update start/end time in session log with id"""
    cursor.execute(f"UPDATE timework{user_id} SET start=(?), finish=(?), time_delta=(?) WHERE id=(?)",
                   (start, end, time_delta, log_id))


@create_connect
def delete_auth_token(cursor, user_auth: str):
    """Delete user's token"""
    user_auth = user_auth.split(':')[1]
    cursor.execute(f"UPDATE tokens SET status=('deleted') WHERE token=(?)",
                   (user_auth,))


@create_connect
def delete_project(cursor, user_id: int, project_id: int):
    """Delete project in table by id"""
    cursor.execute(f"DELETE FROM all_projects{user_id} WHERE id={project_id}")


@create_connect
def delete_project_task(cursor, user_id: int, project_task_id: int):
    """Delete project task with id in main project with id."""
    cursor.execute(f"DELETE FROM project_task{user_id} WHERE id={project_task_id}")


@create_connect
def delete_session_log(cursor, user_id: int, session_log_id: int):
    """Delete session log with"""
    cursor.execute(f"DELETE FROM timework{user_id} WHERE id={session_log_id}")


@create_connect
def write_log(cursor, user_id: int, log_text: str):
    """Write user log"""
    data = datetime.datetime.now()
    cursor.execute(f"INSERT OR IGNORE INTO log{user_id} VALUES (?,?,?)",
                   (None, log_text, data))
