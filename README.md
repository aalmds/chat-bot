# Chat-bot

Este é um projeto da disciplina Infraestrutura de Comunicação e nosso objetivo é implementar um chat utilizando cliente e servidor UDP com transmissão confiável (rdt3.0).

## Pré-requisitos

Antes de começar, você vai precisar ter instalado em sua máquina as seguintes ferramentas:

- [Python 3](https://www.python.org/downloads/)

- [Biblioteca termcolor](https://pypi.org/project/termcolor/)

```bash
  pip install termcolor
```

## Como usar

Primeiramente, rodamos o servidor, com o seguinte comando:

```bash
  python3 server.py
```

Depois disso, em terminais diferentes rodamos cada cliente, com o seguinte comando:

```bash
  python3 client.py
```

### Comandos

Nosso chat possui as seguintes funcionalidades que podem ser solicitadas através de linhas de comando pelos clientes:

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

- Mensagem particular (inbox):

```bash
  @<nome_de_usuario> <mensagem>
```

- Expulsão:

```bash
  ban @<nome_de_usuario>
```

## Contribuidores

- [Andresa Almeida da Silva](https://github.com/aalmds)
- [Joao Marcos Alcantara Vanderley](https://github.com/jmarcossss)
- [Maria Clara Alves Acruchi](https://github.com/acrucha)
- [Maria Vitoria Soares Muniz](https://github.com/mariavmuniz)
