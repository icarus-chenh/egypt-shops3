# Generated by Django 3.2 on 2021-07-08 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shops", "0003_shop_subdomain"),
    ]

    def forward(apps, schema_editor):
        shops = apps.get_model("shops", "Shop")
        for shop in shops.objects.all():
            shop.subdomain = shop.id
            shop.save()

    operations = [migrations.RunPython(forward)]