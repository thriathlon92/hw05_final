from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from django.urls import reverse
from yatube.settings import PAGE_SIZE

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment


def index(request):
    post_list = Post.objects.select_related('group')
    paginator = Paginator(post_list, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    paginator = Paginator(posts, PAGE_SIZE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'page': page,
        'posts': posts,
        'paginator': paginator,
    }
    return render(request, 'group.html', context)


@login_required
def new_posts(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()

            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count = post_list.count()
    context = {
        'author': author,
        'page': page,
        'count': count,
        'paginator': paginator,
    }

    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    count = Post.objects.filter(author=post.author).select_related(
        'author').count()
    comments = Comment.objects.filter(post_id=post.pk)
    form = PostForm(request.POST or None)
    return render(request, 'post.html', {
        'author': post.author,
        'post': post,
        'count': count,
        'post_id': post_id,
        'comments': comments,
        'form': form,
    })


@login_required
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=request.user.username,
                            post_id=post_id)

    return render(
        request, 'new.html', {'form': form, 'post': post, 'is_edit': True},
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            form.save()
            return redirect('post', username=username, post_id=post_id)
    return render(request, 'post.html',
                  {'post': post, 'author': post.author, 'form': form})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
