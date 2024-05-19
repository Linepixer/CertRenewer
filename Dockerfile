FROM certbot/certbot

RUN apk update && \
    apk add --no-cache python3 py3-pip

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar software principal
COPY main.py /app/main.py

# Ejecucion de la aplicacion
ENTRYPOINT ["python", "./main.py"]
