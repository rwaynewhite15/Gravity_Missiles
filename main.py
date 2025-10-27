import pygame
import math
import random

pygame.init()
pygame.mixer.init() # Initialize mixer for sound effects

# Load sounds
try:
    # Sound effects
    sound_explode = pygame.mixer.Sound('sound/explode.wav')
    sound_hit = pygame.mixer.Sound('sound/hit.wav')
    sound_choose = pygame.mixer.Sound('sound/shoot.wav')
    sound_fire = pygame.mixer.Sound('sound/fire.wav')
    sound_explode.set_volume(0.15)  # Set explosion sound volume lower
    sound_hit.set_volume(0.125)  # Set hit sound volume lower
    sound_choose.set_volume(0.125)  # Set choose sound volume lower
    sound_fire.set_volume(0.125)  # Set fire sound volume lower
    # Background music
    pygame.mixer.music.load('sound/boss.ogg')
    pygame.mixer.music.set_volume(0.25)  # 25% volume
    pygame.mixer.music.play(-1)  # Loop forever
except:
    print("Sound files not found - continuing without sound")

WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Missiles")
clock = pygame.time.Clock()

# Load background image
try:
    background = pygame.image.load('bg5.jpg')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # Scale to fit screen
except:
    print("Background image not found - using black background")
    background = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 50)
GRAY = (150, 150, 150)
PURPLE = (180, 100, 200)
ORANGE = (255, 150, 50)
GREEN = (50, 200, 50)

# Game States
MENU = 0
PLAYING = 1
GAME_OVER = 2

