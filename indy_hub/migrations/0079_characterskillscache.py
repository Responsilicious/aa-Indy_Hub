# Generated migration for CharacterSkillsCache model

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('indy_hub', '0078_blueprintcopyoffer_source_scope'),
    ]

    operations = [
        migrations.CreateModel(
            name='CharacterSkillsCache',
            fields=[
                ('character_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('skills_json', models.JSONField(help_text='JSON data of character skills from ESI')),
                ('cached_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Cached Character Skills',
                'verbose_name_plural': 'Cached Character Skills',
                'default_permissions': (),
            },
        ),
    ]
