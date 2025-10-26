import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 2400, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Artillery")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 50)
GRAY = (150, 150, 150)
PURPLE = (180, 100, 200)
ORANGE = (255, 150, 50)

class GravityObject:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = max(15, min(40, mass / 50))
        
    def draw(self, screen):
        # Draw gravity well visualization
        for i in range(3):
            alpha_radius = self.radius + i * 20
            pygame.draw.circle(screen, (*PURPLE[:3], 30), (int(self.x), int(self.y)), int(alpha_radius), 1)
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), int(self.radius))
        
    def get_gravity_force(self, x, y):
        dx = self.x - x
        dy = self.y - y
        dist_sq = dx*dx + dy*dy + 1  # +1 to avoid division by zero
        dist = math.sqrt(dist_sq)
        
        # Gravitational force: F = G * m1 * m2 / r^2
        G = 1.0  # Gravitational constant (scaled for gameplay)
        force = G * self.mass / dist_sq
        
        # Return force components
        if dist > 0:
            return (force * dx / dist, force * dy / dist)
        return (0, 0)

class BlackHole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.mass = 8000  # Much stronger than regular gravity objects
        self.event_horizon = 35  # Point of no return
        self.radius = 20
        
    def draw(self, screen):
        # Draw accretion disk (swirling effect)
        for i in range(5):
            alpha_radius = self.event_horizon + i * 15
            color = (100 - i * 15, 0, 100 - i * 15)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(alpha_radius), 2)
        
        # Draw event horizon
        pygame.draw.circle(screen, (50, 0, 50), (int(self.x), int(self.y)), self.event_horizon, 3)
        
        # Draw black hole center
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (20, 0, 20), (int(self.x), int(self.y)), self.radius, 2)
        
    def get_gravity_force(self, x, y):
        dx = self.x - x
        dy = self.y - y
        dist_sq = dx*dx + dy*dy + 1
        dist = math.sqrt(dist_sq)
        
        # Much stronger gravitational constant for black holes
        G = 3.0
        force = G * self.mass / dist_sq
        
        if dist > 0:
            return (force * dx / dist, force * dy / dist)
        return (0, 0)
    
    def check_captured(self, missile_x, missile_y):
        """Check if missile has crossed the event horizon"""
        dist = math.sqrt((missile_x - self.x)**2 + (missile_y - self.y)**2)
        return dist < self.event_horizon

class Asteroid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(25, 45)
        self.color = (150, 150, 150)
        self.destroyed = False
        
    def draw(self, screen):
        if not self.destroyed:
            # Draw asteroid with rocky appearance
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), self.radius, 3)
            # Add some detail circles
            pygame.draw.circle(screen, (120, 120, 120), (int(self.x - 8), int(self.y - 8)), 5)
            pygame.draw.circle(screen, (120, 120, 120), (int(self.x + 10), int(self.y + 5)), 7)
    
    def check_collision(self, missile_x, missile_y):
        if not self.destroyed:
            dist = math.sqrt((missile_x - self.x)**2 + (missile_y - self.y)**2)
            return dist < self.radius
        return False
    
    def explode(self, missile_color, missile_vx, missile_vy):
        """Create multiple missiles firing in all directions"""
        self.destroyed = True
        fragments = []
        num_fragments = random.randint(10, 15)
        
        for i in range(num_fragments):
            # angle = (360 / num_fragments) * i + random.uniform(-15, 15)
            # angle_rad = math.radians(angle)
            # speed = random.uniform(10, 50)
            # vx = math.cos(angle_rad) * speed
            # vy = math.sin(angle_rad) * speed
            vx = missile_vx + random.uniform(-10, 10)
            vy = missile_vy + random.uniform(-10, 10)
            fragment = Missile(self.x, self.y, vx, vy, missile_color)
            fragments.append(fragment)
        
        return fragments

