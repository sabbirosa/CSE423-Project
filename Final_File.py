import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random
import time

class GameEngine:
    def __init__(self, game_state, game_render, input_handler):
        self.game_state = game_state
        self.game_render = game_render
        self.input_handler = input_handler
        self.window_width = 800
        self.window_height = 600 

    def init_opengl(self):
        glClearColor(0.02, 0.05, 0.1, 1.0) #Background color (Color of the space)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #Basic Laghting
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        #Setting up liight
        light_position = [10.0, 10.0, 10.0, 0.0]
        light_ambient = [0.2, 0.2, 0.2, 1.0]
        light_diffuse = [1.0, 1.0, 1.0, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        glEnable(GL_LIGHT0)

    def update_frame(self, value):
        self.game_state.update()
        glutPostRedisplay()
        glutTimerFunc(16, self.update_frame, 0)

    def setup_callbacks(self):
        glutDisplayFunc(self.game_render.render_scene)
        glutReshapeFunc(self.input_handler.handle_reshape)

        glutKeyboardFunc(self.input_handler.handle_keyboard)
        glutKeyboardUpFunc(self.input_handler.handle_keyboard_up)
        glutSpecialFunc(self.input_handler.handle_special_keys)

        glutMouseFunc(self.input_handler.handle_mouse)
        glutPassiveMotionFunc(self.input_handler.handle_mouse_motion)

        glutTimerFunc(16, self.update_frame, 0)

    def start(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_width, self.window_height)
        glutCreateWindow(b"Space Survival 3D")
        
        self.init_opengl()
        self.setup_callbacks()
        glutMainLoop()


class GameRendererHud:
    def render_hud(self, game_state, window_width, window_height):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        if game_state.boss_warning and (game_state.warning_flash_timer % 20 < 10):
            hud_color = game_state.colors["hud_warning"]
        else:
            hud_color = game_state.colors["hud"]
        
        self.draw_hud_background(10, window_height - 100, 250, 90, hud_color)

        glColor3f(1.0, 1.0, 1.0)
  
        self.draw_text(20, window_height - 30, f"SCORE: {game_state.score}")
 
        self.draw_text(20, window_height - 50, f"HEALTH: {game_state.player_health}")
    
        self.draw_text(20, window_height - 70, f"WAVE: {game_state.wave}")
      
        self.draw_text(20, window_height - 90, f"MISSED: {game_state.bullets_missed}/{game_state.max_missed_bullets}")
      
        if game_state.bullet_boost_active:
            self.draw_text(window_width - 200, window_height - 30, "SPEED BOOST ACTIVE")
            
        if game_state.player_shield_active:
            self.draw_text(window_width - 200, window_height - 50, "SHIELD ACTIVE")
    
        if game_state.cheat_mode_cooldown > 0:
            cooldown_percent = game_state.cheat_mode_cooldown / 1000.0
            self.draw_text(window_width - 200, window_height - 70, f"CHEAT: {int((1.0 - cooldown_percent) * 100)}%")
        else:
            self.draw_text(window_width - 200, window_height - 70, "CHEAT: READY (C)")
      
        camera_text = "VIEW: " + ("FIRST PERSON" if game_state.camera_mode == "first_person" else "THIRD PERSON")
        self.draw_text(window_width - 200, window_height - 90, camera_text)
    
        if game_state.boss_active and game_state.boss_asteroid:
            boss = game_state.boss_asteroid
            max_health = 5 + game_state.wave
            health_percent = boss["hit_points"] / max_health
     
            self.draw_text(window_width / 2 - 100, window_height - 30, "BOSS HEALTH")
         
            glColor3f(0.2, 0.2, 0.2)
            glBegin(GL_QUADS)
            glVertex2f(window_width / 2 - 100, window_height - 50)
            glVertex2f(window_width / 2 + 100, window_height - 50)
            glVertex2f(window_width / 2 + 100, window_height - 40)
            glVertex2f(window_width / 2 - 100, window_height - 40)
            glEnd()
          
            glColor3f(1.0 - health_percent, health_percent, 0.0)  # Green to red based on health
            glBegin(GL_QUADS)
            glVertex2f(window_width / 2 - 100, window_height - 50)
            glVertex2f(window_width / 2 - 100 + (200 * health_percent), window_height - 50)
            glVertex2f(window_width / 2 - 100 + (200 * health_percent), window_height - 40)
            glVertex2f(window_width / 2 - 100, window_height - 40)
            glEnd()
        
        # Add a directional indicator showing "FRONT" direction
        front_indicator_x = window_width / 2
        front_indicator_y = 70
        
        glColor3f(1.0, 1.0, 0.0)  # Bright yellow "FRONT" indicator
        self.draw_text(front_indicator_x - 20, front_indicator_y - 30, "FRONT")
        
        glBegin(GL_TRIANGLES)
        glVertex2f(front_indicator_x, front_indicator_y)
        glVertex2f(front_indicator_x - 10, front_indicator_y - 20)
        glVertex2f(front_indicator_x + 10, front_indicator_y - 20)
        glEnd()
       
        glColor3f(0.7, 0.7, 0.7)
        self.draw_text(10, 30, "Right and Left Arrow: Move   Left Click: Shoot   Right Click: Toggle View   C: Cheat   P: Pause   R: Restart")
        
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def render_game_over(self, game_state, window_width, window_height):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        
        glColor3f(1.0, 0.2, 0.2)
        self.draw_text_large(window_width / 2 - 100, window_height / 2 + 50, "GAME OVER")
        
        glColor3f(1.0, 1.0, 1.0)
        self.draw_text(window_width / 2 - 120, window_height / 2, f"FINAL SCORE: {game_state.score}")
        self.draw_text(window_width / 2 - 120, window_height / 2 - 30, f"WAVES SURVIVED: {game_state.wave}")
        
        glColor3f(0.2, 1.0, 0.2)
        self.draw_text(window_width / 2 - 120, window_height / 2 - 80, "PRESS 'R' TO RESTART")
        
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def render_paused_screen(self, window_width, window_height):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(window_width, 0)
        glVertex2f(window_width, window_height)
        glVertex2f(0, window_height)
        glEnd()
        
        glColor3f(0.2, 0.8, 1.0)
        self.draw_text_large(window_width / 2 - 80, window_height / 2 + 20, "PAUSED")
        
        glColor3f(1.0, 1.0, 1.0)
        self.draw_text(window_width / 2 - 120, window_height / 2 - 30, "PRESS 'P' TO CONTINUE")
        
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_hud_background(self, x, y, width, height, color):
        glColor4f(color[0], color[1], color[2], 0.5)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
        
        glColor4f(color[0], color[1], color[2], 0.8)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

    def draw_text(self, x, y, text):
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char)) # type: ignore

    def draw_text_large(self, x, y, text):
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))  # type: ignore


