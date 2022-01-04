# Generated by Django 4.0 on 2022-01-04 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_alter_reservationeventseat_event_seat_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='reservationeventseat',
            name='reservations_reservationeventseat_unique_reservation_event_seat',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.SmallIntegerField(choices=[(1, 'Created'), (2, 'Invalidated'), (3, 'Payment Started'), (4, 'Payment Complete'), (5, 'Reserved')], default=1),
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('payment_id__isnull', True), ('status__in', [1, 2, 3])), models.Q(('payment_id__isnull', False), ('status__in', [4, 5])), _connector='OR'), name='reservations_reservation_completed_payment_must_have_payment_id'),
        ),
    ]