from django.views.generic import ListView
from django.db.models import Count
from .models import *


class VisitorListView(ListView):
    model = Visitor

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.values('useragent').annotate(count=Count('id'))
        return queryset

    def dispatch(self, request, *args, **kwargs):
        self.model.objects.create(useragent=request.META.get('HTTP_USER_AGENT', '-'))
        return super().dispatch(request, *args, **kwargs)
