import streamlit as st
import psycopg
from psycopg.rows import dict_row

# Usamos la URL que tienes definida
URL_DE_RENDER = "postgresql://postgres.oecjufwgepeakcqmrelx:[YOUR-PASSWORD]@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

def conseguir_conexion():
    """Función para conectar directamente a la base de datos de Render"""
    try:
        conexion = psycopg.connect(URL_DE_RENDER, row_factory=dict_row)
        return conexion
    except Exception as e:
        print(f"Error al conectar a Render: {e}")
        return None

def inicializar_base_datos():
    """Función que crea las tablas y el usuario administrador en Render"""
    print("Verificando/Creando tablas en la base de datos de Render...")
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
    """Busca el usuario en Render y verifica su credencial"""
    conexion = conseguir_conexion()
    if not conexion:
        return False
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE username = %s AND password_hash = %s;", 
            (username.strip(), password.strip())
        )
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()
        return usuario is not None
    except Exception as e:
        print(f"Error al autenticar: {e}")
        return False