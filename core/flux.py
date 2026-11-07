"""Flux RSS des articles publiés (/articles/rss/)."""
from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.utils import timezone

from .models import Article


class FluxArticles(Feed):
    title = "Basile Bagoudou — Notes de data"
    link = "/articles/"
    description = "Ce que j'apprends en travaillant sur mes projets data, avec le code."

    def items(self):
        return Article.objects.filter(publie=True)[:20]

    def item_title(self, item):
        return item.titre_fr

    def item_description(self, item):
        return item.resume_fr

    def item_pubdate(self, item):
        return timezone.make_aware(datetime.combine(item.date_publication, time(9)))
