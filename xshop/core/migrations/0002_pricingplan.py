# Generated by Django 3.1.1 on 2020-10-05 15:00

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import djmoney.models.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricingPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('EGP', 'EGP E£')], default='EGP', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), help_text='The cost of the plan', max_digits=14)),
                ('shop', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.shop')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]