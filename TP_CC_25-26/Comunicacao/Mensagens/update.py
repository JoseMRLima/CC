class Update:
    def __init__(self, misson_id,coordenadas):
        self.misson_id = misson_id
        self.coordenadas = coordenadas

class UpdateAmostras(Update):
    def __init__(self, misson_id, nr_amostras, coordenadas):
        super().__init__(misson_id, coordenadas)
        self.nr_amostras = nr_amostras


class UpdateImagens(Update):
    def __init__(self, misson_id, nr_imagens, coordenadas):
        super().__init__(misson_id, coordenadas)
        self.nr_imagens = nr_imagens

class UpdateAmbiental(Update):
    def __init__(self, misson_id, temperatura, pressao, umidade, coordenadas):
        super().__init__(misson_id, coordenadas)
        self.temperatura = temperatura
        self.pressao = pressao
        self.umidade = umidade