# from django.core.management.base import BaseCommand
# from reviews.models import (Genre, Title, Category, GenreTitle,
#                             User, Review, Comment)
# import pandas as pd


# class Command(BaseCommand):
#     def handle(
#         self,
#         *args,
#         **options
#     ):
#         """Заполняем датафреймы"""
#         df_genre = pd.read_csv('static/data/genre.csv', index_col='id')
#         df_category = pd.read_csv('static/data/category.csv', index_col='id')
#         df_titles = pd.read_csv('static/data/titles.csv')
#         df_genre_title = pd.read_csv('static/data/genre_title.csv',
#                                      index_col='id')
#         df_users = pd.read_csv('static/data/users.csv')
#         df_review = pd.read_csv('static/data/review.csv')
#         df_comment = pd.read_csv('static/data/comments.csv')

#         """Заполняем Genre и Category с предобработкой данных."""
#         Genre.objects.all().delete()
#         Category.objects.all().delete()
#         df_gen_cat = [(df_genre, Genre), (df_category, Category)]
#         for df, db in df_gen_cat:
#             df.dropna(inplace=True)
#             df.drop_duplicates('slug', inplace=True)
#             """Наполняем базы."""
#             for ind in df.index:
#                 db.objects.create(slug=df.loc[ind, 'slug'],
#                                   name=df.loc[ind, 'name'])

#         """Заполняем Title с предобработкой данных."""
#         Title.objects.all().delete()
#         df_titles.dropna(inplace=True)
#         df_titles.drop_duplicates('id', inplace=True)
#         df_titles = df_titles.merge(df_category[['slug']],
#                                     how='left',
#                                     left_on='category',
#                                     right_on='id').set_index('id')

#         for ind in df_titles.index:
#             Title.objects.create(
#                 id=ind,
#                 name=df_titles.loc[ind, 'name'],
#                 year=df_titles.loc[ind, 'year'],
#                 category=Category.objects.get(
#                     slug=df_titles.loc[ind, 'slug']
#                 )
#             )
#         """Заполняем GenreTitle."""
#         GenreTitle.objects.all().delete()
#         for ind in df_genre_title.index:
#             title_ind = df_genre_title.loc[ind, "title_id"]
#             genre_ind = df_genre_title.loc[ind, "genre_id"]
#             if title_ind in df_titles.index and genre_ind in df_genre.index:
#                 genre_slug = df_genre.loc[genre_ind, 'slug']
#                 GenreTitle.objects.create(
#                     id=ind,
#                     title=Title.objects.get(pk=title_ind),
#                     genre=Genre.objects.get(slug=genre_slug)
#                 )

#         """Заполняем User и предобработка."""
#         User.objects.all().delete()
#         df_users.drop_duplicates('username', inplace=True)
#         df_users.drop_duplicates('email', inplace=True)
#         df_users = df_users[['id', 'username', 'email', 'role']]
#         for ind in df_users.index:
#             data = df_users.loc[ind].to_dict()
#             User.objects.create(**data)

#         """Заполняем Review."""
#         Review.objects.all().delete()
#         df_review.drop_duplicates('id', inplace=True)
#         df_review.dropna(inplace=True)
#         df_review.rename(columns={'title_id': 'title'}, inplace=True)
#         for ind in df_review.index:
#             title_ind = df_review.loc[ind, 'title']
#             author_ind = df_review.loc[ind, 'author']
#             if (title_ind in df_titles.index
#                     and author_ind in df_users['id'].values):
#                 title = Title.objects.get(pk=title_ind)
#                 author = User.objects.get(pk=author_ind)
#                 Review.objects.create(
#                     id=df_review.loc[ind, 'id'],
#                     title=title,
#                     author=author,
#                     score=df_review.loc[ind, 'score'],
#                     text=df_review.loc[ind, 'text'],
#                     pub_date=df_review.loc[ind, 'pub_date']
#                 )

#         """Заполняем Comment."""
#         Comment.objects.all().delete()
#         df_comment.drop_duplicates('id', inplace=True)
#         df_comment.dropna(inplace=True)
#         df_comment.rename(columns={'review_id': 'review'}, inplace=True)
#         for ind in df_comment.index:
#             review_ind = df_comment.loc[ind, 'review']
#             author_ind = df_comment.loc[ind, 'author']
#             if (
#                 review_ind in df_review['id'].values and author_ind
#                 in df_users['id'].values
#             ):
#                 review = Review.objects.get(pk=review_ind)
#                 author = User.objects.get(pk=author_ind)
#                 Comment.objects.create(
#                     id=df_comment.loc[ind, 'id'],
#                     review=review,
#                     author=author,
#                     text=df_comment.loc[ind, 'text'],
#                     pub_date=df_comment.loc[ind, 'pub_date']
#                 )
