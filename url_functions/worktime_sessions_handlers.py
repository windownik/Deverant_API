from starlette import status as _status
from starlette.responses import Response

from modules.decorators import check_token, check_task_id, check_time, check_worktime_log, check_project_id
from modules.sqLite import *


def update_task_worktime(user_id: int, project_id: int, task_id: int):
    """Update user's worktime in profile"""
    task_logs = all_task_worktime_logs(user_id=user_id, task_id=task_id)
    task_worktime = 0
    for element in task_logs:
        if element[5] != 0:
            task_worktime = task_worktime + int(element[5])

    project_logs = all_project_worktime_logs(user_id=user_id, project_id=project_id)
    project_worktime = 0
    for element in project_logs:
        if element[5] != 0:
            project_worktime = project_worktime + int(element[5])

    update_project_worktime(user_id=user_id, worktime=project_worktime, project_id=project_id)
    update_project_task_worktime(user_id=user_id, work_time=task_worktime, project_task_id=task_id)

    task_data = get_project_task_by_id(user_id=user_id, project_task_id=task_id)
    if str(task_data[0][6]) == 'separately':
        pass
    else:
        project_data = get_project_by_id(user_id=user_id, project_id=project_id)
        money = int(project_data[0][4] / project_data[0][3] * task_worktime)
        update_task_price(user_id=user_id, price=money, task_id=task_id, money_type='part')


@check_task_id
@check_time
def service_create_project_worktime(user_id: int, project_task_data: tuple, project_task_id: int,
                                    start_time: str, end_time: str, time_delta: int):
    """User create a new worktime session log with task id and main project id"""

    project_id = project_task_data[0][1]
    log_id = create_task_worktime_session(user_id=user_id, project_id=project_id, task_id=project_task_id,
                                          start=start_time, end=end_time, time_delta=time_delta)
    if not log_id:
        return Response(content=f"Error in database",
                        status_code=_status.HTTP_403_FORBIDDEN)

    else:
        # Update worktime in tables
        update_task_worktime(user_id=user_id, project_id=project_id, task_id=project_task_id)
        return {"status": True,
                "auth_token_status": "active",
                "project_task_id": "active",
                "session_log_id": log_id,
                "description": "session log saved",
                "date": datetime.datetime.now()}


@check_worktime_log
@check_time
def service_update_project_worktime(user_id: int, session_log_id: int, start_time: str, end_time: str, time_delta: int):
    """User update start-end time in worktime session log with id"""
    update_session_log(user_id=user_id, start=start_time, end=end_time,
                       time_delta=time_delta, log_id=session_log_id)
    # Update worktime in tables
    log_data = get_worktime_log_by_id(user_id=user_id, session_log_id=session_log_id)
    update_task_worktime(user_id=user_id, project_id=log_data[0][1], task_id=log_data[0][2])
    return {"status": True,
            "auth_token_status": "active",
            "session_log_id": session_log_id,
            "description": "start/end time is update",
            "date": datetime.datetime.now()
            }


@check_token
def service_get_worktime_session(user_id: int, session_log_id: int):
    """User create a new worktime session log with task id and main project id"""

    log_id = get_worktime_log_by_id(user_id=user_id, session_log_id=session_log_id)
    if str(log_id) == "[]":
        return Response(content=f"Session log not found",
                        status_code=_status.HTTP_403_FORBIDDEN)

    else:
        return {"status": True,
                "auth_token_status": "active",
                "session_log_id": log_id[0][0],
                "project_id": log_id[0][1],
                "project_task_id": log_id[0][2],
                "start_log": log_id[0][3],
                "end_log": log_id[0][4],
                "time_delta_sec": log_id[0][5],
                "create_data": log_id[0][6],
                "date": datetime.datetime.now()}


@check_project_id
def service_get_projects_worktime_sessions(user_id: int, project_id: int, project_data: tuple):
    """Get all worktime session log from project with id"""

    session_logs = all_worktime_logs_of_project(user_id=user_id, project_id=project_id)
    if str(session_logs) == "[]":
        return Response(content=f"no worktime sessions logs in project with id: {project_id}",
                        status_code=_status.HTTP_403_FORBIDDEN)
    data = {"status": True,
            "auth_token_status": "active",
            "project_id_status": "active"}
    time_delta = 0
    for log in session_logs:
        time_delta = time_delta + int(log[5])
        data[log[0]] = {
            "session_log_id": log[0],
            "project_id": log[1],
            "project_task_id": log[2],
            "start_log": log[3],
            "end_log": log[4],
            "time_delta_sec": log[5],
            "create_data": log[6]}
    data["all_worktime_sec"] = time_delta
    return data


@check_project_id
@check_time
def service_get_projects_sessions_time(user_id: int, project_id: int, project_data: tuple, start_time: str,
                                       end_time: str, time_delta: int):
    """Get all worktime session log from project with id in time period"""
    session_logs = all_worktime_logs_of_project_in_time(
        user_id=user_id, project_id=project_id, start=start_time, end=end_time)
    if str(session_logs) == "[]":
        return Response(content=f"no worktime sessions logs in project with id: {project_id} in this time",
                        status_code=_status.HTTP_403_FORBIDDEN)
    data = {"status": True,
            "auth_token_status": "active",
            "project_id_status": "active"}
    time_delta = 0
    for log in session_logs:
        time_delta = time_delta + int(log[5])
        data[log[0]] = {
            "session_log_id": log[0],
            "project_id": log[1],
            "project_task_id": log[2],
            "start_log": log[3],
            "end_log": log[4],
            "time_delta_sec": log[5],
            "create_data": log[6]}
    data["all_worktime_sec"] = time_delta
    return data


