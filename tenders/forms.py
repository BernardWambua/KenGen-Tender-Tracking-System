"""
Forms for tenders app
"""
from django import forms
from django.contrib.auth.models import User
from .models import (
    Tender, Contract, TenderOpeningCommittee, TenderEvaluationCommittee,
    ContractCITCommittee, Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee
)


class TenderForm(forms.ModelForm):
    """Form for creating and editing tenders"""
    
    class Meta:
        model = Tender
        fields = [
            'tender_id', 'quarter', 'egp_tender_reference', 'kengen_tender_reference',
            'requisition_number', 'shopping_cart', 'tender_description',
            'procurement_type', 'reservation', 'tender_status', 'region', 'department', 'section', 'user',
            'tender_creator', 'tender_advert_date',
            'tender_closing_date', 'tender_closing_time', 'tender_validity_expiry_date',
            'tender_evaluation_duration', 'estimated_value'
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
            'requisition_number': 'Requisition Number',
            'shopping_cart': 'Shopping Cart',
            'tender_description': 'Tender Description',
            'procurement_type': 'Procurement Type',
            'reservation': 'Reservation (AGPO)',
            'tender_status': 'Tender Status',
            'region': 'Region',
            'department': 'Department',
            'section': 'Section',
            'user': 'Assigned User',
            'tender_creator': 'Tender Creator',
            'tender_advert_date': 'Tender Advert Date',
            'tender_closing_date': 'Tender Closing Date',
            'tender_closing_time': 'Tender Closing Time',
            'tender_validity_expiry_date': 'Tender Validity Expiry Date',
            'tender_evaluation_duration': 'Tender Evaluation Duration',
            'estimated_value': 'Estimated Value (KSh)',
        }


class ContractForm(forms.ModelForm):
    """Form for creating and editing contracts"""
    
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


class ContractCITCommitteeForm(forms.ModelForm):
    """Form for adding CIT/Inspection & Acceptance committee members"""
    
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