class GameRendererCore:
    def render_bullets(self, game_state, quadric):
        for bullet in game_state.bullets:
           glPushMatrix()

           #Position of the Bullet
           glTranslatef(bullet["pos"][0], bullet["pos"][1], bullet["pos"][2])

           #Face direction of travel
           glRotatef(bullet["direction"] * 180.0 / math.pi, 0, 1, 0)
           glRotatef(90, 0, 0, 1) 

           #Color of the bullet
           glColor3f(bullet["color"][0], bullet["color"][1], bullet["color"][2])

           gluCylinder(quadric, bullet["size"] * 0.2, bullet["size"] * 0.2, bullet["size"] * 3.0, 8, 1)

           glPushMatrix()
           glTranslatef(0, 0, bullet["size"] * 3.0)
           glColor3f(1.0, 1.0, 0.5)
           gluSphere(quadric, bullet["size"] * 0.3, 8, 8)
           glPopMatrix()

           #Bullet trails
           glPushMatrix()
           glRotatef(180, 0, 1, 0)
           glColor4f(1.0, 0.6, 0.2, 0.6)
           gluCylinder(quadric, 0, bullet["size"] * 0.4, bullet["size"] * 2.0, 8, 1)
           glPopMatrix()
           glPopMatrix()

    def render_asteroids(self, game_state, quadric):
        for asteroid in game_state.asteroids:
            glPushMatrix()

            #Asteriods Positions
            glTranslatef(asteroid["pos"][0], asteroid["pos"][1], asteroid["pos"][2])

            #Roate Asteriods
            glRotatef(asteroid["rotation"][0], 1, 0, 0)
            glRotatef(asteroid["rotation"][1], 0, 1, 0)
            glRotatef(asteroid["rotation"][2], 0, 0, 1)

            #Asteroids Color
            glColor3f(asteroid["color"][0], asteroid["color"][1], asteroid["color"][2])

            if asteroid["shape"] == "cube":
                glutSolidCube(asteroid["size"])
                for i in range(4):
                    glPushMatrix()
                    angle = i * 90.0
                    x_offset = math.sin(angle * math.pi / 180.0) * asteroid["size"] * 0.5
                    z_offset = math.cos(angle * math.pi / 180.0) * asteroid["size"] * 0.5

                    glTranslatef(x_offset, asteroid["size"] * 0.4, z_offset)
                    glColor3f(asteroid["color"][0] * 0.8, asteroid["color"][1] * 0.8, asteroid["color"][2] * 0.8) #Darker Color

                    glScalef(0.3, 0.3, 0.3)
                    glutSolidCube(asteroid["size"] * 0.5)
                    glPopMatrix()

            else:
                gluSphere(quadric, asteroid["size"], 12, 12)
                for i in range(3):
                    glPushMatrix()
                    angle1 = i * 120.0
                    angle2 = i * 60.0
                    x_offset = math.sin(angle1 * math.pi / 180.0) * asteroid["size"] * 0.7
                    y_offset = math.sin(angle2 * math.pi / 180.0) * asteroid["size"] * 0.7
                    z_offset = math.cos(angle1 * math.pi / 180.0) * asteroid["size"] * 0.7

                    glTranslatef(x_offset, y_offset, z_offset)
                    glColor3f(asteroid["color"][0] * 0.7, asteroid["color"][1] * 0.7, asteroid["color"][2] * 0.7)

                    gluSphere(quadric, asteroid["size"] * 0.2, 8, 8)
                    glPopMatrix()

            glPopMatrix()

    def render_boss(self, game_state, quadric):
        boss = game_state.boss_asteroid
        if boss:
            glPushMatrix()

            #Position of the boss
            glTranslatef(boss["pos"][0], boss["pos"][1], boss["pos"][2])

            glRotatef(boss["rotation"][0], 1, 0, 0)
            glRotatef(boss["rotation"][1], 0, 1, 0)
            glRotatef(boss["rotation"][2], 0, 0, 1)

            #Boss color with pulsing
            if game_state.boss_warning and (game_state.warning_flash_timer % 20 < 10):
                glColor3f(1.0, 0.2, 0.2)
            else:
                glColor3f(boss["color"][0], boss["color"][1], boss["color"][2])

            gluSphere(quadric, boss["size"] * 0.8, 16, 16)
            offset = boss["size"] * 0.6

            for x in [-1, 1]:
                for y in [-1, 1]:
                    for z in [-1, 1]:
                        glPushMatrix()
                        glTranslatef(x * offset, y * offset, z * offset)
                        glColor3f(boss["color"][0] * 0.8, boss["color"][1] * 0.8, boss["color"][2] * 0.8)
                        glutSolidCube(boss["size"] * 0.5)
                        glPopMatrix()

            for i in range(6):
                glPushMatrix()

                if i == 0:
                    glTranslatef(boss["size"] * 0.8, 0, 0)
                    glRotatef(90, 0, 1, 0)
                elif i == 1:
                    glTranslatef(-boss["size"] * 0.8, 0, 0)
                    glRotatef(-90, 0, 1, 0)
                elif i == 2:
                    glTranslatef(0, boss["size"] * 0.8, 0)
                    glRotatef(-90, 1, 0, 0)
                elif i == 3:
                    glTranslatef(0, -boss["size"] * 0.8, 0)
                    glRotatef(90, 1, 0, 0)
                elif i == 4:
                    glTranslatef(0, 0, boss["size"] * 0.8)
                else:
                    glTranslatef(0, 0, -boss["size"] * 0.8)
                    glRotatef(180, 0, 1, 0)

                #Spikes
                glColor3f(1.0, 0.3, 0.0)
                gluCylinder(quadric, boss["size"] * 0.2, 0, boss["size"] * 0.6, 8, 1)
                glPopMatrix()

            health_percent = boss["hit_points"] / (5.0 + game_state.wave)
            core_pulse = (math.sin(time.time() * 3.0) + 1.0) * 0.5

            glPushMatrix()
            glColor3f(1.0, 0.3 + (1.0 - health_percent) * 0.7, 0.0)
            gluSphere(quadric, boss["size"] * 0.4 * (0.8 + core_pulse * 0.2), 12, 12)
            glPopMatrix()
            glPopMatrix()

    def render_powerups(self, game_state, quadric):
        for powerup in game_state.powerups:
            glPushMatrix()
            glTranslatef(powerup["pos"][0], powerup["pos"][1], powerup["pos"][2])
            glRotatef(powerup["rotation"], 0, 1, 0)
            glRotatef(time.time() * 30 % 360, 1, 1, 1)
            glColor3f(powerup["color"][0], powerup["color"][1], powerup["color"][2])

            if powerup["type"] == "health":
                glutSolidCube(powerup["size"] * 0.8)

                glPushMatrix()
                glScalef(0.2, 1.0, 0.2)
                glutSolidCube(powerup["size"] * 1.5)
                glPopMatrix()

                glPushMatrix()
                glScalef(1.0, 0.2, 0.2)
                glutSolidCube(powerup["size"] * 1.5)
                glPopMatrix()
            
            elif powerup["type"] == "speed":
                gluSphere(quadric, powerup["size"] * 0.5, 12, 12)
                glPushMatrix()
                glTranslatef(0, 0, powerup["size"] * 0.5)
                glRotatef(90, 1, 0, 0)
                gluCylinder(quadric, powerup["size"] * 0.2, powerup["size"] * 0.2, powerup["size"] * 0.8, 8, 2)

                glTranslatef(0, 0, powerup["size"] * 0.8)
                gluCylinder(quadric, powerup["size"] * 0.4, 0, powerup["size"] * 0.4, 8, 2)
                glPopMatrix()

            else:
                glutSolidCube(powerup["size"] * 0.6)
                glColor4f(powerup["color"][0], powerup["color"][1], powerup["color"][2], 0.5)
                gluSphere(quadric, powerup["size"] * 0.8, 12, 12)

            pulse = (math.sin(time.time() * 5.0) + 1.0) / 2.0
            glColor4f(powerup["color"][0], powerup["color"][1], powerup["color"][2], 0.3 * pulse)
            gluSphere(quadric, powerup["size"] * (1.0 + 0.2 * pulse), 12, 12)

            glPopMatrix()

    def render_explosions(self, game_state, quadric):
        for explosion in game_state.explosions:
            glPushMatrix()

            glTranslatef(explosion["pos"][0], explosion["pos"][1], explosion["pos"][2])
            glColor4f(explosion["color"][0], explosion["color"][1], explosion["color"][2], explosion["alpha"])
            gluSphere(quadric, explosion["size"], 12, 12)
            inner_size = explosion["size"] * 0.7
            glColor4f(1.0, 0.8, 0.2, explosion["alpha"] * 0.8)
            gluSphere(quadric, inner_size, 8, 8)
            
            glPopMatrix() 


