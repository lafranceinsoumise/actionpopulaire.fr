<p align="center">
  <img height="150" src="https://github.com/lafranceinsoumise/actionpopulaire.fr/blob/staging/agir/front/components/genericComponents/logos/action-populaire.svg">
</p>

![Tests status](https://github.com/lafranceinsoumise/actionpopulaire.fr/actions/workflows/run-tests.yml/badge.svg)

# actionpopulaire.fr


## Mise en place du projet


```bash
lando start
lando manage migrate 

# create a super user for the admin part
lando manage createsuperperson --email yourEmail@email.com

```


# OLD

1. [Vagrant installation](#vagrant)
2. [Useful commands](#frontend-pages)

## Vagrant installation

You can use Vagrant to create a virtual machine running the project out of the box.
You need to have Vagrant and VirtualBox installed on your computer. 


If this is not already installed, install vagrant-hostmanager plugin :
```bash 
$ vagrant plugin install vagrant-hostmanager
```
Then just launch the box :
```bash 
$ vagrant up
```

This installs PostgreSQL, Redis and Node onto the virtual
machine, and launch three more systemd services :

* `django` which is the development server of this project
* `MailHog`, a catch-all SMTP server used for development
* `webpack`, the webpack dev server with hot reloading

You can access Django from [http://agir.local:8000][django-server]
and Mailhog from [http://agir.local:8025][mailhog].
Webpack dev server listens on port 3000.

Initial migrations are automatically applied, and some fake data has been
loaded up. You can connect directly connect to the [django admin][django-admin] using the
default superuser `admin@agir.local` with password `password`.


The `/vagrant` directory in the box is synchronized with your
project directory on the host.

## Useful commands

Whenever you change the django models, you'll have to generate the migrations and apply them.

Connect to the vagrant box and move to the project directory :
```bash

$ vagrant ssh
$ cd /vagrant
```

Generate, then apply the migrations :
```bash
$ poetry run ./manage.py makemigrations
$ poetry run ./manage.py migrate
```

We use Travis to automatically test our code. To make sure you won't have to
recommit again, you should run the tests and the linters before pushing (again, this should
be ran from inside the `/vagrant` folder in the vagrant box).

```bash
$ black agir/
$ node_modules/.bin/eslint --fix agir/
$ poetry run ./manage.py test
``` 

# Mise à jour suite au squashing des migrations du 7 janvier 2021

Si vous avez un environnement de développement déjà en place avant le 7 janvier,
vous devez réaliser les opérations suivantes pour qu'il reste fonctionnel.

Assurez-vous de d'abord réaliser toutes les migrations jusqu'au commit c5e16d4be173.
Ensuite, dans une console django, exécutez le script suivant :

```python
from django.db import connection

QUERY = """
INSERT INTO django_migrations (app, name, applied)
VALUES 
('people', '0001_creer_modeles', NOW()),
('people', '0002_objets_initiaux', NOW()),
('people', '0003_segments', NOW()),
('payments', '0001_creer_modeles', NOW()),
('groups', '0001_creer_modeles', NOW()),
('groups', '0002_creer_sous_types', NOW()),
('events', '0001_creer_modeles', NOW()),
('events', '0002_objets_initiaux_et_recherche', NOW());
"""

with connection.cursor() as cursor:
    cursor.execute(QUERY)
```

Les nouvelles migrations seront ainsi considérées comme déjà exécutées.


[django-server]: http://agir.local:8000/
[mailhog]: http://agir.local:8025/
[django-admin]: http://agir.local:8000/admin/
