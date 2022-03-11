# Generated by Django 3.1.14 on 2022-03-10 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0005_auto_20220310_0616'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='setting',
            options={'permissions': [('change_basic', 'Can change basic setting'), ('change_email', 'Can change email setting'), ('change_auth', 'Can change auth setting'), ('change_sms', 'Can change sms setting'), ('change_security', 'Can change security setting'), ('change_clean', 'Can change clean setting'), ('change_other', 'Can change other setting'), ('change_interface', 'Can change interface setting'), ('change_license', 'Can change license setting'), ('change_terminal_basic_setting', 'Can change terminal basic setting')], 'verbose_name': 'System setting'},
        ),
    ]