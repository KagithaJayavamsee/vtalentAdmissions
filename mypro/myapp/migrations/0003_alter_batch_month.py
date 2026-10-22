from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0002_coursenote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='month',
            field=models.CharField(
                choices=[
                    ('1', 'January'),
                    ('2', 'February'),
                    ('3', 'March'),
                    ('4', 'April'),
                    ('5', 'May'),
                    ('6', 'June'),
                    ('7', 'July'),
                    ('8', 'August'),
                    ('9', 'September'),
                    ('10', 'October'),
                    ('11', 'November'),
                    ('12', 'December'),
                ],
                max_length=30,
            ),
        ),
    ]
