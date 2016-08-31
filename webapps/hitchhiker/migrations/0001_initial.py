# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=256, blank=True)),
                ('rideTime', models.IntegerField(blank=True)),
                ('rideTimeStr', models.CharField(max_length=255, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255)),
                ('messageType', models.CharField(max_length=30)),
                ('rideType', models.CharField(max_length=30)),
                ('rideId', models.IntegerField()),
                ('active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=256, blank=True)),
                ('rideTime', models.IntegerField(blank=True)),
                ('rideTimeStr', models.CharField(max_length=255, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('gID', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('imgUrl', models.CharField(max_length=256, null=True, blank=True)),
                ('address', models.CharField(max_length=256, blank=True)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
                ('hotness', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lName', models.CharField(max_length=30, null=True, blank=True)),
                ('fName', models.CharField(max_length=30, null=True, blank=True)),
                ('age', models.IntegerField(default=0, null=True, blank=True)),
                ('shortBio', models.CharField(default='This man leaves nothing', max_length=430, null=True, blank=True)),
                ('email', models.CharField(max_length=40, null=True, blank=True)),
                ('pictureUrl', models.CharField(max_length=256, null=True, blank=True)),
                ('destinations', models.ManyToManyField(related_name='profile_destinations', to='hitchhiker.Position', blank=True)),
                ('friends', models.ManyToManyField(related_name='profile_friends', to='hitchhiker.Profile', blank=True)),
                ('messages', models.ManyToManyField(related_name='profile_messages', to='hitchhiker.Message')),
                ('user', models.ForeignKey(related_name='profile_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeStamp', models.BigIntegerField()),
                ('text', models.CharField(max_length=1024)),
                ('author', models.CharField(max_length=30)),
                ('rating', models.FloatField()),
                ('text_length', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='position',
            name='reviews',
            field=models.ManyToManyField(related_name='position_reviews', null=True, to='hitchhiker.Review', blank=True),
        ),
        migrations.AddField(
            model_name='passenger',
            name='destination',
            field=models.ForeignKey(related_name='passenger_destination', to='hitchhiker.Position'),
        ),
        migrations.AddField(
            model_name='passenger',
            name='origin',
            field=models.ForeignKey(related_name='passenger_origin', to='hitchhiker.Position'),
        ),
        migrations.AddField(
            model_name='passenger',
            name='profile',
            field=models.ForeignKey(related_name='passenger_profile', to='hitchhiker.Profile'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(related_name='message_sender', to='hitchhiker.Profile'),
        ),
        migrations.AddField(
            model_name='driver',
            name='destination',
            field=models.ForeignKey(related_name='driver_destination', to='hitchhiker.Position'),
        ),
        migrations.AddField(
            model_name='driver',
            name='origin',
            field=models.ForeignKey(related_name='driver_origin', to='hitchhiker.Position'),
        ),
        migrations.AddField(
            model_name='driver',
            name='profile',
            field=models.ForeignKey(related_name='driver_profile', to='hitchhiker.Profile'),
        ),
    ]
