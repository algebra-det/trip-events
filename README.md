# Event booking App ( APIs )

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone git@github.com:algebra-det/trip-events.git
$ cd trip-events
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ virtualenv2 --no-site-packages env
$ source env/bin/activate
OR
$ python -m venv env
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv2` or `venv`.

Once `pip` has finished downloading the dependencies, run migrations for DB:
```sh
(env)$ python manage.py migrate
```

Create a super user for Admin Panel:
```sh
(env)$ python manage.py createsuperuser
(env)$ python manage.py runserver
```
Run Django Server:
```sh
(env)$ python manage.py runserver
```

And navigate to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
