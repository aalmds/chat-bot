# Chat-bot

Projeto da disciplina Infraestrutura de Comunicação que tem o objetivo de implementar um chat de múltiplos clientes utilizando comunicação cliente-servidor com protocolo UDP e de transmissão confiável (rdt3.0).

## Setup inicial

Antes de começar, você precisa instalar, caso não tenha, as seguintes ferramentas:

- [Python 3.10](https://www.python.org/downloads/)

- [Termcolor](https://pypi.org/project/termcolor/)
```bash
  pip install termcolor
```
- [Typing](https://pypi.org/project/typing/)
```bash
  pip install typing
```

## Como usar

Primeiramente, abra um terminal e execute o servidor utilizando o seguinte comando:

```bash
  python3 server.py
```

Depois disso, abra um terminal para cada cliente e, em todos, execute o seguinte comando:

```bash
  python3 client.py
```

### Comandos

O chat possui as seguintes funcionalidades que podem ser solicitadas através de linhas de comando pelos clientes:

- Conectar à sala

```bash
  hi, meu nome eh <nome_de_usuario>
```

- Sair da sala:

```bash
  bye
```

- Exibir lista de usuários:

```bash
  list
```

- Enviar uma mensagem particular (inbox):

```bash
  @<nome_de_usuario> <mensagem>
```

- Solicitar banimento de um usuário:

```bash
  ban @<nome_de_usuario>
```

## Contribuidores

- [Andresa Almeida da Silva](https://github.com/aalmds)
- [Joao Marcos Alcantara Vanderley](https://github.com/jmarcossss)
- [Maria Clara Alves Acruchi](https://github.com/acrucha)
- [Maria Vitoria Soares Muniz](https://github.com/mariavmuniz)
