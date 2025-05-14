from OpenGL.GL import *
from OpenGL.GLUT import *
import math

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

        #elif key == 'w':
            #make it move forward
                
        elif key == 's':
            if not self.game_state.paused and not self.game_state.game_over:
                angle_rad = self.game_state.player_rotation * math.pi / 180.0
                self.game_state.player_pos[0] -= math.sin(angle_rad) * self.game_state.player_speed
                self.game_state.player_pos[2] -= math.cos(angle_rad) * self.game_state.player_speed
                
        elif key == 'd':
            if not self.game_state.paused and not self.game_state.game_over:
                self.game_state.player_rotation = (self.game_state.player_rotation - 5.0) % 360
                
        elif key == 'a':
            if not self.game_state.paused and not self.game_state.game_over:
                self.game_state.player_rotation = (self.game_state.player_rotation + 5.0) % 360
        
        glutPostRedisplay()

    def handle_keyboard_up(self, key, x, y):
        pass

    def handle_special_keys(self, key, x, y):
        if not self.game_state.paused and not self.game_state.game_over:
            if key == GLUT_KEY_UP:
                self.game_state.camera_tilt = min(45.0, self.game_state.camera_tilt + 2.0)
                
            elif key == GLUT_KEY_DOWN:
                self.game_state.camera_tilt = max(-20.0, self.game_state.camera_tilt - 2.0)
                
            elif key == GLUT_KEY_LEFT:
                self.game_state.camera_rotation = (self.game_state.camera_rotation - 5.0) % 360
                
            elif key == GLUT_KEY_RIGHT:
                self.game_state.camera_rotation = (self.game_state.camera_rotation + 5.0) % 360
        
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
