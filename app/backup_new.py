import os
import json
import shutil
import sqlite3
import zipfile
from datetime import datetime
import psutil

def criar_backup_novo():
    """
    Cria backup completo do sistema com dados de monitoramento em tempo real
    Versão corrigida para uso com Flask
    """
    try:
        # Configurações
        origem_db = 'database/tarefas.db'
        data_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'backup'
        
        # Cria pasta de backup se não existir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Nomes dos arquivos
        destino_db = f'{backup_dir}/tarefas_backup_{data_str}.db'
        destino_json = f'{backup_dir}/system_data_{data_str}.json'
        destino_txt = f'{backup_dir}/resumo_backup_{data_str}.txt'
        destino_zip = f'{backup_dir}/backup_completo_{data_str}.zip'
        
        # ============================================
        # 1. COLETA DADOS DO SISTEMA EM TEMPO REAL
        # ============================================
        
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        memoria = psutil.virtual_memory()
        disco = psutil.disk_usage('/')
        rede_io = psutil.net_io_counters()
        
        try:
            addrs = psutil.net_if_addrs()
            ip_local = next((addr.address for iface_addrs in addrs.values() 
                           for addr in iface_addrs if addr.family == 2), 'N/A')
        except:
            ip_local = 'N/A'
        
        # Processos (top 10 por uso de CPU)
        processos = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processos.append({
                    'pid': info['pid'],
                    'nome': info['name'],
                    'cpu_percent': info['cpu_percent'],
                    'memory_percent': info['memory_percent']
                })
            except:
                pass
        
        processos = sorted(processos, key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
        
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        
        # Monta estrutura de dados completa
        system_data = {
            'timestamp': datetime.now().isoformat(),
            'data_backup': data_str,
            'cpu': {
                'uso_percent': cpu_percent,
                'nucleos': cpu_count,
                'frequencia_mhz': cpu_freq.current if cpu_freq else None
            },
            'memoria': {
                'total_gb': round(memoria.total / (1024**3), 2),
                'usado_gb': round(memoria.used / (1024**3), 2),
                'disponivel_gb': round(memoria.available / (1024**3), 2),
                'percent_usado': memoria.percent
            },
            'disco': {
                'total_gb': round(disco.total / (1024**3), 2),
                'usado_gb': round(disco.used / (1024**3), 2),
                'livre_gb': round(disco.free / (1024**3), 2),
                'percent_usado': disco.percent
            },
            'rede': {
                'ip_local': ip_local,
                'bytes_enviados': rede_io.bytes_sent,
                'bytes_recebidos': rede_io.bytes_recv,
                'pacotes_enviados': rede_io.packets_sent,
                'pacotes_recebidos': rede_io.packets_recv
            },
            'sistema': {
                'boot_time': boot_time.isoformat(),
                'uptime_horas': round(uptime_seconds / 3600, 2),
                'nome_so': os.name
            },
            'processos_top10': processos
        }
        
        # ============================================
        # 2. SALVA DADOS EM JSON
        # ============================================
        with open(destino_json, 'w', encoding='utf-8') as f:
            json.dump(system_data, f, indent=4, ensure_ascii=False)
        
        # ============================================
        # 3. COPIA BANCO DE DADOS ORIGINAL
        # ============================================
        if os.path.exists(origem_db):
            shutil.copy(origem_db, destino_db)
        else:
            sqlite3.connect(destino_db).close()
        
        # ============================================
        # 4. CRIA/ATUALIZA BANCO COM DADOS DE MONITORAMENTO
        # ============================================
        conn = sqlite3.connect(destino_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoramento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memoria_percent REAL,
                disco_percent REAL,
                uptime_horas REAL,
                processos_ativos INTEGER
            )
        ''')
        
        cursor.execute('''
            INSERT INTO monitoramento 
            (timestamp, cpu_percent, memoria_percent, disco_percent, uptime_horas, processos_ativos)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            system_data['timestamp'],
            system_data['cpu']['uso_percent'],
            system_data['memoria']['percent_usado'],
            system_data['disco']['percent_usado'],
            system_data['sistema']['uptime_horas'],
            len(system_data['processos_top10'])
        ))
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processos_backup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                pid INTEGER,
                nome TEXT,
                cpu_percent REAL,
                memory_percent REAL
            )
        ''')
        
        for proc in system_data['processos_top10']:
            cursor.execute('''
                INSERT INTO processos_backup (timestamp, pid, nome, cpu_percent, memory_percent)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                system_data['timestamp'],
                proc['pid'],
                proc['nome'],
                proc['cpu_percent'],
                proc['memory_percent']
            ))
        
        conn.commit()
        conn.close()
        
        # ============================================
        # 5. CRIA ARQUIVO DE RESUMO TXT
        # ============================================
        with open(destino_txt, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"BACKUP TASKMONITOR PRO - {data_str}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"🕐 Data/Hora do Backup: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("RESUMO DO SISTEMA\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"💻 CPU:\n")
            f.write(f"   - Uso Atual: {cpu_percent}%\n")
            f.write(f"   - Núcleos: {cpu_count}\n")
            if cpu_freq:
                f.write(f"   - Frequência: {cpu_freq.current:.0f} MHz\n")
            f.write("\n")
            
            f.write(f"🧠 MEMÓRIA:\n")
            f.write(f"   - Total: {system_data['memoria']['total_gb']} GB\n")
            f.write(f"   - Usado: {system_data['memoria']['usado_gb']} GB ({memoria.percent}%)\n")
            f.write(f"   - Disponível: {system_data['memoria']['disponivel_gb']} GB\n")
            f.write("\n")
            
            f.write(f"💾 DISCO:\n")
            f.write(f"   - Total: {system_data['disco']['total_gb']} GB\n")
            f.write(f"   - Usado: {system_data['disco']['usado_gb']} GB ({disco.percent}%)\n")
            f.write(f"   - Livre: {system_data['disco']['livre_gb']} GB\n")
            f.write("\n")
            
            f.write(f"🌐 REDE:\n")
            f.write(f"   - IP Local: {ip_local}\n")
            f.write(f"   - Bytes Enviados: {rede_io.bytes_sent:,}\n")
            f.write(f"   - Bytes Recebidos: {rede_io.bytes_recv:,}\n")
            f.write("\n")
            
            f.write(f"⏱️ SISTEMA:\n")
            f.write(f"   - Boot: {boot_time.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"   - Uptime: {system_data['sistema']['uptime_horas']} horas\n")
            f.write("\n")
            
            f.write("=" * 60 + "\n")
            f.write("TOP 10 PROCESSOS (por uso de CPU)\n")
            f.write("=" * 60 + "\n\n")
            
            for i, proc in enumerate(processos, 1):
                f.write(f"{i}. {proc['nome']} (PID: {proc['pid']})\n")
                f.write(f"   CPU: {proc['cpu_percent']}% | RAM: {proc['memory_percent']:.1f}%\n\n")
        
        # ============================================
        # 6. COMPACTA TUDO EM ZIP
        # ============================================
        with zipfile.ZipFile(destino_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(destino_db, os.path.basename(destino_db))
            zipf.write(destino_json, os.path.basename(destino_json))
            zipf.write(destino_txt, os.path.basename(destino_txt))
        
        return f'Backup criado com sucesso! Arquivos: {destino_db}, {destino_json}, {destino_txt}, {destino_zip}'
        
    except Exception as e:
        return f'Erro ao criar backup: {str(e)}'
