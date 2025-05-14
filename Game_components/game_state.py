import math
import random
import time

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
        self.camera_mode = "third_person"  
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
        self.spawn_direction = "front_only" 
        
        # Power-ups
        self.powerups = []
        self.powerup_spawn_chance = 0.01  
        
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
        for i in range(200):
            self.stars.append([
                random.uniform(-50, 50),  
                random.uniform(-50, 50),  
                random.uniform(-50, 50),  
                random.uniform(0.5, 1.0) 
            ])

        self.spawn_asteroid_wave()

    def spawn_asteroid_wave(self):
        self.asteroids = []
        
        if self.wave % self.boss_wave_interval == 0:
            self.boss_active = True
            self.spawn_boss_asteroid()
        else:
            self.boss_active = False

            asteroid_count = 5 + self.wave * 2 
            
            for i in range(asteroid_count):

                player_angle_rad = self.player_rotation * math.pi / 180.0
                front_direction_x = math.sin(player_angle_rad)
                front_direction_z = math.cos(player_angle_rad)

                spawn_angle = player_angle_rad + random.uniform(-math.pi/3, math.pi/3)  
                distance = random.uniform(20, 30)  
                
                pos_x = self.player_pos[0] + math.sin(spawn_angle) * distance
                pos_z = self.player_pos[2] + math.cos(spawn_angle) * distance
             
                asteroid_type = random.choice(["normal", "fast", "large"])
                if self.wave < 2:  
                    asteroid_type = "normal"
                elif self.wave < 4:  
                    asteroid_type = random.choice(["normal", "fast"])
       
                self.spawn_asteroid(pos_x, 0, pos_z, asteroid_type)

    def spawn_asteroid(self, x, y, z, asteroid_type="normal"):
        speed_multiplier = 1.0 + (self.wave * 0.1) 
        
        asteroid = {
            "pos": [x, y, z],
            "rotation": [random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)],
            "rot_speed": [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)],
            "type": asteroid_type,
            "color": list(self.colors["asteroid"]),
            "hit_points": 1
        }
        
        # Asteroid properties
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
        player_angle_rad = self.player_rotation * math.pi / 180.0
        distance = 35 
  
        pos_x = self.player_pos[0] + math.sin(player_angle_rad) * distance
        pos_z = self.player_pos[2] + math.cos(player_angle_rad) * distance
        
        self.boss_asteroid = {
            "pos": [pos_x, 0, pos_z],
            "rotation": [random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)],
            "rot_speed": [random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)],
            "size": 3.0,
            "speed": 0.02,
            "hit_points": 5 + self.wave,  
            "color": list(self.colors["boss"]),
            "shape": "boss",
            "warning_distance": 10.0  
        }

    def spawn_powerup(self):
        if random.random() < self.powerup_spawn_chance:
            player_angle_rad = self.player_rotation * math.pi / 180.0
            
            spawn_angle = player_angle_rad + random.uniform(-math.pi/4, math.pi/4) 
            distance = random.uniform(15, 25)
            
            pos_x = self.player_pos[0] + math.sin(spawn_angle) * distance
            pos_z = self.player_pos[2] + math.cos(spawn_angle) * distance
       
            powerup_type = random.choice(["health", "speed", "shield"])
           
            if powerup_type == "health":
                color = self.colors["health_powerup"]
            elif powerup_type == "speed":
                color = self.colors["speed_powerup"]
            else:  
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
        angle_rad = self.player_rotation * math.pi / 180.0
        front_x = self.player_pos[0] + math.sin(angle_rad) * self.player_size
        front_z = self.player_pos[2] + math.cos(angle_rad) * self.player_size
     
        bullet = {
            "pos": [front_x, self.player_pos[1], front_z],
            "direction": angle_rad,
            "speed": self.bullet_speed * (2.0 if self.bullet_boost_active else 1.0),
            "distance": 0, 
            "max_distance": 50,  
            "size": 0.15,
            "color": list(self.colors["bullet"])
        }
        
        self.bullets.append(bullet)

    def activate_cheat_mode(self):
        if self.cheat_mode_cooldown <= 0:
            self.cheat_mode_active = True
            self.cheat_mode_cooldown = 1000 
            
            for angle in range(0, 360, 15): 
                # Calculate bullet starting position
                angle_rad = angle * math.pi / 180.0
                front_x = self.player_pos[0] + math.sin(angle_rad) * self.player_size
                front_z = self.player_pos[2] + math.cos(angle_rad) * self.player_size
                
                bullet = {
                    "pos": [front_x, self.player_pos[1], front_z],
                    "direction": angle_rad,
                    "speed": self.bullet_speed * 1.5, 
                    "distance": 0,
                    "max_distance": 50,
                    "size": 0.2,  
                    "color": [1.0, 0.3, 0.3] 
                }
                
                self.bullets.append(bullet)

    def add_explosion(self, pos, size, color):
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
        if self.game_over or self.paused:
            return
 
        self.update_player()
 
        self.update_bullets()
 
        self.update_asteroids()
 
        if self.boss_active and self.boss_asteroid:
            self.update_boss()
            
        self.update_powerups()

        self.update_explosions()

        self.spawn_powerup()

        self.update_timers()

        if self.player_health <= 0 or self.bullets_missed >= self.max_missed_bullets:
            self.game_over = True

    def update_player(self):
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
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            bullet["pos"][0] += math.sin(bullet["direction"]) * bullet["speed"]
            bullet["pos"][2] += math.cos(bullet["direction"]) * bullet["speed"]

            dist_moved = bullet["speed"]
            bullet["distance"] += dist_moved

            if bullet["distance"] >= bullet["max_distance"]:
                bullets_to_remove.append(i)
                self.bullets_missed += 1
                continue
          
            hit = self.check_bullet_collisions(bullet)
            if hit:
                bullets_to_remove.append(i)

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)

    def update_asteroids(self):
        asteroids_to_remove = []
        
        for i, asteroid in enumerate(self.asteroids):
            dx = self.player_pos[0] - asteroid["pos"][0]
            dz = self.player_pos[2] - asteroid["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)

            if dist > 0:
                asteroid["pos"][0] += (dx / dist) * asteroid["speed"]
                asteroid["pos"][2] += (dz / dist) * asteroid["speed"]

            for j in range(3):
                asteroid["rotation"][j] = (asteroid["rotation"][j] + asteroid["rot_speed"][j]) % 360

            if self.check_player_asteroid_collision(asteroid):
                if not self.player_shield_active:  # Shield blocks asteroid damage
                    self.player_health -= 1
                    self.add_explosion(self.player_pos, self.player_size * 1.5, self.colors["explosion"])
                
                asteroids_to_remove.append(i)

        for i in sorted(asteroids_to_remove, reverse=True):
            if i < len(self.asteroids):
                self.asteroids.pop(i)

        if len(self.asteroids) == 0 and not self.boss_active:
            self.wave += 1
            self.spawn_asteroid_wave()

    def update_boss(self):
        boss = self.boss_asteroid
        
        if boss:
            dx = self.player_pos[0] - boss["pos"][0]
            dz = self.player_pos[2] - boss["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist > 0:
                boss["pos"][0] += (dx / dist) * boss["speed"]
                boss["pos"][2] += (dz / dist) * boss["speed"]
            
            for j in range(3):
                boss["rotation"][j] = (boss["rotation"][j] + boss["rot_speed"][j]) % 360
            
            if dist < boss["warning_distance"] and not self.boss_warning:
                self.boss_warning = True
                self.warning_flash_timer = 100  # Flash duration
            elif dist >= boss["warning_distance"]:
                self.boss_warning = False
                
            if self.check_player_asteroid_collision(boss):
                if not self.player_shield_active:  
                    self.player_health -= 2  
                    self.add_explosion(self.player_pos, self.player_size * 2.0, self.colors["explosion"])
                boss["hit_points"] -= 1
                if boss["hit_points"] <= 0:
                    self.boss_defeated()

    def update_powerups(self):
        powerups_to_remove = []
        
        for i, powerup in enumerate(self.powerups):
            dx = self.player_pos[0] - powerup["pos"][0]
            dz = self.player_pos[2] - powerup["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist > 0:
                powerup["pos"][0] += (dx / dist) * powerup["speed"]
                powerup["pos"][2] += (dz / dist) * powerup["speed"]
            
            powerup["rotation"] = (powerup["rotation"] + 2) % 360
                
            if self.check_player_powerup_collision(powerup):
                self.apply_powerup(powerup)
                powerups_to_remove.append(i)

        for i in sorted(powerups_to_remove, reverse=True):
            if i < len(self.powerups):
                self.powerups.pop(i)

    def update_explosions(self):
        explosions_to_remove = []
        
        for i, explosion in enumerate(self.explosions):
            explosion["size"] += explosion["growth_rate"]
            
            explosion["alpha"] -= explosion["fade_rate"]
            
            if explosion["alpha"] <= 0 or explosion["size"] >= explosion["max_size"]:
                explosions_to_remove.append(i)
        
        for i in sorted(explosions_to_remove, reverse=True):
            if i < len(self.explosions):
                self.explosions.pop(i)

    def update_timers(self):
        if self.cheat_mode_cooldown > 0:
            self.cheat_mode_cooldown -= 1
            
        if self.bullet_boost_timer > 0:
            self.bullet_boost_timer -= 1
            if self.bullet_boost_timer <= 0:
                self.bullet_boost_active = False

        if self.player_shield_timer > 0:
            self.player_shield_timer -= 1
            if self.player_shield_timer <= 0:
                self.player_shield_active = False
                self.player_color = self.colors["player"]  # Reset color

        if self.warning_flash_timer > 0:
            self.warning_flash_timer -= 1

    def check_bullet_collisions(self, bullet):
        if self.boss_active and self.boss_asteroid:
            boss = self.boss_asteroid
            dx = bullet["pos"][0] - boss["pos"][0]
            dz = bullet["pos"][2] - boss["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist < (boss["size"] / 1.5 + bullet["size"]):
                boss["hit_points"] -= 1
                self.add_explosion(bullet["pos"], 0.5, self.colors["explosion"])
                self.score += 5 

                if boss["hit_points"] <= 0:
                    self.boss_defeated()
                    
                return True

        for i, asteroid in enumerate(self.asteroids):
            dx = bullet["pos"][0] - asteroid["pos"][0]
            dz = bullet["pos"][2] - asteroid["pos"][2]
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist < (asteroid["size"] / 1.5 + bullet["size"]):
                asteroid["hit_points"] -= 1
                
                if asteroid["hit_points"] <= 0:
                    self.add_explosion(asteroid["pos"], asteroid["size"], self.colors["explosion"])

                    if asteroid["type"] == "normal":
                        self.score += 10
                    elif asteroid["type"] == "fast":
                        self.score += 15
                    elif asteroid["type"] == "large":
                        self.score += 20

                    if asteroid["type"] == "large":
                        for i in range(random.randint(2, 3)):
                            offset_x = random.uniform(-1, 1)
                            offset_z = random.uniform(-1, 1)

                            new_pos = [
                                asteroid["pos"][0] + offset_x,
                                asteroid["pos"][1],
                                asteroid["pos"][2] + offset_z
                            ]

                            fragment_type = random.choice(["normal", "fast"])
                            self.spawn_asteroid(new_pos[0], new_pos[1], new_pos[2], fragment_type)
  
                    self.asteroids.pop(i)
                else:
                    self.add_explosion(bullet["pos"], 0.3, self.colors["explosion"])
                
                return True
        
        return False

    def check_player_asteroid_collision(self, asteroid):
        dx = self.player_pos[0] - asteroid["pos"][0]
        dz = self.player_pos[2] - asteroid["pos"][2]
        dist = math.sqrt(dx*dx + dz*dz)

        collision_threshold = self.player_size + asteroid["size"] * 0.7
        
        return dist < collision_threshold

    def check_player_powerup_collision(self, powerup):
        dx = self.player_pos[0] - powerup["pos"][0]
        dz = self.player_pos[2] - powerup["pos"][2]
        dist = math.sqrt(dx*dx + dz*dz)

        collision_threshold = self.player_size + powerup["size"]
        
        return dist < collision_threshold

    def apply_powerup(self, powerup):
        powerup_type = powerup["type"]
        
        if powerup_type == "health":
            if self.player_health < 5:  
                self.player_health += 1
                
        elif powerup_type == "speed":
            self.bullet_boost_active = True
            self.bullet_boost_timer = 500 
            
        elif powerup_type == "shield":
            self.player_shield_active = True
            self.player_shield_timer = 500 

    def boss_defeated(self):
        if self.boss_asteroid:
            self.add_explosion(
                self.boss_asteroid["pos"], 
                self.boss_asteroid["size"] * 2, 
                self.colors["explosion"]
            )

            self.score += 100 + (self.wave * 10)

            self.boss_asteroid = None
            self.boss_active = False
            self.boss_warning = False

            self.wave += 1
            self.spawn_asteroid_wave()

    def reset_game(self):
        self.__init__()  
