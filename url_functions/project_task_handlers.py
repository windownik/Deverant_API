from starlette.responses import Response
import starlette.status as _status

from modules.sqLite import *
from modules.decorators import check_token, check_task_id, check_project_currency_id, check_project_id
import datetime


def get_user_auth_status(user_auth: str):
    """This method returns user_auth actuality status"""
    auth = get_token_status(auth_token=user_auth)
    if auth is None:
        return Response(content='Bad auth token',
                        status_code=_status.HTTP_403_FORBIDDEN)
    else:
        return {"status": True,
                "user_auth": user_auth,
                "date": datetime.datetime.now()}


@check_token
def service_create_project(user_id: int, name: str, description: str):
    """
    User create new project.\n
    At first: check user's auth token status\n
    Next: create line in table user's projects and table for timework sessions
    """
    project_id = user_create_project(user_id=user_id, name=name, description=description)
    # Write first log
    write_log(user_id=user_id, log_text=f'User with id: {user_id}, create new project with name {name},'
                                        f'new project id: {project_id}')
    return {"status": True,
            "auth_token_status": "active",
            "description": "new project created",
            "project_id": project_id,
            'project_name': name,
            "date": datetime.datetime.now()}


@check_project_id
def service_create_project_task(user_id: int, project_id: int, name: str, description: str, project_data: tuple):
    """
    User create new project.\n
    At first: check user's auth token status\n
    Next: create line in table user's projects and table for timework sessions
    """
    print(name, description)
    project_task_id = user_create_project_task(user_id=user_id, project_id=project_id, name=name,
                                               description=description)
    # Write log
    write_log(user_id=user_id,
              log_text=f'User with id: {user_id}, create new project task with name {name}, '
                       f'main project id: {project_id}, new project task id: {project_task_id}')
    return {"status": True,
            "auth_token_status": "active",
            "description": "new project task created",
            "main_project_id": project_id,
            'project_task_name': name,
            'project_task_id': project_task_id,
            "date": datetime.datetime.now()}


@check_token
def get_my_projects(user_id: int, offset: int = 0, limit: int = 0):
    """Find all user's projects and get ids"""
    if limit != 0:
        my_projects = grab_my_projects_offset(user_id=user_id, offset=offset, limit=limit)
    else:
        my_projects = grab_all_my_projects(user_id=user_id)
    count_all = len(grab_all_my_projects(user_id=user_id))
    all_projects = []
    projects_list = []
    for element in my_projects:
        project = {
            'id': element[0],
            "project_name": element[1],
            "description": element[2],
            "work_time": element[3],
            "money": element[4],
            "currency": element[5],
            "create_data": element[6],
            "lust_activity": element[7]}
        all_projects.append(project)
        projects_list.append(element[0])
    return {"status": True,
            'total_count': count_all,
            'projects_list': projects_list,
            'projects': all_projects
            }


@check_project_id
def get_my_project_by_id(user_id: str, project_id: int, project_data: tuple):
    """Find user's project with id"""
    return_data = {"status": True,
                   'id': project_data[0][0],
                   "project_name": project_data[0][1],
                   "description": project_data[0][2],
                   "work_time": project_data[0][3],
                   "money": project_data[0][4],
                   "separately_money": 0,
                   "currency": project_data[0][5],
                   "create_data": project_data[0][6],
                   "lust_activity": project_data[0][7]}
    project_tasks = all_project_tasks_separately_price(user_id=user_id, project_id=project_id)
    if str(project_tasks) == '[]':
        return return_data
    else:
        separately_price = 0
        for task in project_tasks:
            separately_price = separately_price + task[5]
        return_data['separately_money'] = separately_price
        return return_data


@check_token
def get_all_users_project_tasks(user_id: int):
    """
    Find all user's project tasks and get data
    """
    my_projects = grab_all_my_project_tasks(user_id=user_id)
    all_projects = {}
    for element in my_projects:
        all_projects[element[0]] = {"status": True,
                                    "auth_token_status": "active",
                                    'id': element[0],
                                    "main_project_id": element[1],
                                    "project_name": element[2],
                                    "description": element[3],
                                    "work_time": element[4],
                                    "money": element[5],
                                    "create_data": element[6],
                                    "lust_activity": element[7]}
    if all_projects == {}:
        return {"status": False,
                "auth_token_status": "active",
                "description": "you haven't any project tasks"}
    return all_projects


@check_project_id
def service_all_tasks_of_one_project(user_id: int, project_id: int, project_data: tuple):
    """Find All tasks of one project with id"""
    my_project_tasks = all_tasks_of_one_project(user_id=user_id, project_id=project_id)
    tasks_part_price = all_project_tasks_part_price(user_id=user_id, project_id=project_id)
    all_time = sum([i[4] for i in tasks_part_price])
    project_money = get_project_by_id(user_id=user_id, project_id=project_id)[0][4]
    tasks = {}
    for element in my_project_tasks:
        if element[6] == 'separately':
            money = element[5]
        else:
            money = int((int(project_money) / all_time) * int(element[4]))
            update_task_price(user_id=user_id, price=int(money), task_id=element[0], money_type='part')
        tasks[element[0]] = {"status": True,
                             'id': element[0],
                             "main_project_id": element[1],
                             "project_name": element[2],
                             "description": element[3],
                             "work_time": element[4],
                             "money": money,
                             "money_type": element[6],
                             "create_data": element[7],
                             "lust_activity": element[8]}

    if tasks == {}:
        return {"status": False,
                "auth_token_status": "active",
                "description": "you haven't any project tasks"}
    return tasks


