import threading
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from TP2.Comunicacao.MissionLink.mission_link import MissionLinkProtocol
from TP2.Comunicacao.Mensagens.mensagem import Mensagem
from TP2.Comunicacao.Mensagens.missons import *
from estado_rovers import EstadoRover
from TP2.Comunicacao.Telemetria.telemetry_client import run_telemetria_loop
import exec_missions

porta = 8888
tcp = 9000


def consumir_bateria_sempre(rover):
    while True:
        time.sleep(1)
        rover.consumir_bateria()

        if rover.bateria <= 20 and rover.estado == "idle":
            chegou_posto = False
            while not chegou_posto:
                chegou_posto = rover.mover(0, 0, 0.5)
                if chegou_posto:
                    rover.carregar()


def main(id_str):
    rover_num = int(id_str)
    rover_id = f"R-{rover_num}"

    if rover_num == 12 or rover_num == 7:
        ip = "10.0.1.10"
    elif rover_num == 10 or rover_num == 11 or rover_num == 6:
        ip = "10.0.2.10"
    else:
        ip = "10.0.4.10"

    rover = EstadoRover(rover_id, 1, 1)
    ml = MissionLinkProtocol(ip, porta)

    # Threads auxiliares
    t_tcp = threading.Thread(target=run_telemetria_loop, args=(rover, ip, tcp))
    t_tcp.daemon = True
    t_tcp.start()

    t_bateria = threading.Thread(target=consumir_bateria_sempre, args=(rover,))
    t_bateria.daemon = True
    t_bateria.start()

    print(f"[ROVER] {rover_id} iniciado e pronto.")

    while True:
        if rover.estado == "idle":
            seq_pedido = rover.next()
            print(f"[ROVER] A pedir missão... (Seq: {seq_pedido})")
            pedido = Mensagem(3, rover_id, seq_pedido, time.strftime("%d/%m/%Y %H:%M:%S"), None)
            if not ml.send(pedido):
                print("[ROVER] Falha ao pedir missão (Rede). Tentando novamente...")
                time.sleep(2) 
                continue

        msg_recebido, addr = ml.listen_packet()


        if msg_recebido is None:
            continue

        elif msg_recebido.tipo == 0:
            missao = msg_recebido.payload
            print(f"[ROVER] Missão recebida: {missao.misson_id}")
            rover.estado = missao.misson_id

            if isinstance(missao, ColetaAmostras):
                exec_missions.exec_coleta(missao, rover, ml)
            elif isinstance(missao, CapturaImagens):
                exec_missions.exec_fotos(missao, rover, ml)
            elif isinstance(missao, AnaliseAmbiental):
                exec_missions.exec_analise(missao, rover, ml)
                
            print(f"[ROVER] Missão {missao.misson_id} terminada. Voltando a idle.")
            rover.estado = "idle"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rover.py <id>")
    else:
        main(sys.argv[1])