# Usa la imagen oficial de Python 3.12
FROM python:3.12-slim

# Establece la carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto
COPY . .

# Comando para iniciar tu app Flask
CMD ["python", "api.py"]
