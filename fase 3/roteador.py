import socket
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol

ROUTER_HOST = '0.0.0.0'
ROUTER_PORT = 6000

COR_ROXA = '\033[95m'
COR_AMARELA = '\033[93m'
COR_VERMELHA = '\033[91m'
COR_RESET = '\033[0m'

tabela_roteamento = {
    "SERVIDOR PRIME": ("127.0.0.1", 5000),
}

tabela_conhecidos = {}

def iniciar_roteador():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((ROUTER_HOST, ROUTER_PORT))
        print(f"{COR_AMARELA}[INFO]{COR_RESET} Roteador (Fase 3) iniciado em {ROUTER_HOST}:{ROUTER_PORT}")
        print(f"{COR_AMARELA}[INFO]{COR_RESET} Rotas estáticas carregadas: {list(tabela_roteamento.keys())}")
    except Exception as e:
        print(f"{COR_VERMELHA}[ERRO]{COR_RESET} Falha ao iniciar Roteador: {e}")
        return

    print("Aguardando pacotes de rede...\n" + "="*50)

    while True:
        try:
            dados, endereco_remetente = sock.recvfrom(4096)
            dados_decodificados = dados.decode('utf-8')
            
            try:
                pacote_recebido = json.loads(dados_decodificados)
                
                src_vip = pacote_recebido.get('src_vip')
                dst_vip = pacote_recebido.get('dst_vip')
                ttl = pacote_recebido.get('ttl', 0)
                payload = pacote_recebido.get('data')
                
                print(f"{COR_ROXA}[REDE - ROTEADOR]{COR_RESET} Pacote recebido de {endereco_remetente}")
                print(f"  -> Origem VIP: {src_vip}")
                print(f"  -> Destino VIP: {dst_vip}")
                print(f"  -> TTL atual: {ttl}")
                
                if src_vip and src_vip not in tabela_roteamento:
                    if src_vip not in tabela_conhecidos or tabela_conhecidos[src_vip] != endereco_remetente:
                        print(f"{COR_ROXA}[REDE - ROTEAMENTO]{COR_RESET} Atualizando rota para '{src_vip}' -> {endereco_remetente}")
                        tabela_conhecidos[src_vip] = endereco_remetente

                if ttl <= 1:
                    print(f"{COR_VERMELHA}[REDE - ROTEADOR]{COR_RESET} Pacote dropado. TTL expirou (Time Exceeded) para {dst_vip}.")
                    print("-" * 50)
                    continue
                    
                ttl -= 1
                print(f"  -> Decrementando TTL para: {ttl}")
                
                destino_real = tabela_roteamento.get(dst_vip) or tabela_conhecidos.get(dst_vip)
                
                if destino_real:
                    print(f"{COR_ROXA}[REDE - ROTEAMENTO]{COR_RESET} Encaminhando pacote para {destino_real[0]}:{destino_real[1]}")
                    
                    pacote_encaminhar = protocol.Pacote(src_vip, dst_vip, ttl, payload)
                    bytes_encaminhar = json.dumps(pacote_encaminhar.to_dict()).encode('utf-8')
                    
                    protocol.enviar_pela_rede_ruidosa(sock, bytes_encaminhar, destino_real)
                else:
                    print(f"{COR_VERMELHA}[REDE - ROTEADOR]{COR_RESET} Destino '{dst_vip}' inatingível. Rota não encontrada.")
                    
                print("-" * 50)
                
            except json.JSONDecodeError:
                print(f"{COR_VERMELHA}[ERRO FÍSICO/JSON]{COR_RESET} Roteador recebeu string ininteligível de {endereco_remetente}. Drop.")
                
        except KeyboardInterrupt:
            print(f"\n{COR_AMARELA}[INFO]{COR_RESET} Encerrando Roteador.")
            break
        except Exception as e:
            print(f"{COR_VERMELHA}[ERRO INESPERADO]{COR_RESET} {e}")

    sock.close()

if __name__ == "__main__":
    iniciar_roteador()
