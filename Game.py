import pygame
import random
import requests

# Inicialização do Pygame
pygame.init()

# Definição das constantes
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 100
ENEMY_WIDTH = 30
ENEMY_HEIGHT = 30
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Inicialização da tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("EP REDES")

# Relógio para controle de FPS
clock = pygame.time.Clock()

# Fonte para o texto
font = pygame.font.Font(None, 36)

# Variáveis de controle
score = 0
player_lives = 80

# No início do seu script
enemies_killed = 0
shots_fired = 0
bosses_killed = 0

# Variável para contabilizar os pontos antes de enviar para o servidor
current_score = 0

# Variável para controlar o nível do jogo
current_level = 0

# Grupo de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()  # Grupo para os tiros dos inimigos

# Carrega as imagens
player_image = pygame.image.load("spaceship.png").convert()

alien_image = pygame.image.load("Monstro2.png").convert()

boss_image = pygame.image.load("boss.png").convert()

bonus_boss_image = pygame.image.load("Monstro3.png")

# Ajusta o tamanho da imagem do jogador
player_image = pygame.transform.scale(player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))
pygame.mixer.init()
shoot_sound = pygame.mixer.Sound("shoot_sound.wav")  # Replace "shoot_sound.wav" with the actual path to your sound file
pygame.mixer.music.load("AdhesiveWombat - Night Shade.mp3")  # Substitua pelo caminho do seu arquivo de som
pygame.mixer.music.set_volume(0.008)  # Ajuste o volume conforme necessário 


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, shooter):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -15
        self.damage = 30
        self.shooter = shooter  # Armazena a referência ao jogador que disparou a bala
        self.shoot_sound = pygame.mixer.Sound("shoot_sound.wav")  # Replace with the actual path to your sound file
        self.shoot_sound.set_volume(0.008)  # Adjust the volume level (0.0 to 1.0)

    def update(self):
        self.rect.y += self.speedy
        # Remove o tiro se sair da tela
        if self.rect.bottom < 0:
            self.shoot_sound.play()
            self.kill()

        # Verifica colisão com o jogador que disparou a bala
        if pygame.sprite.collide_rect(self, self.shooter):
            self.kill()

        # Toca o som de tiro quando for disparado
        if self.rect.bottom < 0:
            self.shoot_sound.play()
            self.kill()


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(player_image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2  # Inicia no centro da tela
        self.rect.centery = SCREEN_HEIGHT - 50  # Inicia no centro vertical da tela
        self.shoot_delay = 50
        self.last_shot = pygame.time.get_ticks()
        self.max_shots = 5
        self.shots_fired = 0
        self.speedx = 5
        self.speedy = 5

        self.enemies_killed = 0  # Adiciona a variável enemies_killed
        self.bosses_killed = 0  # Adicione a variável bosses_killed

    def update(self):
        global current_score
        global enemies_killed
        global shots_fired
        global bosses_killed

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speedx
        if keys[pygame.K_d] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speedx
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speedy
        if keys[pygame.K_s] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speedy

        # Atirar com a tecla "K"
        now = pygame.time.get_ticks()
        if keys[pygame.K_k] and now - self.last_shot > self.shoot_delay:
            self.last_shot = now

            # Verifica se ainda pode disparar mais tiros
            if self.shots_fired < self.max_shots:
                bullet = Bullet(self.rect.centerx, self.rect.top, self)
                all_sprites.add(bullet)
                bullets.add(bullet)

                # Atualiza o contador de tiros disparados
                shots_fired += 1

        # Lógica para incrementar variáveis
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullets_hit in hits.items():
            enemy.health -= sum(bullet.damage for bullet in bullets_hit)
            if enemy.health <= 0:
                current_score += 10  # Atualiza a variável current_score
                enemies_killed += 1
                enemy.kill()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = 1

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom > SCREEN_HEIGHT:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = alien_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 20
        self.shoot_delay = random.randrange(500, 2000)  # Aleatório entre 1 e 3 segundos
        self.last_shot = pygame.time.get_ticks()
        self.speedx = 5  # Velocidade lateral
        self.direction = 1  # Direção do movimento (1: direita, -1: esquerda)

    def update(self):
        # Movimento lateral alternado
        self.rect.x += self.speedx * self.direction

        # Alterna a direção quando atinge as bordas da tela
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1

        # Atirar em intervalos regulares
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(enemy_bullet)
            enemy_bullets.add(enemy_bullet)


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if current_level == 10:
            self.image = pygame.transform.scale(bonus_boss_image, (5 * ENEMY_WIDTH, 5 * ENEMY_HEIGHT))
        else:
            self.image = pygame.transform.scale(boss_image, (5 * ENEMY_WIDTH, 5 * ENEMY_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 2000  # Vida do Boss
        self.shoot_delay = random.randrange(100, 200)  # Aleatório entre 1 e 2 segundos
        self.last_shot = pygame.time.get_ticks()
        self.speedx = 9  # Velocidade lateral

    def update(self):
        # Movimento lateral
        self.rect.x += self.speedx

        # Alterna a direção quando atinge as bordas da tela
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speedx *= -1

        # Atirar em intervalos regulares
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            boss_bullet = BossBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(boss_bullet)
            enemy_bullets.add(boss_bullet)


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = 10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom > SCREEN_HEIGHT:
            self.kill()


def is_boss_level():
    if current_level > 0:
        return current_level % 5 == 0


# Adiciona os inimigos ao grupo de sprites
def new_enemies():
    global current_level

    if is_boss_level():
        boss = Boss(SCREEN_WIDTH // 2 - 25, 50)
        all_sprites.add(boss)
        enemies.add(boss)
    else:
        for row in range(4):  # 4 fileiras de inimigos
            for col in range(5):  # 5 inimigos por fileira
                enemy = Enemy(col * 180 + 100, row * 100 + 50)
                all_sprites.add(enemy)
                enemies.add(enemy)

    current_level += 1


# Adiciona os inimigos à fase inicial
new_enemies()

# Adiciona o jogador ao grupo de sprites
player = Player()
all_sprites.add(player)


# Função para verificar se é um nível de chefe
def is_boss_level():
    return current_level % 5 == 0


# Função para atualizar a pontuação no servidor Flask
def update_server_score(player, score, enemies_killed, shots_fired, current_level, bosses_killed, player_lives):
    url = "http://127.0.0.1:5000/update_score"
    data = {

        "player": player,
        "score": score,
        "enemies_killed": enemies_killed,
        "shots_fired": shots_fired,
        "current_level": current_level,
        "bosses_killed": bosses_killed,
        "player_lives": player_lives,
    }
    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("Pontuação atualizada no servidor com sucesso.")
    else:
        print(f"Falha ao atualizar pontuação. Status code: {response.status_code}")


# Inicie a reprodução do som de fundo
pygame.mixer.music.play(-1)
# Loop principal do jogo
running = True
while running and player_lives > 0:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Verifica se todos os inimigos foram derrotados para passar de fase
    if len(enemies) == 0:
        new_enemies()  # Adicione essa linha para iniciar a fase ao derrotar todos os inimigos

    # Atualiza todos os sprites
    all_sprites.update()

    # Verifica colisões entre o jogador e os inimigos
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        player_lives -= 1
        for enemy in hits:
            enemy.kill()

    # Verifica colisões entre os tiros do jogador e os inimigos
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullets_hit in hits.items():
        enemy.health -= sum(bullet.damage for bullet in bullets_hit)
        if enemy.health <= 0:
            if isinstance(enemy, Boss):  # Verifica se o inimigo é um chefe
                bosses_killed += 1
            else:
                enemies_killed += 1
            current_score += 10  # Atualiza a variável current_score
            enemy.kill()

    # Verifica colisões entre o jogador e os tiros dos inimigos
    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    if hits:
        player_lives -= 1

    # Verifica colisões entre o jogador e os tiros dos inimigos
    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    if hits:
        player_lives -= 1

    # Limpa a tela
    screen.fill(BLACK)

    # Desenha todos os sprites
    all_sprites.draw(screen)

    # Exibe o contador de pontos e vidas na tela
    score_text = f"Pontos: {current_score} Inimigos: {enemies_killed} Tiros Disparados: {shots_fired} Nível: {current_level} Bosses: {bosses_killed} Vidas: {player_lives}"
    score_surface = font.render(score_text, True, WHITE)
    screen.blit(score_surface, (5, 5))

    # Atualiza a tela
    pygame.display.flip()

    # Atualiza pontuação no servidor Flask
    update_server_score("JB", current_score, enemies_killed, shots_fired, current_level, bosses_killed, player_lives)
    print(current_score, enemies_killed, shots_fired, current_level, bosses_killed, player_lives)

    # Controla o FPS
    clock.tick(FPS)

# Mostra mensagem de fim de jogo
if player_lives <= 0:
    game_over_text = font.render("Game Over", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
    pygame.display.flip()

    pygame.time.delay(2000)  # Aguarda 2 segundos antes de encerrar
    pygame.mixer.music.stop()

# Encerra o Pygame
pygame.quit()
