# PostgreSQL Database Setup

This project uses PostgreSQL as the database.

## Prerequisites

1. **Install PostgreSQL**: Download from https://www.postgresql.org/download/
2. **Install psycopg2**: `pip install psycopg2-binary`
3. **Install python-decouple**: `pip install python-decouple`

## Database Setup

### 1. Create Database

Open PostgreSQL command line (psql) or pgAdmin and run:

```sql
CREATE DATABASE tenders;
CREATE USER tenders_user WITH PASSWORD 'your_secure_password';
ALTER ROLE tenders_user SET client_encoding TO 'utf8';
ALTER ROLE tenders_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tenders_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE tenders TO tenders_user;
```

Or use the default postgres user (simpler for development):
```sql
CREATE DATABASE tenders;
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (same directory as manage.py):

```bash
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

**Important**: Replace `your_postgres_password` with your actual PostgreSQL password.

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Setup Groups and Permissions

```bash
python manage.py setup_groups
```

### 6. Create User Profiles for Existing Users

```bash
python manage.py create_user_profiles
```

## Configuration Details

The database configuration is in `tender_tracking/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tenders',
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

## Security Notes

- ✅ `.env` is in `.gitignore` - your password is NOT committed to git
- ✅ Use `.env.example` as a template for others
- ⚠️ Never commit your actual `.env` file
- ⚠️ Use strong passwords in production
- ⚠️ Consider using environment-specific .env files (.env.dev, .env.prod)

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: "ModuleNotFoundError: No module named 'decouple'"
```bash
pip install python-decouple
```

### Error: "FATAL: password authentication failed"
- Check your password in `.env` file
- Verify PostgreSQL is running
- Check PostgreSQL authentication settings in `pg_hba.conf`

### Error: "database 'tenders' does not exist"
- Create the database using the SQL commands above
- Verify database name matches in settings

### Connection Refused
- Ensure PostgreSQL service is running
- Check if PostgreSQL is listening on the correct port (default: 5432)
- Verify HOST and PORT in `.env` file

## Backup and Restore

### Backup
```bash
pg_dump -U postgres tenders > backup.sql
```

### Restore
```bash
psql -U postgres tenders < backup.sql
```

## Production Recommendations

1. Create a dedicated database user (not postgres)
2. Use strong passwords
3. Enable SSL connections
4. Regular backups
5. Monitor database performance
6. Consider connection pooling (pgBouncer)
7. Set up replication for high availability
