# Check instances

Um script em Python para monitorar suas instâncias e notificar no Discord quando algo falhar. Ele faz duas verificações:
- **SSH** (a cada 4 horas): conecta via SSH em cada instância listada no `instances.json` para confirmar que ela está online.
- **Health de produção** (`prod01` e `prod02`, cada uma a cada 10 minutos, alternando de 5 em 5 minutos): consulta os endpoints de health e notifica quando a resposta não for HTTP 200.

Pré-requisitos:
1. Biblioteca paramiko: É usada para conectar-se via SSH.
2. Biblioteca rocketry: É usada como schedule no script.
3. Biblioteca requests: É usada para consultar os endpoints de health e enviar as notificações ao Discord.
4. Chave SSH: Um arquivo `.pem` com acesso às suas instâncias.
5. Arquivo de Configuração: Crie um arquivo `instances.json` com a lista de instâncias.

## Configuração

### instances.json
Cada instância precisa dos campos abaixo. O campo `pem_key` é o caminho da chave SSH relativo ao diretório do script:
```json
[
  {
    "instance_name": "Prod Instance",
    "host": "URL",
    "username": "USERNAME",
    "port": 22,
    "pem_key": "pemKey.pem"
  }
]
```

### Discord
Edite as constantes no início do `check_instances.py`:
- `DISCORD_WEBHOOK_URL`: URL do webhook do Discord (`https://discord.com/api/webhooks/...`).
- `ROLE_ID`: ID do cargo que será marcado nas mensagens de erro.

## Como usar:
1. Certifique-se de que o arquivo `instances.json` está no mesmo diretório do script.
2. Certifique-se de que a chave `.pem` está no mesmo diretório do script, com o mesmo nome informado no campo `pem_key` do `instances.json`.
3. Ative a venv (virtual environment) com o comando:
```bash
pipenv shell
```
4. Instale as bibliotecas necessárias com o comando:
```bash
pipenv install
```
5. Execute o script:
```bash
python check_instances.py
```
Para rodar em segundo plano:
```bash
nohup python check_instances.py &
```

## Como usar com o Docker:
Antes de gerar a imagem:
- Deixe **exatamente um** arquivo `.pem` no diretório do projeto. Ele pode ter qualquer nome, pois dentro do container ele é copiado como `pemKey.pem`. Se houver mais de um `.pem` (ou nenhum), o build falha.
- No `instances.json`, use `"pem_key": "pemKey.pem"` em todas as instâncias.

O `.dockerignore` só envia para o build os arquivos necessários (`Pipfile`, `Pipfile.lock`, `check_instances.py`, `instances.json` e o `.pem`). Se o script passar a usar outro arquivo, adicione-o no `.dockerignore` (com `!arquivo`) e no `COPY` do `Dockerfile`.

Passos:
1. Para gerar o arquivo Pipfile.lock, já dentro da venv rode o comando:
```bash
pipenv install
```
ou
```bash
pipenv lock
```
2. Para criar a imagem docker:
```bash
sudo docker build -t check_instances .
```
3. Para subir o container, garantindo que ele suba quando a máquina reiniciar:
```bash
sudo docker run -d --restart unless-stopped check_instances
```
4. Para acompanhar os logs:
```bash
sudo docker logs -f <id_ou_nome_do_container>
```

Resultado:

O script retornará o status de cada instância e notificará no Discord se houver algum erro ao se conectar via SSH ou se algum endpoint de health de produção não responder 200.

https://www.paramiko.org/

https://requests.readthedocs.io/en/latest/

https://rocketry.readthedocs.io/en/stable/index.html
