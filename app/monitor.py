import psutil
import platform
import socket
import requests
from datetime import datetime
import wmi


def get_system_info():
    """Retorna informações básicas do sistema"""
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        temperatura = "N/A"
        
        for sensor in w.Sensor():
            if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                temperatura = f"{sensor.Value:.1f}°C"
                break
    except:
        temperatura = "N/A"
    
    # Frequência RAM
    try:
        w_cimv2 = wmi.WMI()
        freq_ram = "N/A"
        for memory in w_cimv2.Win32_PhysicalMemory():
            if memory.ConfiguredClockSpeed:
                freq_ram = f"{memory.ConfiguredClockSpeed} MHz"
                break
    except:
        freq_ram = "N/A"
    
    # Energia RAM
    try:
        mem = psutil.virtual_memory()
        energia_ram = f"{(mem.used / (1024**3) * 0.003):.2f}W"
    except:
        energia_ram = "N/A"
    
    # Bateria
    try:
        battery = psutil.sensors_battery()
        if battery:
            bateria_info = {
                'percent': f"{battery.percent}%",
                'status': 'Carregando' if battery.power_plugged else 'Descarregando',
                'type': 'Notebook'
            }
        else:
            bateria_info = {
                'percent': 'N/A',
                'status': 'Desktop',
                'type': 'Desktop'
            }
    except:
        bateria_info = {
            'percent': 'N/A',
            'status': 'Desktop',
            'type': 'Desktop'
        }
    
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu_percent': round(cpu_percent, 1),
        'memory_percent': round(memory.percent, 1),
        'disk_percent': round(disk.percent, 1),
        'temperatura': temperatura,
        'freq_ram': freq_ram,
        'energia_ram': energia_ram,
        'bateria': bateria_info,
        'status': 'Online',
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.machine(),
        'hostname': socket.gethostname(),
        'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%d/%m/%Y %H:%M:%S")
    }


def get_processes():
    """Retorna lista de processos com uso de CPU e memória - MELHORADO"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Força leitura de informações do processo
            pinfo = proc.info
            
            # Tenta acessar mais informações para garantir permissão
            cpu_usage = proc.cpu_percent(interval=0.1)
            
            processes.append({
                'pid': pinfo['pid'],
                'name': pinfo['name'] or 'Unknown',
                'cpu_percent': round(cpu_usage if cpu_usage else 0, 1),
                'memory_percent': round(pinfo['memory_percent'] if pinfo['memory_percent'] else 0, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Ignora processos sem permissão de acesso
            continue
        except Exception:
            # Ignora qualquer outro erro
            continue
    
    return processes


def get_top_processes_by_cpu(limit=10):
    """Retorna os processos que mais consomem CPU"""
    processes = get_processes()
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]


def get_top_processes_by_memory(limit=10):
    """Retorna os processos que mais consomem memória"""
    processes = get_processes()
    return sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]


def get_network_info():
    """Retorna informações de rede"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "N/A"
    
    try:
        public_ip = requests.get('https://api.ipify.org', timeout=3).text
    except:
        public_ip = "N/A"
    
    net_io = psutil.net_io_counters()
    
    return {
        'local_ip': local_ip,
        'public_ip': public_ip,
        'bytes_sent': round(net_io.bytes_sent / (1024**2), 2),
        'bytes_recv': round(net_io.bytes_recv / (1024**2), 2),
        'packets_sent': net_io.packets_sent,
        'packets_recv': net_io.packets_recv
    }


def kill_process(pid):
    """Encerra um processo pelo PID"""
    try:
        process = psutil.Process(pid)
        process.terminate()
        return True, f"Processo {pid} encerrado com sucesso"
    except psutil.NoSuchProcess:
        return False, f"Processo {pid} não encontrado"
    except psutil.AccessDenied:
        return False, f"Sem permissão para encerrar o processo {pid}"
    except Exception as e:
        return False, f"Erro ao encerrar processo: {str(e)}"


def get_hardware_info():
    """Retorna informações de hardware"""
    try:
        w = wmi.WMI()
        
        # CPU
        cpu_info = w.Win32_Processor()[0]
        cpu_name = cpu_info.Name.strip()
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        
        # RAM
        ram_info = w.Win32_ComputerSystem()[0]
        total_ram = round(int(ram_info.TotalPhysicalMemory) / (1024**3), 2)
        
        # Disco
        disk = psutil.disk_usage('/')
        total_disk = round(disk.total / (1024**3), 2)
        
        # GPU (se disponível)
        try:
            gpu_info = w.Win32_VideoController()[0]
            gpu_name = gpu_info.Name
        except:
            gpu_name = "N/A"
        
        return {
            'cpu_name': cpu_name,
            'cpu_cores': cpu_cores,
            'cpu_threads': cpu_threads,
            'ram_total': f"{total_ram} GB",
            'disk_total': f"{total_disk} GB",
            'gpu_name': gpu_name
        }
    except:
        return {
            'cpu_name': 'N/A',
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'ram_total': 'N/A',
            'disk_total': 'N/A',
            'gpu_name': 'N/A'
        }


def get_uptime():
    """Retorna o tempo de atividade do sistema"""
    boot_time = psutil.boot_time()
    uptime_seconds = datetime.now().timestamp() - boot_time
    
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    
    boot_datetime = datetime.fromtimestamp(boot_time)
    
    return {
        'boot_time': boot_datetime.strftime("%d/%m/%Y %H:%M:%S"),
        'uptime_days': days,
        'uptime_hours': hours,
        'uptime_minutes': minutes,
        'uptime_formatted': f"{days}d {hours}h {minutes}min"
    }