import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.form = PostForm()
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='Testmane1')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_label(self):
        text_label = PostFormTests.form.fields['text'].label
        group_label = PostFormTests.form.fields['group'].label
        image_label = PostFormTests.form.fields['image'].label
        self.assertEqual(text_label, 'Введите текст')
        self.assertEqual(group_label, 'Выберите группу')
        self.assertEqual(image_label, 'Картинка')

    def test_help_text(self):
        text_help_text = PostFormTests.form.fields['text'].help_text
        group_help_text = PostFormTests.form.fields['group'].help_text
        image_hel_text = PostFormTests.form.fields['image'].help_text
        self.assertEqual(text_help_text, 'ввидите новую запись')
        self.assertEqual(group_help_text, 'выберите группу')
        self.assertEqual(image_hel_text, 'загрузите картинку поста')

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовая запись',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(text='Тестовая запись').exists())
