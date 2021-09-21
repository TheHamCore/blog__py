from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post


class LatestPostsFeed(Feed):
    title = 'My blog'
    link = '/blog/'
    description = 'New posts of my blog.'

    def items(self):  # объекты, которые будут включены в рассылку
        return Post.objects.all()[:5]

    def item_title(self, item):  # получаем из item заголовок
        return item.title

    def item_description(self, item):  # получаем из item description
        return truncatewords(item.body, 30)
