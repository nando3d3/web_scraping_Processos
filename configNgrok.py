import subprocess

def start_ngrok_with_token():

    command = f'ngrok authtoken 2cdq36JUG9ipHDY3vjOhKvkpBDw_3Snw4nFNGTdVytMPscQoj'

    # Executa o comando no terminal
    subprocess.run(command, shell=True)
    subprocess.run("ngrok http --domain=prepared-related-tadpole.ngrok-free.app 8000", shell=True)