class GravityObject:
    def __init__(self, x, y, mass):
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = max(15, min(40, mass / 50))
        
        # Assign a random planet type
        planet_types = ['mars', 'jupiter', 'saturn', 'neptune', 'uranus', 'venus']
        self.planet_type = random.choice(planet_types)

    def draw(self, screen):
        # Draw gravity well visualization
        for i in range(3):
            alpha_radius = self.radius + i * 20
            pygame.draw.circle(screen, (*PURPLE[:3], 30), (int(self.x), int(self.y)), int(alpha_radius), 1)
        
        # Draw planet based on type
        if self.planet_type == 'mars':
            # Mars - Red planet
            pygame.draw.circle(screen, (193, 68, 14), (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(screen, (150, 50, 10), (int(self.x - self.radius/3), int(self.y - self.radius/3)), int(self.radius/4))
            pygame.draw.circle(screen, (170, 60, 12), (int(self.x + self.radius/4), int(self.y + self.radius/4)), int(self.radius/3))
        
        elif self.planet_type == 'jupiter':
            # Jupiter - Orange with stripes
            pygame.draw.circle(screen, (216, 146, 88), (int(self.x), int(self.y)), int(self.radius))
            # Bands
            for i in range(-1, 1):
                y_offset = i * self.radius / 3
                pygame.draw.ellipse(screen, (180, 120, 70), 
                                  (self.x - self.radius, self.y + y_offset - 3, self.radius * 2, 6))
            # Great Red Spot
            pygame.draw.ellipse(screen, (200, 100, 80), 
                              (self.x - self.radius/2, self.y, self.radius * 0.6, self.radius * 0.4))
        
        elif self.planet_type == 'saturn':
            # Saturn - Pale yellow with rings
            pygame.draw.circle(screen, (237, 221, 152), (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(screen, (220, 200, 130), (int(self.x), int(self.y)), int(self.radius), 2)
            # Rings
            ring_width = self.radius * 4
            ring_height = self.radius * 0.4
            pygame.draw.ellipse(screen, (200, 180, 120), 
                              (self.x - ring_width/2, self.y - ring_height/2, ring_width, ring_height), 3)
            pygame.draw.ellipse(screen, (180, 160, 100), 
                              (self.x - ring_width/2 + 4, self.y - ring_height/2 + 2, ring_width - 8, ring_height - 4), 2)
        
        elif self.planet_type == 'neptune':
            # Neptune - Deep blue
            pygame.draw.circle(screen, (62, 84, 232), (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(screen, (82, 104, 255), (int(self.x - self.radius/2), int(self.y - self.radius/4)), int(self.radius/3))
            # Dark spot
            pygame.draw.ellipse(screen, (40, 60, 180), 
                              (self.x - self.radius/3, self.y, self.radius * 0.5, self.radius * 0.2))
        
        elif self.planet_type == 'uranus':
            # Uranus - Cyan/turquoise
            pygame.draw.circle(screen, (79, 208, 231), (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(screen, (100, 220, 240), (int(self.x), int(self.y)), int(self.radius), 2)
            # Faint bands
            for i in range(0, 1):
                y_offset = i * self.radius / 2
                pygame.draw.line(screen, (60, 180, 200), 
                               (self.x - self.radius, self.y + y_offset), 
                               (self.x + self.radius, self.y + y_offset), 4)
        
        elif self.planet_type == 'venus':
            # Venus - Pale yellow/white
            pygame.draw.circle(screen, (255, 240, 200), (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(screen, (240, 220, 180), (int(self.x), int(self.y)), int(self.radius), 2)
            # Cloud patterns
            pygame.draw.arc(screen, (230, 210, 170), 
                          (self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2), 
                          0, 3.14, 2)
        
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
        G = 5.0
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
        
        # Generate random shape points
        self.num_points = random.randint(8, 12)
        self.shape_points = []
        for i in range(self.num_points):
            angle = (2 * math.pi * i) / self.num_points
            # Randomize radius for each point to make irregular shape
            point_radius = self.radius * random.uniform(0.7, 1.0)
            point_x = self.x + math.cos(angle) * point_radius
            point_y = self.y + math.sin(angle) * point_radius
            self.shape_points.append((point_x, point_y))
        
    def draw(self, screen):
        if not self.destroyed:
            # Draw asteroid with irregular rocky shape
            if len(self.shape_points) > 2:
                pygame.draw.polygon(screen, self.color, self.shape_points)
                pygame.draw.polygon(screen, (100, 100, 100), self.shape_points, 3)
            
            # Add some crater details
            for i in range(2):
                angle = math.pi
                distance = self.radius * i * .125 + 1
                crater_x = int(self.x + math.cos(angle) * distance)
                crater_y = int(self.y + math.sin(angle) * distance)
                crater_size = 5
                pygame.draw.circle(screen, (120, 120, 120), (crater_x, crater_y), crater_size)
    
    def check_collision(self, missile_x, missile_y):
        if not self.destroyed:
            dist = math.sqrt((missile_x - self.x)**2 + (missile_y - self.y)**2)
            return dist < self.radius
        return False
    
    def explode(self, missile_vx, missile_vy):
        """Create multiple missiles firing in all directions"""
        self.destroyed = True
        fragments = []
        num_fragments = random.randint(10, 15)
        
        for i in range(num_fragments):
            vx = missile_vx + random.uniform(-10, 10)
            vy = missile_vy + random.uniform(-10, 10)
            fragment = Missile(self.x, self.y, vx, vy, GRAY)
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
    def __init__(self, x, y, color, name, is_cpu=False):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.angle = -45 if x < WIDTH/2 else -135
        self.power = 10
        self.health = 100
        self.is_cpu = is_cpu
        self.destroyed = False
        
    def draw(self, screen, is_active):
        if self.destroyed:
            return  # Don't draw if destroyed
        
        # Draw health bar
        bar_width = 60
        bar_height = 8
        health_width = int(bar_width * (self.health / 100))
        pygame.draw.rect(screen, GRAY, (self.x - bar_width//2, self.y - 50, bar_width, bar_height))
        pygame.draw.rect(screen, self.color, (self.x - bar_width//2, self.y - 50, health_width, bar_height))
        
        # Draw flying saucer
        # Bottom dome
        pygame.draw.ellipse(screen, self.color, (self.x - 25, self.y - 5, 50, 15))
        pygame.draw.ellipse(screen, tuple(max(0, c - 50) for c in self.color), (self.x - 25, self.y - 5, 50, 15), 2)
        
        # Middle disk (main body)
        pygame.draw.ellipse(screen, self.color, (self.x - 30, self.y - 15, 60, 20))
        pygame.draw.ellipse(screen, tuple(min(255, c + 50) for c in self.color), (self.x - 30, self.y - 15, 60, 20), 2)
        
        # Top dome (cockpit)
        pygame.draw.ellipse(screen, tuple(min(255, c + 80) for c in self.color), (self.x - 15, self.y - 25, 30, 15))
        pygame.draw.ellipse(screen, WHITE, (self.x - 15, self.y - 25, 30, 15), 1)
        
        # Windows/lights
        pygame.draw.circle(screen, YELLOW, (int(self.x - 15), int(self.y - 5)), 3)
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y - 5)), 3)
        pygame.draw.circle(screen, YELLOW, (int(self.x + 15), int(self.y - 5)), 3)
        
        # Draw cannon (energy beam emitter)
        angle_rad = math.radians(self.angle)
        cannon_start_x = self.x + math.cos(angle_rad) * 15
        cannon_start_y = self.y + math.sin(angle_rad) * 10
        end_x = self.x + math.cos(angle_rad) * 40
        end_y = self.y + math.sin(angle_rad) * 40
        
        # Beam emitter
        pygame.draw.line(screen, tuple(min(255, c + 100) for c in self.color), 
                        (cannon_start_x, cannon_start_y), (end_x, end_y), 4)
        pygame.draw.circle(screen, YELLOW, (int(end_x), int(end_y)), 4)
        
        # Draw power indicator if active
        if is_active:
            power_length = self.power * 5
            power_x = self.x + math.cos(angle_rad) * (40 + power_length)
            power_y = self.y + math.sin(angle_rad) * (40 + power_length)
            pygame.draw.line(screen, YELLOW, (end_x, end_y), (power_x, power_y), 3)
            # Pulsing effect
            pygame.draw.circle(screen, YELLOW, (int(power_x), int(power_y)), 6, 2)
        
        # Draw name
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, WHITE)
        screen.blit(text, (self.x - text.get_width()//2, self.y + 25))
        
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
        if self.health <= 0:
            self.destroyed = True
        return self.health <= 0

    def explode(self, missile_vx, missile_vy):
        """Create multiple missiles firing in all directions when destroyed"""
        fragments = []
        num_fragments = random.randint(15, 20)
        
        for i in range(num_fragments):
            vx = missile_vx + random.uniform(-15, 15)
            vy = missile_vy + random.uniform(-15, 15)
            fragment = Missile(self.x, self.y, vx, vy, self.color)
            fragments.append(fragment)
        
        return fragments

class CPUPlayer:
    def __init__(self, difficulty):
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.aim_timer = 0
        self.aim_duration = 60  # frames to "think" before shooting
        self.has_aimed = False
        
    def reset_aim(self):
        self.aim_timer = 0
        self.has_aimed = False
        
    def update(self, cpu_pad, target_pad, gravity_objects, black_holes):
        """Update CPU AI and return True when ready to fire"""
        if not self.has_aimed:
            self.aim_timer += 1
            
            if self.aim_timer >= self.aim_duration:
                self.aim(cpu_pad, target_pad, gravity_objects, black_holes)
                self.has_aimed = True
                return True
        return False
    
    def aim(self, cpu_pad, target_pad, gravity_objects, black_holes):
        """Calculate angle and power to hit target"""
        dx = target_pad.x - cpu_pad.x
        dy = target_pad.y - cpu_pad.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if self.difficulty == "easy":
            # Easy: Aim roughly at opponent with large randomness
            base_angle = math.degrees(math.atan2(dy, dx))
            cpu_pad.angle = base_angle + random.uniform(-30, 30)
            cpu_pad.power = random.randint(8, 16)
            
        elif self.difficulty == "medium":
            # Medium: Better aim, considers distance
            base_angle = math.degrees(math.atan2(dy, dx))
            cpu_pad.angle = base_angle + random.uniform(-15, 15)
            
            # Adjust power based on distance
            power = distance / 80
            power = max(8, min(18, power))
            cpu_pad.power = power + random.uniform(-2, 2)
            
        elif self.difficulty == "hard":
            # Hard: Simulate trajectory to find best shot
            best_angle = None
            best_power = None
            best_score = float('inf')
            
            # Try multiple angle/power combinations
            for test_angle in range(-180, 180, 10):
                for test_power in range(8, 20, 2):
                    score = self.simulate_shot(cpu_pad, target_pad, test_angle, test_power, 
                                              gravity_objects, black_holes)
                    if score < best_score:
                        best_score = score
                        best_angle = test_angle
                        best_power = test_power

            # little randomness to avoid perfect shots
            cpu_pad.angle = best_angle + random.uniform(-.025, .025)
            cpu_pad.power = best_power + random.uniform(-.05, .05)

    def simulate_shot(self, cpu_pad, target_pad, angle, power, gravity_objects, black_holes):
        """Simulate a shot and return distance to target (lower is better)"""
        angle_rad = math.radians(angle)
        x = cpu_pad.x + math.cos(angle_rad) * 35
        y = cpu_pad.y + math.sin(angle_rad) * 35
        vx = math.cos(angle_rad) * power
        vy = math.sin(angle_rad) * power
        
        min_dist = float('inf')
        
        # Simulate for limited steps
        for step in range(200):
            # Apply gravity
            for obj in gravity_objects:
                fx, fy = obj.get_gravity_force(x, y)
                vx += fx
                vy += fy
            
            for bh in black_holes:
                fx, fy = bh.get_gravity_force(x, y)
                vx += fx
                vy += fy
                
                # Check if captured
                if bh.check_captured(x, y):
                    return float('inf')  # Bad shot
            
            # Update position
            x += vx
            y += vy
            
            # Check distance to target
            dist = math.sqrt((x - target_pad.x)**2 + (y - target_pad.y)**2)
            min_dist = min(min_dist, dist)
            
            # If very close, this is a good shot
            if dist < 30:
                return dist
            
            # Check boundaries
            if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
                break
        
        return min_dist

# Game setup functions
def create_gravity_objects():
    objects = []
    num_objects = 3
    min_distance_between_planets = 250  # Planets should be far from each other
    
    for _ in range(num_objects):
        attempts = 0
        while attempts < 100:
            x = random.randint(300, WIDTH - 300)
            y = random.randint(250, HEIGHT - 250)
            
            # Check distance from all existing planets
            valid = True
            for obj in objects:
                dist = math.sqrt((x - obj.x)**2 + (y - obj.y)**2)
                if dist < min_distance_between_planets:
                    valid = False
                    break
            
            if valid:
                mass = random.randint(1000, 3000)
                objects.append(GravityObject(x, y, mass))
                break
            
            attempts += 1
    
    return objects

def create_black_holes(gravity_objects, launch_pads):
    black_holes = []
    num_black_holes = 1
    min_distance_from_planets = 300  # Black holes need even more space from planets
    min_distance_from_pads = 250
    
    for _ in range(num_black_holes):
        attempts = 0
        while attempts < 100:
            x = random.randint(int(WIDTH * 0.3), int(WIDTH * 0.7))
            y = random.randint(250, HEIGHT - 250)
            
            # Check distance from launch pads
            valid = True
            for pad in launch_pads:
                dist = math.sqrt((x - pad.x)**2 + (y - pad.y)**2)
                if dist < min_distance_from_pads:
                    valid = False
                    break
            
            # Check distance from planets (gravity objects)
            if valid:
                for obj in gravity_objects:
                    dist = math.sqrt((x - obj.x)**2 + (y - obj.y)**2)
                    if dist < min_distance_from_planets:
                        valid = False
                        break
            
            # Check distance from other black holes
            if valid:
                for bh in black_holes:
                    dist = math.sqrt((x - bh.x)**2 + (y - bh.y)**2)
                    if dist < min_distance_from_planets:
                        valid = False
                        break
            
            if valid:
                black_holes.append(BlackHole(x, y))
                break
            
            attempts += 1
    
    return black_holes

def create_asteroids(gravity_objects, black_holes, launch_pads):
    asteroids = []
    num_asteroids = 1
    min_distance = 150  # Minimum distance from other objects
    
    for _ in range(num_asteroids):
        attempts = 0
        while attempts < 100:
            x = random.randint(int(WIDTH * 0.2), int(WIDTH * 0.8))
            y = random.randint(150, HEIGHT - 150)
            
            # Check distance from launch pads
            valid = True
            for pad in launch_pads:
                dist = math.sqrt((x - pad.x)**2 + (y - pad.y)**2)
                if dist < min_distance:
                    valid = False
                    break
            
            # Check distance from gravity objects
            if valid:
                for obj in gravity_objects:
                    dist = math.sqrt((x - obj.x)**2 + (y - obj.y)**2)
                    if dist < min_distance:
                        valid = False
                        break
            
            # Check distance from black holes
            if valid:
                for bh in black_holes:
                    dist = math.sqrt((x - bh.x)**2 + (y - bh.y)**2)
                    if dist < min_distance:
                        valid = False
                        break
            
            # Check distance from other asteroids
            if valid:
                for ast in asteroids:
                    dist = math.sqrt((x - ast.x)**2 + (y - ast.y)**2)
                    if dist < min_distance:
                        valid = False
                        break
            
            if valid:
                asteroids.append(Asteroid(x, y))
                break
            
            attempts += 1
    
    return asteroids

def create_launch_pads(is_cpu=False, cpu_difficulty=None):
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
    
    if is_cpu:
        player2 = LaunchPad(x2, y2, BLUE, f"CPU ({cpu_difficulty.capitalize()})", is_cpu=True)
    else:
        player2 = LaunchPad(x2, y2, BLUE, "Player 2")
    
    player1.angle = angle1
    player2.angle = angle2
    
    return player1, player2

def draw_menu(screen, font_large, font_med, selected_option):
    # Draw background
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)

    # Title
    title = font_large.render("GRAVITY MISSILES", True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    
    # Menu options
    options = [
        ("1. Player vs Player", WHITE if selected_option != 0 else GREEN),
        ("2. Player vs CPU (Easy)", WHITE if selected_option != 1 else GREEN),
        ("3. Player vs CPU (Medium)", WHITE if selected_option != 2 else GREEN),
        ("4. Player vs CPU (Hard)", WHITE if selected_option != 3 else GREEN),
        ("Q. Quit", WHITE if selected_option != 4 else GREEN)
    ]
    
    y_pos = 300
    for text, color in options:
        option_text = font_med.render(text, True, color)
        screen.blit(option_text, (WIDTH//2 - option_text.get_width()//2, y_pos))
        y_pos += 60
    
    # Instructions
    instructions = font_med.render("Use Arrow Keys and Press Enter", True, GRAY)
    screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 100))

def reset_game(is_cpu, cpu_difficulty):
    player1, player2 = create_launch_pads(is_cpu, cpu_difficulty)
    players = [player1, player2]
    gravity_objects = create_gravity_objects()
    black_holes = create_black_holes(gravity_objects, players)
    asteroids = create_asteroids(gravity_objects, black_holes, players)
    missiles = []
    shot_history = []
    current_player = 0
    winner = None
    missile_fired = False
    active_missile = None
    
    cpu_ai = None
    if is_cpu:
        cpu_ai = CPUPlayer(cpu_difficulty)
    
    return (player1, player2, players, gravity_objects, black_holes, 
            asteroids, missiles, shot_history, current_player, winner, missile_fired, 
            active_missile, cpu_ai)

# Initialize game
game_state = MENU
selected_menu_option = 0
is_cpu_game = False
cpu_difficulty = None
cpu_ai = None

player1, player2 = create_launch_pads()
players = [player1, player2]
gravity_objects = create_gravity_objects()
black_holes = create_black_holes(gravity_objects, players)
asteroids = create_asteroids(gravity_objects, black_holes, players)
missiles = []
shot_history = []  # Keep track of last 5 shots
current_player = 0
players = [player1, player2]
winner = None
active_missile = None
missile_fired = False

font_large = pygame.font.Font(None, 48)
font_med = pygame.font.Font(None, 32)
font_small = pygame.font.Font(None, 24)

# Game loop
running = True
clock = pygame.time.Clock()
mouse_dragging = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if game_state == PLAYING and not missile_fired:
                    current = players[current_player]
                    if not current.is_cpu:
                        # Check if clicking near the current player
                        mouse_x, mouse_y = event.pos
                        dist = math.sqrt((mouse_x - current.x)**2 + (mouse_y - current.y)**2)
                        if dist < 100:  # Within 100 pixels of player
                            mouse_dragging = True
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_dragging = False
        
        if event.type == pygame.MOUSEMOTION:
            if mouse_dragging and game_state == PLAYING and not missile_fired:
                current = players[current_player]
                if not current.is_cpu:
                    mouse_x, mouse_y = event.pos
                    
                    # Calculate angle from player to mouse
                    dx = mouse_x - current.x
                    dy = mouse_y - current.y
                    current.angle = math.degrees(math.atan2(dy, dx))
                    
                    # Calculate power based on distance (capped between 3 and 20)
                    distance = math.sqrt(dx**2 + dy**2)
                    current.power = max(3, min(20, distance / 10))

        if event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_UP:
                    if sound_choose:
                        sound_choose.play()
                    selected_menu_option = (selected_menu_option - 1) % 5
                elif event.key == pygame.K_DOWN:
                    if sound_choose:
                        sound_choose.play()
                    selected_menu_option = (selected_menu_option + 1) % 5
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if sound_fire:
                        sound_fire.play()
                    if selected_menu_option == 0:
                        # PvP
                        is_cpu_game = False
                        cpu_difficulty = None
                        (player1, player2, players, gravity_objects, black_holes, 
                         asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                         active_missile, cpu_ai) = reset_game(False, None)
                        game_state = PLAYING
                    elif selected_menu_option == 1:
                        # CPU Easy
                        is_cpu_game = True
                        cpu_difficulty = "easy"
                        (player1, player2, players, gravity_objects, black_holes, 
                         asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                         active_missile, cpu_ai) = reset_game(True, "easy")
                        game_state = PLAYING
                    elif selected_menu_option == 2:
                        # CPU Medium
                        is_cpu_game = True
                        cpu_difficulty = "medium"
                        (player1, player2, players, gravity_objects, black_holes, 
                         asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                         active_missile, cpu_ai) = reset_game(True, "medium")
                        game_state = PLAYING
                    elif selected_menu_option == 3:
                        # CPU Hard
                        is_cpu_game = True
                        cpu_difficulty = "hard"
                        (player1, player2, players, gravity_objects, black_holes, 
                         asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                         active_missile, cpu_ai) = reset_game(True, "hard")
                        game_state = PLAYING
                    elif selected_menu_option == 4:
                        running = False
                elif event.key == pygame.K_1:
                    is_cpu_game = False
                    cpu_difficulty = None
                    (player1, player2, players, gravity_objects, black_holes, 
                     asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                     active_missile, cpu_ai) = reset_game(False, None)
                    game_state = PLAYING
                elif event.key == pygame.K_2:
                    is_cpu_game = True
                    cpu_difficulty = "easy"
                    (player1, player2, players, gravity_objects, black_holes, 
                     asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                     active_missile, cpu_ai) = reset_game(True, "easy")
                    game_state = PLAYING
                elif event.key == pygame.K_3:
                    is_cpu_game = True
                    cpu_difficulty = "medium"
                    (player1, player2, players, gravity_objects, black_holes, 
                     asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                     active_missile, cpu_ai) = reset_game(True, "medium")
                    game_state = PLAYING
                elif event.key == pygame.K_4:
                    is_cpu_game = True
                    cpu_difficulty = "hard"
                    (player1, player2, players, gravity_objects, black_holes, 
                     asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                     active_missile, cpu_ai) = reset_game(True, "hard")
                    game_state = PLAYING
                elif event.key == pygame.K_q:
                    running = False
                    
            elif game_state == PLAYING:
                current = players[current_player]
                
                # Only allow human input if current player is not CPU
                if not current.is_cpu:
                    if not missile_fired:
                        if event.key == pygame.K_LEFT:
                            current.angle -= .5
                        elif event.key == pygame.K_RIGHT:
                            current.angle += .5
                        elif event.key == pygame.K_UP:
                            current.power = min(20, current.power + .5)
                        elif event.key == pygame.K_DOWN:
                            current.power = max(3, current.power - .5)
                        elif event.key == pygame.K_SPACE:
                            if sound_fire:
                                sound_fire.play()
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
                
                if event.key == pygame.K_p:
                    # End current turn and switch to next player
                    current_player = 1 - current_player
                    missile_fired = False
                    active_missile = None
                    # Deactivate any active missiles
                    for missile in missiles:
                        missile.active = False
                    # Reset asteroids for next turn
                    asteroids = create_asteroids(gravity_objects, black_holes, players)
                    # Reset CPU AI if switching to CPU
                    if is_cpu_game and players[current_player].is_cpu:
                        cpu_ai.reset_aim()
                
                if event.key == pygame.K_r:
                    # Reset game with same settings
                    (player1, player2, players, gravity_objects, black_holes, 
                     asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                     active_missile, cpu_ai) = reset_game(is_cpu_game, cpu_difficulty)
                    game_state = PLAYING
                    
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    selected_menu_option = 0
                    
            elif game_state == GAME_OVER:
                if event.key == pygame.K_r:
                    # Reset game with same settings
                    (player1, player2, players, gravity_objects, black_holes, 
                     asteroids, missiles, shot_history, current_player, winner, missile_fired, 
                     active_missile, cpu_ai) = reset_game(is_cpu_game, cpu_difficulty)
                    game_state = PLAYING
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    selected_menu_option = 0
    
    # Update game logic
    if game_state == PLAYING or game_state == GAME_OVER:
        # CPU AI logic (only during PLAYING)
        if game_state == PLAYING and is_cpu_game and players[current_player].is_cpu and not missile_fired:
            if cpu_ai.update(players[current_player], players[1 - current_player], 
                           gravity_objects, black_holes):
                # CPU is ready to fire
                missile = players[current_player].fire()
                if sound_fire:
                    sound_fire.play()
                missiles.append(missile)
                missile_fired = True
                active_missile = missile
                cpu_ai.reset_aim()
        
        # Update missiles (continue even during GAME_OVER)
        if missile_fired:
            all_inactive = True
            for missile in missiles:
                if missile.active:
                    missile.update(gravity_objects, black_holes)
                    all_inactive = False
                    
                    # Check collision with asteroids
                    for asteroid in asteroids:
                        if missile.active and asteroid.check_collision(missile.x, missile.y):
                            if sound_explode:
                                sound_explode.play()
                            missile.active = False
                            # Create fragment missiles from asteroid
                            fragments = asteroid.explode(missile.vx, missile.vy)
                            missiles.extend(fragments)
                            break
                    
                    # Check collision with players (including friendly fire)
                    for i, player in enumerate(players):
                        if missile.active and not player.destroyed and game_state == PLAYING:
                            dist = math.sqrt((missile.x - player.x)**2 + (missile.y - player.y)**2)
                            if dist < 25:
                                if sound_hit:
                                    sound_hit.play()
                                missile.active = False
                                if player.take_damage(20):
                                    # Player destroyed - create explosion
                                    if sound_explode:
                                        sound_explode.play()
                                    fragments = player.explode(missile.vx, missile.vy)
                                    missiles.extend(fragments)
                                    game_state = GAME_OVER
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
            if all_inactive and game_state == PLAYING:
                # Save the trails of missiles from this shot to history
                shot_trails = []
                for missile in missiles:
                    if len(missile.trail) > 1:
                        shot_trails.append((missile.trail[:], missile.color))
                
                if shot_trails:
                    # Store with player identifier
                    shot_history.append((current_player, shot_trails))
                    
                    # Keep only the last shot from each player (max 2 shots total)
                    # Remove older shots from the same player
                    player_shots = [i for i, (player_id, _) in enumerate(shot_history) if player_id == current_player]
                    if len(player_shots) > 1:
                        # Remove the oldest shot from this player
                        shot_history.pop(player_shots[0])
                
                current_player = 1 - current_player
                missile_fired = False
                active_missile = None
                # Reset asteroids for next turnPP
                asteroids = create_asteroids(gravity_objects, black_holes, players)
                # Clear current missiles
                missiles = []
                # Reset CPU AI if switching to CPU
                if is_cpu_game and players[current_player].is_cpu:
                    cpu_ai.reset_aim()
    
    # Draw background
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)
    
    if game_state == MENU:
        draw_menu(screen, font_large, font_med, selected_menu_option)
        
    elif game_state == PLAYING:
        # Draw gravity objects
        for obj in gravity_objects:
            obj.draw(screen)
        
        # Draw black holes
        for bh in black_holes:
            bh.draw(screen)
        
        # Draw asteroids
        for asteroid in asteroids:
            asteroid.draw(screen)
        
        # Draw previous shot trails (last shot from each player)
        for player_id, shot in shot_history:
            for trail, color in shot:
                if len(trail) > 1:
                    for i in range(len(trail) - 1):
                        pygame.draw.line(screen, color, trail[i], trail[i+1], 1)

        # Draw current missiles
        for missile in missiles:
            missile.draw(screen)
        
        # Draw players
        for i, player in enumerate(players):
            player.draw(screen, i == current_player and not missile_fired)
        
        # Draw UI
        turn_text = font_med.render(f"{players[current_player].name}'s Turn", True, players[current_player].color)
        screen.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, 20))
        
        if missile_fired and active_missile and active_missile.active and not players[current_player].is_cpu:
            controls = f"Space/↑: Forward | ↓/Shift: Reverse | ←/→: Strafe ({active_missile.fuel} fuel) | P: End Turn"
            controls_text = font_small.render(controls, True, ORANGE)
        elif not players[current_player].is_cpu:
            controls = "Arrow Keys: Aim & Power | Space: Fire | P: End Turn | ESC: Menu"
            controls_text = font_small.render(controls, True, WHITE)
        else:
            controls = "CPU is thinking..."
            controls_text = font_small.render(controls, True, YELLOW)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, 60))
    
    elif game_state == GAME_OVER:
        # Draw final game state
        for obj in gravity_objects:
            obj.draw(screen)
        for bh in black_holes:
            bh.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)
        for missile in missiles:
            missile.draw(screen)
        for player in players:
            player.draw(screen, False)
        
        # Draw game over text
        game_over_text = font_large.render(f"{winner.name} Wins!", True, winner.color)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        
        restart_text = font_med.render("Press R to Restart | ESC for Menu", True, WHITE)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()