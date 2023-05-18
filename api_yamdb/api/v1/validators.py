from rest_framework import serializers


def validate_username(name):
    if name == "me":
        raise serializers.ValidationError()
    elif name is None or name == "":
        raise serializers.ValidationError()
    return name


def validate_email(email):
    if email is None or email == "":
        raise serializers.ValidationError()
    return email
