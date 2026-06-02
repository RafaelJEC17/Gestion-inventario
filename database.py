import streamlit as st
import psycopg
from psycopg.rows import dict_row

# Cambiamos el nombre de la variable para que haga match con tu base de datos actual
URL_DE_SUPABASE = "postgresql://postgres.oecjufwgepeakcqmrelx:I8ofk123456789kul@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

def conseguir_conexion():
    """Función para conectar directamente a la base de datos de Supabase"""
    try:
        # Añadimos sslmode=require al final si no lo tenías para evitar rechazos de Supabase
        conexion = psycopg.connect(URL_DE_SUPABASE, row_factory=dict_row)
        return conexion
    except Exception as e:
        print(f"Error al conectar a Supabase: {e}")
        return None

def inicializar_base_datos():
    """Función que crea las tablas y el usuario administrador en Supabase"""
    print("Verificando/Creando tablas en la base de datos de Supabase...")
    conexion = conseguir_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            
            # Tabla Categorías
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(50) NOT NULL UNIQUE
                );
            """)
            
            # Tabla Productos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    precio NUMERIC(10, 2) NOT NULL,
                    stock INT NOT NULL,
                    categoria_id INT,
                    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
                );
            """)
            
            # Tabla Usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    rol VARCHAR(20) DEFAULT 'admin'
                );
            """)
            
            # Insertar usuario administrador inicial
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, rol) 
                VALUES ('rafael', 'admin123', 'admin')
                ON CONFLICT (username) DO NOTHING;
            """)
            
            conexion.commit()
            print("¡Tablas verificadas/creadas con éxito! 🚀")
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"Error ejecutando la inicialización: {e}")

def verificar_usuario(username, password):
    """Busca el usuario en la base de datos y verifica su credencial usando un alias explícito"""
    conexion = conseguir_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        
        # CAMBIO CLAVE: Agregamos "AS total" para fijar el nombre de la columna en el diccionario
        cursor.execute(
            "SELECT COUNT(*) AS total FROM usuarios WHERE username = %s AND password_hash = %s;", 
            (username.strip(), password.strip())
        )
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()
        
        # Evaluamos de forma segura según el tipo de respuesta
        if isinstance(resultado, dict):
            cantidad = resultado.get('total', 0)
        else:
            cantidad = resultado[0] if resultado else 0
            
        return cantidad > 0
    except Exception as e:
        print(f"Error al autenticar: {e}")
        return False