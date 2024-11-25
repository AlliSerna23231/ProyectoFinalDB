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

            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN a.id_us = %s THEN u2.nombre 
                        ELSE u1.nombre 
                    END AS nombre_amigo,
                    CASE 
                        WHEN a.id_us = %s THEN u2.apellido 
                        ELSE u1.apellido 
                    END AS apellido_amigo
                FROM amistad a
                LEFT JOIN usuario u1 ON a.id_us = u1.id_us
                LEFT JOIN usuario u2 ON a.id_us2 = u2.id_us
                WHERE a.id_us = %s OR a.id_us2 = %s
            """, [documento, documento, documento, documento])
            amigos = cursor.fetchall()



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
    publicaciones = []  #lista
    
    with connection.cursor() as cursor:
        query = """
            SELECT titulo, contenido, fecha_pub, hora_pub, id_publicacion
            FROM publicacion
            WHERE id_us = %s
        """
        cursor.execute(query, [documento])  
        results = cursor.fetchall()  # Obtiene todos los resultados
        
        # Verifica si se obtuvieron resultados
        if not results:
            print("No se encontraron publicaciones para el documento:", documento)
        
        # Formateamos la fecha antes de agregarla a la lista
        publicaciones = [
            {
                'titulo': row[0],
                'contenido': row[1],
                'fecha_pub': row[2].strftime('%d/%m/%Y') if row[2] else None,  # Formatea la fecha
                'hora_pub': row[3],
                'id_publicacion': row[4]
            }
            for row in results
        ]
        amigos_list = [{'nombre': amigo[0], 'apellido': amigo[1]} for amigo in amigos]


    return render(request, 'home.html', {'usuario': usuario, 'publicaciones': publicaciones, 'amigos': amigos_list})



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


from datetime import datetime


def mostrar_publicacion(request):
    documento = request.session.get('documento')  # Obtienemos el documento del usuario logueado
    
    if not documento:
        print("No se encontró documento en la sesión.")
        return render(request, 'home.html', {'publicaciones': []})  
    
    publicaciones = []  # Lista de publicaciones
    
    with connection.cursor() as cursor:
        query = """
            SELECT p.titulo, p.contenido, p.fecha_pub, p.hora_pub, p.id_publicacion
            FROM publicacion p
            WHERE p.id_us = %s
        """
        cursor.execute(query, [documento])  
        results = cursor.fetchall()  
        
        if not results:
            print("No se encontraron publicaciones para el documento:", documento)
        
        # Formateamos la fecha antes de agregarla a la lista
        publicaciones = [
            {
                'titulo': row[0],
                'contenido': row[1],
                'fecha_pub': row[2].strftime('%d/%m/%Y') if row[2] else None,
                'hora_pub': row[3],
                'id_publicacion': row[4]
            }
            for row in results
        ]

    return render(request, 'home.html', {'publicaciones': publicaciones})


def me_gusta(request, id_publicacion):
    documento = request.session.get('documento')  

    if not documento:
        messages.error(request, "Debes iniciar sesión para dar 'Me gusta'.")
        return redirect('login')  

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_megusta, estado
            FROM ME_GUSTA
            WHERE id_us = %s AND id_publicacion = %s
        """, [documento, id_publicacion])

        result = cursor.fetchone()

        if result:
            id_megusta, estado = result
            new_estado = 0 if estado == 1 else 1

            cursor.execute("""
                UPDATE ME_GUSTA
                SET estado = %s
                WHERE id_megusta = %s
            """, [new_estado, id_megusta])

            if new_estado == 1:
                messages.success(request, "¡Te ha gustado esta publicación!")
            else:
                messages.success(request, "Has quitado tu 'Me gusta' de esta publicación.")
        else:
            cursor.execute("""
                INSERT INTO ME_GUSTA (id_us, id_publicacion, estado)
                VALUES (%s, %s, 1)
            """, [documento, id_publicacion])

            messages.success(request, "¡Te ha gustado esta publicación!")

    return redirect('home')  


