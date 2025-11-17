from flask import Blueprint, render_template, jsonify, request
from .monitor import get_status

main = Blueprint('main', __name__)

@main.route('/')
def index():
    dados = get_status()
    return render_template('index.html', **dados)

@main.route('/status')
def status():
    return jsonify(get_status())

@main.route('/backup')
def backup():
    from .backup_new import criar_backup_novo
    resultado = criar_backup_novo()
    registrar_log(resultado)
    return resultado


@main.route('/logs')
def logs():
    try:
        with open('logs/monitor.log', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler logs: {str(e)}"

@main.route('/processos')
def processos():
    import psutil
    from psutil import AccessDenied, NoSuchProcess, ZombieProcess
    filtro = request.args.get('filtro', 'todos')
    nome = request.args.get('nome')
    pid = request.args.get('pid')
    lista = []

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            info['cpu_percent'] = info.get('cpu_percent', 0.0) or 0.0
            info['memory_percent'] = info.get('memory_percent', 0.0) or 0.0
            lista.append(info)
        except (AccessDenied, NoSuchProcess, ZombieProcess):
            continue

    if pid:
        lista = [p for p in lista if str(p['pid']) == pid]
    elif nome:
        lista = [p for p in lista if nome.lower() in p['name'].lower()]
    elif filtro == 'memoria':
        lista = sorted(lista, key=lambda p: p['memory_percent'], reverse=True)[:10]
    elif filtro == 'cpu':
        lista = sorted(lista, key=lambda p: p['cpu_percent'], reverse=True)[:10]
    elif filtro == 'inativos':
        lista = [p for p in lista if p['cpu_percent'] == 0 and p['memory_percent'] == 0]
    else:
        lista = sorted(lista, key=lambda p: p['pid'])

    return jsonify(lista)

@main.route('/encerrar', methods=['POST'])
def encerrar():
    pid = request.json.get('pid')
    import psutil
    try:
        psutil.Process(pid).terminate()
        registrar_log(f"Processo encerrado: PID {pid}")
        return jsonify({"status": "encerrado", "pid": pid})
    except Exception as e:
        registrar_log(f"Erro ao encerrar processo {pid}: {str(e)}")
        return jsonify({"status": "erro", "mensagem": str(e)})

@main.route('/rede')
def rede():
    import psutil, socket, requests
    try:
        ip_local = socket.gethostbyname(socket.gethostname())
        ip_publico = requests.get('https://api.ipify.org').text
        net = psutil.net_io_counters()
        return jsonify({
            "ip_local": ip_local,
            "ip_publico": ip_publico,
            "enviado": round(net.bytes_sent / (1024 * 1024), 2),
            "recebido": round(net.bytes_recv / (1024 * 1024), 2)
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

@main.route('/rede/historico')
def rede_historico():
    import psutil
    import datetime
    try:
        net = psutil.net_io_counters()
        return jsonify({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "enviado": round(net.bytes_sent / (1024 * 1024), 2),
            "recebido": round(net.bytes_recv / (1024 * 1024), 2)
        })
    except Exception as e:
        return jsonify({"erro": str(e)})


@main.route('/hardware')
def hardware():
    import platform, psutil
    try:
        return jsonify({
            "sistema": platform.system(),
            "versao": platform.version(),
            "arquitetura": platform.machine(),
            "processador": platform.processor(),
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_threads": psutil.cpu_count(logical=True),
            "memoria_total": round(psutil.virtual_memory().total / (1024**3), 2),
            "disco_total": round(psutil.disk_usage('/').total / (1024**3), 2)
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

@main.route('/uptime')
def uptime():
    import psutil, datetime
    try:
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        agora = datetime.datetime.now()
        delta = agora - boot
        return jsonify({
            "horas": delta.seconds // 3600,
            "minutos": (delta.seconds % 3600) // 60,
            "inicio": boot.strftime("%d/%m/%Y %H:%M")
        })
    except Exception as e:
        return jsonify({"erro": str(e)})

def registrar_log(mensagem):
    import datetime, os
    os.makedirs('logs', exist_ok=True)
    with open('logs/monitor.log', 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensagem}\n")