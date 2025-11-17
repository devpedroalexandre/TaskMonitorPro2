import shutil
import datetime

def criar_backup():
    origem = 'database/tarefas.db'
    destino = f'backup/tarefas_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    try:
        shutil.copy(origem, destino)
        return f"Backup criado com sucesso: {destino}"
    except Exception as e:
        return f"Erro ao criar backup: {str(e)}"