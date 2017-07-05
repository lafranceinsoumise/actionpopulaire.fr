api-django
==========

1. Installation
    1. [Configure PostgreSQL](#configure-postgresql)
    2. [Install requirements](#install-requirements)
    3. [Create super users](#create-super-user-person)
2. [Usage : public endpoints](#public-endpoints)
    1. [/events](#events)
    1. [/groups](#groups)
    2. [Resources filters](#resources-filters)

Configure PostgreSQL
--------------------

PostgreSQL server needs to be installed and started.

On Ubuntu, this means installing the following packages:

```bash
apt install postgresql-9.6 postgis
```

For production, you need to create a database and a role with owner
rights, and add the `postgis` extension to the database.

```bash
sudo -u postgres psql
# the following commmands should be typed inside psql

CREATE ROLE api;
CREATE DATABASE api WITH owner api;
USE api;
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

# Public endpoints

## `/events`

The list of all published, upcoming events (paginated).

To get the complete list in one request, use `/events/summary`.

## `/groups`

The list of all published groups.

To get the complete list in one request, use `/groups/summary`.

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

* `start_time`: ISO 8601 Datetime, get only events starting after this date
