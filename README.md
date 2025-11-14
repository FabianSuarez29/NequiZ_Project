# 💸 Nequi - Microservicio de Transacciones

Aplicación web que simula el sistema de transacciones de Nequi usando Python Flask.

## 📋 Características

- ✅ Transacciones entre usuarios registrados
- ✅ Validación de saldo y datos
- ✅ Historial completo de transacciones
- ✅ Interface web intuitiva
- ✅ Base de datos SQLite
- ✅ API REST completa

## 🚀 Instalación

### 1. Crear estructura de carpetas

```
nequi_app/
│
├── app.py
├── requirements.txt
└── templates/
    └── index.html
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://127.0.0.1:5000**

## 👥 Usuarios Pre-registrados

La aplicación incluye 2 usuarios de prueba:

| Nombre | Número de Celular | Saldo Inicial |
|--------|-------------------|---------------|
| Juan Pérez | 3001234567 | $500,000 |
| María García | 3009876543 | $750,000 |

## 🔌 API Endpoints

### 1. Obtener todos los usuarios
```http
GET /api/usuarios
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "numero_celular": "3001234567",
    "saldo": "$500,000.00",
    "fecha_registro": "2024-01-15 10:30:00"
  }
]
```

### 2. Obtener usuario específico
```http
GET /api/usuario/<numero_celular>
```

**Ejemplo:**
```http
GET /api/usuario/3001234567
```

### 3. Realizar transacción
```http
POST /api/transaccion
Content-Type: application/json

{
  "numero_origen": "3001234567",
  "numero_destino": "3009876543",
  "monto": 50000,
  "mensaje": "Pago de almuerzo"
}
```

**Respuesta exitosa:**
```json
{
  "mensaje": "Transacción exitosa",
  "transaccion_id": 1,
  "numero_origen": "3001234567",
  "numero_destino": "3009876543",
  "monto": "$50,000.00",
  "nuevo_saldo_origen": "$450,000.00",
  "nuevo_saldo_destino": "$800,000.00",
  "fecha": "2024-01-15 14:30:00"
}
```

### 4. Obtener todas las transacciones
```http
GET /api/transacciones
```

### 5. Obtener transacciones de un usuario
```http
GET /api/transacciones/<numero_celular>
```

## ✅ Validaciones Implementadas

- ✅ Número de celular obligatorio
- ✅ Monto obligatorio y mayor a cero
- ✅ Verificación de saldo suficiente
- ✅ Validación de usuario origen y destino
- ✅ Prevención de auto-transferencias
- ✅ Formato de número de celular (10 dígitos)

## 🧪 Pruebas de Transacciones

### Ejemplo 1: Transacción exitosa
```bash
curl -X POST http://127.0.0.1:5000/api/transaccion \
  -H "Content-Type: application/json" \
  -d '{
    "numero_origen": "3001234567",
    "numero_destino": "3009876543",
    "monto": 50000,
    "mensaje": "Préstamo"
  }'
```

### Ejemplo 2: Verificar saldo después de transacción
```bash
curl http://127.0.0.1:5000/api/usuario/3001234567
```

### Ejemplo 3: Ver historial de transacciones
```bash
curl http://127.0.0.1:5000/api/transacciones/3001234567
```

## 📊 Base de Datos

La aplicación utiliza SQLite con las siguientes tablas:

### Tabla: usuarios
- `id`: INTEGER PRIMARY KEY
- `nombre`: TEXT
- `numero_celular`: TEXT UNIQUE
- `saldo`: REAL
- `fecha_registro`: TEXT

### Tabla: transacciones
- `id`: INTEGER PRIMARY KEY
- `numero_origen`: TEXT
- `numero_destino`: TEXT
- `monto`: REAL
- `mensaje`: TEXT
- `fecha`: TEXT
- `estado`: TEXT

## 🎯 Próximas Funcionalidades (Fase 2)

- Sistema de autenticación y login
- Registro de nuevos usuarios
- Recarga de saldo
- Retiro de dinero
- Historial con filtros avanzados
- Notificaciones de transacciones
- QR para pagos rápidos

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.x + Flask
- **Base de Datos:** SQLite
- **Frontend:** HTML5 + CSS3 + JavaScript Vanilla
- **API:** REST

## 📝 Notas Importantes

- La base de datos se crea automáticamente al ejecutar la aplicación
- Los usuarios de prueba se insertan solo la primera vez
- Todas las transacciones quedan registradas en la base de datos
- La aplicación actualiza los saldos automáticamente cada 5 segundos

## 🔒 Seguridad

Esta es una versión de desarrollo. Para producción se recomienda:
- Implementar autenticación JWT
- Usar variables de entorno
- Cifrar contraseñas
- Implementar rate limiting
- Usar HTTPS
- Validar inputs en backend y frontend

## 📞 Soporte

Para consultas o reportar problemas, contacta al equipo de desarrollo.
