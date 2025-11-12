from django.db import migrations

def create_default_preferences(apps, schema_editor):
    Preference = apps.get_model('member', 'Preference')

    PREFERENCE_CHOICES = [
        ('T_SHIRT', 'T-shirt'),
        ('PANTALON', 'Pantalon'),
        ('ROBE', 'Robe'),
        ('CHAUSSURE', 'Chaussure'),
        ('VESTE', 'Veste'),
        ('ELECTRONIQUE', 'Électronique'),
        ('ACCESSOIRES', 'Accessoires'),
    ]

    for name, _ in PREFERENCE_CHOICES:
        Preference.objects.get_or_create(name=name)

def delete_preferences(apps, schema_editor):
    Preference = apps.get_model('member', 'Preference')
    Preference.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0006_preference_member_preferences'),  
    ]

    operations = [
        migrations.RunPython(create_default_preferences, delete_preferences),
    ]
