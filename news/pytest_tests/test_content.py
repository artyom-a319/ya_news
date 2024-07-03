from http import HTTPStatus
import pytest

from news.forms import CommentForm

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_10_news_per_page(last_11_news, client):
    # Загружаем главную страницу.
    response = client.get(reverse('news:home'))
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    # Проверяем, что на странице именно 10 новостей.
    assert news_count == 10


@pytest.mark.django_db
def test_news_order(last_11_news, client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(last_11_comments, client, news):
    response = client.get(reverse('news:detail', args=[news.id]))
    single_news = response.context['news']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [comment.created for comment in single_news.comment_set.all()]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    response = client.get(reverse('news:detail', args=[news.id]))
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    response = author_client.get(reverse('news:detail', args=[news.id]))
    assert 'form' in response.context
    # Проверим, что объект формы соответствует нужному классу формы.
    assert isinstance(response.context['form'], CommentForm)
