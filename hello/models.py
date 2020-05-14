from django.db import models


__all__ = [
    'Visitor',
]


class Visitor(models.Model):
    useragent = models.TextField()
