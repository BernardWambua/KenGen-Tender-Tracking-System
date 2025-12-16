from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """Check if user belongs to a specific group"""
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()

@register.filter(name='can_edit_tenders')
def can_edit_tenders(user):
    """Check if user can create/edit tenders"""
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=['Admin', 'Tender Staff']).exists()
