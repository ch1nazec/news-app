from celery import shared_task
from django.utils import timezone
from .models import Subscription, PinnedPost, SubscriptionHistory


@shared_task
def check_subscriptions():
    '''Периодическая задача для проверки истекших подписок'''
    now = timezone.now()

    expired_subscriptions = Subscription.objects.filter(
        status='active',
        end_date__lt=now,
    )

    expired_count = 0
    pinned_posts_removed = 0

    for subscription in expired_subscriptions:
        subscription.delete()
        expired_count += 1

        # Удалить закрп. пост если есть
        try:
            pinned_post = subscription.user.pinned_post
            pinned_post.delete()

            pinned_posts_removed += 1
        except PinnedPost.DoesNotExist:
            pass

        # Запись в историю
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action='expired',
            description='Subscription expired authomatically'
        )
    
    return {
        'expired_subscriptions': expired_count,
        'pinned_posts_removed': pinned_posts_removed
    }


@shared_task
def send_subscription_expiry_reminder():
    '''Отправка напоминаний о скором истечении подписки'''

    from datetime import timedelta
    from django.core.mail import send_mail
    from django.conf import settings

    # Находим подписки, которые истекают через 3 дня
    reminder_date = timezone.now() + timedelta(days=3)

    expiring_subscriptions = Subscription.objects.filter(
        status='active',
        end_date__date=reminder_date.date(),
        auto_renew=False
    )

    send_count = 0

    for subscription in expiring_subscriptions:
        try:
            send_mail(
                subject='Your subscription is expiring soon',
                message=f'Dear {subscription.user.get_full_name() or subscription.user.username},\n\n'
                       f'Your {subscription.plan.name} subscription will expire on {subscription.end_date.strftime("%B %d, %Y")}.\n\n'
                       f'To continue enjoying premium features, please renew your subscription.\n\n'
                       f'Best regards,\nNews Site Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.user.email],
                fail_silently=True,
            )
            send_count += 1
        except Exception as e:
            # Логирование ошибки, но продолжаем воркать
            print(f'Failed to send reminder {subscription.user.email}: {e}')
    
    return {'reminders_sent': send_count}