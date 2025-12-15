"""
Forms for tenders app
"""
from django import forms
from django.contrib.auth.models import User
from .models import (
    Tender, TenderOpeningCommittee, TenderEvaluationCommittee,
    Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee
)


class TenderForm(forms.ModelForm):
    """Form for creating and editing tenders"""
    
    class Meta:
        model = Tender
        fields = [
            'tender_id', 'egp_tender_reference', 'kengen_tender_reference',
            'requisition_number', 'shopping_cart', 'tender_description',
            'procurement_type', 'region', 'department', 'section', 'user',
            'tender_creator', 'contract_creator', 'tender_advert_date',
            'tender_closing_date', 'tender_closing_time', 'tender_validity_expiry_date',
            'tender_evaluation_duration', 'loa_status', 'contract_status',
            'e_purchase_order_no', 'sap_purchase_order_no', 'estimated_value'
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
            'requisition_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., EPS/382/REQ/2025-26/1'
            }),
            'shopping_cart': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shopping Cart Number'
            }),
            'tender_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter detailed tender description...'
            }),
            'procurement_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'region': forms.Select(attrs={
                'class': 'form-select'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'section': forms.Select(attrs={
                'class': 'form-select'
            }),
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tender_creator': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_creator': forms.Select(attrs={
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
            'tender_validity_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tender_evaluation_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 30 Days, 21 Days'
            }),
            'loa_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contract_status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'e_purchase_order_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e-Purchase Order Number'
            }),
            'sap_purchase_order_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SAP Purchase Order Number'
            }),
            'estimated_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated value in KSh',
                'step': '0.01'
            }),
        }
        labels = {
            'tender_id': 'Tender ID',
            'egp_tender_reference': 'eGP Tender Reference',
            'kengen_tender_reference': 'KenGen Tender Reference',
            'requisition_number': 'Requisition Number',
            'shopping_cart': 'Shopping Cart',
            'tender_description': 'Tender Description',
            'procurement_type': 'Procurement Type',
            'region': 'Region',
            'department': 'Department',
            'section': 'Section',
            'user': 'Assigned User',
            'tender_creator': 'Tender Creator',
            'contract_creator': 'Contract Creator',
            'tender_advert_date': 'Tender Advert Date',
            'tender_closing_date': 'Tender Closing Date',
            'tender_closing_time': 'Tender Closing Time',
            'tender_validity_expiry_date': 'Tender Validity Expiry Date',
            'tender_evaluation_duration': 'Tender Evaluation Duration',
            'loa_status': 'LOA Status',
            'contract_status': 'Contract Status',
            'e_purchase_order_no': 'e-Purchase Order Number',
            'sap_purchase_order_no': 'SAP Purchase Order Number',
            'estimated_value': 'Estimated Value (KSh)',
        }


class TenderOpeningCommitteeForm(forms.ModelForm):
    """Form for adding opening committee members"""
    
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
