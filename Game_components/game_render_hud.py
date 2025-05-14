from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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
        self.draw_text(10, 30, "W,A,S,D: Move   Left Click: Shoot   Right Click: Toggle View   C: Cheat   P: Pause   R: Restart")
        
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
