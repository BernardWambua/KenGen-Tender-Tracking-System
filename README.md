# Tender Tracking Application

A full-stack Django application for managing and tracking procurement tenders.

## Features

- **Comprehensive Tender Management**: Track tenders with complete lifecycle information
- **Organizational Structure**: Manage regions, departments, divisions, and sections
- **Employee Management**: Track employees with their organizational assignments
- **Committee Management**: One-to-many relationships for tender opening and evaluation committees
- **Lookup Fields**: Procurement types, e-Contract Step, e-Contract Status
- **Admin Interface**: Full-featured Django admin for data management

## Models

### Lookup Models
- **Region**: Geographic regions
- **Department**: Organizational departments
- **Division**: Divisions within departments
- **Section**: Sections within divisions
- **ProcurementType**: Types of procurement methods
- **LOAStatus**: Letter of Award statuses
- **ContractStatus**: e-Contract Status types

### Core Models
- **Employee**: Employee information with organizational structure
- **Tender**: Main tender tracking with all procurement details
- **TenderOpeningCommittee**: Committee members for tender opening
- **TenderEvaluationCommittee**: Committee members for tender evaluation

## Installation

1. **Clone the repository or navigate to the project folder**
   ```bash
   cd c:\Users\kgn71188\Documents\projects\TenderTrackingApp
   ```

2. **Create a virtual environment (if not already done)**
   ```bash
   python -m venv env
   env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the admin interface**
   Open your browser and navigate to: `http://127.0.0.1:8000/admin/`

## Data Structure from CSV

The application is designed to manage data with the following fields:

- No, Region, Department, Section, User
- Shopping Cart, Requisition Number
- Tender Creator, Procurement Type
- Tender ID, eGP Tender Reference, KenGen Tender Reference
- Tender Description
- Tender Advert Date, Tender Closing Date, Tender Closing Time
- Tender Opening Committee, Tender Evaluation Committee
- Tender Evaluation Duration, Tender Validity Expiry Date
- Contract Creator
- LOA (Letter of Award) Status, e-Contract Status
- e-Purchase Order No, SAP Purchase Order No
- Estimated Value

## Usage

### Adding Master Data

1. **Create Regions**: Add all geographic regions
2. **Create Departments**: Add organizational departments
3. **Create Divisions**: Add divisions under departments
4. **Create Sections**: Add sections under divisions
5. **Create Lookup Data**: Add procurement types, e-Contract Stepes, e-Contract Statuses

### Managing Employees

1. First create a User account in Django admin
2. Create an Employee record linked to that user
3. Assign department, division, and section to the employee

### Managing Tenders

1. Create a new tender with all required information
2. Assign tender creator and contract creator (employees)
3. Add committee members using the inline forms:
   - Tender Opening Committee members
   - Tender Evaluation Committee members
4. Track tender progress through LOA and e-Contract Statuses

## Admin Features

- **Search**: Search tenders by ID, description, references
- **Filters**: Filter by procurement type, region, department, status, dates
- **Date Hierarchy**: Browse tenders by advert date
- **Autocomplete**: Employee selection with autocomplete functionality
- **Inline Editing**: Add committee members directly in the tender form
- **Field Organization**: Grouped fields in logical sections

## Next Steps

- Import existing data from CSV file
- Create custom views and templates for end-users
- Add reporting and analytics
- Implement email notifications
- Add document attachments
- Create dashboard with charts and statistics

## Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite (development) - can be changed to PostgreSQL/MySQL for production
- **Admin Interface**: Django Admin

## Project Structure

```
TenderTrackingApp/
├── tenders/              # Main Django app
│   ├── models.py        # Database models
│   ├── admin.py         # Admin configuration
│   ├── views.py         # Views (to be developed)
│   └── migrations/      # Database migrations
├── tender_tracking/     # Project settings
│   ├── settings.py      # Django settings
│   ├── urls.py          # URL configuration
│   └── wsgi.py          # WSGI configuration
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── Procurement Tracking.csv  # Source data
```

## License

Proprietary - KenGen Tender Tracking Application

## Run with Docker (Recommended)

### 1) Prepare environment file

Copy the example file and edit values:

```powershell
Copy-Item .env.docker.example .env
```

Update at least:
- `SECRET_KEY` (set a long random value)
- `DB_PASSWORD` (set a strong password)
- `ALLOWED_HOSTS` (add your server IP/domain in production)

### 2) Build and start containers

```powershell
docker compose up --build -d
```

The app runs at:
- `http://localhost:8000`

### 3) Create admin user

```powershell
docker compose exec web python manage.py createsuperuser
```

### 4) View logs

```powershell
docker compose logs -f web
docker compose logs -f db
```

### 5) Stop the stack

```powershell
docker compose down
```

To stop and remove volumes (this deletes database data):

```powershell
docker compose down -v
```

## Hosting on a VPS with Docker

1. Install Docker + Docker Compose on the VPS.
2. Copy project files to the server.
3. Create `.env` from `.env.docker.example` and set production values.
4. Run:

```bash
docker compose up --build -d
```

5. Open firewall for port `8000` or place Nginx in front and proxy to `web:8000`.

For Red Hat specific setup, see [REDHAT_DOCKER_DEPLOYMENT.md](REDHAT_DOCKER_DEPLOYMENT.md).
