import sys
import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Game state variables
class GameState:
    def __init__(self):
        # Player state
        self.player_pos = [0.0, 0.0, 0.0]
        self.player_rotation = 0.0
        self.player_health = 30
        self.player_speed = 0.2
        self.player_size = 0.5
        self.player_color = [0.2, 0.6, 1.0]  # Bright blue
        self.player_shield_active = False
        self.player_shield_timer = 0
        
        # Camera settings
        self.camera_mode = "third_person"  # "first_person" or "third_person"
        self.camera_tilt = 15.0
        self.camera_rotation = 0.0
        
        # Game mechanics
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.paused = False
        self.cheat_mode_active = False
        self.cheat_mode_cooldown = 0
        self.bullets_missed = 0
        self.max_missed_bullets = 100
        
        # Bullet properties
        self.bullets = []
        self.bullet_speed = 1.0
        self.bullet_boost_active = False
        self.bullet_boost_timer = 0
        
        # Asteroids
        self.asteroids = []
        self.boss_asteroid = None
        self.boss_wave_interval = 3
        self.boss_active = False
        self.boss_warning = False
        self.spawn_direction = "front_only"  # Set the spawn direction to front-only
        
        # Power-ups
        self.powerups = []
        self.powerup_spawn_chance = 0.01  # 1% chance per frame
        
        # Visual effects
        self.stars = []
        self.explosions = []
        self.warning_flash_timer = 0
        
        # Colors (vibrant palette)
        self.colors = {
            "player": [0.2, 0.6, 1.0],       # Bright blue
            "bullet": [1.0, 0.8, 0.2],       # Yellow
            "asteroid": [0.8, 0.4, 0.1],     # Orange
            "boss": [1.0, 0.2, 0.2],         # Red
            "health_powerup": [0.2, 1.0, 0.4], # Green
            "speed_powerup": [0.9, 0.4, 1.0], # Purple
            "shield_powerup": [0.0, 0.8, 0.8], # Cyan
            "explosion": [1.0, 0.5, 0.0],    # Bright orange
            "stars": [0.9, 0.9, 1.0],        # White with blue tint
            "hud": [0.0, 1.0, 0.6],          # Neon green
            "hud_warning": [1.0, 0.2, 0.2],  # Red
            "background": [0.02, 0.05, 0.1]  # Dark blue
        }
        
        # Initialize stars
        for _ in range(200):
            self.stars.append([
                random.uniform(-50, 50),  # x
                random.uniform(-50, 50),  # y
                random.uniform(-50, 50),  # z
                random.uniform(0.5, 1.0)  # brightness
            ])
        
        # Initialize asteroid field
        self.spawn_asteroid_wave()

    def spawn_asteroid_wave(self):
        """Spawn a new wave of asteroids with difficulty based on current wave"""
        # Clear existing asteroids
        self.asteroids = []
        
        # Determine if this is a boss wave
        if self.wave % self.boss_wave_interval == 0:
            self.boss_active = True
            self.spawn_boss_asteroid()
        else:
            self.boss_active = False
            
            # Spawn regular asteroids
            asteroid_count = 5 + self.wave * 2  # Increase count with wave
            
            for _ in range(asteroid_count):
                # Randomize asteroid spawn position (only from the front)
                # Calculate the front direction based on player rotation
                player_angle_rad = self.player_rotation * math.pi / 180.0
                front_direction_x = math.sin(player_angle_rad)
                front_direction_z = math.cos(player_angle_rad)
                
                # Create a frontal spawn area (within a 120-degree arc in front of player)
                spawn_angle = player_angle_rad + random.uniform(-math.pi/3, math.pi/3)  # +/- 60 degrees
                distance = random.uniform(20, 30)  # Further away to give player time to react
                
                pos_x = self.player_pos[0] + math.sin(spawn_angle) * distance
                pos_z = self.player_pos[2] + math.cos(spawn_angle) * distance
                
                # Randomize asteroid type
                asteroid_type = random.choice(["normal", "fast", "large"])
                if self.wave < 2:  # Only normal asteroids in first wave
                    asteroid_type = "normal"
                elif self.wave < 4:  # No large asteroids until wave 4
                    asteroid_type = random.choice(["normal", "fast"])
                
                # Create asteroid
                self.spawn_asteroid(pos_x, 0, pos_z, asteroid_type)

    def spawn_asteroid(self, x, y, z, asteroid_type="normal"):
        """Add a new asteroid to the game"""
        speed_multiplier = 1.0 + (self.wave * 0.1)  # Increase speed with wave
        
        asteroid = {
            "pos": [x, y, z],
            "rotation": [random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)],
            "rot_speed": [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)],
            "type": asteroid_type,
            "color": list(self.colors["asteroid"]),
            "hit_points": 1
        }
        
        # Set asteroid specific properties
        if asteroid_type == "normal":
            asteroid["size"] = random.uniform(0.8, 1.2)
            asteroid["speed"] = 0.05 * speed_multiplier
            asteroid["shape"] = "cube"
        elif asteroid_type == "fast":
            asteroid["size"] = random.uniform(0.4, 0.7)
            asteroid["speed"] = 0.1 * speed_multiplier
            asteroid["color"] = [0.9, 0.6, 0.2]  # Lighter orange for fast
            asteroid["shape"] = "sphere"
        elif asteroid_type == "large":
            asteroid["size"] = random.uniform(1.5, 2.5)
            asteroid["speed"] = 0.03 * speed_multiplier
            asteroid["color"] = [0.7, 0.3, 0.1]  # Darker orange for large
            asteroid["hit_points"] = 2
            asteroid["shape"] = "cube"
        
        self.asteroids.append(asteroid)

    def spawn_boss_asteroid(self):
        """Create a boss asteroid"""
        # Position boss asteroid far ahead of the player
        player_angle_rad = self.player_rotation * math.pi / 180.0
        distance = 35  # Further than regular asteroids
        
        # Directly in front of player
        pos_x = self.player_pos[0] + math.sin(player_angle_rad) * distance
        pos_z = self.player_pos[2] + math.cos(player_angle_rad) * distance
        
        self.boss_asteroid = {
            "pos": [pos_x, 0, pos_z],
            "rotation": [random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)],
            "rot_speed": [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)],
            "size": 3.0,
            "speed": 0.02,
            "hit_points": 5 + self.wave,  # Boss gets stronger each wave
            "color": list(self.colors["boss"]),
            "shape": "boss",
            "warning_distance": 10.0  # Distance to trigger warning
        }

    def spawn_powerup(self):
        """Randomly spawn a power-up"""
        if random.random() < self.powerup_spawn_chance:
            # Spawn power-ups in front of the player (in the field of view)
            player_angle_rad = self.player_rotation * math.pi / 180.0
            
            # Create a spawn area slightly spread out in front of player
            spawn_angle = player_angle_rad + random.uniform(-math.pi/4, math.pi/4)  # +/- 45 degrees
            distance = random.uniform(15, 25)
            
            pos_x = self.player_pos[0] + math.sin(spawn_angle) * distance
            pos_z = self.player_pos[2] + math.cos(spawn_angle) * distance
            
            # Randomize power-up type
            powerup_type = random.choice(["health", "speed", "shield"])
            
            # Set color based on type
            if powerup_type == "health":
                color = self.colors["health_powerup"]
            elif powerup_type == "speed":
                color = self.colors["speed_powerup"]
            else:  # shield
                color = self.colors["shield_powerup"]
            
            powerup = {
                "pos": [pos_x, 0, pos_z],
                "rotation": 0,
                "type": powerup_type,
                "size": 0.5,
                "speed": 0.03,
                "color": color
            }
            
            self.powerups.append(powerup)

    def shoot_bullet(self):
        """Fire a bullet from the player's ship"""
        # Calculate bullet starting position (front of ship)
        angle_rad = self.player_rotation * math.pi / 180.0
        front_x = self.player_pos[0] + math.sin(angle_rad) * self.player_size
        front_z = self.player_pos[2] + math.cos(angle_rad) * self.player_size
        
        # Create new bullet
        bullet = {
            "pos": [front_x, self.player_pos[1], front_z],
            "direction": angle_rad,
            "speed": self.bullet_speed * (2.0 if self.bullet_boost_active else 1.0),
            "distance": 0,  # Distance traveled
            "max_distance": 50,  # Max travel distance before considered "missed"
            "size": 0.15,
            "color": list(self.colors["bullet"])
        }
        
        self.bullets.append(bullet)

    def activate_cheat_mode(self):
        """Activate the cheat mode (clear screen)"""
        if self.cheat_mode_cooldown <= 0:
            self.cheat_mode_active = True
            self.cheat_mode_cooldown = 1000  # Cooldown time (in frames)
            
            # Fire bullets in all directions
            for angle in range(0, 360, 15):  # 24 bullets in a circle
                # Calculate bullet starting position
                angle_rad = angle * math.pi / 180.0
                front_x = self.player_pos[0] + math.sin(angle_rad) * self.player_size
                front_z = self.player_pos[2] + math.cos(angle_rad) * self.player_size
                
                # Create new bullet
                bullet = {
                    "pos": [front_x, self.player_pos[1], front_z],
                    "direction": angle_rad,
                    "speed": self.bullet_speed * 1.5,  # Faster cheat bullets
                    "distance": 0,
                    "max_distance": 50,
                    "size": 0.2,  # Bigger cheat bullets
                    "color": [1.0, 0.3, 0.3]  # Red cheat bullets
                }
                
                self.bullets.append(bullet)

    def add_explosion(self, pos, size, color):
        """Add explosion effect at the given position"""
        explosion = {
            "pos": list(pos),
            "size": size,
            "max_size": size * 2.5,
            "growth_rate": 0.1,
            "alpha": 1.0,
            "fade_rate": 0.05,
            "color": color
        }
        
        self.explosions.append(explosion)

    def update(self):
        """Update game state for one frame"""
        if self.game_over or self.paused:
            return
            
        # Update player
        self.update_player()
        
        # Update bullets
        self.update_bullets()
        
        # Update asteroids
        self.update_asteroids()
        
        # Update boss if active
        if self.boss_active and self.boss_asteroid:
            self.update_boss()
            
        # Update power-ups
        self.update_powerups()
        
        # Update explosions
        self.update_explosions()
            
        # Check for power-up spawning
        self.spawn_powerup()
        
        # Update timers
        self.update_timers()
        
        # Check game over condition
        if self.player_health <= 0 or self.bullets_missed >= self.max_missed_bullets:
            self.game_over = True

    def update_player(self):
        """Update player state"""
        # Player ship rotation effects
        if self.player_shield_active:
            # Pulse shield color
            t = time.time() * 5.0
            pulse = (math.sin(t) + 1.0) / 2.0
            self.player_color = [
                0.2 + pulse * 0.2,
                0.6 + pulse * 0.2,
                0.8 + pulse * 0.2
            ]

    def update_bullets(self):
        """Update all bullets"""
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            # Move bullet forward
            bullet["pos"][0] += math.sin(bullet["direction"]) * bullet["speed"]
            bullet["pos"][2] += math.cos(bullet["direction"]) * bullet["speed"]
            
            # Update distance traveled
            dist_moved = bullet["speed"]
            bullet["distance"] += dist_moved
            
            # Check if bullet has traveled too far (missed)
            if bullet["distance"] >= bullet["max_distance"]:
                bullets_to_remove.append(i)
                self.bullets_missed += 1
                continue
                
            # Check collision with asteroids
            hit = self.check_bullet_collisions(bullet)
            if hit:
                bullets_to_remove.append(i)
        
        # Remove bullets (from highest index to lowest to avoid shifting issues)
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)

    def update_asteroids(self):
        """Update all asteroids"""
        asteroids_to_remove = []
        
        for i, asteroid in enumerate(self.asteroids):
            # Calculate direction toward player
            dx = self.player_pos[0] - asteroid["pos"][0]
            dz = self.player_pos[2] - asteroid["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            # Move asteroid toward player
            if dist > 0:
                asteroid["pos"][0] += (dx / dist) * asteroid["speed"]
                asteroid["pos"][2] += (dz / dist) * asteroid["speed"]
            
            # Rotate asteroid
            for j in range(3):
                asteroid["rotation"][j] = (asteroid["rotation"][j] + asteroid["rot_speed"][j]) % 360
                
            # Check collision with player
            if self.check_player_asteroid_collision(asteroid):
                if not self.player_shield_active:  # Shield blocks asteroid damage
                    self.player_health -= 1
                    self.add_explosion(self.player_pos, self.player_size * 1.5, self.colors["explosion"])
                
                asteroids_to_remove.append(i)
        
        # Remove destroyed asteroids (from highest index to lowest)
        for i in sorted(asteroids_to_remove, reverse=True):
            if i < len(self.asteroids):
                self.asteroids.pop(i)
                
        # If all asteroids destroyed and no boss, spawn new wave
        if len(self.asteroids) == 0 and not self.boss_active:
            self.wave += 1
            self.spawn_asteroid_wave()

    def update_boss(self):
        """Update boss asteroid state"""
        boss = self.boss_asteroid
        
        if boss:
            # Calculate direction toward player
            dx = self.player_pos[0] - boss["pos"][0]
            dz = self.player_pos[2] - boss["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            # Move boss toward player
            if dist > 0:
                boss["pos"][0] += (dx / dist) * boss["speed"]
                boss["pos"][2] += (dz / dist) * boss["speed"]
            
            # Rotate boss
            for j in range(3):
                boss["rotation"][j] = (boss["rotation"][j] + boss["rot_speed"][j]) % 360
            
            # Check if boss is close to player (warning)
            if dist < boss["warning_distance"] and not self.boss_warning:
                self.boss_warning = True
                self.warning_flash_timer = 100  # Flash duration
            elif dist >= boss["warning_distance"]:
                self.boss_warning = False
                
            # Check collision with player
            if self.check_player_asteroid_collision(boss):
                if not self.player_shield_active:  # Shield blocks boss damage
                    self.player_health -= 2  # Boss does double damage
                    self.add_explosion(self.player_pos, self.player_size * 2.0, self.colors["explosion"])
                
                # Update boss hit points but don't destroy on collision
                boss["hit_points"] -= 1
                if boss["hit_points"] <= 0:
                    self.boss_defeated()

    def update_powerups(self):
        """Update all power-ups"""
        powerups_to_remove = []
        
        for i, powerup in enumerate(self.powerups):
            # Calculate direction toward player
            dx = self.player_pos[0] - powerup["pos"][0]
            dz = self.player_pos[2] - powerup["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            # Move power-up toward player
            if dist > 0:
                powerup["pos"][0] += (dx / dist) * powerup["speed"]
                powerup["pos"][2] += (dz / dist) * powerup["speed"]
            
            # Rotate power-up for visual effect
            powerup["rotation"] = (powerup["rotation"] + 2) % 360
                
            # Check collision with player
            if self.check_player_powerup_collision(powerup):
                self.apply_powerup(powerup)
                powerups_to_remove.append(i)
        
        # Remove collected power-ups
        for i in sorted(powerups_to_remove, reverse=True):
            if i < len(self.powerups):
                self.powerups.pop(i)

    def update_explosions(self):
        """Update explosion effects"""
        explosions_to_remove = []
        
        for i, explosion in enumerate(self.explosions):
            # Grow explosion
            explosion["size"] += explosion["growth_rate"]
            
            # Fade explosion
            explosion["alpha"] -= explosion["fade_rate"]
            
            # Remove explosion if completely faded
            if explosion["alpha"] <= 0 or explosion["size"] >= explosion["max_size"]:
                explosions_to_remove.append(i)
        
        # Remove finished explosions
        for i in sorted(explosions_to_remove, reverse=True):
            if i < len(self.explosions):
                self.explosions.pop(i)

    def update_timers(self):
        """Update all game timers"""
        # Cheat mode cooldown
        if self.cheat_mode_cooldown > 0:
            self.cheat_mode_cooldown -= 1
            
        # Bullet boost timer
        if self.bullet_boost_timer > 0:
            self.bullet_boost_timer -= 1
            if self.bullet_boost_timer <= 0:
                self.bullet_boost_active = False
                
        # Shield timer
        if self.player_shield_timer > 0:
            self.player_shield_timer -= 1
            if self.player_shield_timer <= 0:
                self.player_shield_active = False
                self.player_color = self.colors["player"]  # Reset color
                
        # Warning flash timer
        if self.warning_flash_timer > 0:
            self.warning_flash_timer -= 1

    def check_bullet_collisions(self, bullet):
        """Check if a bullet collides with any asteroid and handle effects"""
        # First check against boss if active
        if self.boss_active and self.boss_asteroid:
            boss = self.boss_asteroid
            # Distance check from bullet to boss center
            dx = bullet["pos"][0] - boss["pos"][0]
            dz = bullet["pos"][2] - boss["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist < (boss["size"] / 1.5 + bullet["size"]):
                # Boss hit!
                boss["hit_points"] -= 1
                self.add_explosion(bullet["pos"], 0.5, self.colors["explosion"])
                self.score += 5  # More points for hitting boss
                
                # Check if boss is defeated
                if boss["hit_points"] <= 0:
                    self.boss_defeated()
                    
                return True
        
        # Then check against regular asteroids
        for i, asteroid in enumerate(self.asteroids):
            # Distance check from bullet to asteroid center
            dx = bullet["pos"][0] - asteroid["pos"][0]
            dz = bullet["pos"][2] - asteroid["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist < (asteroid["size"] / 1.5 + bullet["size"]):
                # Asteroid hit!
                asteroid["hit_points"] -= 1
                
                if asteroid["hit_points"] <= 0:
                    # Destroy asteroid
                    self.add_explosion(asteroid["pos"], asteroid["size"], self.colors["explosion"])
                    
                    # Add score
                    if asteroid["type"] == "normal":
                        self.score += 10
                    elif asteroid["type"] == "fast":
                        self.score += 15
                    elif asteroid["type"] == "large":
                        self.score += 20
                        
                    # Fragment large asteroids
                    if asteroid["type"] == "large":
                        # Spawn 2-3 smaller asteroids
                        for _ in range(random.randint(2, 3)):
                            # Random offset from original asteroid
                            offset_x = random.uniform(-1, 1)
                            offset_z = random.uniform(-1, 1)
                            
                            # Spawn fragment asteroid
                            new_pos = [
                                asteroid["pos"][0] + offset_x,
                                asteroid["pos"][1],
                                asteroid["pos"][2] + offset_z
                            ]
                            
                            # Randomly choose between normal and fast for fragments
                            fragment_type = random.choice(["normal", "fast"])
                            self.spawn_asteroid(new_pos[0], new_pos[1], new_pos[2], fragment_type)
                    
                    # Remove the asteroid
                    self.asteroids.pop(i)
                else:
                    # Only damaged, show small explosion
                    self.add_explosion(bullet["pos"], 0.3, self.colors["explosion"])
                
                return True
        
        return False

    def check_player_asteroid_collision(self, asteroid):
        """Check if the player collides with an asteroid"""
        # Distance check from player to asteroid center
        dx = self.player_pos[0] - asteroid["pos"][0]
        dz = self.player_pos[2] - asteroid["pos"][2]
        dist = math.sqrt(dx*dx + dz*dz)
        
        # Collision threshold based on sizes
        collision_threshold = self.player_size + asteroid["size"] * 0.7
        
        return dist < collision_threshold

    def check_player_powerup_collision(self, powerup):
        """Check if the player collides with a power-up"""
        # Distance check from player to power-up center
        dx = self.player_pos[0] - powerup["pos"][0]
        dz = self.player_pos[2] - powerup["pos"][2]
        dist = math.sqrt(dx*dx + dz*dz)
        
        # Collision threshold based on sizes
        collision_threshold = self.player_size + powerup["size"]
        
        return dist < collision_threshold

    def apply_powerup(self, powerup):
        """Apply power-up effect to the player"""
        powerup_type = powerup["type"]
        
        if powerup_type == "health":
            # Restore 1 health point
            if self.player_health < 5:  # Cap health at 5
                self.player_health += 1
                
        elif powerup_type == "speed":
            # Activate bullet speed boost
            self.bullet_boost_active = True
            self.bullet_boost_timer = 500  # Duration in frames
            
        elif powerup_type == "shield":
            # Activate player shield
            self.player_shield_active = True
            self.player_shield_timer = 500  # Duration in frames

    def boss_defeated(self):
        """Handle boss asteroid defeat"""
        if self.boss_asteroid:
            # Big explosion
            self.add_explosion(
                self.boss_asteroid["pos"], 
                self.boss_asteroid["size"] * 2, 
                self.colors["explosion"]
            )
            
            # Bonus score
            self.score += 100 + (self.wave * 10)
            
            # Clear boss
            self.boss_asteroid = None
            self.boss_active = False
            self.boss_warning = False
            
            # Next wave
            self.wave += 1
            self.spawn_asteroid_wave()

    def reset_game(self):
        """Reset the game to starting state"""
        self.__init__()  # Reinitialize all game state


# OpenGL rendering functions
class GameRenderer:
    def __init__(self, game_state):
        self.game_state = game_state
        self.quadric = gluNewQuadric()
        
    def render_scene(self):
        """Render the entire game scene"""
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up camera
        self.setup_camera()
        
        # Draw stars (background)
        self.render_stars()
        
        # Draw game objects
        self.render_player()
        self.render_bullets()
        self.render_asteroids()
        if self.game_state.boss_active and self.game_state.boss_asteroid:
            self.render_boss()
        self.render_powerups()
        self.render_explosions()
        
        # Draw HUD
        self.render_hud()
        
        # Game over screen
        if self.game_state.game_over:
            self.render_game_over()
            
        # Paused screen
        if self.game_state.paused:
            self.render_paused_screen()
        
        # Swap buffers
        glutSwapBuffers()

    def setup_camera(self):
        """Set up the camera based on current game state"""
        # Set projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, window_width / window_height, 0.1, 100.0)
        
        # Set camera position based on mode
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        if self.game_state.camera_mode == "first_person":
            # First-person view (from ship cockpit)
            angle_rad = self.game_state.player_rotation * math.pi / 180.0
            
            # Calculate eye position (at cockpit)
            eye_x = self.game_state.player_pos[0]
            eye_y = self.game_state.player_pos[1] + 0.3  # Slightly above ship center
            eye_z = self.game_state.player_pos[2]
            
            # Calculate look-at position (in front of ship)
            look_x = eye_x + math.sin(angle_rad) * 10
            look_y = eye_y + math.tan(self.game_state.camera_tilt * math.pi / 180.0)
            look_z = eye_z + math.cos(angle_rad) * 10
            
            gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 1, 0)
            
        else:  # Third-person view
            # Calculate camera angle (player rotation + camera rotation)
            total_angle_rad = (self.game_state.player_rotation + self.game_state.camera_rotation) * math.pi / 180.0
            tilt_rad = self.game_state.camera_tilt * math.pi / 180.0
            
            # Camera distance from player
            distance = 5.0
            
            # Calculate camera position
            cam_x = self.game_state.player_pos[0] - math.sin(total_angle_rad) * distance
            cam_y = self.game_state.player_pos[1] + math.sin(tilt_rad) * distance
            cam_z = self.game_state.player_pos[2] - math.cos(total_angle_rad) * distance
            
            # Look at player
            gluLookAt(cam_x, cam_y, cam_z, 
                      self.game_state.player_pos[0], self.game_state.player_pos[1], self.game_state.player_pos[2], 
                      0, 1, 0)

    def render_stars(self):
        """Render starfield background"""
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glPointSize(2.0)
        glBegin(GL_POINTS)
        
        for star in self.game_state.stars:
            # Set star color based on brightness
            glColor3f(star[3] * self.game_state.colors["stars"][0],
                      star[3] * self.game_state.colors["stars"][1],
                      star[3] * self.game_state.colors["stars"][2])
            
            glVertex3f(star[0], star[1], star[2])
            
        glEnd()
        
        # Restore OpenGL state
        glEnable(GL_DEPTH_TEST)
        glPointSize(1.0)

    def render_player(self):
        """Render the player's ship"""
        # Save matrix state
        glPushMatrix()
        
        # Position and rotate ship
        glTranslatef(self.game_state.player_pos[0],
                     self.game_state.player_pos[1],
                     self.game_state.player_pos[2])
        
        glRotatef(self.game_state.player_rotation, 0, 1, 0)  # Rotate around Y axis
        
        # If in cheat mode, add additional rotation
        if self.game_state.cheat_mode_active:
            rotation_speed = 10.0  # Degrees per frame
            current_time = time.time()
            glRotatef(current_time * 180, 0, 1, 0)  # Spin during cheat mode
        
        # Draw shield effect if active
        if self.game_state.player_shield_active:
            # Pulsing shield sphere
            shield_scale = 1.1 + math.sin(time.time() * 5.0) * 0.1
            shield_color = self.game_state.colors["shield_powerup"]
            
            glColor4f(shield_color[0], shield_color[1], shield_color[2], 0.4)
            glPushMatrix()
            glScalef(shield_scale, shield_scale, shield_scale)
            gluSphere(self.quadric, self.game_state.player_size * 1.2, 16, 16)
            glPopMatrix()
        
        # Main ship body (cube)
        glColor3f(self.game_state.player_color[0],
                  self.game_state.player_color[1],
                  self.game_state.player_color[2])
        
        # Body
        glPushMatrix()
        glScalef(1.0, 0.4, 2.0)  # Flattened, elongated cube
        glutSolidCube(self.game_state.player_size)
        glPopMatrix()
        
        # Cockpit (sphere)
        glPushMatrix()
        glTranslatef(0, self.game_state.player_size * 0.2, self.game_state.player_size * 0.3)
        glColor3f(0.2, 0.8, 1.0)  # Light blue
        gluSphere(self.quadric, self.game_state.player_size * 0.25, 12, 12)
        glPopMatrix()
        
        # Wings (cubes)
        glPushMatrix()
        glTranslatef(self.game_state.player_size * 0.8, 0, 0)
        glScalef(0.2, 0.1, 1.0)
        glColor3f(0.5, 0.7, 0.9)  # Lighter blue
        glutSolidCube(self.game_state.player_size)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-self.game_state.player_size * 0.8, 0, 0)
        glScalef(0.2, 0.1, 1.0)
        glColor3f(0.5, 0.7, 0.9)  # Lighter blue
        glutSolidCube(self.game_state.player_size)
        glPopMatrix()
        
        # Engines (cylinders)
        glPushMatrix()
        glTranslatef(self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.3, 0.1)  # Engine color
        gluCylinder(self.quadric, self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.3, 8, 3)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.3, 0.1)  # Engine color
        gluCylinder(self.quadric, self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.3, 8, 3)
        glPopMatrix()
        
        # Engine glow (animated)
        engine_glow = (math.sin(time.time() * 10) + 1.0) * 0.5  # Pulsating value 0-1
        glPushMatrix()
        glTranslatef(self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8 - 0.05)
        glRotatef(90, 1, 0, 0)
        glColor3f(1.0, 0.5 + engine_glow * 0.5, 0.0)  # Orange-yellow glow
        gluDisk(self.quadric, 0, self.game_state.player_size * 0.13, 8, 1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8 - 0.05)
        glRotatef(90, 1, 0, 0)
        glColor3f(1.0, 0.5 + engine_glow * 0.5, 0.0)  # Orange-yellow glow
        gluDisk(self.quadric, 0, self.game_state.player_size * 0.13, 8, 1)
        glPopMatrix()
        
        # Restore matrix state
        glPopMatrix()

    def render_bullets(self):
        """Render all bullets"""
        for bullet in self.game_state.bullets:
            glPushMatrix()
            
            # Position bullet
            glTranslatef(bullet["pos"][0], bullet["pos"][1], bullet["pos"][2])
            
            # Rotate to face direction of travel
            glRotatef(bullet["direction"] * 180.0 / math.pi, 0, 1, 0)
            glRotatef(90, 0, 0, 1)  # Align cylinder along travel direction
            
            # Set bullet color
            glColor3f(bullet["color"][0], bullet["color"][1], bullet["color"][2])
            
            # Draw bullet (cylinder)
            gluCylinder(self.quadric, bullet["size"] * 0.2, bullet["size"] * 0.2, 
                        bullet["size"] * 3.0, 8, 1)
                        
            # Bullet glow (sphere at front)
            glPushMatrix()
            glTranslatef(0, 0, bullet["size"] * 3.0)
            glColor3f(1.0, 1.0, 0.5)  # Bright yellow tip
            gluSphere(self.quadric, bullet["size"] * 0.3, 8, 8)
            glPopMatrix()
            
            # Bullet trail (cone)
            glPushMatrix()
            glRotatef(180, 0, 1, 0)
            glColor4f(1.0, 0.6, 0.2, 0.6)  # Orange with transparency
            gluCylinder(self.quadric, 0, bullet["size"] * 0.4, 
                        bullet["size"] * 2.0, 8, 1)
            glPopMatrix()
            
            glPopMatrix()

    def render_asteroids(self):
        """Render all asteroids"""
        for asteroid in self.game_state.asteroids:
            glPushMatrix()
            
            # Position asteroid
            glTranslatef(asteroid["pos"][0], asteroid["pos"][1], asteroid["pos"][2])
            
            # Rotate asteroid
            glRotatef(asteroid["rotation"][0], 1, 0, 0)
            glRotatef(asteroid["rotation"][1], 0, 1, 0)
            glRotatef(asteroid["rotation"][2], 0, 0, 1)
            
            # Set asteroid color
            glColor3f(asteroid["color"][0], asteroid["color"][1], asteroid["color"][2])
            
            # Draw asteroid based on its shape
            if asteroid["shape"] == "cube":
                # Rocky asteroid (cube with distortion)
                glutSolidCube(asteroid["size"])
                
                # Add rocky details (small cubes)
                for i in range(4):
                    glPushMatrix()
                    # Random position on surface
                    angle = i * 90.0
                    x_offset = math.sin(angle * math.pi / 180.0) * asteroid["size"] * 0.5
                    z_offset = math.cos(angle * math.pi / 180.0) * asteroid["size"] * 0.5
                    
                    glTranslatef(x_offset, asteroid["size"] * 0.4, z_offset)
                    glColor3f(asteroid["color"][0] * 0.8, 
                              asteroid["color"][1] * 0.8, 
                              asteroid["color"][2] * 0.8)  # Darker color for details
                    
                    # Small detail cube
                    glScalef(0.3, 0.3, 0.3)
                    glutSolidCube(asteroid["size"] * 0.5)
                    glPopMatrix()
                
            else:  # sphere
                # Smooth asteroid (sphere)
                gluSphere(self.quadric, asteroid["size"], 12, 12)
                
                # Add crater details (small spheres)
                for i in range(3):
                    glPushMatrix()
                    # Random position on surface
                    angle1 = i * 120.0
                    angle2 = i * 60.0
                    x_offset = math.sin(angle1 * math.pi / 180.0) * asteroid["size"] * 0.7
                    y_offset = math.sin(angle2 * math.pi / 180.0) * asteroid["size"] * 0.7
                    z_offset = math.cos(angle1 * math.pi / 180.0) * asteroid["size"] * 0.7
                    
                    glTranslatef(x_offset, y_offset, z_offset)
                    glColor3f(asteroid["color"][0] * 0.7, 
                              asteroid["color"][1] * 0.7, 
                              asteroid["color"][2] * 0.7)  # Darker color for craters
                    
                    # Small crater sphere
                    gluSphere(self.quadric, asteroid["size"] * 0.2, 8, 8)
                    glPopMatrix()
            
            glPopMatrix()

    def render_boss(self):
        """Render the boss asteroid"""
        boss = self.game_state.boss_asteroid
        
        if boss:
            glPushMatrix()
            
            # Position boss
            glTranslatef(boss["pos"][0], boss["pos"][1], boss["pos"][2])
            
            # Rotate boss
            glRotatef(boss["rotation"][0], 1, 0, 0)
            glRotatef(boss["rotation"][1], 0, 1, 0)
            glRotatef(boss["rotation"][2], 0, 0, 1)
            
            # Boss color with pulsing effect if warning is active
            if self.game_state.boss_warning and (self.game_state.warning_flash_timer % 20 < 10):
                # Flashing warning color
                glColor3f(1.0, 0.2, 0.2)  # Bright red
            else:
                # Normal boss color
                glColor3f(boss["color"][0], boss["color"][1], boss["color"][2])
            
            # Core (large sphere)
            gluSphere(self.quadric, boss["size"] * 0.8, 16, 16)
            
            # Outer shell (cube corners)
            offset = boss["size"] * 0.6
            
            # Eight cubic corners
            for x in [-1, 1]:
                for y in [-1, 1]:
                    for z in [-1, 1]:
                        glPushMatrix()
                        glTranslatef(x * offset, y * offset, z * offset)
                        glColor3f(boss["color"][0] * 0.8, 
                                  boss["color"][1] * 0.8, 
                                  boss["color"][2] * 0.8)  # Darker color
                        glutSolidCube(boss["size"] * 0.5)
                        glPopMatrix()
            
            # Spikes (cylinders)
            for i in range(6):
                glPushMatrix()
                
                # Spike direction
                if i == 0:
                    # +X axis
                    glTranslatef(boss["size"] * 0.8, 0, 0)
                    glRotatef(90, 0, 1, 0)
                elif i == 1:
                    # -X axis
                    glTranslatef(-boss["size"] * 0.8, 0, 0)
                    glRotatef(-90, 0, 1, 0)
                elif i == 2:
                    # +Y axis
                    glTranslatef(0, boss["size"] * 0.8, 0)
                    glRotatef(-90, 1, 0, 0)
                elif i == 3:
                    # -Y axis
                    glTranslatef(0, -boss["size"] * 0.8, 0)
                    glRotatef(90, 1, 0, 0)
                elif i == 4:
                    # +Z axis
                    glTranslatef(0, 0, boss["size"] * 0.8)
                    # No rotation needed
                else:  # i == 5
                    # -Z axis
                    glTranslatef(0, 0, -boss["size"] * 0.8)
                    glRotatef(180, 0, 1, 0)
                
                # Draw spike
                glColor3f(1.0, 0.3, 0.0)  # Orange spikes
                gluCylinder(self.quadric, boss["size"] * 0.2, 0, boss["size"] * 0.6, 8, 1)
                
                glPopMatrix()
            
            # Energy core glow (inner sphere)
            health_percent = boss["hit_points"] / (5.0 + self.game_state.wave)  # Normalize health
            core_pulse = (math.sin(time.time() * 3.0) + 1.0) * 0.5  # Pulsing effect
            
            glPushMatrix()
            glColor3f(1.0, 0.3 + (1.0 - health_percent) * 0.7, 0.0)  # Changes from orange to red as health decreases
            gluSphere(self.quadric, boss["size"] * 0.4 * (0.8 + core_pulse * 0.2), 12, 12)
            glPopMatrix()
                
            glPopMatrix()

    def render_powerups(self):
        """Render all power-ups"""
        for powerup in self.game_state.powerups:
            glPushMatrix()
            
            # Position powerup
            glTranslatef(powerup["pos"][0], powerup["pos"][1], powerup["pos"][2])
            
            # Rotate powerup for visual effect
            glRotatef(powerup["rotation"], 0, 1, 0)
            glRotatef(time.time() * 30 % 360, 1, 1, 1)  # Additional rotation
            
            # Set powerup color
            glColor3f(powerup["color"][0], powerup["color"][1], powerup["color"][2])
            
            # Draw powerup based on type
            if powerup["type"] == "health":
                # Health powerup (cross)
                glutSolidCube(powerup["size"] * 0.8)
                
                # Add cross mark
                glPushMatrix()
                glScalef(0.2, 1.0, 0.2)
                glutSolidCube(powerup["size"] * 1.5)
                glPopMatrix()
                
                glPushMatrix()
                glScalef(1.0, 0.2, 0.2)
                glutSolidCube(powerup["size"] * 1.5)
                glPopMatrix()
                
            elif powerup["type"] == "speed":
                # Speed powerup (arrow)
                gluSphere(self.quadric, powerup["size"] * 0.5, 12, 12)
                
                # Add arrow shape
                glPushMatrix()
                glTranslatef(0, 0, powerup["size"] * 0.5)
                glRotatef(90, 1, 0, 0)
                gluCylinder(self.quadric, powerup["size"] * 0.2, 
                            powerup["size"] * 0.2, 
                            powerup["size"] * 0.8, 8, 2)
                            
                # Arrow head
                glTranslatef(0, 0, powerup["size"] * 0.8)
                gluCylinder(self.quadric, powerup["size"] * 0.4, 
                            0, 
                            powerup["size"] * 0.4, 8, 2)
                glPopMatrix()
                
            else:  # Shield powerup
                # Shield powerup (sphere)
                glutSolidCube(powerup["size"] * 0.6)
                
                # Add outer shell (transparent sphere)
                glColor4f(powerup["color"][0], powerup["color"][1], powerup["color"][2], 0.5)
                gluSphere(self.quadric, powerup["size"] * 0.8, 12, 12)
            
            # Add glow effect (pulsing)
            pulse = (math.sin(time.time() * 5.0) + 1.0) / 2.0
            glColor4f(powerup["color"][0], powerup["color"][1], powerup["color"][2], 0.3 * pulse)
            gluSphere(self.quadric, powerup["size"] * (1.0 + 0.2 * pulse), 12, 12)
            
            glPopMatrix()

    def render_explosions(self):
        """Render explosion effects"""
        for explosion in self.game_state.explosions:
            glPushMatrix()
            
            # Position explosion
            glTranslatef(explosion["pos"][0], explosion["pos"][1], explosion["pos"][2])
            
            # Set explosion color with alpha
            glColor4f(explosion["color"][0], explosion["color"][1], explosion["color"][2], explosion["alpha"])
            
            # Draw explosion (sphere)
            gluSphere(self.quadric, explosion["size"], 12, 12)
            
            # Add internal glow (brighter inner sphere)
            inner_size = explosion["size"] * 0.7
            glColor4f(1.0, 0.8, 0.2, explosion["alpha"] * 0.8)
            gluSphere(self.quadric, inner_size, 8, 8)
            
            glPopMatrix()

    def render_hud(self):
        """Render the HUD (Heads-Up Display)"""
        # Switch to orthographic projection for 2D HUD
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Set HUD color (with warning flash if needed)
        if self.game_state.boss_warning and (self.game_state.warning_flash_timer % 20 < 10):
            hud_color = self.game_state.colors["hud_warning"]
        else:
            hud_color = self.game_state.colors["hud"]
        
        # Draw HUD background
        self.draw_hud_background(10, window_height - 100, 250, 90, hud_color)
        
        # Set text color
        glColor3f(1.0, 1.0, 1.0)
        
        # Display score
        self.draw_text(20, window_height - 30, f"SCORE: {self.game_state.score}")
        
        # Display health
        self.draw_text(20, window_height - 50, f"HEALTH: {self.game_state.player_health}")
        
        # Display wave
        self.draw_text(20, window_height - 70, f"WAVE: {self.game_state.wave}")
        
        # Display bullets missed
        self.draw_text(20, window_height - 90, f"MISSED: {self.game_state.bullets_missed}/{self.game_state.max_missed_bullets}")
        
        # Display active power-ups
        if self.game_state.bullet_boost_active:
            self.draw_text(window_width - 200, window_height - 30, "SPEED BOOST ACTIVE")
            
        if self.game_state.player_shield_active:
            self.draw_text(window_width - 200, window_height - 50, "SHIELD ACTIVE")
            
        # Display cheat mode cooldown
        if self.game_state.cheat_mode_cooldown > 0:
            cooldown_percent = self.game_state.cheat_mode_cooldown / 1000.0
            self.draw_text(window_width - 200, window_height - 70, f"CHEAT: {int((1.0 - cooldown_percent) * 100)}%")
        else:
            self.draw_text(window_width - 200, window_height - 70, "CHEAT: READY (C)")
            
        # Camera mode indicator
        camera_text = "VIEW: " + ("FIRST PERSON" if self.game_state.camera_mode == "first_person" else "THIRD PERSON")
        self.draw_text(window_width - 200, window_height - 90, camera_text)
        
        # Boss health bar (if boss is active)
        if self.game_state.boss_active and self.game_state.boss_asteroid:
            boss = self.game_state.boss_asteroid
            max_health = 5 + self.game_state.wave
            health_percent = boss["hit_points"] / max_health
            
            # Boss health label
            self.draw_text(window_width / 2 - 100, window_height - 30, "BOSS HEALTH")
            
            # Health bar background
            glColor3f(0.2, 0.2, 0.2)
            glBegin(GL_QUADS)
            glVertex2f(window_width / 2 - 100, window_height - 50)
            glVertex2f(window_width / 2 + 100, window_height - 50)
            glVertex2f(window_width / 2 + 100, window_height - 40)
            glVertex2f(window_width / 2 - 100, window_height - 40)
            glEnd()
            
            # Health bar fill
            glColor3f(1.0 - health_percent, health_percent, 0.0)  # Green to red based on health
            glBegin(GL_QUADS)
            glVertex2f(window_width / 2 - 100, window_height - 50)
            glVertex2f(window_width / 2 - 100 + (200 * health_percent), window_height - 50)
            glVertex2f(window_width / 2 - 100 + (200 * health_percent), window_height - 40)
            glVertex2f(window_width / 2 - 100, window_height - 40)
            glEnd()
        
        # Add a directional indicator showing "FRONT" direction
        # This helps player understand which way asteroids are coming from
        front_indicator_x = window_width / 2
        front_indicator_y = 70
        
        # Draw "FRONT" text
        glColor3f(1.0, 1.0, 0.0)  # Bright yellow
        self.draw_text(front_indicator_x - 20, front_indicator_y - 30, "FRONT")
        
        # Draw arrow pointing to front
        glBegin(GL_TRIANGLES)
        glVertex2f(front_indicator_x, front_indicator_y)
        glVertex2f(front_indicator_x - 10, front_indicator_y - 20)
        glVertex2f(front_indicator_x + 10, front_indicator_y - 20)
        glEnd()
            
        # Controls reminder
        glColor3f(0.7, 0.7, 0.7)
        self.draw_text(10, 30, "W,A,S,D: Move   Left Click: Shoot   Right Click: Toggle View   C: Cheat   P: Pause   R: Restart")
        
        # Restore OpenGL state
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def render_game_over(self):
        """Render the game over screen"""
        # Switch to orthographic projection for 2D overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Semi-transparent background
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        
        # Game Over text
        glColor3f(1.0, 0.2, 0.2)
        self.draw_text_large(window_width / 2 - 100, window_height / 2 + 50, "GAME OVER")
        
        # Final stats
        glColor3f(1.0, 1.0, 1.0)
        self.draw_text(window_width / 2 - 120, window_height / 2, f"FINAL SCORE: {self.game_state.score}")
        self.draw_text(window_width / 2 - 120, window_height / 2 - 30, f"WAVES SURVIVED: {self.game_state.wave}")
        
        # Restart instruction
        glColor3f(0.2, 1.0, 0.2)
        self.draw_text(window_width / 2 - 120, window_height / 2 - 80, "PRESS 'R' TO RESTART")
        
        # Restore OpenGL state
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def render_paused_screen(self):
        """Render the pause screen"""
        # Switch to orthographic projection for 2D overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # Semi-transparent background
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        
        # Paused text
        glColor3f(0.2, 0.8, 1.0)
        self.draw_text_large(window_width / 2 - 80, window_height / 2 + 20, "PAUSED")
        
        # Continue instruction
        glColor3f(1.0, 1.0, 1.0)
        self.draw_text(window_width / 2 - 120, window_height / 2 - 30, "PRESS 'P' TO CONTINUE")
        
        # Restore OpenGL state
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_hud_background(self, x, y, width, height, color):
        """Draw a semi-transparent HUD background rectangle"""
        glColor4f(color[0], color[1], color[2], 0.5)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        # Border
        glColor4f(color[0], color[1], color[2], 0.8)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

    def draw_text(self, x, y, text):
        """Draw text using OpenGL's bitmap characters"""
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

    def draw_text_large(self, x, y, text):
        """Draw large text for titles"""
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))


