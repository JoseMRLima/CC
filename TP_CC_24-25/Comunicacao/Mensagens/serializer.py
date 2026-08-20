import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from este.Comunicacao.Mensagens.mensagem import Mensagem
from este.Comunicacao.Telemetria.telemetria import Telemetria
from este.Comunicacao.Mensagens.missons import Missao, ColetaAmostras, CapturaImagens, AnaliseAmbiental
from este.Comunicacao.Mensagens.update import UpdateAmostras, UpdateImagens, UpdateAmbiental
from este.Comunicacao.Mensagens.final import FinalAmostras, FinalImagens, FinalAmbiental



def int_to_bytes(value, length):
    return [(value >> (8 * (length - 1 - i))) & 0xFF for i in range(length)]

def bytes_to_int(b):
    v = 0
    for x in b:
        v = (v << 8) | x
    return v

def serialize_str(s):
    b = [ord(c) for c in s]
    return [len(b)] + b

def deserialize_str(data, offset):
    length = data[offset]
    start = offset + 1
    end = start + length
    return ''.join(chr(c) for c in data[start:end]), end


def serialize_missao(m: Missao):
    data = []

    # tipo da missão
    data.append(m.tipo)

    # strings
    data.extend(serialize_str(m.misson_id))

    # coordenadas
    x, y = m.coordenadas
    data.extend(int_to_bytes(x, 2))
    data.extend(int_to_bytes(y, 2))

    # tempos
    data.extend(int_to_bytes(m.tempo_limite, 2))
    data.extend(int_to_bytes(m.update_interval, 2))

    if isinstance(m, ColetaAmostras):
        data.extend(serialize_str(m.tipo_amostra))

    elif isinstance(m, CapturaImagens):
        data.extend(int_to_bytes(m.max_fotos, 2))

    return data


def deserialize_missao(data, offset=0):
    tipo = data[offset]; offset += 1

    mission_id, offset = deserialize_str(data, offset)

    x = bytes_to_int(data[offset:offset+2]); offset += 2
    y = bytes_to_int(data[offset:offset+2]); offset += 2

    tempo_limite = bytes_to_int(data[offset:offset+2]); offset += 2
    update_interval = bytes_to_int(data[offset:offset+2]); offset += 2

    if tipo == 0:  # Coleta
        tipo_amostra, offset = deserialize_str(data, offset)
        m = ColetaAmostras(mission_id, (x, y), tempo_limite, update_interval, tipo_amostra)

    elif tipo == 1:  # Imagens
        max_fotos = bytes_to_int(data[offset:offset+2]); offset += 2
        m = CapturaImagens(mission_id, (x, y), tempo_limite, update_interval, max_fotos)

    elif tipo == 2:  # Ambiental
        m = AnaliseAmbiental(mission_id, (x, y), tempo_limite, update_interval)


    return m, offset


def serialize_update(u):
    data = []

    if isinstance(u, UpdateAmostras):
        data.append(0)
        data.extend(serialize_str(u.misson_id))
        data.extend(int_to_bytes(u.nr_amostras, 2))
        x, y = u.coordenadas
        data.extend(int_to_bytes(x, 2))
        data.extend(int_to_bytes(y, 2))

    elif isinstance(u, UpdateImagens):
        data.append(1)
        data.extend(serialize_str(u.misson_id))
        data.extend(int_to_bytes(u.nr_imagens, 2))
        x, y = u.coordenadas
        data.extend(int_to_bytes(x, 2))
        data.extend(int_to_bytes(y, 2))

    elif isinstance(u, UpdateAmbiental):
        data.append(2)
        data.extend(serialize_str(u.misson_id))
        data.extend(int_to_bytes(u.temperatura, 2))
        data.extend(int_to_bytes(u.pressao, 2))
        data.extend(int_to_bytes(u.umidade, 2))
        x, y = u.coordenadas
        data.extend(int_to_bytes(x, 2))
        data.extend(int_to_bytes(y, 2))

    return data


