# Itakalo-backend

================================

### Technical Stack

    - Python/Django: python 3.9, Django 4.2

    - Database: PostgreSQL 17.4

    - JWT auth based RESTful API

### Create server

    ```
    $ python3 -m venv env

    $ source env/bin/activate

    $ pip install -r requirements.txt
    ```

### Migrate models into database

    ```
    $ ./manage.py makemigrations

    $ ./manage.py migrate
    ```

### Create admin user on server

    ```
    $ ./manage.py createsuperuser
    ```

### Run server

    ```
    $ ./manage.py runserver
    ```

    or

    ```
    $ ./manage.py runserver 0.0.0.0:8000
    ```

### Server urls

<!-- - http://127.0.0.1:8000/super-admin/ -->

- http://127.0.0.1:8000/api/

<!-- - http://127.0.0.1:8000/api-docs/ -->



### Requirements
  ```
  $ pip freeze > requirements.txt
  ```