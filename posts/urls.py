from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('new/', views.new_posts, name='new_post'),
    # Профайл пользователя
    path('<str:username>/', views.profile, name='profile'),
    path("<str:username>/<int:post_id>/comment",
         views.add_comment,
         name="add_comment"
         ),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit,
         name='post_edit'
         ),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('404/', views.page_not_found, name='404'),
    path('500/', views.server_error, name='500'),
]
