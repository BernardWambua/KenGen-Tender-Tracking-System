# User-Employee Relationship Refactoring

## Overview
Refactored the relationship between Users and Employees to support a more flexible architecture where:
- Employees can exist without user accounts (bulk uploaded)
- Users can exist without employee records (e.g., admin accounts)
- Auto-linking happens when users sign up with their staff number

## Changes Made

### 1. Models (`tenders/models.py`)
**Added UserProfile Model:**
- Links User to Employee via optional relationship
- Auto-created when User is created (via signals)
- Auto-links to employee if username matches employee_id

**Updated Employee Model:**
- Removed `user` OneToOneField (was causing tight coupling)
- Employee now independent entity
- Can be bulk uploaded without requiring user accounts

### 2. Forms (`tenders/auth_forms.py`)
**Updated SignUpForm:**
- Changed username label to "Staff Number"
- Updated placeholder to "Staff Number (e.g., EMP-001)"
- Added help text explaining auto-linking
- UserProfile auto-created and linked via signal

### 3. Employee Form (`tenders/forms.py`)
**Simplified EmployeeForm:**
- Removed `username` and `password` fields
- Employees managed separately from users
- Focused on employee data only

### 4. Admin Views (`tenders/admin_views.py`)
**Added User-Employee Management:**
- `manage_user_employee_links()` - View all user-employee links
- `link_user_to_employee()` - Manually link/unlink users
- Shows statistics (total users, linked users, unlinked employees)

### 5. Templates

**employee_form.html:**
- Removed system access section
- Clean employee data entry only

**signup.html:**
- Added info alert about using staff number
- Emphasizes auto-linking for employees
- Shows help text from form

**admin/dashboard.html:**
- Added "User Management" section
- Link to manage user-employee links

**admin/user_employee_links.html (NEW):**
- Shows all users with their employee links
- Modal dialogs for linking/unlinking
- Lists unlinked employees
- Statistics dashboard

### 6. URLs (`tenders/urls.py`)
Added routes:
- `/custom-admin/user-employee-links/` - Manage links page
- `/custom-admin/user-employee-links/<user_id>/link/` - Link/unlink action

### 7. Admin (`tenders/admin.py`)
- Registered UserProfile model
- Admin interface for viewing/editing links

## Workflow

### For Employees:
1. HR bulk uploads employee data via CSV/Excel
2. Employees exist in system without user accounts
3. When employee needs system access:
   - They sign up using their staff number as username
   - System auto-links their user account to employee record
   - Or admin manually links in admin panel

### For Non-Employee Users:
1. User signs up (e.g., admin, consultant)
2. UserProfile created but no employee link
3. User can still use system with assigned roles

### For Admins:
1. Access "Manage User-Employee Links" in admin panel
2. View all users and their employee links
3. Manually link/unlink as needed
4. See lists of unlinked users and employees

## Database Migration Required

Run these commands:
```bash
python manage.py makemigrations
python manage.py migrate
```

This will:
- Create UserProfile table
- Remove user field from Employee table
- Create signal handlers for auto-linking

## Benefits

1. **Flexibility**: Employees don't need user accounts
2. **Bulk Upload**: Easy mass import of employees
3. **Auto-Linking**: Staff number signup auto-links
4. **Manual Control**: Admins can manage links
5. **Clean Separation**: User auth separate from employee data
6. **Scalability**: Supports external users (contractors, consultants)
