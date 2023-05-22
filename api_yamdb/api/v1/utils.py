import uuid

from django.core.mail import send_mail

from api_yamdb.settings import ADMIN_EMAIL


def get_and_send_confirmation_code(user):
    for u in user:
        u.confirmation_code = str(uuid.uuid4()).split("-")[0]
        u.save()
        send_mail(
            "Код подтверждения",
            f'Код подтверждения "{u.username}": {u.confirmation_code}',
            ADMIN_EMAIL,
            [u.email],
        )
