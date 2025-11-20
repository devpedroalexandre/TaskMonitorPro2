🖥️ TaskMonitor Pro 2
Monitor profissional de sistema com interface moderna, temas claro/escuro e sensores avançados.

TaskMonitor Pro 2
Python
License

✨ Funcionalidades
📊 Status em Tempo Real: CPU, Memória, Disco, Servidor

🌡️ Sensores Avançados: Temperatura CPU, Frequência RAM, Energia RAM, Bateria

⚙️ Gerenciamento de Processos: Top CPU, Top Memória, Encerrar processos

🌐 Monitoramento de Rede: IP Local, IP Público, Download/Upload em tempo real

💾 Backups Automáticos: Salva snapshots completos do sistema

📋 Logs: Histórico de todos os backups

🌙 Temas: Modo claro e escuro profissionais

📈 Gráficos em Tempo Real: Visualização de CPU, Memória e Disco

⏱️ Uptime: Monitoramento do tempo de atividade do sistema

🛠️ Tecnologias
Backend: Python Flask

Frontend: HTML5, CSS3, JavaScript, Bootstrap 5

Gráficos: Chart.js

Monitor de Sistema: psutil, WMI

📦 Instalação
Pré-requisitos
Python 3.8 ou superior

Windows (para sensores WMI)

Privilégios de administrador (para temperatura)

Passo a Passo
Clone o repositório:

bash
git clone https://github.com/devpedroalexandre/Task-Monitor-Pro-2.0.git
cd Task-Monitor-Pro-2.0
Crie um ambiente virtual:

bash
python -m venv venv
Ative o ambiente:

bash
# Windows
.\venv\Scripts\activate
Instale as dependências:

bash
pip install -r requirements.txt
Execute:

bash
python run.py
Acesse no navegador:

text
http://localhost:5000
⚙️ Execução como Administrador
Para visualizar a temperatura do CPU, execute como Administrador:

Opção 1: Usando o .bat (RECOMENDADO)
bash
# Clique com botão direito em:
run-taskmonitor.bat

# Selecione: "Executar como administrador"
Opção 2: PowerShell como Admin
powershell
# Abra PowerShell como Administrador
cd "C:\caminho\para\TaskMonitorPro2"
python run.py
📊 Estrutura do Projeto
text
TaskMonitor-Pro-2/
├── app/
│   ├── __init__.py          # Inicialização do Flask
│   ├── monitor.py           # Coleta dados do sistema (MELHORADO)
│   ├── backup_new.py        # Gera backups automáticos
│   └── routes.py            # Rotas Flask (API)
├── templates/
│   └── index.html           # Interface web completa
├── static/
│   └── [arquivos estáticos] # CSS, JS, imagens
├── backups/                 # Pasta de backups automáticos
├── venv/                    # Ambiente virtual (não enviar ao Git)
├── run.py                   # Arquivo principal de execução
├── requirements.txt         # Dependências Python
├── run-taskmonitor.bat      # Script Windows para execução
└── README.md                # Este arquivo
🎨 Temas
Modo Claro
Gradiente roxo/azul moderno

Cards com gradientes suaves

Sombras elegantes

Modo Escuro
Interface elegante com cores suaves

Alta legibilidade

Contraste otimizado

Clique no botão 🌙 no canto superior direito para alternar!

🔧 Melhorias de Código (v2.0)
Monitor de Processos Melhorado
✅ Tratamento de erros AccessDenied, NoSuchProcess, ZombieProcess

✅ Captura mais processos mesmo sem privilégios de administrador

✅ Ignora processos sem permissão automaticamente

✅ Performance otimizada com cpu_percent(interval=0.1)

Limitações Conhecidas
Recurso	Sem Admin	Com Admin
Processos	⚠️ Alguns processos de sistema não aparecem	✅ Todos os processos
Temperatura	❌ Sempre mostra N/A (limitação Windows)	✅ Temperatura real
Sensores WMI	❌ Não funciona	✅ Funciona completamente
Nota: A temperatura do CPU requer obrigatoriamente privilégios de administrador devido a restrições de segurança do Windows.

📸 Screenshots
Dashboard Principal
Dashboard

Monitoramento de Processos
Processos

Modo Claro vs Escuro
Temas

🚀 Funcionalidades Detalhadas
1. Status do Sistema
Uso de CPU em tempo real

Uso de Memória RAM

Uso de Disco

Status do servidor (Online/Offline)

2. Sensores Avançados
Temperatura CPU: Requer modo administrador

Frequência RAM: MHz em tempo real

Energia RAM: Consumo estimado em Watts

Bateria: Percentual e status (Notebook/Desktop)

3. Rede
IP Local (LAN)

IP Público (WAN)

Download/Upload em MB

Gráficos em tempo real

4. Hardware
Informações do processador

Total de RAM instalada

Espaço total em disco

Placa de vídeo (GPU)

5. Processos
Top CPU: 10 processos que mais consomem CPU

Top Memória: 10 processos que mais consomem RAM

Todos: Lista completa de processos

Encerrar: Botão para matar processos

6. Backup Automático
Snapshot completo do sistema

Salvo em formato JSON

Timestamp único para cada backup

Histórico completo nos logs

7. Uptime
Tempo desde último boot

Data e hora do último boot

Formato: dias, horas, minutos

🐛 Solução de Problemas
Temperatura sempre mostra N/A
Causa: Não está executando como administrador
Solução: Use o arquivo run-taskmonitor.bat como admin

Poucos processos aparecem
Causa: Falta de privilégios de administrador
Solução: Execute como admin ou aceite a limitação (alguns processos de sistema precisam de admin)

Erro ao instalar dependências
Causa: pip desatualizado
Solução: python -m pip install --upgrade pip

Porta 5000 já está em uso
Causa: Outro serviço usando a porta
Solução: Mude a porta em run.py:

python
app.run(debug=True, host='0.0.0.0', port=5001)
📝 Dependências (requirements.txt)
text
Flask==3.0.0
psutil==5.9.6
pyWin32==306
WMI==1.5.1
requests==2.31.0
👨‍💻 Autor
Pedro Alexandre
Desenvolvedor Full-Stack em formação

GitHub: @devpedroalexandre

LinkedIn: Pedro Alexandre

📝 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

🤝 Contribuições
Contribuições são bem-vindas! Sinta-se à vontade para:

Fazer um Fork do projeto

Criar uma branch para sua feature (git checkout -b feature/NovaFeature)

Commit suas mudanças (git commit -m 'Adiciona nova feature')

Push para a branch (git push origin feature/NovaFeature)

Abrir um Pull Request

🔮 Próximas Funcionalidades (Roadmap)
 Gráficos históricos (24h, 7 dias, 30 dias)

 Alertas personalizados por email/SMS

 Exportação de relatórios em PDF

 API REST para integração externa

 Dashboard responsivo para mobile

 Suporte para Linux e macOS

 Monitoramento remoto de múltiplos servidores

 Integração com banco de dados