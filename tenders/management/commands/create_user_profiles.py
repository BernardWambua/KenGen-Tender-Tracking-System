from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tenders.models import UserProfile, Employee


class Command(BaseCommand):
    help = 'Create UserProfile for all existing users and auto-link to employees if username matches employee_id'

    def handle(self, *args, **kwargs):
        users_processed = 0
        profiles_created = 0
        auto_linked = 0

        for user in User.objects.all():
            users_processed += 1
            
            # Check if profile already exists
            if hasattr(user, 'profile'):
                self.stdout.write(f'  Profile already exists for {user.username}')
                continue
            
            # Try to find matching employee by username (staff number)
            employee = None
            try:
                employee = Employee.objects.filter(employee_id=user.username).first()
                if employee:
                    auto_linked += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created profile for {user.username} and linked to {employee.full_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Created profile for {user.username} (no matching employee)')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Error finding employee for {user.username}: {e}')
                )
            
            # Create the profile
            UserProfile.objects.create(user=user, employee=employee)
            profiles_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Processed {users_processed} users')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Created {profiles_created} profiles')
        )
        self.stdout.write(
            self.style.SUCCESS(f'✓ Auto-linked {auto_linked} users to employees')
        )
