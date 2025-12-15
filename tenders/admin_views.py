import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from openpyxl import load_workbook

from .models import (
    Region, Department, Division, Section, 
    ProcurementType, LOAStatus, ContractStatus
)
from .bulk_upload_forms import (
    RegionUploadForm, DepartmentUploadForm, DivisionUploadForm,
    SectionUploadForm, ProcurementTypeUploadForm, LOAStatusUploadForm,
    ContractStatusUploadForm
)


# Role-based access control decorators
def is_admin_or_superuser(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or user.groups.filter(name='Tender Admin').exists()


def is_manager_or_above(user):
    """Check if user is manager, admin, or superuser"""
    return user.is_superuser or user.groups.filter(name__in=['Tender Admin', 'Tender Manager']).exists()


def is_staff_or_above(user):
    """Check if user has any tender management role"""
    return user.is_superuser or user.groups.filter(name__in=['Tender Admin', 'Tender Manager', 'Tender Staff']).exists()


@login_required
@user_passes_test(is_admin_or_superuser)
def custom_admin_dashboard(request):
    """Custom admin dashboard with bulk upload options"""
    context = {
        'title': 'Custom Admin Panel',
        'lookup_models': [
            {'name': 'Region', 'url': 'tenders:bulk_upload_region', 'count': Region.objects.count()},
            {'name': 'Department', 'url': 'tenders:bulk_upload_department', 'count': Department.objects.count()},
            {'name': 'Division', 'url': 'tenders:bulk_upload_division', 'count': Division.objects.count()},
            {'name': 'Section', 'url': 'tenders:bulk_upload_section', 'count': Section.objects.count()},
            {'name': 'Procurement Type', 'url': 'tenders:bulk_upload_procurement_type', 'count': ProcurementType.objects.count()},
            {'name': 'LOA Status', 'url': 'tenders:bulk_upload_loa_status', 'count': LOAStatus.objects.count()},
            {'name': 'Contract Status', 'url': 'tenders:bulk_upload_contract_status', 'count': ContractStatus.objects.count()},
        ]
    }
    return render(request, 'tenders/admin/dashboard.html', context)


def process_csv_file(file, columns):
    """Process CSV file and return list of dictionaries"""
    decoded_file = file.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)
    
    # Validate headers
    if not all(col in reader.fieldnames for col in columns):
        raise ValueError(f"CSV must contain columns: {', '.join(columns)}")
    
    return list(reader)


