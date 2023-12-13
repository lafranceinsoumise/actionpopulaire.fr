#!/usr/bin/env bash

set -e

echo "## Setting environment variables"
declare -A env
##########################################################################
# Environment variables key-value pairs
# These variables will be available in the provision shell script and in
# all vagrant shell sessions
env[PYTHON_KEYRING_BACKEND]="\"keyring.backends.null.Keyring\""
env[POETRY_HOME]="$HOME/poetry"
env[POETRY_VERSION]="1.2.2"
##########################################################################
source ~/.profile
for key in ${!env[@]}; do
  value=${env[${key}]}
  if [ -z "${!key}" ]; then
    echo "export ${key}=${value}" >> ~/.profile
  fi
done
source ~/.profile

echo "## Make journald persistent..."
# journald uses persistent logging by default *as long as /var/log/journal exists*
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald

echo "## Set locales..."
# avoid some weird bugs with click when locale is not properly set
sudo bash -c 'printf "fr_FR.UTF8 UTF-8\nen_US.UTF-8 UTF-8\n" > /etc/locale.gen'
sudo locale-gen
sudo localectl set-locale LANG=fr_FR.UTF-8

echo "## Update packages"
sudo apt-get update -qq &> /dev/null

echo "## Install postgresql..."
if ! dpkg -s postgresql-12 &> /dev/null; then
    sudo apt-get -yqq install postgresql-12 postgresql-12-postgis-3 postgresql-12-postgis-3-scripts libpq-dev &> /dev/null
fi
sudo -u postgres psql -c "CREATE ROLE api WITH PASSWORD 'password';" || echo "PostgreSQL role already exists"
sudo -u postgres psql -c "CREATE DATABASE api WITH owner api;" || echo "PostgreSQL database already exists"
sudo -u postgres psql -c "ALTER ROLE api WITH superuser;"
sudo -u postgres psql -c "ALTER ROLE api WITH login;"
sudo -u postgres psql -c "CREATE EXTENSION postgis;" || echo "Postgis extension already installed"

echo "## Install Python..."
if ! (dpkg -s python3.9 && dpkg -s python3.9-dev) &> /dev/null; then
    sudo apt-get -yqq install python3.9 python3.9-dev python3.9-venv python3.9-distutils python3-pip libsystemd-dev &> /dev/null
    # Install Poetry
    sudo mkdir -p $POETRY_HOME
    sudo python3.9 -m venv $POETRY_HOME --clear --upgrade-deps &> /dev/null
    sudo $POETRY_HOME/bin/pip3 install poetry==$POETRY_VERSION &> /dev/null
    sudo ln -s $POETRY_HOME/bin/poetry /usr/local/bin/poetry
fi

echo "## Install python dependencies..."
(cd /vagrant && $POETRY_HOME/bin/poetry install) &> /dev/null

echo "## Install wkhtmltopdf"
if ! dpkg -s wkhtmltox &> /dev/null; then
     sudo apt-get -yqq install wkhtmltopdf &> /dev/null
fi

echo "## Install librsvg2-bin"
if ! dpkg -s librsvg2-bin &> /dev/null; then
     sudo apt-get -yqq install librsvg2-bin &> /dev/null
fi

echo "## Install node..."
if ! dpkg -s nodejs &> /dev/null; then
    curl -sL https://deb.nodesource.com/setup_18.x -o /tmp/nodesource_setup.sh
    sudo bash /tmp/nodesource_setup.sh &> /dev/null
    sudo apt-get -yqq install nodejs &> /dev/null
fi

echo "## Install redis..."
sudo apt-get install -yqq redis-server &> /dev/null

echo "## Install MailHog..."
if [ ! -x MailHog ]; then
    wget --quiet -O MailHog https://github.com/mailhog/MailHog/releases/download/v1.0.0/MailHog_linux_amd64
    chmod +x MailHog
fi

echo "## Migrate and populate test database..."
(cd /vagrant && $POETRY_HOME/bin/poetry run ./manage.py migrate && ($POETRY_HOME/bin/poetry run ./manage.py load_fake_data || true)) &> /dev/null

echo "## Create super user (address: admin@agir.local, password: password)"
(cd /vagrant && (SUPERPERSON_PASSWORD="password" $POETRY_HOME/bin/poetry run ./manage.py createsuperperson --noinput --email admin@agir.local || true)) &> /dev/null

echo "## Install fonts"
sudo /vagrant/scripts/install_fonts.sh


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
ExecStart=$POETRY_HOME/bin/poetry run celery --app agir.api worker --concurrency 2 -Q celery
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
ExecStart=$POETRY_HOME/bin/poetry run celery --app nuntius.celery worker --concurrency 2 -Q nuntius -n nuntius@%%h
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
ExecStart=$POETRY_HOME/bin/poetry run ./manage.py runserver 0.0.0.0:8000
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
PYTHON=$(cd /vagrant && $POETRY_HOME/bin/poetry env info --path)/bin/python

$PYTHON /vagrant/manage.py "$@"
EOT
sudo chmod a+x /usr/local/bin/manage
