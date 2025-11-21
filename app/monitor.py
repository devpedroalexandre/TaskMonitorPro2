import psutil
import platform
from datetime import datetime, timedelta

def get_cpu_temperature_wmi():
    """Tenta obter temperatura da CPU via WMI (OpenHardwareMonitor ou HWiNFO)"""
    try:
        import wmi
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        temperature_infos = w.Sensor()
        
        for sensor in temperature_infos:
            if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                return round(sensor.Value, 1)
        
        # Se não encontrou via OpenHardwareMonitor, tenta namespace WMI padrão
        w = wmi.WMI(namespace="root\\WMI")
        temperature_infos = w.MSAcpi_ThermalZoneTemperature()
        
        if temperature_infos:
            temp_kelvin = temperature_infos[0].CurrentTemperature / 10.0
            temp_celsius = temp_kelvin - 273.15
            return round(temp_celsius, 1)
            
    except Exception as e:
        print(f"[INFO] Temperatura CPU não disponível: {e}")
        pass
    
    return "N/A"


def get_ram_frequency_wmi():
    """Tenta obter frequência da RAM via WMI (OpenHardwareMonitor ou HWiNFO)"""
    try:
        import wmi
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        clocks = w.Sensor()
        
        for sensor in clocks:
            if sensor.SensorType == 'Clock' and 'Memory' in sensor.Name:
                return round(sensor.Value, 1)
                
    except Exception as e:
        print(f"[INFO] Frequência RAM não disponível: {e}")
        pass
    
    return "N/A"


def calcular_energia_ram():
    """Calcula energia estimada da RAM baseada no uso"""
    try:
        mem = psutil.virtual_memory()
        mem_gb = mem.total / (1024**3)
        
        # Estimativa: ~1.5W por 8GB de RAM em uso moderado
        watts_base = (mem_gb / 8) * 1.5
        fator_uso = mem.percent / 100.0
        energia_estimada = watts_base * (0.5 + (fator_uso * 0.5))
        
        return {
            "total_watts": round(energia_estimada, 2),
            "uso_percent": mem.percent
        }
    except:
        return "N/A"


def get_battery_info():
    """Obtém informações da bateria (se disponível)"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            return {
                "percent": battery.percent,
                "plugged": battery.power_plugged,
                "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
            }
    except:
        pass
    
    return "N/A"


def get_status():
    """Retorna status completo do sistema"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory().percent
        disco = psutil.disk_usage('/').percent
        
        # Tenta obter temperatura e frequência via WMI
        cpu_temperatura = get_cpu_temperature_wmi()
        ram_frequencia = get_ram_frequency_wmi()
        ram_energia = calcular_energia_ram()
        bateria = get_battery_info()
        
        return {
            'cpu': round(cpu, 1),
            'memoria': round(memoria, 1),
            'disco': round(disco, 1),
            'status_servidor': 'Online',
            'cpu_temperatura': cpu_temperatura,
            'ram_frequencia': ram_frequencia,
            'ram_energia': ram_energia,
            'bateria': bateria
        }
    except Exception as e:
        print(f"❌ Erro em get_status: {e}")
        return {
            'cpu': 0,
            'memoria': 0,
            'disco': 0,
            'status_servidor': 'Erro',
            'cpu_temperatura': 'N/A',
            'ram_frequencia': 'N/A',
            'ram_energia': 'N/A',
            'bateria': 'N/A'
        }


def get_network_info():
    """Retorna informações de rede"""
    try:
        import socket
        import requests
        
        stats = psutil.net_io_counters()
        
        ip_local = socket.gethostbyname(socket.gethostname())
        
        try:
            ip_publico = requests.get('https://api.ipify.org', timeout=3).text
        except:
            ip_publico = "Não disponível"
        
        return {
            'ip_local': ip_local,
            'ip_publico': ip_publico,
            'enviado': round(stats.bytes_sent / (1024**2), 2),
            'recebido': round(stats.bytes_recv / (1024**2), 2)
        }
    except Exception as e:
        print(f"❌ Erro em get_network_info: {e}")
        return {
            'ip_local': 'Erro',
            'ip_publico': 'Erro',
            'enviado': 0,
            'recebido': 0
        }


def get_network_history():
    """Retorna histórico de rede para gráfico"""
    try:
        stats = psutil.net_io_counters()
        return {
            'enviado': round(stats.bytes_sent / (1024**2), 2),
            'recebido': round(stats.bytes_recv / (1024**2), 2)
        }
    except:
        return {'erro': 'Dados não disponíveis'}


def get_hardware_info():
    """Retorna informações de hardware"""
    try:
        uname = platform.uname()
        mem = psutil.virtual_memory()
        disco = psutil.disk_usage('/')
        
        return {
            'sistema': uname.system,
            'versao': uname.version,
            'arquitetura': platform.architecture()[0],
            'processador': uname.processor or platform.processor(),
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'memoria_total': round(mem.total / (1024**3), 2),
            'disco_total': round(disco.total / (1024**3), 2)
        }
    except Exception as e:
        print(f"❌ Erro em get_hardware_info: {e}")
        return {
            'sistema': 'Erro',
            'versao': 'Erro',
            'arquitetura': 'Erro',
            'processador': 'Erro',
            'cpu_cores': 0,
            'cpu_threads': 0,
            'memoria_total': 0,
            'disco_total': 0
        }


def get_uptime():
    """Retorna tempo de atividade do sistema"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        dias = uptime.days
        horas = int(uptime.seconds // 3600)
        minutos = int((uptime.seconds % 3600) // 60)
        
        return {
            'dias': dias,
            'horas': horas,
            'minutos': minutos,
            'inicio': boot_time.strftime('%d/%m/%Y %H:%M:%S')
        }
    except Exception as e:
        print(f"❌ Erro em get_uptime: {e}")
        return {
            'dias': 0,
            'horas': 0,
            'minutos': 0,
            'inicio': 'Erro'
        }


def get_processes(filtro='todos'):
    """Retorna lista de processos"""
    try:
        processos = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processos.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu_percent': round(info['cpu_percent'] or 0, 1),
                    'memory_percent': round(info['memory_percent'] or 0, 2)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if filtro == 'cpu':
            processos = sorted(processos, key=lambda x: x['cpu_percent'], reverse=True)[:15]
        elif filtro == 'memoria':
            processos = sorted(processos, key=lambda x: x['memory_percent'], reverse=True)[:15]
        else:
            processos = sorted(processos, key=lambda x: x['cpu_percent'], reverse=True)[:30]
        
        return processos
    except Exception as e:
        print(f"❌ Erro em get_processes: {e}")
        return []


def kill_process(pid):
    """Encerra um processo pelo PID"""
    try:
        processo = psutil.Process(pid)
        processo.terminate()
        return {'status': 'encerrado', 'pid': pid}
    except psutil.NoSuchProcess:
        return {'status': 'erro', 'pid': pid, 'mensagem': 'Processo não encontrado'}
    except psutil.AccessDenied:
        return {'status': 'erro', 'pid': pid, 'mensagem': 'Acesso negado'}
    except Exception as e:
        return {'status': 'erro', 'pid': pid, 'mensagem': str(e)}
