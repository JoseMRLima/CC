class Missao:
    def __init__(self, misson_id, tipo, coordenadas, tempo_limite, update_interval):
        self.misson_id = misson_id
        self.tipo = tipo
        self.coordenadas = coordenadas
        self.tempo_limite = tempo_limite
        self.update_interval = update_interval

class ColetaAmostras(Missao):
    def __init__(self, mission_id, coordenadas, tempo_limite, update_interval, tipo_amostra):
        super().__init__(mission_id,0, coordenadas, tempo_limite, update_interval)
        self.tipo_amostra = tipo_amostra

    def display(self):
        print(self.misson_id, self.coordenadas, self.tempo_limite, self.update_interval, self.tipo_amostra)

class CapturaImagens(Missao):
    def __init__(self, mission_id, coordenadas, tempo_limite, update_interval, max_fotos):
        super().__init__(mission_id, 1, coordenadas, tempo_limite, update_interval)
        self.max_fotos = max_fotos

    def display(self):
        print(self.misson_id, self.coordenadas, self.tempo_limite, self.update_interval, self.max_fotos)

class AnaliseAmbiental(Missao):
    def __init__(self, mission_id, coordenadas, tempo_limite, update_interval):
        super().__init__(mission_id,2, coordenadas, tempo_limite, update_interval)

    def display(self):
        print(self.misson_id, self.coordenadas, self.tempo_limite, self.update_interval)