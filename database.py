import psycopg
from psycopg.rows import dict_row

# Una sola variable limpia con todos tus datos reales de Supabase.
# RECUERDA: Cambia [YOUR-PASSWORD] por la contraseña real que le pusiste a Supabase.
URL_DE_SUPABASE = "postgresql://rafael:lCP262T35MwwlUEKrNaOwfIH9YIGSSd3@dpg-d8fepof7f7vs73cub09g-a.ohio-postgres.render.com/inventario_cloud"

def conseguir_conexion():
    """Función para conectar directamente a la base de datos de Supabase"""
    try:
        # Pasamos la URL directa y listo, psycopg se encarga del resto
        conexion = psycopg.connect(URL_DE_SUPABASE, row_factory=dict_row)
        return conexion
    except Exception as e:
        print(f"Error al conectar a Supabase: {e}")
        return None

if __name__ == "__main__":
    print("Creando tablas en la base de datos de Render...")
    conexion = conseguir_conexion()
    if conexion:
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
        
        conexion.commit()
        print("¡Tablas creadas con éxito en la nube! 🚀")
        cursor.close()
        conexion.close()