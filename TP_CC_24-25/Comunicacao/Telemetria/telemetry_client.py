import socket
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from este.Rover.estado_rovers import EstadoRover
from este.Comunicacao.Mensagens.serializer import serialize_telemetria


def run_telemetria_loop(rover: EstadoRover, ip_nave, porta_tcp):
    print("[TCP] A iniciar serviço de telemetria...")

    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((ip_nave, porta_tcp))
            print(f"[TCP] Conectado à Nave {ip_nave}:{porta_tcp}")

            while True:
                tele = rover.get_telemetria()

                packet = serialize_telemetria(tele)
                s.sendall(packet)

                time.sleep(2)

        except Exception as e:
            print(f"[TCP] Ligação perdida ou falha: {e}. Reconectando em 5s...")
            if s: s.close()
            time.sleep(5)