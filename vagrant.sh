#!/usr/bin/env bash

set -e

echo "## Make journald persistent..."
# journald uses persistent logging by default *as long as /var/log/journal exists*
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald

echo "## Set locales..."
# avoid some weird bugs with click when locale is not properly set
sudo bash -c 'printf "fr_FR.UTF8 UTF-8\nen_US.UTF-8 UTF-8\n" > /etc/locale.gen'
sudo locale-gen
sudo localectl set-locale LANG=fr_FR.UTF-8

echo "## update packages"
sudo apt-get update -qq > /dev/null

echo "## Install Python..."
if ! (dpkg -s python3.9 && dpkg -s python3.9-dev) &> /dev/null; then
    sudo apt-get -yqq install python3.9 python3.9-dev python3.9-venv python3.9-distutils python3-pip libsystemd-dev > /dev/null
    sudo -H pip3 install poetry
fi

echo "## Install wkhtmltopdf"
if ! dpkg -s wkhtmltox &> /dev/null; then
     sudo apt-get -yqq install wkhtmltopdf > /dev/null
fi

echo "## Install node..."
if ! dpkg -s nodejs &> /dev/null; then
    curl -sL https://deb.nodesource.com/setup_14.x -o /tmp/nodesource_setup.sh &> /dev/null
    sudo bash /tmp/nodesource_setup.sh &> /dev/null
    sudo apt-get -yqq install nodejs > /dev/null
fi

echo "## Install postgresql..."

if ! dpkg -s postgresql-12 &> /dev/null; then
    sudo apt-get -yqq install postgresql-12 postgresql-12-postgis-3 postgresql-12-postgis-3-scripts libpq-dev > /dev/null
fi
sudo -u postgres psql -c "CREATE ROLE api WITH PASSWORD 'password';" || echo "PostgreSQL role already exists"
sudo -u postgres psql -c "CREATE DATABASE api WITH owner api;" || echo "PostgreSQL database already exists"
sudo -u postgres psql -c "ALTER ROLE api WITH superuser;"
sudo -u postgres psql -c "ALTER ROLE api WITH login;"
sudo -u postgres psql -c "CREATE EXTENSION postgis;" || echo "Postgis extension already installed"

echo "## Install redis..."
sudo apt-get install -yqq redis-server > /dev/null

echo "## Install MailHog..."
if [ ! -x MailHog ]; then
    wget --quiet -O MailHog https://github.com/mailhog/MailHog/releases/download/v1.0.0/MailHog_linux_amd64
    chmod +x MailHog
fi

echo "## Install python dependencies..."
(cd /vagrant && PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring" /usr/local/bin/poetry install) &> /dev/null

echo "## Migrate and populate test database..."
(cd /vagrant && /usr/local/bin/poetry run ./manage.py migrate && (/usr/local/bin/poetry run ./manage.py load_fake_data || true)) &> /dev/null

echo "## Create super user (address: admin@agir.local, password: password)"
(cd /vagrant && (SUPERPERSON_PASSWORD="password" /usr/local/bin/poetry run ./manage.py createsuperperson --noinput --email admin@agir.local || true)) &> /dev/null


echo "## Create unit files..."

sudo bash -c "cat > /etc/systemd/system/mailhog.service" <<EOT
[Unit]
Description=MailHog Email Catcher
After=syslog.target network.target

[Service]
User=vagrant
Type=simple
ExecStart=/home/vagrant/MailHog
StandardOutput=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT

sudo bash -c "cat > /etc/systemd/system/celery.service" <<EOT
[Unit]
Description=fi-api celery worker

[Service]
WorkingDirectory=/vagrant
ExecStart=/usr/local/bin/poetry run celery worker --app agir.api --concurrency 2 -Q celery
User=vagrant
Group=vagrant
Restart=on-failure
KillSignal=SIGTERM
Type=simple

[Install]
WantedBy=vagrant.mount
EOT

sudo bash -c "cat > /etc/systemd/system/celery-nuntius.service" <<EOT
[Unit]
Description=fi-api celery worker

[Service]
WorkingDirectory=/vagrant
ExecStart=/usr/local/bin/poetry run celery worker --app nuntius.celery --concurrency 2 -Q nuntius -n nuntius@%%h
User=vagrant
Group=vagrant
Restart=on-failure
KillSignal=SIGTERM
Type=simple

[Install]
WantedBy=vagrant.mount
EOT

sudo bash -c "cat > /etc/systemd/system/django.service" <<EOT
[Unit]
Description=Django Development Server
After=webpack.service

[Service]
User=vagrant
Type=simple
WorkingDirectory=/vagrant
ExecStart=/usr/local/bin/poetry run ./manage.py runserver 0.0.0.0:8000
StandardOutput=journal
Restart=on-failure

[Install]
WantedBy=vagrant.mount
EOT

sudo bash -c "cat > /etc/systemd/system/webpack.service" <<EOT
[Unit]
Description=Webpack Development Server

[Service]
User=vagrant
Type=simple
WorkingDirectory=/vagrant
ExecStart=/usr/bin/npm run watch
StandardOutput=journal
Restart=on-failure
Wants=vagrant.mount

[Install]
WantedBy=vagrant.mount
EOT

sudo systemctl daemon-reload

echo "## Enable all services..."
sudo systemctl enable django
sudo systemctl enable celery
sudo systemctl enable celery-nuntius
sudo systemctl enable mailhog
sudo systemctl enable webpack

echo "## Start all services..."
sudo systemctl start django
sudo systemctl start celery
sudo systemctl start celery-nuntius
sudo systemctl start mailhog
sudo systemctl start webpack

echo "## Installing manage script"
sudo bash -c "cat > /usr/local/bin/manage" <<'EOT'
PYTHON=$(cd /vagrant && poetry env list --full-path)/bin/python

$PYTHON /vagrant/manage.py "$@"
EOT
sudo chmod a+x /usr/local/bin/manage
