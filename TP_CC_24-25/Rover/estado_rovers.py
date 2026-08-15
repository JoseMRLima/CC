import threading
import math
import time
from TP2.Comunicacao.Telemetria.telemetria import Telemetria

class EstadoRover:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.velocidade = 0
        self.temperatura = 30
        self.bateria = 100
        self.estado = "idle"
        self.lock = threading.Lock()
        self.seq = 0

    def next(self):
        with self.lock:
            self.seq += 1
            return self.seq

    def consumir_bateria(self):
        with self.lock:
            if self.bateria > 0:
                self.bateria -= 0.05
                if self.bateria < 0: self.bateria = 0

    def update(self, x, y, vel, custo_bateria, custo_temperatura):
        with self.lock:
            self.x = x
            self.y = y
            self.velocidade = vel
            self.bateria -= custo_bateria
            self.temperatura += custo_temperatura

    def get_telemetria(self):
        with self.lock:
            return Telemetria(
                self.id,
                time.strftime("%d/%m/%Y %H:%M:%S"),
                (self.x, self.y),
                self.bateria,
                self.velocidade,
                self.temperatura,
                self.estado,
            )

    def mover(self, x, y, dt, vel_max = 10):
        with self.lock:
            curr_x, curr_y = self.x, self.y
            bateria = self.bateria

        if bateria <= 0:
            return False

        dx = x - curr_x
        dy = y - curr_y
        dist = math.sqrt(dx**2 + dy**2)

        if dist <= 0.5:
            self.update(x, y, 0, 0.01, 0.01)
            return True

        passo = vel_max * dt
        if passo > dist:
            passo = dist
        ratio = passo/dist

        novo_x = curr_x + dx * ratio
        novo_y = curr_y + dy * ratio

        self.update(round(novo_x), round(novo_y), vel_max, 0.05*dt, 0.02*dt)
        return False

    def carregar(self):
        self.estado = "Carregar"
        while self.bateria < 100:
            time.sleep(1)
            self.bateria += 1
        self.temperatura = 30
        self.estado = "idle"