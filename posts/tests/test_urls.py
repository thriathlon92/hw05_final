from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_static_pages_response(self):
        urls = {
            reverse('index'): 200,
            reverse('about:author'): 200,
            reverse('about:tech'): 200,
        }
        for key, value in urls.items():
            response = self.guest_client.get(key)
            self.assertEqual(response.status_code, value)


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='тестовый заголовок',
            description='Создан для теста',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            text='Тест для поста',
            author=get_user_model().objects.create(username='Testname'),
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_url_for_guest_client(self):
        """Страница / доступна любому пользователю."""
        urls = {
            reverse('index'): 200,
            reverse('group', args=[self.group.slug]): 200,
            reverse('new_post'): 302,
            reverse('profile', kwargs={'username': self.post.author}): 200,
            reverse('post', kwargs={'username': self.post.author,
                                    'post_id': self.post.pk}): 200,
            reverse('post_edit', kwargs={'username': self.post.author.username,
                                         'post_id': self.post.pk}): 302,
            '/weird/url/': 404,
            reverse('add_comment',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk
                            }): 302,
            reverse('profile_follow',
                    kwargs={'username': self.post.author.username}): 302,
            reverse('profile_unfollow',
                    kwargs={'username': self.post.author.username}): 302,
        }
        for key, value in urls.items():
            response = self.guest_client.get(key)
            self.assertEqual(response.status_code, value)

    def test_detail_url_exists_at_desired_location_authorized(self):
        """Страница доступна авторизованному пользователю."""
        urls = {
            reverse('index'): 200,
            reverse('group', args=[self.group.slug]): 200,
            reverse('new_post'): 200,
            reverse('profile',
                    kwargs={'username': self.post.author.username}): 200,
            reverse('post', kwargs={'username': self.post.author.username,
                                    'post_id': self.post.pk}): 200,
            reverse('post_edit', kwargs={'username': self.post.author.username,
                                         'post_id': self.post.pk}): 200,
            reverse('add_comment',
                    kwargs={'username': self.post.author.username,
                            'post_id': self.post.pk}): 200,
        }
        for key, value in urls.items():
            response = self.authorized_client.get(key)
            self.assertEqual(response.status_code, value)

    def test_post_list_url_redirect_anonymous_on_admin_login(self):
        """Страница /new/ и edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        urls = {
            reverse('new_post'): f"/auth/login/?next={reverse('new_post')}",
            reverse('post_edit', kwargs={'username': self.post.author,
                                         'post_id': self.post.id}
                    ): f"/auth/login/?next=/{self.post.author}/{self.post.pk}/edit/",
        }
        for key, value in urls.items():
            response = self.guest_client.get(key, follow=True)
            self.assertRedirects(response, value)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', args=[self.group.slug]),
            'new.html': reverse('new_post'),
            'profile.html': reverse('profile',
                                    kwargs={'username': self.post.author}),
            'post.html': reverse('post', kwargs={'username': self.post.author,
                                                 'post_id': self.post.pk}),
            'misc/404.html': '/404/',
        }
        for key, value in templates_url_names.items():
            with self.subTest(url=value):
                response = self.authorized_client.get(value)
                self.assertTemplateUsed(response, key)

    def test_new_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        response = self.authorized_client.get(reverse(
            'post_edit', kwargs={
                'username': self.post.author.username,
                'post_id': self.post.pk,
            }
        )
        )
        self.assertTemplateUsed(response, 'new.html')