def me_gustapublicacion(request, id_publicacion):
    documento = request.session.get('documento')  

    if not documento:
        messages.error(request, "Debes iniciar sesión para dar 'Me gusta'.")
        return redirect('login')  

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_megusta, estado
            FROM ME_GUSTA
            WHERE id_us = %s AND id_publicacion = %s
        """, [documento, id_publicacion])

        result = cursor.fetchone()

        if result:
            id_megusta, estado = result
            new_estado = 0 if estado == 1 else 1

            cursor.execute("""
                UPDATE ME_GUSTA
                SET estado = %s
                WHERE id_megusta = %s
            """, [new_estado, id_megusta])

            if new_estado == 1:
                messages.success(request, "¡Te ha gustado esta publicación!")
            else:
                messages.success(request, "Has quitado tu 'Me gusta' de esta publicación.")
        else:
            cursor.execute("""
                INSERT INTO ME_GUSTA (id_us, id_publicacion, estado)
                VALUES (%s, %s, 1)
            """, [documento, id_publicacion])

            messages.success(request, "¡Te ha gustado esta publicación!")

    return redirect('publicaciones') 


def me_gustaperfil(request, id_publicacion):
    documento = request.session.get('documento')  

    if not documento:
        messages.error(request, "Debes iniciar sesión para dar 'Me gusta'.")
        return redirect('login')  

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_megusta, estado
            FROM ME_GUSTA
            WHERE id_us = %s AND id_publicacion = %s
        """, [documento, id_publicacion])

        result = cursor.fetchone()

        if result:
            id_megusta, estado = result
            new_estado = 0 if estado == 1 else 1

            cursor.execute("""
                UPDATE ME_GUSTA
                SET estado = %s
                WHERE id_megusta = %s
            """, [new_estado, id_megusta])

            if new_estado == 1:
                messages.success(request, "¡Te ha gustado esta publicación!")
            else:
                messages.success(request, "Has quitado tu 'Me gusta' de esta publicación.")
        else:
            cursor.execute("""
                INSERT INTO ME_GUSTA (id_us, id_publicacion, estado)
                VALUES (%s, %s, 1)
            """, [documento, id_publicacion])

            messages.success(request, "¡Te ha gustado esta publicación!")

    return redirect('usuarios') 

def comentar(request, id_publicacion):
    documento = request.session.get('documento')  

    contenido = request.POST['comentario']
    fec_pub = datetime.now().strftime('%Y-%m-%d')  


    if not documento:
        messages.error(request, "Debes iniciar sesión para dar 'Me gusta'.")
        return redirect('login')  

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO comentario (id_us, id_publicacion, contenido, fec_pub)
            VALUES (%s, %s, %s, %s)
        """, [documento, id_publicacion, contenido, fec_pub])

        messages.success(request, "¡Has comentado esta publicación!")

    return redirect('home') 


def comentarios(request, id_publicacion):
    comentarios = []
    print('holaaaaaa bitch')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_us, id_publicacion, contenido, fec_pub
            FROM comentario
            WHERE id_publicacion = %s
        """, [id_publicacion])
        resultados = cursor.fetchall()

        for resultado in resultados:
            id_us, id_publicacion, contenido, fec_pub = resultado
            comentarios.append({
                'id_us': id_us,
                'id_publicacion': id_publicacion,
                'contenido': contenido,
                'fec_pub': fec_pub,
            })
            

    return render(request, 'home.html', {
        'comentarios': comentarios,  
        'id_publicacion': id_publicacion  
    })





def usuarios(request):
    documento = request.session.get('documento')  

    usuarios = []  

    if documento:
        with connection.cursor() as cursor:
            query = """
                SELECT id_us, nombre, apellido, correo, fecha_nac, ubicacion
                FROM usuario
                WHERE id_us != %s
            """
            cursor.execute(query, [documento])  
            results = cursor.fetchall()

            usuarios = [
                {
                    'id_us': row[0],
                    'nombre': row[1],
                    'apellido': row[2],
                    'correo': row[3],
                    'fecha_nac': row[4],
                    'ubicacion': row[5],
                }
                for row in results
            ]
    
    return render(request, 'addamigos.html', {'usuarios': usuarios})


