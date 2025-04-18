# Generated by Django 5.1.1 on 2025-04-11 19:42

import blog.fields
import blog.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0004_alter_post_picture"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="picture",
            field=blog.fields.SVGAndImageField(
                default="",
                upload_to=blog.models.user_directory_path,
                validators=[
                    blog.fields.validate_svg_or_image,
                    blog.fields.validate_svg_or_image,
                ],
                verbose_name="Picture",
            ),
        ),
    ]