# Input handling functions
def keyboard(key, x, y):
    """Handle keyboard input"""
    key = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()
    
    if key == 'p':
        # Toggle pause
        game_state.paused = not game_state.paused
        
    elif key == 'r':
        # Restart game
        game_state.reset_game()
        
    elif key == 'c':
        # Activate cheat mode
        if not game_state.paused and not game_state.game_over:
            game_state.activate_cheat_mode()
            
    # Update player movement keys
    elif key == 'w':
        # Move forward
        if not game_state.paused and not game_state.game_over:
            angle_rad = game_state.player_rotation * math.pi / 180.0
            game_state.player_pos[0] -= math.sin(angle_rad) * game_state.player_speed
            game_state.player_pos[2] -= math.cos(angle_rad) * game_state.player_speed
            
    elif key == 'a':
        # Rotate left
        if not game_state.paused and not game_state.game_over:
            game_state.player_rotation = (game_state.player_rotation - 5.0) % 360
            
    elif key == 'd':
        # Rotate right
        if not game_state.paused and not game_state.game_over:
            game_state.player_rotation = (game_state.player_rotation + 5.0) % 360
    
    glutPostRedisplay()

def keyboard_up(key, x, y):
    """Handle key release events"""
    # Function for future expansion (e.g., smooth movement)
    pass

