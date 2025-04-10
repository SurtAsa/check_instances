# Use uma imagem oficial do Python como base
FROM python:3.10-slim-buster

# Define o diretório de trabalho no container
WORKDIR /app

# Copia a chave para o container
COPY pemKey.pem ./

# Atribui permissões
RUN  chmod 400 pemKey.pem

# Copia o arquivo de dependências para o container
COPY Pipfile Pipfile.lock ./

# Instala as dependências do projeto
RUN pip install pipenv && pipenv install --system --deploy

# Copia o restante do código para o container
COPY . .

# Comando para iniciar o bot
CMD ["python", "check_instances.py"]
