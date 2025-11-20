import psutil
import platform
import subprocess


def get_cpu_temperature_wmi():
    """
    Lê temperatura do CPU via WMI no Windows.
    Converte de décimos de Kelvin para Celsius.
    """
    try:
        if platform.system() != "Windows":
            return None
        
        result = subprocess.run(
            [
                "powershell",
                "-Command",
                "(Get-WmiObject -Namespace 'root/WMI' -Class MSAcpi_ThermalZoneTemperature | Select-Object -First 1).CurrentTemperature"
            ],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            temp_str = result.stdout.strip()
            if temp_str and temp_str.isdigit():
                temp_kelvin = int(temp_str) / 10
                temp_celsius = temp_kelvin - 273.15
                return round(temp_celsius, 1)
        
        return None
    except Exception as e:
        print(f"[DEBUG] Erro WMI temperatura: {e}")
        return None


def get_cpu_temperature():
    """
    Obtém temperatura do CPU.
    """
    try:
        if platform.system() == "Windows":
            temp = get_cpu_temperature_wmi()
            if temp is not None:
                return temp
        
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            for name in ['coretemp', 'cpu_thermal', 'k10temp', 'zenpower', 'it8792']:
                if name in temps:
                    entries = temps[name]
                    if entries:
                        return round(entries[0].current, 1)
        
        return None
    except Exception as e:
        print(f"[DEBUG] Erro ao obter temperatura: {e}")
        return None


def get_ram_frequency():
    """
    Obtém a frequência da memória RAM em MHz.
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "memorychip", "get", "speed"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                    speeds = []
                    for line in lines[1:]:
                        if line and line.isdigit():
                            speed = int(line)
                            if speed > 100:
                                speeds.append(speed)
                    
                    if speeds:
                        return speeds[0]
            except Exception as e:
                print(f"[DEBUG] Erro WMIC: {e}")
        
        elif system == "Linux":
            try:
                result = subprocess.run(
                    ["sudo", "dmidecode", "-t", "memory"], 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                for line in result.stdout.split('\n'):
                    if 'Speed:' in line and 'MHz' in line:
                        try:
                            speed = int(line.split(':')[1].strip().split()[0])
                            if speed > 100:
                                return speed
                        except:
                            pass
            except Exception as e:
                print(f"[DEBUG] Erro dmidecode: {e}")
        
        return None
    except Exception as e:
        print(f"[DEBUG] Erro geral RAM frequency: {e}")
        return None


def get_ram_power_consumption():
    """
    Estima o consumo de energia da RAM.
    """
    try:
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        estimated_watts = (total_gb / 8) * 3
        
        return {
            "total_watts": round(estimated_watts, 2)
        }
    except Exception as e:
        print(f"[DEBUG] Erro ao calcular consumo: {e}")
        return None


def get_battery_info():
    """
    Obtém informações da bateria (apenas para notebooks).
    Retorna percentual de carga e status.
    """
    try:
        if not hasattr(psutil, "sensors_battery"):
            return None
        
        battery = psutil.sensors_battery()
        if battery is None:
            return None
        
        return {
            "percent": round(battery.percent, 1),
            "plugged": battery.power_plugged,
            "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
        }
    except Exception as e:
        print(f"[DEBUG] Erro ao obter bateria: {e}")
        return None


def get_status():
    """
    Retorna status completo do sistema.
    """
    try:
        cpu_temp = get_cpu_temperature()
        ram_freq = get_ram_frequency()
        ram_power = get_ram_power_consumption()
        battery = get_battery_info()
        
        status = {
            "cpu": psutil.cpu_percent(interval=1),
            "memoria": psutil.virtual_memory().percent,
            "disco": psutil.disk_usage('/').percent,
            "status_servidor": "Online",
            "cpu_temperatura": cpu_temp if cpu_temp is not None else "N/A",
            "ram_frequencia": ram_freq if ram_freq is not None else "N/A",
            "ram_energia": ram_power if ram_power else {"total_watts": "N/A"},
            "bateria": battery if battery else "N/A"
        }
        
        return status
    except Exception as e:
        print(f"[DEBUG] Erro ao obter status: {e}")
        return {
            "cpu": "N/A",
            "memoria": "N/A",
            "disco": "N/A",
            "status_servidor": "Erro",
            "cpu_temperatura": "N/A",
            "ram_frequencia": "N/A",
            "ram_energia": {"total_watts": "N/A"},
            "bateria": "N/A"
        }