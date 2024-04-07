import pytest

# Импортируем класс клиента.
from django.test.client import Client
from django.utils import timezone
from django.conf import settings

from datetime import datetime, timedelta

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment



@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass

@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client

@pytest.fixture
def anonimus_client():
    client = Client()
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст news',
    )
    return news

@pytest.fixture
def news_list():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def pk_for_args(news):  
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (news.id,)

@pytest.fixture
# Фикстура запрашивает другую фикстуру создания коммент.
def comment_author(news, author):  
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    comment = Comment.objects.create(  # Создаём объект заметки.
        news=news,
        text='Текст comment',
        author=author,
    )
    return comment

@pytest.fixture
def comment_list(news, author):
    today = datetime.today()
    all_news = [
        Comment(
            news=news,
            author=author,
            text=f'Просто текст {index}.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            created=today - timedelta(days=index)
        )
        for index in range(settings.COMMENTS_COUNT_ON_NEWS_PAGE + 1)
    ]
    Comment.objects.bulk_create(all_news)

@pytest.fixture
# Фикстура запрашивает другую фикстуру создания заметки.
def pk_comment_for_args(comment_author):  
    # И возвращает кортеж, который содержит slug заметки.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (comment_author.id,)

@pytest.fixture
def form_data(news, author):
    return {
        'news':news,
        'text':'Новый Текст comment',
        'author':author,
    }
