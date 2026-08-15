import time
import threading
import sys
import os
import json
import urllib.request
import urllib.error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

NAVEMA_IP = "10.0.6.10"
API_PORT = 5000
API_URL = f"http://{NAVEMA_IP}:{API_PORT}/api/status"

ESTADO_ATUAL = {
    "telemetry": {},
    "missions": []
}
data_lock = threading.Lock()


def network_listener():
    global ESTADO_ATUAL

    while True:
        try:
            with urllib.request.urlopen(API_URL, timeout=3) as response:
                if response.status == 200:
                    data_str = response.read().decode('utf-8')
                    data = json.loads(data_str)

                    with data_lock:
                        ESTADO_ATUAL = data

        except urllib.error.URLError:
            pass
        except Exception as e:
            print(f"\n[!] Erro de conexão: {e}")

        time.sleep(1)


def ver_rovers():
    print("=== ESTADO DOS ROVERS ===")
    with data_lock:
        tele = ESTADO_ATUAL.get("telemetry", {})
        if not tele:
            print("\n[!] Nenhum dado de telemetria recebido ainda.")
        else:
            print(f"\n{'ID':<10} | {'BAT':<6} | {'TEMP':<6} | {'POS':<12} | {'ESTADO'}")
            print("-" * 60)
            for rid, t in tele.items():
                bat = t.get('bateria', 0)
                temp = t.get('temperatura', 0)
                pos = str(t.get('coordenadas', [0, 0]))
                estado = t.get('estado', 'Unknown')
                print(f"{rid:<10} | {bat:.0f}%   | {temp:.0f}C   | {pos:<12} | {estado}")
    input("\n[Enter] Voltar ao menu...")


def ver_missoes():
    print("===  HISTÓRICO E MISSÕES ATIVAS ===")
    with data_lock:
        missoes = ESTADO_ATUAL.get("missions", [])
        if not missoes:
            print("\n[!] Nenhuma missão registada.")
        else:
            print(f"\n{'ID':<12} | {'Rover':<10} | {'Tipo':<15} | {'Status'}")
            print("-" * 60)
            for m in reversed(missoes):
                mid = m.get('mission_id', m.get('id', 'N/A'))
                rover = m.get('rover_id', m.get('rover', 'N/A'))
                mtype = m.get('type', 'Unknown')
                status = m.get('status', 'Unknown')
                print(f"{mid:<12} | {rover:<10} | {mtype:<15} | {status}")
    input("\n[Enter] Voltar ao menu...")


def ver_detalhe_missao():
    mid_alvo = input("\nDigite o ID da Missão: ").strip()
    found = None
    with data_lock:
        missoes = ESTADO_ATUAL.get("missions", [])
        for m in missoes:
            curr_id = m.get('mission_id', m.get('id'))
            if curr_id == mid_alvo:
                found = m
                break
    if found:
        print(f"\n--- Detalhes de {found.get('mission_id')} ---")
        print(f"Rover Responsável: {found.get('rover_id')}")
        print(f"Tipo de Missão:    {found.get('type')}")
        print(f"Estado Atual:      {found.get('status')}")
        print(f"Updates Recebidos: {len(found.get('updates', []))}")
    else:
        print(f"\n[!] Missão {mid_alvo} não encontrada.")
    input("\n[Enter] Voltar ao menu...")


def main():
    t = threading.Thread(target=network_listener)
    t.daemon = True
    t.start()
    print(f"A conectar à API em {API_URL}...")
    time.sleep(1)

    while True:
        print("╔════════════════════════════════════╗")
        print("║           GROUND CONTROL           ║")
        print("╠════════════════════════════════════╣")
        print("║  1 - Ver Estado dos Rovers         ║")
        print("║  2 - Ver Lista de Missões          ║")
        print("║  3 - Detalhes de uma Missão        ║")
        print("║  0 - Sair                          ║")
        print("╚════════════════════════════════════╝")

        try:
            opcao = input("Opção > ").strip()
            if opcao == "1":
                ver_rovers()
            elif opcao == "2":
                ver_missoes()
            elif opcao == "3":
                ver_detalhe_missao()
            elif opcao == "0":
                break
            else:
                input("Opção inválida...")
        except EOFError:
            break


if __name__ == "__main__":
    main()