Requisitos previos
Git
Python 3.8 o superior 
(En Windows, durante la instalación marca la opción “Add Python to PATH”)

1. Clonar el repositorio: git clone https://github.com/gigirenbu-ui/Calculadora_centroides.git
   
2. Crear ambiente virtual windows: 
python -m venv .venv
.venv\Scripts\activate
Linux/mac os:
python3 -m venv .venv
source .venv/bin/activate

3. Instalar dependencias: 
pip install -r requirements.txt
Si por alguna razón no se encuentran, ejecutar manualmente: pip install pyqt5 numpy matplotlib

4. Ejecución del programa:
python main.py

Nota: En caso de tener problemas con la ejecución de scripts para la creación del ambiente virtual ejecutar:
Set-ExecutionPolicy Bypass -Scope Process    => Permiso de ejecución de comandos en powershell windows
.venv\Scripts\activate    => Activación del entorno virtual
