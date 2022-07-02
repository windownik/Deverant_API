import os
import smtplib


def send_email(user_email: str, activated_cod: str, auth_token: str):
    sender = "deverant.main@gmail.com"
    password = os.getenv('EMAIL_PASSWORD')
    password = '170095Ap14'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    header = 'http://45.82.69.211:443'
    # header = 'https://deverant-server.herokuapp.com'

    try:
        server.login(sender, password)
        server.sendmail(sender, user_email, f'Subject: Deverant new Account\nPlease confirm your email!\n'
                                            f'Yor activated cod:   {activated_cod}\n'
                                            f'Activated link: {header}/confirm_account/{auth_token}?email_cod='
                                            f'{activated_cod}\n\n'
                                            f'Your Deverant team')
    except Exception as _ex:
        print(_ex)