def deserialize_update(data, offset=0):
    tipo = data[offset]; offset += 1

    misson_id, offset = deserialize_str(data, offset)

    if tipo == 0:  # Amostras
        nr = bytes_to_int(data[offset:offset+2]); offset += 2
        x = bytes_to_int(data[offset:offset+2]); offset += 2
        y = bytes_to_int(data[offset:offset+2]); offset += 2
        return UpdateAmostras(misson_id, nr, (x, y)), offset

    elif tipo == 1:  # Imagens
        nr = bytes_to_int(data[offset:offset+2]); offset += 2
        x = bytes_to_int(data[offset:offset+2]); offset += 2
        y = bytes_to_int(data[offset:offset+2]); offset += 2
        return UpdateImagens(misson_id, nr, (x, y)), offset

    elif tipo == 2:  # Ambiental
        temp = bytes_to_int(data[offset:offset+2]); offset += 2
        press = bytes_to_int(data[offset:offset+2]); offset += 2
        umid = bytes_to_int(data[offset:offset+2]); offset += 2
        x = bytes_to_int(data[offset:offset+2]); offset += 2
        y = bytes_to_int(data[offset:offset+2]); offset += 2
        return UpdateAmbiental(misson_id, temp, press, umid, (x, y)), offset



def serialize_final(f):
    data = []

    if isinstance(f, FinalAmostras):
        data.append(0)
        data.extend(serialize_str(f.mission_id))
        data.extend(int_to_bytes(f.nr_amostras, 2))

    elif isinstance(f, FinalImagens):
        data.append(1)
        data.extend(serialize_str(f.mission_id))
        imgs = f.imagens
        data.append(len(imgs))

        for img in imgs:
            if isinstance(img, str):
                img = [ord(c) for c in img]

            data.extend(int_to_bytes(len(img), 2))
            data.extend(img)

    elif isinstance(f, FinalAmbiental):
        data.append(2)
        data.extend(serialize_str(f.mission_id))

        lt = f.lista_temperatura
        lp = f.lista_pressao
        lu = f.lista_umidade

        data.append(len(lt))
        for v in lt:
            data.extend(int_to_bytes(v, 2))

        data.append(len(lp))
        for v in lp:
            data.extend(int_to_bytes(v, 2))

        data.append(len(lu))
        for v in lu:
            data.extend(int_to_bytes(v, 2))

    return data


def deserialize_final(data, offset=0):
    tipo = data[offset]; offset += 1

    mission_id, offset = deserialize_str(data, offset)

    if tipo == 0:
        nr = bytes_to_int(data[offset:offset+2]); offset += 2
        return FinalAmostras(mission_id, nr), offset

    elif tipo == 1:
        n = data[offset]; offset += 1
        imgs = []
        for _ in range(n):
            size = bytes_to_int(data[offset:offset+2]); offset += 2
            img = bytes(data[offset:offset+size])
            offset += size
            imgs.append(img)
        return FinalImagens(mission_id, imgs), offset

    elif tipo == 2:
        lt = []
        lp = []
        lu = []

        n_t = data[offset]; offset += 1
        for _ in range(n_t):
            val = bytes_to_int(data[offset:offset+2]); offset += 2
            lt.append(val)

        n_p = data[offset]; offset += 1
        for _ in range(n_p):
            val = bytes_to_int(data[offset:offset+2]); offset += 2
            lp.append(val)

        n_u = data[offset]; offset += 1
        for _ in range(n_u):
            val = bytes_to_int(data[offset:offset+2]); offset += 2
            lu.append(val)

        return FinalAmbiental(mission_id, lt, lp, lu), offset


def serialize_message(msg: Mensagem):
    data = []

    data.append(msg.tipo)
    data.append(msg.seq)

    rover_bytes = [ord(c) for c in msg.rover_id]
    ts_bytes = [ord(c) for c in msg.timestamp]

    data.append(len(rover_bytes))
    data.append(len(ts_bytes))

    if msg.tipo == 3 or msg.tipo == 4:
        payload = []

    elif msg.tipo == 0:
        payload = serialize_missao(msg.payload)

    elif msg.tipo == 1:
        payload = serialize_update(msg.payload)

    elif msg.tipo == 2:
        payload = serialize_final(msg.payload)

    data.extend(int_to_bytes(len(payload), 2))

    data.extend(rover_bytes)
    data.extend(ts_bytes)
    data.extend(payload)

    return bytes(data)


