import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-created_at', '-id'),
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('duration', models.CharField(max_length=80)),
                ('description', models.TextField(blank=True)),
                ('syllabus', models.TextField(blank=True)),
                ('display_order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('display_order', 'title'),
            },
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('month', models.PositiveSmallIntegerField(choices=[(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')])),
                ('year', models.PositiveSmallIntegerField()),
                ('duration', models.CharField(blank=True, max_length=80)),
                ('google_form_url', models.URLField(blank=True, max_length=500)),
                ('registrations_open', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='myapp.course')),
            ],
            options={
                'ordering': ('year', 'month', 'name'),
            },
        ),
    ]
