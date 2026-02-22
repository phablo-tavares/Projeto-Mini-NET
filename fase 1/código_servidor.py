import socket
import json

HOST = '0.0.0.0'
PORT = 5000

COR_VERDE = '\033[92m'
COR_AMARELA = '\033[93m'
COR_VERMELHA = '\033[91m'
COR_RESET = '\033[0m'

def iniciar_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((HOST, PORT))
        print(f"{COR_AMARELA}[INFO]{COR_RESET} Servidor UDP iniciado e escutando em {HOST}:{PORT}")
    except Exception as e:
        print(f"{COR_VERMELHA}[ERRO]{COR_RESET} Falha ao iniciar ou vincular o socket do servidor: {e}")
        return

    print("Aguardando mensagens...")

    while True:
        try:
            dados, endereco_cliente = sock.recvfrom(4096)
            dados_decodificados = dados.decode('utf-8')
            
            try:
                mensagem_json = json.loads(dados_decodificados)
                
                remetente = mensagem_json.get('sender', 'Desconhecido')
                texto = mensagem_json.get('message', '')
                timestamp = mensagem_json.get('timestamp', '00:00:00')
                
                print(f"{COR_VERDE}[MSG APLICAÇÃO]{COR_RESET} [{timestamp}] {remetente} ({endereco_cliente[0]}): {texto}")
                
            except json.JSONDecodeError:
                print(f"{COR_VERMELHA}[ERRO FÍSICO/JSON]{COR_RESET} Pacote corrompido ou mal formado de {endereco_cliente}. Dados brutos: {dados_decodificados}")
                
        except KeyboardInterrupt:
            print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Encerrando o servidor de forma segura.")
            break
        except Exception as e:
            print(f"{COR_VERMELHA}[ERRO INESPERADO]{COR_RESET} {e}")

    sock.close()

if __name__ == "__main__":
    iniciar_servidor()