class GameRenderer:
    def __init__(self, game_state, window_width=800, window_height=600):
        self.game_state = game_state
        self.quadric = gluNewQuadric()
        self.window_width = window_width
        self.window_height = window_height

        self.renderer_core = GameRendererCore()
        self.renderer_hud = GameRendererHud()
        
    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
       
        self.setup_camera()
        
        self.render_stars()
        
        self.render_player()
        self.renderer_core.render_bullets(self.game_state, self.quadric)
        self.renderer_core.render_asteroids(self.game_state, self.quadric)
        
        if self.game_state.boss_active and self.game_state.boss_asteroid:
            self.renderer_core.render_boss(self.game_state, self.quadric)
            
        self.renderer_core.render_powerups(self.game_state, self.quadric)
        self.renderer_core.render_explosions(self.game_state, self.quadric)
        
        self.renderer_hud.render_hud(self.game_state, self.window_width, self.window_height)
        
        if self.game_state.game_over:
            self.renderer_hud.render_game_over(self.game_state, self.window_width, self.window_height)
        
        if self.game_state.paused:
            self.renderer_hud.render_paused_screen(self.window_width, self.window_height)
       
        glutSwapBuffers()
        
    def set_window_size(self, width, height):
        self.window_width = width
        self.window_height = height

    def setup_camera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.window_width / self.window_height, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        if self.game_state.camera_mode == "first_person":
            # Calculate eye position (at cockpit)
            eye_x = self.game_state.player_pos[0]
            eye_y = self.game_state.player_pos[1] + 0.3 
            eye_z = self.game_state.player_pos[2]
            
            # Look straight ahead
            look_x = eye_x
            look_y = eye_y
            look_z = eye_z + 10  # Look forward along z-axis
            
            gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 1, 0)

        # 3rd person view    
        else:  
            # Position camera behind and slightly above the player
            distance = 5.0
            height = 2.0
          
            cam_x = self.game_state.player_pos[0]
            cam_y = self.game_state.player_pos[1] + height
            cam_z = self.game_state.player_pos[2] - distance
            
            # Look at player position
            gluLookAt(cam_x, cam_y, cam_z, 
                      self.game_state.player_pos[0], self.game_state.player_pos[1], self.game_state.player_pos[2], 
                      0, 1, 0)

    def render_stars(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        glPointSize(2.0)
        glBegin(GL_POINTS)
        
        for star in self.game_state.stars:
            glColor3f(star[3] * self.game_state.colors["stars"][0],
                      star[3] * self.game_state.colors["stars"][1],
                      star[3] * self.game_state.colors["stars"][2])
            
            glVertex3f(star[0], star[1], star[2])
            
        glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glPointSize(1.0)

    def render_player(self):
        glPushMatrix()
        
        glTranslatef(self.game_state.player_pos[0],
                     self.game_state.player_pos[1],
                     self.game_state.player_pos[2])
        
        # Always face forward (no rotation)
        # Fixed rotation of 0 degrees (facing forward along z-axis)
 
        if self.game_state.player_shield_active:
            shield_scale = 1.1 + math.sin(time.time() * 5.0) * 0.1
            shield_color = self.game_state.colors["shield_powerup"]
            
            glColor4f(shield_color[0], shield_color[1], shield_color[2], 0.4)
            glPushMatrix()
            glScalef(shield_scale, shield_scale, shield_scale)
            gluSphere(self.quadric, self.game_state.player_size * 1.2, 16, 16)
            glPopMatrix()

        glColor3f(self.game_state.player_color[0],
                  self.game_state.player_color[1],
                  self.game_state.player_color[2])

        glPushMatrix()
        glScalef(1.0, 0.4, 2.0)  
        glutSolidCube(self.game_state.player_size)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, self.game_state.player_size * 0.2, self.game_state.player_size * 0.3)
        glColor3f(0.2, 0.8, 1.0) 
        gluSphere(self.quadric, self.game_state.player_size * 0.25, 12, 12)
        glPopMatrix()
 
        glPushMatrix()
        glTranslatef(self.game_state.player_size * 0.8, 0, 0)
        glScalef(0.2, 0.1, 1.0)
        glColor3f(0.5, 0.7, 0.9)  
        glutSolidCube(self.game_state.player_size)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-self.game_state.player_size * 0.8, 0, 0)
        glScalef(0.2, 0.1, 1.0)
        glColor3f(0.5, 0.7, 0.9)  
        glutSolidCube(self.game_state.player_size)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.3, 0.1)  
        gluCylinder(self.quadric, self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.3, 8, 3)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.3, 0.1)  
        gluCylinder(self.quadric, self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.15, 
                    self.game_state.player_size * 0.3, 8, 3)
        glPopMatrix()
   
        engine_glow = (math.sin(time.time() * 10) + 1.0) * 0.5  
        glPushMatrix()
        glTranslatef(self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8 - 0.05)
        glRotatef(90, 1, 0, 0)
        glColor3f(1.0, 0.5 + engine_glow * 0.5, 0.0)  
        gluDisk(self.quadric, 0, self.game_state.player_size * 0.13, 8, 1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-self.game_state.player_size * 0.4, -self.game_state.player_size * 0.1, -self.game_state.player_size * 0.8 - 0.05)
        glRotatef(90, 1, 0, 0)
        glColor3f(1.0, 0.5 + engine_glow * 0.5, 0.0)  
        gluDisk(self.quadric, 0, self.game_state.player_size * 0.13, 8, 1)
        glPopMatrix()
  
        glPopMatrix() 


