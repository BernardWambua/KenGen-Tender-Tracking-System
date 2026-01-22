"""
Forms for tenders app
"""
from django import forms
from django.contrib.auth.models import User
from .models import (
    Tender, Contract, TenderOpeningCommittee, TenderEvaluationCommittee,
    ContractCITCommittee, Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee, Requisition
)


def get_employee_ordered_queryset():
    return Employee.objects.order_by('last_name', 'first_name', 'employee_id')


class DivisionSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.department_by_division = kwargs.pop('department_by_division', {})
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value in self.department_by_division:
            option.setdefault('attrs', {})['data-department-id'] = str(self.department_by_division[value])
        return option


class SectionSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.division_by_section = kwargs.pop('division_by_section', {})
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value in self.division_by_section:
            option.setdefault('attrs', {})['data-division-id'] = str(self.division_by_section[value])
        return option


class EmployeeSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.employee_org_map = kwargs.pop('employee_org_map', {})
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value in self.employee_org_map:
            department_id, division_id, section_id = self.employee_org_map[value]
            option.setdefault('attrs', {})['data-department-id'] = str(department_id or '')
            option.setdefault('attrs', {})['data-division-id'] = str(division_id or '')
            option.setdefault('attrs', {})['data-section-id'] = str(section_id or '')
        return option


