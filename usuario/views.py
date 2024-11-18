from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db import connection
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.backends.db import SessionStore
from datetime import datetime


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
                    SELECT nombre, id_us
                    FROM USUARIO 
                    WHERE correo = %s AND password = %s
                """, [correo, password])
                user = cursor.fetchone()
                print('usuario fino: ' , user)
            
            if user:
                # guardamos el documento en sesión
                request.session['documento'] = user[1]  
                messages.success(request, f"Bienvenido {user[0]}!")
                return redirect('home')  

            else:
                messages.error(request, "Credenciales incorrectas. Inténtalo de nuevo.")
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}")

    return render(request, 'iniciosesion.html')


from datetime import date

def home(request):
    documento = request.session.get('documento')  
    usuario = []

    if documento:
        with connection.cursor() as cursor:
            query = """
                SELECT nombre, apellido, correo, fecha_nac, ubicacion
                FROM usuario
                WHERE id_us = %s
            """
            cursor.execute(query, [documento])  
            result = cursor.fetchone()  

            if result:
                nombre, apellido, correo, fecha_nac, ubicacion = result
                today = date.today()
                edad = today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))
                
                usuario = {
                    'nombre': nombre,
                    'apellido': apellido,
                    'correo': correo,
                    'fecha_nac': fecha_nac,
                    'edad': edad,
                    'ubicacion': ubicacion,
                }

    return render(request, 'home.html', {'usuario': usuario})



def publicar(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        contenido = request.POST['contenido']

        #obetemos el doc del usuario logueado
        documento = request.session.get('documento')
        print('id del usuario fino: ',documento)

        # Obtenemos la fecha y la hora actuales
        fecha_pub = datetime.now().strftime('%Y-%m-%d')  
        hora_pub = datetime.now().strftime('%H:%M:%S')  


        with connection.cursor() as cursor:
            cursor.execute("""
                            INSERT INTO PUBLICACION (id_us, contenido, fecha_pub, titulo, hora_pub)
                            VALUES (%s, %s, %s, %s, %s)
                        """, [documento, contenido, fecha_pub, titulo, hora_pub])
        
            messages.success(request, "Publicación exitosa.")
            return redirect('home') 



    return render(request, 'home.html')


def mostrar_publicacion(request):
    documento = request.session.get('documento')  
    
    publicaciones = []  # Lista para almacenar publicaciones
    
    if documento:
        # Abre un cursor para ejecutar la consulta SQL
        with connection.cursor() as cursor:
            query = """
                SELECT titulo, contenido, fech_pub, hora_pub
                FROM publicacion
                WHERE id_us = %s
            """
            cursor.execute(query, [documento])  # Evita SQL Injection utilizando parámetros
            results = cursor.fetchall()  # Recupera todas las publicaciones como una lista de tuplas
            
            # Convierte cada tupla en un diccionario
            publicaciones = [
                {'titulo': row[0], 'contenido': row[1], 'fecha': row[2], 'hora': row[3]}
                for row in results
            ]
    
            print('publiii que hay: ', publicaciones)
    # Renderiza la plantilla y pasa las publicaciones al contexto
    return render(request, 'home.html', {'publicaciones': publicaciones})



def cerrar_sesion(request):
    logout(request)  
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('iniciosesion')  