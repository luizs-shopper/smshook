#!/usr/bin/env python
# smshook - Aplicação para recebimento de SMS
# 
# Ao receber uma mensagem SMS a aplicação chama um endpoint da web e responde
# o SMS com a mensagem de retorno deste endpoint
# 
# @author: Luiz Fernando da Silva Souza <luiz.souza@shopper.com.br>


import logging
import traceback
import requests
from gsmmodem.modem import GsmModem


PORT = "/dev/ttyACM0"
# Porta serial do Modem GSM
BAUDRATE = 115200
# Taxa de pulsos por segundo
PIN = None
# PIN do cartão SIM, se existir
WEBHOOK_URL = "http://172.26.0.3:5009/sms"
# URL que deve ser chamada ao receber um SMS
WEBHOOK_TIMEOUT = 2000
# Tempo em milissegundos para esperar a resposta do endpoint
ADMIN_NUMBER = "+5511974957861"
# Número para enviar notificações de erro
LOG_LEVEL = logging.INFO
# Nível do log


def handleError(error, message):
    """Faz log do stack trace"""
    trace = ''.join(traceback.format_exception(None,  error, error.__traceback__))
    request = error.request if hasattr(error, 'request') else None
    response = error.response if hasattr(error, 'response') else None
    body = f"""{message}

    Request:
        URL: {request.url if request is not None else 'N/A'}
        Method: {request.method if request is not None else 'N/A'}
        Headers:
        {request.headers if request is not None else 'N/A'}
        Data:
        {request.body if request is not None and request.body else 'N/A'}
    
    Response:
        Status: {response.status_code if response is not None else 'N/A'}
        Data:
        {response.text if response is not None else 'N/A'}
    
    Traceback:
        {trace}
    """
    print(body)


def callWebhook(number: str, time: str, message: str) -> str:
    """Chama o webhook e devolve a resposta"""
    feedback_message = None
    admin_message = None
    try:
        response = requests.post(WEBHOOK_URL, json={
            "number": number,
            "time": time.isoformat(),
            "message": message
        }, timeout=WEBHOOK_TIMEOUT)
        response.raise_for_status()
        feedback_message = response.text
    except requests.ConnectionError as error:
        admin_message = "CONNECTION ERROR RAISED"
        handleError(error, admin_message)
    except requests.Timeout as error:
        admin_message = "TIMEOUT ERROR RAISED"
        handleError(error, admin_message)
    except requests.HTTPError as error:
        admin_message = f"HTTP ERROR {error.response.status_code} RAISED"
        handleError(error, admin_message)
    except Exception as error:
        admin_message = "UNKNOWN ERROR RAISED"
        handleError(error, admin_message)
    return feedback_message, admin_message


def handleSms(sms):
    """Processa um SMS recebido"""
    number = sms.number
    time = sms.time
    message = sms.text
    print(u"[+] SMS recebido\n\tDe: {0}\n\tÀs: {1}\n\tMensagem: {2}\n".format(
        number,
        time,
        message
    ))
    print("- Chamando webhook...")
    feedback, admin = callWebhook(number, time, message)
    if feedback:
        print(f"- Respondendo o SMS: {feedback[:100]}...")
        sms.reply(feedback[:100])
        print("- Resposta enviada.")
    if admin:
        print(f"- Enviando notificação para o administrador: {admin[:100]}")
        sms.sendSms(ADMIN_NUMBER, admin[:100])
        print("- Notificação enviada.")
    print("\n")


def main():
    print("[+] Inicializando modem...")
    logging.basicConfig(format="%(levelname)s: %(message)s", level=LOG_LEVEL)
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=handleSms)
    modem.smsTextMode = False
    modem.connect(PIN)
    print("[+] Aguardando por mensagem SMS...")
    try:
        modem.rxThread.join(2**31)
    finally:
        modem.close()


if __name__ == "__main__":
    main()
