from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("automation", "0003_alter_event_event_type"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="event",
            index=models.Index(
                fields=["tenant", "event_type", "-created_at"],
                name="event_tenant_type_created_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="rule",
            index=models.Index(
                fields=["tenant", "event_type", "is_active"],
                name="rule_tenant_type_active_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="rule",
            index=models.Index(
                fields=["tenant", "event_type", "action"],
                name="rule_tenant_type_action_idx",
            ),
        ),
    ]
