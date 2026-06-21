from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Creates a super admin user'

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(email='admin@jobportal.com').exists():
            admin = CustomUser.objects.create_superuser(
                email='admin@jobportal.com',
                password='Admin@123',
                first_name='Admin',
                last_name='User',
                user_type='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {admin.email}'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))