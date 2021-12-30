# Generated by Django 4.0 on 2021-12-27 13:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_alter_event_tags_alter_event_user_alter_event_venue_and_more"),
        ("reservations", "0004_alter_reservation_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reservationeventseat",
            name="event_seat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reservations",
                to="events.eventseat",
            ),
        ),
        migrations.AlterField(
            model_name="reservationeventseat",
            name="reservation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="event_seats",
                to="reservations.reservation",
            ),
        ),
    ]