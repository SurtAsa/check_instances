# Check instances

Um script em Python para verificar o status de suas instâncias. Ele usa o protocolo SSH para acessar remotamente as máquinas e verificar se um serviço específico está em execução.

Pré-requisitos:
1. Biblioteca paramiko: É usada para conectar-se via SSH.
2. Biblioteca rocketry: É usada como schedule no script.
3. Chaves SSH: Certifique-se de que a máquina principal tem acesso às suas instâncias por meio de chave SSH.
4. Arquivo de Configuração: Crie um arquivo instances.json com a lista de instâncias.

## Como usar:
1. Certifique-se de que o arquivo instances.json está no mesmo diretório do script.
2. Certifique-se que o arquivo mercado-topografico.pem está no mesmo diretório do script.
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
Para usar esse script dentro de um Docker container você precisa rodar os seguintes comandos:
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
sudo docker build -t check_instaces .
```
3. Para subir o container, garantindo que ele suba quando a máquina reiniciar:
```bash
sudo docker run -d --restart unless-stopped check_instaces
```

Resultado:

O script retornará o status de cada instância, indicando se o serviço especificado está ativo e notificará no Discord se houve algum erro ao se conectar.

https://www.paramiko.org/

https://requests.readthedocs.io/en/latest/

https://rocketry.readthedocs.io/en/stable/index.html