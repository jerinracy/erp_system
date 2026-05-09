from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="subscriptionplan",
            index=models.Index(fields=["is_active"], name="plan_active_idx"),
        ),
        migrations.AddIndex(
            model_name="subscription",
            index=models.Index(
                fields=["tenant", "status", "-end_date"],
                name="sub_tenant_status_end_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="subscription",
            index=models.Index(fields=["status", "end_date"], name="sub_status_end_idx"),
        ),
        migrations.AddIndex(
            model_name="subscription",
            index=models.Index(
                fields=["status", "notified_before_expiry", "end_date"],
                name="sub_notify_expiry_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["tenant", "-created_at"],
                name="payment_tenant_created_idx",
            ),
        ),
    ]
