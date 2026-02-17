from django.contrib import admin
from .models import (
    Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee, Tender, Contract, Requisition,
    TenderOpeningCommittee, TenderEvaluationCommittee, ContractCITCommittee, UserProfile,
    Currency, Country
)

# Register your models here.

# User Profile Admin
class CreatedByAdminMixin:
    def save_model(self, request, obj, form, change):
        if hasattr(obj, 'created_by') and not obj.created_by_id:
            obj.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
        super().save_model(request, obj, form, change)


@admin.register(UserProfile)
class UserProfileAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'employee', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'employee__employee_id', 'employee__first_name', 'employee__last_name']
    raw_id_fields = ['user', 'employee']


# Lookup models - simple admin
@admin.register(Region)
class RegionAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Department)
class DepartmentAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Division)
class DivisionAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'department', 'created_at']
    list_filter = ['department']
    search_fields = ['name', 'department__name']


@admin.register(Section)
class SectionAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'division', 'created_at']
    list_filter = ['division__department', 'division']
    search_fields = ['name', 'division__name']


@admin.register(ProcurementType)
class ProcurementTypeAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(LOAStatus)
class LOAStatusAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(ContractStatus)
class ContractStatusAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Currency)
class CurrencyAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['code', 'name']


@admin.register(Country)
class CountryAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


