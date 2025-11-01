import stripe
from django.core.management import BaseCommand
from django.conf import settings
from apps.subscribe.models import SubscriptionPlan

stripe.api_key = settings.STRIPE_SECRET_KEY


class Command(BaseCommand):
    help = 'Fix stripe integration by creating real products and prices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate even if stripe_price_id exists'
        )
    
    def handle(self, *args, **options):
        force = options['force']

        # Проверка на подключение к Stripe
        try:
            stripe.Balance.retrieve()
            self.stdout.write(self.style.SUCCESS('Подключение к stripe успешно'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка подключения к Stripe: {e}'))
            return
    
        plans = SubscriptionPlan.objects.filter(is_active=True)

        for plan in plans:
            self.stdout.write(f'Обработка плана: {plan.name}')

            # Нужно ли создавать план
            if plan.stripe_price_id and not force and plan.stripe_price_id.startswith(''):
                self.stdout.write(f'План уже имеет Stripe ID: {plan.stripe_price_id}')
                continue

            try:
                product = stripe.Product.create(
                    name=plan.name,
                    description=f'Description plan: {plan.name}',
                    metadata={
                        'plan_id': plan.id,
                        'django_model': 'SubscriptionPlan',
                        'created_by': 'django_management_command'
                    }
                )
                self.stdout.write(f'Продукт создан {product.id}')

                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(plan.price * 100),
                    currency='usd',
                    recurring={'interval': 'month'},
                    metadata={
                        'plan_id': plan.id,
                        'django_model': 'SubscriptionPlan',
                    }
                )
                self.stdout.write(f'Цена создана: {price.id}')

                old_id = plan.stripe_price_id
                plan.stripe_price_id = price.id
                plan.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        F'План обновления: {old_id} - {price.id}'
                    )
                )
            except stripe.StripeError as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка Stripe: {plan.name} {e}')
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Общая ошибка плана {plan.name}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Обработка завершена! проверьте Stripe DashBoard.')
        )