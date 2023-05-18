from django.core.management.base import BaseCommand
from reviews.models import Genre, Title, Category, GenreTitle
from django.test import Client
from django.db.models import Count
from pprint import pprint


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('тут будет наполнение базы')