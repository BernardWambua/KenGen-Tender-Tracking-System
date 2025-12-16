from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from .models import (
    Tender, Employee, Department, Region, 
    ProcurementType, LOAStatus, ContractStatus
)
from .forms import (
    TenderForm, TenderOpeningCommitteeFormSet, 
    TenderEvaluationCommitteeFormSet, EmployeeForm
)
from .auth_forms import SignUpForm

# Create your views here.

# Role-based access control
def is_admin_or_superuser(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or user.groups.filter(name='Admin').exists()

def can_create_edit_tenders(user):
    """Check if user can create/edit tenders (Admin or Tender Staff)"""
    return user.is_superuser or user.groups.filter(name__in=['Admin', 'Tender Staff']).exists()

def landing_page(request):
    """Landing page with overview and statistics"""
    total_tenders = Tender.objects.count()
    active_tenders = Tender.objects.filter(
        tender_closing_date__gte=datetime.now().date()
    ).count()
    total_employees = Employee.objects.filter(is_active=True).count()
    total_value = Tender.objects.aggregate(
        total=Sum('estimated_value')
    )['total'] or 0
    
    # Recent tenders
    recent_tenders = Tender.objects.select_related(
        'procurement_type', 'region', 'department', 'loa_status', 'contract_status'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_tenders': total_tenders,
        'active_tenders': active_tenders,
        'total_employees': total_employees,
        'total_value': total_value,
        'recent_tenders': recent_tenders,
    }
    return render(request, 'tenders/landing.html', context)


@login_required
def dashboard(request):
    """Dashboard with analytics and charts"""
    # Tenders by status
    tenders_by_loa_status = LOAStatus.objects.annotate(
        count=Count('tenders')
    ).order_by('-count')
    
    tenders_by_contract_status = ContractStatus.objects.annotate(
        count=Count('tenders')
    ).order_by('-count')
    
    # Tenders by procurement type
    tenders_by_type = ProcurementType.objects.annotate(
        count=Count('tenders')
    ).order_by('-count')
    
    # Tenders by region
    tenders_by_region = Region.objects.annotate(
        count=Count('tenders')
    ).order_by('-count')
    
    # Tenders by department
    tenders_by_department = Department.objects.annotate(
        count=Count('tenders')
    ).order_by('-count')[:10]
    
    # Upcoming closing dates
    upcoming_tenders = Tender.objects.filter(
        tender_closing_date__gte=datetime.now().date(),
        tender_closing_date__lte=datetime.now().date() + timedelta(days=30)
    ).select_related('department', 'region').order_by('tender_closing_date')[:10]
    
    # Recent activity
    recent_tenders = Tender.objects.select_related(
        'procurement_type', 'tender_creator', 'department'
    ).order_by('-created_at')[:10]
    
    context = {
        'tenders_by_loa_status': tenders_by_loa_status,
        'tenders_by_contract_status': tenders_by_contract_status,
        'tenders_by_type': tenders_by_type,
        'tenders_by_region': tenders_by_region,
        'tenders_by_department': tenders_by_department,
        'upcoming_tenders': upcoming_tenders,
        'recent_tenders': recent_tenders,
    }
    return render(request, 'tenders/dashboard.html', context)


@login_required
def tender_list(request):
    """List all tenders with filters"""
    tenders = Tender.objects.select_related(
        'procurement_type', 'region', 'department', 'section',
        'tender_creator', 'loa_status', 'contract_status'
    ).all()
    
    # Filters
    search_query = request.GET.get('search', '')
    if search_query:
        tenders = tenders.filter(
            Q(tender_id__icontains=search_query) |
            Q(tender_description__icontains=search_query) |
            Q(egp_tender_reference__icontains=search_query) |
            Q(kengen_tender_reference__icontains=search_query)
        )
    
    region_filter = request.GET.get('region', '')
    if region_filter:
        tenders = tenders.filter(region_id=region_filter)
    
    department_filter = request.GET.get('department', '')
    if department_filter:
        tenders = tenders.filter(department_id=department_filter)
    
    procurement_type_filter = request.GET.get('procurement_type', '')
    if procurement_type_filter:
        tenders = tenders.filter(procurement_type_id=procurement_type_filter)
    
    loa_status_filter = request.GET.get('loa_status', '')
    if loa_status_filter:
        tenders = tenders.filter(loa_status_id=loa_status_filter)
    
    contract_status_filter = request.GET.get('contract_status', '')
    if contract_status_filter:
        tenders = tenders.filter(contract_status_id=contract_status_filter)
    
    # For filter dropdowns
    regions = Region.objects.all()
    departments = Department.objects.all()
    procurement_types = ProcurementType.objects.all()
    loa_statuses = LOAStatus.objects.all()
    contract_statuses = ContractStatus.objects.all()
    
    tenders = tenders.order_by('-tender_advert_date', '-created_at')
    
    context = {
        'tenders': tenders,
        'regions': regions,
        'departments': departments,
        'procurement_types': procurement_types,
        'loa_statuses': loa_statuses,
        'contract_statuses': contract_statuses,
        'search_query': search_query,
        'region_filter': region_filter,
        'department_filter': department_filter,
        'procurement_type_filter': procurement_type_filter,
        'loa_status_filter': loa_status_filter,
        'contract_status_filter': contract_status_filter,
    }
    return render(request, 'tenders/tender_list.html', context)


@login_required
def tender_detail(request, pk):
    """Detail view for a single tender"""
    tender = get_object_or_404(
        Tender.objects.select_related(
            'procurement_type', 'region', 'department', 'section',
            'tender_creator', 'contract_creator', 'user',
            'loa_status', 'contract_status'
        ).prefetch_related(
            'opening_committee_members__employee',
            'evaluation_committee_members__employee'
        ),
        pk=pk
    )
    
    context = {
        'tender': tender,
    }
    return render(request, 'tenders/tender_detail.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def employee_list(request):
    """List all employees - Admin only"""
    employees = Employee.objects.select_related(
        'department', 'division', 'section', 'user_account__user'
    ).filter(is_active=True).order_by('last_name', 'first_name')
    
    # Filter by department
    department_filter = request.GET.get('department', '')
    if department_filter:
        employees = employees.filter(department_id=department_filter)
    
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    departments = Department.objects.all()
    
    context = {
        'employees': employees,
        'departments': departments,
        'department_filter': department_filter,
        'search_query': search_query,
    }
    return render(request, 'tenders/employee_list.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def employee_create(request):
    """Create a new employee - Admin only"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.full_name} created successfully!')
            return redirect('tenders:employee_list')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'tenders/employee_form.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def employee_edit(request, pk):
    """Edit an existing employee - Admin only"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.full_name} updated successfully!')
            return redirect('tenders:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    
    context = {
        'form': form,
        'employee': employee,
        'is_edit': True,
    }
    return render(request, 'tenders/employee_form.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def employee_delete(request, pk):
    """Delete/deactivate an employee - Admin only"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.full_name
        # Soft delete - just mark as inactive
        employee.is_active = False
        employee.save()
        messages.success(request, f'Employee {employee_name} deactivated successfully!')
        return redirect('tenders:employee_list')
    
    context = {
        'employee': employee,
    }
    return render(request, 'tenders/employee_confirm_delete.html', context)


@login_required
@user_passes_test(can_create_edit_tenders)
def tender_create(request):
    """Create a new tender - Admin and Tender Staff only"""
    if request.method == 'POST':
        form = TenderForm(request.POST)
        opening_formset = TenderOpeningCommitteeFormSet(request.POST)
        evaluation_formset = TenderEvaluationCommitteeFormSet(request.POST)
        
        if form.is_valid() and opening_formset.is_valid() and evaluation_formset.is_valid():
            tender = form.save()
            
            # Save opening committee
            opening_formset.instance = tender
            opening_formset.save()
            
            # Save evaluation committee
            evaluation_formset.instance = tender
            evaluation_formset.save()
            
            messages.success(request, f'Tender {tender.tender_id} created successfully!')
            return redirect('tenders:tender_detail', pk=tender.pk)
    else:
        form = TenderForm()
        opening_formset = TenderOpeningCommitteeFormSet()
        evaluation_formset = TenderEvaluationCommitteeFormSet()
    
    context = {
        'form': form,
        'opening_formset': opening_formset,
        'evaluation_formset': evaluation_formset,
        'is_edit': False,
    }
    return render(request, 'tenders/tender_form.html', context)


@login_required
@user_passes_test(can_create_edit_tenders)
def tender_edit(request, pk):
    """Edit an existing tender - Admin and Tender Staff only"""
    tender = get_object_or_404(Tender, pk=pk)
    
    if request.method == 'POST':
        form = TenderForm(request.POST, instance=tender)
        opening_formset = TenderOpeningCommitteeFormSet(request.POST, instance=tender)
        evaluation_formset = TenderEvaluationCommitteeFormSet(request.POST, instance=tender)
        
        if form.is_valid() and opening_formset.is_valid() and evaluation_formset.is_valid():
            tender = form.save()
            opening_formset.save()
            evaluation_formset.save()
            
            messages.success(request, f'Tender {tender.tender_id} updated successfully!')
            return redirect('tenders:tender_detail', pk=tender.pk)
    else:
        form = TenderForm(instance=tender)
        opening_formset = TenderOpeningCommitteeFormSet(instance=tender)
        evaluation_formset = TenderEvaluationCommitteeFormSet(instance=tender)
    
    context = {
        'form': form,
        'opening_formset': opening_formset,
        'evaluation_formset': evaluation_formset,
        'tender': tender,
        'is_edit': True,
    }
    return render(request, 'tenders/tender_form.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def tender_delete(request, pk):
    """Delete a tender - Admin only"""
    tender = get_object_or_404(Tender, pk=pk)
    
    if request.method == 'POST':
        tender_id = tender.tender_id
        tender.delete()
        messages.success(request, f'Tender {tender_id} deleted successfully!')
        return redirect('tenders:tender_list')
    
    context = {
        'tender': tender,
    }
    return render(request, 'tenders/tender_confirm_delete.html', context)


def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('tenders:landing')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Log the user in
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, f'Welcome {user.first_name}! Your account has been created with Tender Staff role.')
            return redirect('tenders:landing')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
    }
    return render(request, 'tenders/auth/signup.html', context)
