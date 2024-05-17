from django.db.models import Manager, Count
from django.db.models.query import QuerySet
from django.utils import timezone


class PostManager(Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).annotate(
            comment_count=Count('comments')
        ).select_related(
            'author',
            'category',
            'location',
        ).order_by(
            '-pub_date',
        )
