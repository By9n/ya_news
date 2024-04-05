import pytest

from django.urls import reverse

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_news_count(client, news_list):
    url = reverse('news:home')  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert (all_dates == sorted_dates)


def test_comments_order(client, pk_for_args, comment_list):
    url = reverse('news:detail', args=pk_for_args)
    response = client.get(url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert ('news' in response.context)
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # Собираем временные метки всех новостей.
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки, менять порядок сортировки не надо.
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что id первого комментария меньше id второго.
    assert (all_timestamps == sorted_timestamps)


@pytest.mark.parametrize(
    'parametrized_client, comment_form',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('anonimus_client'), False),
    )
)
def test_has_form_for_different_users(
    parametrized_client, pk_for_args, comment_form
):
    url = reverse('news:detail', args=pk_for_args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is comment_form
    # Проверим, что объект формы соответствует нужному классу формы.
    if comment_form:
        assert isinstance(
            response.context['form'], CommentForm) is comment_form
