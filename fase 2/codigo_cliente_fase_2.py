import socket
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol

SERVER_IP = '34.57.243.31' 
SERVER_PORT = 5000

COR_VERDE = '\033[92m'
COR_AMARELA = '\033[93m'
COR_AZUL = '\033[94m'
COR_RESET = '\033[0m'
COR_VERMELHA = '\033[91m'

def iniciar_cliente():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
    except Exception as e:
        print(f"{COR_VERMELHA}[ERRO]{COR_RESET} Não foi possível criar o socket UDP: {e}")
        return

    print(f"{COR_AZUL}="*50)
    print(f"   BEM-VINDO AO CHAT MINI-NET (FASE 2)   ")
    print(f"="*50 + COR_RESET)
    print("Digite '/sair' a qualquer momento para encerrar.\n")
    
    remetente = input(f"{COR_AMARELA}Digite seu nome de usuário: {COR_RESET}").strip()
    if not remetente:
        remetente = "Anônimo"
        
    print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Tudo pronto! Enviando mensagens para {SERVER_IP}:{SERVER_PORT}")
    print("-" * 50)
    
    seq_atual = 0

    while True:
        try:
            mensagem_texto = input(f"{COR_VERDE}Você > {COR_RESET}")
            
            if mensagem_texto.strip().lower() == '/sair':
                print(f"{COR_AMARELA}[INFO]{COR_RESET} Você saiu do chat.")
                break
                
            if not mensagem_texto.strip():
                continue
                
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            dados_dict = {
                "sender": remetente,
                "message": mensagem_texto,
                "timestamp": timestamp
            }
            
            segmento = protocol.Segmento(seq_num=seq_atual, is_ack=False, payload=dados_dict)
            dados_json = json.dumps(segmento.to_dict()).encode('utf-8')
            
            ack_recebido = False
            
            while not ack_recebido:
                print(f"{COR_AZUL}[TRANSPORTE]{COR_RESET} Enviando pacote (SEQ {seq_atual}). Aguardando ACK...")
                protocol.enviar_pela_rede_ruidosa(sock, dados_json, (SERVER_IP, SERVER_PORT))
                
                try:
                    resposta_bytes, _ = sock.recvfrom(4096)
                    
                    try:
                        resposta_segmento = json.loads(resposta_bytes.decode('utf-8'))
                        seq_ack = resposta_segmento.get('seq_num')
                        is_ack = resposta_segmento.get('is_ack')
                        
                        if is_ack and seq_ack == seq_atual:
                            print(f"{COR_VERDE}[TRANSPORTE]{COR_RESET} ACK recebido para SEQ {seq_atual}. Mensagem confirmada!")
                            ack_recebido = True
                            seq_atual = 1 - seq_atual
                        else:
                            print(f"{COR_AMARELA}[TRANSPORTE]{COR_RESET} Mensagem inesperada ou duplicada ignorada.")
                            
                    except json.JSONDecodeError:
                        print(f"{COR_VERMELHA}[ERRO FÍSICO/JSON]{COR_RESET} Resposta corrompida. Tratando como perda de ACK.")
                
                except socket.timeout:
                    print(f"{COR_VERMELHA}[TRANSPORTE]{COR_RESET} Timeout ao aguardar ACK para SEQ {seq_atual}. Retransmitindo...")

        except KeyboardInterrupt:
            print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Fechamento forçado detectado. Encerrando o cliente.")
            break
        except Exception as e:
            print(f"{COR_VERMELHA}[ERRO INESPERADO]{COR_RESET} Falha ao enviar a mensagem: {e}")

    sock.close()

if __name__ == "__main__":
    iniciar_cliente()
