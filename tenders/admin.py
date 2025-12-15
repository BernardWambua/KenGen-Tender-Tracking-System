from django.contrib import admin
from .models import (
    Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee, Tender,
    TenderOpeningCommittee, TenderEvaluationCommittee, UserProfile
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


# Inline admins for committees
class TenderOpeningCommitteeInline(admin.TabularInline):
    model = TenderOpeningCommittee
    extra = 1
    autocomplete_fields = ['employee']


class TenderEvaluationCommitteeInline(admin.TabularInline):
    model = TenderEvaluationCommittee
    extra = 1
    autocomplete_fields = ['employee']


# Tender Admin
@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = [
        'tender_id', 'tender_description_short', 'procurement_type', 
        'region', 'department', 'tender_advert_date', 'tender_closing_date',
        'loa_status', 'contract_status', 'estimated_value'
    ]
    list_filter = [
        'procurement_type', 'region', 'department', 'loa_status', 
        'contract_status', 'tender_advert_date'
    ]
    search_fields = [
        'tender_id', 'tender_description', 'egp_tender_reference', 
        'kengen_tender_reference', 'requisition_number'
    ]
    autocomplete_fields = ['tender_creator', 'contract_creator', 'user']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'tender_advert_date'
    
    fieldsets = (
        ('Identification', {
            'fields': ('tender_id', 'egp_tender_reference', 'kengen_tender_reference', 
                      'requisition_number', 'shopping_cart')
        }),
        ('Description & Classification', {
            'fields': ('tender_description', 'procurement_type')
        }),
        ('Location & Assignment', {
            'fields': ('region', 'department', 'section', 'user')
        }),
        ('Creators', {
            'fields': ('tender_creator', 'contract_creator')
        }),
        ('Important Dates', {
            'fields': ('tender_advert_date', 'tender_closing_date', 'tender_closing_time',
                      'tender_validity_expiry_date', 'tender_evaluation_duration')
        }),
        ('Status', {
            'fields': ('loa_status', 'contract_status')
        }),
        ('Purchase Orders', {
            'fields': ('e_purchase_order_no', 'sap_purchase_order_no')
        }),
        ('Financial', {
            'fields': ('estimated_value',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TenderOpeningCommitteeInline, TenderEvaluationCommitteeInline]
    
    def tender_description_short(self, obj):
        return obj.tender_description[:50] + '...' if len(obj.tender_description) > 50 else obj.tender_description
    tender_description_short.short_description = 'Description'


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
