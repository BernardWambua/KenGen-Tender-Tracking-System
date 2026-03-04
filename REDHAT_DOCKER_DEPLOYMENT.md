# Red Hat Linux Docker Deployment Guide

This guide shows how to deploy the Tender Tracking app on a Red Hat server using Docker Compose.

## 1) Prerequisites on your local machine

- Git installed
- Docker Desktop installed
- GitHub account

## 2) Push project to GitHub (from Windows)

Run in project root:

```powershell
git status
git add .
git commit -m "Dockerize app and add deployment docs"
```

Create an empty repository on GitHub (no README), then run:

```powershell
git remote add origin https://github.com/<your-username>/<your-repo>.git
git branch -M main
git push -u origin main
```

If `origin` already exists:

```powershell
git remote set-url origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 3) Prepare Red Hat server

SSH to server:

```bash
ssh <user>@<server-ip>
```

Install Docker Engine + Compose plugin:

```bash
sudo dnf -y update
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and back in so docker group applies.

## 4) Open firewall port

For direct app access on port 8000:

```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 5) Clone and configure app on server

```bash
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/<your-username>/<your-repo>.git tendertracking
cd tendertracking
cp .env.docker.example .env
```

Edit `.env`:

```bash
nano .env
```

Set at least:

- `SECRET_KEY` (long random string; avoid `$` unless escaped as `$$`)
- `DEBUG=False`
- `DB_PASSWORD` (strong password)
- `ALLOWED_HOSTS=<server-ip>,<your-domain>,localhost,127.0.0.1`

## 6) Start containers

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f web
```

Create admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

Your app should now be reachable at:

`http://<server-ip>:8000`

## 7) SELinux note (Red Hat specific)

If containers fail to read/write mounted paths due to permission denial, relabel mounts in compose with `:Z`.

Example:

```yaml
volumes:
  - static_volume:/app/staticfiles:Z
  - media_volume:/app/media:Z
```

For named volumes this is usually not needed, but keep this in mind if you switch to host-path mounts.

## 8) Updating app after new GitHub push

```bash
cd ~/apps/tendertracking
git pull
docker compose up --build -d
docker compose logs -f web
```

## 9) Useful operations

```bash
docker compose logs -f web
docker compose logs -f db
docker compose restart web
docker compose down
docker compose down -v
```

`down -v` deletes PostgreSQL data volume.
