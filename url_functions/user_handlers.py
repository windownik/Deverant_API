
from modules.little_funcs import create_token
from modules.send_confirm_email import send_email
from modules.sqLite import *
import sha512_crypt


def check_user_mail(mail: str):
    """Check user mail on coincidence in database"""
    status = find_email(mail=mail)
    if str(status) == "[]":
        return {"mail in database": False}
    else:
        return {"mail in database": True}


def login(mail: str, password: str):
    """Create new auth token, save it in database and return to user"""
    user_id = get_user_id_by_email(email=mail, password=password)
    if user_id:
        auth_token, _secret = create_token()
        secret_hash = sha512_crypt.encrypt(_secret)
        data = datetime.datetime.now() + datetime.timedelta(days=30)
        create_auth_token(user_id=user_id, auth_token=auth_token, secret_hash=secret_hash, status='active',
                          dead_time=data, creat_time=datetime.datetime.now())
        return {"status": True,
                "user_auth": auth_token,
                "secret_key": _secret,
                "date": datetime.datetime.now()}
    else:
        return {"status": False,
                "description": 'email or password Error',
                "date": datetime.datetime.now()}


def logout(user_auth: str,):
    """This method delete user's auth token"""
    user_id = get_id_by_auth(auth_token=user_auth)
    if str(user_id) == '[]':
        return {"status": False,
                "description": "auth_token not valid",
                "date": datetime.datetime.now()}
    else:
        delete_auth_token(user_auth=user_auth)
        return {"status": True,
                "description": "user logout",
                "date": datetime.datetime.now()}


def confirm_email(user_auth: str, email_cod: str):
    """Confirm email"""
    user_id, status = get_id_by_auth(auth_token=user_auth)
    confirm_cod_in_db = get_user_status(user_id)
    if str(confirm_cod_in_db[0][0]).lower() == email_cod.lower():
        update_user_status(user_id=user_id)
        return {"status": True,
                "description": "your email is confirm",
                "date": datetime.datetime.now()}
    else:
        return {"status": False,
                "description": "bad confirm cod",
                "date": datetime.datetime.now()}


def service_create_user_account(mail: str, password: str, nickname: str):
    """Create new user account if mail isn't coincidence with notes in database"""
    status = check_user_mail(mail=mail)
    if status["mail in database"]:
        return {"status": False,
                "description": 'i have same email in database'}

    salt = secrets.token_urlsafe(10)

    password_hash = sha512_crypt.encrypt(f"{password}{salt}")
    status, user_id, email_cod = create_user_account(mail=mail, hash_password=password_hash, salt=salt,
                                                     nickname=nickname)
    if status:
        # Create user's project table and user's log table
        create_table_user_projects(user_id=user_id)
        create_table_users_tasks(user_id=user_id)
        create_user_project_timework_table(user_id=user_id)
        create_table_user_log(user_id=user_id)
        user_data = login(mail=mail, password=password)
        auth_token = user_data['user_auth']
        _secret = user_data['secret_key']
        # Write first log
        write_log(user_id=user_id, log_text=f'Create user account with mail: {mail}, '
                                            f'user_id:{user_id} and nickname: {nickname}')
        try:
            send_email(user_email=mail, activated_cod=email_cod, auth_token=f"{_secret}:{auth_token}")
        except Exception as _ex:
            pass
        return {"status": True,
                "user mail": mail,
                "user_auth": auth_token,
                "secret_key": _secret,
                "description": 'check your email',
                "date": datetime.datetime.now()}
    else:
        return {"status": False,
                "description": "Error in database. Can't create new account",
                "date": datetime.datetime.now()}
