from fastapi import FastAPI, HTTPException
# Importamos la función de conexión que creamos en el otro archivo
from database import conseguir_conexion 

app = FastAPI(title="Sistema de Inventario")

# --- ENDPOINT 1: CREAR UNA CATEGORÍA (POST) ---
@app.post("/categorias/")
def crear_categoria(nombre: str):
    conexion = conseguir_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    try:
        cursor = conexion.cursor()
        # Insertamos la nueva categoría en la base de datos
        query = "INSERT INTO categorias (nombre) VALUES (%s) RETURNING id, nombre;"
        cursor.execute(query, (nombre,))
        
        # Guardamos los cambios y obtenemos el registro creado
        nueva_categoria = cursor.fetchone()
        conexion.commit()
        
        cursor.close()
        conexion.close()
        return {"mensaje": "Categoría creada con éxito", "datos": nueva_categoria}
        
    except Exception as e:
        conexion.close()
        raise HTTPException(status_code=400, detail=f"Error al crear categoría: {e}")


# --- ENDPOINT 2: LISTAR TODOS LOS PRODUCTOS (GET) ---
@app.get("/productos/")
def obtener_productos():
    conexion = conseguir_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = conexion.cursor()
    # Hacemos un SELECT clásico
    cursor.execute("SELECT * FROM productos;")
    productos = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return productos

# --- ENDPOINT 3: CREAR UN PRODUCTO (POST) ---
@app.post("/productos/")
def crear_producto(nombre: str, precio: float, stock: int, categoria_id: int):
    conexion = conseguir_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    try:
        cursor = conexion.cursor()
        # Consulta SQL para insertar el producto
        query = """
            INSERT INTO productos (nombre, precio, stock, categoria_id) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id, nombre, precio, stock, categoria_id;
        """
        cursor.execute(query, (nombre, precio, stock, categoria_id))
        nuevo_producto = cursor.fetchone()
        conexion.commit()
        
        cursor.close()
        conexion.close()
        return {"mensaje": "Producto creado con éxito", "producto": nuevo_producto}
        
    except Exception as e:
        conexion.close()
        raise HTTPException(status_code=400, detail=f"Error al crear producto: {e}")


# --- ENDPOINT 4: ACTUALIZAR STOCK DE UN PRODUCTO (PUT) ---
@app.put("/productos/{producto_id}/stock")
def actualizar_stock(producto_id: int, nuevo_stock: int):
    conexion = conseguir_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = conexion.cursor()
    # Actualizamos el stock filtrando por el ID del producto
    query = "UPDATE productos SET stock = %s WHERE id = %s RETURNING id, nombre, stock;"
    cursor.execute(query, (nuevo_stock, producto_id))
    producto_actualizado = cursor.fetchone()
    conexion.commit()
    
    cursor.close()
    conexion.close()
    
    # Si la consulta no devolvió nada, es porque el ID no existe
    if not producto_actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    return {"mensaje": "Stock actualizado", "datos": producto_actualizado}


# --- ENDPOINT 5: ELIMINAR UN PRODUCTO (DELETE) ---
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    conexion = conseguir_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
    
    cursor = conexion.cursor()
    # Eliminamos el registro
    query = "DELETE FROM productos WHERE id = %s RETURNING id, nombre;"
    cursor.execute(query, (producto_id,))
    producto_eliminado = cursor.fetchone()
    conexion.commit()
    
    cursor.close()
    conexion.close()
    
    if not producto_eliminado:
        raise HTTPException(status_code=404, detail="El producto que intentas eliminar no existe")
        
    return {"mensaje": "Producto eliminado correctamente", "datos": producto_eliminado}