from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("integrations", "0007_webhook_secret"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="apikey",
            index=models.Index(
                fields=["tenant", "is_active"],
                name="apikey_tenant_active_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="apikeyusage",
            index=models.Index(
                fields=["api_key", "timestamp"],
                name="apikeyusage_key_time_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="iprequestlog",
            index=models.Index(
                fields=["ip_address", "timestamp"],
                name="iplog_ip_time_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="webhook",
            index=models.Index(
                fields=["tenant", "event", "is_active"],
                name="webhook_tenant_event_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="failedwebhook",
            index=models.Index(
                fields=["status", "next_retry_at"],
                name="failedwh_status_retry_idx",
            ),
        ),
    ]
