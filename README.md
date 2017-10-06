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
3. [Usage: frontend pages](#frontend-pages)

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
* `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET` are the id and secret of
  the client that should be used to authenticate to the OAUTH provider.
* `OAUTH_AUTHORIZATION_URL` and `OAUTH_TOKEN_URL` are the URIs for the
  oauth authorization endpoint to which the end user should first be
  redirected, and of the token exchange endpoint, at which the
  authorization code can be exchanged for the access token.
* `OAUTH_REDIRECT_DOMAIN` is the base domain that is to be used in the
  uri redirection from the OAUTH provider back to the front pages server
* `OAUTH_LOGOFF_URL` is the URI to which the end user should be sent to
  disconnect her.

## Pages

1. An event management section, that a user can visit to see the events
   she organised, and those she RSVPed to. Events she organised may be
   modified through this section
2. A support group management section that allows the user to see the
   list of groups she is part of, and to modify those of which she is a
   group manager.
