# servidor_web.py
from flask import Flask, jsonify, render_template_string, request, redirect, url_for, session
from datetime import datetime
import os
import sys
from pathlib import Path
from supabase import create_client, Client
from supabase_config import SUPABASE_URL, SUPABASE_KEY

app = Flask(__name__)
app.secret_key = 'MI_CLAVE_SECRETA_12345'

# CONTRASEÑA DE ACCESO AL PANEL WEB (cámbiala si quieres)
CONTRASENA = "TECNO2024"

# Cliente de Supabase (global)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# PANTALLA DE LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        clave = request.form.get('clave')
        if clave == CONTRASENA:
            session['logueado'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Contraseña incorrecta'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TECNOBOTS - Acceso</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
            }
            .login-box {
                background: white;
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                width: 90%;
                max-width: 350px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 { color: #667eea; margin-bottom: 10px; }
            input {
                width: 100%;
                padding: 12px;
                margin: 15px 0;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
            }
            button:hover { background: #764ba2; }
            .error { color: red; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🔐 TECNOBOTS</h1>
            <p>Ingrese la contraseña</p>
            <form method="POST">
                <input type="password" name="clave" placeholder="Contraseña" autofocus>
                <button type="submit">ACCEDER</button>
            </form>
            ''' + (f'<div class="error">{error}</div>' if error else '') + '''
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.pop('logueado', None)
    return redirect(url_for('login'))

def requiere_login(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorador

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/dashboard')
@requiere_login
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TECNOBOTS - Panel</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }
            .container { max-width: 1400px; margin: 0 auto; }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            h1 { color: white; }
            .logout-btn {
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                text-decoration: none;
                border: 1px solid white;
            }
            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
            .card .valor { font-size: 28px; font-weight: bold; color: #667eea; }
            .section {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                overflow-x: auto;
            }
            .section h2 { margin-bottom: 15px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; font-size: 14px; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #667eea; color: white; }
            tr:hover { background: #f5f5f5; }
            .stock-bajo { color: red; font-weight: bold; }
            .refresh-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            }
            .update-time { text-align: center; color: white; margin-top: 20px; font-size: 12px; }
            @media (max-width: 600px) {
                body { padding: 10px; }
                .card .valor { font-size: 20px; }
                table { font-size: 11px; }
                th, td { padding: 6px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 TECNOBOTS</h1>
                <a href="/logout" class="logout-btn">🚪 Cerrar Sesión</a>
            </div>
            
            <div class="dashboard">
                <div class="card"><h3>💰 EFECTIVO</h3><div class="valor" id="efectivo">$0</div></div>
                <div class="card"><h3>📦 MERCANCÍA</h3><div class="valor" id="mercancia">$0</div></div>
                <div class="card"><h3>🏪 ALMACÉN (Pendiente)</h3><div class="valor" id="almacen">$0</div></div>
                <div class="card"><h3>🆕 PRODUCTOS NUEVOS</h3><div class="valor" id="productos_nuevos">$0</div></div>
                <div class="card"><h3>⚠️ CRÉDITOS PENDIENTES</h3><div class="valor" id="creditos">$0</div></div>
                <div class="card"><h3>📊 VENTAS HOY</h3><div class="valor" id="ventas_hoy">$0</div></div>
                <div class="card"><h3>📈 VENTAS MES</h3><div class="valor" id="ventas_mes">$0</div></div>
                <div class="card"><h3>🏦 CAPITAL NETO</h3><div class="valor" id="capital">$0</div></div>
            </div>
            
            <div class="section">
                <h2>📋 ÚLTIMAS VENTAS</h2>
                <table id="tabla_ventas"><thead><tr><th>#</th><th>Cliente</th><th>Total</th><th>Estado</th><th>Abono</th><th>Pendiente</th><th>Fecha</th></tr></thead><tbody><tr><td colspan="7">Cargando...</td></tr></tbody></table>
            </div>
            
            <div class="section">
                <h2>📦 INVENTARIO</h2>
                <table id="tabla_inventario"><thead><tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Valor Total</th></tr></thead><tbody><tr><td colspan="4">Cargando...</td></tr></tbody></table>
            </div>
            
            <div class="section">
                <h2>💸 GASTOS RECIENTES</h2>
                <table id="tabla_gastos"><thead><tr><th>Descripción</th><th>Monto</th><th>Fecha</th></tr></thead><tbody><tr><td colspan="3">Cargando...</td></tr></tbody></table>
            </div>
            
            <div class="update-time" id="update_time"></div>
        </div>
        <button class="refresh-btn" onclick="cargarTodo()">🔄</button>
        
        <script>
            function cargarTodo() {
                fetch('/api/resumen').then(r=>r.json()).then(d=>{
                    document.getElementById('efectivo').innerHTML = '$'+d.efectivo.toFixed(2);
                    document.getElementById('mercancia').innerHTML = '$'+d.mercancia.toFixed(2);
                    document.getElementById('almacen').innerHTML = '$'+d.total_almacen.toFixed(2);
                    document.getElementById('productos_nuevos').innerHTML = '$'+d.total_productos_nuevos.toFixed(2);
                    document.getElementById('creditos').innerHTML = '$'+d.creditos_pendientes.toFixed(2);
                    document.getElementById('ventas_hoy').innerHTML = '$'+d.ventas_hoy.toFixed(2);
                    document.getElementById('ventas_mes').innerHTML = '$'+d.ventas_mes.toFixed(2);
                    document.getElementById('capital').innerHTML = '$'+d.capital_neto.toFixed(2);
                });
                
                fetch('/api/ventas').then(r=>r.json()).then(v=>{
                    let html = '';
                    v.forEach(v=>{
                        html += `<tr><td>${v.numero}</td><td>${v.cliente}</td><td>$${v.total.toFixed(2)}</td><td>${v.estado}</td><td>$${v.abono.toFixed(2)}</td><td>$${v.pendiente.toFixed(2)}</td><td>${new Date(v.fecha).toLocaleString()}</td></tr>`;
                    });
                    document.getElementById('tabla_ventas').innerHTML = '<thead><tr><th>#</th><th>Cliente</th><th>Total</th><th>Estado</th><th>Abono</th><th>Pendiente</th><th>Fecha</th></tr></thead><tbody>' + (html || '<tr><td colspan="7">Sin ventas</td></tr>') + '</tbody>';
                });
                
                fetch('/api/inventario').then(r=>r.json()).then(i=>{
                    let html = '';
                    i.forEach(p=>{
                        let clase = p.cantidad <= 2 ? 'class="stock-bajo"' : '';
                        html += `<tr><td>${p.nombre}</td><td ${clase}>${p.cantidad}</td><td>$${p.precio_venta.toFixed(2)}</td><td>$${p.valor_total.toFixed(2)}</td></tr>`;
                    });
                    document.getElementById('tabla_inventario').innerHTML = '<thead><tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Valor Total</th></tr></thead><tbody>' + (html || '<tr><td colspan="4">Sin productos</td></tr>') + '</tbody>';
                });
                
                fetch('/api/gastos').then(r=>r.json()).then(g=>{
                    let html = '';
                    g.forEach(g=>{
                        html += `<tr><td>${g.descripcion}</td><td>$${g.monto.toFixed(2)}</td><td>${new Date(g.fecha).toLocaleString()}</td></tr>`;
                    });
                    document.getElementById('tabla_gastos').innerHTML = '<thead><tr><th>Descripción</th><th>Monto</th><th>Fecha</th></tr></thead><tbody>' + (html || '<tr><td colspan="3">Sin gastos</td></tr>') + '</tbody>';
                });
                
                document.getElementById('update_time').innerHTML = '🔄 Actualizado: ' + new Date().toLocaleString();
            }
            
            cargarTodo();
            setInterval(cargarTodo, 30000);
        </script>
    </body>
    </html>
    '''

# API para resumen financiero completo (desde Supabase)
@app.route('/api/resumen')
@requiere_login
def api_resumen():
    # Mercancía
    res_merc = supabase.table("productos").select("cantidad, precio_venta").execute()
    mercancia = sum(p["cantidad"] * p["precio_venta"] for p in res_merc.data) if res_merc.data else 0

    # Efectivo
    res_ventas = supabase.table("ventas").select("abono").execute()
    ventas_pagadas = sum(v["abono"] for v in res_ventas.data) if res_ventas.data else 0

    res_inc = supabase.table("incrementos_efectivo").select("monto").execute()
    incrementos = sum(i["monto"] for i in res_inc.data) if res_inc.data else 0

    res_gastos = supabase.table("gastos").select("monto").execute()
    gastos = sum(g["monto"] for g in res_gastos.data) if res_gastos.data else 0

    efectivo = ventas_pagadas + incrementos - gastos

    # Total en almacén (pendientes)
    res_almacen = supabase.table("registros_almacen").select("cantidad, precio_venta").eq("estado", "Pendiente").execute()
    total_almacen = sum(a["cantidad"] * a["precio_venta"] for a in res_almacen.data) if res_almacen.data else 0

    # Total en productos nuevos pendientes
    res_nuevos = supabase.table("productos_nuevos").select("cantidad, precio_venta").eq("estado", "Pendiente").execute()
    total_productos_nuevos = sum(n["cantidad"] * n["precio_venta"] for n in res_nuevos.data) if res_nuevos.data else 0

    # Créditos pendientes
    res_creditos = supabase.table("ventas").select("total, abono").eq("estado", "Crédito").execute()
    creditos_pendientes = 0
    if res_creditos.data:
        for v in res_creditos.data:
            if v["abono"] < v["total"]:
                creditos_pendientes += v["total"] - v["abono"]

    # Capital neto (suma total)
    capital_neto = mercancia + efectivo + total_almacen + total_productos_nuevos + creditos_pendientes

    # Ventas de hoy y del mes
    hoy = datetime.now().strftime('%Y-%m-%d')
    res_hoy = supabase.table("ventas").select("total").gte("fecha_venta", hoy).lte("fecha_venta", hoy + " 23:59:59").execute()
    ventas_hoy = sum(v["total"] for v in res_hoy.data) if res_hoy.data else 0

    mes_actual = datetime.now().strftime('%Y-%m')
    res_mes = supabase.table("ventas").select("total").gte("fecha_venta", mes_actual + "-01").execute()
    ventas_mes = sum(v["total"] for v in res_mes.data) if res_mes.data else 0

    return jsonify({
        'mercancia': mercancia,
        'efectivo': efectivo,
        'total_almacen': total_almacen,
        'total_productos_nuevos': total_productos_nuevos,
        'creditos_pendientes': creditos_pendientes,
        'capital_neto': capital_neto,
        'ventas_hoy': ventas_hoy,
        'ventas_mes': ventas_mes
    })

# API para últimas ventas (desde Supabase)
@app.route('/api/ventas')
@requiere_login
def api_ventas():
    result = supabase.table("ventas").select("numero_venta, total, fecha_venta, estado, abono, cliente").order("fecha_venta", desc=True).limit(50).execute()
    ventas = []
    for v in result.data:
        ventas.append({
            'numero': v["numero_venta"],
            'total': v["total"],
            'fecha': v["fecha_venta"],
            'estado': v["estado"],
            'abono': v["abono"],
            'cliente': v["cliente"] or "Consumidor",
            'pendiente': v["total"] - v["abono"] if v["estado"] == "Crédito" else 0
        })
    return jsonify(ventas)

# API para inventario (desde Supabase)
@app.route('/api/inventario')
@requiere_login
def api_inventario():
    result = supabase.table("productos").select("nombre, cantidad, precio_venta").order("nombre").execute()
    productos = []
    for p in result.data:
        productos.append({
            'nombre': p["nombre"],
            'cantidad': p["cantidad"],
            'precio_venta': p["precio_venta"],
            'valor_total': p["cantidad"] * p["precio_venta"]
        })
    return jsonify(productos)

# API para gastos recientes (desde Supabase)
@app.route('/api/gastos')
@requiere_login
def api_gastos():
    result = supabase.table("gastos").select("descripcion, monto, fecha").order("fecha", desc=True).limit(50).execute()
    gastos = []
    for g in result.data:
        gastos.append({
            'descripcion': g["descripcion"],
            'monto': g["monto"],
            'fecha': g["fecha"]
        })
    return jsonify(gastos)

def iniciar_servidor():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def iniciar_servidor_en_hilo():
    import threading
    hilo = threading.Thread(target=iniciar_servidor, daemon=True)
    hilo.start()
    return "http://localhost:5000"

if __name__ == '__main__':
    iniciar_servidor()