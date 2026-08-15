import time
import random
import math
from TP2.Comunicacao.Mensagens.missons import *
from TP2.Comunicacao.Mensagens.update import *
from TP2.Comunicacao.Mensagens.final import *
from TP2.Comunicacao.Mensagens.serializer import *
from TP2.Comunicacao.Mensagens.mensagem import Mensagem


def exec_coleta(missao, rover, ml):
    inicio = time.time()
    ultimo_update = inicio

    amostras = 0
    chegou = False
    dest_x, dest_y = missao.coordenadas

    while (time.time() - inicio) < missao.tempo_limite:
        tick = 0.5
        time.sleep(tick)

        if not chegou:
            chegou = rover.mover(dest_x, dest_y, tick)
        else:
            rover.update(rover.x, rover.y, 0, 0.1, 0.05)
            if random.random() < 0.35:
                amostras += 1

        if (time.time() - ultimo_update) >= missao.update_interval:
            up = UpdateAmostras(missao.misson_id, amostras, (rover.x, rover.y))
            msg = Mensagem(1, rover.id, rover.next(), time.strftime("%d/%m/%Y %H:%M:%S"), up)
            
            if not ml.send(msg):
                print(f"[EXEC] Falha crítica no update (Coleta). Abortando...")
                return
            
            ultimo_update = time.time()

    final = FinalAmostras(missao.misson_id, amostras)
    msg_final = Mensagem(2, rover.id, rover.next(), time.strftime("%d/%m/%Y %H:%M:%S"), final)
    
    if not ml.send(msg_final):
        print(f"[EXEC] Falha crítica no envio final (Coleta).")
        return

    chegou_posto = False
    while not chegou_posto:
        chegou_posto = rover.mover(0, 0, 0.5)
        if chegou_posto:
            rover.carregar()

    rover.estado = "idle"


def exec_fotos(missao, rover, ml):
    inicio = time.time()
    ultimo_update = inicio

    fotos = 0
    chegou = False
    dest_x, dest_y = missao.coordenadas
    fotos_image = []

    while (time.time() - inicio) < missao.tempo_limite:
        tick = 0.5
        time.sleep(tick)

        if not chegou:
            chegou = rover.mover(dest_x, dest_y, tick)
        else:
            rover.update(rover.x, rover.y, 0, 0.1, 0.05)
            if random.random() < 0.35 and fotos < missao.max_fotos:
                time.sleep(5)
                fotos += 1
                img = f"img/fotos/{fotos}.png"
                fotos_image.append(img)

        if (time.time() - ultimo_update) >= missao.update_interval:
            up = UpdateImagens(missao.misson_id, fotos, (rover.x, rover.y))
            msg = Mensagem(1, rover.id, rover.next(), time.strftime("%d/%m/%Y %H:%M:%S"), up)
            
            if not ml.send(msg):
                print(f"[EXEC] Falha crítica no update (Fotos). Abortando...")
                return
            
            ultimo_update = time.time()

    final = FinalImagens(missao.misson_id, fotos_image)
    msg_final = Mensagem(2, rover.id, rover.next(), time.strftime("%d/%m/%Y %H:%M:%S"), final)
    
    if not ml.send(msg_final):
        print(f"[EXEC] Falha crítica no envio final (Fotos).")
        return

    rover.estado = "idle"


def ler_sensor(t_med=20, t_amp=5, h_med=60, h_amp=20, p_med=1013, p_amp=2, ruido=0.1):
    agora = time.localtime()
    hora_decimal = agora.tm_hour + (agora.tm_min / 60) + (agora.tm_sec / 3600)

    ciclo = 2 * math.pi * (hora_decimal - 14) / 24
    temp_base = t_med + t_amp * math.cos(ciclo)
    hum_base = h_med - h_amp * math.cos(ciclo)

    ciclo_12h = 2 * math.pi * (hora_decimal - 10) / 12
    pressao = p_med + p_amp * math.cos(ciclo_12h)

    temp_final = temp_base + random.uniform(-ruido, ruido)
    hum_final0 = hum_base + random.uniform(-ruido, ruido)
    pressao_final = pressao + random.uniform(-ruido * 0.5, ruido * 0.5)

    hum_final = max(0, min(100, hum_final0))

    return round(temp_final), round(hum_final), round(pressao_final)


def exec_analise(missao, rover, ml):
    inicio = time.time()
    ultimo_update = inicio

    chegou = False
    dest_x, dest_y = missao.coordenadas

    temperatura = []
    pressao = []
    humidade = []

    while (time.time() - inicio) < missao.tempo_limite:
        tick = 0.5
        time.sleep(tick)

        if not chegou:
            chegou = rover.mover(dest_x, dest_y, tick)
        else:
            rover.update(rover.x, rover.y, 0, 0.1, 0.05)

        if (time.time() - ultimo_update) >= missao.update_interval:
            temp, hum, pre = ler_sensor()
            temperatura.append(temp)
            humidade.append(hum)
            pressao.append(pre)

            up = UpdateAmbiental(missao.misson_id, temp, pre, hum, (rover.x, rover.y))
            msg = Mensagem(1, rover.id, rover.next(), time.strftime("%d/%m/%Y %H:%M:%S"), up)
            
            if not ml.send(msg):
                print(f"[EXEC] Falha crítica no update (Análise). Abortando...")
                return

            ultimo_update = time.time()

    final = FinalAmbiental(missao.misson_id, temperatura, pressao, humidade)
    msg_final = Mensagem(2, rover.id, rover.next(), time.strftime("%d/%m/%Y %H:%M:%S"), final)
    
    if not ml.send(msg_final):
        print(f"[EXEC] Falha crítica no envio final (Análise).")
        return
    
    rover.estado = "idle"