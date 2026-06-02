import streamlit as st
from database import conseguir_conexion, verificar_usuario

# Configuración de la página
st.set_page_config(page_title="Control de Inventario", page_icon="📦", layout="wide")

# ==========================================
# CONTROL DE AUTENTICACIÓN (BASE DE DATOS)
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Botón en la barra lateral para cerrar sesión si se está adentro
if st.session_state.autenticado:
    st.sidebar.title("👤 Administrador")
    if st.sidebar.button("Cerrar Sesión 🔓", type="secondary"):
        st.session_state.autenticado = False
        st.rerun()

st.title("📦 Sistema de Gestión de Inventario")
st.markdown("Panel de pruebas.")
st.markdown("---")

# Creamos las pestañas para organizar la navegación
tab1, tab2, tab3 = st.tabs(["📊 Ver Inventario", "➕ Agregar Mercancía", "⚙️ Gestionar Categorías"])

# ==========================================
# PESTAÑA 1: VER INVENTARIO Y ACCIONES (Pública)
# ==========================================
with tab1:
    st.header("📊 Inventario Actual")
    conexion = conseguir_conexion()
    if conexion:
        cursor = conexion.cursor()
        query = """
            SELECT p.id, p.nombre, p.precio, p.stock, c.nombre AS categoria 
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.id DESC;
        """
        cursor.execute(query)
        inventario = cursor.fetchall()
        
        # Traemos también la lista para el editor de stock rápido
        cursor.execute("SELECT id, nombre, stock FROM productos ORDER BY nombre;")
        productos_edicion = cursor.fetchall()
        
        cursor.close()
        conexion.close()
        
        if inventario:
            # Columnas internas para separar la tabla de los botones de acción
            col_tabla, col_accion = st.columns([2, 1])
            
            with col_tabla:
                st.subheader("Lista de Productos")
                st.table(inventario)
                
            with col_accion:
                st.subheader("⚡ Modificar Stock")
                opciones_prod = {p['nombre']: p['id'] for p in productos_edicion}
                prod_seleccionado = st.selectbox("Selecciona producto:", list(opciones_prod.keys()))
                id_prod_modificar = opciones_prod[prod_seleccionado]
                stock_actual = next(p['stock'] for p in productos_edicion if p['id'] == id_prod_modificar)
                
                st.write(f"Stock actual: **{stock_actual}** uds.")
                nuevo_stock = st.number_input("Nuevo stock:", min_value=0, value=int(stock_actual), step=1)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("Actualizar", type="secondary"):
                        conexion = conseguir_conexion()
                        cursor = conexion.cursor()
                        cursor.execute("UPDATE productos SET stock = %s WHERE id = %s;", (nuevo_stock, id_prod_modificar))
                        conexion.commit()
                        cursor.close()
                        conexion.close()
                        st.success("¡Actualizado!")
                        st.rerun()
                with col_btn2:
                    if st.button("🗑️ Eliminar", type="primary"):
                        conexion = conseguir_conexion()
                        cursor = conexion.cursor()
                        cursor.execute("DELETE FROM productos WHERE id = %s;", (id_prod_modificar,))
                        conexion.commit()
                        cursor.close()
                        conexion.close()
                        st.warning("Eliminado.")
                        st.rerun()
        else:
            st.info("No hay productos en el inventario todavía.")

