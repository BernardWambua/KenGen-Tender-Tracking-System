import calendar
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

# User Profile to link User with Employee
class UserProfile(models.Model):
    """Extended user profile to link system users with employee records"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee = models.OneToOneField('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_account')
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_user_profiles')
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
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_regions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(models.Model):
    """Organizational departments"""
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_departments')
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
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_divisions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['department', 'name']
        unique_together = ['department', 'name']

    def __str__(self):
        return self.name


class Section(models.Model):
    """Organizational sections within divisions"""
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='sections')
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_sections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['division', 'name']
        unique_together = ['division', 'name']

    def __str__(self):
        return self.name


class LOAStatus(models.Model):
    """Letter of Award Status"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_loa_statuses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "e-Contract Step"
        verbose_name_plural = "e-Contract Steps"

    def __str__(self):
        return self.name


class ContractStatus(models.Model):
    """e-Contract Status types"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contract_statuses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "e-Contract Status"
        verbose_name_plural = "e-Contract Statuses"

    def __str__(self):
        return self.name


class Currency(models.Model):
    """Supported contract currencies"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_currencies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Country(models.Model):
    """Countries of origin"""
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_countries')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

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
    
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_employees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Requisition(models.Model):
    """Requisition details created before a tender"""
    SHOPPING_CART_STATUS_CHOICES = [
        ('APPROVED', 'Approved'),
        ('PENDING', 'Pending'),
        ('BUDGET_ISSUE', 'Budget Issue'),
    ]

    PROCUREMENT_TYPE_CHOICES = [
        ('TENDER', 'Tender'),
        ('QUOTATION', 'Quotation'),
    ]

    e_requisition_no = models.CharField(max_length=100, unique=True, verbose_name="e-Requisition No")
    requisition_description = models.TextField()
    shopping_cart_no = models.PositiveBigIntegerField()
    shopping_cart_amount = models.DecimalField(max_digits=15, decimal_places=2)
    shopping_cart_status = models.CharField(max_length=20, choices=SHOPPING_CART_STATUS_CHOICES)

    # Organizational structure (captured at requisition stage)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='requisitions')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='requisitions')
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisitions')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='requisitions')

    assigned_user = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requisitions',
        verbose_name="Owner(DO)"
    )

    procurement_type = models.CharField(max_length=20, choices=PROCUREMENT_TYPE_CHOICES)
    tender_creator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisition_tender_creations'
    )
    date_assigned = models.DateField()
    creation_deadline = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_requisitions')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.e_requisition_no}"

    def save(self, *args, **kwargs):
        if self.date_assigned:
            deadline_days = getattr(settings, 'REQUISITION_CREATION_DEADLINE_DAYS', 7)
            self.creation_deadline = self.date_assigned + timedelta(days=deadline_days)

        super().save(*args, **kwargs)


