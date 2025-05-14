from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import time

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
