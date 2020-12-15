# agir.lafranceinsoumise.fr

[![Build Status](https://travis-ci.org/lafranceinsoumise/agir.lafranceinsoumise.fr.svg?branch=master)](https://travis-ci.org/lafranceinsoumise/agir.lafranceinsoumise.fr)

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
$ pipenv run ./manage.py makemigrations
$ pipenv run ./manage.py migrate
```

We use Travis to automatically test our code. To make sure you won't have to
recommit again, you should run the tests and the linters before pushing (again, this should
be ran from inside the `/vagrant` folder in the vagrant box).

```bash
$ black agir/
$ node_modules/.bin/esling --fix agir/
$ pipenv run ./manage.py test
``` 


[django-server]: http://agir.local:8000/
[mailhog]: http://agir.local:8025/
[django-admin]: http://agir.local:8000/admin/