class Tender(models.Model):
    """Main tender tracking model"""
    # Requisition and identification
    requisition = models.ForeignKey(
        Requisition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tenders'
    )
    tender_id = models.PositiveIntegerField(unique=True)
    tender_reference_number = models.CharField(max_length=150)
    tender_creation_date = models.DateField()

    # Description and classification
    tender_description = models.TextField()

    ELIGIBILITY_CHOICES = [
        ('INTERNATIONAL', 'Open International'),
        ('NATIONAL', 'Open National'),
        ('CITIZEN_CONTRACTOR', 'Citizen Contractor'),
        ('AGPO', 'AGPO'),
    ]
    AGPO_CATEGORY_CHOICES = [
        ('PLWD', 'PLWD'),
        ('YOUTH', 'Youth'),
        ('WOMEN', 'Women'),
    ]
    eligibility = models.CharField(max_length=20, choices=ELIGIBILITY_CHOICES)
    agpo_category = models.CharField(max_length=20, choices=AGPO_CATEGORY_CHOICES, blank=True, null=True)

    PROCUREMENT_METHOD_CHOICES = [
        ('OPEN_TENDER', 'Open Tender'),
        ('RESTRICTED_TENDER', 'Restricted Tender'),
        ('REQUEST_FOR_QUOTATION', 'Request for Quotation'),
        ('DIRECT_PROCUREMENT', 'Direct Procurement'),
        ('REQUEST_FOR_PROPOSAL', 'Request for Proposal'),
        ('EXPRESSION_OF_INTEREST', 'Expression of Interest'),
        ('PREQUALIFICATION', 'Pre-Qualification'),
        ('FRAMEWORK', 'Framework'),

    ]
    procurement_method = models.CharField(max_length=30, choices=PROCUREMENT_METHOD_CHOICES, blank=True, null=True)
    # Approval and workflow
    TENDER_APPROVAL_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CLARIFICATION_REQUESTED', 'Clarification Requested'),
    ]
    tender_approval_status = models.CharField(max_length=30, choices=TENDER_APPROVAL_STATUS_CHOICES, blank=True, null=True)

    TENDER_STEP_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('EVALUATION', 'Evaluation'),
        ('NEGOTIATION', 'Negotiation'),
        ('CANCELLED', 'Cancelled'),
    ]
    tender_step = models.CharField(max_length=20, choices=TENDER_STEP_CHOICES, blank=True, null=True)

    # Creators
    tender_creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_tenders')

    # Important dates
    proposed_advert_date = models.DateField(blank=True, null=True)
    tender_advert_date = models.DateField(blank=True, null=True)
    tender_closing_date = models.DateField(blank=True, null=True)
    tender_closing_time = models.TimeField(blank=True, null=True)
    tender_opening_date = models.DateField(blank=True, null=True)
    tender_opening_time = models.TimeField(blank=True, null=True)
    tender_validity_expiry_date = models.DateField(blank=True, null=True)
    tender_validity_days = models.PositiveIntegerField(blank=True, null=True, help_text="Validity period in days")
    
    # Evaluation details
    tender_evaluation_duration_days = models.PositiveIntegerField(blank=True, null=True, help_text="Evaluation duration in days")
    tender_evaluation_end_date = models.DateField(blank=True, null=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tender_records')

    class Meta:
        ordering = ['-tender_advert_date', '-created_at']

    def __str__(self):
        return f"{self.tender_id} - {self.tender_description[:50]}"

    def save(self, *args, **kwargs):
        if not self.tender_creation_date:
            self.tender_creation_date = datetime.now().date()

        if self.eligibility != 'AGPO':
            self.agpo_category = None

        if self.tender_creation_date and (not self.proposed_advert_date or self.proposed_advert_date.weekday() != 2):
            self.proposed_advert_date = self._get_next_proposed_advert_date(self.tender_creation_date)

        if self.tender_closing_date:
            self.tender_opening_date = self.tender_closing_date

        if self.tender_closing_date and self.tender_closing_time:
            opening_datetime = datetime.combine(self.tender_closing_date, self.tender_closing_time) + timedelta(minutes=30)
            self.tender_opening_time = opening_datetime.time()

        base_validity_date = self.tender_opening_date or self.tender_closing_date
        if base_validity_date and self.tender_validity_days is not None:
            self.tender_validity_expiry_date = base_validity_date + timedelta(days=self.tender_validity_days)

        if self.tender_opening_date and self.tender_evaluation_duration_days is not None:
            self.tender_evaluation_end_date = self.tender_opening_date + timedelta(days=self.tender_evaluation_duration_days)

        if self.tender_evaluation_duration_days is None and self.requisition_id:
            procurement_type = getattr(self.requisition, 'procurement_type', None)
            if procurement_type:
                self.tender_evaluation_duration_days = 21 if procurement_type == 'QUOTATION' else 30
                if self.tender_opening_date:
                    self.tender_evaluation_end_date = self.tender_opening_date + timedelta(days=self.tender_evaluation_duration_days)

        super().save(*args, **kwargs)

    @staticmethod
    def _get_next_proposed_advert_date(base_date):
        days_dict = {
            0: 9,   # Monday -> Wed week after next
            1: 8,   # Tuesday -> Wed week after next
            2: 7,   # Wednesday -> Next Wed
            3: 6,   # Thursday -> Next Wed
            4: 12,  # Friday -> Wed week after next
            5: 11,  # Saturday -> Wed week after next
            6: 10   # Sunday -> Wed week after next
        }
        days_to_add = days_dict.get(base_date.weekday())
        return base_date + timedelta(days=days_to_add)
    @property
    def days_remaining_to_opening(self):
        target_date = self.tender_opening_date or self.tender_closing_date
        if not target_date:
            return None
        return (target_date - datetime.now().date()).days

    @property
    def days_remaining_for_evaluation(self):
        if not self.tender_evaluation_end_date:
            return None
        return (self.tender_evaluation_end_date - datetime.now().date()).days


class Contract(models.Model):
    """Contract information linked to a tender"""
    # Link to tender (OneToOne relationship - each tender can have one contract)
    tender = models.OneToOneField(Tender, on_delete=models.CASCADE, related_name='contract')
    
    DURATION_MEASURE_CHOICES = [
        ('DAYS', 'Days'),
        ('MONTHS', 'Months'),
        ('YEARS', 'Years'),
    ]

    RESPONSIBILITY_CHOICES = [
        ('CONTRACT_CREATOR', 'Contract Creator'),
        ('SUPPLIER', 'Supplier'),
        ('LEGAL', 'Legal'),
        ('HOP', 'Head of Procurement'),
        ('AO', 'Accounting Officer'),
        ('TENDER_CREATOR', 'Tender Creator'),
    ]

    CONTRACT_STEP_CHOICES = [
        ('ION', 'Intention of Notification'),
        ('LOA', 'Letter of Award'),
        ('ARB', 'ARB Decision'),
        ('DRAFT', 'Draft Contract'),
        ('FINAL', 'Final Contract'),
    ]

    # Contract reference
    contract_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    contract_title = models.CharField(max_length=255, blank=True, null=True)
    
    # Contract creator
    contract_creator = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contracts')

    # Contract duration and dates
    contract_duration_measure = models.CharField(max_length=10, choices=DURATION_MEASURE_CHOICES, blank=True, null=True)
    contract_duration = models.PositiveIntegerField(blank=True, null=True)
    commencement_date = models.DateField(blank=True, null=True)
    contract_expiry_date = models.DateField(blank=True, null=True)

    # Contract financial details
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    contract_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    
    # Supplier information
    contractor_supplier = models.CharField(max_length=200, blank=True, null=True)
    country_of_origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    
    # Security information
    tender_security_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    tender_security_validity_days = models.PositiveIntegerField(blank=True, null=True)
    tender_security_expiry_date = models.DateField(blank=True, null=True)
    performance_security_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    performance_security_duration_days = models.PositiveIntegerField(blank=True, null=True)
    performance_security_expiry_date = models.DateField(blank=True, null=True)
    
    # Status information
    contract_step = models.CharField(max_length=20, choices=CONTRACT_STEP_CHOICES, blank=True, null=True)
    contract_status = models.ForeignKey(ContractStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='contracts')
    responsibility = models.CharField(max_length=50, choices=RESPONSIBILITY_CHOICES, blank=True, null=True)
    
    # Delivery
    contract_delivery_period_measure = models.CharField(max_length=10, choices=DURATION_MEASURE_CHOICES, blank=True, null=True)
    contract_delivery_period = models.PositiveIntegerField(blank=True, null=True)
    
    # Purchase orders
    e_purchase_order_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="eGP Purchase Order No")
    sap_purchase_order_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="SAP Purchase Order No")
    
    # Audit fields
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contract_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contract for {self.tender.tender_id}"

    @staticmethod
    def add_months(start_date, months):
        if not start_date or months is None:
            return None
        month_index = start_date.month - 1 + months
        year = start_date.year + month_index // 12
        month = month_index % 12 + 1
        day = min(start_date.day, calendar.monthrange(year, month)[1])
        return start_date.replace(year=year, month=month, day=day)

    def save(self, *args, **kwargs):
        if self.commencement_date and self.contract_duration and self.contract_duration_measure:
            if self.contract_duration_measure == 'DAYS':
                self.contract_expiry_date = self.commencement_date + timedelta(days=self.contract_duration)
            elif self.contract_duration_measure == 'MONTHS':
                self.contract_expiry_date = self.add_months(self.commencement_date, self.contract_duration)
            elif self.contract_duration_measure == 'YEARS':
                self.contract_expiry_date = self.add_months(self.commencement_date, self.contract_duration * 12)

        if self.commencement_date and self.tender_security_validity_days is not None:
            self.tender_security_expiry_date = self.commencement_date + timedelta(days=self.tender_security_validity_days)

        if self.commencement_date and self.performance_security_duration_days is not None:
            self.performance_security_expiry_date = self.commencement_date + timedelta(days=self.performance_security_duration_days)

        super().save(*args, **kwargs)


