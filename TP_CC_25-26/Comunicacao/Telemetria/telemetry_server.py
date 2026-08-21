import socket
import threading
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from este.Comunicacao.Mensagens.serializer import deserialize_telemetria



def handle_rover(conn, addr, estado):
    print(f"[TCP] Nova conexão de telemetria: {addr}")

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            try:
                tele = deserialize_telemetria(data)
            except Exception as e:
                print(f"[TELEMETRIA] Pacote inválido de {addr}: {e}")
                continue
            
            estado[tele.rover_id] = tele

            print(f"[TELEMETRIA] {tele.rover_id} | Bat: {tele.bateria}% "
                  f"| Pos: {tele.coordenadas} | Estado: {tele.estado}")

        except Exception as e:
            print(f"[TCP] Erro com {addr}: {e}")
            break

    print(f"[TCP] Desconectado: {addr}")
    conn.close()



def start_telemetry_server(estado, host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[SERVIDOR TCP] TelemetryStream a ouvir na porta {port}...")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_rover, args=(conn, addr, estado))
            thread.daemon = True
            thread.start()

    except Exception as e:
        print(f"[SERVIDOR TCP] Erro fatal: {e}")
    finally:
        server.close()

