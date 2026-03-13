from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_trip_has_issue_issue_text"),
    ]

    operations = [
        migrations.CreateModel(
            name="BusCurrentLocation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("lat", models.FloatField()),
                ("lon", models.FloatField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "trip",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.trip",
                    ),
                ),
            ],
        ),
    ]
