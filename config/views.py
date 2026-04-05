import os

from django.db import connection
from django.db.utils import Error
from django.http import HttpResponse


def home(request):
    app_env = os.getenv('APP_ENV', 'local')
    db_status = 'Conexion exitosa a la base de datos'

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Error as exc:
        db_status = f'Error de conexion a la base de datos: {exc}'

    return HttpResponse(
        f"""
        <h1>Hola mundo</h1>
        <p>Entorno: {app_env}</p>
        <p>{db_status}</p>
        <p>La app Django está funcionando correctamente.</p>
        """
    )
