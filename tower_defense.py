import pygame
import sys
import random

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kule Savunma Oyunu")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)

# Path for enemies (simple horizontal line)
PATH = [(0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2)]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp, speed, color):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = PATH[0]
        self.hp = hp
        self.speed = speed
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)

    def update(self, dt):
        if self.rect.x < PATH[1][0]:
            self.pos.x += self.speed * dt
            self.rect.x = int(self.pos.x)
        else:
            self.kill()
            # Enemy reached the end - reduce player lives etc.

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y, range_radius, damage, fire_rate, color):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.range = range_radius
        self.damage = damage
        self.fire_rate = fire_rate
        self.last_shot = 0
        self.level = 1
        self.base_color = color

    def upgrade(self):
        self.level += 1
        self.damage += 1
        self.range += 10
        self.image.fill(tuple(min(255, c + 40) for c in self.base_color))

    def update(self, dt, enemies, projectiles):
        self.last_shot += dt
        if self.last_shot >= self.fire_rate:
            # find target
            target = None
            closest_dist = self.range
            for enemy in enemies:
                dist = pygame.math.Vector2(enemy.rect.center).distance_to(self.rect.center)
                if dist <= closest_dist:
                    closest_dist = dist
                    target = enemy
            if target:
                projectile = Projectile(self.rect.centerx, self.rect.centery, target, self.damage)
                projectiles.add(projectile)
                self.last_shot = 0

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, damage):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.target = target
        self.speed = 300
        self.damage = damage

    def update(self, dt, enemies):
        if not self.target.alive():
            self.kill()
            return
        direction = pygame.math.Vector2(self.target.rect.center) - pygame.math.Vector2(self.rect.center)
        distance = direction.length()
        if distance <= self.speed * dt:
            # Hit the target
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.kill()
            self.kill()
        else:
            direction.normalize_ip()
            move = direction * self.speed * dt
            self.rect.move_ip(move)

# Tower types
def create_basic_tower(x, y):
    return Tower(x, y, range_radius=120, damage=1, fire_rate=0.8, color=(100, 100, 255))

def create_fast_tower(x, y):
    return Tower(x, y, range_radius=100, damage=1, fire_rate=0.3, color=(100, 255, 100))

def create_heavy_tower(x, y):
    return Tower(x, y, range_radius=150, damage=2, fire_rate=1.2, color=(255, 100, 100))

# Enemy types
def create_basic_enemy():
    return Enemy(hp=3, speed=50, color=(0, 200, 200))

def create_fast_enemy():
    return Enemy(hp=2, speed=80, color=(200, 200, 0))

def create_tank_enemy():
    return Enemy(hp=5, speed=30, color=(200, 0, 200))

TOWER_TYPES = [create_basic_tower, create_fast_tower, create_heavy_tower]
ENEMY_TYPES = [create_basic_enemy, create_fast_enemy, create_tank_enemy]

towers = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

def spawn_wave(wave_number):
    num_enemies = 5 + wave_number
    for i in range(num_enemies):
        enemy_type = random.choice(ENEMY_TYPES)
        enemy = enemy_type()
        enemy.hp += wave_number  # increase hp each wave
        enemy.speed += wave_number * 2
        enemy.rect.x -= i * 40  # stagger spawns
        enemies.add(enemy)

wave = 0
spawn_wave(wave)

selected_tower_type = 0
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_TAB:
                selected_tower_type = (selected_tower_type + 1) % len(TOWER_TYPES)
            elif event.key == pygame.K_SPACE:
                wave += 1
                spawn_wave(wave)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            tower = TOWER_TYPES[selected_tower_type](x, y)
            towers.add(tower)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            # upgrade tower on right click
            for tower in towers:
                if tower.rect.collidepoint(event.pos):
                    tower.upgrade()

    # update entities
    enemies.update(dt)
    projectiles.update(dt, enemies)
    for tower in towers:
        tower.update(dt, enemies, projectiles)

    screen.fill(BLACK)

    # draw path line
    pygame.draw.line(screen, WHITE, PATH[0], PATH[1], 5)

    towers.draw(screen)
    enemies.draw(screen)
    projectiles.draw(screen)

    info = font.render(f"Wave {wave} | Towers: {len(towers)} | Enemies: {len(enemies)}", True, WHITE)
    screen.blit(info, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
