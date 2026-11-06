#!/usr/bin/env python
__author__ = "Paulo Martins"
__version__ = "1.2.0"

import paramiko
import json
import os
import requests
import time

from rocketry import Rocketry
from rocketry.conds import cron

app = Rocketry()

ROLE_ID = "1086351331813499020"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1222560415620534312/aCeVnHGjM0JmluBYmWUhBAhNKGMYx7zSFGkUdStUy9bHLRRJN8Uz3EjSrb2xfcrvoJYX"

PROD_HEALTH_ENDPOINTS = {
    "prod01": "https://prod01.mercadotopografico.com.br/api/v1/health",
    "prod02": "https://prod02.mercadotopografico.com.br/api/v1/health",
}

def send_discord_notification(message):
    """
    Envia uma mensagem para o Discord via webhook.
    """
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("[INFO] Notificação enviada ao Discord com sucesso.")
        else:
            print(f"[ERRO] Falha ao enviar notificação ao Discord: {response.status_code}")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar ao Discord: {e}")

def check_instance_online(instance):
    instance_name = instance["instance_name"]
    host = instance["host"]
    username = instance["username"]
    port = instance.get("port", 22)
    pem_key = instance["pem_key"]

    try:
        # Verifica se a chave PEM existe
        if not os.path.isfile(pem_key):
            message = f"[ERRO] {instance_name} - Chave PEM '{pem_key}' não encontrada para {host} <@&{ROLE_ID}>"
            send_discord_notification(message)
            return message

        # Configura a chave PEM para autenticação
        key = paramiko.RSAKey.from_private_key_file(pem_key)

        # Conecta à instância
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=port, username=username, pkey=key, timeout=5)
        ssh.close()
        return f"[OK] {instance_name} - Instância {host} está online"
    except Exception as e:
        message = f"[ERRO] {instance_name} - Falha ao conectar com {host}: {e} <@&{ROLE_ID}>"
        send_discord_notification(message)
        return message

def check_production_endpoint(name, url):
    """
    Consulta o health de uma máquina de produção.
    Notifica o Discord apenas quando a resposta não for HTTP 200.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"[OK] {name} - Health respondeu 200")
            return

        message = (
            f"[ERRO] {name} - Health {url} respondeu {response.status_code} "
            f"<@&{ROLE_ID}>"
        )
    except Exception as e:
        message = f"[ERRO] {name} - Falha ao acessar {url}: {e} <@&{ROLE_ID}>"

    print(message)
    send_discord_notification(message)

@app.task(cron(minute="0,10,20,30,40,50"))
def check_prod01_health():
    check_production_endpoint("prod01", PROD_HEALTH_ENDPOINTS["prod01"])

@app.task(cron(minute="5,15,25,35,45,55"))
def check_prod02_health():
    check_production_endpoint("prod02", PROD_HEALTH_ENDPOINTS["prod02"])

@app.task('every 4 hour')
def main():
    MAX_RETRIES = 5  # Número máximo de tentativas
    RETRY_COUNT = 0  # Contador de tentativas
    try:
        print("[INFO] Iniciando a verificação das instâncias...")
        
        while RETRY_COUNT < MAX_RETRIES:
            try:
                # Carrega a configuração das instâncias
                with open("instances.json", "r") as file:
                    instances = json.load(file)
                break  # Sai do loop se o carregamento for bem-sucedido    
            except FileNotFoundError as e:
                RETRY_COUNT += 1
                print(f"[ERRO] Arquivo de configuração não encontrado: {e}")
                send_discord_notification(f"[ERRO] Arquivo de configuração não encontrado: {e} <@&{ROLE_ID}>")
            except json.JSONDecodeError as e:
                RETRY_COUNT += 1
                print(f"[ERRO] Erro no formato do arquivo de configuração: {e}")
                send_discord_notification(f"[ERRO] Erro no formato do arquivo de configuração: {e} <@&{ROLE_ID}>")
            except Exception as e:
                RETRY_COUNT += 1
                print(f"[ERRO] Não foi possível carregar o arquivo de configuração: {e}")
                send_discord_notification(f"[ERRO] Não foi possível carregar o arquivo de configuração: {e} <@&{ROLE_ID}>")

            if RETRY_COUNT < MAX_RETRIES:
                print(f"[INFO] Tentando novamente em 1 minuto... ({RETRY_COUNT}/{MAX_RETRIES})")
                time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente
            else:
                print(f"[CRÍTICO] Limite de {MAX_RETRIES} tentativas atingido. Abortando.")
                send_discord_notification(f"[CRÍTICO] Limite de {MAX_RETRIES} tentativas atingido. Verifique o sistema. <@&{ROLE_ID}>")
                return  # Sai da função ou interrompe a execução

        # Verifica cada instância
        for instance in instances:
            result = check_instance_online(instance)
            print(result)

        print("[INFO] Verificação concluída. Aguardando 1 hora para a próxima execução.")
        send_discord_notification(f"[INFO] Verificação das instâncias concluída.")

    
    except KeyboardInterrupt:
        print("\n[INFO] Interrupção manual detectada. Encerrando o script.")
        send_discord_notification(f"[INFO] Script de verificação encerrado manualmente. <@&{ROLE_ID}>")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        send_discord_notification(f"[ERRO] Erro inesperado: {e} <@&{ROLE_ID}>")

if __name__ == "__main__":
    app.run()
