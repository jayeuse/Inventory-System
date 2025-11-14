# Generated manually for OTP model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory_system', '0021_alter_userinformation_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('otp_code', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, db_column='otp_code')),
                ('otp', models.CharField(max_length=6, db_column='otp')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('expires_at', models.DateTimeField(db_column='expires_at')),
                ('is_used', models.BooleanField(default=False, db_column='is_used')),
                ('is_verified', models.BooleanField(default=False, db_column='is_verified')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otp_codes', to=settings.AUTH_USER_MODEL, db_column='user_id')),
            ],
            options={
                'db_table': 'otp',
                'ordering': ['-created_at'],
            },
        ),
    ]
