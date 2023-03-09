# smshook

Script para receber SMS, chamar uma URL e enviar a resposta por SMS

É necessário ter um modem USB conectado e atualizar a porta em que ele está conectado na constante `PORT`.

Atualize a URL que deseja chamar ao receber o SMS na constante `WEBHOOK_URL`.

Atualize o número de telefone para ser notificado em casos de erro na constante `ADMIN_NUMBER`.

Execute o script com o comando:
```
python main.py
```

Existe uma versão simplificada de servidor para testes, execute com o comando:
```
python web.py
```
