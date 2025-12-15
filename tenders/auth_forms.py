from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """Custom signup form - username is staff number for auto-linking to employee"""

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Staff Number (e.g., 71188)'
            }),
        }
        help_texts = {
            'username': 'Enter your staff number to access the system.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
        # Update username label
        self.fields['username'].label = 'Staff Number'

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Try to get employee data based on staff number
        from .models import Employee
        employee = Employee.objects.filter(employee_id=user.username).first()
        
        if employee:
            # Populate user data from employee record
            user.email = employee.email
            user.first_name = employee.first_name
            user.last_name = employee.last_name
        
        if commit:
            user.save()
            # Assign default "Tender Staff" role
            from django.contrib.auth.models import Group
            try:
                default_group = Group.objects.get(name='Tender Staff')
                user.groups.add(default_group)
            except Group.DoesNotExist:
                pass  # Group will be created by setup_groups command
            
            # UserProfile will be auto-created by signal and auto-linked if employee exists
        
        return user
