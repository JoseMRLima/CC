class Mensagem:
    def __init__(self, tipo, rover_id, seq, timestamp, payload):
        self.tipo = tipo
        self.rover_id = rover_id
        self.seq = seq
        self.timestamp = timestamp
        self.payload = payload

    def display(self):
        print("Tipo:", self.tipo)
        print("Rover:", self.rover_id)
        print("Seq:", self.seq)
        print("Timestamp:", self.timestamp)

        payload = self.payload

        if payload is None:
            print("Payload: None")
            return

        print("\nPayload:", payload.__class__.__name__)

        for nome, valor in payload.__dict__.items():
            print(f"  {nome}: {valor}")

