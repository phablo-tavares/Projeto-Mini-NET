import socket
import json
from datetime import datetime

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
    except Exception as e:
        print(f"{COR_VERMELHA}[ERRO]{COR_RESET} Não foi possível criar o socket UDP: {e}")
        return

    print(f"{COR_AZUL}="*50)
    print(f"   BEM-VINDO AO CHAT MINI-NET (FASE 1)   ")
    print(f"="*50 + COR_RESET)
    print("Digite '/sair' a qualquer momento para encerrar.\n")
    
    remetente = input(f"{COR_AMARELA}Digite seu nome de usuário: {COR_RESET}").strip()
    if not remetente:
        remetente = "Anônimo"
        
    print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Tudo pronto! Enviando mensagens para {SERVER_IP}:{SERVER_PORT}")
    print("-" * 50)
    
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
            
            dados_json = json.dumps(dados_dict)
            
            dados_bytes = dados_json.encode('utf-8')
            
            sock.sendto(dados_bytes, (SERVER_IP, SERVER_PORT))
            
        except KeyboardInterrupt:
            print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Fechamento forçado detectado. Encerrando o cliente.")
            break
        except Exception as e:
            print(f"{COR_VERMELHA}[ERRO INESPERADO]{COR_RESET} Falha ao enviar a mensagem: {e}")

    sock.close()

if __name__ == "__main__":
    iniciar_cliente()
