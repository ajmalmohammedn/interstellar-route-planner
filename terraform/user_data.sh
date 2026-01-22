#!/bin/bash
set -euo pipefail

# Ensure script runs as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

exec > >(tee -a /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

echo "=== user_data start: $(date -Is) ==="

apt-get update -y
apt-get install -y git curl ca-certificates

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

UBUNTU_CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $UBUNTU_CODENAME stable" > /etc/apt/sources.list.d/docker.list

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker

docker version
docker compose version

# Deploy the application
rm -rf /opt/app
git clone "${app_repo}" /opt/app
cd /opt/app

cat > .env.docker <<EOF
DEBUG=False
SECRET_KEY=${django_secret_key}
ALLOWED_HOSTS=*

POSTGRES_DB=interstellar
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${db_password}

DB_NAME=interstellar
DB_USER=postgres
DB_PASSWORD=${db_password}
DB_HOST=db
DB_PORT=5432
EOF

mkdir -p nginx
cat > nginx/nginx.conf <<'EOF'
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name _;

    location /static/ {
        alias /app/staticfiles/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

cat > docker-compose.prod.yml <<'EOF'
services:
  db:
    image: postgres:15
    env_file:
      - .env.docker
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d interstellar"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  web:
    build: .
    env_file:
      - .env.docker
    volumes:
      - static_files:/app/staticfiles
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "python manage.py migrate &&
             python manage.py loaddata initial_gates &&
             python manage.py collectstatic --noinput &&
             gunicorn interstellar.wsgi:application --bind 0.0.0.0:8000 --workers 2"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_files:/app/staticfiles:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_files:
EOF

docker compose -f docker-compose.prod.yml up -d --build

echo "=== Deployment complete: $(date -Is) ==="
