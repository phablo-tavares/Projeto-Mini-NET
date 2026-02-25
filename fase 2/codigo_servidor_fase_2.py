import socket
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol

HOST = '0.0.0.0'
PORT = 5000

COR_VERDE = '\033[92m'
COR_AMARELA = '\033[93m'
COR_AZUL = '\033[94m'
COR_VERMELHA = '\033[91m'
COR_RESET = '\033[0m'

def iniciar_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((HOST, PORT))
        print(f"{COR_AMARELA}[INFO]{COR_RESET} Servidor UDP (Fase 2) iniciado e escutando em {HOST}:{PORT}")
    except Exception as e:
        print(f"{COR_VERMELHA}[ERRO]{COR_RESET} Falha ao iniciar ou vincular o socket do servidor: {e}")
        return

    print("Aguardando mensagens...")
    
    seq_esperado = 0

    while True:
        try:
            dados, endereco_cliente = sock.recvfrom(4096)
            
            try:
                dados_decodificados = dados.decode('utf-8')
                segmento_recebido = json.loads(dados_decodificados)
                
                seq_num = segmento_recebido.get('seq_num')
                is_ack = segmento_recebido.get('is_ack')
                payload = segmento_recebido.get('payload', {})
                
                if is_ack:
                    print(f"{COR_AMARELA}[TRANSPORTE]{COR_RESET} ACK recebido inesperadamente de {endereco_cliente}. Ignorando.")
                    continue
                
                print(f"{COR_AZUL}[TRANSPORTE]{COR_RESET} Segmento recebido de {endereco_cliente[0]}:{endereco_cliente[1]} - SEQ: {seq_num}")

                if seq_num == seq_esperado:
                    remetente = payload.get('sender', 'Desconhecido')
                    texto = payload.get('message', '')
                    timestamp = payload.get('timestamp', '00:00:00')
                    
                    print(f"{COR_VERDE}[MSG APLICAÇÃO]{COR_RESET} [{timestamp}] {remetente} ({endereco_cliente[0]}): {texto}")
                    
                    seq_esperado = 1 - seq_esperado
                else:
                    print(f"{COR_AMARELA}[TRANSPORTE]{COR_RESET} Duplicata detectada (SEQ {seq_num}). Pacote descartado na aplicação.")

                ack = protocol.Segmento(seq_num=seq_num, is_ack=True, payload={})
                ack_json = json.dumps(ack.to_dict()).encode('utf-8')
                
                print(f"{COR_AZUL}[TRANSPORTE]{COR_RESET} Preparando ACK (SEQ {seq_num}) para {endereco_cliente[0]}:{endereco_cliente[1]}")
                
                protocol.enviar_pela_rede_ruidosa(sock, ack_json, endereco_cliente)
                print("-" * 50)
                
            except json.JSONDecodeError:
                print(f"{COR_VERMELHA}[ERRO FÍSICO/JSON]{COR_RESET} Pacote corrompido ou mal formado de {endereco_cliente}. Ignorando.")
                
        except KeyboardInterrupt:
            print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Encerrando o servidor de forma segura.")
            break
        except Exception as e:
            print(f"{COR_VERMELHA}[ERRO INESPERADO]{COR_RESET} {e}")

    sock.close()

if __name__ == "__main__":
    iniciar_servidor()