@check_task_id
def service_task_by_id(user_id: int, project_task_id: int, project_task_data: tuple):
    """Get task info by task_id"""
    return_data = {"status": True,
                   'id': project_task_data[0][0],
                   "main_project_id": project_task_data[0][1],
                   "project_name": project_task_data[0][2],
                   "description": project_task_data[0][3],
                   "work_time": project_task_data[0][4],
                   "money": project_task_data[0][5],
                   "money_type": project_task_data[0][6],
                   "create_data": project_task_data[0][7],
                   "lust_activity": project_task_data[0][8]}
    return return_data


@check_token
def service_change_project(user_id: int, project_id: int, name: str, description: str):
    """Change name and description in project with id"""
    update_project(user_id=user_id, name=name, description=description, project_id=project_id)
    # Write log
    write_log(user_id=user_id, log_text=f'User with id: {user_id}, change project with id: {project_id},'
                                        f'New name: {name},'
                                        f'New description: {description}')
    return {"status": True,
            "auth_token_status": "active",
            "id": project_id,
            'project_name': name,
            "description": description,
            "date": datetime.datetime.now()}


@check_task_id
def service_change_project_task_info(user_id: int, project_task_id: int, name: str, description: str,
                                     project_task_data: tuple):
    """Change name and description in project with id"""
    update_project_task(user_id=user_id, name=name, description=description, project_task_id=project_task_id)
    # Write log
    write_log(user_id=user_id,
              log_text=f'User with id: {user_id}, change project task with id: {project_task_id},'
                       f'New name: {name}, New description: {description}')
    return {"status": True,
            "auth_token_status": "active",
            "project_task_id": project_task_id,
            'project_task_name': name,
            "task_description": description,
            "date": datetime.datetime.now()}


@check_project_id
def service_update_project_price(user_id: int, project_id: int, price: int, project_data: tuple):
    """Update price in project"""
    update_project_price(user_id=user_id, price=price, project_id=project_id)
    # Write log
    write_log(user_id=user_id, log_text=f'User with id: {user_id}, update project with id: {project_id},'
                                        f'New price: {price}')

    my_project_tasks = all_tasks_of_one_project(user_id=user_id, project_id=project_id)
    for task in my_project_tasks:
        if task[6] == 'separately':
            pass
        else:

            tasks_part_price = all_project_tasks_part_price(user_id=user_id, project_id=project_id)
            all_time = sum([i[4] for i in tasks_part_price])
            money = (price / all_time) * int(task[4])
            update_task_price(user_id=user_id, price=int(money), task_id=task[0], money_type='part')

    return {"status": True,
            "auth_token_status": "active",
            "id": project_id,
            "price": price,
            "date": datetime.datetime.now()}


@check_task_id
def service_update_task_price(user_id: int, project_task_data: tuple, project_task_id: id, price: int, money_type: int):
    """Update price in task and project"""
    project_data = get_project_by_id(user_id=user_id, project_id=project_task_data[0][1])
    # Check change money type
    if money_type == 1 and project_task_data[0][6] == 'separately':
        money_type = 'separately'

    elif money_type == 1 and project_task_data[0][6] == 'part':
        money_type = 'separately'
        update_project_price(user_id=user_id, price=int(project_data[0][4]) - price, project_id=project_task_data[0][1])

    elif money_type == 0 and project_task_data[0][6] == 'separately':
        money_type = 'part'
        if project_data[0][4] >= price:
            update_project_price(user_id=user_id, price=int(project_data[0][4]) + price,
                                 project_id=project_task_data[0][1])
        else:
            return {"status": False,
                    "auth_token_status": "active",
                    "money_type": "active",
                    "description": "bad price. You can't separate task price bigger then project price",
                    "date": datetime.datetime.now()}

    elif money_type == 0 and project_task_data[0][6] == 'part':
        money_type = 'part'
        update_project_price(user_id=user_id, price=project_data[0][4] + price, project_id=project_task_data[0][1])

    else:
        return {"status": False,
                "auth_token_status": "active",
                "money_type": False,
                "description": "money type not valid",
                "date": datetime.datetime.now()}
    update_task_price(user_id=user_id, price=price, task_id=project_task_id, money_type=money_type)
    # Write log
    write_log(user_id=user_id, log_text=f'User with id: {user_id}, update task with id: {project_task_id},'
                                        f'New price: {price}')
    return {"status": True,
            "auth_token_status": "active",
            "task_id": project_task_id,
            "price": price,
            "money_type": money_type,
            "date": datetime.datetime.now()}


@check_project_currency_id
def service_update_project_currency(user_id: int, project_id: int, currency: str):
    """Update price in currency"""
    update_project_currency(user_id=user_id, currency=currency, project_id=project_id)
    # Write log
    write_log(user_id=user_id, log_text=f'User with id: {user_id}, update project with id: {project_id},'
                                        f'New currency: {currency}')
    return {"status": True,
            "auth_token_status": "active",
            "id": project_id,
            "currency": currency,
            "date": datetime.datetime.now()}


@check_project_id
def service_delete_project(user_id: str, project_id: int, project_data: tuple):
    delete_project(user_id=user_id, project_id=project_id)
    # Write log
    write_log(user_id=user_id, log_text=f'User with id: {user_id}, delete project with id: {project_id}')
    return {"status": True,
            "auth_token_status": "active",
            "description": "project deleted successfully",
            "date": datetime.datetime.now()}


@check_task_id
def service_delete_project_task(user_id: int, project_task_id: int, project_task_data: tuple):
    delete_project_task(user_id=user_id, project_task_id=project_task_id)
    # Write log
    write_log(user_id=user_id,
              log_text=f'User with id: {user_id}, '
                       f'delete project task with id: {project_task_id}')
    return {"status": True,
            "auth_token_status": "active",
            "description": "project task deleted successfully",
            "date": datetime.datetime.now()}