class GameState:
    def __init__(self):
        # Player state
        self.player_pos = [0.0, 0.0, 0.0]
        self.player_rotation = 0.0
        self.player_health = 3  # Changed from 30 to 3 for better health management
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
        
        # Check if this wave should have a boss
        if self.wave > 0 and self.wave % self.boss_wave_interval == 0:
            self.boss_active = True
            self.spawn_boss_asteroid()
        else:
            self.boss_active = False

            asteroid_count = 5 + self.wave * 2 
            
            for i in range(asteroid_count):
                # Fixed front direction (z-axis)
                distance = random.uniform(20, 30)
                
                # Randomize x position across the screen width
                pos_x = random.uniform(-10, 10)
                pos_z = self.player_pos[2] + distance  # Always in front of the player
             
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
        # Position boss in front of player
        distance = 35
        
        # Random x position but within visible range
        pos_x = random.uniform(-8, 8)
        pos_z = self.player_pos[2] + distance
        
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
            # Spawn powerup in front of the player
            distance = random.uniform(15, 25)
            
            # Random x position but within visible range
            pos_x = random.uniform(-10, 10)
            pos_z = self.player_pos[2] + distance
       
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
        # Ship always faces forward (fixed direction)
        # Bullet starts at player position and moves forward
        front_x = self.player_pos[0]
        front_z = self.player_pos[2] + self.player_size
        
        # Fixed direction (straight ahead)
        direction = 0  # 0 radians = forward along z-axis
     
        bullet = {
            "pos": [front_x, self.player_pos[1], front_z],
            "direction": direction,
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
            
            # Clear all asteroids with explosions
            for asteroid in self.asteroids[:]:
                self.add_explosion(asteroid["pos"], asteroid["size"] * 1.5, self.colors["explosion"])
                self.score += 10
            
            # Clear boss if present
            if self.boss_active and self.boss_asteroid:
                self.add_explosion(
                    self.boss_asteroid["pos"], 
                    self.boss_asteroid["size"] * 2, 
                    self.colors["explosion"]
                )
                self.score += 100
                self.boss_asteroid = None
                self.boss_active = False
                self.boss_warning = False
            
            # Clear the asteroids list
            self.asteroids = []
            
            # Create a visual effect of bullets without counting misses
            # These bullets will be removed immediately after creation
            bullets_for_effect = []
            for angle in range(0, 360, 15): 
                angle_rad = angle * math.pi / 180.0
                
                # Calculate bullet starting position
                front_x = self.player_pos[0] + math.sin(angle_rad) * self.player_size
                front_z = self.player_pos[2] + math.cos(angle_rad) * self.player_size
                
                bullet = {
                    "pos": [front_x, self.player_pos[1], front_z],
                    "direction": angle_rad,
                    "speed": self.bullet_speed * 1.5, 
                    "distance": 0,
                    "max_distance": 10,  # Short range for visual effect
                    "size": 0.2,  
                    "color": [1.0, 0.3, 0.3] 
                }
                
                bullets_for_effect.append(bullet)
            
            # Add the bullets for visual effect only
            self.bullets.extend(bullets_for_effect)

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
        
        # Spawn new asteroid wave if there are none and we're not in boss mode
        # This is now handled in update_asteroids to avoid double spawning
        
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
            # Bullets move forward along z-axis
            bullet["pos"][2] += bullet["speed"]

            dist_moved = bullet["speed"]
            bullet["distance"] += dist_moved

            if bullet["distance"] >= bullet["max_distance"]:
                bullets_to_remove.append(i)
                # Only count missed bullets if not in cheat mode
                if not self.cheat_mode_active:
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
            # Move asteroids toward player's z-position (not tracking player's x position)
            asteroid["pos"][2] -= asteroid["speed"]  # Move toward player (decreasing z)

            # Rotate asteroid
            for j in range(3):
                asteroid["rotation"][j] = (asteroid["rotation"][j] + asteroid["rot_speed"][j]) % 360

            # Check if asteroid passed the player (dodged)
            if asteroid["pos"][2] < self.player_pos[2]:
                asteroids_to_remove.append(i)
                continue

            # Check for collision
            if self.check_player_asteroid_collision(asteroid):
                if not self.player_shield_active:  # Shield blocks asteroid damage
                    self.player_health -= 1
                    self.add_explosion(self.player_pos, self.player_size * 1.5, self.colors["explosion"])
                
                asteroids_to_remove.append(i)

        for i in sorted(asteroids_to_remove, reverse=True):
            if i < len(self.asteroids):
                self.asteroids.pop(i)

        # Increment wave if asteroids are cleared
        if len(self.asteroids) == 0 and not self.boss_active:
            self.wave += 1

        # Spawn new asteroid wave if there are none and we're not in boss mode
        if len(self.asteroids) == 0 and not self.boss_active:
            self.spawn_asteroid_wave()

    def update_boss(self):
        boss = self.boss_asteroid
        
        if boss:
            # Move boss toward player's z-position
            boss["pos"][2] -= boss["speed"]
            
            # Slowly move toward player's x position for more challenge
            if boss["pos"][0] < self.player_pos[0]:
                boss["pos"][0] += boss["speed"] * 0.5
            elif boss["pos"][0] > self.player_pos[0]:
                boss["pos"][0] -= boss["speed"] * 0.5
            
            for j in range(3):
                boss["rotation"][j] = (boss["rotation"][j] + boss["rot_speed"][j]) % 360
            
            # Check if boss passed the player (dodged)
            if boss["pos"][2] < self.player_pos[2]:
                self.boss_asteroid = None
                self.boss_active = False
                self.boss_warning = False
                self.wave += 1
                self.spawn_asteroid_wave()
                return
            
            # Warning when boss is close
            dist_z = boss["pos"][2] - self.player_pos[2]
            if dist_z < boss["warning_distance"] and not self.boss_warning:
                self.boss_warning = True
                self.warning_flash_timer = 100  # Flash duration
            elif dist_z >= boss["warning_distance"]:
                self.boss_warning = False
                
            if self.check_player_asteroid_collision(boss):
                if not self.player_shield_active:  
                    # Boss causes 1 damage point like regular asteroids
                    self.player_health -= 1
                    self.add_explosion(self.player_pos, self.player_size * 2.0, self.colors["explosion"])
                boss["hit_points"] -= 1
                if boss["hit_points"] <= 0:
                    self.boss_defeated()

    def update_powerups(self):
        powerups_to_remove = []
        
        for i, powerup in enumerate(self.powerups):
            # Move powerups toward player
            powerup["pos"][2] -= powerup["speed"]
            
            # Rotate powerup for visual effect
            powerup["rotation"] = (powerup["rotation"] + 2) % 360
            
            # Check if powerup passed the player (missed)
            if powerup["pos"][2] < self.player_pos[2]:
                powerups_to_remove.append(i)
                continue
                
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
            
        # Reset cheat mode active flag after a short duration (30 frames)
        if self.cheat_mode_active:
            self.cheat_mode_active = False
            
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
        # Check x-axis distance (horizontal plane)
        dx = self.player_pos[0] - asteroid["pos"][0]
        
        # Check z-axis distance (depth)
        dz = self.player_pos[2] - asteroid["pos"][2]
        
        # Calculate distance in the xz-plane
        dist = math.sqrt(dx*dx + dz*dz)

        # Adjust collision threshold based on asteroid size
        collision_threshold = self.player_size + asteroid["size"] * 0.7
        
        return dist < collision_threshold

    def check_player_powerup_collision(self, powerup):
        # Check x-axis distance (horizontal plane)
        dx = self.player_pos[0] - powerup["pos"][0]
        
        # Check z-axis distance (depth)
        dz = self.player_pos[2] - powerup["pos"][2]
        
        # Calculate distance in the xz-plane
        dist = math.sqrt(dx*dx + dz*dz)

        collision_threshold = self.player_size + powerup["size"]
        
        return dist < collision_threshold

    def apply_powerup(self, powerup):
        powerup_type = powerup["type"]
        
        if powerup_type == "health":
            # Increase health by 1, with a maximum of 5
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



class InputHandler:
    def __init__(self, game_state, game_renderer):
        self.game_state = game_state
        self.game_renderer = game_renderer
        
    def handle_keyboard(self, key, x, y):
        key = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()
        
        if key == 'p':
            self.game_state.paused = not self.game_state.paused
            
        elif key == 'r':
            self.game_state.reset_game()
            
        elif key == 'c':
            if not self.game_state.paused and not self.game_state.game_over:
                self.game_state.activate_cheat_mode()
        
        glutPostRedisplay()

    def handle_keyboard_up(self, key, x, y):
        pass

    def handle_special_keys(self, key, x, y):
        if not self.game_state.paused and not self.game_state.game_over:
            if key == GLUT_KEY_RIGHT:
                # Move ship left on x-axis
                self.game_state.player_pos[0] -= self.game_state.player_speed
                # Limit the ship's movement to stay on screen
                screen_bound = 10.0  # Adjust based on your game's scale
                self.game_state.player_pos[0] = max(-screen_bound, self.game_state.player_pos[0])
                
            elif key == GLUT_KEY_LEFT:
                # Move ship right on x-axis
                self.game_state.player_pos[0] += self.game_state.player_speed
                # Limit the ship's movement to stay on screen
                screen_bound = 10.0  # Adjust based on your game's scale
                self.game_state.player_pos[0] = min(screen_bound, self.game_state.player_pos[0])
        
        glutPostRedisplay()

    def handle_mouse(self, button, state, x, y):
        if not self.game_state.paused and not self.game_state.game_over:
            if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
                self.game_state.shoot_bullet()
                
            elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
                if self.game_state.camera_mode == "third_person":
                    self.game_state.camera_mode = "first_person"
                else:
                    self.game_state.camera_mode = "third_person"
        
        glutPostRedisplay()

    def handle_mouse_motion(self, x, y):
        pass

    def handle_reshape(self, width, height):
        self.game_renderer.set_window_size(width, height)

        glViewport(0, 0, width, height)

def main():
    game_state = GameState()

    game_renderer = GameRenderer(game_state)

    input_handler = InputHandler(game_state, game_renderer)

    game_engine = GameEngine(game_state, game_renderer, input_handler)
    game_engine.start()

if __name__ == "__main__":
    main()