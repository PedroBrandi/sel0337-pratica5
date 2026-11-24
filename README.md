# sel0337-pratica5

### Integrantes:
* João Henrique Viana de Oliveira - 15462907
* Pedro Brandi Pereira - 15640990
* Uriah Rodrigues Martins - 15490750

Este projeto consiste na exploração do processo de boot de um sistema Linux embarcado e do controle de versão de código. Foi utilizada a Raspberry Pi com Raspberry Pi OS, e o objetivo foi fazer um programa iniciar sozinho junto com o sistema operacional, gerenciado pelo **systemd**, sem que ninguém precise fazer login e executá-lo manualmente. Todo o código foi versionado com **Git** e armazenados neste repositório do **GitHub**.

O objetivo do sistema divide-se em duas etapas: a primeira reproduz o exemplo do roteiro, em *bash script*, que acessa a GPIO diretamente pelo sistema de arquivos do Linux (`/sys/class/gpio`) para piscar um LED; a segunda é a atividade de entrega, que repete o processo com um programa em **Python** e acrescenta um programa executado quando o serviço é parado.

A explicação linha a linha de cada arquivo está na seção "Explicação dos códigos", mais abaixo.

## Funcionalidades Apresentadas

* **Pisca-pisca por bash script (`blink.sh`):** exporta a GPIO 18, configura como saída e, em um laço infinito, escreve 1 e 0 no arquivo de valor do pino com intervalo de 0,2 s, acendendo e apagando o LED.

* **Pisca-pisca por Python (`pisca_led.py`):** usa a biblioteca `gpiozero` para controlar o LED da GPIO 18, ligando e desligando em laço infinito com intervalo de 0,5 s. Registra uma função com o módulo `atexit` para apagar o LED quando o programa termina.

* **Programa de parada (`pisca_led_stop.py`):** executado pelo systemd quando o serviço é parado (`systemctl stop`). Imprime a mensagem "Pisca LED parado.", que fica registrada no log do serviço.

* **Serviços do systemd (`blink.service` e `pisca_led.service`):** *unit files* que descrevem como o systemd deve iniciar e parar cada programa e em que momento do boot ele entra em operação.

* **Controle de versão:** os códigos e histórico de alterações foram mantidos com Git e enviados ao GitHub por meio de commits e `git push`.

## Arquitetura Implementada

* **Init system (systemd):** após o kernel Linux ser carregado, o systemd inicia os serviços do sistema. Os *unit files* copiados para `/lib/systemd/system/` colocam os programas do projeto entre esses serviços.

* **Unit file:** cada arquivo `.service` possui três blocos:
  * `[Unit]`: descrição do serviço e ordem de inicialização (`After=multi-user.target`, ou seja, depois que o sistema chega ao modo multiusuário).
  * `[Service]`: o que executar ao iniciar (`ExecStart`) e, no `pisca_led.service`, o que executar ao parar (`ExecStop`).
  * `[Install]`: `WantedBy=multi-user.target`, que faz o serviço iniciar no boot quando habilitado com `systemctl enable`.

* **Controle do serviço (systemctl):** comando usado para iniciar (`start`), parar (`stop`), habilitar no boot (`enable`) e verificar o estado (`status`) dos serviços.

* **Acesso à GPIO:** o `blink.sh` acessa o pino pelo sistema de arquivos do Linux, enquanto o `pisca_led.py` usa a biblioteca `gpiozero`, que abstrai esse acesso.

* **Montagem:** LED ligado à GPIO 18 (pino físico 12) por um resistor limitador de corrente, com o outro terminal do LED no GND.

## Explicação dos códigos

### blink.sh
```bash
#!/bin/bash

# Exporta o GPIO 18, ou seja, cria a pasta gpio18 em /sys/class/gpio para podermos controlá-lo
echo 18 > /sys/class/gpio/export
# Configura o GPIO 18 como saída (out)
echo out > /sys/class/gpio/gpio18/direction

# Loop infinito
while [ 1 ]
	do
		# Escreve 1 no pino e LED acende
		echo 1 > /sys/class/gpio/gpio18/value
		# Espera 0,2 segundo
		sleep 0.2s
		# Escreve 0 no pino e LED apaga
		echo 0 > /sys/class/gpio/gpio18/value
		# Espera 0,2 segundo
		sleep 0.2s
	done
```

