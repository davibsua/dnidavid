from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NumeroForm, Fecha
import os
import hashlib
import datetime
from django.conf import settings

# Ruta del archivo que almacena usuarios
USER_FILE = "usuarios.txt"

# Función para encriptar contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Función para verificar contraseñas
def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# Función para crear la carpeta y los archivos asociados a un usuario
def crear_estructura_usuario(usuario):
    user_folder = f"usuarios/{usuario}"
    os.makedirs(user_folder, exist_ok=True)
    cuenta_path = os.path.join(user_folder, "cuenta.txt")
    movimientos_path = os.path.join(user_folder, "movimientos.txt")

    if not os.path.exists(cuenta_path):
        with open(cuenta_path, "w") as cuenta:
            cuenta.write("0.0")  # Saldo inicial

    if not os.path.exists(movimientos_path):
        with open(movimientos_path, "w") as movimientos:
            movimientos.write("")  # Archivo vacío para movimientos

# Función para obtener el saldo del usuario
def obtener_saldo(usuario):
    cuenta_path = f"usuarios/{usuario}/cuenta.txt"
    with open(cuenta_path, "r") as cuenta:
        return float(cuenta.read().strip())

# Función para actualizar el saldo
def actualizar_saldo(usuario, nuevo_saldo):
    cuenta_path = f"usuarios/{usuario}/cuenta.txt"
    with open(cuenta_path, "w") as cuenta:
        cuenta.write(str(nuevo_saldo))

# Función para registrar movimientos
def registrar_movimiento(usuario, movimiento):
    movimientos_path = f"usuarios/{usuario}/movimientos.txt"
    with open(movimientos_path, "a") as movimientos:
        movimientos.write(f"{movimiento}\n")

# Función para validar fechas
def validar_fecha_programada(fecha):
    hoy = datetime.datetime.now().date()
    return hoy == fecha

# Vista para el índice
def index(request):
    usuario = request.session.get("usuario")
    if not usuario:
        return redirect("login")

    saldo = obtener_saldo(usuario)
    return render(request, "index.html", {"saldo": saldo})

# Vista para ingresar dinero
def ingreso(request):
    usuario = request.session.get("usuario")
    if not usuario:
        return redirect("login")

    if request.method == "POST":
        form = NumeroForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data["numero"]
            saldo_actual = obtener_saldo(usuario)
            nuevo_saldo = saldo_actual + monto
            actualizar_saldo(usuario, nuevo_saldo)
            registrar_movimiento(usuario, f"Ingreso: +{monto}")
            return render(request, "ingreso.html", {"form": form, "saldo_nuevo": nuevo_saldo})
    else:
        form = NumeroForm()

    return render(request, "ingreso.html", {"form": form})

# Vista para ingreso programado
def ingreso_programado(request):
    usuario = request.session.get("usuario")
    if not usuario:
        return redirect("login")

    if request.method == "POST":
        form = Fecha(request.POST)
        if form.is_valid():
            fecha_programada = form.cleaned_data["fecha"]
            if validar_fecha_programada(fecha_programada):
                mform = NumeroForm(request.POST)
                if mform.is_valid():
                    monto = mform.cleaned_data["numero"]
                    saldo_actual = obtener_saldo(usuario)
                    nuevo_saldo = saldo_actual + monto
                    actualizar_saldo(usuario, nuevo_saldo)
                    registrar_movimiento(usuario, f"{datetime.datetime.now()} Ingreso programado: +{monto}")
                    return render(request, "ingreso_programado.html", {
                        "form": form, "mform": mform, "nuevo_saldo": nuevo_saldo
                    })
            else:
                return render(request, "ingreso_programado.html", {
                    "form": form, "error": "La fecha programada no coincide con hoy."
                })
    else:
        form = Fecha()

    return render(request, "ingreso_programado.html", {"form": form})

# Vista para retiro programado
def retiro_programado(request):
    usuario = request.session.get("usuario")
    if not usuario:
        return redirect("login")

    if request.method == "POST":
        form = Fecha(request.POST)
        if form.is_valid():
            fecha_programada = form.cleaned_data["fecha"]
            if validar_fecha_programada(fecha_programada):
                mform = NumeroForm(request.POST)
                if mform.is_valid():
                    monto = mform.cleaned_data["numero"]
                    saldo_actual = obtener_saldo(usuario)
                    if saldo_actual >= monto:
                        nuevo_saldo = saldo_actual - monto
                        actualizar_saldo(usuario, nuevo_saldo)
                        registrar_movimiento(usuario, f"{datetime.datetime.now()} Retiro programado: -{monto}")
                        return render(request, "retiro_programado.html", {
                            "form": form, "mform": mform, "nuevo_saldo": nuevo_saldo
                        })
                    else:
                        return render(request, "retiro_programado.html", {
                            "form": form, "mform": mform, "error": "Saldo insuficiente."
                        })
            else:
                return render(request, "retiro_programado.html", {
                    "form": form, "error": "La fecha programada no coincide con hoy."
                })
    else:
        form = Fecha()

    return render(request, "retiro_programado.html", {"form": form})

# Vista para retirar dinero
def retiro(request):
    usuario = request.session.get("usuario")
    if not usuario:
        return redirect("login")

    if request.method == "POST":
        form = NumeroForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data["numero"]
            saldo_actual = obtener_saldo(usuario)
            if saldo_actual >= monto:
                nuevo_saldo = saldo_actual - monto
                actualizar_saldo(usuario, nuevo_saldo)
                registrar_movimiento(usuario, f"Retiro: -{monto}")
                return render(request, "retiro.html", {"form": form, "saldo_nuevo": nuevo_saldo})
            else:
                return render(request, "retiro.html", {"form": form, "error": "Saldo insuficiente"})
    else:
        form = NumeroForm()

    return render(request, "retiro.html", {"form": form})

