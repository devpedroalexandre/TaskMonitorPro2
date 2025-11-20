import datetime
import os
import psutil
from .monitor import get_status


def criar_backup_novo():
    """
    Cria backup completo do sistema com formato detalhado.
    Inclui: CPU, Memória, Disco, Rede, Uptime, Top 10 Processos + Novos sensores.
    """
    try:
        os.makedirs('backups', exist_ok=True)
        
        # Obtém dados do sistema
        dados = get_status()
        
        # Dados adicionais
        cpu_info = psutil.cpu_freq()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.datetime.now() - boot_time).total_seconds()
        uptime_hours = uptime_seconds / 3600
        
        # IP Local
        try:
            addrs = psutil.net_if_addrs()
            ip_local = next((addr.address for iface in addrs.values() 
                           for addr in iface if addr.family == 2 and not addr.address.startswith('127.')), 'N/A')
        except:
            ip_local = 'N/A'
        
        # Top 10 processos
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processos.append(proc.info)
            except:
                pass
        top_processos = sorted(processos, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
        
        # Gera timestamp e nome do arquivo
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f'backups/resumo_backup_{timestamp}.txt'
        
        # Formata conteúdo
        conteudo = f"""============================================================
BACKUP TASKMONITOR PRO 2 - {timestamp}
============================================================

🕐 Data/Hora do Backup: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

============================================================
RESUMO DO SISTEMA
============================================================

💻 CPU:
   - Uso Atual: {dados['cpu']}%
   - Núcleos: {psutil.cpu_count(logical=False)}
   - Frequência: {int(cpu_info.current) if cpu_info else 0} MHz

🧠 MEMÓRIA:
   - Total: {mem.total / (1024**3):.2f} GB
   - Usado: {mem.used / (1024**3):.2f} GB ({mem.percent}%)
   - Disponível: {mem.available / (1024**3):.2f} GB

💾 DISCO:
   - Total: {disk.total / (1024**3):.2f} GB
   - Usado: {disk.used / (1024**3):.2f} GB ({disk.percent}%)
   - Livre: {disk.free / (1024**3):.2f} GB

🌐 REDE:
   - IP Local: {ip_local}
   - Bytes Enviados: {net.bytes_sent:,}
   - Bytes Recebidos: {net.bytes_recv:,}

⏱️ SISTEMA:
   - Boot: {boot_time.strftime('%d/%m/%Y %H:%M:%S')}
   - Uptime: {uptime_hours:.2f} horas

============================================================
SENSORES AVANÇADOS
============================================================

🌡️ TEMPERATURA CPU:
   - Valor: {dados['cpu_temperatura']}{'°C' if dados['cpu_temperatura'] != 'N/A' else ''}

⚡ FREQUÊNCIA RAM:
   - Valor: {dados['ram_frequencia']}{' MHz' if dados['ram_frequencia'] != 'N/A' else ''}

🔋 ENERGIA RAM:
   - Consumo Total: {dados['ram_energia']['total_watts'] if isinstance(dados['ram_energia'], dict) else dados['ram_energia']}{' W' if isinstance(dados['ram_energia'], dict) and dados['ram_energia']['total_watts'] != 'N/A' else ''}
"""
        
        # Adiciona bateria se disponível
        if dados['bateria'] != 'N/A' and isinstance(dados['bateria'], dict):
            status_plugado = "Conectado na tomada" if dados['bateria']['plugged'] else "Usando bateria"
            tempo_restante = ""
            if dados['bateria']['time_left'] and dados['bateria']['time_left'] > 0:
                minutos = dados['bateria']['time_left'] // 60
                tempo_restante = f" ({minutos} min restantes)"
            
            conteudo += f"""
🔋 BATERIA:
   - Carga: {dados['bateria']['percent']}%
   - Status: {status_plugado}{tempo_restante}
"""
        else:
            conteudo += f"""
🔋 BATERIA:
   - Status: N/A (Desktop ou sensor não disponível)
"""
        
        # Top 10 processos
        conteudo += """
============================================================
TOP 10 PROCESSOS (por uso de CPU)
============================================================

"""
        for i, proc in enumerate(top_processos, 1):
            conteudo += f"""{i}. {proc['name']} (PID: {proc['pid']})
   CPU: {proc['cpu_percent'] or 0:.1f}% | RAM: {proc['memory_percent'] or 0:.1f}%

"""
        
        # Salva o backup
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        return f"✅ Backup criado com sucesso: {nome_arquivo}"
    
    except Exception as e:
        return f"❌ Erro ao criar backup: {str(e)}"