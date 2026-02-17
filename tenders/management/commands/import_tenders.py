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
    LOAStatus, ContractStatus, Employee, Tender, Requisition,
    Currency, Country, Contract
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
                loa_status = self.get_or_create_loa_status(row.get('LOA (Letter of Award status)'))
                contract_status = self.get_or_create_contract_status(row.get('e-Contract Status'))
                
                # Get or create employees
                tender_creator = self.get_or_create_employee(row.get('Tender Creator'), department)
                contract_creator = self.get_or_create_employee(row.get('Contract Creator'), department)
                user = self.get_or_create_employee(row.get('User'), department)
                
                # Parse dates
                tender_creation_date = self.parse_date(row.get('Tender Creation Date'))
                proposed_advert_date = self.parse_date(row.get('Proposed Advert Date'))
                tender_advert_date = self.parse_date(row.get('Tender Advert Date'))
                tender_closing_date = self.parse_date(row.get('Tender Closing Date'))
                tender_validity_expiry_date = self.parse_date(row.get('Tender Validity Expiry Date'))
                
                # Parse time
                tender_closing_time = self.parse_time(row.get('Tender Closing Time'))
                
                # Parse estimated value
                estimated_value = self.parse_decimal(row.get('Estimated'))
                
                # Extract tender ID from the "Tender ID : 38" format
                tender_id_raw = row.get('Tender ID', '')
                tender_id_clean = tender_id_raw.split(':')[-1].strip() if ':' in tender_id_raw else tender_id_raw
                tender_id = self.parse_int(tender_id_clean) or 0

                tender_reference_number = row.get('Tender Reference Number') or row.get('eGP Tender Reference') or row.get('KenGen Tender Reference') or ''
                eligibility = (row.get('Eligibility') or 'OPEN').strip().upper()
                agpo_category = (row.get('AGPO') or '').strip().upper() or None
                tender_approval_status = (row.get('Tender Approval status') or '').strip().upper().replace(' ', '_') or None
                tender_step = (row.get('Tender Step') or '').strip().upper().replace(' ', '_') or None
                tender_validity_days = self.parse_int(row.get('Tender Validity(days)'))
                procurement_method = self.map_procurement_method(row.get('Procurement Method') or row.get('Procurement Type'))
                
                requisition_number = row.get('Requisition Number') or None
                if not requisition_number:
                    requisition_number = f"REQ-{tender_id}"

                shopping_cart_no = self.parse_int(row.get('Shopping Cart'))
                shopping_cart_amount = self.parse_decimal(row.get('Shopping Cart Amount')) or 0
                shopping_cart_status_raw = (row.get('Shopping cart status') or '').strip().upper()
                shopping_cart_status = shopping_cart_status_raw.replace(' ', '_') or 'PENDING'
                requisition_description = row.get('Requisition Description') or row.get('Tender Description') or ''
                date_assigned = self.parse_date(row.get('Date Assigned')) or tender_advert_date or datetime.today().date()

                procurement_type_raw = (row.get('Procurement Type') or '').strip().upper()
                procurement_type = 'QUOTATION' if 'QUOTATION' in procurement_type_raw else 'TENDER'

                requisition, _ = Requisition.objects.update_or_create(
                    e_requisition_no=requisition_number,
                    defaults={
                        'requisition_description': requisition_description,
                        'shopping_cart_no': shopping_cart_no or 0,
                        'shopping_cart_amount': shopping_cart_amount,
                        'shopping_cart_status': shopping_cart_status,
                        'region': region,
                        'department': department,
                        'division': division,
                        'section': section,
                        'assigned_user': user,
                        'procurement_type': procurement_type,
                        'tender_creator': tender_creator,
                        'date_assigned': date_assigned,
                    }
                )

                # Create or update tender
                tender, created = Tender.objects.update_or_create(
                    tender_id=tender_id,
                    defaults={
                        'requisition': requisition,
                        'tender_reference_number': tender_reference_number,
                        'tender_creation_date': tender_creation_date or tender_advert_date or datetime.today().date(),
                        'tender_description': row.get('Tender Description') or '',
                        'eligibility': 'AGPO' if eligibility == 'AGPO' else 'OPEN',
                        'agpo_category': agpo_category if eligibility == 'AGPO' else None,
                        'procurement_method': procurement_method,
                        'tender_creator': tender_creator,
                        'created_by': tender_creator,
                        'proposed_advert_date': proposed_advert_date,
                        'tender_advert_date': tender_advert_date,
                        'tender_closing_date': tender_closing_date,
                        'tender_closing_time': tender_closing_time,
                        'tender_validity_days': tender_validity_days,
                        'tender_validity_expiry_date': tender_validity_expiry_date,
                        'tender_evaluation_duration_days': self.parse_int(row.get('Tender Evaluation Duration(30/21 Days)')),
                        'tender_approval_status': tender_approval_status,
                        'tender_step': tender_step,
                        'estimated_value': estimated_value,
                    }
                )

                contract_number = self.parse_int(row.get('Contract number'))
                contract_title = row.get('Contract title') or None
                contract_duration_measure = self.map_duration_measure(row.get('Contract duration measure'))
                contract_duration = self.parse_int(row.get('Contract duration'))
                commencement_date = self.parse_date(row.get('Commencement date'))
                contract_value = self.parse_decimal(row.get('Contract Value'))
                contract_currency = self.get_or_create_currency(row.get('Contract Currency'))
                contractor_supplier = row.get('Contractor/Supplier') or None
                country_of_origin = self.get_or_create_country(row.get('Country of Origin'))
                tender_security_amount = self.parse_decimal(row.get('Tender Security Amount'))
                tender_security_validity_days = self.parse_int(row.get('Tender Security validity (days)'))
                contract_step = self.map_contract_step(row.get('Contract Step'))
                responsibility = self.map_responsibility(row.get('Responsibility'))
                contract_delivery_period = self.parse_int(row.get('Contract Delivery Period'))
                performance_security_amount = self.parse_decimal(row.get('Performance Security Amount'))
                performance_security_duration_days = self.parse_int(row.get('Performance Security Duration (Days)'))
                e_purchase_order_no = row.get('eGP Purchase order No') or None
                sap_purchase_order_no = row.get('SAP Purchase Order No') or None

                if contract_number or contract_title or contract_value or contractor_supplier:
                    Contract.objects.update_or_create(
                        tender=tender,
                        defaults={
                            'contract_number': contract_number,
                            'contract_title': contract_title,
                            'contract_creator': contract_creator,
                            'contract_duration_measure': contract_duration_measure,
                            'contract_duration': contract_duration,
                            'commencement_date': commencement_date,
                            'contract_value': contract_value,
                            'contract_currency': contract_currency,
                            'contractor_supplier': contractor_supplier,
                            'country_of_origin': country_of_origin,
                            'tender_security_amount': tender_security_amount,
                            'tender_security_validity_days': tender_security_validity_days,
                            'contract_step': contract_step,
                            'contract_status': contract_status,
                            'responsibility': responsibility,
                            'contract_delivery_period': contract_delivery_period,
                            'performance_security_amount': performance_security_amount,
                            'performance_security_duration_days': performance_security_duration_days,
                            'e_purchase_order_no': e_purchase_order_no,
                            'sap_purchase_order_no': sap_purchase_order_no,
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

    def map_procurement_method(self, raw_value):
        if not raw_value:
            return None
        value = str(raw_value).strip().upper()
        if 'QUOTATION' in value:
            return 'REQUEST_FOR_QUOTATION'
        if 'DIRECT' in value:
            return 'DIRECT_PROCUREMENT'
        if 'RESTRICTED' in value:
            return 'RESTRICTED_TENDER'
        if 'OPEN' in value:
            return 'OPEN_TENDER'
        if 'PROPOSAL' in value:
            return 'REQUEST_FOR_PROPOSAL'
        if 'EXPRESSION' in value:
            return 'EXPRESSION_OF_INTEREST'
        if 'PREQUAL' in value:
            return 'PREQUALIFICATION'
        if 'FRAMEWORK' in value:
            return 'FRAMEWORK'
        return None

    def parse_int(self, value_str):
        """Parse integer values"""
        if not value_str or value_str.strip() == '':
            return None

        try:
            clean_value = value_str.strip().replace(',', '')
            return int(float(clean_value))
        except ValueError:
            self.stdout.write(self.style.WARNING(f'Could not parse int: {value_str}'))
            return None

    def map_duration_measure(self, raw_value):
        if not raw_value:
            return None
        value = str(raw_value).strip().upper()
        if 'DAY' in value:
            return 'DAYS'
        if 'MONTH' in value:
            return 'MONTHS'
        if 'YEAR' in value:
            return 'YEARS'
        return None

    def map_contract_step(self, raw_value):
        if not raw_value:
            return None
        value = str(raw_value).strip().upper().replace(' ', '_')
        mapping = {
            'DRAFT': 'DRAFT',
            'ACTIVE': 'ACTIVE',
            'AWARDED': 'AWARDED',
            'SIGNED': 'SIGNED',
            'CLOSED': 'CLOSED',
        }
        return mapping.get(value)

    def map_responsibility(self, raw_value):
        if not raw_value:
            return None
        value = str(raw_value).strip().upper().replace(' ', '_')
        mapping = {
            'PROCUREMENT': 'PROCUREMENT',
            'FINANCE': 'FINANCE',
            'LEGAL': 'LEGAL',
            'USER_DEPT': 'USER_DEPT',
            'USER_DEPARTMENT': 'USER_DEPT',
            'ICT': 'ICT',
            'OTHER': 'OTHER',
        }
        return mapping.get(value, 'OTHER')

    def get_or_create_currency(self, raw_value):
        if not raw_value:
            return None
        code = str(raw_value).strip().upper()
        currency, _ = Currency.objects.get_or_create(code=code, defaults={'name': code})
        return currency

    def get_or_create_country(self, raw_value):
        if not raw_value:
            return None
        name = str(raw_value).strip()
        country, _ = Country.objects.get_or_create(name=name)
        return country
