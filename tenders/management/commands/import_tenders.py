"""
Management command to import tender data from CSV file
Usage: python manage.py import_tenders
"""
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tenders.models import (
    Region, Department, Division, Section, ProcurementType,
    LOAStatus, ContractStatus, Employee, Tender, Requisition
)


class Command(BaseCommand):
    help = 'Import tender data from CSV file'

    def handle(self, *args, **options):
        csv_file = 'Procurement Tracking.csv'
        
        self.stdout.write(self.style.SUCCESS(f'Starting import from {csv_file}'))
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                self.stdout.write(f"Processing Tender ID: {row.get('Tender ID', 'N/A')}")
                
                # Get or create lookup data
                region = self.get_or_create_region(row.get('Region'))
                department = self.get_or_create_department(row.get('Department '))  # Note the space in CSV
                section = self.get_or_create_section(row.get('Section'), department)
                division = section.division if section else None
                procurement_type = self.get_or_create_procurement_type(row.get('Procurement Type'))
                loa_status = self.get_or_create_loa_status(row.get('LOA (Letter of Award status)'))
                contract_status = self.get_or_create_contract_status(row.get('e-Contract Status'))
                
                # Get or create employees
                tender_creator = self.get_or_create_employee(row.get('Tender Creator'), department)
                contract_creator = self.get_or_create_employee(row.get('Contract Creator'), department)
                user = self.get_or_create_employee(row.get('User'), department)
                
                # Parse dates
                tender_advert_date = self.parse_date(row.get('Tender Advert Date'))
                tender_closing_date = self.parse_date(row.get('Tender Closing Date'))
                tender_validity_expiry_date = self.parse_date(row.get('Tender Validity Expiry Date'))
                
                # Parse time
                tender_closing_time = self.parse_time(row.get('Tender Closing Time'))
                
                # Parse estimated value
                estimated_value = self.parse_decimal(row.get('Estimated'))
                
                # Extract tender ID from the "Tender ID : 38" format
                tender_id_raw = row.get('Tender ID', '')
                tender_id = tender_id_raw.split(':')[-1].strip() if ':' in tender_id_raw else tender_id_raw
                
                requisition_number = row.get('Requisition Number') or None
                if not requisition_number:
                    requisition_number = f"REQ-{tender_id}"

                requisition, _ = Requisition.objects.update_or_create(
                    requisition_number=requisition_number,
                    defaults={
                        'shopping_cart': row.get('Shopping Cart') or None,
                        'region': region,
                        'department': department,
                        'division': division,
                        'section': section,
                        'assigned_user': user,
                    }
                )

                # Create or update tender
                tender, created = Tender.objects.update_or_create(
                    tender_id=tender_id,
                    defaults={
                        'requisition': requisition,
                        'egp_tender_reference': row.get('eGP Tender Reference') or None,
                        'kengen_tender_reference': row.get('KenGen Tender Reference') or None,
                        'tender_description': row.get('Tender Description') or '',
                        'procurement_type': procurement_type,
                        'tender_creator': tender_creator,
                        'tender_advert_date': tender_advert_date,
                        'tender_closing_date': tender_closing_date,
                        'tender_closing_time': tender_closing_time,
                        'tender_validity_expiry_date': tender_validity_expiry_date,
                        'tender_evaluation_duration': row.get('Tender Evaluation Duration(30/21 Days)') or None,
                        'estimated_value': estimated_value,
                    }
                )
                
                action = 'Created' if created else 'Updated'
                self.stdout.write(self.style.SUCCESS(f'{action} tender: {tender.tender_id}'))
        
        self.stdout.write(self.style.SUCCESS('Import completed successfully!'))
    
    def get_or_create_region(self, name):
        if not name or name.strip() == '':
            return None
        region, _ = Region.objects.get_or_create(name=name.strip())
        return region
    
    def get_or_create_department(self, name):
        if not name or name.strip() == '':
            return None
        department, _ = Department.objects.get_or_create(name=name.strip())
        return department
    
    def get_or_create_section(self, name, department):
        if not name or name.strip() == '' or not department:
            return None
        # For simplicity, create a default division if needed
        division, _ = Division.objects.get_or_create(
            name='General',
            department=department
        )
        section, _ = Section.objects.get_or_create(
            name=name.strip(),
            division=division
        )
        return section
    
    def get_or_create_procurement_type(self, name):
        if not name or name.strip() == '':
            return None
        proc_type, _ = ProcurementType.objects.get_or_create(name=name.strip())
        return proc_type
    
    def get_or_create_loa_status(self, name):
        if not name or name.strip() == '':
            return None
        loa_status, _ = LOAStatus.objects.get_or_create(name=name.strip())
        return loa_status
    
    def get_or_create_contract_status(self, name):
        if not name or name.strip() == '':
            return None
        contract_status, _ = ContractStatus.objects.get_or_create(name=name.strip())
        return contract_status
    
    def get_or_create_employee(self, name, department):
        if not name or name.strip() == '':
            return None
        
        # Split name into first and last
        name_parts = name.strip().split()
        first_name = name_parts[0] if len(name_parts) > 0 else 'Unknown'
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Create a username from the name
        username = name.strip().replace(' ', '_').lower()
        employee_id = username
        
        # Get or create user
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        # Get or create employee
        employee, _ = Employee.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': employee_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': f'{username}@kengen.co.ke',
                'department': department,
            }
        )
        
        return employee
    
    def parse_date(self, date_str):
        """Parse various date formats"""
        if not date_str or date_str.strip() == '':
            return None
        
        # Try different date formats
        formats = [
            '%dth %B %Y',  # 9th September 2025
            '%dst %B %Y',  # 1st September 2025
            '%dnd %B %Y',  # 2nd September 2025
            '%drd %B %Y',  # 3rd September 2025
            '%d %B %Y',    # 25 October 2025
            '%Y-%m-%d',    # 2025-09-09
            '%d/%m/%Y',    # 09/09/2025
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        self.stdout.write(self.style.WARNING(f'Could not parse date: {date_str}'))
        return None
    
    def parse_time(self, time_str):
        """Parse time format"""
        if not time_str or time_str.strip() == '':
            return None
        
        # Try different time formats
        formats = [
            '%I.%M %p',  # 10.00 a.m
            '%I:%M %p',  # 10:00 AM
            '%H:%M',     # 10:00
        ]
        
        time_str = time_str.strip().replace('a.m', 'AM').replace('p.m', 'PM')
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt).time()
            except ValueError:
                continue
        
        self.stdout.write(self.style.WARNING(f'Could not parse time: {time_str}'))
        return None
    
    def parse_decimal(self, value_str):
        """Parse decimal values"""
        if not value_str or value_str.strip() == '':
            return None
        
        try:
            # Remove commas and convert to decimal
            clean_value = value_str.strip().replace(',', '')
            return float(clean_value)
        except ValueError:
            self.stdout.write(self.style.WARNING(f'Could not parse decimal: {value_str}'))
            return None
