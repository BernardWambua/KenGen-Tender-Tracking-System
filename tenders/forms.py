"""
Forms for tenders app
"""
from django import forms
from django.contrib.auth.models import User
from .models import (
    Tender, Contract, TenderOpeningCommittee, TenderEvaluationCommittee,
    ContractCITCommittee, Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee, Requisition, Currency, Country
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


class RequisitionSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        self.procurement_type_by_requisition = kwargs.pop('procurement_type_by_requisition', {})
        super().__init__(*args, **kwargs)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value in self.procurement_type_by_requisition:
            option.setdefault('attrs', {})['data-procurement-type'] = str(
                self.procurement_type_by_requisition[value] or ''
            )
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
        for field_name in ['requisition', 'tender_creator', 'tender_creation_date', 'tender_reference_number']:
            if field_name in self.fields:
                self.fields[field_name].required = True
        if 'requisition' in self.fields:
            self.fields['requisition'].queryset = Requisition.objects.order_by('-created_at')
            requisition_map = dict(Requisition.objects.values_list('id', 'procurement_type'))
            if isinstance(self.fields['requisition'].widget, RequisitionSelect):
                self.fields['requisition'].widget.procurement_type_by_requisition = requisition_map

        if not self.is_bound and 'tender_evaluation_duration_days' in self.fields:
            requisition_id = self.initial.get('requisition') or getattr(self.instance, 'requisition_id', None)
            if requisition_id:
                procurement_type = Requisition.objects.filter(id=requisition_id).values_list('procurement_type', flat=True).first()
                self.fields['tender_evaluation_duration_days'].initial = 21 if procurement_type == 'QUOTATION' else 30

    def clean(self):
        cleaned_data = super().clean()
        eligibility = cleaned_data.get('eligibility')
        agpo_category = cleaned_data.get('agpo_category')
        if eligibility == 'AGPO' and not agpo_category:
            self.add_error('agpo_category', 'Please select an AGPO category.')
        if not cleaned_data.get('tender_evaluation_duration_days'):
            requisition = cleaned_data.get('requisition')
            if requisition:
                cleaned_data['tender_evaluation_duration_days'] = 21 if requisition.procurement_type == 'QUOTATION' else 30
        return cleaned_data
    
    class Meta:
        model = Tender
        fields = [
            'tender_id', 'tender_reference_number', 'tender_creation_date',
            'requisition', 'tender_description',
            'eligibility', 'agpo_category', 'procurement_method',
            'tender_approval_status', 'tender_step',
            'tender_creator', 'proposed_advert_date', 'tender_advert_date',
            'tender_closing_date', 'tender_closing_time', 'tender_opening_date', 'tender_opening_time',
            'tender_validity_days', 'tender_validity_expiry_date',
            'tender_evaluation_duration_days', 'tender_evaluation_end_date', 'estimated_value'
        ]
        widgets = {
            'tender_id': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 38',
                'min': 0
            }),
            'tender_reference_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., KENGEN/197/0001/2025-26'
            }),
            'tender_creation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'requisition': RequisitionSelect(attrs={
                'class': 'form-select'
            }),
            'tender_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter detailed tender description...'
            }),
            'eligibility': forms.Select(attrs={
                'class': 'form-select'
            }),
            'agpo_category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'procurement_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_approval_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_step': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_creator': forms.Select(attrs={
                'class': 'form-select'
            }),
            'proposed_advert_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
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
            'tender_validity_days': forms.NumberInput(attrs={
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
            'tender_reference_number': 'Tender Reference Number',
            'tender_creation_date': 'Tender Creation Date',
            'requisition': 'Requisition',
            'tender_description': 'Tender Description',
            'eligibility': 'Eligibility',
            'agpo_category': 'AGPO Category',
            'procurement_method': 'Procurement Method',
            'tender_approval_status': 'Tender Approval Status',
            'tender_step': 'Tender Step',
            'tender_creator': 'Tender Creator',
            'proposed_advert_date': 'Proposed Advert Date',
            'tender_advert_date': 'Tender Advert Date',
            'tender_closing_date': 'Tender Closing Date',
            'tender_closing_time': 'Tender Closing Time',
            'tender_opening_date': 'Tender Opening Date',
            'tender_opening_time': 'Tender Opening Time',
            'tender_validity_days': 'Tender Validity (Days)',
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
            self.fields['contract_creator'].queryset = employee_queryset.filter(
                section__name__icontains='contract',
                section__division__name__iexact='compliance & reporting'
            )
        if 'contract_currency' in self.fields:
            self.fields['contract_currency'].queryset = Currency.objects.order_by('code')
        if 'country_of_origin' in self.fields:
            self.fields['country_of_origin'].queryset = Country.objects.order_by('name')
    
    class Meta:
        model = Contract
        fields = [
            'tender', 'contract_number', 'contract_title', 'contract_creator',
            'contract_duration_measure', 'contract_duration', 'commencement_date', 'contract_expiry_date',
            'contract_value', 'contract_currency',
            'contractor_supplier', 'country_of_origin',
            'tender_security_amount', 'tender_security_validity_days', 'tender_security_expiry_date',
            'contract_step', 'contract_status', 'responsibility',
            'contract_delivery_period',
            'performance_security_amount', 'performance_security_duration_days', 'performance_security_expiry_date',
            'e_purchase_order_no', 'sap_purchase_order_no'
        ]
        widgets = {
            'tender': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract number',
                'min': 0
            }),
            'contract_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract title'
            }),
            'contract_creator': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_duration_measure': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract duration',
                'min': 0
            }),
            'commencement_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'contract_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
            'contract_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract value',
                'step': '0.01'
            }),
            'contract_currency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contractor_supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contractor/Supplier'
            }),
            'country_of_origin': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_security_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tender security amount',
                'step': '0.01'
            }),
            'tender_security_validity_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tender security validity (days)',
                'min': 0
            }),
            'tender_security_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
            'contract_step': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'responsibility': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_delivery_period': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contract delivery period (days)',
                'min': 0
            }),
            'performance_security_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Performance security amount',
                'step': '0.01'
            }),
            'performance_security_duration_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Performance security duration (days)',
                'min': 0
            }),
            'performance_security_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
            'e_purchase_order_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'eGP Purchase Order No'
            }),
            'sap_purchase_order_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SAP Purchase Order No'
            }),
        }
        labels = {
            'tender': 'Linked Tender',
            'contract_number': 'Contract Number',
            'contract_title': 'Contract Title',
            'contract_creator': 'Contract Creator',
            'contract_duration_measure': 'Contract Duration Measure',
            'contract_duration': 'Contract Duration',
            'commencement_date': 'Commencement Date',
            'contract_expiry_date': 'Contract Expiry Date',
            'contract_value': 'Contract Value',
            'contract_currency': 'Contract Currency',
            'contractor_supplier': 'Contractor/Supplier',
            'country_of_origin': 'Country of Origin',
            'tender_security_amount': 'Tender Security Amount',
            'tender_security_validity_days': 'Tender Security Validity (Days)',
            'tender_security_expiry_date': 'Tender Security Validity Expiry Date',
            'contract_step': 'Contract Step',
            'contract_status': 'Contract Status',
            'responsibility': 'Responsibility',
            'contract_delivery_period': 'Contract Delivery Period (Days)',
            'performance_security_amount': 'Performance Security Amount',
            'performance_security_duration_days': 'Performance Security Duration (Days)',
            'performance_security_expiry_date': 'Performance Security Expiry Date',
            'e_purchase_order_no': 'eGP Purchase Order No',
            'sap_purchase_order_no': 'SAP Purchase Order No',
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
            'role': forms.Select(attrs={
                'class': 'form-select'
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
            'role': forms.Select(attrs={
                'class': 'form-select'
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
            'role': forms.Select(attrs={
                'class': 'form-select'
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
        if 'tender_creator' in self.fields:
            self.fields['tender_creator'].queryset = employee_queryset.filter(
                section__name__iexact='tenders',
                section__division__name__iexact='procurement'
            )

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

        for field_name in [
            'e_requisition_no', 'requisition_description', 'shopping_cart_no',
            'shopping_cart_amount', 'shopping_cart_status', 'region', 'department',
            'division', 'section', 'assigned_user', 'procurement_type',
            'tender_creator', 'date_assigned'
        ]:
            if field_name in self.fields:
                self.fields[field_name].required = True

    class Meta:
        model = Requisition
        fields = [
            'e_requisition_no', 'requisition_description',
            'shopping_cart_no', 'shopping_cart_amount', 'shopping_cart_status',
            'region', 'department', 'division', 'section', 'assigned_user',
            'procurement_type', 'tender_creator', 'date_assigned', 'creation_deadline'
        ]
        widgets = {
            'e_requisition_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., EPS/382/REQ/2025-26/1'
            }),
            'requisition_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter requisition description...'
            }),
            'shopping_cart_no': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shopping Cart Number',
                'min': 0
            }),
            'shopping_cart_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shopping Cart Amount',
                'min': 0,
                'step': '0.01'
            }),
            'shopping_cart_status': forms.Select(attrs={
                'class': 'form-select'
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
            'procurement_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_creator': EmployeeSelect(attrs={
                'class': 'form-select'
            }),
            'date_assigned': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'creation_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'readonly': True
            }),
        }
        labels = {
            'e_requisition_no': 'e-Requisition No',
            'requisition_description': 'Requisition Description',
            'shopping_cart_no': 'Shopping Cart No',
            'shopping_cart_amount': 'Shopping Cart Amount',
            'shopping_cart_status': 'Shopping Cart Status',
            'region': 'Region',
            'department': 'Department',
            'division': 'Division',
            'section': 'Section',
            'assigned_user': 'Requisition Owner',
            'procurement_type': 'Procurement Type',
            'tender_creator': 'Tender Creator',
            'date_assigned': 'Date Assigned',
            'creation_deadline': 'Creation Deadline',
        }


class EmployeeForm(forms.ModelForm):
    """Form for creating and editing employees (bulk uploaded or individual entry)"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'division' in self.fields:
            division_map = dict(Division.objects.values_list('id', 'department_id'))
            if isinstance(self.fields['division'].widget, DivisionSelect):
                self.fields['division'].widget.department_by_division = division_map
        if 'section' in self.fields:
            section_map = dict(Section.objects.values_list('id', 'division_id'))
            if isinstance(self.fields['section'].widget, SectionSelect):
                self.fields['section'].widget.division_by_section = section_map
    
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
            'division': DivisionSelect(attrs={
                'class': 'form-select'
            }),
            'section': SectionSelect(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'employee_id': 'Staff number - will be used to link with user account if they sign up'
        }
