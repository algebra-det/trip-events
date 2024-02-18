import random, requests, os, json

from django.core.mail import send_mail
from django.conf import settings

def get_code():
    code = str()
    for _ in range(4):
        num = random.randint(0,9)
        code+=str(num)
    return code


def sending_email(email_subject, email_body, email_to):
    send_mail(
        email_subject,
        email_body,
        'no-reply@dignitech.com',
        [email_to],
        fail_silently=True,
    )



def sending_code(random_code, email_to, phone, usage):
    email_subject = 'Verification Code'
    email_body = 'Below is the verification code:\n{}'.format(random_code)
    email_to = email_to
    sending_email(email_subject, email_body, email_to)

    # To Phone

    if usage == 'register':
        ContentID = os.environ.get('SMS_CONTENT_ID')

    elif usage == 'forgot_password':
        ContentID = os.environ.get('SMS_CONTENT_ID')
        # response = requests.post(
        #     "https://bulksmsapi.vispl.in/",
        #     data=request_body,
        #     headers={"Content-Type": "application/json"}
        # )
        # print(request_body)
        # print(response.json()['status'])

    else:
        ContentID = os.environ.get('SMS_CONTENT_ID')

    response = requests.get(
        """https://bulksmsapi.vispl.in/?
        username={}&
        password={}&
        messageType=text&senderId={}&
        ContentID={}&
        EntityID={}&
        message=Hola%20Amigo!,%20Your%20Login%20OTP%20Is%20{}.%20In%20case%20you%20have%20not%20requested%20for%20OTP,%20Please%20contact%20us%20at%20support@migo.com.%20Thanks,%20TribeTraveller%20Tech.&
        mobile={}"""
            .format(
                os.environ.get('SMS_USERNAME'),
                os.environ.get('SMS_PASSWORD'),
                os.environ.get('SMS_SENDER_ID'),
                ContentID,
                os.environ.get('SMS_ENTITY_ID'),
                random_code,
                phone
            )
    )

    print(response.text)
    if response.status_code == 200:
        if "Message submitted successfully" in response.text:
            return True
        return False
    return False


def sending_invite(email_to):
    email_subject = 'Invitation for Cultrendweb game'
    email_body = """
        Ciao,

        sono (Nama of user cultrend), ti volevo invitare a partecipare ad una campagna GameTour su Cultrend, una app innovatva che ti permette di guadagnare premi fantastici partecipando a delle challanges.

        Per scoprire di più visita il sito web oppure scarica l'app.

        Ti avviso che è in corso un evento ed a breve le iscrizioni termineranno ! Non perdere l'occasione, vieni a scoprire di cosa sto parlando ! 
        ----
        Object: Invito Cultrend """
    email_to = email_to
    sending_email(email_subject, email_body, email_to)