@check_task_id
def service_get_tasks_worktime_sessions(user_id: int, project_task_data: tuple, project_task_id: int):
    """Get all worktime session log from project id"""
    session_logs = all_worktime_logs_of_task(user_id=user_id, task_id=project_task_id)
    if str(session_logs) == "[]":
        return Response(content=f"no worktime sessions logs in task with id: {project_task_id}",
                        status_code=_status.HTTP_403_FORBIDDEN)
    data = {"status": True,
            "auth_token_status": "active",
            "task_id_status": "active"}
    time_delta = 0
    for log in session_logs:
        time_delta = time_delta + int(log[5])
        data[log[0]] = {
            "session_log_id": log[0],
            "project_id": log[1],
            "project_task_id": log[2],
            "start_log": log[3],
            "end_log": log[4],
            "time_delta_sec": log[5],
            "create_data": log[6]}
    data["all_worktime_sec"] = time_delta
    return data


@check_task_id
@check_time
def service_get_task_sessions_time(user_id: int, project_task_data: tuple, project_task_id: int,
                                   start_time: str, end_time: str, time_delta: int):
    """Get all worktime session log from task with id in time period"""

    session_logs = all_worktime_logs_of_task_in_time(
        user_id=user_id, task_id=project_task_id, start=start_time, end=end_time)
    if str(session_logs) == "[]":
        return Response(content="no worktime sessions logs in task with id: {project_task_id} in this time",
                        status_code=_status.HTTP_403_FORBIDDEN)
    data = {"status": True,
            "auth_token_status": "active",
            "task_id_status": "active"}
    time_delta = 0
    for log in session_logs:
        time_delta = time_delta + int(log[5])
        data[log[0]] = {
            "session_log_id": log[0],
            "project_id": log[1],
            "project_task_id": log[2],
            "start_log": log[3],
            "end_log": log[4],
            "time_delta_sec": log[5],
            "create_data": log[6]}
    data["all_worktime_sec"] = time_delta
    return data


@check_token
@check_time
def service_get_users_sessions_time(user_id: int, start_time: str, end_time: str, time_delta: int):
    """Get all user's worktime session log in time period"""
    session_logs = all_users_worktime_logs_in_time(user_id=user_id, start=start_time, end=end_time)
    if str(session_logs) == "[]":
        return Response(content="no user's worktime sessions logs in this time",
                        status_code=_status.HTTP_403_FORBIDDEN)
    data = {"status": True,
            "auth_token_status": "active",
            "task_id_status": "active"}
    time_delta = 0
    for log in session_logs:
        time_delta = time_delta + int(log[5])
        data[log[0]] = {
            "session_log_id": log[0],
            "project_id": log[1],
            "project_task_id": log[2],
            "start_log": log[3],
            "end_log": log[4],
            "time_delta_sec": log[5],
            "create_data": log[6]}
    data["all_worktime_sec"] = time_delta
    return data


@check_token
@check_time
def service_users_time_stat(user_id: int, start_time: str, end_time: str, time_delta: int):
    """Get all user's statistic in time period"""
    session_logs = all_users_worktime_logs_in_time(user_id=user_id, start=start_time, end=end_time)
    projects = []
    all_time = 0
    for log in session_logs:
        all_time += log[5]
        if log[1] in projects:
            pass
        else:
            projects.append(log[1])
    # Calculate time for each project and money
    projects_time_in_period = {}
    projects_currency_in_period = {}
    projects_money_in_period = {}
    all_time_money = 0
    for project in projects:
        # Calculate time
        session_logs = all_worktime_logs_of_project_in_time(
            user_id=user_id, project_id=project, start=start_time, end=end_time)
        project_time = sum([el[5] for el in session_logs])
        projects_time_in_period[project] = project_time
        # Calculate money
        project_data = get_project_by_id(user_id=user_id, project_id=project)
        full_price = project_data[0][4]
        full_time = project_data[0][3]
        money = int((full_price / full_time) * project_time)
        projects_money_in_period[project] = money

        all_time_money += money
        # Get project currency
        projects_currency_in_period[project] = project_data[0][5]
    if all_time == 0:
        price_hour = 0
    else:
        price_hour = int((all_time_money * 3600) / all_time)
    return_data = {"all_work_time": all_time,
                   "all_money_in_time_period": all_time_money,
                   "currency": "RUR",
                   "price_hour": price_hour,
                   "all_projects_ids": projects}
    project_list = []
    for project in projects:
        price_hour = int((projects_money_in_period[project] * 3600) / projects_time_in_period[project])
        project_list.append({'project number': project,
                             'project_time_in_time_period': projects_time_in_period[project],
                             "project_money_in_time_period": projects_money_in_period[project],
                             "project_currency": projects_currency_in_period[project],
                             "price_hour": price_hour})
    return_data['projecs_list'] = project_list
    return return_data


@check_worktime_log
def service_delete_worktime_session(user_id: int, session_log_id: int):
    """User create a new worktime session log with task id and main project id"""

    log_id = get_worktime_log_by_id(user_id=user_id, session_log_id=session_log_id)
    if str(log_id) == "[]":
        return Response(content='Session log not found',
                        status_code=_status.HTTP_403_FORBIDDEN)

    else:
        delete_session_log(user_id=user_id, session_log_id=session_log_id)
        update_task_worktime(user_id=user_id, project_id=log_id[0][1], task_id=log_id[0][2])
        return {"status": True,
                "description": "Session log deleted",
                "date": datetime.datetime.now()}
