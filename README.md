# 🤖 Asistente de Contenido para TikTok

Un bot de Telegram inteligente que genera ideas de contenido para TikTok usando IA (Google Gemini), con gestión de categorías y soporte multiidioma (español e inglés).

## 📁 Estructura del Proyecto

```
Asistente/
├── app.py                  # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── .env                    # Variables de entorno (configurar)
├── README.md              # Documentación del proyecto
├── db/
│   └── db.sql             # Estructura de la base de datos
├── env/                   # Entorno virtual
├── config/
│   ├── __init__.py
│   └── config.py          # Configuración centralizada
├── database/
│   ├── __init__.py
│   └── database.py        # Manejo de base de datos MySQL
├── services/
│   ├── __init__.py
│   ├── ai_generator.py    # Generador de contenido con Google Gemini
│   └── content_manager.py # Gestor de contenido y operaciones
├── controllers/
│   ├── __init__.py
│   └── access_controller.py # Control de acceso de usuarios
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py    # Lógica del bot de Telegram
└── telegram/
    └── telegram_bot.py    # (duplicado, revisar)
```

## 🛠️ Tecnologías Utilizadas

- **Python 3.13+**
- **Telegram Bot API** - Interfaz del bot
- **Google Gemini AI** - Generación de contenido
- **MySQL** - Base de datos
- **python-dotenv** - Gestión de variables de entorno
- **mysql-connector-python** - Conector MySQL

## 📋 Requisitos Previos

- Python 3.13 o superior
- MySQL Server
- Cuenta de Telegram Bot (obtener token de @BotFather)
- API Key de Google Gemini

## 🚀 Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/zamo23/contenido.git
   cd contenido
   ```

2. **Crea un entorno virtual:**
   ```bash
   python -m venv env
   # En Windows:
   env\Scripts\activate
   # En Linux/Mac:
   source env/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno:**
   Crea un archivo `.env` en la raíz del proyecto:
   ```env
   # Base de datos MySQL
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=tu_usuario_mysql
   DB_PASSWORD=tu_password_mysql
   DB_NAME=contenido

   # API de Google Gemini
   IA_GOOGLE=tu_api_key_de_google_gemini

   # Token del Bot de Telegram
   token_telegram=tu_token_de_telegram_bot
   ```

## 🗄️ Estructura de la Base de Datos

### Creación de la Base de Datos

Ejecuta el script `db/db.sql` en tu servidor MySQL para crear la base de datos y las tablas necesarias. El script crea la base de datos `contenido` con codificación UTF8MB4 para soporte completo de caracteres Unicode.

Alternativamente, puedes copiar y pegar el script SQL completo de la sección siguiente directamente en tu cliente MySQL.

### Tablas

#### 1. `users`
Almacena la información de los usuarios de Telegram que tienen acceso al bot.

```sql
CREATE TABLE users (
  id BIGINT(20) NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) DEFAULT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB;
```

**Campos:**
- `id`: ID único de Telegram (clave primaria, auto-incremental)
- `username`: Nombre de usuario de Telegram
- `created_at`: Fecha de creación del registro

#### 2. `content_ideas`
Almacena las ideas principales de contenido generadas por el bot.