class TenderForm(forms.ModelForm):
    """Form for creating and editing tenders"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee_queryset = get_employee_ordered_queryset()
        if 'tender_creator' in self.fields:
            self.fields['tender_creator'].queryset = employee_queryset
        if 'tender_creator' in self.fields:
            self.fields['tender_creator'].queryset = employee_queryset.filter(
                section__name__iexact='tenders',
                section__division__name__iexact='procurement'
            )
        for field_name in ['requisition', 'tender_creator']:
            if field_name in self.fields:
                self.fields[field_name].required = True
        if 'requisition' in self.fields:
            self.fields['requisition'].queryset = Requisition.objects.order_by('-created_at')
    
    class Meta:
        model = Tender
        fields = [
            'tender_id', 'quarter', 'egp_tender_reference', 'kengen_tender_reference',
            'requisition', 'tender_description',
            'procurement_type', 'reservation', 'tender_status',
            'tender_creator', 'tender_advert_date',
            'tender_closing_date', 'tender_closing_time', 'tender_opening_date', 'tender_opening_time',
            'tender_validity_duration_days', 'tender_validity_expiry_date',
            'tender_evaluation_duration_days', 'tender_evaluation_end_date', 'estimated_value'
        ]
        widgets = {
            'tender_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Tender ID : 38'
            }),
            'egp_tender_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., KENGEN/197/0001/2025-26'
            }),
            'kengen_tender_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., KGN-SONDU-017-2025'
            }),
            'requisition': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter detailed tender description...'
            }),
            'quarter': forms.Select(attrs={
                'class': 'form-select'
            }),
            'procurement_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reservation': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_creator': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_advert_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tender_closing_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tender_closing_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'tender_opening_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
            'tender_opening_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'readonly': True
            }),
            'tender_validity_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
            'tender_validity_duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30',
                'min': 0
            }),
            'tender_evaluation_duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 14',
                'min': 0
            }),
            'tender_evaluation_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
            'estimated_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated value in KSh',
                'step': '0.01'
            }),
        }
        labels = {
            'tender_id': 'Tender ID',
            'quarter': 'Quarter',
            'egp_tender_reference': 'eGP Tender Reference',
            'kengen_tender_reference': 'KenGen Tender Reference',
            'requisition': 'Requisition',
            'tender_description': 'Tender Description',
            'procurement_type': 'Procurement Type',
            'reservation': 'Reservation (AGPO)',
            'tender_status': 'Tender Status',
            'tender_creator': 'Tender Creator',
            'tender_advert_date': 'Tender Advert Date',
            'tender_closing_date': 'Tender Closing Date',
            'tender_closing_time': 'Tender Closing Time',
            'tender_opening_date': 'Tender Opening Date',
            'tender_opening_time': 'Tender Opening Time',
            'tender_validity_duration_days': 'Tender Validity Duration (Days)',
            'tender_validity_expiry_date': 'Tender Validity Expiry Date',
            'tender_evaluation_duration_days': 'Tender Evaluation Duration (Days)',
            'tender_evaluation_end_date': 'Tender Evaluation End Date',
            'estimated_value': 'Estimated Value (KSh)',
        }


class ContractForm(forms.ModelForm):
    """Form for creating and editing contracts"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee_queryset = get_employee_ordered_queryset()
        if 'contract_creator' in self.fields:
            self.fields['contract_creator'].queryset = employee_queryset
    
    class Meta:
        model = Contract
        fields = [
            'tender', 'contract_reference', 'contract_creator',
            'loa_status', 'contract_status', 'supplier_name', 'supplier_county',
            'e_purchase_order_no', 'sap_purchase_order_no', 
            'contract_signature_date', 'contract_expiry_date',
            'contract_duration', 'contract_delivery_period', 'contract_value',
            'tender_security_value', 'tender_security_expiry_date',
            'performance_security_amount', 'performance_security_duration',
            'performance_security_expiry_date'
        ]
        widgets = {
            'tender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract reference number'
            }),
            'contract_creator': forms.Select(attrs={
                'class': 'form-select'
            }),
            'loa_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of Supplier Awarded'
            }),
            'supplier_county': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'County of Origin'
            }),
            'e_purchase_order_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e-Purchase Order Number'
            }),
            'sap_purchase_order_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SAP Purchase Order Number'
            }),
            'contract_signature_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contract_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contract_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 12 months, 2 years'
            }),
            'contract_delivery_period': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract delivery period'
            }),
            'contract_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract value in KSh',
                'step': '0.01'
            }),
            'tender_security_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tender security value in KSh',
                'step': '0.01'
            }),
            'tender_security_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'performance_security_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Performance security amount in KSh',
                'step': '0.01'
            }),
            'performance_security_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 12 months'
            }),
            'performance_security_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'tender': 'Linked Tender',
            'contract_reference': 'Contract Reference',
            'contract_creator': 'Contract Creator',
            'loa_status': 'e-Contract Step',
            'contract_status': 'e-Contract Status',
            'supplier_name': 'Name of Supplier Awarded',
            'supplier_county': 'County of Origin',
            'e_purchase_order_no': 'e-Purchase Order Number',
            'sap_purchase_order_no': 'SAP Purchase Order Number',
            'contract_signature_date': 'Contract Signature Date',
            'contract_expiry_date': 'Contract Expiry Date',
            'contract_duration': 'Contract Duration',
            'contract_delivery_period': 'Contract Delivery Period',
            'contract_value': 'Contract Value (KSh)',
            'tender_security_value': 'Tender Security Value (KSh)',
            'tender_security_expiry_date': 'Tender Security Expiry Date',
            'performance_security_amount': 'Performance Security Amount (KSh)',
            'performance_security_duration': 'Performance Security Duration',
            'performance_security_expiry_date': 'Performance Security Expiry Date',
        }


class TenderOpeningCommitteeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'employee' in self.fields:
            self.fields['employee'].queryset = get_employee_ordered_queryset()
    
    class Meta:
        model = TenderOpeningCommittee
        fields = ['employee', 'role']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select'
            }),
            'role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chairperson, Member, Secretary'
            }),
        }


class TenderEvaluationCommitteeForm(forms.ModelForm):
    """Form for adding evaluation committee members"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'employee' in self.fields:
            self.fields['employee'].queryset = get_employee_ordered_queryset()
    
    class Meta:
        model = TenderEvaluationCommittee
        fields = ['employee', 'role']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select'
            }),
            'role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chairperson, Technical Evaluator, Financial Evaluator'
            }),
        }


class ContractCITCommitteeForm(forms.ModelForm):
    """Form for adding CIT/Inspection & Acceptance committee members"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'employee' in self.fields:
            self.fields['employee'].queryset = get_employee_ordered_queryset()
    
    class Meta:
        model = ContractCITCommittee
        fields = ['employee', 'role']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select'
            }),
            'role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chairperson, Inspector, Acceptance Officer'
            }),
        }


