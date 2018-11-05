api-django
==========

[![Build Status](https://travis-ci.org/lafranceinsoumise/api-django.svg?branch=master)](https://travis-ci.org/lafranceinsoumise/api-django)

1. [Vagrant installation](#vagrant)
1. Manual installation
    1. [Configure PostgreSQL](#configure-postgresql)
    2. [Install requirements](#install-requirements)
    3. [Create super users](#create-super-user-person)
    4. [Development data](#development-data)
2. [Usage : public endpoints](#public-endpoints)
    1. [/events](#events)
    1. [/groups](#groups)
    2. [Resources filters](#resources-filters)
3. [Usage: frontend pages](#frontend-pages)

# Vagrant installation

You can use Vagrant to create a virtual machine with all necessary
dependencies on it. You first need to have Vagrant and VirtualBox
installed on your computer.

Then just do this in the project directory.
```bash
vagrant up
```

This will install PostgreSQL, Redis and Node onto the virtual
machine, and launch four other services :

* `django` which is the development server of this project
* `MailHog`, a catch-all SMTP server used for development
* `webpack`, the webpack dev server with hot reloading

All port are forwarded to localhost, so once your vagrant box is up,
you can access Django from [http://localhost:8000](http://localhost:8000)
and Mailhog from [http://localhost:8025](http://localhost:8025).
Webpack dev server listen on port 3000 but you don't need
to access it directly.

Once your box is up, you need to run a few commands in the virtual
machine to get things running :
```bash
vagrant ssh
cd /vagrant
pipenv run src/manage.py migrate # you will need to run this each time you migrate
pipenv run src/manage.py load_fake_data # to create base users
```

The `/vagrant` directory in the box is syncrhonized with your
project directory on the host.

# Manual installation

Configure PostgreSQL
--------------------

PostgreSQL server needs to be installed and started.

On Ubuntu, this means installing the following packages:

```bash
apt install postgresql-9.6 postgis
```

On Mac OS, this can be installed with brew with the following commands :

```bash
brew install postgresql postgis
```

For development, you need to create a database and a role with owner
rights, and add the `postgis` extension to the database.

```bash
sudo -u postgres psql
# the following commmands should be typed inside psql

CREATE ROLE api WITH PASSWORD 'password';
CREATE DATABASE api WITH owner api;
\connect api
CREATE EXTENSION postgis;
```

For testing, the `api` role need to be a superuser to be able to create
a new test database with the `postgis` extension.

```bash
sudo -u postgres psql
# the following commmands should be typed inside psql

ALTER ROLE api WITH superuser;
```

Install requirements
--------------------

Python 3.6 is recommended.

To install Python dependencies, run :

```bash
pip install -r requirements.txt
```

To run the tests :

```bash
coverage run --source='.' manage.py test
```

in the `src` directory.

Create super user (person)
--------------------------

Run:

```bash
./manage.py createsuperperson
```

Create super user (client)
--------------------------

Open a django console with:

```bash
./manage.py shell
```

Then execute the following commands:

```python
from clients.models import Client
c = Client.objects.create(label='client_login', name='Nom du client')
c.role.set_password('client_password')
c.role.is_superuser = True
c.role.save()
```

Development data
----------------

You can load data in the database. All role passwords are 'incredible password'.s

```bash
./manage.py loaddata fixtures.json
``` 

To update and commit it in a git diff readable way, use the following command :

```bash
./manage.py dumpdata authentication clients events groups front people polls
```

# Public endpoints

## `/events`

The list of all published, upcoming events (paginated).

To get the complete list in one request, use `/events/summary`.

## `/calendars`

The list of all calendars. Events are part of one calendar.

## `/groups`

The list of all published groups.

To get the complete list in one request, use `/groups/summary`.

# Authenticated endpoints

## `/people/me`

Profile of the authenticated user.

# Resources filters

Each resource expose a series of filter that you can use to fetch a subset of the resource collection.

Filters can be passed as query parameters, eg `https://api.lafranceinsoumise.fr/legacy/groups/?contact_email=example@example.com`

## `groups` and `events`

* `contact_email`
* `nb_path` : path on legacy NationBuilder website
* `close_to` : find events close to a given location. Value must be a JSON Object with
    * `max_distance` : distance in meters
    * `coordinates` : array of coordinates [Longitude, Latitude]
* `order_by_distance_to` : list all events, but by ordering them by distance to JSON array of [Longitude, Latitude]. By getting the first page, you get the 25 closest events.

## `events`

* `after`: ISO 8601 Datetime, get only events *finishing* after this date
* `before`: ISO 8601 Datetime, get only events *starting* before this date
* `calendar`: String, get only events belonging to a specific calendar

# Frontend pages

An optional HTML frontend is available for the API.

## Configuration

The following additional environment variables are used to configure the
HTML frontend.

* `ENABLE_FRONT` when set to `yes` enable the front pages routes. Leave
  unset, empty or set to `no` to disable it.

## Pages

1. An event management section, that a user can visit to see the events
   she organised, and those she RSVPed to. Events she organised may be
   modified through this section
2. A support group management section that allows the user to see the
   list of groups she is part of, and to modify those of which she is a
   group manager.
