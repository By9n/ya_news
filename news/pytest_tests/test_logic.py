import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from pytils.translit import slugify
from django.urls import reverse

from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


# Указываем фикстуру form_data в параметрах теста.
def test_user_can_create_comment(author_client, author, form_data, pk_for_args):
    url = reverse('news:detail', args=pk_for_args)
    # Создаём пользователя и клиент, логинимся в клиенте
    # В POST-запросе отправляем данные, полученные из фикстуры form_data:
    response = author_client.post(url, data=form_data)
    # Проверяем, что был выполнен редирект на страницу успешного добавления commenta:
    assertRedirects(response, f'{url}#comments')
    # Считаем общее количество comments в БД, ожидаем 1.
    assert Comment.objects.count() == 1
    # Чтобы проверить значения полей заметки -
    # получаем её из базы при помощи метода get():
    new_comment = Comment.objects.get()
    # Сверяем атрибуты объекта с ожидаемыми.
    assert new_comment.news == form_data['news']
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(anonimus_client, form_data, pk_for_args, news):
    url = reverse('news:detail', args=pk_for_args)
    # Через анонимный клиент пытаемся создать заметку:
    response = anonimus_client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, pk_for_args, form_data):
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    url = reverse('news:detail', args=pk_for_args)
    form_data['text'] = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url, data=form_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert (comments_count == 0)


def test_author_can_delete_comment(
    author_client, pk_comment_for_args, pk_for_args, comment_author
):
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    url = reverse('news:delete', args=(pk_comment_for_args))
    response = author_client.delete(url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Адрес новости.
    news_url = reverse('news:detail', args=(pk_comment_for_args))
    url_to_comments = news_url + '#comments'
    # Заодно проверим статус-коды ответов.
    assertRedirects(response, url_to_comments)
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    assert (comments_count == 0)


def test_not_author_cant_delete_comment_of_another_user(
    not_author_client, pk_comment_for_args  
):
    url = reverse('news:delete', args=(pk_comment_for_args))
    # Выполняем запрос на удаление от пользователя-читателя.
    response = not_author_client.delete(url)
    # Проверяем, что вернулась 404 ошибка.
    assert (response.status_code == HTTPStatus.NOT_FOUND)
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert (comments_count == 1)


def test_author_can_edit_comment(
    author_client, pk_comment_for_args, pk_for_args, comment_author,
    form_data
):
    # Выполняем запрос на редактирование от имени автора комментария.
    url = reverse('news:edit', args=(pk_comment_for_args))
    response = author_client.post(url, data=form_data)
    # Проверяем, что сработал редирект.
    news_url = reverse('news:detail', args=(pk_for_args))
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    # Обновляем объект комментария.
    comment_author.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert (comment_author.text == form_data['text'])


def test_not_author_cant_edit_comment_of_another_user(
    not_author_client, pk_comment_for_args, form_data,
    comment_author

):
    url = reverse('news:edit', args=(pk_comment_for_args))
    # Выполняем запрос на удаление от пользователя-читателя.
    response = not_author_client.post(url, data=form_data)
    # Проверяем, что вернулась 404 ошибка.
    assert (response.status_code == HTTPStatus.NOT_FOUND)
    # Убедимся, что комментарий по-прежнему на месте.
    comment_author.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert (comment_author.text != form_data['text'])
