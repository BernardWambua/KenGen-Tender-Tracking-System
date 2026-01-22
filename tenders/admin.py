from django.contrib import admin
from .models import (
    Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee, Tender, Contract, Requisition,
    TenderOpeningCommittee, TenderEvaluationCommittee, ContractCITCommittee, UserProfile
)

# Register your models here.

# User Profile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'employee__employee_id', 'employee__first_name', 'employee__last_name']
    raw_id_fields = ['user', 'employee']


# Lookup models - simple admin
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'created_at']
    list_filter = ['department']
    search_fields = ['name', 'department__name']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'division', 'created_at']
    list_filter = ['division__department', 'division']
    search_fields = ['name', 'division__name']


@admin.register(ProcurementType)
class ProcurementTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(LOAStatus)
class LOAStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


@admin.register(ContractStatus)
class ContractStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']


# Employee Admin
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
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
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ['requisition_number', 'shopping_cart', 'region', 'department', 'division', 'section', 'assigned_user', 'created_at']
    list_filter = ['region', 'department', 'division', 'section']
    search_fields = ['requisition_number', 'shopping_cart', 'assigned_user__first_name', 'assigned_user__last_name']
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
            'fields': ('contract_reference', 'contract_creator')
        }),
        ('Status', {
            'fields': ('loa_status', 'contract_status')
        }),
        ('Supplier Information', {
            'fields': ('supplier_name', 'supplier_county')
        }),
        ('Purchase Orders', {
            'fields': ('e_purchase_order_no', 'sap_purchase_order_no')
        }),
        ('Contract Dates', {
            'fields': ('contract_signature_date', 'contract_expiry_date', 'contract_duration', 'contract_delivery_period')
        }),
        ('Financial', {
            'fields': ('contract_value',)
        }),
        ('Security', {
            'fields': ('tender_security_value', 'tender_security_expiry_date', 
                      'performance_security_amount', 'performance_security_duration', 
                      'performance_security_expiry_date')
        }),
    )


# Tender Admin
@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = [
        'tender_id', 'tender_description_short', 'quarter', 'procurement_type', 
        'requisition', 'tender_status', 'tender_advert_date', 'tender_closing_date',
        'estimated_value'
    ]
    list_filter = [
        'quarter', 'tender_status', 'reservation', 'procurement_type', 
        'requisition__region', 'requisition__department', 'requisition__division', 'requisition__section', 'tender_advert_date'
    ]
    search_fields = [
        'tender_id', 'tender_description', 'egp_tender_reference', 
        'kengen_tender_reference', 'requisition__requisition_number'
    ]
    autocomplete_fields = ['tender_creator', 'requisition']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'tender_advert_date'
    
    fieldsets = (
        ('Identification', {
            'fields': ('tender_id', 'quarter', 'egp_tender_reference', 'kengen_tender_reference',
                      'requisition')
        }),
        ('Description & Classification', {
            'fields': ('tender_description', 'procurement_type', 'reservation', 'tender_status')
        }),
        ('Location', {
            'fields': ('region',)
        }),
        ('Creator', {
            'fields': ('tender_creator',)
        }),
        ('Important Dates', {
            'fields': ('tender_advert_date', 'tender_closing_date', 'tender_closing_time',
                      'tender_opening_date', 'tender_opening_time', 'tender_validity_duration_days',
                      'tender_validity_expiry_date', 'tender_evaluation_duration_days',
                      'tender_evaluation_end_date')
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
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        'tender', 'contract_reference', 'supplier_name', 'loa_status', 'contract_status',
        'contract_value', 'contract_signature_date'
    ]
    list_filter = ['loa_status', 'contract_status', 'contract_signature_date', 'supplier_county']
    search_fields = [
        'contract_reference', 'tender__tender_id', 'supplier_name', 'supplier_county',
        'e_purchase_order_no', 'sap_purchase_order_no'
    ]
    autocomplete_fields = ['tender', 'contract_creator']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'contract_signature_date'
    
    fieldsets = (
        ('Tender Link', {
            'fields': ('tender',)
        }),
        ('Contract Information', {
            'fields': ('contract_reference', 'contract_creator')
        }),
        ('Status', {
            'fields': ('loa_status', 'contract_status')
        }),
        ('Supplier Information', {
            'fields': ('supplier_name', 'supplier_county')
        }),
        ('Purchase Orders', {
            'fields': ('e_purchase_order_no', 'sap_purchase_order_no')
        }),
        ('Contract Dates & Duration', {
            'fields': ('contract_signature_date', 'contract_expiry_date', 
                      'contract_duration', 'contract_delivery_period')
        }),
        ('Financial', {
            'fields': ('contract_value',)
        }),
        ('Security Details', {
            'fields': ('tender_security_value', 'tender_security_expiry_date',
                      'performance_security_amount', 'performance_security_duration',
                      'performance_security_expiry_date')
        }),
        ('Committees', {
            'fields': ('cit_committee',)
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
