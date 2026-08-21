class Telemetria:
    def __init__(self, rover_id, timestamp, coordenadas, bateria, velocidade, temperatura, estado):
        self.rover_id = rover_id
        self.timestamp = timestamp
        self.coordenadas = coordenadas
        self.bateria = bateria
        self.velocidade = velocidade
        self.temperatura = temperatura
        self.estado = estado