# Formsets for committees
from django.forms import inlineformset_factory

TenderOpeningCommitteeFormSet = inlineformset_factory(
    Tender,
    TenderOpeningCommittee,
    form=TenderOpeningCommitteeForm,
    extra=3,
    can_delete=True,
    min_num=0,
    validate_min=False,
)

TenderEvaluationCommitteeFormSet = inlineformset_factory(
    Tender,
    TenderEvaluationCommittee,
    form=TenderEvaluationCommitteeForm,
    extra=3,
    can_delete=True,
    min_num=0,
    validate_min=False,
)

ContractCITCommitteeFormSet = inlineformset_factory(
    Contract,
    ContractCITCommittee,
    form=ContractCITCommitteeForm,
    extra=3,
    can_delete=True,
    min_num=0,
    validate_min=False,
)


class RequisitionForm(forms.ModelForm):
    """Form for creating and editing requisitions"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee_queryset = get_employee_ordered_queryset()
        if 'assigned_user' in self.fields:
            self.fields['assigned_user'].queryset = employee_queryset

        department_id = self.data.get('department') if self.data else None
        division_id = self.data.get('division') if self.data else None
        section_id = self.data.get('section') if self.data else None

        if not (department_id or division_id or section_id) and self.instance.pk:
            department_id = getattr(self.instance, 'department_id', None)
            division_id = getattr(self.instance, 'division_id', None)
            section_id = getattr(self.instance, 'section_id', None)

        if 'assigned_user' in self.fields:
            if section_id:
                self.fields['assigned_user'].queryset = employee_queryset.filter(section_id=section_id)
            elif division_id:
                self.fields['assigned_user'].queryset = employee_queryset.filter(division_id=division_id)
            elif department_id:
                self.fields['assigned_user'].queryset = employee_queryset.filter(department_id=department_id)

        if 'division' in self.fields:
            division_map = dict(Division.objects.values_list('id', 'department_id'))
            if isinstance(self.fields['division'].widget, DivisionSelect):
                self.fields['division'].widget.department_by_division = division_map
        if 'section' in self.fields:
            section_map = dict(Section.objects.values_list('id', 'division_id'))
            if isinstance(self.fields['section'].widget, SectionSelect):
                self.fields['section'].widget.division_by_section = section_map
        if 'assigned_user' in self.fields and isinstance(self.fields['assigned_user'].widget, EmployeeSelect):
            employee_map = {
                emp_id: (dept_id, div_id, sec_id)
                for emp_id, dept_id, div_id, sec_id in Employee.objects.values_list(
                    'id', 'department_id', 'division_id', 'section_id'
                )
            }
            self.fields['assigned_user'].widget.employee_org_map = employee_map

        for field_name in ['region', 'department', 'division', 'section', 'assigned_user']:
            if field_name in self.fields:
                self.fields[field_name].required = True

    class Meta:
        model = Requisition
        fields = [
            'requisition_number', 'shopping_cart',
            'region', 'department', 'division', 'section', 'assigned_user'
        ]
        widgets = {
            'requisition_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., EPS/382/REQ/2025-26/1'
            }),
            'shopping_cart': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shopping Cart Number'
            }),
            'region': forms.Select(attrs={
                'class': 'form-select'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'division': DivisionSelect(attrs={
                'class': 'form-select'
            }),
            'section': SectionSelect(attrs={
                'class': 'form-select'
            }),
            'assigned_user': EmployeeSelect(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'requisition_number': 'Requisition Number',
            'shopping_cart': 'Shopping Cart',
            'region': 'Region',
            'department': 'Department',
            'division': 'Division',
            'section': 'Section',
            'assigned_user': 'Requisition Owner',
        }


class EmployeeForm(forms.ModelForm):
    """Form for creating and editing employees (bulk uploaded or individual entry)"""
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'job_title', 'email', 'phone',
            'department', 'division', 'section', 'is_active'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 71188'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Procurement Officer'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@kengen.co.ke'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254 700 000 000'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'division': forms.Select(attrs={
                'class': 'form-select'
            }),
            'section': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'employee_id': 'Staff number - will be used to link with user account if they sign up'
        }
