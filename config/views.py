import os

from django.http import HttpResponse


def home(request):
    app_env = os.getenv('APP_ENV', 'local')
    return HttpResponse(
        f"""
        <h1>Hola mundo</h1>
        <p>Entorno: {app_env}</p>
        <p>La app Django está funcionando correctamente.</p>
        """
    )
