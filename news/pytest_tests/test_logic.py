
from http import HTTPStatus
import pytest

from news.forms import CommentForm

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data_comment, news):
    DETAIL_URL = reverse('news:detail', args=[news.id])
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.   
    client.post(DETAIL_URL, data=form_data_comment)
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, form_data_comment, news):
    DETAIL_URL = reverse('news:detail', args=[news.id])
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.   
    response = author_client.post(DETAIL_URL, data=form_data_comment)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{DETAIL_URL}#comments')
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Убеждаемся, что есть один комментарий.
    assert comments_count == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == form_data_comment['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    DETAIL_URL = reverse('news:detail', args=[news.id])
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.   
    response = author_client.post(DETAIL_URL, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(comment, author_client, news):
    DELETE_URL = reverse('news:delete', args=[comment.id])
    DETAIL_URL = reverse('news:detail', args=[news.id])
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    response = author_client.delete(DELETE_URL)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Заодно проверим статус-коды ответов.
    assertRedirects(response, f'{DETAIL_URL}#comments')
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(comment, not_author_client, news):
    DELETE_URL = reverse('news:delete', args=[comment.id])
    # Выполняем запрос на удаление от пользователя-читателя.
    response = not_author_client.delete(DELETE_URL)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(comment, author_client, news, form_data_edit_comment):
    EDIT_URL = reverse('news:edit', args=[comment.id])
    DETAIL_URL = reverse('news:detail', args=[news.id])
    # Выполняем запрос на редактирование от имени автора комментария.
    response = author_client.post(EDIT_URL, data=form_data_edit_comment)
    # Проверяем, что сработал редирект.
    assertRedirects(response, f'{DETAIL_URL}#comments')
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert comment.text == form_data_edit_comment['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(comment, not_author_client, news, form_data_edit_comment):
    EDIT_URL = reverse('news:edit', args=[comment.id])
    COMMENT_TEXT = comment.text
    # Выполняем запрос на редактирование от имени другого пользователя.
    response = not_author_client.post(EDIT_URL, data=form_data_edit_comment)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == COMMENT_TEXT
