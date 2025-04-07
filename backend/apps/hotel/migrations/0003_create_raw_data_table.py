from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0002_guest_reservation'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS raw_data (
                    datetime     TIMESTAMPTZ NOT NULL,
                    device_id    BIGINT NOT NULL REFERENCES hotel_device(id),
                    datapoint    TEXT NOT NULL,
                    value        TEXT NOT NULL
                );
                SELECT create_hypertable('raw_data', 'datetime', if_not_exists => TRUE);
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS raw_data;
            """
        )
    ]
