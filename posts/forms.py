from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'group': 'Выберите группу',
                  'text': 'Введите текст',
                  'image': 'Картинка',
                  }
        help_texts = {
            'group': 'выберите группу',
            'text': 'ввидите новую запись',
            'image': 'загрузите картинку поста',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = ('Добавьте комментарий',)

