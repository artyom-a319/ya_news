# conftest.py
from datetime import datetime, timedelta
import pytest

# Импортируем класс клиента.
from django.test.client import Client
from django.utils import timezone

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment


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
def news(author):
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def form_data_comment():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def form_data_edit_comment():
    return {
        'text': 'Текст комментария',
    }


@pytest.fixture
def last_11_news():
    all_news = []
    # Изменённый цикл для корректного использования index
    for index in range(11):
        today = datetime.today()
        news = News(title=f'Новость {index}', text='Просто текст.')
        news.date = today - timedelta(days=index)  # Устанавливаем дату на основе index
        all_news.append(news)
    News.objects.bulk_create(all_news)  # Создаём все новости сразу



@pytest.fixture
def last_11_comments(news, author):
    # Изменённый цикл для корректного использования index
    today = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(news=news, author=author, text='Просто текст.')
        comment.created = today - timedelta(days=index)  # Устанавливаем дату на основе index
        comment.save()


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(  # Создаём объект заметки.
        text='Текст заметки',
        news=news,
        author=author,
    )
    return comment