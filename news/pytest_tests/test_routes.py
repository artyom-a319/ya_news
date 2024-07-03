from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
# Указываем имя изменяемого параметра в сигнатуре теста.
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, url):
    url = reverse(url)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page_for_anonymous_user(client, news):
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_pages_for_author(comment, author_client):
    edit_url = reverse('news:edit', args=[comment.id])
    delete_url = reverse('news:delete', args=[comment.id])
    all_urls = [edit_url, delete_url]

    for url in all_urls:
        response = author_client.get(url)  # Выполняем запрос.
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_pages_for_reader(comment, not_author_client):
    edit_url = reverse('news:edit', args=[comment.id])
    delete_url = reverse('news:delete', args=[comment.id])
    all_urls = [edit_url, delete_url]

    for url in all_urls:
        response = not_author_client.get(url)  # Выполняем запрос.
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_redirects_for_anonymous(client, comment):
    edit_url = reverse('news:edit', args=[comment.id])
    delete_url = reverse('news:delete', args=[comment.id])
    all_urls = [edit_url, delete_url]

    for url in all_urls:
        response = client.get(url)  # Выполняем запрос.
        redirect_url = reverse('users:login') + '?next=' + url
        assertRedirects(response, redirect_url)
