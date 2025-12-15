from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# User Profile to link User with Employee
class UserProfile(models.Model):
    """Extended user profile to link system users with employee records"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee = models.OneToOneField('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_account')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.employee.full_name if self.employee else 'No employee linked'}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when User is created"""
    if created:
        # Try to find matching employee by staff number (username)
        employee = None
        try:
            employee = Employee.objects.filter(employee_id=instance.username).first()
        except Exception:
            pass
        UserProfile.objects.create(user=instance, employee=employee)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # If profile doesn't exist, create it (for existing users)
        try:
            employee = Employee.objects.filter(employee_id=instance.username).first()
            UserProfile.objects.create(user=instance, employee=employee)
        except Exception:
            pass


# Lookup Models
class Region(models.Model):
    """Geographic regions"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(models.Model):
    """Organizational departments"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Division(models.Model):
    """Organizational divisions within departments"""
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='divisions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'name']
        unique_together = ['department', 'name']

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Section(models.Model):
    """Organizational sections within divisions"""
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='sections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['division', 'name']
        unique_together = ['division', 'name']

    def __str__(self):
        return f"{self.division.name} - {self.name}"


class ProcurementType(models.Model):
    """Types of procurement methods"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LOAStatus(models.Model):
    """Letter of Award Status"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "LOA Status"
        verbose_name_plural = "LOA Statuses"

    def __str__(self):
        return self.name


class ContractStatus(models.Model):
    """Contract status types"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Contract Status"
        verbose_name_plural = "Contract Statuses"

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Employee information - can exist independently of user accounts"""
    employee_id = models.CharField(max_length=50, unique=True, help_text="Staff number/Employee ID")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Organizational structure
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    
    # Employment details
    job_title = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Tender(models.Model):
    """Main tender tracking model"""
    # Requisition and identification
    shopping_cart = models.CharField(max_length=100, blank=True, null=True)
    requisition_number = models.CharField(max_length=100, blank=True, null=True)
    tender_id = models.CharField(max_length=100, unique=True)
    egp_tender_reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="eGP Tender Reference")
    kengen_tender_reference = models.CharField(max_length=100, blank=True, null=True, verbose_name="KenGen Tender Reference")
    
    # Description and classification
    tender_description = models.TextField()
    procurement_type = models.ForeignKey(ProcurementType, on_delete=models.SET_NULL, null=True, related_name='tenders')
    
    # Location and assignment
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='tenders')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='tenders')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenders')
    user = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tenders', verbose_name="Assigned User")
    
    # Creators
    tender_creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_tenders')
    contract_creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contracts')
    
    # Important dates
    tender_advert_date = models.DateField(blank=True, null=True)
    tender_closing_date = models.DateField(blank=True, null=True)
    tender_closing_time = models.TimeField(blank=True, null=True)
    tender_validity_expiry_date = models.DateField(blank=True, null=True)
    
    # Evaluation details
    tender_evaluation_duration = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 30 Days, 21 Days")
    
    # Status and contract information
    loa_status = models.ForeignKey(LOAStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenders', verbose_name="LOA Status")
    contract_status = models.ForeignKey(ContractStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenders')
    
    # Purchase orders
    e_purchase_order_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="e-Purchase Order No")
    sap_purchase_order_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="SAP Purchase Order No")
    
    # Financial
    estimated_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-tender_advert_date', '-created_at']

    def __str__(self):
        return f"{self.tender_id} - {self.tender_description[:50]}"


class TenderOpeningCommittee(models.Model):
    """Many-to-many relationship for tender opening committee members"""
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='opening_committee_members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='opening_committees')
    role = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Chairperson, Member, Secretary")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tender', 'employee']
        verbose_name = "Tender Opening Committee Member"
        verbose_name_plural = "Tender Opening Committee Members"

    def __str__(self):
        return f"{self.tender.tender_id} - {self.employee.full_name}"


class TenderEvaluationCommittee(models.Model):
    """Many-to-many relationship for tender evaluation committee members"""
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='evaluation_committee_members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluation_committees')
    role = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Chairperson, Technical Evaluator, Financial Evaluator")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tender', 'employee']
        verbose_name = "Tender Evaluation Committee Member"
        verbose_name_plural = "Tender Evaluation Committee Members"

    def __str__(self):
        return f"{self.tender.tender_id} - {self.employee.full_name}"
