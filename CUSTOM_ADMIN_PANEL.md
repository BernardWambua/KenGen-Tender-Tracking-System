# Admin Panel with Bulk Upload - Setup Guide

## Overview
This Admin panel provides bulk upload functionality for lookup models with role-based access control.

## Features

### 1. Bulk Upload Support
- Upload CSV or Excel files (.csv, .xlsx, .xls)
- Automatic validation and error handling
- Update existing records or create new ones
- Maximum file size: 5MB

### 2. Supported Models
- **Region** - Required columns: name, code
- **Department** - Required columns: name, code
- **Division** - Required columns: name, code, department_code
- **Section** - Required columns: name, code, division_code
- **Procurement Type** - Required columns: name, code
- **e-Contract Step** - Required columns: name
- **e-Contract Status** - Required columns: name

### 3. Role-Based Access Control

#### User Roles:
1. **Tender Admin**
   - Full access to bulk uploads
   - Can add, change, delete, and view all models
   - Access to Admin panel

2. **Tender Manager**
   - Can create and manage tenders
   - View-only access to lookup data
   - Manage committee members

3. **Tender Staff**
   - Can add and view tenders
   - View-only access to all other data

4. **Superuser**
   - Complete system access
   - Access to Django admin and Admin panel

## Setup Instructions

### Step 1: Install Required Package
```bash
pip install openpyxl
```

### Step 2: Create User Groups and Permissions
```bash
python manage.py setup_groups
```

This command will create three user groups with appropriate permissions.

### Step 3: Assign Users to Groups

#### Option A: Using Django Admin
1. Go to `/admin/`
2. Navigate to Users
3. Edit a user
4. Scroll to "Groups" section
5. Add user to desired group (e.g., "Tender Admin")
6. Save

#### Option B: Using Django Shell
```python
python manage.py shell

from django.contrib.auth.models import User, Group

# Get the user
user = User.objects.get(username='your_username')

# Get the group
group = Group.objects.get(name='Tender Admin')

# Add user to group
user.groups.add(group)
```

### Step 4: Access Admin Panel
- URL: `/custom-admin/`
- Only accessible to users with "Tender Admin" role or superusers
- Click "Admin" in the navigation bar (visible only to authorized users)

## Usage

### Bulk Upload Process

1. **Access the Admin Panel**
   - Navigate to `/custom-admin/`
   - You'll see all lookup models with their current record counts

2. **Select a Model to Upload**
   - Click "Bulk Upload" on any model card

3. **Download Template (Optional)**
   - Click "Download CSV Template" for a pre-formatted file
   - Or create your own CSV/Excel file with required columns

4. **Prepare Your Data**
   - Example for Regions (CSV):
     ```csv
     name,code
     Western Region,WR
     Eastern Region,ER
     Central Region,CR
     ```

   - Example for Divisions (CSV):
     ```csv
     name,code,department_code
     Operations Division,OPS,PROC
     Strategic Division,STRAT,HR
     ```

5. **Upload the File**
   - Choose your CSV or Excel file
   - Click "Upload and Process"
   - System will validate and import the data

6. **Review Results**
   - Success message shows count of created/updated records
   - Warning messages indicate any skipped rows or errors

### File Format Requirements

#### CSV Format
```csv
column1,column2,column3
value1,value2,value3
value4,value5,value6
```

#### Excel Format
- First row must contain column headers
- Data starts from second row
- Use either .xlsx or .xls format

### Important Notes

1. **Duplicate Handling**
   - Records with matching codes will be updated
   - New codes will create new records

2. **Relationship Fields**
   - For Division: `department_code` must match existing Department code
   - For Section: `division_code` must match existing Division code
   - Missing relationships will generate warnings

3. **Validation**
   - Empty rows are automatically skipped
   - Rows with missing required fields are skipped
   - Invalid file formats are rejected

4. **Error Handling**
   - File size validation (5MB limit)
   - Format validation (CSV/Excel only)
   - Column validation (required columns must be present)
   - Data validation (relationships must exist)

## Security

### Access Control
- Admin panel requires authentication
- Only "Tender Admin" or superuser roles can access
- Regular users will see 403 Forbidden error
- Permissions enforced at view level with decorators

### Permission Decorators Used
```python
@login_required  # Must be logged in
@user_passes_test(is_admin_or_superuser)  # Must have admin role
```

## URL Structure

```
/custom-admin/                                    - Main dashboard
/custom-admin/bulk-upload/region/                - Upload regions
/custom-admin/bulk-upload/department/            - Upload departments
/custom-admin/bulk-upload/division/              - Upload divisions
/custom-admin/bulk-upload/section/               - Upload sections
/custom-admin/bulk-upload/procurement-type/      - Upload procurement types
/custom-admin/bulk-upload/loa-status/            - Upload e-Contract Stepes
/custom-admin/bulk-upload/contract-status/       - Upload e-Contract Statuses
```

## Troubleshooting

### Issue: "Permission Denied" Error
**Solution:** Ensure user is assigned to "Tender Admin" group or is a superuser.

### Issue: "Invalid file format" Error
**Solution:** Check file extension is .csv, .xlsx, or .xls

### Issue: "CSV must contain columns" Error
**Solution:** Verify first row has exact column names as specified

### Issue: Records not created/updated
**Solution:** Check for:
- Empty required fields
- Invalid relationship codes (department_code, division_code)
- File encoding issues (use UTF-8 for CSV)

### Issue: File size too large
**Solution:** Split data into multiple files under 5MB each

## Example Data Files

### regions.csv
```csv
name,code
Western Region,WR
Eastern Region,ER
Central Region,CR
Northern Region,NR
```

### departments.csv
```csv
name,code
Human Resources,HR
Finance,FIN
Procurement,PROC
Operations,OPS
```

### divisions.csv
```csv
name,code,department_code
Recruitment Division,REC,HR
Payroll Division,PAY,HR
Budget Division,BUD,FIN
Accounts Division,ACC,FIN
Tender Division,TEN,PROC
Contract Division,CON,PROC
```

### procurement_types.csv
```csv
name,code
Open Tender,OT
Restricted Tender,RT
Direct Procurement,DP
Request for Quotation,RFQ
```

## Next Steps

1. Create a superuser if you haven't already:
   ```bash
   python manage.py createsuperuser
   ```

2. Set up user groups:
   ```bash
   python manage.py setup_groups
   ```

3. Assign users to appropriate groups via Django admin

4. Test the bulk upload with sample data

5. Start importing your production data