def special_keys(key, x, y):
    """Handle special keys (arrow keys)"""
    if not game_state.paused and not game_state.game_over:
        if key == GLUT_KEY_UP:
            # Tilt camera up
            game_state.camera_tilt = min(45.0, game_state.camera_tilt + 2.0)
            
        elif key == GLUT_KEY_DOWN:
            # Tilt camera down
            game_state.camera_tilt = max(-20.0, game_state.camera_tilt - 2.0)
            
        elif key == GLUT_KEY_LEFT:
            # Rotate camera left
            game_state.camera_rotation = (game_state.camera_rotation - 5.0) % 360
            
        elif key == GLUT_KEY_RIGHT:
            # Rotate camera right
            game_state.camera_rotation = (game_state.camera_rotation + 5.0) % 360
    
    glutPostRedisplay()

def mouse(button, state, x, y):
    """Handle mouse button events"""
    if not game_state.paused and not game_state.game_over:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # Fire bullet
            game_state.shoot_bullet()
            
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            # Toggle camera mode
            if game_state.camera_mode == "third_person":
                game_state.camera_mode = "first_person"
            else:
                game_state.camera_mode = "third_person"
    
    glutPostRedisplay()

def mouse_motion(x, y):
    """Handle mouse motion"""
    # For future expansion (e.g., aiming)
    pass

