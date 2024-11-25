#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.core.management import execute_from_command_line
from django.db import connections
from django.db.utils import OperationalError

def load_initial_data():
    """Carga los datos iniciales desde los fixtures"""
    try:
        # Intenta conectar a la base de datos
        conn = connections['default']
        conn.cursor()
        
        # Si la conexión es exitosa, carga los fixtures
        fixtures = [
            'initial_categories',
            'initial_products',
        ]
        
        for fixture in fixtures:
            try:
                execute_from_command_line(['manage.py', 'loaddata', fixture])
                print(f'✅ Fixture {fixture} cargado correctamente')
            except Exception as e:
                print(f'❌ Error al cargar {fixture}: {str(e)}')
                
    except OperationalError:
        print('❌ Base de datos no disponible')
    except Exception as e:
        print(f'❌ Error inesperado: {str(e)}')

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')
    
    # Si el comando es migrate, ejecutamos las migraciones y luego cargamos los datos
    if len(sys.argv) > 1 and sys.argv[1] == 'migrate':
        execute_from_command_line(sys.argv)
        load_initial_data()
    else:
        execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
