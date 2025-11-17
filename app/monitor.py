import psutil

def get_status():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memoria": psutil.virtual_memory().percent,
        "disco": psutil.disk_usage('/').percent,
        "status_servidor": "Online"
    }