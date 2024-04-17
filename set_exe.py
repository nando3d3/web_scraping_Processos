import subprocess
import shutil

shutil.copy2('templates/pesquisa.html', 'dist/templates/pesquisa.html')
shutil.copy2('templates/resultado.html', 'dist/templates/resultado.html')

subprocess.run(["pyinstaller", "--onefile", "app.py"])

print("\nexecutável criado com sucesso!")