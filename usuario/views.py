from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db import connection
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password

# vista para insertar un usuario en la tabla USUARIO
def registro(request):
    if request.method == 'POST':
        try:

            documento = request.POST['documento']
            nombre = request.POST['nombre']
            apellido = request.POST['apellido']
            correo = request.POST['correo']
            password = request.POST['password']
            fecha_nac = request.POST['fecha_nac']
            ubicacion = request.POST['ubicacion']

            #cifrar el password
            #hashed_password = make_password(password)

            with connection.cursor() as cursor:
                cursor.execute("""
                            INSERT INTO USUARIO (id_us, nombre, apellido, correo, password, fecha_nac, ubicacion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, [documento, nombre, apellido, correo, password, fecha_nac, ubicacion])
        
            messages.success(request, "Registro de usuario exitoso.")
            return redirect('registro')
    
        except Exception as e:
            error_message = f"Error en el registro de usuario: {str(e)}"
            print(error_message)
            messages.error(request, error_message)
            return render(request, 'registro.html')

    return render(request, 'registro.html')

def iniciosesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        # Consulta con cursor SQL
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT nombre 
                    FROM USUARIO 
                    WHERE correo = %s AND password = %s
                """, [correo, password])
                user = cursor.fetchone()
            
            if user:
                # Usuario autenticado, redirigir a otro template
                messages.success(request, f"Bienvenido {user[0]}!")
                return redirect('home')  # Cambia 'home' por tu URL correspondiente
            else:
                messages.error(request, "Credenciales incorrectas. Inténtalo de nuevo.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")

    return render(request, 'iniciosesion.html')

def home(request):
    return render(request, 'home.html')