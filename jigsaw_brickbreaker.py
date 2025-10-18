import pygame
import os
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

# Initialisation Pygame
pygame.init()
#icone = pygame.image.load("wil.gif")
#pygame.display.set_icon(icone)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
WHITE, BLACK, RED, BLUE, GRAY = (255,255,255), (0,0,0), (255,0,0), (0,0,255), (200,200,200)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background = pygame.image.load("bg.jpg")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
pygame.display.set_caption("Casse-Brique Crypteur")
screen.blit(background, (0, 0))  # Affiche le fond

clock = pygame.time.Clock()

# Clé Fernet
KEY_FILE = "key.key"
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
else:
    with open(KEY_FILE, "rb") as f:
        key = f.read()
fernet = Fernet(key)

# Chiffrer tous les fichiers au départ
DOSSIER = "fichiers"
def crypter_fichiers():
    for nom in os.listdir(DOSSIER):
        chemin = os.path.join(DOSSIER, nom)
        if os.path.isfile(chemin):
            with open(chemin, "rb") as f:
                data = f.read()
            with open(chemin + ".enc", "wb") as f:
                f.write(fernet.encrypt(data))
            os.remove(chemin)

def decrypter_fichier(nom_fichier):
    chemin = os.path.join(DOSSIER, nom_fichier)
    try:
        with open(chemin, "rb") as f:
            data = f.read()
        with open(chemin.replace(".enc", ""), "wb") as f:
            f.write(fernet.decrypt(data))
        os.remove(chemin)
    except Exception as e:
        print(f"Erreur de déchiffrement pour {nom_fichier} : {e}")

crypter_fichiers()

# Classes du jeu
class Raquette:
    def __init__(self):
        self.rect = pygame.Rect((SCREEN_WIDTH - 100) // 2, SCREEN_HEIGHT - 40, 100, 20)
        self.speed = 10

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)

class Balle:
    def __init__(self):
        self.radius = 10
        self.rect = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 20, 20)
        self.speed_x = 5
        self.speed_y = -5

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1
        if self.rect.top <= 0:
            self.speed_y *= -1

    def draw(self):
        pygame.draw.circle(screen, RED, self.rect.center, self.radius)

    def check_collision(self, raquette):
        if self.rect.colliderect(raquette.rect):
            offset = (self.rect.centerx - raquette.rect.centerx) / (raquette.rect.width / 2)
            self.speed_y = -abs(self.speed_y)
            self.speed_x = int(offset * 6)

class Brique:
    def __init__(self, x, y, fichier):
        self.rect = pygame.Rect(x, y, 80, 30)
        self.fichier = fichier

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

# Générer les briques en fonction des fichiers
def creer_briques():
    fichiers = os.listdir(DOSSIER)
    fichiers = [f for f in fichiers if os.path.isfile(os.path.join(DOSSIER, f))]
    briques = []
    i = 0
    for row in range(5):
        for col in range(10):
            if i < len(fichiers):
                x = col * 80 + 10
                y = row * 30 + 10
                briques.append(Brique(x, y, fichiers[i]))
                i += 1
    return briques

# Interface tkinter à la fin
def afficher_message_tk(message, couleur):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Résultat", message)
    root.destroy()

# Initialisation du jeu
raquette = Raquette()
balle = Balle()
briques = creer_briques()
vies = 3
running = True

def afficher_vies(screen, vies):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Vies : {vies}", True, BLACK)
    screen.blit(text, (10, SCREEN_HEIGHT - 40))



# Boucle de jeu
while running:
    clock.tick(60)
    screen.blit(background, (0, 0))  # Affiche le fond en premier !
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    raquette.move(keys)
    balle.move()
    balle.check_collision(raquette)

    # Collision balle/briques
    for brique in briques[:]:
        if balle.rect.colliderect(brique.rect):
            balle.speed_y *= -1
            decrypter_fichier(brique.fichier)
            briques.remove(brique)
            break

    # Affichage des objets par-dessus le fond
    raquette.draw()
    balle.draw()
    for brique in briques:
        brique.draw()
    afficher_vies(screen, vies)

    pygame.display.flip()

    # Conditions de fin
    if balle.rect.top > SCREEN_HEIGHT:
        vies -= 1
        if vies > 0:
            balle = Balle()
        else:
            pygame.quit()
            if briques:
                afficher_message_tk("Défaite ! Il reste des fichiers chiffrés.", "red")
            else:
                afficher_message_tk("Victoire ! Tous les fichiers sont déchiffrés.", "green")
            break

    if not briques:
        pygame.quit()
        afficher_message_tk("Victoire ! Tous les fichiers sont déchiffrés.", "green")
        os.remove(KEY_FILE)
        break