class TenderOpeningCommittee(models.Model):
    """Many-to-many relationship for tender opening committee members"""
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('CHAIR', 'Chair'),
        ('SECRETARY', 'Secretary'),
    ]
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='opening_committee_members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='opening_committees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_opening_committee_members')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tender', 'employee']
        verbose_name = "Tender Opening Committee Member"
        verbose_name_plural = "Tender Opening Committee Members"

    def __str__(self):
        return f"{self.tender.tender_id} - {self.employee.full_name}"


class TenderEvaluationCommittee(models.Model):
    """Many-to-many relationship for tender evaluation committee members"""
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('CHAIR', 'Chair'),
        ('SECRETARY', 'Secretary'),
    ]
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='evaluation_committee_members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='evaluation_committees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_evaluation_committee_members')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tender', 'employee']
        verbose_name = "Tender Evaluation Committee Member"
        verbose_name_plural = "Tender Evaluation Committee Members"

    def __str__(self):
        return f"{self.tender.tender_id} - {self.employee.full_name}"


class ContractCITCommittee(models.Model):
    """Many-to-many relationship for contract CIT/Inspection & Acceptance committee members"""
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('CHAIR', 'Chair'),
        ('SECRETARY', 'Secretary'),
    ]
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='cit_committee_members')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='cit_committees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    created_by = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_cit_committee_members')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['contract', 'employee']
        verbose_name = "CIT/Inspection & Acceptance Committee Member"
        verbose_name_plural = "CIT/Inspection & Acceptance Committee Members"

    def __str__(self):
        return f"{self.contract.tender.tender_id} - {self.employee.full_name}"