def deserialize_message(buf: bytes):
    data = list(buf)
    offset = 0

    tipo = data[offset]; offset += 1
    seq  = data[offset]; offset += 1

    rid_len = data[offset]; offset += 1
    ts_len  = data[offset]; offset += 1

    payload_len = bytes_to_int(data[offset:offset+2]); offset += 2

    rover_id = ''.join(chr(c) for c in data[offset:offset+rid_len])
    offset += rid_len

    timestamp = ''.join(chr(c) for c in data[offset:offset+ts_len])
    offset += ts_len

    payload_data = data[offset:offset+payload_len]

    if tipo == 0:
        payload, _ = deserialize_missao(payload_data)
    elif tipo == 1:
        payload, _ = deserialize_update(payload_data)
    elif tipo == 2:
        payload, _ = deserialize_final(payload_data)
    else:
        payload = None

    return Mensagem(tipo, rover_id, seq, timestamp, payload)


def serialize_telemetria(t: Telemetria):
    data = []

    data.extend(serialize_str(t.rover_id))

    data.extend(serialize_str(t.timestamp))

    x, y = t.coordenadas
    data.extend(int_to_bytes(int(x), 2))
    data.extend(int_to_bytes(int(y), 2))

    data.append(int(t.bateria))

    vel_int = int(t.velocidade * 100)
    data.extend(int_to_bytes(vel_int, 2))

    temp_int = int(t.temperatura * 100)
    data.extend(int_to_bytes(temp_int, 2))

    data.extend(serialize_str(t.estado))

    return bytes(data)


def deserialize_telemetria(data):

    if isinstance(data, bytes):
        data = list(data)

    offset = 0

    rover_id, offset = deserialize_str(data, offset)

    timestamp, offset = deserialize_str(data, offset)

    x = bytes_to_int(data[offset:offset + 2])
    offset += 2
    y = bytes_to_int(data[offset:offset + 2])
    offset += 2

    bateria = data[offset]
    offset += 1

    vel_int = bytes_to_int(data[offset:offset + 2])
    offset += 2
    velocidade = vel_int / 100.0

    temp_int = bytes_to_int(data[offset:offset + 2])
    offset += 2
    temperatura = temp_int / 100.0

    estado, offset = deserialize_str(data, offset)

    return Telemetria(rover_id, timestamp, (x, y), bateria, velocidade, temperatura, estado)


def serialize_snapshot(telemetria_dict, mission_store_dict):
    data = []

    data.extend(int_to_bytes(len(telemetria_dict), 2))

    for tele_obj in telemetria_dict.values():
        t_bytes = serialize_telemetria(tele_obj)
        data.extend(int_to_bytes(len(t_bytes), 2))
        data.extend(t_bytes)
    data.extend(int_to_bytes(len(mission_store_dict), 2))

    for m_data in mission_store_dict.values():
        data.extend(serialize_str(m_data.get("mission_id", "?")))
        data.extend(serialize_str(m_data.get("rover_id", "?")))
        data.extend(serialize_str(m_data.get("status", "?")))
        data.extend(serialize_str(m_data.get("type", "?")))

        n_updates = len(m_data.get("updates", []))
        data.extend(int_to_bytes(n_updates, 2))

    return bytes(data)


def deserialize_snapshot(data):
    if isinstance(data, bytes):
        data = list(data)

    offset = 0
    snapshot = {"telemetry": {}, "missions": []}

    n_rovers = bytes_to_int(data[offset:offset + 2])
    offset += 2

    for _ in range(n_rovers):
        block_len = bytes_to_int(data[offset:offset + 2])
        offset += 2
        tele_bytes = data[offset:offset + block_len]
        offset += block_len

        t_obj = deserialize_telemetria(tele_bytes)
        snapshot["telemetry"][t_obj.rover_id] = t_obj

    n_missions = bytes_to_int(data[offset:offset + 2])
    offset += 2

    for _ in range(n_missions):
        mid, offset = deserialize_str(data, offset)
        rid, offset = deserialize_str(data, offset)
        status, offset = deserialize_str(data, offset)
        mtype, offset = deserialize_str(data, offset)
        n_updates = bytes_to_int(data[offset:offset + 2])
        offset += 2

        snapshot["missions"].append({
            "id": mid, "rover": rid, "status": status, "type": mtype, "updates": n_updates
        })

    return snapshot