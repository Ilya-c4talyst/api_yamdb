from django.core.exceptions import ValidationError


def custom_username_validator(value):
    if value.lower() == 'me':
        raise ValidationError('Username cannot be "me".')
