from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Comment


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Создан для теста',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            text='Тест для поста',
            author=get_user_model().objects.create(username='Testname'),
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=get_user_model().objects.create(username='Testname1'),
            text='тест'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = self.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'),
            'group.html': (
                reverse('group', kwargs={'slug': 'test-slug'})),
            'profile.html': (
                reverse('profile', kwargs={'username': self.post.author})),
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context.get('group').title, self.group.title)
        self.assertEqual(response.context.get('group').description,
                         self.group.description)
        self.assertEqual(response.context.get('group').slug, self.group.slug)

    def test_index_list_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author.username
        post_group_0 = response.context.get('page')[0].group.title
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_group_0, self.group.title)


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create(username='Testname')
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Создан для теста',
            slug='test-slug'
        )
        posts = []
        for i in range(1, 12):
            posts.append(Post(
                text='Тест для поста' + str(i),
                author=cls.user,
                group=cls.group
            ))
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTests.user)

    def test_first_page_containse_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""

        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        """Проверка: на второй странице должен быть один пост."""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 1)

    def test_cache_index_page(self):
        """Проверка работы кеша"""
        response = self.guest_client.get(reverse('index'))

        Post.objects.create(
            text='Тест для поста',
            author=self.user,
            group=self.group
        )
        response2 = self.guest_client.get(reverse('index'))
        self.assertHTMLEqual(str(response), str(response2),
                             'Что-то пошло не так')
