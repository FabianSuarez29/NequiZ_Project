from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)

# Configuración de la base de datos
DATABASE = 'nequi.db'

def get_db():
    """Conectar a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializar la base de datos con usuarios y tablas"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            numero_celular TEXT UNIQUE NOT NULL,
            saldo REAL DEFAULT 0,
            fecha_registro TEXT NOT NULL
        )
    ''')
    
    # Crear tabla de transacciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_origen TEXT NOT NULL,
            numero_destino TEXT NOT NULL,
            monto REAL NOT NULL,
            mensaje TEXT,
            fecha TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (numero_origen) REFERENCES usuarios (numero_celular),
            FOREIGN KEY (numero_destino) REFERENCES usuarios (numero_celular)
        )
    ''')
    
    # Verificar si ya existen usuarios
    cursor.execute('SELECT COUNT(*) as count FROM usuarios')
    count = cursor.fetchone()[0]
    
    # Insertar usuarios de prueba solo si no existen
    if count == 0:
        usuarios_prueba = [
            ('Andres Gerena', '3001234567', 500000.00),
            ('Fabian Suarez', '3009876543', 750000.00),
            ('Camila Mosquera', '3108556655', 10000.00)
        ]
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for nombre, celular, saldo in usuarios_prueba:
            cursor.execute('''
                INSERT INTO usuarios (nombre, numero_celular, saldo, fecha_registro)
                VALUES (?, ?, ?, ?)
            ''', (nombre, celular, saldo, fecha_actual))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    """Obtener todos los usuarios"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()
    
    usuarios_list = []
    for usuario in usuarios:
        usuarios_list.append({
            'id': usuario['id'],
            'nombre': usuario['nombre'],
            'numero_celular': usuario['numero_celular'],
            'saldo': f"${usuario['saldo']:,.2f}",
            'fecha_registro': usuario['fecha_registro']
        })
    
    return jsonify(usuarios_list)

