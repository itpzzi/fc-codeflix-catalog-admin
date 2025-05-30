# Projeto CodeFlix - Backend Django com Integração RabbitMQ

Este projeto implementa parte do backend da plataforma CodeFlix, com integração de filas RabbitMQ para processamento assíncrono de vídeos. Abaixo estão as instruções para executar o projeto, configurar variáveis de ambiente e rodar os testes end-to-end (E2E).

---

## 📦 Requisitos

- Python 3.11+
- Docker e Docker Compose
- Virtualenv

---

## ⚙️ Configuração do Ambiente

1. Crie e ative o ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Exporte as variáveis de ambiente necessárias:

Crie um arquivo `.env` com o seguinte conteúdo:

```env
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
PYTHONUNBUFFERED=1
PYTHONPATH=venv/bin/python
```

---

## 🐇 Subindo o RabbitMQ via Docker

Utilize o `docker-compose.yml` já incluso no projeto ou execute manualmente:

```bash
docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

---

## 🚀 Executando o Projeto

1. Aplique as migrações:

```bash
python manage.py migrate
```

2. Inicie o servidor Django:

```bash
python manage.py runserver
```

3. Inicie o consumer responsável pelo processamento das mensagens:

```bash
python manage.py startconsumer
```

---

## ✅ Testes End-to-End

Os testes E2E do desafio estão localizados em:

```bash
/src/tests_e2e/test_e2e_video_flow.py
```

### O que o teste faz:

- Cria instâncias de Category, Genre e CastMember via API.
- Cria um vídeo (sem mídia) via API.
- Faz upload da mídia do vídeo.
- Verifica publicação do evento `videos.new`.
- Simula publicação do evento `videos.converted`.
- Aguarda processamento.
- Verifica se o vídeo foi processado com `MediaStatus.COMPLETED`.

### Considerações sobre os testes:

1. Certifique-se de que o RabbitMQ está em execução via compose.
2. O consumer (`startconsumer`) será chamado nos testes via `call_command` para consumir apenas uma mensagem "once". É feito um sleep para certificar a leitura antes das asserções.
3. Execute os testes com:

```bash
pytest /src/tests_e2e/test_e2e_video_flow.py
```

---

## 📌 Observações

- As filas `videos.new` e `videos.converted` são purgadas inicialmente pelo teste para garantir que não há resquicios de mensagens anteriores.
- O teste simula um encoder finalizando o processamento do vídeo.
- Não é necessário atualizar manualmente o corpo da mensagem publicada com o ID real do vídeo, o teste faz isso automaticamente.
- Utilizei uma classe gerenciadora do RabbitMQ para facilitar a manipulação das mensagens e filas `src.tests.helpers.rabbitmq_test_manager.RabbitMQTestManager`

---
