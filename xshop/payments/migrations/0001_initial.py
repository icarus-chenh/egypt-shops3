# Generated by Django 3.2 on 2021-07-06 22:18

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('mutual_reference', models.CharField(blank=True, editable=False, max_length=36, null=True)),
                ('gateway_transaction_id', models.CharField(blank=True, editable=False, max_length=36, null=True)),
                ('status', models.CharField(blank=True, editable=False, max_length=12, null=True)),
                ('order', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to='orders.order')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]