def ver_perfil(request, id_us):
    usuario = []

    if id_us:
        with connection.cursor() as cursor:
            query = """
                SELECT id_us, nombre, apellido, correo, fecha_nac, ubicacion
                FROM usuario
                WHERE id_us = %s
            """
            cursor.execute(query, [id_us])  
            result = cursor.fetchone()  

            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN a.id_us = %s THEN u2.nombre 
                        ELSE u1.nombre 
                    END AS nombre_amigo,
                    CASE 
                        WHEN a.id_us = %s THEN u2.apellido 
                        ELSE u1.apellido 
                    END AS apellido_amigo
                FROM amistad a
                LEFT JOIN usuario u1 ON a.id_us = u1.id_us
                LEFT JOIN usuario u2 ON a.id_us2 = u2.id_us
                WHERE a.id_us = %s OR a.id_us2 = %s
            """, [id_us, id_us, id_us, id_us])
            amigos = cursor.fetchall()

            if result:
                id_us, nombre, apellido, correo, fecha_nac, ubicacion = result
                today = date.today()
                edad = today.year - fecha_nac.year - ((today.month, today.day) < (fecha_nac.month, fecha_nac.day))
                
                usuario = {
                    'id_us': id_us,
                    'nombre': nombre,
                    'apellido': apellido,
                    'correo': correo,
                    'fecha_nac': fecha_nac,
                    'edad': edad,
                    'ubicacion': ubicacion,
                }
        publicaciones = []  # Lista de publicaciones
    
    with connection.cursor() as cursor:
        query = """
            SELECT p.titulo, p.contenido, p.fecha_pub, p.hora_pub, p.id_publicacion
            FROM publicacion p
            WHERE p.id_us = %s
        """
        cursor.execute(query, [id_us])  
        results = cursor.fetchall()  
        
        if not results:
            print("No se encontraron publicaciones para el documento:", id_us)
        
        # Formateamos la fecha antes de agregarla a la lista
        publicaciones = [
            {
                'titulo': row[0],
                'contenido': row[1],
                'fecha_pub': row[2].strftime('%d/%m/%Y') if row[2] else None,
                'hora_pub': row[3],
                'id_publicacion': row[4]
            }
            for row in results
        ]
        amigos_list = [{'nombre': amigo[0], 'apellido': amigo[1]} for amigo in amigos]


    return render(request, 'verperfil.html', {'usuario': usuario, 'publicaciones': publicaciones, 'amigos': amigos_list})


def chatear(request, id_us):
    # Obtengo el documento del usuario logueado
    documento = request.session.get('documento')

    if not documento:
        return redirect('iniciosesion')  

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_us, contenido, fec_envio
            FROM mensaje
            WHERE 
            (id_us = %s AND id_us2 = %s)  
            OR 
            (id_us = %s AND id_us2 = %s)
            ORDER BY fec_envio
        """, [documento, id_us, id_us, documento])
        mensajes = cursor.fetchall()

        #Sacamos el nombre y apellido del usuario seleccionado para mostrarlo en el template
        cursor.execute("""
            SELECT nombre, apellido
            FROM usuario
            WHERE id_us = %s
        """, [id_us])
        usuario_seleccionado = cursor.fetchone()

        if usuario_seleccionado:
            nombre_usuario = usuario_seleccionado[0]
            apellido_usuario = usuario_seleccionado[1]
        else:
            nombre_usuario = "Desconocido"
            apellido_usuario = ""

    mensajes_dict = [{
        'id_us': mensaje[0],
        'contenido': mensaje[1],
        'fec_envio': mensaje[2]
    } for mensaje in mensajes]

    return render(request, 'chatear.html', {
        'mensajes': mensajes_dict,
        'id_us': id_us,
        'documento': documento,  
        'nombre_usuario': nombre_usuario,
        'apellido_usuario': apellido_usuario
    })




