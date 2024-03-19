import subprocess

def start_menu():
    choice = input("Pressione Enter para iniciar ou digite um token do Ngrok: ")
    return choice.strip()  # Remover espaços em branco extras

def start_ngrok_with_token():
    token = start_menu()
    if not token:
        token = "2dsxW1aWbHh9dBetMyAKRZCHw3b_3AktjKc7iPUJF8irVcGeM"  # Token padrão
    
    command1 = "ngrok.exe"
    command2 = f"ngrok authtoken {token}"
    command3 = "ngrok http --domain=delicate-corgi-mostly.ngrok-free.app 1344"
    
    # Comando para abrir um novo terminal e executar os comandos
    command = f'start cmd /k "{command1} && {command2} && {command3}"'
    subprocess.Popen(command, shell=True)
