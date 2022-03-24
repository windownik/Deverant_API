
from functools import wraps
import sqlite3
import datetime


# Create tables in database
class CreateDatabaseTables:
    connect = sqlite3.connect('modules/database.db', check_same_thread=False)
    cursor = connect.cursor()

    def create_table_all_users(self):
        """Create table all_users in database"""
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS all_users (
         id INTEGER PRIMARY KEY,
         mail TEXT,
         password TEXT,
         nickname TEXT,
         account_status TEXT DEFAULT active,
         auth_token TEXT,
         first_reg DATETIME,
         lust_activity DATETIME)''')
        self.connect.commit()
        self.connect.close()


# Work with user database methods
class DataBaseUsers:
    def __init__(self):
        self.cursor = None
        self.connect = None

    def create_connect(self, func):
        self.connect = sqlite3.connect('modules/database.db', check_same_thread=False)
        self.cursor = self.connect.cursor()

        @wraps(func)
        def _con(*args, **kwargs):
            result = func(*args, **kwargs)
            self.connect.commit()
            self.connect.close()
            return result
        return _con()

    def close_connection(self):
        """Close connection with database"""
        self.connect.close()

    @create_connect
    def create_table_user_log(self, user_id: int):
        """Create user log table in database"""
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS log{user_id} (
         id INTEGER PRIMARY KEY,
         log_text TEXT,
         data DATETIME)''')

    @create_connect
    def create_table_user_projects(self, user_id: int):
        """Create user's all projects table in database by user id"""
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS all_projects{user_id} (
         id INTEGER PRIMARY KEY,
         project_name TEXT DEFAULT Project,
         description TEXT,
         work_time INTEGER,
         money INTEGER,
         currency TEXT DEFAULT "USD",
         create_data DATETIME,
         lust_active DATETIME)''')

    def create_table_users_tasks(self, user_id: int):
        """Create user's all projects table in database by user id"""
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS project_task{user_id} (
         id INTEGER PRIMARY KEY,
         main_project_id INTEGER,
         name TEXT,
         description TEXT,
         work_time DATETIME,
         money INTEGER,
         create_data DATETIME,
         lust_active DATETIME)''')
        self.connect.commit()

    def create_user_project_timework_table(self, user_id: int):
        """Create user's all projects table in database by user id"""
        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS timework{user_id} (
         id INTEGER PRIMARY KEY,
         project_id INTEGER,
         task_id INTEGER,
         start DATETIME,
         finish DATETIME,
         time_delta INTEGER,
         data DATETIME)''')
        self.connect.commit()

    def get_id_by_auth(self, auth_token: str):
        """
        Get account id by auth token
        """
        self.cursor.execute(f'SELECT id FROM all_users WHERE "auth_token" = "{auth_token}"')
        data = self.cursor.fetchall()
        self.connect.close()
        return data

    def get_token_status(self, auth_token: str):
        """
        Get infor about token actuality
        """
        self.cursor.execute(f'SELECT id FROM all_users WHERE "auth_token" = "{auth_token}"')
        data = self.cursor.fetchall()
        self.connect.close()
        return data

    def get_user_auth(self, mail: str, password: str):
        """
        Get user auth token
        """
        self.cursor.execute(f'SELECT auth_token FROM all_users WHERE "mail" = "{mail}" AND "password" = "{password}"')
        data = self.cursor.fetchall()
        self.connect.close()
        if str(data) == "[]":
            return False
        return data

    def get_user_id_by_email(self, email: str, password: str):
        """
        Get user id by email and password
        """
        self.cursor.execute(f'SELECT id FROM all_users WHERE "mail" = "{email}" AND "password" = "{password}"')
        data = self.cursor.fetchall()
        if str(data) == "[]":
            return False
        return data[0][0]

    def find_email(self, mail: str):
        """
        Find user mail in database
        """
        try:
            self.cursor.execute(f'SELECT id FROM all_users WHERE "mail" = "{mail}"')
            data = self.cursor.fetchall()
            return data
        except:
            return '[]'

    def create_user_account(self, mail: str, password: str, auth_token: str, nickname: str):
        """Create a new account by """
        data = datetime.datetime.now()
        try:
            self.cursor.execute(f"INSERT OR IGNORE INTO all_users VALUES (?,?,?,?,?,?,?,?)",
                                (None, mail, password, nickname, "active", auth_token, data, data))
            self.connect.commit()
            return True
        except Exception as _ex:
            print("[INFORMATION] ERROR in db", _ex)
            return False

    def user_create_project(self, user_id: int, name: str, description: str):
        """User create a new project"""
        data = datetime.datetime.now()
        try:
            self.cursor.execute(f"INSERT OR IGNORE INTO all_projects{user_id} VALUES (?,?,?,?,?,?,?,?)",
                                (None, name, description, '0', 0, "USD", data, data))
            self.connect.commit()
            self.cursor.execute(f'SELECT id FROM all_projects{user_id} WHERE "create_data" = "{data}"')
            data = self.cursor.fetchall()[0][0]
            return data
        except Exception as _ex:
            print("[INFORMATION] ERROR in db", _ex)
            return False

    def user_create_project_task(self, user_id: int, project_id: int, name: str, description: str):
        """User create a new project task with main project with id"""
        data = datetime.datetime.now()
        try:
            self.cursor.execute(f"INSERT OR IGNORE INTO project_task{user_id} VALUES (?,?,?,?,?,?,?,?)",
                                (None, project_id, name, description, '0', 0, data, data))
            self.connect.commit()
            self.cursor.execute(f'SELECT id FROM project_task{user_id} WHERE "create_data" = "{data}"')
            data = self.cursor.fetchall()[0][0]
            return data
        except Exception as _ex:
            print("[INFORMATION] ERROR in db", _ex)
            return False

    def create_task_worktime_session(self, user_id: int, project_id: int, task_id: int, start: str, end: str,
                                     time_delta: str):
        """User create a new worktime session log with task id and main project id"""
        data = datetime.datetime.now()
        try:
            self.cursor.execute(f"INSERT OR IGNORE INTO timework{user_id} VALUES (?,?,?,?,?,?,?)",
                                (None, project_id, task_id, start, end, time_delta, data))
            self.connect.commit()
            self.cursor.execute(f'SELECT id FROM timework{user_id} WHERE "data" = "{data}"')
            data = self.cursor.fetchall()[0][0]
            return data
        except Exception as _ex:
            print("[INFORMATION] ERROR in db", _ex)
            return False

    def grab_all_my_projects(self, user_id: int):
        """Get all user's projects"""
        self.cursor.execute(f'SELECT * FROM all_projects{user_id}')
        data = self.cursor.fetchall()
        return data

    def get_project_by_id(self, user_id: int, project_id: int):
        """Get user's project data by id"""
        self.cursor.execute(f'SELECT * FROM all_projects{user_id} WHERE id=(?)', (project_id,))
        data = self.cursor.fetchall()
        return data

    def get_project_task_by_id(self, user_id: int, project_task_id: int):
        """Get user's project task data by id"""
        self.cursor.execute(f'SELECT * FROM project_task{user_id} WHERE id=(?)', (project_task_id,))
        data = self.cursor.fetchall()
        return data

    def grab_all_my_project_tasks(self, user_id: int):
        """Get all user's project tasks"""
        self.cursor.execute(f'SELECT * FROM project_task{user_id}')
        data = self.cursor.fetchall()
        return data

    def all_tasks_of_one_project(self, user_id: int, project_id: int):
        """Find All tasks of one project with id"""
        self.cursor.execute(f'SELECT * FROM project_task{user_id} WHERE main_project_id=(?)', (project_id,))
        data = self.cursor.fetchall()
        return data

    def all_project_worktime_logs(self, user_id: int, project_id: int):
        """Find All worktime sessions logs of one project with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE project_id=(?)', (project_id,))
        data = self.cursor.fetchall()
        return data

    def all_task_worktime_logs(self, user_id: int, task_id: int):
        """Find All worktime sessions logs of one task with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE task_id=(?)', (task_id,))
        data = self.cursor.fetchall()
        return data

    def get_worktime_log_by_id(self, user_id: int, session_log_id: int):
        """Get worktime sessions log with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE id=(?)', (session_log_id,))
        data = self.cursor.fetchall()
        return data

    def all_worktime_logs_of_project(self, user_id: int, project_id: int):
        """Get worktime sessions log of project with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE project_id=(?)', (project_id,))
        data = self.cursor.fetchall()
        return data

    def all_worktime_logs_of_project_in_time(self, user_id: int, project_id: int, start: str, end: str):
        """Get worktime sessions log of project with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE project_id=(?) AND '
                            f'(start BETWEEN "{start}" AND "{end}")', (project_id,))
        data = self.cursor.fetchall()
        return data

    def all_worktime_logs_of_task(self, user_id: int, task_id: int):
        """Get worktime sessions log of task with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE task_id=(?)', (task_id,))
        data = self.cursor.fetchall()
        return data

    def all_worktime_logs_of_task_in_time(self, user_id: int, task_id: int, start: str, end: str):
        """Get worktime sessions log of task with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE task_id=(?) AND '
                            f'(start BETWEEN "{start}" AND "{end}")', (task_id,))
        data = self.cursor.fetchall()
        return data

    def all_users_worktime_logs_in_time(self, user_id: int, start: str, end: str):
        """Get worktime sessions log of task with id"""
        self.cursor.execute(f'SELECT * FROM timework{user_id} WHERE (start BETWEEN "{start}" AND "{end}")')
        data = self.cursor.fetchall()
        return data

    def update_project(self, user_id: int, name: str, description: str, project_id: int):
        """Change name and description in project with id"""
        self.cursor.execute(f"UPDATE all_projects{user_id} SET project_name=(?), description=(?) WHERE id=(?)",
                            (name, description, project_id))
        self.connect.commit()

    def update_project_worktime(self, user_id: int, worktime: int, project_id: int):
        """Change worktime in project with id"""
        self.cursor.execute(f"UPDATE all_projects{user_id} SET work_time=(?) WHERE id=(?)",
                            (worktime, project_id))
        self.connect.commit()

    def update_project_price(self, user_id: int, price: int, project_id: int):
        """Change price in project with id"""
        self.cursor.execute(f"UPDATE all_projects{user_id} SET money=(?) WHERE id=(?)",
                            (price, project_id))
        self.connect.commit()

    def update_project_currency(self, user_id: int, currency: str, project_id: int):
        """Change currency in project with id"""
        self.cursor.execute(f"UPDATE all_projects{user_id} SET currency=(?) WHERE id=(?)",
                            (currency, project_id))
        self.connect.commit()

    @create_connect
    def update_project_task(self, user_id: int, name: str, description: str, project_task_id: int):
        """Change name and description in project task with id"""
        self.cursor.execute(f"UPDATE project_task{user_id} SET name=(?), description=(?) WHERE id=(?)",
                            (name, description, project_task_id))

    @create_connect
    def update_project_task_worktime(self, user_id: int, work_time: int, project_task_id: int):
        """Change worktime in project task with id"""
        self.cursor.execute(f"UPDATE project_task{user_id} SET work_time=(?) WHERE id=(?)",
                            (work_time, project_task_id))
        self.connect.commit()

    def update_auth_token(self, user_id: int, auth_token: str):
        """Update user's token"""
        self.cursor.execute(f"UPDATE all_users SET auth_token=(?) WHERE id=(?)",
                            (auth_token, user_id))
        self.connect.commit()

    def update_session_log(self, user_id: int, start: str, end: str, time_delta: int, log_id: int):
        """Update start/end time in session log with id"""
        self.cursor.execute(f"UPDATE timework{user_id} SET start=(?), finish=(?), time_delta=(?) WHERE id=(?)",
                            (start, end, time_delta, log_id))
        self.connect.commit()

    def delete_auth_token(self, user_id: int):
        """Delete user's token"""
        self.cursor.execute(f"UPDATE all_users SET auth_token=('deleted') WHERE id=(?)",
                            (user_id,))
        self.connect.commit()

    def delete_project(self, user_id: int, project_id: int):
        """Delete project in table by id"""
        self.cursor.execute(f"DELETE FROM all_projects{user_id} WHERE id={project_id}")
        self.connect.commit()

    def delete_project_task(self, user_id: int, project_task_id: int):
        """Delete project task with id in main project with id."""
        self.cursor.execute(f"DELETE FROM project_task{user_id} WHERE id={project_task_id}")
        self.connect.commit()

    def delete_session_log(self, user_id: int, session_log_id: int):
        """Delete session log with"""
        self.cursor.execute(f"DELETE FROM timework{user_id} WHERE id={session_log_id}")
        self.connect.commit()

    def write_log(self, user_id: int, log_text: str):
        """Write user log"""
        data = datetime.datetime.now()
        self.cursor.execute(f"INSERT OR IGNORE INTO log{user_id} VALUES (?,?,?)",
                            (None, log_text, data))
        self.connect.commit()


#
# # Пользователь проверяет себя по базе данных
# def read_value_table_name(
#         table: str,
#         telegram_id, *,
#         graph: str = '*',
#         id_name: str = 'telegram_id',
#         sort: str = ""):
#
#     curs = connect.cursor()
#     curs.execute(f'SELECT {graph} FROM {table} WHERE {id_name} ="{telegram_id}" {sort}')
#     data = curs.fetchall()
#     return data
#
#
# # Пользователь проверяет данные по двум параметрам
# def read_value_2_(user_tg_id,
#                   ignor_tg_id, *,
#                   table: str = 'ignor',
#                   id_name1: str = 'user_tg_id',
#                   id_name2: str = 'ignor_tg_id',
#                   name: str = '*'):
#     # connect = sqlite3.connect('modules/database.db')
#     curs = connect.cursor()
#     curs.execute(f'SELECT {name} FROM {table} WHERE "{id_name1}" = "{user_tg_id}" AND "{id_name2}" = "{ignor_tg_id}"')
#     data = curs.fetchall()
#     return data


# # Пользователь проверяет себя по базе данных
# def read_all_log_sort(
#         name: str = '*',
#         table: str = 'all_users',
#         sort_name: str = 'id'):
#     curs = connect.cursor()
#     curs.execute(f'SELECT {name} FROM {table} ORDER BY {sort_name} DESC')
#     data = curs.fetchall()
#     return data

#
# # Обновляем любые данные в любую таблицу
# def insert_info(
#         table: str,
#         telegram_id,
#         name: str,
#         data, *,
#         id_name: str = 'telegram_id'):
#     curs = connect.cursor()
#     curs.execute(f"UPDATE {table} SET {name}= ('{data}') WHERE {id_name}='{telegram_id}'")
#     connect.commit()

#
# # Удаляем данные из таблицы
# def delete_str(
#         table: str,
#         data, *,
#         name: str = 'telegram_id'):
#     curs = connect.cursor()
#     curs.execute(f"DELETE FROM '{table}' WHERE {name}={data}")
#     connect.commit()
#
#
# # Удаляем все данные из таблицы
# def delete_all_str(table: str):
#     curs = connect.cursor()
#     curs.execute(f"DELETE FROM '{table}'")
#     connect.commit()
#
#
# # Удаляем таблицу
# def delete_table(table: str):
#     curs = connect.cursor()
#     curs.execute(f"DROP TABLE IF EXISTS {table}")
#     connect.commit()
