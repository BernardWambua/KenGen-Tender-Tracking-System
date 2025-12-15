"""
Management command to create user groups and assign permissions for role-based access control
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tenders.models import (
    Tender, Employee, Region, Department, Division, Section,
    ProcurementType, LOAStatus, ContractStatus,
    TenderOpeningCommittee, TenderEvaluationCommittee
)


class Command(BaseCommand):
    help = 'Create user groups and assign permissions for role-based access control'

    def handle(self, *args, **kwargs):
        # Define groups and their permissions
        groups_permissions = {
            'Tender Admin': {
                'description': 'Full access to all tender management features and bulk uploads',
                'models': [
                    Tender, Employee, Region, Department, Division, Section,
                    ProcurementType, LOAStatus, ContractStatus,
                    TenderOpeningCommittee, TenderEvaluationCommittee
                ],
                'permissions': ['add', 'change', 'delete', 'view']
            },
            'Tender Manager': {
                'description': 'Can create and manage tenders, view lookup data',
                'models': [Tender, TenderOpeningCommittee, TenderEvaluationCommittee],
                'permissions': ['add', 'change', 'view'],
                'view_only': [Region, Department, Division, Section, ProcurementType, LOAStatus, ContractStatus, Employee]
            },
            'Tender Staff': {
                'description': 'Can view tenders and basic data entry',
                'models': [Tender],
                'permissions': ['add', 'view'],
                'view_only': [
                    Employee, Region, Department, Division, Section,
                    ProcurementType, LOAStatus, ContractStatus,
                    TenderOpeningCommittee, TenderEvaluationCommittee
                ]
            }
        }

        for group_name, config in groups_permissions.items():
            # Create or get the group
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Group already exists: {group_name}'))
                # Clear existing permissions
                group.permissions.clear()

            # Add permissions for models
            for model in config['models']:
                content_type = ContentType.objects.get_for_model(model)
                
                for perm_type in config['permissions']:
                    codename = f'{perm_type}_{model._meta.model_name}'
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=content_type
                        )
                        group.permissions.add(permission)
                        self.stdout.write(f'  Added {perm_type} permission for {model.__name__}')
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  Permission {codename} does not exist')
                        )

            # Add view-only permissions
            if 'view_only' in config:
                for model in config['view_only']:
                    content_type = ContentType.objects.get_for_model(model)
                    codename = f'view_{model._meta.model_name}'
                    try:
                        permission = Permission.objects.get(
                            codename=codename,
                            content_type=content_type
                        )
                        group.permissions.add(permission)
                        self.stdout.write(f'  Added view permission for {model.__name__}')
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  Permission {codename} does not exist')
                        )

            self.stdout.write(
                self.style.SUCCESS(f'Configured {group_name}: {config["description"]}\n')
            )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Successfully created all groups and assigned permissions!')
        )
        self.stdout.write('\nTo assign users to groups, use:')
        self.stdout.write('  python manage.py shell')
        self.stdout.write('  >>> from django.contrib.auth.models import User, Group')
        self.stdout.write('  >>> user = User.objects.get(username="username")')
        self.stdout.write('  >>> group = Group.objects.get(name="Tender Admin")')
        self.stdout.write('  >>> user.groups.add(group)')
