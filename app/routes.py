from flask import Blueprint, render_template, jsonify, request
from .monitor import get_status
from .backup_new import criar_backup_novo
import psutil
import os
import glob

main = Blueprint('main', __name__)


@main.route('/')
def index():
    dados = get_status()
    return render_template('index.html', **dados)


@main.route('/status')
def status():
    return jsonify(get_status())


@main.route('/logs')
def logs():
    """
    Lista todos os arquivos de backup da pasta backups/
    Retorna conteúdo dos últimos 10 backups.
    """
    try:
        # Verifica se a pasta backups existe
        if not os.path.exists('backups'):
            return "📁 Nenhum backup encontrado. Crie um backup primeiro!"
        
        # Lista todos os arquivos .txt na pasta backups
        arquivos_backup = glob.glob('backups/resumo_backup_*.txt')
        
        if not arquivos_backup:
            return "📁 Nenhum backup encontrado. Crie um backup primeiro!"
        
        # Ordena por data de modificação (mais recente primeiro)
        arquivos_backup.sort(key=os.path.getmtime, reverse=True)
        
        # Pega os 10 mais recentes
        arquivos_recentes = arquivos_backup[:10]
        
        # Monta lista com informações dos backups
        logs_conteudo = []
        logs_conteudo.append("=" * 60)
        logs_conteudo.append("📋 HISTÓRICO DE BACKUPS - TASKMONITOR PRO 2")
        logs_conteudo.append("=" * 60)
        logs_conteudo.append(f"\nTotal de backups encontrados: {len(arquivos_backup)}")
        logs_conteudo.append(f"Mostrando os {len(arquivos_recentes)} mais recentes:\n")
        
        for i, arquivo in enumerate(arquivos_recentes, 1):
            nome_arquivo = os.path.basename(arquivo)
            tamanho = os.path.getsize(arquivo)
            data_mod = os.path.getmtime(arquivo)
            
            import datetime
            data_formatada = datetime.datetime.fromtimestamp(data_mod).strftime('%d/%m/%Y %H:%M:%S')
            
            logs_conteudo.append(f"\n{'=' * 60}")
            logs_conteudo.append(f"📄 BACKUP #{i}: {nome_arquivo}")
            logs_conteudo.append(f"   📅 Data: {data_formatada}")
            logs_conteudo.append(f"   📦 Tamanho: {tamanho / 1024:.2f} KB")
            logs_conteudo.append(f"{'=' * 60}\n")
            
            # Lê o conteúdo do backup
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    # Limita a 2000 caracteres para não sobrecarregar
                    if len(conteudo) > 2000:
                        logs_conteudo.append(conteudo[:2000] + "\n\n... [CONTEÚDO TRUNCADO] ...\n")
                    else:
                        logs_conteudo.append(conteudo)
            except Exception as e:
                logs_conteudo.append(f"   ⚠️ Erro ao ler arquivo: {str(e)}\n")
        
        logs_conteudo.append("\n" + "=" * 60)
        logs_conteudo.append("FIM DO HISTÓRICO DE BACKUPS")
        logs_conteudo.append("=" * 60)
        
        return "\n".join(logs_conteudo)
    
    except Exception as e:
        return f"❌ Erro ao carregar logs: {str(e)}"


@main.route('/processos')
def processos():
    filtro = request.args.get('filtro', 'todos')
    lista = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            if filtro == 'cpu' and info['cpu_percent'] < 5:
                continue
            if filtro == 'memoria' and info['memory_percent'] < 5:
                continue
            lista.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if filtro == 'cpu':
        lista = sorted(lista, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:20]
    elif filtro == 'memoria':
        lista = sorted(lista, key=lambda x: x['memory_percent'] or 0, reverse=True)[:20]
    else:
        lista = sorted(lista, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:50]
    
    return jsonify(lista)


@main.route('/encerrar', methods=['POST'])
def encerrar():
    try:
        dados = request.get_json()
        pid = dados.get('pid')
        proc = psutil.Process(pid)
        proc.terminate()
        return jsonify({'status': 'encerrado', 'pid': pid})
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)})


@main.route('/rede')
def rede():
    net = psutil.net_io_counters()
    addrs = psutil.net_if_addrs()
    
    ip_local = 'N/A'
    for iface, enderecos in addrs.items():
        for addr in enderecos:
            if addr.family == 2 and not addr.address.startswith('127.'):
                ip_local = addr.address
                break
    
    try:
        import requests
        ip_publico = requests.get('https://api.ipify.org', timeout=5).text
    except:
        ip_publico = 'N/A'
    
    return jsonify({
        'ip_local': ip_local,
        'ip_publico': ip_publico,
        'enviado': round(net.bytes_sent / (1024**2), 2),
        'recebido': round(net.bytes_recv / (1024**2), 2)
    })


@main.route('/rede/historico')
def rede_historico():
    try:
        net = psutil.net_io_counters()
        return jsonify({
            'enviado': round(net.bytes_sent / (1024**2), 2),
            'recebido': round(net.bytes_recv / (1024**2), 2)
        })
    except Exception as e:
        return jsonify({'erro': str(e)})


@main.route('/hardware')
def hardware():
    import platform
    
    return jsonify({
        'sistema': platform.system(),
        'versao': platform.version(),
        'arquitetura': platform.machine(),
        'processador': platform.processor(),
        'cpu_cores': psutil.cpu_count(logical=False),
        'cpu_threads': psutil.cpu_count(logical=True),
        'memoria_total': round(psutil.virtual_memory().total / (1024**3), 2),
        'disco_total': round(psutil.disk_usage('/').total / (1024**3), 2)
    })


@main.route('/uptime')
def uptime():
    import datetime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    
    return jsonify({
        'horas': int(uptime.total_seconds() // 3600),
        'minutos': int((uptime.total_seconds() % 3600) // 60),
        'inicio': boot_time.strftime('%d/%m/%Y %H:%M:%S')
    })


@main.route('/backup')
def backup():
    return criar_backup_novo()