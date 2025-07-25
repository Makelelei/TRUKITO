import pygame

PALOS = ["Espada", "Basto", "Oro", "Copa"]
VALORES = ["1", "2", "3", "4", "5", "6", "7", "10", "11", "12"]
SIMBOLOS = {"Espada": "♠", "Basto": "♣", "Oro": "♦", "Copa": "♥"}
COLOR_PALO = {"Espada": (0,0,0), "Basto": (0,128,0), "Oro": (190,140,0), "Copa": (200,20,70)}

class Carta:
    def __init__(self, valor, palo):
        self.valor = valor
        self.palo = palo
        self.rect = pygame.Rect(0, 0, 90, 140)

    def valor_num(self):
        try:
            num = int(self.valor)
            return num if num <= 7 else 0
        except:
            return 0

    def dibujar(self, pantalla, x, y, seleccionada=False, hover=False, tapada=False, sombreada=False):
        rect = pygame.Rect(x, y, 90, 140)
        self.rect = rect
        color = (255,255,255)
        if sombreada:
            color = (180,180,180)
        elif seleccionada:
            color = (255,255,160)
        elif hover:
            color = (220,255,220)
        pygame.draw.rect(pantalla, color, rect, border_radius=10)
        pygame.draw.rect(pantalla, (0,0,0), rect, 3, border_radius=10)
        font = pygame.font.SysFont("arialblack", 32)
        fontpalo = pygame.font.SysFont("arialblack", 28)
        if tapada:
            pygame.draw.rect(pantalla, (50,50,50), rect, border_radius=10)
            pygame.draw.rect(pantalla, (0,0,0), rect, 3, border_radius=10)
            fonttap = pygame.font.SysFont("arialblack", 40)
            t = fonttap.render("?", True, (255,255,0))
            pantalla.blit(t, (x+30, y+45))
        else:
            txt = font.render(self.valor, True, COLOR_PALO[self.palo])
            pantalla.blit(txt, (x+10, y+10))
            palo = SIMBOLOS[self.palo]
            txtpalo = fontpalo.render(palo, True, COLOR_PALO[self.palo])
            pantalla.blit(txtpalo, (x+10, y+70))
            fontsm = pygame.font.SysFont("arial", 18)
            pantxt = fontsm.render(self.palo, True, (60,60,60))
            pantalla.blit(pantxt, (x+10, y+120))

    def colisiona(self, pos):
        return self.rect.collidepoint(pos)