# ==========================================
# PESTAÑA 2: AGREGAR NUEVO PRODUCTO (Protegida)
# ==========================================
with tab2:
    st.header("🛍️ Registrar Nuevo Producto")
    
    if not st.session_state.autenticado:
        st.warning("🔒 Se requieren credenciales administrativas para añadir productos.")
        usuario_p2 = st.text_input("Usuario:", key="user_p2")
        clave_p2 = st.text_input("Contraseña:", type="password", key="pass_p2")
        
        if st.button("Autenticar", key="btn_p2", type="primary"):
            if verificar_usuario(usuario_p2, clave_p2):
                st.session_state.autenticado = True
                st.success("Acceso concedido. Cargando formulario...")
                st.rerun()
            else:
                st.error("Acceso denegado. Credenciales incorrectas. ❌")
    else:
        # Código de ejecución original
        conexion = conseguir_conexion()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM categorias;")
            categorias_productos = cursor.fetchall()
            cursor.close()
            conexion.close()

        if categorias_productos:
            opciones_categorias = {cat['nombre']: cat['id'] for cat in categorias_productos}
            
            # Formulario limpio
            with st.form("formulario_producto"):
                nombre_prod = st.text_input("Nombre del producto:")
                precio_prod = st.number_input("Precio ($):", min_value=0.0, step=0.1)
                stock_prod = st.number_input("Stock inicial:", min_value=0, step=1)
                categoria_seleccionada = st.selectbox("Categoría:", list(opciones_categorias.keys()))
                
                enviado = st.form_submit_button("Guardar Producto en Inventario", type="primary")
                if enviado:
                    if nombre_prod.strip() == "":
                        st.warning("El nombre no puede estar vacío.")
                    else:
                        id_cat = opciones_categorias[categoria_seleccionada]
                        conexion = conseguir_conexion()
                        cursor = conexion.cursor()
                        query = "INSERT INTO productos (nombre, precio, stock, categoria_id) VALUES (%s, %s, %s, %s);"
                        cursor.execute(query, (nombre_prod.strip(), precio_prod, stock_prod, id_cat))
                        conexion.commit()
                        cursor.close()
                        conexion.close()
                        st.success(f"¡{nombre_prod} agregado con éxito!")
                        st.rerun()
        else:
            st.info("Ve a la pestaña de Categorías para crear una primero.")

# ==========================================
# PESTAÑA 3: GESTIONAR CATEGORÍAS (Protegida)
# ==========================================
with tab3:
    st.header("📂 Gestión de Categorías")
    
    if not st.session_state.autenticado:
        st.warning("🔒 Se requieren credenciales administrativas para gestionar categorías.")
        usuario_p3 = st.text_input("Usuario:", key="user_p3")
        clave_p3 = st.text_input("Contraseña:", type="password", key="pass_p3")
        
        if st.button("Autenticar", key="btn_p3", type="primary"):
            if verificar_usuario(usuario_p3, clave_p3):
                st.session_state.autenticado = True
                st.success("Acceso concedido. Cargando panel de categorías...")
                st.rerun()
            else:
                st.error("Acceso denegado. Credenciales incorrectas. ❌")
    else:
        # Código de ejecución original
        col_crear, col_ver = st.columns(2)
        
        with col_crear:
            st.subheader("Crear Categoría")
            nueva_cat = st.text_input("Nombre de la nueva categoría:", key="input_nueva_cat")
            
            if st.button("Guardar Categoría", type="primary"):
                if nueva_cat.strip() != "":
                    cat_limpia = nueva_cat.strip().lower()
                    
                    # --- PASO 1: AGREGAR A LA MEMORIA LOCAL AL INSTANTE (Optimista) ---
                    if "lista_categorias" in st.session_state:
                        st.session_state.lista_categorias.append({"nombre": cat_limpia})
                    
                    st.toast(f"¡Categoría '{nueva_cat}' creada con éxito! 🎉")
                    
                    # --- PASO 2: HACER EL PROCESO PESADO CON RENDER ---
                    conexion = conseguir_conexion()
                    try:
                        cursor = conexion.cursor()
                        cursor.execute("INSERT INTO categorias (nombre) VALUES (%s);", (cat_limpia,))
                        conexion.commit()
                        cursor.close()
                        conexion.close()
                        st.rerun()
                    except Exception as e:
                        if "lista_categorias" in st.session_state:
                            st.session_state.lista_categorias = [c for c in st.session_state.lista_categorias if c["nombre"] != cat_limpia]
                        st.error("⚠️ Esa categoría ya existe en el sistema.")
                else:
                    st.warning("Por favor, escribe un nombre válido.")
                    
        with col_ver:
            st.subheader("Categorías Actuales")
            conexion = conseguir_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT * FROM categorias ORDER BY nombre;")
                lista_cats = cursor.fetchall()
                cursor.close()
                conexion.close()
                for c in lista_cats:
                    st.text(f"📁 [{c['id']}] - {c['nombre']}")