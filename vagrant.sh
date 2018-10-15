#!/usr/bin/env bash

sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald

echo "Install postgresql..."
sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main"
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get -qq update
sudo apt-get -yqq upgrade
sudo apt-get -yqq install postgresql-9.6 postgis
sudo -u postgres psql -c "CREATE ROLE api WITH PASSWORD 'password';"
sudo -u postgres psql -c "CREATE DATABASE api WITH owner api;"
sudo -u postgres psql -c "ALTER ROLE api WITH superuser;"
sudo -u postgres psql -c "ALTER ROLE api WITH login;"
sudo -u postgres psql -c "\connect api"
sudo -u postgres psql -c "CREATE EXTENSION postgis;"

echo "Install redis..."
sudo apt-get install -yqq redis-server

echo "Install MailHog..."
wget --quiet -O MailHog https://github.com/mailhog/MailHog/releases/download/v1.0.0/MailHog_linux_amd64
chmod +x MailHog
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
sudo systemctl daemon-reload
sudo systemctl enable mailhog

echo "Install Celery..."
sudo -H pip install celery
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
WantedBy=multi-user.target vagrant.mount
EOT
sudo systemctl daemon-reload
sudo systemctl enable celery

echo "Install django dev server..."
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get -yqq update
sudo apt-get -yqq install python3.6 python3.6-dev python3-pip libsystemd-dev
sudo -H pip3 install pipenv
cd /vagrant
/usr/local/bin/pipenv install
/usr/local/bin/pipenv run ./manage.py migrate
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
sudo systemctl daemon-reload
sudo systemctl enable django

echo "Install node..."
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash - >> /dev/null 2>&1
sudo apt-get -yqq install nodejs
cd /vagrant
/usr/local/bin/pipenv run npm install
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
sudo systemctl enable webpack


sudo systemctl start django
sudo systemctl start celery
sudo systemctl start mailhog
sudo systemctl start webpack