```sql
CREATE TABLE content_ideas (
  id INT(11) NOT NULL AUTO_INCREMENT,
  user_id BIGINT(20) NOT NULL,
  category VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY user_id (user_id),
  CONSTRAINT fk_content_ideas_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

**Campos:**
- `id`: ID único de la idea (clave primaria, auto-incremental)
- `user_id`: ID del usuario que creó la idea (clave foránea)
- `category`: Categoría de la idea (ej: "cocina", "fitness", etc.)
- `created_at`: Fecha de creación de la idea

#### 3. `content_translations`
Almacena las traducciones de cada idea en diferentes idiomas.

```sql
CREATE TABLE content_translations (
  id INT(11) NOT NULL AUTO_INCREMENT,
  idea_id INT(11) NOT NULL,
  language ENUM('es','en') NOT NULL,
  title VARCHAR(255) NOT NULL,
  content LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (JSON_VALID(content)),
  hashtags TEXT DEFAULT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  video_prompts TEXT DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idea_id (idea_id),
  CONSTRAINT fk_content_translations_idea FOREIGN KEY (idea_id) REFERENCES content_ideas(id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

**Campos:**
- `id`: ID único de la traducción (clave primaria, auto-incremental)
- `idea_id`: ID de la idea relacionada (clave foránea)
- `language`: Idioma de la traducción ('es' para español, 'en' para inglés)
- `title`: Título de la idea en el idioma correspondiente
- `content`: Contenido de la idea en formato JSON (guion dividido en gancho, cuerpo, cierre) con validación JSON
- `hashtags`: Lista de hashtags relevantes
- `created_at`: Fecha de creación de la traducción
- `video_prompts`: Prompts para generación de videos relacionados

### Relaciones

- Un usuario puede tener múltiples ideas (`users` → `content_ideas`)
- Una idea puede tener múltiples traducciones (`content_ideas` → `content_translations`)
- Las eliminaciones en cascada mantienen la integridad referencial

### Script SQL Completo

Copia y pega el siguiente script en tu cliente MySQL para crear la base de datos completa:

```sql
CREATE DATABASE IF NOT EXISTS contenido CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE contenido;

-- Tabla de usuarios
CREATE TABLE users (
  id BIGINT(20) NOT NULL AUTO_INCREMENT,
  username VARCHAR(100) DEFAULT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

-- Tabla de ideas de contenido
CREATE TABLE content_ideas (
  id INT(11) NOT NULL AUTO_INCREMENT,
  user_id BIGINT(20) NOT NULL,
  category VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY user_id (user_id),
  CONSTRAINT fk_content_ideas_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla de traducciones de contenido
CREATE TABLE content_translations (
  id INT(11) NOT NULL AUTO_INCREMENT,
  idea_id INT(11) NOT NULL,
  language ENUM('es','en') NOT NULL,
  title VARCHAR(255) NOT NULL,
  content LONGTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (JSON_VALID(content)),
  hashtags TEXT DEFAULT NULL,
  created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  video_prompts TEXT DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idea_id (idea_id),
  CONSTRAINT fk_content_translations_idea FOREIGN KEY (idea_id) REFERENCES content_ideas(id) ON DELETE CASCADE
) ENGINE=InnoDB;

```

1. **Base de datos MySQL:**
   - Crea una base de datos llamada `contenido`
   - Ejecuta el script `db/db.sql`
   - Asegúrate de que las credenciales en `.env` sean correctas

2. **Bot de Telegram:**
   - Crea un bot con @BotFather en Telegram
   - Copia el token en la variable `token_telegram` del archivo `.env`

3. **Google Gemini:**
   - Obtén una API key de Google AI Studio
   - Configura la variable `IA_GOOGLE` en el archivo `.env`

## 🎯 Uso

1. **Inicia el bot:**
   ```bash
   python app.py
   ```

2. **Comandos disponibles:**
   - `/start` - Verificar acceso y mostrar menú principal
   - `/generar` - Generar nuevas ideas de contenido
   - `/help` - Mostrar ayuda

3. **Funcionalidades principales:**
   - ✅ Gestión de categorías de contenido
   - ✅ Generación automática de ideas con IA
   - ✅ Soporte multiidioma (español e inglés)
   - ✅ Gestión de usuarios con control de acceso
   - ✅ Almacenamiento persistente en base de datos

## 📝 Funcionalidades

### 🤖 Generación de Contenido
- Genera ideas originales para TikTok usando Google Gemini
- Contenido optimizado para videos de 30-45 segundos
- Estructura: Gancho → Cuerpo → Cierre
- Hashtags virales incluidos

### 🗂️ Gestión de Categorías
- Crear categorías personalizadas
- Organizar ideas por temas
- Listar y navegar categorías
- Editar y eliminar categorías

### 🌍 Soporte Multiidioma
- Generación automática en español e inglés
- Traducciones consistentes
- Hashtags adaptados por idioma

### 👥 Control de Acceso
- Sistema de usuarios autorizados
- Verificación de acceso por ID de Telegram
- Mensajes de error para usuarios no autorizados

## 🔧 Arquitectura

El proyecto sigue los principios SOLID:

- **Single Responsibility**: Cada clase tiene una responsabilidad única
- **Open/Closed**: Abierto para extensión, cerrado para modificación
- **Liskov Substitution**: Subtipos sustituibles
- **Interface Segregation**: Interfaces específicas
- **Dependency Inversion**: Dependencias de abstracciones

### Componentes Principales

1. **Config**: Gestión centralizada de configuraciones
2. **Database**: Operaciones con MySQL
3. **Services**: Lógica de negocio (AI, gestión de contenido)
4. **Controllers**: Control de acceso y validaciones
5. **Bot**: Interfaz de Telegram

## 📊 Estado del Proyecto

✅ **Completado:**
- Arquitectura modular siguiendo SOLID
- Generación de contenido con IA
- Base de datos MySQL
- Bot de Telegram funcional
- Soporte multiidioma
- Control de acceso

🔄 **En desarrollo:**
- [ ] Interfaz web de administración
- [ ] Análisis de rendimiento de contenido
- [ ] Integración con otras plataformas

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes preguntas o problemas:
1. Revisa la documentación
2. Verifica la configuración de las variables de entorno
3. Asegúrate de que la base de datos esté correctamente configurada
4. Revisa los logs del bot para errores

---

**Desarrollado con ❤️ para creadores de contenido**