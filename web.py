#!/usr/bin/env python
# web - Aplicação para processar o SMS recebido no hook
#
# O hook de SMS irá chamar essa aplicação para obter uma resposta
#
# @author: Luiz Fernando da Silva Souza <luiz.souza@shopper.com.br>


import json
import datetime
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer


PORT = 5009
# Porta HTTP para ficar ouvindo
LOG_LEVEL = logging.INFO
# Nível do log


def handleSms(body):
    """Processa uma requisição de SMS"""
    data = json.loads(body)
    if data["message"] == "ERRO":
        return "", 501
    elif data["message"] == "CAFE":
        return "com leite", 201
    elif data["message"] == "AGORA":
        return datetime.datetime.now().isoformat(), 200
    else:
        return "", 200


class handler(BaseHTTPRequestHandler):
    """Gerenciador de requisições"""
    def do_POST(self):
        """Processa uma requisição POST"""
        length = int(self.headers['content-length'])
        body = self.rfile.read(length)
        print("[+] Requisição recebida\n\tCaminho: {0}\n\tMétodo: {1}\n\tCorpo: {2}\n".format(
            self.path,
            self.command,
            body
        ))

        message = ""
        status = 400
        if self.path == "/sms":
            print("- Processando dados do SMS recebido...")
            message, status = handleSms(body)
        
        
        self.send_response(status)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))
        print(f"- Enviando resposta HTTP {status}: {message}...")
        print("\n")


def main():
    print("[+] Inicializando servidor web...")
    logging.basicConfig(format="%(levelname)s: %(message)s", level=LOG_LEVEL)
    with HTTPServer(('', PORT), handler) as server:
        print(f"[+] Aguardando requisições na porta {PORT}...")
        server.serve_forever()


if __name__ == "__main__":
    main()