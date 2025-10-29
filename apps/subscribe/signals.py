from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Subscription, PinnedPost, SubscriptionHistory


@receiver(post_save, sender=Subscription)
def subscription_post_save(sender, instance, created, **kwargs):
    '''Обработчик сохранения подписки'''

    if created:
        # Создаем запись в истории при создании подписки
        SubscriptionHistory.objects.create(
            subscription=instance,
            action='created',
            description=f'Subscription created for plan {instance.plan.name}'
        )
    else:
        # Проверка на изменения статуса
        if hasattr(instance, '_previous_status'):

            if instance._previous_status != instance.status:
                SubscriptionHistory.objects.create(
                    subscription=instance,
                    action=instance.status,
                    description=f'Subscription status changed from {instance._previous_status} to {instance.status}')


@receiver(pre_delete, sender=Subscription)
def subscription_pre_delete(sender, instance, **kwargs):
    '''Обработчик удаления подписки'''

    try:
        instance.user.pinned_post.delete()
    except PinnedPost.DoesNotExist:
        pass


@receiver(post_save, sender=PinnedPost)
def pinned_post_post_save(sender, instance, created, **kwargs):
    '''Обработчик сохранения закрепленного поста'''
    
    if created:
        # Проверка на наличие у юзера активной подписки
        if not hasattr(instance.user, 'subscription') or not instance.user.subscription.is_active:
            instance.delete()
            return

        # Записываем в историю подписки
        SubscriptionHistory.objects.create(
            subscription=instance.user.subscription,
            action='post_pinned',
            description=f'Post "{instance.post.title}" pinned',

            metadata={
                'post_id': instance.post.id,
                'post_title': instance.post.title,
            }
        )


@receiver(post_save, sender=PinnedPost)
def pinned_post_pre_save(sender, instance, **kwargs):
    '''Обработчик удаления закрепленного поста'''
    if not hasattr(instance.user, 'subscription'):
        # Записываем в историю подписки
        SubscriptionHistory.objects.create(
            subscription=instance.user.subscription,
            action='post_unpinned',
            description=f'Post "{instance.post.title}" unpinned',

            metadata={
                'post_id': instance.post.id,
                'post_title': instance.post.title,
            }
        )