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

echo "## Install Python..."
sudo add-apt-repository ppa:deadsnakes/ppa > /dev/null
sudo apt-get -yqq update > /dev/null
sudo apt-get -yqq install python3.6 python3.6-dev python3-pip libsystemd-dev > /dev/null
sudo -H pip3 install pipenv

echo "## Install wkhtmltopdf"
RELEASE=$(. /etc/lsb_release ; echo $DISTRIB_CODENAME)
curl https://builds.wkhtmltopdf.org/0.12.1.3/wkhtmltox_0.12.1.3-1~${RELEASE}_amd64.deb --output wkhtmltox.deb -q
sudo apt-get -yqq install libpng16-16 xfonts-75dpi xfonts-base > /dev/null
sudo dpkg -i wkhtmltox.deb

echo "## Install node..."
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash - > /dev/null
sudo apt-get -yqq install nodejs > /dev/null

echo "## Install postgresql..."
sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main"
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get -qq update > /dev/null
sudo apt-get -yqq upgrade > /dev/null
sudo apt-get -yqq install postgresql-9.6 postgis postgresql-server-dev-9.6 > /dev/null
sudo -u postgres psql -c "CREATE ROLE api WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE api WITH owner api;"
sudo -u postgres psql -c "ALTER ROLE api WITH superuser;"
sudo -u postgres psql -c "ALTER ROLE api WITH login;"
sudo -u postgres psql -c "\connect api"
sudo -u postgres psql -c "CREATE EXTENSION postgis;"

echo "## Install redis..."
sudo apt-get install -yqq redis-server > /dev/null

echo "## Install MailHog..."
wget --quiet -O MailHog https://github.com/mailhog/MailHog/releases/download/v1.0.0/MailHog_linux_amd64
chmod +x MailHog

echo "## Install python dependencies..."
(cd /vagrant && /usr/local/bin/pipenv sync) > /dev/null

echo "## Install npm dependencies..."
(cd /vagrant && /usr/local/bin/pipenv run npm install) > /dev/null

echo "## Migrate and populate test database..."
(cd /vagrant && /usr/local/bin/pipenv run ./manage.py migrate && /usr/local/bin/pipenv run ./manage.py load_fake_data) > /dev/null

echo "## Create super user (address: admin@agir.local, password: password)"
(cd /vagrant && SUPERPERSON_PASSWORD="password" /usr/local/bin/pipenv run ./manage.py createsuperperson --noinput --email admin@agir.local) > /dev/null


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
ExecStart=/usr/local/bin/pipenv run celery worker --app agir.api --concurrency 2 --logfile=/dev/null
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
ExecStart=/usr/local/bin/pipenv run ./manage.py runserver 0.0.0.0:8000
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
sudo systemctl enable mailhog
sudo systemctl enable webpack

echo "## Start all services..."
sudo systemctl start django
sudo systemctl start celery
sudo systemctl start mailhog
sudo systemctl start webpack

echo "## Installing manage script"
sudo bash -c "cat > /usr/local/bin/manage" <<'EOT'
PYTHON=$(cd /vagrant && pipenv --venv)/bin/python

$PYTHON /vagrant/manage.py "$@"
EOT
sudo chmod a+x /usr/local/bin/manage
