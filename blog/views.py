from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector
from .forms import EmailPostForm, CommentForm, SearchForm


# на основе класса 1
# class PostListView(ListView):
#     """Запрос всех опубликованных статей"""
#     queryset = Post.objects.all()
#     context_object_name = 'posts'  # по умолчанию используется object_list
#     paginate_by = 3  # переменная page_obj отвечает за постраничный вывод
#     template_name = 'blog/post/list.html'  # по умолчанию blog/post_list


# на основе функции 1
def post_list(request, tag_slug=None):
    """Запрос всех опубликованных статей"""
    object_list = Post.objects.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)  # по 3 статьи на каждой странице
    page = request.GET.get('page')  # извлекаем текущую страницу
    try:
        posts = paginator.page(page)  # cписок объектов на нужной странице
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'page': page,
        'tag': tag
    }
    return render(request, 'blog/post/list.html', context)


def post_detail(request, year, month, day, post):
    """Получение статьи по указанным слагу и дате"""
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                             publish__month=month, publish__day=day)
    # Список всех активных комментариев для этой статьи.
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # пользователь отправил комментарий
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комментарий но не сохраняем его в БД (новый объект Comment)
            new_comment = comment_form.save(commit=False)
            # привязываем комментарий к текущей статье.
            new_comment.post = post  # модель Comment
            # print(new_comment.post, 'пост')
            # print(new_comment.name)
            # print(new_comment.email)
            # print(new_comment.body)

            # сохраняем комментарий в БД
            new_comment.save()
    else:
        comment_form = CommentForm()

    # Формирование списка похожих статей
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    context = {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts
    }

    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    """Получение статьи по идентификатору"""
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # форма была отправлена на сохранение
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию
            cd = form.cleaned_data
            # Отправка электронной почты
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cd["name"]} {cd["email"]} recommends you reading {post.title}'
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'thehamcoree@gmail.com',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    context = {
        'post': post,
        'form': form,
        'sent': sent
    }

    return render(request, 'blog/post/share.html', context)


def post_search(request):
    """Обработчик поиска статей"""
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # формируем запрос на поиск статей
            results = Post.objects.annotate(
                search=SearchVector('title', 'body'),
            ).filter(search=query)

    context = {
        'form': form,
        'query': query,
        'results': results
    }

    return render(request, 'blog/post/search.html', context)
