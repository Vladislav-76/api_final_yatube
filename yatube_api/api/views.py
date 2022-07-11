from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import filters
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404

from posts.models import Post, Comment, Group, Follow
from .serializers import (PostSerializer, CommentSerializer, GroupSerializer,
                          FollowSerializer)
from .permissions import IsAuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    """
    Получение всех публикаций. Работают параметры limit и offset.
    Добавление новой публикации. Анонимные запросы запрещены.
    Получение публикации по id.
    Обновление публикации по id только автором. Анонимные запросы запрещены.
    Частичное обновление публикации только автором. Анонимные запрещены.
    Удаление публикации по id только автором. Анонимные запросы запрещены.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Получение всех комментариев к публикации.
    Добавление нового комментария к публикации. Анонимные запросы запрещены.
    Получение комментария к публикации по id.
    Обновление комментария только автором комментария. Анонимные запрещены.
    Частичное обновление комментария только автором. Анонимные запрещены.
    Удаление комментария по id только автором. Анонимные запросы запрещены.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def post_from_url(self):
        post_id = self.kwargs.get("post_id")
        return get_object_or_404(Post, pk=post_id)

    def get_queryset(self):
        new_queryset = Comment.objects.filter(
            post=self.post_from_url())
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            post=self.post_from_url()
        )


class GroupViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """
    Получение списка доступных сообществ.
    Получение информации о сообществе по id.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class FollowViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """
    Возвращает подписки пользователя. Анонимные запросы запрещены.
    Создает подписку пользователя от имени которого сделан запрос
    на пользователя переданного в теле запроса. Подписываться на себя
    запрещено. Дублировать подписки запрещено. Анонимные запросы запрещены.
    """
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        new_queryset = Follow.objects.filter(user=self.request.user)
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,)
