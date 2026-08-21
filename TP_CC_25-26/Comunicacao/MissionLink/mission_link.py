import socket
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from este.Comunicacao.Mensagens.mensagem import Mensagem
from este.Comunicacao.Mensagens.serializer import serialize_message, deserialize_message

timeout = 5
buffer = 100000


class MissionLinkProtocol:
    def __init__(self, ip, port, role="client"):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        if role == "server":
            self.socket.bind(self.addr)
        else:
            self.server_addr = (ip, port)
            self.socket.settimeout(timeout)

    def send(self, mensagem, dest=None):
        target = dest if dest else self.server_addr
        mens = serialize_message(mensagem)

        tentativas = 0
        max_tentativas = 5

        while tentativas < max_tentativas:
            try:
                self.socket.sendto(mens, target)
                self.socket.settimeout(timeout)
                data, addr = self.socket.recvfrom(buffer)

                ack_mensagem = deserialize_message(data)
                if ack_mensagem.tipo == 4 and ack_mensagem.seq == mensagem.seq:
                    return True

            except socket.timeout:
                tentativas += 1
                print(f"[MissionLink] Timeout envio seq {mensagem.seq}. Tentativa {tentativas}/{max_tentativas}")
            except Exception as e:
                print(f"[MissionLink] Erro crítico: {e}")
                break

        print(f"[MissionLink] Falha no envio seq {mensagem.seq} após {max_tentativas} tentativas.")
        return False

    def listen_packet(self):
        try:
            if self.socket.gettimeout() is not None:
                self.socket.settimeout(None)

            data, addr = self.socket.recvfrom(buffer)
            mensagem = deserialize_message(data)

            if mensagem.tipo == 4:
                return None, addr

            self.send_ack(mensagem.seq, mensagem.rover_id, addr)

            return mensagem, addr
        except Exception as e:
            return None, None

    def send_ack(self, seq_recebido, rover_id, addr):
        timestamp = time.strftime("%d/%m/%Y-%H:%M:%S")
        ack_msg = Mensagem(tipo=4, rover_id=rover_id, seq=seq_recebido, timestamp=timestamp, payload=None)
        data = serialize_message(ack_msg)
        self.socket.sendto(data, addr)

    def close(self):
        self.socket.close()