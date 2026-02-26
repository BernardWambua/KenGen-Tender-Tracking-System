from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, Sum
from datetime import datetime, timedelta
from .models import (
    Tender, Contract, Employee, Department, Region, Requisition,
    LOAStatus, ContractStatus
)
from .forms import (
    TenderForm, TenderOpeningCommitteeFormSet, 
    TenderEvaluationCommitteeFormSet, EmployeeForm,
    ContractForm, ContractCITCommitteeFormSet, RequisitionForm
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
    total_requisitions = Requisition.objects.count()
    total_contracts = Contract.objects.count()
    active_tenders = Tender.objects.filter(
        tender_closing_date__gte=datetime.now().date()
    ).count()
    total_employees = Employee.objects.filter(is_active=True).count()
    total_value = Requisition.objects.aggregate(
        total=Sum('shopping_cart_amount')
    )['total'] or 0
    
    # Recent tenders
    recent_tenders = Tender.objects.select_related(
        'requisition', 'requisition__region', 'requisition__department'
    ).prefetch_related('contract').order_by('-created_at')[:5]

    recent_requisitions = Requisition.objects.select_related(
        'region', 'department', 'division', 'section', 'assigned_user'
    ).order_by('-created_at')[:5]

    recent_contracts = Contract.objects.select_related(
        'tender', 'tender__requisition', 'tender__requisition__region', 'tender__requisition__department'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_tenders': total_tenders,
        'total_requisitions': total_requisitions,
        'total_contracts': total_contracts,
        'active_tenders': active_tenders,
        'total_employees': total_employees,
        'total_value': total_value,
        'recent_tenders': recent_tenders,
        'recent_requisitions': recent_requisitions,
        'recent_contracts': recent_contracts,
    }
    return render(request, 'tenders/landing.html', context)


@login_required
def dashboard(request):
    """Dashboard with analytics and charts"""
    total_requisitions = Requisition.objects.count()
    total_contracts = Contract.objects.count()
    # Contracts by step
    contract_step_counts = Contract.objects.values('contract_step').annotate(
        count=Count('id')
    ).order_by('-count')
    contract_step_labels = dict(Contract.CONTRACT_STEP_CHOICES)
    tenders_by_loa_status = [
        {
            'name': contract_step_labels.get(item['contract_step'], 'Unspecified'),
            'count': item['count'],
        }
        for item in contract_step_counts
    ]
    
    tenders_by_contract_status = ContractStatus.objects.annotate(
        count=Count('contracts')
    ).order_by('-count')
    
    # Tenders by procurement method
    tender_method_counts = Tender.objects.values('procurement_method').annotate(
        count=Count('id')
    ).order_by('-count')
    procurement_method_labels = dict(Tender.PROCUREMENT_METHOD_CHOICES)
    tenders_by_type = [
        {
            'name': procurement_method_labels.get(item['procurement_method'], 'Unspecified'),
            'count': item['count'],
        }
        for item in tender_method_counts
    ]
    
    # Requisitions by region
    tenders_by_region = Region.objects.annotate(
        count=Count('requisitions', distinct=True)
    ).order_by('-count')
    
    # Requisitions by department
    tenders_by_department = Department.objects.annotate(
        count=Count('requisitions', distinct=True)
    ).order_by('-count')[:10]
    
    # Upcoming closing dates
    upcoming_tenders = Tender.objects.filter(
        tender_closing_date__gte=datetime.now().date(),
        tender_closing_date__lte=datetime.now().date() + timedelta(days=30)
    ).select_related('requisition__department', 'requisition__region').order_by('tender_closing_date')[:10]
    
    # Recent activity
    recent_tenders = Tender.objects.select_related(
        'tender_creator', 'requisition__region', 'requisition__department'
    ).order_by('-created_at')[:10]

    recent_requisitions = Requisition.objects.select_related(
        'region', 'department', 'division', 'section', 'assigned_user'
    ).order_by('-created_at')[:10]

    recent_contracts = Contract.objects.select_related(
        'tender', 'tender__requisition', 'tender__requisition__region', 'tender__requisition__department'
    ).order_by('-created_at')[:10]
    
    context = {
        'total_requisitions': total_requisitions,
        'total_contracts': total_contracts,
        'tenders_by_loa_status': tenders_by_loa_status,
        'tenders_by_contract_status': tenders_by_contract_status,
        'tenders_by_type': tenders_by_type,
        'tenders_by_region': tenders_by_region,
        'tenders_by_department': tenders_by_department,
        'upcoming_tenders': upcoming_tenders,
        'recent_tenders': recent_tenders,
        'recent_requisitions': recent_requisitions,
        'recent_contracts': recent_contracts,
    }
    return render(request, 'tenders/dashboard.html', context)


@login_required
def tender_list(request):
    """List all tenders with filters"""
    tenders = Tender.objects.select_related(
        'requisition', 'requisition__region', 'requisition__department',
        'requisition__division', 'requisition__section', 'tender_creator'
    ).prefetch_related('contract').all()
    
    # Filters
    search_query = request.GET.get('search', '')
    if search_query:
        tender_filters = (
            Q(tender_description__icontains=search_query) |
            Q(tender_reference_number__icontains=search_query)
        )
        if search_query.isdigit():
            tender_filters |= Q(tender_id=int(search_query))
        tenders = tenders.filter(tender_filters)
    
    region_filter = request.GET.get('region', '')
    if region_filter:
        tenders = tenders.filter(requisition__region_id=region_filter)
    
    department_filter = request.GET.get('department', '')
    if department_filter:
        tenders = tenders.filter(requisition__department_id=department_filter)
    
    procurement_method_filter = request.GET.get('procurement_method', '')
    if procurement_method_filter:
        tenders = tenders.filter(procurement_method=procurement_method_filter)
    
    loa_status_filter = request.GET.get('loa_status', '')
    if loa_status_filter:
        tenders = tenders.filter(contract__loa_status_id=loa_status_filter)
    
    contract_status_filter = request.GET.get('contract_status', '')
    if contract_status_filter:
        tenders = tenders.filter(contract__contract_status_id=contract_status_filter)
    
    # For filter dropdowns
    regions = Region.objects.all()
    departments = Department.objects.all()
    procurement_methods = Tender.PROCUREMENT_METHOD_CHOICES
    loa_statuses = LOAStatus.objects.all()
    contract_statuses = ContractStatus.objects.all()
    
    tenders = tenders.order_by('-tender_advert_date', '-created_at')
    
    context = {
        'tenders': tenders,
        'regions': regions,
        'departments': departments,
        'procurement_methods': procurement_methods,
        'loa_statuses': loa_statuses,
        'contract_statuses': contract_statuses,
        'search_query': search_query,
        'region_filter': region_filter,
        'department_filter': department_filter,
        'procurement_method_filter': procurement_method_filter,
        'loa_status_filter': loa_status_filter,
        'contract_status_filter': contract_status_filter,
    }
    return render(request, 'tenders/tender_list.html', context)


@login_required
def tender_detail(request, pk):
    """Detail view for a single tender"""
    tender = get_object_or_404(
        Tender.objects.select_related(
            'requisition', 'requisition__region', 'requisition__department',
            'requisition__division', 'requisition__section', 'requisition__assigned_user',
            'tender_creator'
        ).prefetch_related(
            'opening_committee_members__employee',
            'evaluation_committee_members__employee',
            'contract'
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
            employee = form.save(commit=False)
            employee.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
            employee.save()
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
def requisition_list(request):
    """List all requisitions"""
    requisitions = Requisition.objects.select_related(
        'region', 'department', 'division', 'section', 'assigned_user', 'tender_creator'
    ).all()

    search_query = request.GET.get('search', '')
    if search_query:
        requisitions = requisitions.filter(
            Q(e_requisition_no__icontains=search_query) |
            Q(shopping_cart_no__icontains=search_query) |
            Q(requisition_description__icontains=search_query)
        )

    department_filter = request.GET.get('department', '')
    if department_filter:
        requisitions = requisitions.filter(department_id=department_filter)

    departments = Department.objects.all()

    context = {
        'requisitions': requisitions.order_by('-created_at'),
        'departments': departments,
        'department_filter': department_filter,
        'search_query': search_query,
    }
    return render(request, 'tenders/requisition_list.html', context)


@login_required
@user_passes_test(can_create_edit_tenders)
def requisition_create(request):
    """Create a requisition"""
    if request.method == 'POST':
        form = RequisitionForm(request.POST)
        if form.is_valid():
            requisition = form.save(commit=False)
            requisition.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
            requisition.save()
            messages.success(request, f'Requisition {requisition.e_requisition_no} created successfully!')
            return redirect('tenders:requisition_list')
    else:
        form = RequisitionForm()

    context = {
        'form': form,
        'is_edit': False,
        'deadline_days': getattr(settings, 'REQUISITION_CREATION_DEADLINE_DAYS', 7),
    }
    return render(request, 'tenders/requisition_form.html', context)


@login_required
@user_passes_test(can_create_edit_tenders)
def requisition_edit(request, pk):
    """Edit a requisition"""
    requisition = get_object_or_404(Requisition, pk=pk)

    if request.method == 'POST':
        form = RequisitionForm(request.POST, instance=requisition)
        if form.is_valid():
            requisition = form.save(commit=False)
            if requisition.created_by_id is None:
                requisition.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
            requisition.save()
            messages.success(request, f'Requisition {requisition.e_requisition_no} updated successfully!')
            return redirect('tenders:requisition_list')
    else:
        form = RequisitionForm(instance=requisition)

    context = {
        'form': form,
        'is_edit': True,
        'requisition': requisition,
        'deadline_days': getattr(settings, 'REQUISITION_CREATION_DEADLINE_DAYS', 7),
    }
    return render(request, 'tenders/requisition_form.html', context)


@login_required
@user_passes_test(can_create_edit_tenders)
def tender_create(request):
    """Create a new tender - Admin and Tender Staff only"""
    if request.method == 'POST':
        form = TenderForm(request.POST)
        opening_formset = TenderOpeningCommitteeFormSet(request.POST)
        evaluation_formset = TenderEvaluationCommitteeFormSet(request.POST)
        
        if form.is_valid() and opening_formset.is_valid() and evaluation_formset.is_valid():
            tender = form.save(commit=False)
            tender.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
            tender.save()
            
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
            tender = form.save(commit=False)
            if tender.created_by_id is None:
                tender.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
            tender.save()
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


@login_required
@user_passes_test(can_create_edit_tenders)
def contract_create(request, tender_pk):
    """Create a contract for a tender - Admin and Tender Staff only"""
    tender = get_object_or_404(Tender, pk=tender_pk)
    
    # Check if contract already exists
    if hasattr(tender, 'contract'):
        messages.warning(request, 'This tender already has a contract. Please edit the existing contract.')
        return redirect('tenders:contract_edit', tender_pk=tender.pk)
    
    if request.method == 'POST':
        form = ContractForm(request.POST)
        cit_formset = ContractCITCommitteeFormSet(request.POST)
        
        if form.is_valid() and cit_formset.is_valid():
            contract = form.save(commit=False)
            contract.tender = tender
            contract.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
            contract.save()
            
            # Save CIT committee
            cit_formset.instance = contract
            cit_formset.save()
            
            messages.success(request, f'Contract for {tender.tender_id} created successfully!')
            return redirect('tenders:tender_detail', pk=tender.pk)
    else:
        # Pre-populate the form with tender reference
        initial_data = {'tender': tender}
        form = ContractForm(initial=initial_data)
        form.fields['tender'].widget.attrs['readonly'] = True
        cit_formset = ContractCITCommitteeFormSet()
    
    context = {
        'form': form,
        'cit_formset': cit_formset,
        'tender': tender,
        'is_edit': False,
    }
    return render(request, 'tenders/contract_form.html', context)


@login_required
@user_passes_test(can_create_edit_tenders)
def contract_edit(request, tender_pk):
    """Edit a contract for a tender - Admin and Tender Staff only"""
    tender = get_object_or_404(Tender, pk=tender_pk)
    contract = get_object_or_404(Contract, tender=tender)
    
    if request.method == 'POST':
        form = ContractForm(request.POST, instance=contract)
        cit_formset = ContractCITCommitteeFormSet(request.POST, instance=contract)
        
        if form.is_valid() and cit_formset.is_valid():
            contract = form.save(commit=False)
            if contract.created_by_id is None:
                contract.created_by = getattr(getattr(request.user, 'profile', None), 'employee', None)
            contract.save()
            cit_formset.save()
            
            messages.success(request, f'Contract for {tender.tender_id} updated successfully!')
            return redirect('tenders:tender_detail', pk=tender.pk)
    else:
        form = ContractForm(instance=contract)
        form.fields['tender'].widget.attrs['readonly'] = True
        cit_formset = ContractCITCommitteeFormSet(instance=contract)
    
    context = {
        'form': form,
        'cit_formset': cit_formset,
        'tender': tender,
        'contract': contract,
        'is_edit': True,
    }
    return render(request, 'tenders/contract_form.html', context)


@login_required
@user_passes_test(is_admin_or_superuser)
def contract_delete(request, tender_pk):
    """Delete a contract - Admin only"""
    tender = get_object_or_404(Tender, pk=tender_pk)
    contract = get_object_or_404(Contract, tender=tender)
    
    if request.method == 'POST':
        contract_ref = contract.contract_number or f"Contract for {tender.tender_id}"
        contract.delete()
        messages.success(request, f'{contract_ref} deleted successfully!')
        return redirect('tenders:tender_detail', pk=tender.pk)
    
    context = {
        'contract': contract,
        'tender': tender,
    }
    return render(request, 'tenders/contract_confirm_delete.html', context)
