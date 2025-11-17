# teste_backup.py
import sys
sys.path.append('app')
from backup import criar_backup

resultado = criar_backup()
print(resultado)