# Employee Admin
@admin.register(Employee)
class EmployeeAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = ['employee_id', 'first_name', 'last_name', 'email', 'department', 'division', 'section', 'is_active']
    list_filter = ['department', 'division', 'is_active']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'employee_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Organizational Structure', {
            'fields': ('department', 'division', 'section', 'job_title')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Requisition Admin
@admin.register(Requisition)
class RequisitionAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = [
        'e_requisition_no', 'shopping_cart_no', 'shopping_cart_amount', 'shopping_cart_status',
        'region', 'department', 'division', 'section', 'assigned_user', 'procurement_type',
        'tender_creator', 'date_assigned', 'creation_deadline', 'created_at'
    ]
    list_filter = ['region', 'department', 'division', 'section']
    search_fields = [
        'e_requisition_no', 'shopping_cart_no', 'requisition_description',
        'assigned_user__first_name', 'assigned_user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']


# Inline admins for committees
class TenderOpeningCommitteeInline(admin.TabularInline):
    model = TenderOpeningCommittee
    extra = 1
    autocomplete_fields = ['employee']


class TenderEvaluationCommitteeInline(admin.TabularInline):
    model = TenderEvaluationCommittee
    extra = 1
    autocomplete_fields = ['employee']


class ContractCITCommitteeInline(admin.TabularInline):
    model = ContractCITCommittee
    extra = 1
    autocomplete_fields = ['employee']


class ContractInline(admin.StackedInline):
    model = Contract
    extra = 0
    autocomplete_fields = ['contract_creator']
    fieldsets = (
        ('Contract Information', {
            'fields': ('contract_number', 'contract_title', 'contract_creator')
        }),
        ('Status', {
            'fields': ('contract_step', 'contract_status', 'responsibility')
        }),
        ('Supplier Information', {
            'fields': ('contractor_supplier', 'country_of_origin')
        }),
        ('Purchase Orders', {
            'fields': ('e_purchase_order_no', 'sap_purchase_order_no')
        }),
        ('Contract Dates', {
            'fields': ('commencement_date', 'contract_expiry_date', 'contract_duration_measure', 'contract_duration', 'contract_delivery_period')
        }),
        ('Financial', {
            'fields': ('contract_value', 'contract_currency')
        }),
        ('Security', {
            'fields': ('tender_security_amount', 'tender_security_validity_days', 'tender_security_expiry_date',
                      'performance_security_amount', 'performance_security_duration_days',
                      'performance_security_expiry_date')
        }),
    )


# Tender Admin
@admin.register(Tender)
class TenderAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = [
        'tender_id', 'tender_reference_number', 'tender_description_short', 'procurement_method',
        'requisition', 'tender_step', 'tender_approval_status', 'tender_advert_date',
        'tender_closing_date', 'estimated_value', 'created_by'
    ]
    list_filter = [
        'tender_step', 'tender_approval_status', 'eligibility', 'agpo_category', 'procurement_method',
        'requisition__region', 'requisition__department', 'requisition__division', 'requisition__section', 'tender_advert_date'
    ]
    search_fields = [
        'tender_id', 'tender_reference_number', 'tender_description',
        'requisition__e_requisition_no'
    ]
    autocomplete_fields = ['tender_creator', 'requisition']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'tender_advert_date'
    
    fieldsets = (
        ('Identification', {
            'fields': ('tender_id', 'tender_reference_number', 'tender_creation_date', 'requisition')
        }),
        ('Description & Classification', {
            'fields': ('tender_description', 'procurement_method', 'eligibility', 'agpo_category',
                      'tender_approval_status', 'tender_step')
        }),
        ('Creator', {
            'fields': ('tender_creator', 'created_by')
        }),
        ('Important Dates', {
            'fields': ('proposed_advert_date', 'tender_advert_date', 'tender_closing_date',
                      'tender_closing_time', 'tender_opening_date', 'tender_opening_time',
                      'tender_validity_days', 'tender_validity_expiry_date',
                      'tender_evaluation_duration_days', 'tender_evaluation_end_date')
        }),
        ('Financial', {
            'fields': ('estimated_value',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ContractInline, TenderOpeningCommitteeInline, TenderEvaluationCommitteeInline]
    
    def tender_description_short(self, obj):
        return obj.tender_description[:50] + '...' if len(obj.tender_description) > 50 else obj.tender_description
    tender_description_short.short_description = 'Description'


# Contract Admin
@admin.register(Contract)
class ContractAdmin(CreatedByAdminMixin, admin.ModelAdmin):
    list_display = [
        'tender', 'contract_number', 'contract_title', 'contract_step', 'contract_status',
        'contract_value', 'commencement_date'
    ]
    list_filter = ['contract_step', 'contract_status', 'commencement_date', 'country_of_origin']
    search_fields = [
        'contract_number', 'contract_title', 'tender__tender_id', 'contractor_supplier',
        'e_purchase_order_no', 'sap_purchase_order_no'
    ]
    autocomplete_fields = ['tender', 'contract_creator']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'commencement_date'
    
    fieldsets = (
        ('Tender Link', {
            'fields': ('tender',)
        }),
        ('Contract Information', {
            'fields': ('contract_number', 'contract_title', 'contract_creator')
        }),
        ('Status', {
            'fields': ('contract_step', 'contract_status', 'responsibility')
        }),
        ('Supplier Information', {
            'fields': ('contractor_supplier', 'country_of_origin')
        }),
        ('Purchase Orders', {
            'fields': ('e_purchase_order_no', 'sap_purchase_order_no')
        }),
        ('Contract Dates & Duration', {
            'fields': ('commencement_date', 'contract_expiry_date',
                      'contract_duration_measure', 'contract_duration', 'contract_delivery_period')
        }),
        ('Financial', {
            'fields': ('contract_value', 'contract_currency')
        }),
        ('Security Details', {
            'fields': ('tender_security_amount', 'tender_security_validity_days', 'tender_security_expiry_date',
                      'performance_security_amount', 'performance_security_duration_days',
                      'performance_security_expiry_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Committee Admin
@admin.register(TenderOpeningCommittee)
class TenderOpeningCommitteeAdmin(admin.ModelAdmin):
    list_display = ['tender', 'employee', 'role', 'added_at']
    list_filter = ['role', 'added_at']
    search_fields = ['tender__tender_id', 'employee__first_name', 'employee__last_name']
    autocomplete_fields = ['tender', 'employee']


@admin.register(TenderEvaluationCommittee)
class TenderEvaluationCommitteeAdmin(admin.ModelAdmin):
    list_display = ['tender', 'employee', 'role', 'added_at']
    list_filter = ['role', 'added_at']
    search_fields = ['tender__tender_id', 'employee__first_name', 'employee__last_name']
    autocomplete_fields = ['tender', 'employee']


@admin.register(ContractCITCommittee)
class ContractCITCommitteeAdmin(admin.ModelAdmin):
    list_display = ['contract', 'employee', 'role', 'added_at']
    list_filter = ['role', 'added_at']
    search_fields = ['contract__tender__tender_id', 'employee__first_name', 'employee__last_name']
    autocomplete_fields = ['contract', 'employee']
