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
sudo systemctl start mailhog

echo "Install django dev server..."
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get -yqq update
sudo apt-get -yqq install python3.6 python3-pip libsystemd-dev
sudo -H pip3 install pipenv
cd /vagrant
pipenv install
pivenv run src/manage.py migrate
sudo bash -c "cat > /etc/systemd/system/django.service" <<EOT
[Unit]
Description=Django Development Server
After=syslog.target network.target

[Service]
User=vagrant
Type=simple
WorkingDirectory=/vagrant
ExecStart=/usr/local/bin/pipenv run src/manage.py runserver 0.0.0.0:8000
StandardOutput=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT
sudo systemctl daemon-reload
sudo systemctl enable django
sudo systemctl start django

echo "Install node..."
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash - >> /dev/null 2>&1
sudo apt-get -yqq install nodejs
sudo bash -c "cat > /etc/systemd/system/webpack.service" <<EOT
[Unit]
Description=Webpack Development Server
After=syslog.target network.target

[Service]
User=vagrant
Type=simple
WorkingDirectory=/vagrant
ExecStart=/usr/bin/npm run watch
StandardOutput=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT
sudo systemctl daemon-reload
sudo systemctl enable webpack
sudo systemctl start webpack

echo "Install oauth..."
cd /opt
sudo apt-get -yqq install git
sudo git clone -a https://github.com/lafranceinsoumise/oauth.git || (cd oauth; sudo git pull)
cd /opt/oauth
sudo npm install
sudo bash -c "cat > /etc/systemd/system/oauth.service" <<EOT
[Unit]
Description=Oauth server
After=syslog.target network.target

[Service]
User=vagrant
Type=simple
WorkingDirectory=/opt/oauth
EnvironmentFile=/opt/oauth/envfile.sample
ExecStart=/usr/bin/npm run start
StandardOutput=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOT
sudo systemctl daemon-reload
sudo systemctl enable oauth
sudo systemctl start oauth
