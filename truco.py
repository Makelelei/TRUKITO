from cartas import Carta, PALOS, VALORES
import random

def jerarquia_truco(carta):
    jerarquia = [
        ("1", "Espada"), ("1", "Basto"), ("7", "Espada"), ("7", "Oro"),
        ("3", None), ("2", None), ("1", None), ("12", None), ("11", None),
        ("10", None), ("7", None), ("6", None), ("5", None), ("4", None)
    ]
    for i, (valor, palo) in enumerate(jerarquia):
        if carta.valor == valor and (palo is None or palo == carta.palo):
            return i
    return len(jerarquia)

def quien_gana(c1, c2):
    j1 = jerarquia_truco(c1)
    j2 = jerarquia_truco(c2)
    if j1 < j2:
        return 0
    elif j2 < j1:
        return 1
    else:
        return -1

def calcular_tanto(mano):
    palos = {}
    for carta in mano:
        if carta.palo not in palos:
            palos[carta.palo] = []
        palos[carta.palo].append(carta)
    max_tanto = 0
    for cartas_palo in palos.values():
        valores = sorted([carta.valor_num() for carta in cartas_palo if carta.valor_num() <= 7], reverse=True)
        if len(valores) >= 2:
            tanto = valores[0] + valores[1] + 20
            max_tanto = max(max_tanto, tanto)
        else:
            for carta in cartas_palo:
                valor = carta.valor_num()
                if valor > 7:
                    valor = 0
                max_tanto = max(max_tanto, valor)
    return max_tanto

def tiene_flor(mano):
    palos = [carta.palo for carta in mano]
    for palo in PALOS:
        if palos.count(palo) == 3:
            return True
    return False

def calcular_flor(mano):
    if not tiene_flor(mano):
        return 0
    return sum(carta.valor_num() for carta in mano) + 20

def cpu_decide_envido(mano, ronda=1):
    tanto = calcular_tanto(mano)
    prob = random.random()
    if tiene_flor(mano) and ronda == 1:
        return "Flor"
    if tanto >= 31:
        return "Falta Envido" if prob < 0.4 else "Real Envido"
    if tanto >= 29:
        return "Real Envido" if prob < 0.5 else "Envido"
    if tanto >= 27:
        return "Envido" if prob < 0.6 else None
    if tanto >= 24 and prob < 0.25:
        return "Envido"
    return None

def cpu_decide_truco(mano, etapa=1):
    jerarquias = [jerarquia_truco(c) for c in mano]
    prob = random.random()
    if etapa == 1:
        if any(j < 3 for j in jerarquias):
            return "Truco"
        if any(j < 6 for j in jerarquias) and prob < 0.5:
            return "Truco"
    elif etapa == 2:
        if any(j < 3 for j in jerarquias):
            return "Retruco"
        if any(j < 6 for j in jerarquias) and prob < 0.5:
            return "Retruco"
    elif etapa == 3:
        if any(j < 2 for j in jerarquias) and prob < 0.5:
            return "Vale Cuatro"
    return None

def cpu_responde_envido(mi_tanto, rival_tanto=None):
    if mi_tanto >= 31: return "Quiero"
    if mi_tanto >= 28: return "Quiero" if random.random() < 0.8 else "No quiero"
    if mi_tanto >= 25: return "Quiero" if random.random() < 0.4 else "No quiero"
    return "No quiero"

def cpu_responde_truco(mano, etapa=1):
    jerarquias = [jerarquia_truco(c) for c in mano]
    if etapa == 1 and any(j < 6 for j in jerarquias):
        return "Quiero"
    if etapa == 2 and any(j < 3 for j in jerarquias):
        return "Quiero"
    if etapa == 3 and any(j < 2 for j in jerarquias):
        return "Quiero"
    return "No quiero" if random.random() < 0.8 else "Quiero"

def crear_mazo():
    return [Carta(valor, palo) for palo in PALOS for valor in VALORES]

def repartir(jugadores):
    mazo = crear_mazo()
    random.shuffle(mazo)
    for j in jugadores:
        j["mano"] = [mazo.pop() for _ in range(3)]
        j["jugadas"] = []

def nueva_partida():
    jugadores = [
        {"nombre": "Vos", "mano": [], "jugadas": [], "puntos": 0},
        {"nombre": "CPU", "mano": [], "jugadas": [], "puntos": 0}
    ]
    mano = 0
    repartir(jugadores)
    return jugadores, mano