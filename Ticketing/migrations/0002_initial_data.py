# ticketing/migrations/0002_initial_data.py

from django.db import migrations

def create_theaters(apps, schema_editor):
    Theater = apps.get_model('Ticketing', 'Theater')
    
    theaters = [
        {
            'name': 'West Texas Cinema',
            'location': 'Lubbock',
            'address': '123 Main St, Lubbock, TX 79401'
        },
        {
            'name': 'Star Movies',
            'location': 'Amarillo',
            'address': '456 Broadway Ave, Amarillo, TX 79101'
        },
        {
            'name': 'Levelland Cinemas',
            'location': 'Levelland',
            'address': '789 College Ave, Levelland, TX 79336'
        },
        {
            'name': 'Plainview Theater',
            'location': 'Plainview',
            'address': '321 Main St, Plainview, TX 79072'
        },
        {
            'name': 'Snyder Movie House',
            'location': 'Snyder',
            'address': '654 Western Ave, Snyder, TX 79549'
        },
        {
            'name': 'Abilene Films',
            'location': 'Abilene',
            'address': '987 Pine St, Abilene, TX 79601'
        }
    ]
    
    for theater_data in theaters:
        Theater.objects.create(**theater_data)

def delete_theaters(apps, schema_editor):
    Theater = apps.get_model('Ticketing', 'Theater')
    Theater.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('Ticketing', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_theaters, delete_theaters),
    ]