@app.route('/api/usuario/<numero_celular>', methods=['GET'])
def obtener_usuario(numero_celular):
    """Obtener información de un usuario específico"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE numero_celular = ?', (numero_celular,))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        return jsonify({
            'id': usuario['id'],
            'nombre': usuario['nombre'],
            'numero_celular': usuario['numero_celular'],
            'saldo': usuario['saldo'],
            'saldo_formateado': f"${usuario['saldo']:,.2f}",
            'fecha_registro': usuario['fecha_registro']
        })
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/api/transaccion', methods=['POST'])
def realizar_transaccion():
    """Realizar una transacción entre usuarios"""
    data = request.get_json()
    
    # Validar datos requeridos
    numero_origen = data.get('numero_origen')
    numero_destino = data.get('numero_destino')
    monto = data.get('monto')
    mensaje = data.get('mensaje', '')
    
    if not numero_origen or not numero_destino or not monto:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    try:
        monto = float(monto)
        if monto <= 0:
            return jsonify({'error': 'El monto debe ser mayor a cero'}), 400
    except ValueError:
        return jsonify({'error': 'Monto inválido'}), 400
    
    if numero_origen == numero_destino:
        return jsonify({'error': 'No puedes enviarte dinero a ti mismo'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Verificar usuario origen
        cursor.execute('SELECT * FROM usuarios WHERE numero_celular = ?', (numero_origen,))
        usuario_origen = cursor.fetchone()
        
        if not usuario_origen:
            return jsonify({'error': 'Usuario origen no encontrado'}), 404
        
        # Verificar usuario destino
        cursor.execute('SELECT * FROM usuarios WHERE numero_celular = ?', (numero_destino,))
        usuario_destino = cursor.fetchone()
        
        if not usuario_destino:
            return jsonify({'error': 'Usuario destino no encontrado'}), 404
        
        # Verificar saldo suficiente
        if usuario_origen['saldo'] < monto:
            return jsonify({'error': 'Saldo insuficiente'}), 400
        
        # Realizar la transacción
        nuevo_saldo_origen = usuario_origen['saldo'] - monto
        nuevo_saldo_destino = usuario_destino['saldo'] + monto
        
        cursor.execute('UPDATE usuarios SET saldo = ? WHERE numero_celular = ?', 
                      (nuevo_saldo_origen, numero_origen))
        cursor.execute('UPDATE usuarios SET saldo = ? WHERE numero_celular = ?', 
                      (nuevo_saldo_destino, numero_destino))
        
        # Registrar la transacción
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO transacciones (numero_origen, numero_destino, monto, mensaje, fecha, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (numero_origen, numero_destino, monto, mensaje, fecha_actual, 'EXITOSA'))
        
        transaccion_id = cursor.lastrowid
        
        conn.commit()
        
        return jsonify({
            'mensaje': 'Transacción exitosa',
            'transaccion_id': transaccion_id,
            'numero_origen': numero_origen,
            'numero_destino': numero_destino,
            'monto': f"${monto:,.2f}",
            'nuevo_saldo_origen': f"${nuevo_saldo_origen:,.2f}",
            'nuevo_saldo_destino': f"${nuevo_saldo_destino:,.2f}",
            'fecha': fecha_actual
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Error en la transacción: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/transacciones', methods=['GET'])
def obtener_transacciones():
    """Obtener todas las transacciones"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, 
               u1.nombre as nombre_origen,
               u2.nombre as nombre_destino
        FROM transacciones t
        JOIN usuarios u1 ON t.numero_origen = u1.numero_celular
        JOIN usuarios u2 ON t.numero_destino = u2.numero_celular
        ORDER BY t.fecha DESC
    ''')
    transacciones = cursor.fetchall()
    conn.close()
    
    transacciones_list = []
    for trans in transacciones:
        transacciones_list.append({
            'id': trans['id'],
            'numero_origen': trans['numero_origen'],
            'nombre_origen': trans['nombre_origen'],
            'numero_destino': trans['numero_destino'],
            'nombre_destino': trans['nombre_destino'],
            'monto': f"${trans['monto']:,.2f}",
            'mensaje': trans['mensaje'],
            'fecha': trans['fecha'],
            'estado': trans['estado']
        })
    
    return jsonify(transacciones_list)

@app.route('/api/transacciones/<numero_celular>', methods=['GET'])
def obtener_transacciones_usuario(numero_celular):
    """Obtener transacciones de un usuario específico"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, 
               u1.nombre as nombre_origen,
               u2.nombre as nombre_destino
        FROM transacciones t
        JOIN usuarios u1 ON t.numero_origen = u1.numero_celular
        JOIN usuarios u2 ON t.numero_destino = u2.numero_celular
        WHERE t.numero_origen = ? OR t.numero_destino = ?
        ORDER BY t.fecha DESC
    ''', (numero_celular, numero_celular))
    transacciones = cursor.fetchall()
    conn.close()
    
    transacciones_list = []
    for trans in transacciones:
        tipo = 'ENVIADO' if trans['numero_origen'] == numero_celular else 'RECIBIDO'
        transacciones_list.append({
            'id': trans['id'],
            'tipo': tipo,
            'numero_origen': trans['numero_origen'],
            'nombre_origen': trans['nombre_origen'],
            'numero_destino': trans['numero_destino'],
            'nombre_destino': trans['nombre_destino'],
            'monto': f"${trans['monto']:,.2f}",
            'mensaje': trans['mensaje'],
            'fecha': trans['fecha'],
            'estado': trans['estado']
        })
    
    return jsonify(transacciones_list)

if __name__ == '__main__':
    # Inicializar la base de datos
    init_db()
    print("=" * 50)
    print("NEQUI - Microservicio de Transacciones")
    print("=" * 50)
    print("\nUsuarios registrados:")
    print("1. Andres Gerena - 3001234567 - Saldo: $1,000,000")
    print("2. Fabian Suarez - 3009876543 - Saldo: $900,000")
    print("3. Camila Mosquera- 3108556655 - Saldo: $750,000")
    print("\nServidor iniciado en: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
