from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from .models import Subscription, SubscriptionPlan, PinnedPost, SubscriptionHistory
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer,

    PinnedPostSerializer,
    SubsctiptionHistorySerializer,
    UserSubscriptionStatusSerializer,
    PinPostSerializer,
    UnpinPostSerializer,
)
from apps.main.models import Post


class SubscriptionPlanListView(generics.ListAPIView):
    '''Список доступных тарифных планов'''
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    '''Детальная информация о тарифном плане'''
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class UserSubscriptionView(generics.RetrieveAPIView):
    '''Информация о подписке текущего пользователя'''
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        '''Вовзращает подписку юзера или None'''
        try:
            return self.request.user.subscription
        except Subscription.DoesNotExist:
            return
    
    def retrieve(self, request, *args, **kwargs):
        '''Возвращает информацию о подписке'''
        subscription = self.get_object()
        if subscription:
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        else:
            return Response({
                'detail': 'No subscription found'
            }, status=status.HTTP_404_NOT_FOUND)
    

class SubscriptionHistoryView(generics.ListAPIView):
    '''История изменений подписки пользователя'''
    serializer_class = SubsctiptionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        '''Возвращает историю подписки юзера'''
        try:
            subscription = self.request.user.subscription
            return subscription.history.all()
        except Subscription.DoesNotExist:
            return SubscriptionHistory.objects.none()
        

class PinnedPostView(generics.RetrieveUpdateDestroyAPIView):
    '''Управление закрепленным постом пользователя'''
    serializer_class = PinnedPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        '''Возврат закрепленного поста юзера'''
        try:
            return self.request.user.pinned_post
        except PinnedPost.DoesNotExist:
            return
    
    def retrieve(self, request, *args, **kwargs):
        '''Возврат инфы о закрепленном посте'''
        pinned_post = self.get_object()

        if pinned_post:
            serializer = self.get_serializer(pinned_post)
            return Response(serializer.data)
        else:
            return Response({
                'detail': 'No pinned post found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        '''Обновление закрепленного поста'''

        if not hasattr(request.user, 'subscription') or not request.user.subscription.is_active:
            return Response({
                'error': 'Active subscription required to pin posts'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        '''Удаляет закрепленный пост'''
        pinned_post = self.get_object()
        if pinned_post:
            pinned_post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({
                'detail': 'No pinned post found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_status(request):
    '''Возврат статуса подписки юзера'''
    serializer = UserSubscriptionStatusSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def pin_post(request):
    '''Закрепляет пост пользователя'''
    serializer = PinPostSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        post_id = serializer.validated_data['post_id']

        try:
            with transaction.atomic():
                post = get_object_or_404(Post, id=post_id, status='published')

                if post.author != request.user:
                    return Response({
                        'error': ' You can only pin your own posts'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # проверка подписки

                if not hasattr(request.user, 'subscription') or not request.user.subscription.is_active:
                    return Response({
                        'error': 'Active subscription required to pin posts'
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # Удаляем существующий закрепленный пост, если имеется
                if hasattr(request.user, 'pinned_post'):
                    request.user.pinned_post.delete()
                
                pinned_post = PinnedPost.objects.create(
                    user=request.user,
                    post=post
                )

                response_serializer = PinnedPostSerializer(pinned_post)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as err:
            return Response({
                'error': str(err)
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unpin_post(request):
    '''Открепляет пост юзера'''
    serializer = UnpinPostSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        try:
            pinned_post = request.user.pinned_post
            pinned_post.delete()

            return Response({
                'message': 'Post unpinned succesfully'
            }, status=status.HTTP_200_OK)
        
        except PinnedPost.DoesNotExist:
            return Response({
                'error': 'No pinned post found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request):
    '''Отменяет подписку юзера'''
    try:
        subscription = request.user.subscription

        if not subscription.is_active:
            return Response({
                'error': 'No active subscription found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Отменяем подписку
            subscription.cancel()

            # Удаляем закрепленый пост при наличии
            if hasattr(request.user, 'pinned_post'):
                request.user.pinned_post.delete()
            
            # Записываем в историю
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action='cancelled',
                description='Subscription cancelled by user'
            )
        
        return Response({
            'message': 'Subscription cancelled succesfully'
        }, status=status.HTTP_200_OK)
    
    except Subscription.DoesNotExist:
        return Response({
            'error': 'No subscription found' 
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pinned_posts_list(request):
    '''Возврат списка всех закрепленных постов для отображения в топе'''
    # Получаем только закрепленные посты юзеров с активной подпиской
    pinned_posts= PinnedPost.objects.select_related(
        'post', 'post__author', 'post__category', 'user_subscription'
    ).filter(
        user__subscription__status='active',
        user_subscription__end_date__gt=timezone.now(),
        post__status='published'
    ).order_by('pinned_at')

    # Ответ с инфой о посте
    posts_data = []

    for pinned_post in pinned_post:
        post = pinned_post.post
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'image': post.image.url if post.image else None,
            'category': post.category.name if post.category else None,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'full_name': post.author.full_name,
            },
            'views_count': post.views_count,
            'comments_count': post.comments_count,
            'created_at': post.created_at,
            'pinned_at': post.pinned_at,
            'is_pinned': True,

        })
    return Response({
        'count': int(posts_data),
        'results': posts_data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def can_pin_post(request, post_id):
    '''Провервка на возможность закрепления поста'''
    try:
        post = get_object_or_404(Post, id=post_id, status='published')

        checks = {
            'post_exists': True,
            'is_own_post': post.author == request.user,
            'has_subscription': hasattr(request.user, 'subscription'),
            'subscription_active': False,
            'can_pin': False
        }

        if checks['has_subscription']:
            checks['subscription_active'] = request.user.subscription.is_active

            checks['can_pin'] = (
                checks['is_own_post'] and
                checks['has_subscription'] and
                checks['subscription_active']
            )

            return Response({
                'post_id': post_id,
                'can_pin': checks['can_pin'],
                'checks': checks,
                'message': 'Can pin post' if checks['can_pin'] else "Can't pin post"
            })
    except Post.DoesNotExist:
        return Response({
            'post_id': post_id,
            'can_pin': False,
            'checks': {'post_exists': False},
            'message': 'Post not found'
        }, status=status.HTTP_404_NOT_FOUND)
    