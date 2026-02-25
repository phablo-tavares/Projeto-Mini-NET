# Manual do Projeto Integrador: "A Mini-Net"

## Visão Geral

Este projeto é a implementação em Python de uma pilha de protocolos de rede customizado sobre UDP seguindo a abordagem Top-Down para a disciplina de Redes de Computadores.
As implementações se dividiram em 4 fases incrementais que tratam desde o fluxo de aplicações (JSON) até a garantia de confiabilidade nos envios (Enlace, Rede, Transporte).

## Infraestrutura e Ambiente (GCP)

Em sua concepção e fase de testes, o ambiente Servidor e o Roteador deste projeto foram hospedados em uma **Instância de Máquina Virtual (VM) no Google Cloud Platform (GCP Console)**. 

No entanto, vale deixar claro que **o servidor pode estar hospedado em qualquer lugar** — não importando se é sua rede local residencial ou qualquer outra provedora de nuvem —, contanto que haja o rigor de definir os IPs corretamente no código fonte do cliente/roteador apontando para ele.

### Regras de Firewall e Portas

Para que a comunicação UDP aconteça e o Servidor e o Roteador estejam expostos e escutando externamente de forma correta (como exigido pela VM do GCP, por exemplo), **regras de firewall rígidas precisaram ser estabelecidas**.
Foi necessário configurar uma regra no provedor de rede/firewall do servidor para:
- **Permitir tráfego UDP de qualquer origem** (IP `0.0.0.0/0`)
- **Nas portas 5000 e 6000**:
  - A porta `5000` está alocada para os scripts de Servidor do projeto.
  - A porta `6000` está alocada para os scripts atuando como Roteador (introduzido na Fase 3).

## Como testar o projeto (Fase a Fase)

O projeto pode ser avaliado individualmente, testando a evolução das fases do programa, caso cada passo abaixo seja seguido:

> **Onde rodar cada script?**
> Para o teste local, os scripts podem ser rodados na mesma máquina (em terminais separados). 
> Caso o professor queira rodar de forma descentralizada:
> - Os scripts de **`código_cliente*`** devem rodar na máquina do enviador/usuário.
> - Os scripts de **`código_servidor*`** devem rodar no ambiente atrelado à porta 5000 (Ex: Máquina Servidora).
> - Os scripts de **`roteador*`** (Fases 3 e 4) devem rodar num ambiente intermediário atrelado à porta 6000 (Ex: Outra VM ou a própria servidora).
> 
> Lembre-se de alterar as variáveis de host (`localhost` / IP reverso) nos scripts, conforme o seu ambiente de teste.
> 
> **Atenção sobre o `protocolo.py`:**
> Este arquivo **NÃO DEVE** ser executado diretamente em um terminal. No entanto, ele é a biblioteca que simula a rede e **DEVE estar fisicamente presente na mesma pasta** (junto aos códigos) tanto na máquina do **Cliente**, quanto na máquina do **Servidor**, e na máquina do **Roteador**. Sem esse arquivo presente nos ambientes, os scripts darão erro de importação nas Fases 2, 3 e 4!

### Fase 1: Aplicação e Sockets (Apenas JSON/Transferência Simples)
Nessa fase o foco é na Formatação JSON e numa comunicação local sem garantias da chegada baseada em nossa própria API.
**Passo a passo:**
1. Abra um terminal e execute o servidor:
   ```bash
   python "fase 1/código_servidor.py"
   ```
2. Abra outro terminal e execute o cliente:
   ```bash
   python "fase 1/código_cliente.py"
   ```
3. Envie uma mensagem pelo terminal do cliente para testar o bate-papo.

### Fase 2: Transporte e Confiabilidade (Stop-and-Wait/Timeouts de UDP)
Nesta fase, a comunicação usa puramente UDP e simulamos o erro da rede via `protocolo.py` garantindo que os clientes aguardem `ACK` ou retransmitam a mensagem usando a técnica de Timeout de Stop-and-wait.
**Passo a passo:**
1. Primeiramente derrube/feche os scripts da Fase 1 se estiverem abertos.
2. Inicie o servidor da Fase 2:
   ```bash
   python "fase 2/codigo_servidor_fase_2.py"
   ```
3. Inicie o cliente:
   ```bash
   python "fase 2/codigo_cliente_fase_2.py"
   ```
4. Ao enviar mensagens, repare os logs exibindo o andamento da entrega e a recepção do ACK de controle.

### Fase 3: Rede e Roteamento (Roteador Intermediário)
O Cliente não conversa mais diretamente com o Servidor. Um serviço intermediário (Roteador) lê e encaminha mensagens e os destinos viram lógicos ("SERVIDOR PRIME" etc).
**Passo a passo:**
1. Feche os aplicativos das Fases anteriores.
2. Inicie o servidor:
   ```bash
   python "fase 3/codigo_servidor_fase_3.py"
   ```
3. Inicie o Roteador numa porta correspondente intermediária:
   ```bash
   python "fase 3/roteador_fase_3.py"
   ```
4. Inicie o Cliente:
   ```bash
   python "fase 3/codigo_cliente_fase_3.py"
   ```
5. Envie uma mensagem e acompanhe nos terminais o Roteador fazendo a ponte usando a resolução de nomes.

### Fase 4: Enlace e Integridade (Comprovação CRC32 e MAC Absoluto)
A fase final estabelece o Checksum / Cálculo e Verificação de Erros pelo CRC32 para simular o meio físico.
**Passo a passo:**
1. Novamente, feche qualquer app de rede prévio.
2. Inicie o servidor final da Fase 4:
   ```bash
   python "fase 4/codigo_servidor_fase_4.py"
   ```
3. Inicie o roteador de redirecionamento:
   ```bash
   python "fase 4/roteador_fase_4.py"
   ```
4. Por fim, inicie o cliente:
   ```bash
   python "fase 4/codigo_cliente_fase_4.py"
   ```
5. Nessa fase final as falhas são descartadas silenciosamente se entrarem corrompidas, provando que a Camada de Transporte implementada anteriormente (Timeouts) entra em ação recuperando e reenviando a string.

## Restrições e Bibliotecas
- Foi utilizada a Linguagem **Python 3.8+**.
- Apenas as bibliotecas padrão de Python exigidas foram declaradas (`socket`, `sys`, `time`, `json`, `random`, `struct`, `zlib`, `threading`).
- O módulo `protocolo.py` atua globalmente simulando o desgaste real da rede física durante a operação.
