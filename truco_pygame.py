import pygame
import sys
import random

# Configuración inicial
WIDTH, HEIGHT = 900, 600
CARD_WIDTH, CARD_HEIGHT = 80, 120
TABLE_COLOR = (0, 128, 0)
WHITE = (255, 255, 255)
FPS = 30

# Palos y valores
PALOS = ['Espada', 'Basto', 'Oro', 'Copa']
VALORES = ['1', '2', '3', '4', '5', '6', '7', '10', '11', '12']

def crear_mazo():
    return [(valor, palo) for palo in PALOS for valor in VALORES]

def dibujar_carta(screen, valor, palo, x, y):
    pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=8)
    font = pygame.font.SysFont(None, 36)
    text = font.render(valor, True, (0,0,0))
    palo_text = font.render(palo[0], True, (0,0,0))
    screen.blit(text, (x+10, y+10))
    screen.blit(palo_text, (x+10, y+50))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Truco Argentino en Pygame")
    clock = pygame.time.Clock()

    # Mezclar y repartir
    mazo = crear_mazo()
    random.shuffle(mazo)
    mano_jugador = [mazo.pop() for _ in range(3)]
    mano_cpu = [mazo.pop() for _ in range(3)]

    running = True
    while running:
        screen.fill(TABLE_COLOR)

        # Dibujar cartas jugador
        for i, (valor, palo) in enumerate(mano_jugador):
            dibujar_carta(screen, valor, palo, 150+i*100, HEIGHT-180)

        # Dibujar cartas CPU (boca abajo)
        for i in range(3):
            pygame.draw.rect(screen, (50,50,50), (150+i*100, 60, CARD_WIDTH, CARD_HEIGHT), border_radius=8)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()