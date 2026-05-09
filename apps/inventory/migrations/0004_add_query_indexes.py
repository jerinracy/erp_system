from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_product_low_stock_alert_sent_and_more"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="category",
            index=models.Index(
                fields=["tenant", "name"],
                name="category_tenant_name_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["tenant", "name"],
                name="product_tenant_name_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                django.db.models.functions.text.Lower("name"),
                "tenant",
                name="product_tenant_lname_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["tenant", "stock"],
                name="product_tenant_stock_idx",
            ),
        ),
    ]
