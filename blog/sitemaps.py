from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    """Объект карты сайта"""
    changefreq = 'weekly'  # частота обновления страниц статей
    priority = 0.9  # степень их совпадения с тематикой сайта


    def items(self):
        """Возвращаем QuerySet объектов, кот. будут отображаться в карте сайта"""
        return Post.objects.all()

    def lastmod(self, obj):
        """Возвращает время последней модификации статьи"""
        return obj.updated