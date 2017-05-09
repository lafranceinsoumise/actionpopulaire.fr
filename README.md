api-django
==========

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
