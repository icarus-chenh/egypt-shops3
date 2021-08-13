# Generated by Django 3.1.1 on 2020-10-04 18:09

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import multiselectfield.db.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('mobile', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('name', models.CharField(max_length=255)),
                ('dashboard_modules', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[], max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