### blink.service
```ini
# Seção com informações gerais do serviço
[Unit]
# Nome/descrição exibido pelo systemd
Description=Blinker
# Só inicia depois que o sistema chegou ao estado multi-user.target
After=multi-user.target

# Seção que define como o serviço executa
[Service]
# Programa executado ao iniciar o serviço
ExecStart=/home/sel/0790/pratica5/blink.sh

# Seção que define quando o serviço é ativado
[Install]
# Com enable, o serviço inicia junto com o boot (multi-user.target)
WantedBy=multi-user.target
```

### pisca_led.py
```python
#!/bin/python3

# Importa a classe LED, que controla um pino GPIO como saída para um LED
from gpiozero import LED
# Importa a função sleep, que pausa o programa por alguns segundos
from time import sleep
# Importa o módulo atexit, que permite registrar uma função para rodar ao encerrar o programa
import atexit

# Cria o objeto led associado ao GPIO 18
led = LED(18)

# Função que apaga o LED
def saida():
    led.off()

# Registra a função saida para ser executada quando o programa terminar
atexit.register(saida)

# Loop infinito
while True:
    # Acende o LED
    led.on()
    # Espera 0,5 segundo
    sleep(0.5)
    # Apaga o LED
    led.off()
    # Espera 0,5 segundo
    sleep(0.5)
```

### pisca_led_stop.py
```python
#!/bin/python3

# Imprime a mensagem na tela 
print("Pisca LED parado.")
```

### pisca_led.service
```ini
# Seção com informações gerais do serviço
[Unit]
# Nome/descrição exibido pelo systemd
Description=Blinker
# Só inicia depois que o sistema chegou ao estado multi-user.target
After=multi-user.target

# Seção que define como o serviço executa
[Service]
# Programa executado ao iniciar o serviço
ExecStart=/home/sel/0790/pratica5/pisca_led.py
# Programa executado ao parar o serviço (systemctl stop)
ExecStop=/home/sel/0790/pratica5/pisca_led_stop.py

# Seção que define quando o serviço é ativado
[Install]
# Com enable, o serviço inicia junto com o boot (multi-user.target)
WantedBy=multi-user.target
```

## Conceitos e comandos utilizados

* **Boot da Raspberry Pi:** a GPU executa o primeiro código, carrega os bootloaders da partição `boot` do cartão microSD, depois o kernel Linux, e por fim o systemd inicia os serviços da partição `rootfs`.
* **systemd, systemctl, unit file, init system.**
* **Git:** `git config`, `git clone`, `git add`, `git commit`, `git push`, `git pull`, `git status`, `git log`.
* **GitHub:** repositório remoto, *Personal Access Token* para autenticação no `git push` e documentação em `README.md`.

## Imagens

### Montagem final
![Montagem final](imagens/Montagem%20final.jfif)

### Imagem do terminal
![Imagem do terminal](imagens/Imagem%20terminal.jfif)

## Controle de versão

O histórico completo de commits, gerado com `git log`, está no arquivo [`historico_git.txt`](historico_git.txt).

## Resultados obtidos

O resultado foi um serviço personalizado integrado ao systemd: após habilitado com `systemctl enable`, o programa que pisca o LED é iniciado automaticamente durante o boot da Raspberry Pi, sem intervenção do usuário, e aparece na lista de serviços iniciados com o estado `OK`. Ao parar o serviço com `systemctl stop`, o systemd executa o programa definido em `ExecStop`, e o `atexit` garante que o LED seja apagado. Além disso, o uso do Git e do GitHub permitiu manter o histórico de versões dos códigos e centralizar a documentação do projeto.

Tais resultados cumprem os objetivos esperados da prática.
