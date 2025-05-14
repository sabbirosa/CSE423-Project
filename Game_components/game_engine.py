import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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
