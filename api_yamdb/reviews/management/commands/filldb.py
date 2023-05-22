import pandas as pd

from django.core.management.base import BaseCommand

from reviews.models import (Genre, Title, Category, GenreTitle,
                            User, Review, Comment)


class Command(BaseCommand):

    df_genre = pd.read_csv('static/data/genre.csv')
    df_category = pd.read_csv('static/data/category.csv')
    df_title = pd.read_csv('static/data/titles.csv')
    df_genre_title = (
        pd.read_csv('static/data/genre_title.csv')
        .rename(columns={'genre_id': 'genre', 'title_id': 'title'})
    )
    df_user = pd.read_csv('static/data/users.csv')[['id',
                                                    'username',
                                                    'email',
                                                    'role']]
    df_review = (pd.read_csv('static/data/review.csv')
                 .rename(columns={'title_id': 'title'}))
    df_comment = pd.read_csv('static/data/comments.csv')
    df = {
        'genre': (df_genre, Genre, 'slug'),
        'category': (df_category, Category, 'slug'),
        'title': (df_title, Title, 'id'),
        'genre_title': (df_genre_title, GenreTitle, 'id'),
        'author': (df_user, User, 'id'),
        'review': (df_review, Review, 'id'),
        'comment': (df_comment, Comment, 'id')
    }

    def correct_df(self, data, name):
        data.dropna(inplace=True)
        data.drop_duplicates(name, inplace=True)

    def check_all_df(self):
        """Убираем дубликаты потенциальных ключей и пустые значения."""
        for tek in self.df:
            self.correct_df(self.df[tek][0], self.df[tek][2])

    def data_translate(self, data):
        """Функция для преобразуем id объектов в объекты."""
        for el in data:
            if el in ['genre', 'category']:
                df_t = self.df[el][0]  # Датасет соответствующего элемента
                class_el = self.df[el][1]
                el_id = data[el]
                if el_id in df_t['id'].values:
                    slug = df_t.set_index('id').loc[el_id, 'slug']
                    data[el] = class_el.objects.get(slug=slug)
                else:
                    return None

            if el in ['author', 'title', 'review']:
                df_t = self.df[el][0]  # Датасет соответствующего элемента
                class_el = self.df[el][1]
                el_id = data[el]
                if el_id in df_t['id'].values:
                    data[el] = class_el.objects.get(pk=el_id)
                else:
                    return None

        return data

    def handle(self, *args, **options):

        self.check_all_df()

        for elem in self.df:
            df_t = self.df[elem][0]
            class_t = self.df[elem][1]
            class_t.objects.all().delete()

            for ind in df_t.index:
                data = df_t.loc[ind].to_dict()
                data = self.data_translate(data)
                if data:
                    if elem in ['genre', 'category']:
                        data.pop('id')
                    class_t.objects.create(**data)

            print(f'Таблица <{class_t.name}> наполнена тестовыми данными.'
                  f' Количество записей - {class_t.objects.count()}.')
