from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_list_or_404

from .models import Category, Post
from .serializers import (
    CategorySerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
)
from .permissions import IsAuthorOrReadOnly


class CategoryListCreateView(generics.ListCreateAPIView):
    '''API endpoint для категорий'''

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryDetailView(generics.RetrieveUpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        '''Посты с учётом прав доступа'''

        queryset = Post.objects.select_related('author', 'category')

        # Фильтрация по правам доступа
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        else:
            queryset = queryset.filter(
                Q(status='published') | Q(author=self.request.user))
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateUpdateSerializer
        return PostListSerializer


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    '''API endpoint для конкретного поста'''

    queryset = Post.objects.select_related('author', 'category')
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        '''Увеличивает счётчик просмотров при GET'''
        instance = self.get_object()

        if request.method == 'GET':
            instance.increment_views()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MyPostsView(generics.ListAPIView):
    '''API endpoint для постов юзера'''

    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'views_count', '']
    ordering = ['-created_at']

    def get_queryset(self):
        return Post.objects.filter(
            author=self.request.user,
            ).select_related('author', 'category')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def popular_posts(request):
    '''10 популярных постов'''
    score_posts = 10

    posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-views_count')[:score_posts]

    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_posts(request):
    '''10 популярных постов'''
    score_posts = 10

    posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-created_at')[:score_posts]

    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def post_by_category(request, category_slug):
    '''Посты определенной категории'''

    category = get_list_or_404(Category, slug=category_slug)
    posts = Post.objects.filter(
        category=category,
        status='published'
    ).select_related('author', 'category').order_by('-created_at')

    serializer = PostListSerializer(posts, many=True, context={'request': request})
    return Response({
        'category': CategorySerializer(category).data,
        'posts': serializer.data
    })