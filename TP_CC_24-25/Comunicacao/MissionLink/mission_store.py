import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from este.Comunicacao.Mensagens.mensagem import Mensagem
from este.Comunicacao.Mensagens.missons import ColetaAmostras, CapturaImagens, AnaliseAmbiental
from este.Comunicacao.Mensagens.update import UpdateAmostras, UpdateImagens, UpdateAmbiental
from este.Comunicacao.Mensagens.final import FinalAmostras, FinalImagens, FinalAmbiental

mission_state: Dict[str, Dict[str, Any]] = {}

current_dir = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.abspath(os.path.join(current_dir, '..', '..', 'Nave', 'historico_missoes.json'))

IMG_FOLDER = os.path.abspath(os.path.join(current_dir, '..', '..', 'Nave', 'imagens_recebidas'))

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

def save_to_disk():
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(mission_state, f, indent=4)
        print("[STORE] Dados persistidos em historico_missoes.json")
    except Exception as e:
        print(f"[STORE] Erro ao guardar JSON: {e}")

def register_mission_message(msg: Mensagem):
    m = msg.payload
    mid = m.misson_id

    if isinstance(m, ColetaAmostras): mtype = "ColetaAmostras"
    elif isinstance(m, CapturaImagens): mtype = "CapturaImagens"
    elif isinstance(m, AnaliseAmbiental): mtype = "AnaliseAmbiental"
    else: mtype = "Desconhecido"

    mission_state[mid] = {
        "mission_id": mid,
        "rover_id": msg.rover_id,
        "type": mtype,
        "status": "Active",
        "start_time": msg.timestamp,
        "target_coords": list(m.coordenadas),
        "updates": [],
        "final_result": None
    }

    save_to_disk()

def register_update_message(msg: Mensagem):
    u = msg.payload
    mid = u.misson_id

    if mid not in mission_state:
        mission_state[mid] = {
            "mission_id": mid,
            "rover_id": msg.rover_id,
            "status": "Active (Recovered)",
            "updates": []
        }

    payload = {"timestamp": msg.timestamp}

    if isinstance(u, UpdateAmostras):
        payload["kind"] = "UpdateAmostras"
        payload["nr_amostras"] = u.nr_amostras
        payload["pos"] = list(u.coordenadas)
    elif isinstance(u, UpdateImagens):
        payload["kind"] = "UpdateImagens"
        payload["nr_imagens"] = u.nr_imagens
        payload["pos"] = list(u.coordenadas)
    elif isinstance(u, UpdateAmbiental):
        payload["kind"] = "UpdateAmbiental"
        payload["temperatura"] = u.temperatura
        payload["pressao"] = u.pressao
        payload["umidade"] = u.umidade
        payload["pos"] = list(u.coordenadas)

    mission_state[mid]["updates"].append(payload)

def register_final_message(msg: Mensagem):
    f = msg.payload
    mid = f.mission_id

    if mid not in mission_state:
        mission_state[mid] = {"mission_id": mid, "updates": []}

    result = {"timestamp": msg.timestamp}

    if isinstance(f, FinalAmostras):
        result["kind"] = "FinalAmostras"
        result["total_amostras"] = f.nr_amostras

    elif isinstance(f, FinalImagens):
        result["kind"] = "FinalImagens"
        result["total_fotos"] = len(f.imagens)
        saved_files = []

        for i, img_bytes in enumerate(f.imagens):
            filename = f"{mid}_foto_{i+1}.png"
            filepath = os.path.join(IMG_FOLDER, filename)
            try:
                with open(filepath, "wb") as img_file:
                    img_file.write(img_bytes)
                saved_files.append(filename)
            except Exception as e:
                print(f"[STORE] Erro ao salvar imagem {filename}: {e}")
        
        result["ficheiros_imagens"] = saved_files

    elif isinstance(f, FinalAmbiental):
        result["kind"] = "FinalAmbiental"
        result["log_temperatura"] = f.lista_temperatura
        result["log_pressao"] = f.lista_pressao
        result["log_umidade"] = f.lista_umidade

    mission_state[mid]["final_result"] = result
    mission_state[mid]["status"] = "Completed"
    mission_state[mid]["end_time"] = msg.timestamp

    save_to_disk()