class Missile:
    def __init__(self, x, y, vx, vy, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.active = True
        self.trail = []
        self.fuel = 20  # Number of thrusts available
        self.thrust_cooldown = 0
        
    def apply_thrust(self):
        if self.fuel > 0 and self.thrust_cooldown <= 0:
            # Apply thrust in current direction of movement
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > 0:
                thrust_amount = 5.0
                self.vx += (self.vx / speed) * thrust_amount
                self.vy += (self.vy / speed) * thrust_amount
                self.fuel -= 1
                self.thrust_cooldown = 10  # Cooldown frames
                return True
        return False

    def apply_reverse_thrust(self):
        if self.fuel > 0 and self.thrust_cooldown <= 0:
            # Apply thrust in opposite direction of movement
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > 0:
                thrust_amount = 5.0
                self.vx -= (self.vx / speed) * thrust_amount
                self.vy -= (self.vy / speed) * thrust_amount
                self.fuel -= 1
                self.thrust_cooldown = 10  # Cooldown frames
                return True
        return False
    
    def apply_left_thrust(self):
        if self.fuel > 0 and self.thrust_cooldown <= 0:
            # Apply thrust perpendicular to current direction (left)
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > 0:
                thrust_amount = 5.0
                # Rotate velocity vector 90 degrees counter-clockwise
                perp_x = -self.vy / speed
                perp_y = self.vx / speed
                self.vx += perp_x * thrust_amount
                self.vy += perp_y * thrust_amount
                self.fuel -= 1
                self.thrust_cooldown = 10
                return True
        return False
    
    def apply_right_thrust(self):
        if self.fuel > 0 and self.thrust_cooldown <= 0:
            # Apply thrust perpendicular to current direction (right)
            speed = math.sqrt(self.vx**2 + self.vy**2)
            if speed > 0:
                thrust_amount = 5.0
                # Rotate velocity vector 90 degrees clockwise
                perp_x = self.vy / speed
                perp_y = -self.vx / speed
                self.vx += perp_x * thrust_amount
                self.vy += perp_y * thrust_amount
                self.fuel -= 1
                self.thrust_cooldown = 10
                return True
        return False
        
    def update(self, gravity_objects, black_holes):
        if not self.active:
            return
        
        if self.thrust_cooldown > 0:
            self.thrust_cooldown -= 1
            
        # Apply gravity from all objects
        for obj in gravity_objects:
            fx, fy = obj.get_gravity_force(self.x, self.y)
            self.vx += fx
            self.vy += fy
        
        # Apply gravity from black holes (much stronger)
        for bh in black_holes:
            fx, fy = bh.get_gravity_force(self.x, self.y)
            self.vx += fx
            self.vy += fy
            
            # Check if captured by black hole
            if bh.check_captured(self.x, self.y):
                self.active = False
                return
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Add to trail
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 100:
            self.trail.pop(0)
        
        # Check boundaries
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False
            
    def draw(self, screen):
        # Draw trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = i / len(self.trail)
                color = tuple(int(c * alpha) for c in self.color)
                pygame.draw.line(screen, color, self.trail[i], self.trail[i+1], 2)
        
        # Draw missile
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)
            
            # Draw thrust effect if recently thrusted
            if self.thrust_cooldown > 5:
                pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 8, 2)

