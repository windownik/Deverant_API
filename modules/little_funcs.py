from modules.sqLite import get_token_status
import secrets
import datetime


def create_token():
    """Create new token and check him in db"""
    auth_token = secrets.token_urlsafe(30)
    _secret = secrets.token_urlsafe(16)
    status = True
    while status:
        auth = get_token_status(auth_token=auth_token)
        if auth is None or str(auth) == '[]':
            status = False
        else:
            pass
    return str(auth_token), str(_secret)


def data_time_validation(start: str, end: str):
    """Check start and end datatime text"""
    try:
        start = datetime.datetime.strptime(str(start), "%Y-%m-%d %H:%M:%S.%f")
    except:
        start = False
    try:
        end = datetime.datetime.strptime(str(end), "%Y-%m-%d %H:%M:%S.%f")
    except:
        end = False
    if end and start:
        if end > start:
            time_delta = end - start
            return start, end, time_delta.seconds
        else:
            return False, False, False
    else:
        return False, False, False