def process_excel_file(file, columns):
    """Process Excel file and return list of dictionaries"""
    wb = load_workbook(file)
    ws = wb.active
    
    # Get headers from first row
    headers = [cell.value for cell in ws[1]]
    
    # Validate headers
    if not all(col in headers for col in columns):
        raise ValueError(f"Excel file must contain columns: {', '.join(columns)}")
    
    # Create list of dictionaries
    data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        row_dict = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
        data.append(row_dict)
    
    return data


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["GET", "POST"])
def bulk_upload_region(request):
    """Bulk upload regions from CSV/Excel"""
    if request.method == 'POST':
        form = RegionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                # Process file based on extension
                if file_ext == 'csv':
                    data = process_csv_file(file, ['name', 'code'])
                else:
                    data = process_excel_file(file, ['name', 'code'])
                
                # Create or update regions
                created_count = 0
                updated_count = 0
                
                for row in data:
                    if not row.get('name') or not row.get('code'):
                        continue
                    
                    region, created = Region.objects.update_or_create(
                        code=row['code'],
                        defaults={'name': row['name']}
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                messages.success(request, f'Successfully processed {created_count} new regions and updated {updated_count} existing regions.')
                return redirect('tenders:custom_admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = RegionUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Upload Regions',
        'model_name': 'Region',
        'required_columns': 'name, code',
        'example_data': 'Western Region,WR\nEastern Region,ER\nCentral Region,CR'
    }
    return render(request, 'tenders/admin/bulk_upload.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["GET", "POST"])
def bulk_upload_department(request):
    """Bulk upload departments from CSV/Excel"""
    if request.method == 'POST':
        form = DepartmentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                if file_ext == 'csv':
                    data = process_csv_file(file, ['name', 'code'])
                else:
                    data = process_excel_file(file, ['name', 'code'])
                
                created_count = 0
                updated_count = 0
                
                for row in data:
                    if not row.get('name') or not row.get('code'):
                        continue
                    
                    department, created = Department.objects.update_or_create(
                        code=row['code'],
                        defaults={'name': row['name']}
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                messages.success(request, f'Successfully processed {created_count} new departments and updated {updated_count} existing departments.')
                return redirect('tenders:custom_admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = DepartmentUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Upload Departments',
        'model_name': 'Department',
        'required_columns': 'name, code',
        'example_data': 'Human Resources,HR\nFinance,FIN\nProcurement,PROC'
    }
    return render(request, 'tenders/admin/bulk_upload.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["GET", "POST"])
def bulk_upload_division(request):
    """Bulk upload divisions from CSV/Excel"""
    if request.method == 'POST':
        form = DivisionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                if file_ext == 'csv':
                    data = process_csv_file(file, ['name', 'code', 'department_code'])
                else:
                    data = process_excel_file(file, ['name', 'code', 'department_code'])
                
                created_count = 0
                updated_count = 0
                errors = []
                
                for row in data:
                    if not row.get('name') or not row.get('code'):
                        continue
                    
                    try:
                        department = None
                        if row.get('department_code'):
                            department = Department.objects.get(code=row['department_code'])
                        
                        division, created = Division.objects.update_or_create(
                            code=row['code'],
                            defaults={
                                'name': row['name'],
                                'department': department
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    except Department.DoesNotExist:
                        errors.append(f"Department with code '{row.get('department_code')}' not found for division '{row['name']}'")
                
                if errors:
                    for error in errors:
                        messages.warning(request, error)
                
                messages.success(request, f'Successfully processed {created_count} new divisions and updated {updated_count} existing divisions.')
                return redirect('tenders:custom_admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = DivisionUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Upload Divisions',
        'model_name': 'Division',
        'required_columns': 'name, code, department_code',
        'example_data': 'Operations Division,OPS,PROC\nStrategic Division,STRAT,HR'
    }
    return render(request, 'tenders/admin/bulk_upload.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["GET", "POST"])
def bulk_upload_section(request):
    """Bulk upload sections from CSV/Excel"""
    if request.method == 'POST':
        form = SectionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                if file_ext == 'csv':
                    data = process_csv_file(file, ['name', 'code', 'division_code'])
                else:
                    data = process_excel_file(file, ['name', 'code', 'division_code'])
                
                created_count = 0
                updated_count = 0
                errors = []
                
                for row in data:
                    if not row.get('name') or not row.get('code'):
                        continue
                    
                    try:
                        division = None
                        if row.get('division_code'):
                            division = Division.objects.get(code=row['division_code'])
                        
                        section, created = Section.objects.update_or_create(
                            code=row['code'],
                            defaults={
                                'name': row['name'],
                                'division': division
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    except Division.DoesNotExist:
                        errors.append(f"Division with code '{row.get('division_code')}' not found for section '{row['name']}'")
                
                if errors:
                    for error in errors:
                        messages.warning(request, error)
                
                messages.success(request, f'Successfully processed {created_count} new sections and updated {updated_count} existing sections.')
                return redirect('tenders:custom_admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = SectionUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Upload Sections',
        'model_name': 'Section',
        'required_columns': 'name, code, division_code',
        'example_data': 'Tender Management,TM,OPS\nContract Admin,CA,OPS'
    }
    return render(request, 'tenders/admin/bulk_upload.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["GET", "POST"])
def bulk_upload_procurement_type(request):
    """Bulk upload procurement types from CSV/Excel"""
    if request.method == 'POST':
        form = ProcurementTypeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                if file_ext == 'csv':
                    data = process_csv_file(file, ['name', 'code'])
                else:
                    data = process_excel_file(file, ['name', 'code'])
                
                created_count = 0
                updated_count = 0
                
                for row in data:
                    if not row.get('name') or not row.get('code'):
                        continue
                    
                    proc_type, created = ProcurementType.objects.update_or_create(
                        code=row['code'],
                        defaults={'name': row['name']}
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                messages.success(request, f'Successfully processed {created_count} new procurement types and updated {updated_count} existing types.')
                return redirect('tenders:custom_admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = ProcurementTypeUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Upload Procurement Types',
        'model_name': 'Procurement Type',
        'required_columns': 'name, code',
        'example_data': 'Open Tender,OT\nRestricted Tender,RT\nDirect Procurement,DP'
    }
    return render(request, 'tenders/admin/bulk_upload.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["GET", "POST"])
def bulk_upload_loa_status(request):
    """Bulk upload LOA statuses from CSV/Excel"""
    if request.method == 'POST':
        form = LOAStatusUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                if file_ext == 'csv':
                    data = process_csv_file(file, ['name'])
                else:
                    data = process_excel_file(file, ['name'])
                
                created_count = 0
                updated_count = 0
                
                for row in data:
                    if not row.get('name'):
                        continue
                    
                    status, created = LOAStatus.objects.get_or_create(
                        name=row['name']
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                messages.success(request, f'Successfully processed {created_count} new LOA statuses.')
                return redirect('tenders:custom_admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = LOAStatusUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Upload LOA Statuses',
        'model_name': 'LOA Status',
        'required_columns': 'name',
        'example_data': 'Pending\nApproved\nRejected'
    }
    return render(request, 'tenders/admin/bulk_upload.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["GET", "POST"])
def bulk_upload_contract_status(request):
    """Bulk upload contract statuses from CSV/Excel"""
    if request.method == 'POST':
        form = ContractStatusUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_ext = file.name.split('.')[-1].lower()
            
            try:
                if file_ext == 'csv':
                    data = process_csv_file(file, ['name'])
                else:
                    data = process_excel_file(file, ['name'])
                
                created_count = 0
                updated_count = 0
                
                for row in data:
                    if not row.get('name'):
                        continue
                    
                    status, created = ContractStatus.objects.get_or_create(
                        name=row['name']
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                messages.success(request, f'Successfully processed {created_count} new contract statuses.')
                return redirect('tenders:custom_admin_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
    else:
        form = ContractStatusUploadForm()
    
    context = {
        'form': form,
        'title': 'Bulk Upload Contract Statuses',
        'model_name': 'Contract Status',
        'required_columns': 'name',
        'example_data': 'Active\nExpired\nTerminated'
    }
    return render(request, 'tenders/admin/bulk_upload.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def manage_user_employee_links(request):
    """View to manage user-employee linkages"""
    from django.contrib.auth.models import User
    from .models import UserProfile, Employee
    
    # Ensure all users have profiles (create missing ones)
    for user in User.objects.all():
        if not hasattr(user, 'profile'):
            # Try to find matching employee by username
            employee = Employee.objects.filter(employee_id=user.username).first()
            UserProfile.objects.create(user=user, employee=employee)
    
    # Get all users with their profiles
    users = User.objects.select_related('profile', 'profile__employee').all()
    
    # Get unlinked employees (no user_account)
    unlinked_employees = Employee.objects.filter(user_account__isnull=True, is_active=True)
    
    # Get users without employee links
    unlinked_users = [u for u in users if not u.profile.employee]
    
    context = {
        'title': 'Manage User-Employee Links',
        'users': users,
        'unlinked_employees': unlinked_employees,
        'unlinked_users': unlinked_users,
    }
    return render(request, 'tenders/admin/user_employee_links.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
@require_http_methods(["POST"])
def link_user_to_employee(request, user_id):
    """Link a user to an employee"""
    from django.contrib.auth.models import User
    from .models import UserProfile, Employee
    
    user = User.objects.get(pk=user_id)
    employee_id = request.POST.get('employee_id')
    
    if employee_id:
        try:
            employee = Employee.objects.get(pk=employee_id)
            user.profile.employee = employee
            user.profile.save()
            messages.success(request, f'Successfully linked {user.username} to {employee.full_name}')
        except Employee.DoesNotExist:
            messages.error(request, 'Employee not found')
    else:
        # Unlink
        user.profile.employee = None
        user.profile.save()
        messages.success(request, f'Unlinked {user.username} from employee')
    
    return redirect('tenders:manage_user_employee_links')
