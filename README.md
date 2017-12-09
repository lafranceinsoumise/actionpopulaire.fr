api-django
==========

1 Requirements
==============

You can install this project using **Docker containers** (method 1) or **manually** (method 2).

1.1 Common requirements
-----------------------

 * Working on UNIX based environment (Linux/MacOS). Windows users may work on a virtual environment (e.g: VirtualBox, VMWare, Vagrant with VirtualBox...)
 * [Git](https://git-scm.com/downloads)

1.2 Method 1: Docker
--------------------

 * [Docker](https://docs.docker.com/engine/installation/#supported-platforms)
 * [Docker Compose](https://docs.docker.com/compose/install/)


1.3 Method 2: manual installation
---------------------------------

 * [VirtualEnv](https://virtualenv.pypa.io/en/stable/installation/) (or Python 3.6 and [pip](https://pip.pypa.io/en/stable/installing/))
 * [PostgreSQL](https://www.postgresql.org/docs/9.6/static/tutorial-install.html) >= 9.6
 * [Postgis extension](http://postgis.net/install/http://postgis.net/install/)
 * On MacOS only: [Homebrew](https://brew.sh/)
 * [nvm](https://github.com/creationix/nvm#installation) or (or Node 8.9.3)

2 Installation
==============

2.1 Common requirements installation
------------------------------------

### Git

On Debian (Ubuntu...) based environment, run: `sudo apt-get install git`
On Fedora based environments, run: `sudo yum install git`
On Mac OSX, run: `brew install git`


2.2 Method 1: Docker
--------------------

### Docker & Docker Compose

You need to install Docker CE (community edition) and Docker Compose:

 * For Docker CE, [follow these steps according to your environment](https://docs.docker.com/engine/installation/#supported-platforms)
 * For Docker Compose, [follow these steps](https://docs.docker.com/compose/install/)


2.3 Method 2: Manual Installation
---------------------------------

### Install Python3.6

On Debian (Ubuntu...) based environment, run: `sudo apt-get install python3.6`
On Fedora based environments, run: `sudo yum install python3.6`
On Mac OSX, run: `brew install python3`

NB: if you use an old Ubuntu like distro, you may need to run these commands before:
```
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get update
```

### Install VirtualEnv

```
sudo pip install virtualenv
```

### Use Python3.6 with VirtualEnv

```
virtualenv venv -p $(which python3.6)
source venv/bin/activate
```

### Install python dependencies

```
pip install -r requirements.txt
```

### Install PostgreSQL

On Debian (Ubuntu...) based environment, run: `sudo apt-get install postgresql-9.6`
On Fedora based environments, run: `sudo yum install postgresql-9.6`
On Mac OSX, run: `brew install postgresql@9.6`

### Install Postgis

On Debian (Ubuntu...) based environment, run: `sudo apt-get install postgresql-9.6-postgis`
On Fedora based environments, run: `sudo yum install postgresql-9.6-postgis`
On Mac OSX, run: `brew install postgis`

### Create and configure database

```bash
sudo -u postgres psql
# the following commmands should be typed inside psql

CREATE ROLE fi_api WITH PASSWORD 'password';
CREATE DATABASE fi_api WITH owner fi_api;
ALTER ROLE fi_api WITH superuser;
\connect fi_api
CREATE EXTENSION postgis;
```

### Run migrations and load fixtures

```
./src/manage.py migrate
./src/manage.py loaddata src/fixtures.json
```

### (Optional) Install nvm

Follow these steps to install `nvm`: https://github.com/creationix/nvm#installation

Then run:
```
nvm install 8.9.3
nvm use 8.9.3
```

### (Optional) Install node dependencies

```
npm install
```

### Start server

```
./src/manage.py runserver 0.0.0.0:8000
```

3 Usage
=======

You can access to API here: http://localhost:8000/admin/

Here are some credentials:
 * `admin@example.com` / `incredible password`
 * `user1@example.com` / `incredible password`
 * `user2@example.com` / `incredible password`


Tests
-----

To run the tests :

```bash
coverage run --source='.' manage.py test
```


Create super user (person)
--------------------------

Run:

```bash
./src/manage.py createsuperperson
```

Create super user (client)
--------------------------

Open a django console with:

```bash
./src/manage.py shell
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

You can reload data in the database:

```bash
./src/manage.py loaddata src/fixtures.json
``` 

To update and commit it in a git diff readable way, use the following command :

```bash
./src/manage.py dumpdata authentication clients events groups front people polls
```

4 API documentation
===================

## Public endpoints

 * `/events`

    The list of all published, upcoming events (paginated).
    
    To get the complete list in one request, use `/events/summary`.

 *  `/calendars`

    The list of all calendars. Events are part of one calendar.

 * `/groups`

    The list of all published groups.
    
    To get the complete list in one request, use `/groups/summary`.

## Authenticated endpoints

 * `/people/me`

    Profile of the authenticated user.

## Resources filters

Each resource expose a series of filter that you can use to fetch a subset of the resource collection.

Filters can be passed as query parameters, e.g. `https://api.lafranceinsoumise.fr/legacy/groups/?contact_email=example@example.com`

 * `groups` and `events`

    * `contact_email`
    * `nb_path` : path on legacy NationBuilder website
    * `close_to` : find events close to a given location. Value must be a JSON Object with
        * `max_distance` : distance in meters
        * `coordinates` : array of coordinates [Longitude, Latitude]
    * `order_by_distance_to` : list all events, but by ordering them by distance to JSON array of [Longitude, Latitude]. By getting the first page, you get the 25 closest events.

 * `events`

    * `after`: ISO 8601 Datetime, get only events *finishing* after this date
    * `before`: ISO 8601 Datetime, get only events *starting* before this date
    * `calendar`: String, get only events belonging to a specific calendar

## Frontend pages

An optional HTML frontend is available for the API.

### Configuration

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

### Pages

1. An event management section, that a user can visit to see the events
   she organised, and those she RSVPed to. Events she organised may be
   modified through this section
2. A support group management section that allows the user to see the
   list of groups she is part of, and to modify those of which she is a
   group manager.