def reshape(width, height):
    """Handle window resizing"""
    global window_width, window_height
    
    # Update window dimensions
    window_width = width
    window_height = height
    
    # Update viewport
    glViewport(0, 0, width, height)
    
    # Update projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, width / height, 0.1, 100.0)
    
    # Reset modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def update_frame(value):
    """Timer callback to update and redraw the game"""
    # Update game state
    game_state.update()
    
    # Redraw the scene
    glutPostRedisplay()
    
    # Reset timer
    glutTimerFunc(16, update_frame, 0)  # ~60 FPS


# Main initialization
def init_opengl():
    """Initialize OpenGL settings"""
    # Set background color (deep space blue)
    glClearColor(0.02, 0.05, 0.1, 1.0)
    
    # Enable features
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Lighting (basic)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set up light
    light_position = [10.0, 10.0, 10.0, 0.0]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    glEnable(GL_LIGHT0)


def main():
    """Main program"""
    global window_width, window_height, game_state, game_renderer
    
    # Initialize window size
    window_width = 800
    window_height = 600
    
    # Initialize game state
    game_state = GameState()
    
    # Initialize GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Space Survival 3D")
    
    # Initialize OpenGL
    init_opengl()
    
    # Initialize game renderer
    game_renderer = GameRenderer(game_state)
    
    # Set callback functions
    glutDisplayFunc(game_renderer.render_scene)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutPassiveMotionFunc(mouse_motion)
    
    # Start update timer
    glutTimerFunc(16, update_frame, 0)  # ~60 FPS
    
    # Start main loop
    glutMainLoop()


if __name__ == "__main__":
    main()