def enviar_mensaje(request, id_us):
    # Obtengo el doc del usuario logueado
    documento = request.session.get('documento')

    if request.method == 'POST':
        contenido = request.POST['contenido']
        fecha_env = datetime.now().strftime('%Y-%m-%d')

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO mensaje (id_us, id_us2, contenido, fec_envio)
                VALUES (%s, %s, %s, %s)
            """, [documento, id_us, contenido, fecha_env])
        
            messages.success(request, "Mensaje enviado exitosamente.")
            return redirect('chatear', id_us=id_us)  

    return render(request, 'chatear.html')


def addamigo(request, id_us):
    documento = request.session.get('documento')

    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO amistad (id_us, id_us2)
            VALUES (%s, %s)
        """, [documento, id_us])

        #Sacamos el nombre y apellido del usuario seleccionado para mostrarlo en el template
        cursor.execute("""
            SELECT nombre, apellido
            FROM usuario
            WHERE id_us = %s
        """, [id_us])
        usuario_seleccionado = cursor.fetchone()

        if usuario_seleccionado:
            nombre_usuario = usuario_seleccionado[0]
            apellido_usuario = usuario_seleccionado[1]
        else:
            nombre_usuario = "Desconocido"
            apellido_usuario = ""

        messages.success(request, f"Tú y {nombre_usuario} {apellido_usuario} son amigos...")
        return redirect('buscar_amigos')  
        

    return render(request, 'addamigos.html')



def buscar_amigos(request):
    usuarios = []
    if request.method == 'POST':
        amigo = request.POST.get('amigo', '').strip()  
        documento = request.session.get('documento')

        with connection.cursor() as cursor:
            query = """
                SELECT id_us, nombre, apellido, correo, fecha_nac, ubicacion
                FROM usuario
                WHERE id_us != %s AND (LOWER(nombre) LIKE %s OR LOWER(apellido) LIKE %s)
            """
            cursor.execute(query, [documento, f"%{amigo.lower()}%", f"%{amigo.lower()}%"])
            results = cursor.fetchall()

        usuarios = [
            {
                'id_us': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'correo': row[3],
                'fecha_nac': row[4],
                'ubicacion': row[5],
            }
            for row in results
        ]

    return render(request, 'addamigos.html', {'usuarios': usuarios})


def publicaciones(request):
    documento = request.session.get('documento')  # Obtienemos el documento del usuario logueado
    
    if not documento:
        print("No se encontró documento en la sesión.")
        return render(request, 'home.html', {'publicaciones': []})  
    
    publicaciones = []  # Lista de publicaciones
    
    with connection.cursor() as cursor:
        query = """
            SELECT p.titulo, p.contenido, p.fecha_pub, p.hora_pub, p.id_publicacion, 
                   p.id_us, u.nombre, u.apellido, u.correo
            FROM publicacion p
            JOIN usuario u ON p.id_us = u.id_us
            ORDER BY p.fecha_pub DESC, p.hora_pub DESC
        """
        cursor.execute(query)  
        results = cursor.fetchall()  
        
        if not results:
            print("No se encontraron publicaciones para el documento:", documento)
        
        # Formateamos los datos antes de agregar a la lista de publicaciones
        publicaciones = [
            {
                'titulo': row[0],
                'contenido': row[1],
                'fecha_pub': row[2].strftime('%d/%m/%Y') if row[2] else None,
                'hora_pub': row[3],
                'id_publicacion': row[4],
                'id_us': row[5],
                'nombre_usuario': row[6],
                'apellido_usuario': row[7],
                'correo_usuario': row[8]
            }
            for row in results
        ]

    return render(request, 'publicaciones.html', {'publicaciones': publicaciones})


def cerrar_sesion(request):
    logout(request)  
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect('iniciosesion')  