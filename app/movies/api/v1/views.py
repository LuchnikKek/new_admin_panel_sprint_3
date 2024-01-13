from typing import Dict

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import Filmwork, PersonFilmworkRole


class MovisApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self) -> QuerySet:
        filmwork_qs: QuerySet = Filmwork.objects.values('id', 'title', 'description', 'creation_date', 'rating', 'type')
        genres_expr = ArrayAgg('genres__name', distinct=True)
        # плюрализация через добавление 's', не смог придумать лучше
        roles_exprs = {
            role + 's': ArrayAgg('persons__full_name', filter=Q(personfilmwork__role__exact=role), distinct=True)
            for role in PersonFilmworkRole.values
        }
        return filmwork_qs.annotate(genres=genres_expr, **roles_exprs,)

    def render_to_response(self, context, **response_kwargs) -> JsonResponse:
        return JsonResponse(context)


class MoviesListApi(MovisApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs) -> Dict:
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            self.get_queryset(),
            self.paginate_by
        )
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "results": list(page.object_list),
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
        }
        return context


class MoviesDetailApi(MovisApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs) -> Dict:
        pk = self.kwargs.get('pk')
        return self.get_queryset().get(pk=pk)
