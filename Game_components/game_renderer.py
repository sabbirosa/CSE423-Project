from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import time

from Game_components.game_renderer_core import GameRendererCore
from Game_components.game_render_hud import GameRendererHud

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
