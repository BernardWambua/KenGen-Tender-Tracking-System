from django import forms
from .models import Region, Department, Division, Section, ProcurementType, LOAStatus, ContractStatus


class BulkUploadForm(forms.Form):
    """Base form for bulk uploading data via CSV/Excel"""
    file = forms.FileField(
        label='Upload File',
        help_text='Upload a CSV or Excel file with the required columns',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            file_ext = file.name.split('.')[-1].lower()
            if file_ext not in ['csv', 'xlsx', 'xls']:
                raise forms.ValidationError('Invalid file format. Please upload CSV or Excel file.')
            
            # Check file size (limit to 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size exceeds 5MB limit.')
        return file


class RegionUploadForm(BulkUploadForm):
    """Form for uploading regions in bulk. Expected columns: name, code"""
    pass


class DepartmentUploadForm(BulkUploadForm):
    """Form for uploading departments in bulk. Expected columns: name, code"""
    pass


class DivisionUploadForm(BulkUploadForm):
    """Form for uploading divisions in bulk. Expected columns: name, code, department_code"""
    pass


class SectionUploadForm(BulkUploadForm):
    """Form for uploading sections in bulk. Expected columns: name, code, division_code"""
    pass


class ProcurementTypeUploadForm(BulkUploadForm):
    """Form for uploading procurement types in bulk. Expected columns: name, code"""
    pass


class LOAStatusUploadForm(BulkUploadForm):
    """Form for uploading e-Contract Stepes in bulk. Expected columns: name"""
    pass


class ContractStatusUploadForm(BulkUploadForm):
    """Form for uploading e-Contract Statuses in bulk. Expected columns: name"""
    pass
