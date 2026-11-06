# Use uma imagem oficial do Python como base
FROM python:3.10-slim-buster

# Define o diretório de trabalho no container
WORKDIR /app

# Exibe os logs do Python em tempo real no docker logs
ENV PYTHONUNBUFFERED=1

# Copia a chave para o container
COPY *.pem ./pemKey.pem

# Atribui permissões
RUN  chmod 400 pemKey.pem

# Copia o arquivo de dependências para o container
COPY Pipfile Pipfile.lock ./

# Instala as dependências do projeto
RUN pip install pipenv && pipenv install --system --deploy

# Copia o código da aplicação para o container
COPY check_instances.py instances.json ./

# Comando para iniciar o bot
CMD ["python", "check_instances.py"]
