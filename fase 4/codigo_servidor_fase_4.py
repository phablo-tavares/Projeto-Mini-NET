import socket
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol

HOST = '0.0.0.0'
PORT = 5000

MEU_VIP = "SERVIDOR PRIME"

MEU_MAC = "MAC_SERVIDOR"
ROUTER_MAC = "MAC_ROTEADOR"

ROUTER_IP = '127.0.0.1' 
ROUTER_PORT = 6000

COR_VERDE = '\033[92m'
COR_AMARELA = '\033[93m'
COR_AZUL = '\033[94m'
COR_ROXA = '\033[95m'
COR_VERMELHA = '\033[91m'
COR_RESET = '\033[0m'

def iniciar_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((HOST, PORT))
        print(f"{COR_AMARELA}[INFO]{COR_RESET} Servidor (Fase 4) escutando fisicamente em {HOST}:{PORT}")
        print(f"{COR_AMARELA}[INFO]{COR_RESET} Endereço VIP: {MEU_VIP}")
    except Exception as e:
        print(f"{COR_VERMELHA}[ERRO]{COR_RESET} Falha ao iniciar ou vincular o socket do servidor: {e}")
        return

    print("Aguardando pacotes roteados...")
    print("=" * 50)
    seq_esperado = 0

    while True:
        try:
            dados, endereco_roteador = sock.recvfrom(4096)
            
            quadro_dict, integro = protocol.Quadro.deserializar(dados)
            
            if not integro:
                print(f"{COR_VERMELHA}[ENLACE]{COR_RESET} Quadro corrompido (Erro CRC). Descartando silenciosamente.")
                continue
                 
            if quadro_dict.get('dst_mac') != MEU_MAC:
                print(f"{COR_AMARELA}[ENLACE]{COR_RESET} Quadro ignorado. MAC destino diferente do meu.")
                continue
                 
            pacote_recebido = quadro_dict.get('data', {})
            
            src_vip = pacote_recebido.get('src_vip')
            dst_vip = pacote_recebido.get('dst_vip')
            ttl = pacote_recebido.get('ttl')
            segmento_recebido = pacote_recebido.get('data', {})
                
            print(f"{COR_ROXA}[REDE]{COR_RESET} Pacote capturado!")
            
            if dst_vip != MEU_VIP:
                print(f"{COR_AMARELA}[REDE]{COR_RESET} Descartado. Destino virtual '{dst_vip}' não me pertence.")
                continue
                
            print(f"{COR_ROXA}[REDE]{COR_RESET} Entregue para meu VIP '{MEU_VIP}' (Vindo de '{src_vip}', TTL restante: {ttl})")
            
            seq_num = segmento_recebido.get('seq_num')
            is_ack = segmento_recebido.get('is_ack')
            payload = segmento_recebido.get('payload', {})
            
            if is_ack:
                continue
            
            print(f"{COR_AZUL}[TRANSPORTE]{COR_RESET} Segmento Recebido - SEQ: {seq_num}")

            if seq_num == seq_esperado:
                remetente = payload.get('sender', 'Desconhecido')
                texto = payload.get('message', '')
                timestamp = payload.get('timestamp', '00:00:00')
                
                print(f"{COR_VERDE}[MSG APLICAÇÃO]{COR_RESET} [{timestamp}] {remetente} (Endereço Lógico: {src_vip}): {texto}")
                seq_esperado = 1 - seq_esperado
            else:
                print(f"{COR_AMARELA}[TRANSPORTE]{COR_RESET} Duplicata de Transporte (SEQ {seq_num}). Sem subir as camadas.")

            ack = protocol.Segmento(seq_num=seq_num, is_ack=True, payload={})
            
            pacote_resposta = protocol.Pacote(
                src_vip=MEU_VIP,
                dst_vip=src_vip,
                ttl=5,
                segmento_dict=ack.to_dict()
            )
            
            quadro_resposta = protocol.Quadro(
                src_mac=MEU_MAC,
                dst_mac=ROUTER_MAC,
                pacote_dict=pacote_resposta.to_dict()
            )
            
            quadro_bytes = quadro_resposta.serializar()
            
            print(f"{COR_ROXA}[REDE]{COR_RESET} Despachando pacote ACK de volta através do gateway {endereco_roteador[0]}:{endereco_roteador[1]}")
            protocol.enviar_pela_rede_ruidosa(sock, quadro_bytes, endereco_roteador)
            print("-" * 50)
                
        except KeyboardInterrupt:
            print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Encerrando o servidor de forma segura.")
            break
        except Exception as e:
            print(f"{COR_VERMELHA}[ERRO INESPERADO]{COR_RESET} {e}")

    sock.close()

if __name__ == "__main__":
    iniciar_servidor()
