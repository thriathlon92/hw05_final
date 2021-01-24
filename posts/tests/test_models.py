from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post, Comment


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='ж' * 200,
            description='Создан для теста'
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Заголовок',
            'description': 'Описание',
            'slug': 'Адрес страници группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = self.group
        field_help_texts = {
            'title': 'Название группы',
            'slug': ('Укажите адрес для страницы группы. '
                     'Используйте только латиницу, цифры, '
                     'дефисы и знаки подчёркивания'),
            'description': 'Опишите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта записано значение поля title."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostCommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тест для поста',
            author=get_user_model().objects.create(username='Testname'))
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=get_user_model().objects.create(username='Testname1'),
            text='тест'
        )

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст',
            'group': 'group',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_verbose_name_comment(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = self.comment
        field_verboses = {
            'text': 'Комментарий',
            'author': 'Автор',
            'created': 'Дата публикации'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'text': 'Текст поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта  записано значение поля post.title."""
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