class LaunchPad:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.angle = -45 if x < WIDTH/2 else -135
        self.power = 10
        self.health = 100
        
    def draw(self, screen, is_active):
        # Draw health bar
        bar_width = 60
        bar_height = 8
        health_width = int(bar_width * (self.health / 100))
        pygame.draw.rect(screen, GRAY, (self.x - bar_width//2, self.y - 40, bar_width, bar_height))
        pygame.draw.rect(screen, self.color, (self.x - bar_width//2, self.y - 40, health_width, bar_height))
        
        # Draw base
        pygame.draw.rect(screen, self.color, (self.x - 20, self.y - 10, 40, 20))
        
        # Draw cannon
        angle_rad = math.radians(self.angle)
        end_x = self.x + math.cos(angle_rad) * 30
        end_y = self.y + math.sin(angle_rad) * 30
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 6)
        
        # Draw power indicator if active
        if is_active:
            power_length = self.power * 5
            power_x = self.x + math.cos(angle_rad) * (30 + power_length)
            power_y = self.y + math.sin(angle_rad) * (30 + power_length)
            pygame.draw.line(screen, YELLOW, (end_x, end_y), (power_x, power_y), 2)
        
        # Draw name
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, WHITE)
        screen.blit(text, (self.x - text.get_width()//2, self.y + 20))
        
    def fire(self):
        angle_rad = math.radians(self.angle)
        vx = math.cos(angle_rad) * self.power
        vy = math.sin(angle_rad) * self.power
        
        # Start missile from end of cannon
        start_x = self.x + math.cos(angle_rad) * 35
        start_y = self.y + math.sin(angle_rad) * 35
        
        return Missile(start_x, start_y, vx, vy, self.color)
    
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

# Game setup
def create_gravity_objects():
    objects = []
    num_objects = random.randint(1, 4)
    for _ in range(num_objects):
        x = random.randint(200, WIDTH - 200)
        y = random.randint(150, HEIGHT - 150)
        mass = random.randint(1000, 3000)
        objects.append(GravityObject(x, y, mass))
    return objects

def create_black_holes():
    black_holes = []
    num_black_holes = random.randint(1, 2)
    for _ in range(num_black_holes):
        x = random.randint(int(WIDTH * 0.3), int(WIDTH * 0.7))
        y = random.randint(200, HEIGHT - 200)
        black_holes.append(BlackHole(x, y))
    return black_holes

def create_asteroids():
    asteroids = []
    num_asteroids = random.randint(1, 5)
    for _ in range(num_asteroids):
        x = random.randint(int(WIDTH * 0.2), int(WIDTH * 0.8))
        y = random.randint(100, HEIGHT - 100)
        asteroids.append(Asteroid(x, y))
    return asteroids

def create_launch_pads():
    # Place first pad in left 10% of screen
    margin = 50
    x1 = random.randint(margin, int(WIDTH * 0.1))
    y1 = random.randint(margin, HEIGHT - margin)
    
    # Place second pad in right 10% of screen
    x2 = random.randint(int(WIDTH * 0.9), WIDTH - margin)
    y2 = random.randint(margin, HEIGHT - margin)
    
    # Calculate initial angles to point roughly at each other
    angle1 = math.degrees(math.atan2(y2 - y1, x2 - x1))
    angle2 = math.degrees(math.atan2(y1 - y2, x1 - x2))
    
    player1 = LaunchPad(x1, y1, RED, "Player 1")
    player2 = LaunchPad(x2, y2, BLUE, "Player 2")
    player1.angle = angle1
    player2.angle = angle2
    
    return player1, player2

# Initialize game
player1, player2 = create_launch_pads()
gravity_objects = create_gravity_objects()
black_holes = create_black_holes()
asteroids = create_asteroids()
missiles = []
current_player = 0
players = [player1, player2]
game_over = False
winner = None
active_missile = None

# Game loop
running = True
missile_fired = False

font_large = pygame.font.Font(None, 48)
font_med = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if not game_over and not missile_fired:
                current = players[current_player]
                
                if event.key == pygame.K_LEFT:
                    current.angle -= 5
                elif event.key == pygame.K_RIGHT:
                    current.angle += 5
                elif event.key == pygame.K_UP:
                    current.power = min(20, current.power + 1)
                elif event.key == pygame.K_DOWN:
                    current.power = max(3, current.power - 1)
                elif event.key == pygame.K_SPACE:
                    missile = current.fire()
                    missiles.append(missile)
                    missile_fired = True
                    active_missile = missile
            elif missile_fired and active_missile and active_missile.active:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    active_missile.apply_thrust()
                elif event.key == pygame.K_DOWN:
                    active_missile.apply_reverse_thrust()
                elif event.key == pygame.K_RIGHT:
                    active_missile.apply_left_thrust()
                elif event.key == pygame.K_LEFT:
                    active_missile.apply_right_thrust()
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    active_missile.apply_reverse_thrust()
            
            if event.key == pygame.K_r:
                # Reset game
                player1, player2 = create_launch_pads()
                players = [player1, player2]
                gravity_objects = create_gravity_objects()
                black_holes = create_black_holes()
                asteroids = create_asteroids()
                missiles = []
                current_player = 0
                game_over = False
                winner = None
                missile_fired = False
                active_missile = None
    
    # Update missiles
    if missile_fired:
        all_inactive = True
        for missile in missiles:
            if missile.active:
                missile.update(gravity_objects, black_holes)
                all_inactive = False
                
                # Check collision with asteroids
                for asteroid in asteroids:
                    if missile.active and asteroid.check_collision(missile.x, missile.y):
                        missile.active = False
                        # Create fragment missiles from asteroid
                        fragments = asteroid.explode(missile.color, missile.vx, missile.vy)
                        missiles.extend(fragments)
                        break
                
                # Check collision with players
                for i, player in enumerate(players):
                    if missile.active and missile.color != player.color:
                        dist = math.sqrt((missile.x - player.x)**2 + (missile.y - player.y)**2)
                        if dist < 25:
                            missile.active = False
                            if player.take_damage(50):
                                game_over = True
                                winner = players[1-i]
                            else:
                                # Relocate the hit player
                                margin = 50
                                if i == 0:  # Player 1 - left 10%
                                    player.x = random.randint(margin, int(WIDTH * 0.1))
                                else:  # Player 2 - right 10%
                                    player.x = random.randint(int(WIDTH * 0.9), WIDTH - margin)
                                player.y = random.randint(margin, HEIGHT - margin)
                                
                                # Reorient cannon toward opponent
                                other_player = players[1-i]
                                player.angle = math.degrees(math.atan2(other_player.y - player.y, other_player.x - player.x))
        
        # Switch turns when all missiles are done
        if all_inactive and not game_over:
            current_player = 1 - current_player
            missile_fired = False
            active_missile = None
            # Reset asteroids for next turn
            asteroids = create_asteroids()
    
    # Draw
    screen.fill(BLACK)
    
    # Draw gravity objects
    for obj in gravity_objects:
        obj.draw(screen)
    
    # Draw black holes
    for bh in black_holes:
        bh.draw(screen)
    
    # Draw asteroids
    for asteroid in asteroids:
        asteroid.draw(screen)
    
    # Draw missiles
    for missile in missiles:
        missile.draw(screen)
    
    # Draw players
    for i, player in enumerate(players):
        player.draw(screen, i == current_player and not missile_fired and not game_over)
    
    # Draw UI
    if not game_over:
        turn_text = font_med.render(f"{players[current_player].name}'s Turn", True, players[current_player].color)
        screen.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, 20))
        
        if missile_fired and active_missile and active_missile.active:
            controls = f"Space/↑: Forward | ↓/Shift: Reverse | ←/→: Strafe ({active_missile.fuel} fuel)"
            controls_text = font_small.render(controls, True, ORANGE)
        else:
            controls = "Arrow Keys: Aim & Power | Space: Fire"
            controls_text = font_small.render(controls, True, WHITE)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, 60))
    else:
        game_over_text = font_large.render(f"{winner.name} Wins!", True, winner.color)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        
        restart_text = font_med.render("Press R to Restart", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()