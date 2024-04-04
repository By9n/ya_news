import pytest

from django.urls import reverse

from django.conf import settings
from django.urls import reverse


from news.models import News, Comment
from news.forms import CommentForm

@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        # ('news:delete', pytest.lazy_fixture('pk_comment_for_args')),
    )
)
def test_news_count(client, name, args, news_list):
    
    url = reverse(name, args=args)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

# @pytest.mark.parametrize(
#     'name, args',
#     (
#         ('news:detail', pytest.lazy_fixture('pk_for_args')),
#         # ('news:delete', pytest.lazy_fixture('pk_comment_for_args')),
#     )
# )
@pytest.mark.parametrize(
       'parametrized_client, comment_form',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('anonimus_client'), False),
)
)
def test_authorized_client_has_form(parametrized_client, pk_for_args, comment_form):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        url = reverse('news:detail', args=pk_for_args)
        response = parametrized_client.get(url)
        assert ('form' in response.context) is comment_form
        # Проверим, что объект формы соответствует нужному классу формы.
        if comment_form:
            assert isinstance(response.context['form'], CommentForm) is comment_form

# def test__list_for_different_users(
#         # Используем фикстуру заметки и параметры из декоратора:
#         note, parametrized_client, note_in_list
# ):
#     url = reverse('notes:list')
#     # Выполняем запрос от имени параметризованного клиента:
#     response = parametrized_client.get(url)
#     object_list = response.context['object_list']
#     # Проверяем истинность утверждения "заметка есть в списке":
#     assert (note in object_list) is note_in_list   
# @pytest.mark.parametrize(
#     # Задаём названия для параметров:
#     'parametrized_client, note_in_list',
#     (
#         # Передаём фикстуры в параметры при помощи "ленивых фикстур":
#         (pytest.lazy_fixture('author_client'), True),
#         (pytest.lazy_fixture('not_author_client'), False),
#     )
# )
# def test_notes_list_for_different_users(
#         # Используем фикстуру заметки и параметры из декоратора:
#         note, parametrized_client, note_in_list
# ):
#     url = reverse('notes:list')
#     # Выполняем запрос от имени параметризованного клиента:
#     response = parametrized_client.get(url)
#     object_list = response.context['object_list']
#     # Проверяем истинность утверждения "заметка есть в списке":
#     assert (note in object_list) is note_in_list
