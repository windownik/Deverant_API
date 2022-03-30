import datetime
from functools import wraps

from modules.little_funcs import data_time_validation
from modules.sqLite import get_id_by_auth, get_project_task_by_id, get_project_by_id, get_worktime_log_by_id


# check token
def check_token(func):
    """Decorator check valid user token"""
    @wraps(func)
    def _con(user_auth: str, *args, **kwargs):
        user_id, user_status = get_id_by_auth(auth_token=user_auth)
        if user_status == 'need_email':
            return {"status": False,
                    "description": "email not confirm",
                    "date": datetime.datetime.now()}
        elif str(user_id) == "[]" or user_auth == 'deleted':
            return {"status": False,
                    "description": "auth token not valid",
                    "date": datetime.datetime.now()}
        result = func(user_id=user_id, *args, **kwargs)
        return result

    return _con


# check token and valid task id
def check_task_id(func):
    """Decorator check valid task id"""
    @wraps(func)
    def _con(user_auth: int, project_task_id: int, *args, **kwargs):

        user_id, user_status = get_id_by_auth(auth_token=user_auth)
        if user_status == 'need_email':
            return {"status": False,
                    "description": "email not confirm",
                    "date": datetime.datetime.now()}
        elif str(user_id) == "[]" or user_auth == 'deleted':
            return {"status": False,
                    "description": "auth token not valid",
                    "date": datetime.datetime.now()}
        project_task_data = get_project_task_by_id(user_id=user_id, project_task_id=project_task_id)

        if str(project_task_data) == "[]":
            return {"status": False,
                    "auth_token_status": "active",
                    "description": "project task not found",
                    "date": datetime.datetime.now()}
        result = func(user_id=user_id, project_task_data=project_task_data, project_task_id=project_task_id,
                      *args, **kwargs)
        return result

    return _con


# check token and valid project id
def check_project_id(func):
    """Decorator check valid project id """
    @wraps(func)
    def _con(user_auth: int, project_id: int, *args, **kwargs):

        user_id, user_status = get_id_by_auth(auth_token=user_auth)
        if user_status == 'need_email':
            return {"status": False,
                    "description": "email not confirm",
                    "date": datetime.datetime.now()}
        elif str(user_id) == "[]" or user_auth == 'deleted':
            return {"status": False,
                    "description": "auth token not valid",
                    "date": datetime.datetime.now()}
        project_data = get_project_by_id(user_id=user_id, project_id=project_id)
        if str(project_data) == "[]":
            return {"status": False,
                    "auth_token_status": "active",
                    "description": "project not found",
                    "date": datetime.datetime.now()}
        result = func(user_id=user_id, project_id=project_id, project_data=project_data,
                      *args, **kwargs)
        return result

    return _con


# check token and currency
def check_project_currency_id(func):
    """Decorator check valid currency id """
    @wraps(func)
    def _con(user_auth: int, currency: str, project_id: int, *args, **kwargs):
        currency = currency.upper()
        user_id, user_status = get_id_by_auth(auth_token=user_auth)
        if user_status == 'need_email':
            return {"status": False,
                    "description": "email not confirm",
                    "date": datetime.datetime.now()}
        elif str(user_id) == "[]" or user_auth == 'deleted':
            return {"status": False,
                    "description": "auth token not valid",
                    "date": datetime.datetime.now()}
        elif currency not in ("USD", "UAH", "RUR", "EUR", "BYN"):
            return {"status": False,
                    "auth_token_status": "active",
                    "currency": 'That currency not supported',
                    "date": datetime.datetime.now()}
        project_task_data = get_project_by_id(user_id=user_id, project_id=project_id)
        if str(project_task_data) == "[]":
            return {"status": False,
                    "auth_token_status": "active",
                    "description": "project not found",
                    "date": datetime.datetime.now()}
        else:
            result = func(user_id=user_id, currency=currency, project_id=project_id, *args, **kwargs)
            return result

    return _con


# check token and valid task id
def check_worktime_log(func):
    """Decorator check valid task id"""
    @wraps(func)
    def _con(user_auth: int, session_log_id: int, *args, **kwargs):

        user_id, user_status = get_id_by_auth(auth_token=user_auth)
        if user_status == 'need_email':
            return {"status": False,
                    "description": "email not confirm",
                    "date": datetime.datetime.now()}
        elif str(user_id) == "[]" or user_auth == 'deleted':
            return {"status": False,
                    "description": "auth token not valid",
                    "date": datetime.datetime.now()}

        log_id = get_worktime_log_by_id(user_id=user_id, session_log_id=session_log_id)
        if str(log_id) == "[]":
            return {"status": False,
                    "auth_token_status": "active",
                    "description": "Session log not found"}
        result = func(user_id=user_id, session_log_id=session_log_id, *args, **kwargs)

        return result

    return _con


def check_time(func):
    """Decorator check valid start/end time """

    @wraps(func)
    def _con(start_time: str, end_time: str, *args, **kwargs):
        start_time, end_time, time_delta = data_time_validation(start=start_time, end=end_time)
        if not start_time or not end_time:
            return {"status": False,
                    "auth_token_status": "active",
                    "project_task_id": "active",
                    "description": "bad datetime format",
                    "date": datetime.datetime.now()}
        result = func(start_time=start_time, end_time=end_time, time_delta=time_delta, *args, **kwargs)
        return result

    return _con
