api-django
==========

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

