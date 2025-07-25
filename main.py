import pygame
import sys
from cartas import Carta
from truco import (
    nueva_partida, repartir, quien_gana, calcular_tanto,
    cpu_decide_envido, cpu_decide_truco, cpu_responde_envido, cpu_responde_truco,
    tiene_flor, calcular_flor
)

WIDTH, HEIGHT = 960, 640
TABLE_COLOR = (0, 110, 0)
FPS = 60

def boton(pantalla, x, y, texto, activo=True):
    color = (0,180,0) if activo else (150,150,150)
    rect = pygame.Rect(x, y, 170, 48)
    pygame.draw.rect(pantalla, color, rect, border_radius=12)
    pygame.draw.rect(pantalla, (0,0,0), rect, 2, border_radius=12)
    font = pygame.font.SysFont("arialblack", 30)
    txt = font.render(texto, True, (255,255,255))
    pantalla.blit(txt, (x+24, y+8))
    return rect

def cartel_tantos(pantalla, tanto_jugador, tanto_cpu, flor=False):
    font_tanto = pygame.font.SysFont("arialblack", 36)
    if flor:
        texto = f"Tu Flor: {tanto_jugador}   CPU: {tanto_cpu}"
    else:
        texto = f"Tu tanto: {tanto_jugador}   CPU: {tanto_cpu}"
    txt = font_tanto.render(texto, True, (255,255,0))
    pantalla.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 40))
    pygame.display.flip()
    pygame.time.wait(1700)

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Truco Argentino SUPER PRO")
    clock = pygame.time.Clock()

    jugadores, mano = nueva_partida()
    turno = mano
    jugada_mesa = [None, None]
    ronda = 1
    mensaje = "¡Arrastrá una carta o cantá Truco/Envido/Flor!"
    game_over = False

    dragging = False
    carta_drag = None
    offset_x = 0
    offset_y = 0
    drag_index = None

    canto_estado = {
        "truco": 0,
        "envido": None,
        "flor": None
    }
    esperando_respuesta = False
    respuesta_pendiente = None
    quien_canto = None
    puntos_envido = {"Envido":2, "Real Envido":3, "Falta Envido":15}
    puntos_truco = [1,2,3]
    puntos_flor = 3

    resultado_envido = None
    resultado_truco = None
    resultado_flor = None

    while True:
        pantalla.fill(TABLE_COLOR)
        font = pygame.font.SysFont("arialblack", 36)

        pygame.draw.rect(pantalla, (0,80,0), (360,230,240,140), border_radius=30)
        pygame.draw.rect(pantalla, (0,0,0), (370,240,220,120), 2, border_radius=24)

        for i, carta in enumerate(jugadores[0]["jugadas"]):
            carta.dibujar(pantalla, 400 + i*40, 340)
        for i, carta in enumerate(jugadores[1]["jugadas"]):
            carta.dibujar(pantalla, 460 + i*40, 200)

        if jugada_mesa[0]:
            jugada_mesa[0].dibujar(pantalla, 400 + len(jugadores[0]["jugadas"])*40, 340)
        if jugada_mesa[1]:
            jugada_mesa[1].dibujar(pantalla, 460 + len(jugadores[1]["jugadas"])*40, 200)

        mouse = pygame.mouse.get_pos()
        for i, carta in enumerate(jugadores[0]["mano"]):
            if dragging and i == drag_index:
                continue
            x = 260 + i*110
            y = 480
            hover = carta.colisiona(mouse) and not dragging
            sombreada = False
            carta.dibujar(pantalla, x, y, seleccionada=False, hover=hover, sombreada=sombreada)
            carta.rect.topleft = (x, y)

        if dragging and carta_drag is not None:
            carta_drag.dibujar(pantalla, carta_drag.rect.x, carta_drag.rect.y, seleccionada=True)

        for i, carta in enumerate(jugadores[1]["mano"]):
            x = 260 + i*110
            y = 60
            carta.dibujar(pantalla, x, y, tapada=True)

        pygame.draw.rect(pantalla, (255,255,255), (0,0,WIDTH,56))
        marcador = font.render(f"{jugadores[0]['nombre']}: {jugadores[0]['puntos']}   {jugadores[1]['nombre']}: {jugadores[1]['puntos']}", True, (30,30,30))
        pantalla.blit(marcador, (WIDTH//2 - marcador.get_width()//2, 8))
        font_peq = pygame.font.SysFont("arialblack", 24)
        mano_txt = font_peq.render(f"Mano: {jugadores[mano]['nombre']}", True, (255,150,0))
        pantalla.blit(mano_txt, (30, 12))
        ronda_txt = font_peq.render(f"Ronda: {ronda}", True, (30,30,30))
        pantalla.blit(ronda_txt, (WIDTH-140, 12))

        btns = {}
        if not game_over and not esperando_respuesta:
            btns["truco"] = boton(
                pantalla, 60, 380, 
                ["Truco", "Retruco", "Vale Cuatro"][canto_estado["truco"]], 
                activo= turno == 0 and canto_estado["truco"] < 3
            )
            if canto_estado["envido"] is None and not tiene_flor(jugadores[0]["mano"]):
                btns["envido"] = boton(
                    pantalla, 60, 440, "Envido", 
                    activo= turno == 0
                )
                btns["realenvido"] = boton(
                    pantalla, 250, 440, "Real Envido", 
                    activo= turno == 0
                )
                btns["faltaenvido"] = boton(
                    pantalla, 440, 440, "Falta Envido", 
                    activo= turno == 0
                )
            if canto_estado["flor"] is None and tiene_flor(jugadores[0]["mano"]):
                btns["flor"] = boton(
                    pantalla, 60, 500, "Flor", activo=turno == 0
                )
        btn_quiero, btn_no_quiero = None, None
        cartel = None
        if esperando_respuesta:
            font_resp = pygame.font.SysFont("arialblack", 28)
            txt = ""
            if respuesta_pendiente[0] == "envido":
                txt = f"¿Querés el {canto_estado['envido']}?"
            elif respuesta_pendiente[0] == "truco":
                txt = ["¿Querés el Truco?", "¿Querés el Retruco?", "¿Querés el Vale Cuatro?"][canto_estado["truco"]-1]
            elif respuesta_pendiente[0] == "flor":
                txt = f"¿Querés la Flor?"
            cartel = font_resp.render(txt, True, (255,255,0))
            pantalla.blit(cartel, (WIDTH//2 - cartel.get_width()//2, 320))
            btn_quiero = boton(pantalla, WIDTH//2 - 180, 380, "Quiero", True)
            btn_no_quiero = boton(pantalla, WIDTH//2 + 20, 380, "No quiero", True)

        font_msg = pygame.font.SysFont("arial", 30)
        msg = font_msg.render(mensaje, True, (255,255,255))
        pygame.draw.rect(pantalla, (0,0,0), (0, HEIGHT-54, WIDTH, 54))
        pantalla.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT-44))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif esperando_respuesta and event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if btn_quiero and btn_quiero.collidepoint(pos):
                    esperando_respuesta = False
                    if respuesta_pendiente[0] == "envido":
                        resultado_envido = "Quiero"
                    elif respuesta_pendiente[0] == "truco":
                        resultado_truco = "Quiero"
                        mensaje = "¡Truco querido!"
                    elif respuesta_pendiente[0] == "flor":
                        resultado_flor = "Quiero"
                elif btn_no_quiero and btn_no_quiero.collidepoint(pos):
                    esperando_respuesta = False
                    if respuesta_pendiente[0] == "envido":
                        resultado_envido = "No quiero"
                    elif respuesta_pendiente[0] == "truco":
                        resultado_truco = "No quiero"
                        mensaje = "No quisiste el Truco."
                    elif respuesta_pendiente[0] == "flor":
                        resultado_flor = "No quiero"
            elif not esperando_respuesta and event.type == pygame.MOUSEBUTTONDOWN and not game_over and turno == 0 and not dragging:
                pos = pygame.mouse.get_pos()
                for i, carta in enumerate(jugadores[0]["mano"]):
                    if carta.colisiona(pos):
                        dragging = True
                        carta_drag = carta
                        drag_index = i
                        offset_x = carta.rect.x - pos[0]
                        offset_y = carta.rect.y - pos[1]
                        break
                if "truco" in btns and btns["truco"].collidepoint(pos):
                    quien_canto = "jugador"
                    canto_estado["truco"] += 1
                    mensaje = ["¡Truco cantado!", "¡Retruco!", "¡Vale Cuatro!"][canto_estado["truco"]-1]
                    esperando_respuesta = True
                    respuesta_pendiente = ("truco", "cpu")
                elif "envido" in btns and btns["envido"].collidepoint(pos):
                    quien_canto = "jugador"
                    canto_estado["envido"] = "Envido"
                    mensaje = "¡Envido cantado!"
                    esperando_respuesta = True
                    respuesta_pendiente = ("envido", "cpu")
                elif "realenvido" in btns and btns["realenvido"].collidepoint(pos):
                    quien_canto = "jugador"
                    canto_estado["envido"] = "Real Envido"
                    mensaje = "¡Real Envido cantado!"
                    esperando_respuesta = True
                    respuesta_pendiente = ("envido", "cpu")
                elif "faltaenvido" in btns and btns["faltaenvido"].collidepoint(pos):
                    quien_canto = "jugador"
                    canto_estado["envido"] = "Falta Envido"
                    mensaje = "¡Falta Envido cantada!"
                    esperando_respuesta = True
                    respuesta_pendiente = ("envido", "cpu")
                elif "flor" in btns and btns["flor"].collidepoint(pos):
                    quien_canto = "jugador"
                    canto_estado["flor"] = "Flor"
                    mensaje = "¡Flor cantada!"
                    esperando_respuesta = True
                    respuesta_pendiente = ("flor", "cpu")
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                pos = pygame.mouse.get_pos()
                mesa_rect = pygame.Rect(360, 230, 240, 140)
                if mesa_rect.collidepoint(pos):
                    jugada_mesa[0] = jugadores[0]["mano"].pop(drag_index)
                    mensaje = "CPU juega..."
                    turno = 1
                dragging = False
                carta_drag = None
                drag_index = None
            elif event.type == pygame.MOUSEMOTION and dragging and carta_drag:
                mouse_x, mouse_y = event.pos
                carta_drag.rect.x = mouse_x + offset_x
                carta_drag.rect.y = mouse_y + offset_y

        if not esperando_respuesta and turno == 1 and not jugada_mesa[1] and not game_over:
            pygame.display.flip(); pygame.time.wait(800)
            if canto_estado["flor"] is None and tiene_flor(jugadores[1]["mano"]):
                quien_canto = "cpu"
                canto_estado["flor"] = "Flor"
                mensaje = "CPU canta Flor"
                esperando_respuesta = True
                respuesta_pendiente = ("flor", "jugador")
            elif canto_estado["envido"] is None and canto_estado["flor"] is None:
                canto_cpu = cpu_decide_envido(jugadores[1]["mano"], ronda)
                if canto_cpu is not None:
                    quien_canto = "cpu"
                    canto_estado["envido"] = canto_cpu
                    mensaje = f"CPU canta {canto_cpu}"
                    esperando_respuesta = True
                    respuesta_pendiente = ("envido", "jugador")
                    pygame.display.flip(); pygame.time.wait(900)
                    continue
            if canto_estado["truco"] < 3:
                canto_cpu = cpu_decide_truco(jugadores[1]["mano"], canto_estado["truco"]+1)
                if canto_cpu is not None:
                    quien_canto = "cpu"
                    canto_estado["truco"] += 1
                    mensaje = ["CPU canta Truco", "CPU canta Retruco", "CPU canta Vale Cuatro"][canto_estado["truco"]-1]
                    esperando_respuesta = True
                    respuesta_pendiente = ("truco", "jugador")
                    pygame.display.flip(); pygame.time.wait(900)
                    continue
            if jugadores[1]["mano"]:
                jugada_mesa[1] = jugadores[1]["mano"].pop(0)
                turno = 2

        if canto_estado["envido"] is not None and resultado_envido is not None:
            if resultado_envido == "Quiero":
                tanto_jugador = calcular_tanto(jugadores[0]["mano"])
                tanto_cpu = calcular_tanto(jugadores[1]["mano"])
                cartel_tantos(pantalla, tanto_jugador, tanto_cpu)
                if tanto_jugador > tanto_cpu:
                    mensaje = "¡Ganaste el Envido!"
                    jugadores[0]["puntos"] += puntos_envido[canto_estado["envido"]]
                elif tanto_cpu > tanto_jugador:
                    mensaje = "CPU gana el Envido."
                    jugadores[1]["puntos"] += puntos_envido[canto_estado["envido"]]
                else:
                    mensaje = "Empate de tantos, gana el mano."
                    jugadores[mano]["puntos"] += puntos_envido[canto_estado["envido"]]
            else:
                if quien_canto == "jugador":
                    jugadores[0]["puntos"] += 1
                else:
                    jugadores[1]["puntos"] += 1
            resultado_envido = None
            canto_estado["envido"] = "resuelto"
            pygame.time.wait(900)

        if canto_estado["flor"] is not None and resultado_flor is not None:
            if resultado_flor == "Quiero":
                flor_jugador = calcular_flor(jugadores[0]["mano"])
                flor_cpu = calcular_flor(jugadores[1]["mano"])
                cartel_tantos(pantalla, flor_jugador, flor_cpu, flor=True)
                if flor_jugador > flor_cpu:
                    mensaje = "¡Ganaste la Flor!"
                    jugadores[0]["puntos"] += puntos_flor
                elif flor_cpu > flor_jugador:
                    mensaje = "CPU gana la Flor."
                    jugadores[1]["puntos"] += puntos_flor
                else:
                    mensaje = "Empate de Flor, gana el mano."
                    jugadores[mano]["puntos"] += puntos_flor
            else:
                if quien_canto == "jugador":
                    jugadores[0]["puntos"] += 1
                else:
                    jugadores[1]["puntos"] += 1
            resultado_flor = None
            canto_estado["flor"] = "resuelto"
            pygame.time.wait(900)

        if canto_estado["truco"] > 0 and resultado_truco is not None:
            if resultado_truco == "No quiero":
                if quien_canto == "jugador":
                    jugadores[1]["puntos"] += puntos_truco[canto_estado["truco"]-1]
                    mensaje = "CPU gana los puntos del Truco."
                else:
                    jugadores[0]["puntos"] += puntos_truco[canto_estado["truco"]-1]
                    mensaje = "¡Sumás los puntos del Truco!"
                canto_estado["truco"] = 0
            resultado_truco = None
            pygame.time.wait(900)

        if jugada_mesa[0] and jugada_mesa[1] and turno == 2:
            ganador = quien_gana(jugada_mesa[0], jugada_mesa[1])
            jugadores[0]["jugadas"].append(jugada_mesa[0])
            jugadores[1]["jugadas"].append(jugada_mesa[1])
            if ganador == 0:
                mensaje = "¡Ganaste la mano!"
                if canto_estado["truco"] > 0:
                    jugadores[0]["puntos"] += puntos_truco[canto_estado["truco"]-1]
                else:
                    jugadores[0]["puntos"] += 1
            elif ganador == 1:
                mensaje = "CPU gana la mano."
                if canto_estado["truco"] > 0:
                    jugadores[1]["puntos"] += puntos_truco[canto_estado["truco"]-1]
                else:
                    jugadores[1]["puntos"] += 1
            else:
                mensaje = "Empate, gana el que sea mano."
                jugadores[mano]["puntos"] += 1
            pygame.display.flip(); pygame.time.wait(1200)
            jugada_mesa = [None, None]
            if not jugadores[0]["mano"] or not jugadores[1]["mano"]:
                ronda += 1
                jugadores[0]["jugadas"].clear()
                jugadores[1]["jugadas"].clear()
                canto_estado = {"truco":0, "envido":None, "flor":None}
                resultado_envido = None
                resultado_truco = None
                resultado_flor = None
                quien_canto = None
                if jugadores[0]["puntos"] >= 15:
                    mensaje = "¡Ganaste el partido!"
                    game_over = True
                elif jugadores[1]["puntos"] >= 15:
                    mensaje = "CPU ganó el partido."
                    game_over = True
                else:
                    mano = 1 - mano
                    repartir(jugadores)
                    mensaje = f"Nueva mano. Mano: {jugadores[mano]['nombre']}"
                    turno = mano
            else:
                turno = mano

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()