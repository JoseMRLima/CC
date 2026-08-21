import threading
import time
import json
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from este.Comunicacao.MissionLink.mission_link import MissionLinkProtocol
from este.Comunicacao.Mensagens.missons import ColetaAmostras, CapturaImagens, AnaliseAmbiental
from este.Comunicacao.Mensagens.mensagem import Mensagem
from este.Comunicacao.Telemetria.telemetry_server import start_telemetry_server
from este.Comunicacao.MissionLink.mission_store import register_mission_message, register_update_message, \
    register_final_message, mission_state
from este.Comunicacao.Mensagens.serializer import serialize_snapshot
from este.Nave.api_server import configure_api, run_api

IP_NAVE = "0.0.0.0"
PORTA_UDP = 8888
PORTA_TCP = 9000
PORTA_GC = 5000

telemetria_atual = {}
fila_missoes = []
contador_aleatorio = 1

nave_seq = 0


def get_nave_seq():
    global nave_seq
    nave_seq += 1
    return nave_seq


def carregar_missoes_locais():
    global fila_missoes
    try:
        with open("missoes_config.json", "r") as f:
            dados = json.load(f)

        for m in dados:
            mid = m["id"]
            coords = tuple(m["coords"])
            tempo = m["tempo"]
            up_interval = m["update_interval"]
            tipo = m["tipo"]
            param = m.get("parametro")

            if tipo == "coleta":
                obj = ColetaAmostras(mid, coords, tempo, up_interval, param)
            elif tipo == "fotos":
                obj = CapturaImagens(mid, coords, tempo, up_interval, int(param))
            elif tipo == "ambiental":
                obj = AnaliseAmbiental(mid, coords, tempo, up_interval)

            fila_missoes.append(obj)

        print(f"[NAVE] {len(fila_missoes)} missões predefinidas carregadas.")

    except FileNotFoundError:
        print("[NAVE] 'missoes_config.json' não encontrado. A iniciar em modo 100% aleatório.")
    except Exception as e:
        print(f"[NAVE] Erro ao ler configuração: {e}")


def gerar_missao_aleatoria(rover_id):
    global contador_aleatorio

    mid = f"M-RND-{contador_aleatorio:03d}"
    contador_aleatorio += 1

    x = random.randint(0, 50)
    y = random.randint(0, 50)
    coords = (x, y)

    tempo = random.randint(30, 60)
    update = 5  # segundos

    escolha = random.choice(["coleta", "fotos", "ambiental"])

    if escolha == "coleta":
        tipo_amostra = random.choice(["Rochas", "Solo", "Gelo", "Po"])
        return ColetaAmostras(mid, coords, tempo, update, tipo_amostra)

    elif escolha == "fotos":
        max_fotos = random.randint(3, 10)
        return CapturaImagens(mid, coords, tempo, update, max_fotos)

    elif escolha == "ambiental":
        return AnaliseAmbiental(mid, coords, tempo, update)


def main():
    carregar_missoes_locais()

    t_tcp = threading.Thread(target=start_telemetry_server, args=(telemetria_atual, IP_NAVE, PORTA_TCP))
    t_tcp.daemon = True
    t_tcp.start()

    configure_api(telemetria_atual, mission_state)

    t_api = threading.Thread(target=run_api, args=(IP_NAVE, PORTA_GC))
    t_api.daemon = True
    t_api.start()
    print(f"[NAVE-GC] API HTTP a correr na porta {PORTA_GC}...")

    ml = MissionLinkProtocol(IP_NAVE, PORTA_UDP, role='server')
    print(f"[NAVE] Sistema de Missão (UDP) a ouvir na porta {PORTA_UDP}...")

    while True:
        try:
            msg, addr = ml.listen_packet()

            if msg:
                rover_id = msg.rover_id

                if msg.tipo == 3:  # Pedido de missão
                    print(f"[NAVE] Pedido de missão recebido de {rover_id} (Seq Req: {msg.seq})")

                    if len(fila_missoes) > 0:
                        missao_atual = fila_missoes.pop(0)
                        origem = "PREDEFINIDA"
                    else:
                        missao_atual = gerar_missao_aleatoria(rover_id)
                        origem = "ALEATORIA"

                    seq_envio = get_nave_seq()
                    resposta = Mensagem(0, rover_id, seq_envio, time.strftime("%d/%m/%Y-%H:%M:%S"), missao_atual)

                    # Tenta enviar e só regista se tiver sucesso (True)
                    if ml.send(resposta, addr):
                        register_mission_message(resposta)
                        print(f"[NAVE] Missão {missao_atual.misson_id} ({origem}) atribuída a {rover_id} (Seq Resp: {seq_envio})")
                    
                    else:
                        # Se falhou, avisamos e tratamos
                        print(f"[NAVE] ERRO CRÍTICO: Falha ao enviar missão {missao_atual.misson_id} para {rover_id}.")
                        
                        # Se a missão era da lista fixa, devolvemos à fila para tentar noutro pedido!
                        if origem == "PREDEFINIDA":
                            fila_missoes.insert(0, missao_atual)
                            print("[NAVE] A missão foi devolvida ao início da fila.")

                elif msg.tipo == 1:  # Update
                    print(f"[NAVE] Update recebido de {rover_id} (Seq: {msg.seq})")
                    register_update_message(msg)

                elif msg.tipo == 2:  # Conclusão
                    print(f"[NAVE] Conclusão recebida de {rover_id} (Seq: {msg.seq})")
                    register_final_message(msg)

            else:
                continue
        except KeyboardInterrupt:
            print("\nA desligar Nave...")
            ml.close()
            break
        except Exception as e:
            print(f"[NAVE] Erro no loop principal: {e}")


if __name__ == "__main__":
    main()