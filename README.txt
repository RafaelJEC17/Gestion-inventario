# Sistema de Gestión de Inventario (Backend API)

Este es un proyecto backend sencillo pero estructurado, ideal para la gestión local del inventario de un negocio. Permite administrar categorías y productos mediante una API REST conectada a una base de datos relacional.

## 🚀 Tecnologías Utilizadas
* **Python** (Lenguaje principal)
* **FastAPI** (Framework ágil para la creación de la API)
* **PostgreSQL** (Base de datos relacional)
* **Psycopg3** (Conector nativo entre Python y PostgreSQL)

## 📊 Diseño de la Base de Datos
El proyecto utiliza un modelo relacional de dos tablas con integridad referencial (`FOREIGN KEY` y `ON DELETE SET NULL`):
* `categorias`: Almacena las secciones del inventario.
* `productos`: Registra los artículos, precios, stock disponible y su categoría correspondiente.

## 🛠️ Cómo Ejecutar el Proyecto Localmente

1. **Clonar el repositorio:**
   ```bash
   git clone <LINK_DE_TU_REPOSITORIO>
   cd inventario-backend