# Vista para mostrar movimientos
def movimientos(request):
    usuario = request.session.get('usuario')
    if usuario:
        archivo_movimientos = os.path.join(settings.BASE_DIR, 'usuarios', usuario, 'movimientos.txt')
        if os.path.exists(archivo_movimientos):
            with open(archivo_movimientos, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
    else:
        lines = []

    return render(request, 'movimientos.html', {'lines': lines})

def media(request):
    ingresos = []
    retiros = []
    usuario = request.session.get('usuario')

    if not usuario:
        return redirect("login")

    archivo_movimientos = os.path.join(settings.BASE_DIR, 'usuarios', usuario, 'movimientos.txt')

    if os.path.exists(archivo_movimientos):
        with open(archivo_movimientos, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.lower().startswith("ingreso:"):
                    try:
                        monto = float(line.split("+")[1])
                        ingresos.append(monto)
                    except (IndexError, ValueError):
                        continue  
                elif line.lower().startswith("retiro:"):
                    try:
                        monto = float(line.split("-")[1])
                        retiros.append(monto)
                    except (IndexError, ValueError):
                        continue  # Saltar líneas mal formateadas

    # Calcular estadísticas
    total_ingresos = sum(ingresos)
    total_retiros = sum(retiros)
    numi = len(ingresos)
    numr = len(retiros)

    media_ingresos = total_ingresos / numi if numi > 0 else 0
    media_retiros = total_retiros / numr if numr > 0 else 0

    total_movimientos = numi + numr
    percentage_numi = (numi / total_movimientos * 100) if total_movimientos > 0 else 0
    percentage_numr = (numr / total_movimientos * 100) if total_movimientos > 0 else 0

    return render(request, "datos.html", {
        "media_ingresos": round(media_ingresos, 2),
        "media_retiros": round(media_retiros, 2),
        "numi": numi,
        "numr": numr,
        "percentage_numi": f"{round(percentage_numi)}%",
        "percentage_numr": f"{round(percentage_numr)}%",
        "movimientos": total_movimientos,
    })

# Vista para el registro
def registro(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contrasena = request.POST.get("contrasena")

        if not usuario or not contrasena:
            return render(request, "registro.html", {"error": "Por favor, complete todos los campos."})

        with open(USER_FILE, "r") as user_file:
            usuarios = [linea.split(",")[0] for linea in user_file.readlines()]

        if usuario in usuarios:
            return render(request, "registro.html", {"error": "El usuario ya existe."})

        hashed_password = hash_password(contrasena)
        with open(USER_FILE, "a") as user_file:
            user_file.write(f"{usuario},{hashed_password}\n")

        crear_estructura_usuario(usuario)
        return redirect("login")

    return render(request, "registro.html")

# Vista para el login
def login(request):
    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contrasena = request.POST.get("contrasena")

        if not usuario or not contrasena:

            return render(request, "login.html", {"error": "Por favor, rellena todos los campos"})

        with open(USER_FILE, "r") as user_file:
            usuarios = user_file.readlines()

        for linea in usuarios:
            try:
                stored_user, stored_pass = linea.strip().split(",")
                if stored_user == usuario and verify_password(stored_pass, contrasena):
                    request.session["usuario"] = usuario
                    return redirect("index")
            except ValueError:
                continue

        return render(request, "login.html", {"error": "Usuario o contraseña incorrectos"})

    return render(request, "login.html")

# Vista para cerrar sesión
def logout(request):
    request.session.flush()
    return redirect("login")


# Vista para generar el histórico y mostrar gráficos
def historico_grafico(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect("login")

    archivo_movimientos = os.path.join(settings.BASE_DIR, 'usuarios', usuario, 'movimientos.txt')
    historico = []
    saldo_actual = 0

    if os.path.exists(archivo_movimientos):
        with open(archivo_movimientos, 'r') as file:
            for linea in file:
                linea = linea.strip()
                if linea.lower().startswith("ingreso:"):
                    try:
                        monto = float(linea.split("+")[1])
                        saldo_actual += monto
                    except (IndexError, ValueError):
                        continue
                elif linea.lower().startswith("retiro:"):
                    try:
                        monto = float(linea.split("-")[1])
                        saldo_actual -= monto
                    except (IndexError, ValueError):
                        continue
                historico.append(saldo_actual)

    return render(request, "datos.html", {"historico": historico})


def datos(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect("login")

    movimientos_path = os.path.join(settings.BASE_DIR, 'usuarios', usuario, 'movimientos.txt')
    saldo_path = os.path.join(settings.BASE_DIR, 'usuarios', usuario, 'cuenta.txt')

    historico = []
    saldo_actual = 0

    if os.path.exists(movimientos_path) and os.path.exists(saldo_path):
        with open(movimientos_path, 'r') as movimientos_file:
            movimientos = movimientos_file.readlines()

        saldo_actual = float(open(saldo_path, 'r').read().strip())

        for movimiento in movimientos:
            if movimiento.lower().startswith("ingreso:"):
                cantidad = float(movimiento.split("+")[1])
                saldo_actual += cantidad
            elif movimiento.lower().startswith("retiro:"):
                cantidad = float(movimiento.split("-")[1])
                saldo_actual -= cantidad

            historico.append(saldo_actual)  # Registro histórico tras cada movimiento.

    return render(request, "datos.html", {"historico": historico})
