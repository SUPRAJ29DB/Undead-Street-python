import math
import random
import sys
import pygame

# Undead Streets — top-down zombie survival
WIDTH, HEIGHT = 960, 600
FPS = 60
PLAYER_SPEED = 245
PLAYER_RADIUS = 15
BULLET_SPEED = 620
ZOMBIE_RADIUS = 17
STARTING_HEALTH = 100

BG = (11, 19, 20)
GRID = (24, 38, 38)
MINT = (102, 255, 213)
WHITE = (230, 242, 242)
RED = (255, 78, 105)
BLUE = (46, 140, 255)
GREEN = (92, 210, 115)
PURPLE = (185, 122, 255)
YELLOW = (255, 222, 112)


def clamp(value, low, high):
    return max(low, min(value, high))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Undead Streets — Zombie Survival")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 19, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self.big_font = pygame.font.SysFont("consolas", 32, bold=True)
        self.reset()

    def reset(self):
        self.player = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.health = STARTING_HEALTH
        self.score = 0
        self.elapsed = 0.0
        self.spawn_timer = 0.45
        self.shoot_timer = 0.0
        self.invulnerable = 0.0
        self.game_over = False
        self.zombies = []
        self.bullets = []
        self.pickups = []
        self.particles = []

    def spawn_zombie(self, wave):
        edge = random.randrange(4)
        if edge == 0:
            pos = pygame.Vector2(random.randrange(WIDTH), -25)
        elif edge == 1:
            pos = pygame.Vector2(WIDTH + 25, random.randrange(HEIGHT))
        elif edge == 2:
            pos = pygame.Vector2(random.randrange(WIDTH), HEIGHT + 25)
        else:
            pos = pygame.Vector2(-25, random.randrange(HEIGHT))
        tough = wave >= 4 and random.random() < 0.25
        self.zombies.append({
            "pos": pos,
            "speed": random.uniform(52, 78) + min(65, (wave - 1) * 5),
            "hp": 2 if tough else 1,
            "radius": ZOMBIE_RADIUS + (3 if tough else 0),
            "color": PURPLE if tough else GREEN,
            "phase": random.random() * math.tau,
        })

    def shoot(self):
        if self.shoot_timer > 0 or self.game_over:
            return
        direction = pygame.Vector2(pygame.mouse.get_pos()) - self.player
        if direction.length_squared() < 1:
            direction = pygame.Vector2(1, 0)
        else:
            direction = direction.normalize()
        self.bullets.append({
            "pos": self.player + direction * 22,
            "vel": direction * BULLET_SPEED,
            "life": 1.25,
        })
        self.shoot_timer = 0.16

    def burst(self, pos, color, count=8):
        for _ in range(count):
            angle = random.random() * math.tau
            speed = random.uniform(35, 150)
            self.particles.append({
                "pos": pygame.Vector2(pos),
                "vel": pygame.Vector2(math.cos(angle), math.sin(angle)) * speed,
                "life": random.uniform(0.15, 0.45),
                "max_life": 0.45,
                "color": color,
            })

    def update(self, dt):
        if self.game_over:
            return

        self.elapsed += dt
        self.shoot_timer = max(0, self.shoot_timer - dt)
        self.invulnerable = max(0, self.invulnerable - dt)

        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if move.length_squared():
            self.player += move.normalize() * PLAYER_SPEED * dt
        self.player.x = clamp(self.player.x, 28, WIDTH - 28)
        self.player.y = clamp(self.player.y, 28, HEIGHT - 28)

        if pygame.mouse.get_pressed()[0]:
            self.shoot()

        wave = 1 + int(self.elapsed / 22)
        self.spawn_timer -= dt
        spawn_interval = max(0.32, 1.45 - (wave - 1) * 0.12)
        if self.spawn_timer <= 0:
            self.spawn_zombie(wave)
            self.spawn_timer = spawn_interval * random.uniform(0.72, 1.18)
            if wave >= 3 and random.random() < min(0.55, 0.08 * wave):
                self.spawn_zombie(wave)

        # Zombie pursuit and player collision.
        for zombie in self.zombies[:]:
            direction = self.player - zombie["pos"]
            if direction.length_squared() > 1:
                zombie["pos"] += direction.normalize() * zombie["speed"] * dt
            zombie["phase"] += dt * 4
            if zombie["pos"].distance_to(self.player) < zombie["radius"] + PLAYER_RADIUS:
                if self.invulnerable <= 0:
                    self.health -= 18
                    self.invulnerable = 0.65
                    self.burst(self.player, RED, 12)
                    away = zombie["pos"] - self.player
                    if away.length_squared():
                        zombie["pos"] += away.normalize() * 24
                    if self.health <= 0:
                        self.health = 0
                        self.game_over = True
                        break

        # Bullet movement and collision.
        for bullet in self.bullets[:]:
            bullet["pos"] += bullet["vel"] * dt
            bullet["life"] -= dt
            p = bullet["pos"]
            if (bullet["life"] <= 0 or p.x < -20 or p.x > WIDTH + 20
                    or p.y < -20 or p.y > HEIGHT + 20):
                self.bullets.remove(bullet)
                continue
            for zombie in self.zombies[:]:
                if p.distance_to(zombie["pos"]) < zombie["radius"] + 5:
                    zombie["hp"] -= 1
                    self.bullets.remove(bullet)
                    if zombie["hp"] <= 0:
                        self.zombies.remove(zombie)
                        self.score += 10
                        self.burst(zombie["pos"], GREEN, 8)
                        if random.random() < 0.18:
                            self.pickups.append({"pos": pygame.Vector2(zombie["pos"]), "pulse": 0})
                    break

        for pickup in self.pickups[:]:
            pickup["pulse"] += dt * 5
            if self.player.distance_to(pickup["pos"]) < PLAYER_RADIUS + 13:
                self.health = min(STARTING_HEALTH, self.health + 25)
                self.score += 5
                self.pickups.remove(pickup)

        for particle in self.particles[:]:
            particle["pos"] += particle["vel"] * dt
            particle["vel"] *= 0.88
            particle["life"] -= dt
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def draw_world(self):
        self.screen.fill(BG)
        for x in range(0, WIDTH, 64):
            pygame.draw.line(self.screen, GRID, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 64):
            pygame.draw.line(self.screen, GRID, (0, y), (WIDTH, y), 1)
        for i in range(18):
            x = (i * 137 + 43) % WIDTH
            y = (i * 89 + 29) % HEIGHT
            pygame.draw.line(self.screen, (49, 66, 61), (x, y), (x + 9, y - 4), 1)
        pygame.draw.line(self.screen, (43, 56, 51), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)

    def draw_player(self):
        if self.invulnerable > 0 and int(self.elapsed * 18) % 2 == 0:
            return
        p = (round(self.player.x), round(self.player.y))
        pygame.draw.circle(self.screen, (0, 0, 0), (p[0] + 2, p[1] + 5), PLAYER_RADIUS + 2)
        pygame.draw.circle(self.screen, BLUE, p, PLAYER_RADIUS)
        pygame.draw.circle(self.screen, (150, 220, 255), (p[0] - 4, p[1] - 5), 5)
        aim = pygame.Vector2(pygame.mouse.get_pos()) - self.player
        if aim.length_squared() > 1:
            aim = aim.normalize()
            end = self.player + aim * 28
            pygame.draw.line(self.screen, (215, 240, 255), p, (round(end.x), round(end.y)), 5)
            pygame.draw.circle(self.screen, YELLOW, (round(end.x), round(end.y)), 3)

    def draw_zombie(self, zombie):
        p = (round(zombie["pos"].x), round(zombie["pos"].y))
        r = zombie["radius"]
        wobble = math.sin(zombie["phase"]) * 2
        pygame.draw.circle(self.screen, (0, 0, 0), (p[0] + 2, p[1] + 5), r + 1)
        pygame.draw.circle(self.screen, zombie["color"], (round(p[0] + wobble), p[1]), r)
        for dx in (-5, 5):
            pygame.draw.circle(self.screen, (225, 255, 185), (p[0] + dx, p[1] - 3), 3)
            pygame.draw.circle(self.screen, (25, 20, 15), (p[0] + dx, p[1] - 3), 1)
        pygame.draw.line(self.screen, (35, 20, 17), (p[0] - 5, p[1] + 6), (p[0] + 5, p[1] + 6), 2)
        if zombie["hp"] > 1:
            pygame.draw.circle(self.screen, PURPLE, p, r + 4, 2)

    def draw_hud(self):
        panel = pygame.Surface((250, 126), pygame.SRCALPHA)
        panel.fill((5, 12, 16, 220))
        self.screen.blit(panel, (14, 14))
        pygame.draw.rect(self.screen, MINT, (14, 14, 250, 126), 1, border_radius=10)
        wave = 1 + int(self.elapsed / 22)
        lines = [
            (f"SCORE  {self.score:06d}", MINT),
            (f"HEALTH  {int(self.health)}%", WHITE),
            (f"TIME  {int(self.elapsed)}s", WHITE),
            (f"WAVE  {wave}", WHITE),
        ]
        for i, (text, color) in enumerate(lines):
            image = self.font.render(text, True, color)
            self.screen.blit(image, (28, 25 + i * 27))
        # Health bar
        pygame.draw.rect(self.screen, (65, 35, 45), (28, 111, 210, 8), border_radius=4)
        pygame.draw.rect(self.screen, RED if self.health < 35 else GREEN,
                         (28, 111, int(210 * self.health / STARTING_HEALTH), 8), border_radius=4)
        hint = self.small_font.render("WASD / ARROWS MOVE   •   MOUSE AIM   •   LEFT CLICK FIRE", True, (180, 205, 205))
        self.screen.blit(hint, (18, HEIGHT - 26))

    def draw_game_over(self):
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((2, 7, 12, 215))
        self.screen.blit(shade, (0, 0))
        title = self.big_font.render("YOU WERE OVERRUN", True, RED)
        body = self.font.render(f"Score: {self.score}    Time: {int(self.elapsed)}s    Wave: {1 + int(self.elapsed / 22)}", True, WHITE)
        sub = self.font.render("Press R or click PLAY AGAIN", True, MINT)
        box = pygame.Rect(WIDTH // 2 - 235, HEIGHT // 2 - 105, 470, 210)
        pygame.draw.rect(self.screen, (8, 22, 27), box, border_radius=16)
        pygame.draw.rect(self.screen, MINT, box, 2, border_radius=16)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 54)))
        self.screen.blit(body, body.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 8)))
        self.screen.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 27)))
        self.restart_rect = pygame.Rect(WIDTH // 2 - 95, HEIGHT // 2 + 48, 190, 40)
        pygame.draw.rect(self.screen, (23, 90, 79), self.restart_rect, border_radius=8)
        pygame.draw.rect(self.screen, MINT, self.restart_rect, 1, border_radius=8)
        label = self.font.render("PLAY AGAIN", True, WHITE)
        self.screen.blit(label, label.get_rect(center=self.restart_rect.center))

    def draw(self):
        self.draw_world()
        for pickup in self.pickups:
            p = (round(pickup["pos"].x), round(pickup["pos"].y))
            r = round(10 + math.sin(pickup["pulse"]) * 1.5)
            pygame.draw.circle(self.screen, (25, 90, 65), p, 14)
            pygame.draw.circle(self.screen, MINT, p, r)
            pygame.draw.rect(self.screen, (5, 45, 30), (p[0] - 3, p[1] - 7, 6, 14))
            pygame.draw.rect(self.screen, (5, 45, 30), (p[0] - 7, p[1] - 3, 14, 6))
        for bullet in self.bullets:
            p = (round(bullet["pos"].x), round(bullet["pos"].y))
            pygame.draw.circle(self.screen, YELLOW, p, 5)
        for zombie in self.zombies:
            self.draw_zombie(zombie)
        self.draw_player()
        for particle in self.particles:
            alpha = max(0, min(255, int(255 * particle["life"] / particle["max_life"])))
            surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            surface.fill((*particle["color"], alpha))
            self.screen.blit(surface, (particle["pos"].x, particle["pos"].y))
        self.draw_hud()
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self):
        running = True
        self.restart_rect = pygame.Rect(0, 0, 0, 0)
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.035)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.game_over and self.restart_rect.collidepoint(event.pos):
                        self.reset()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
