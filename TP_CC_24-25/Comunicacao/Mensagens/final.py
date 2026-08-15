class Final:
    def __init__(self, misson_id):
        self.mission_id = misson_id

class FinalAmostras(Final):
    def __init__(self, misson_id, nr_amostras):
        super().__init__(misson_id)
        self.nr_amostras = nr_amostras

class FinalImagens(Final):
    def __init__(self, misson_id, imagens):
        super().__init__(misson_id)
        self.imagens = imagens

class FinalAmbiental(Final):
    def __init__(self, mission_id, lista_temperatura, lista_pressao, lista_umidade):
        super().__init__(mission_id)
        self.lista_temperatura = lista_temperatura
        self.lista_pressao = lista_pressao
        self.lista_umidade = lista_umidade