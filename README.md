I tried to keep the api structure in such a way so that it be used to
write both the admin site and general user site.
Check `TODO` for new ideas.

## Run the api server

* docker-compose up -d
* python manage.py migrate
* python manage.py runserver

## Run celery and beat server
* celery -A ticket_world worker --loglevel=info
* celery -A ticket_world beat -l info

## Celery tasks
I have wrote 3 celery periodic tasks :
* `event_starter` : every 1 minute this tries to make event status `RUNNING`
* `event_stopper` : every 1 minute it tries to invalidate, stopped or complete the event status.
* `start_reservation_invalidator` : tries to invalidate reservation if 15 minutes passed after creation without making actual payment.

I am using `django-celery-beat`. This extension enables you to store the periodic task schedule in the database.
The periodic tasks can be managed from the Django Admin interface, where you can create, edit and delete periodic tasks and how often they should run.
So we need to create these 3 tasks from admin panel.

## Run tests
* python manage.py test --keepdb

## TODO
* write more tests
* Before deleting an event seat check whether its occupied or not
* Implement avoid one - we can only buy tickets in a quantity that will not leave only 1 ticket
* Integrate `flower` for celery task monitoring.

