import uvicorn
from fastapi import FastAPI
from url_functions.project_task_handlers import service_create_project, get_my_project_by_id, service_change_project, \
    get_my_projects, service_create_project_task, service_task_by_id, get_all_users_project_tasks, \
    service_all_tasks_of_one_project, service_change_project_task_info, service_update_project_price, \
    service_update_project_currency, service_delete_project, service_delete_project_task, service_update_task_price, \
    service_create_project_full
from url_functions.user_handlers import check_user_mail, login, logout, service_create_user_account, confirm_email, \
    check_user_auth_token
from url_functions.worktime_sessions_handlers import service_create_project_worktime, service_update_project_worktime, \
    service_get_worktime_session, service_delete_worktime_session, service_get_projects_worktime_sessions, \
    service_get_projects_sessions_time, service_get_tasks_worktime_sessions, service_get_task_sessions_time, \
    service_get_users_sessions_time, service_users_time_stat
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=["Origin, X-Requested-With, Content-Type, Accept"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Welcome to Deverant API",
        version="0.0.1.2 Alfa",
        description="Our service is diary for your incomes'\n\n"
                    "This api can:\n\n"
                    "Create new account, of course you can log in and log out.\n"
                    "All functions of our service available for log in users.\n\n"
                    "At first you can create new project and create new tasks in this project. In this version every "
                    "project must have tasks\n\n"
                    "When you create task you can write worktime logs. Worktime log is information when you "
                    "started working on the task and finished. After you create worktime log our service calculate "
                    "how long time you work on every your project and every your task. If you don't know what is your "
                    "price hour - Deverant calculate it for you.\n\n"
                    "Currency - Default USD. This param you can change after project creation. In this version service "
                    "can't exchange money automatically.\n\n"
                    "",
        routes=app.routes,
        tags=[{'name': 'Users', 'description': "All user's endpoints to work with account"},
              {'name': 'Projects', 'description': "Endpoints to work with projects"},
              {'name': 'Project Tasks', 'description': "Endpoints to work with project tasks"},
              {'name': 'WorkTime Logs', 'description': "Endpoints to work with worktime sessions logs"},
              {'name': "User's Statistic", 'description': "User statistics when working on projects and tasks"}]
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://i.postimg.cc/wvhDZTPn/Deverant.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


def generate_html_response():
    html_content = """
    <html>
        <head>
            <title>Start page</title>
        </head>
        <body>
            <h2>Documentation for Deverant API</h2>
            <p><a href="/docs">Documentation standart</a></p>
            <p><a href="/redoc">Documentation from reDoc</a></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get('/', response_class=HTMLResponse)
def main_page():
    """main page"""
    return generate_html_response()


@app.get(path='/check/{mail}', tags=['Users'])
def check_new_mail(mail: str):
    """This method return user's mail status."""
    return check_user_mail(mail=mail)


@app.get(path='/getMe/{user_auth}', tags=['Users'])
def check_new_mail(user_auth: str):
    """This method return user's mail status."""
    return check_user_auth_token(user_auth=user_auth)


@app.get(path='/login/{email}', tags=['Users'])
def login_user(email: str, password: str):
    """
    This method return user auth token and secret. Didn't lose your secret\n
    How to prepare token to sand?\n
    Token = secret:auth_token.
    """
    return login(mail=email, password=password)


@app.put(path='/logout/{user_auth}', tags=['Users'])
def logout_user(user_auth: str):
    """
    This method logout user auth token.\n
    Example of token: secret:auth_token"""
    return logout(user_auth=user_auth)


@app.post(path='/create_account/{mail}', tags=['Users'])
def create_new_user_account(mail: str, password: str, user_name: str):
    """This method create new user account. """
    return service_create_user_account(mail=mail, password=password, nickname=user_name)


# @app.get(path='/confirm_account/{user_auth}', tags=['Users'])
# def confirm_new_user_account(user_auth: str, email_cod: str):
#     """Confirm new account by email cod"""
#     return confirm_email(user_auth=user_auth, email_cod=email_cod)


@app.post(path='/project/{user_auth}', tags=['Projects'])
def create_project(user_auth: str, name: str, description: str):
    """
    This method create new project in database with name and description.\n
    Return new project id;
    Name - it's short name of your new project.\n
    Description - it's long text about new project. There are you can explain about this project.\n
    """
    return service_create_project(user_auth=user_auth, name=name, description=description)


@app.post(path='/project_price/{user_auth}', tags=['Projects'])
def create_project_with_price(user_auth: str, name: str, description: str, price: str):
    """
    This method create new project in database with name, description and price.\n
    Return new project id;
    Name - it's short name of your new project.\n
    Description - it's long text about new project. There are you can explain about this project.\n
    Price - total price of new project.
    """
    return service_create_project_full(user_auth=user_auth, name=name, description=description, price=price)


@app.get(path='/project/{user_auth}', tags=['Projects'])
def my_project_by_id(user_auth: str, project_id: int):
    """This method returns information of user's one project with id"""
    return get_my_project_by_id(user_auth=user_auth, project_id=project_id)


@app.put(path='/project/{user_auth}', tags=['Projects'])
def update_project(user_auth: str, project_id: int, name: str, description: str):
    """
    Change name and description in project with id.
    Send new name and new description.
    """
    return service_change_project(user_auth=user_auth, project_id=project_id, name=name, description=description)


@app.get(path='/all_projects/{user_auth}', tags=['Projects'])
def get_all_my_projects(user_auth: str, offset: int = 0, limit: int = 0):
    """
    This method returns json with all user's projects
    """
    return get_my_projects(user_auth=user_auth, offset=offset, limit=limit)


@app.put(path='/project_price/{user_auth}', tags=['Projects'])
def update_project_price(user_auth: str, project_id: int, price: int):
    """Update project price with id
    Price - Default 0. This param you can change after project creation"""
    return service_update_project_price(user_auth=user_auth, project_id=project_id, price=price)


@app.put(path='/project_currency/{user_auth}', tags=['Projects'])
def update_project_currency(user_auth: str, project_id: int, currency: str):
    """
    Update project currency with id\n
    Supported currency: "USD", "EUR", "BYN", "UAH", "RUR"\n
    Currency - Default USD. This param you can change after project creation. In this version service
    can't exchange money automatically.\n
    """
    return service_update_project_currency(user_auth=user_auth, project_id=project_id, currency=currency)


@app.delete(path='/project/{user_auth}', tags=['Projects'])
def delete_project(user_auth: str, project_id: int):
    """Delete project with id."""
    return service_delete_project(user_auth=user_auth, project_id=project_id)


@app.post(path='/project_task/{user_auth}', tags=['Project Tasks'])
def create_project_task(user_auth: str, project_id: int, name: str, description: str):
    """
    This method create new project task in database with name and description.\n
    This task is part of the main project\n
    Return new project task id and main project id
    """
    return service_create_project_task(user_auth=user_auth, project_id=project_id,
                                       name=name, description=description)


@app.get(path='/project_task/{user_auth}', tags=['Project Tasks'])
def task_by_id(user_auth: str, project_task_id: int):
    """This method returns json of all data of one task with id"""
    return service_task_by_id(user_auth=user_auth, project_task_id=project_task_id)


@app.get(path='/users_project_tasks/{user_auth}', tags=['Project Tasks'])
def users_all_tasks(user_auth: str):
    """This method returns json of all user's project tasks"""
    return get_all_users_project_tasks(user_auth=user_auth)


@app.get(path='/all_tasks_of_project/{user_auth}', tags=['Project Tasks'])
def all_tasks_of_one_project(user_auth: str, project_id: int):
    """This method returns json of All tasks of one project with id"""
    return service_all_tasks_of_one_project(user_auth=user_auth, project_id=project_id)


@app.put(path='/project_task/{user_auth}', tags=['Project Tasks'])
def update_project_task_info(user_auth: str, project_task_id: int, name: str, description: str):
    """
    Change name and description in project task with id.
    Send new name and new description.
    """
    return service_change_project_task_info(user_auth=user_auth, project_task_id=project_task_id, name=name,
                                            description=description)


@app.put(path='/task_price/{user_auth}', tags=['Project Tasks'])
def update_project_price(user_auth: str, task_id: int, price: int, money_type: int):
    """Update task price with id\n
    ATTENTION money_type can take two values 0 or 1\n
    1 -- if you want to add task's price separate of main project's price\n
    0 -- if you want to add task's price to main project's price.
    """
    return service_update_task_price(user_auth=user_auth, project_task_id=task_id, price=price, money_type=money_type)


@app.delete(path='/project_task/{user_auth}', tags=['Project Tasks'])
def delete_project_task(user_auth: str, project_task_id: int):
    """ Delete project task with id in main project with id."""
    return service_delete_project_task(user_auth=user_auth, project_task_id=project_task_id)


@app.post(path='/task_worktime_log/{user_auth}', tags=['WorkTime Logs'])
def create_project_worktime_session(user_auth: str, project_task_id: int, start_time: str, end_time: str):
    """
    Write project task worktime log in database\n
    start/end time example: 2022-03-17 12:42:14.348834
    """
    return service_create_project_worktime(user_auth=user_auth, project_task_id=project_task_id, start_time=start_time,
                                           end_time=end_time)


@app.put(path='/task_worktime_log/{user_auth}', tags=['WorkTime Logs'])
def update_project_worktime_session(user_auth: str, session_log_id: int, start_time: str, end_time: str):
    """
    Write project task worktime log in database\n
    start/end time example: 2022-03-17 12:42:14.348834
    """
    return service_update_project_worktime(user_auth=user_auth, session_log_id=session_log_id, start_time=start_time,
                                           end_time=end_time)


@app.get(path='/task_worktime_log/{user_auth}', tags=['WorkTime Logs'])
def get_project_worktime(user_auth: str, session_log_id: int):
    """Get all info about worktime session log with id"""
    return service_get_worktime_session(user_auth=user_auth, session_log_id=session_log_id)


@app.delete(path='/task_worktime_log/{user_auth}', tags=['WorkTime Logs'])
def delete_project_worktime(user_auth: str, session_log_id: int):
    """Delete worktime session log with id"""
    return service_delete_worktime_session(user_auth=user_auth, session_log_id=session_log_id)


@app.get(path='/all_project_worktime_logs/{user_auth}', tags=['WorkTime Logs'])
def all_project_worktime_logs(user_auth: str, project_id: int):
    """Get all worktime session logs of one project with id"""
    return service_get_projects_worktime_sessions(user_auth=user_auth, project_id=project_id)


@app.get(path='/all_project_worktime_logs_time/{user_auth}', tags=['WorkTime Logs'])
def all_project_worktime_logs_in_time(user_auth: str, project_id: int, start_time: str, end_time: str):
    """Get all worktime session logs of one project with id between start and end"""
    return service_get_projects_sessions_time(
        user_auth=user_auth, project_id=project_id, start_time=start_time, end_time=end_time)


@app.get(path='/all_task_worktime_logs/{user_auth}', tags=['WorkTime Logs'])
def all_task_worktime_logs(user_auth: str, project_task_id: int):
    """Get all worktime session logs of one task with id"""
    return service_get_tasks_worktime_sessions(user_auth=user_auth, project_task_id=project_task_id)


@app.get(path='/task_worktime_logs_time/{user_auth}', tags=['WorkTime Logs'])
def all_task_worktime_logs_in_time(user_auth: str, project_task_id: int, start_time: str, end_time: str):
    """Get all worktime session logs of one task with id between start and end"""
    return service_get_task_sessions_time(
        user_auth=user_auth, project_task_id=project_task_id, start_time=start_time, end_time=end_time)


@app.get(path='/worktime_logs_time/{user_auth}', tags=['WorkTime Logs'])
def users_worktime_logs_in_time(user_auth: str, start_time: str, end_time: str):
    """Get all User's worktime session logs start and end"""
    return service_get_users_sessions_time(
        user_auth=user_auth, start_time=start_time, end_time=end_time)


@app.get(path='/users_time_stat/{user_auth}', tags=["User's Statistic"])
def users_statistic_in_time_period(user_auth: str, start_time: str, end_time: str):
    """Get User's statistic in time period.\n
    Get next statistic:\n
    All work time in this time period\n
    All money which you earned in this time period\n
    Yor average price hour in USD"""
    return service_users_time_stat(
        user_auth=user_auth, start_time=start_time, end_time=end_time)


@app.get(path='/send_db', response_class=FileResponse)
def send_db_file():
    """THIS method only for devs\n
    Use this for download old database in server"""
    file_path = 'modules/database.db'

    return FileResponse(file_path, filename="dataBase.db")


if __name__ == '__main__':
    uvicorn.run("main:app",
                host="45.82.69.211",
                port=443,
                reload=True)
