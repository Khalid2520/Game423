import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

cameraPos = [0, 500, 500]
cameraRot = 0


fpView = False
gunViewState = False
fieldPos = 130


noEnemy = 5
enemyList = []
enemyChngRate = [1] * noEnemy
enemyRadius = 55

score = 0
bMissed = 0
life = 5
gameStatus = False


for _ in range(noEnemy):
    while True:
        x, y = random.randint(-470, 470), random.randint(-470, 470)
        if abs(x) >= 150 or abs(y) >= 150:
            enemyList.append([x, y, 0])
            break

def distance(pos1, pos2):
    dx, dy, dz = pos1[0] - pos2[0], pos1[1] - pos2[1], pos1[2] - pos2[2]
    return math.sqrt(dx**2 + dy**2 + dz**2)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def isEnemyInRange(enemy_pos):
    dx, dy = enemy_pos[0] - playerPos[0], enemy_pos[1] - playerPos[1]
    distance_sq = dx**2 + dy**2
    if distance_sq < 1:
        return False
    enemy_angle = math.degrees(math.atan2(-dy, -dx)) % 360
    gun_angle_norm = gunAngle % 360
    angle_diff = abs(gun_angle_norm - enemy_angle)
    angle_diff = min(angle_diff, 360 - angle_diff)
    return angle_diff <= 16

def keyboardListener(key, x, y):
    global gunAngle, playerPos, playerSpeed, gameStatus, cheatMode, movAngle, gunViewState, fpView

    if gameStatus:
        if key == b'r':
            resetGame()
        return

    if key == b'c':
        cheatMode = not cheatMode
        movAngle = gunAngle

    if key == b'v' and not cheatMode:
        fpView = not fpView
        if fpView:
            gunViewState = True

    handleRotation(key)
    handleMovement(key)

    if key == b'r':
        resetGame()

    glutPostRedisplay()

def handleRotation(key):
    global gunAngle, movAngle, cheatMode
    if not cheatMode:
        if key == b'a':
            gunAngle = (gunAngle + 5) % 360
            movAngle = gunAngle
        elif key == b'd':
            gunAngle = (gunAngle - 5) % 360
            movAngle = gunAngle

def handleMovement(key):
    global playerPos, playerSpeed, movAngle, gunAngle, cheatMode
    moveDirection = movAngle if cheatMode else gunAngle
    dx = playerSpeed * math.cos(math.radians(moveDirection))
    dy = playerSpeed * math.sin(math.radians(moveDirection))
    
    if key == b'w':
        nextX, nextY = playerPos[0] - dx, playerPos[1] - dy
    elif key == b's':
        nextX, nextY = playerPos[0] + dx, playerPos[1] + dy
    else:
        return
    
    if -500 <= nextX <= 500 and -500 <= nextY <= 500:
        playerPos[0], playerPos[1] = nextX, nextY

def specialKeyListener(key, x, y):
    global cameraPos, cameraRot, fpView
    if fpView:
        glutPostRedisplay()
        return

    camX, camY, camZ = cameraPos

    if key == GLUT_KEY_UP:
        camZ = min(camZ + 20, 800)
    elif key == GLUT_KEY_DOWN:
        camZ = max(camZ - 20, 200)
    elif key == GLUT_KEY_LEFT:
        cameraRot = (cameraRot + 5) % 360
    elif key == GLUT_KEY_RIGHT:
        cameraRot = (cameraRot - 5) % 360

    cameraPos = (camX, camY, camZ)
    glutPostRedisplay()

playerPos = [0, 0, 0]
gunAngle = 90
movAngle = 90
playerSpeed = 12
playerRadius = 35

bulletList = []
bullet_size = 20
bullet_speed = 12
bulletLimit = 10

def bulletFire():
    global bulletList, gunAngle, playerPos, cheatMode, enemyList

    gun_length = 70
    gun_offset_x = -math.cos(math.radians(gunAngle)) * gun_length
    gun_offset_y = -math.sin(math.radians(gunAngle)) * gun_length

    bullet_pos = [
        playerPos[0] + gun_offset_x,
        playerPos[1] + gun_offset_y,
        playerPos[2] + 100
    ]

    bullet_vel = [
        -math.cos(math.radians(gunAngle)) * bullet_speed,
        -math.sin(math.radians(gunAngle)) * bullet_speed,
        0
    ]

    target_index = -1
    if cheatMode:
        target_index = next(
            (i for i, enemy_pos in enumerate(enemyList) if isEnemyInRange(enemy_pos)),
            -1
        )

    bulletList.append({
        'position': bullet_pos,
        'direction': bullet_vel,
        'active': True,
        'targetLocked': cheatMode and target_index != -1,
        'target': target_index
    })

def cameraSetUp():
    global fpView, playerPos, gunAngle, cameraPos, cameraRot, gunViewState

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(100 if fpView else fieldPos, 1.25, 0.1, 1500)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if fpView:
        eX, eY, eZ = playerPos[0], playerPos[1], playerPos[2] + 150
        if cheatMode and not gunViewState:
            x = eX - math.cos(math.radians(90)) * 100
            y = eY - math.sin(math.radians(90)) * 100
        else:
            x = eX - math.cos(math.radians(gunAngle)) * 100
            y = eY - math.sin(math.radians(gunAngle)) * 100
        gluLookAt(eX, eY, eZ, x, y, eZ, 0, 0, 1)
    else:
        x = 450 * math.cos(math.radians(cameraRot))
        y = 450 * math.sin(math.radians(cameraRot))
        gluLookAt(x, y, cameraPos[2], 0, 0, 0, 0, 0, 1)

def idle():
    global enemyList, bulletList, score, bMissed, life, enemyChngRate, gameStatus
    global scaleIncrease, scaleStatus, sTimer, scaleMin, scaleMax
    global gunAngle, cheatMode, autoFire

    if gameStatus:
        glutPostRedisplay()
        return

    if cheatMode:
        gunAngle = (gunAngle + auto_rotation_speed) % 360
        autoFire += 1
        if autoFire >= autoFireTimeSpan:
            for i, enemy in enumerate(enemyList):
                if isEnemyInRange(enemy):
                    dx, dy = enemy[0] - playerPos[0], enemy[1] - playerPos[1]
                    gunAngle = (math.degrees(math.atan2(dy, dx)) + 180) % 360
                    bulletFire()
                    autoFire = 0
                    break

    updateEnemyScaling()
    moveEnemiesAndCheckCollisions()
    manageBullets()

def mouseListener(button, state, x, y):
    global gameStatus, fpView
    if gameStatus:
        return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bulletFire()
        glutPostRedisplay()

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        fpView = not fpView
        glutPostRedisplay()
cheatMode = False
auto_rotation_speed = 2.9 
autoFire = 0
autoFireTimeSpan = 15 

scaleMin = 0.5
scaleMax = 1
steps = 20 
scaleIncrease =  0.025
scaleStatus = 1
sTimer = 0 
scaleSpan = 100 


def moveEnemiesAndCheckCollisions():
    global enemyList, bulletList, score, life, gameStatus, enemyChngRate
    
    enemy_speed = 0.1
    player_radius = 35
    
    for i in range(len(enemyList)):
        dx = playerPos[0] - enemyList[i][0]
        dy = playerPos[1] - enemyList[i][1]
        

        if dx != 0 or dy != 0:
            inv_length = 1.0 / math.sqrt(dx*dx + dy*dy)
            dx *= inv_length
            dy *= inv_length
        

        enemyList[i][0] += dx * enemy_speed
        enemyList[i][1] += dy * enemy_speed
        
        enemy_radius = 60 * enemyChngRate[i]
        dist_x = playerPos[0] - enemyList[i][0]
        dist_y = playerPos[1] - enemyList[i][1]
        dist_z = playerPos[2] - enemyList[i][2]
        dist_sq = dist_x*dist_x + dist_y*dist_y + dist_z*dist_z
        
        if dist_sq < (enemy_radius + player_radius)**2:
            life -= 1
            while True:
                x = random.randint(-470, 470)
                y = random.randint(-470, 470)
                if abs(x) >= 150 or abs(y) >= 150:
                    enemyList[i] = [x, y, 0]
                    break
            
            if life <= 0:
                gameStatus = True
                return


def manageBullets():
    global bulletList, enemyList, score, bMissed, life, gameStatus, cheatMode
    
    BULLET_SPEED_BOOST = 1.5
    BULLET_LIMIT = 600
    ENEMY_HEIGHT = 30
    VERTICAL_HIT_RANGE = 100
    

    bullets_to_remove = []
    
    for i in range(len(bulletList)):
        bullet = bulletList[i]
        if not bullet['active']:
            bullets_to_remove.append(i)
            continue
        

        if cheatMode and bullet.get('targetLocked', False):
            target_index = bullet.get('target', -1)
            if 0 <= target_index < len(enemyList):
                target = enemyList[target_index]
                dx = target[0] - bullet['position'][0]
                dy = target[1] - bullet['position'][1]
                dz = ENEMY_HEIGHT - bullet['position'][2]
                

                length = math.sqrt(dx*dx + dy*dy + dz*dz)
                if length > 0:
                    bullet['direction'] = [
                        dx/length * bullet_speed * BULLET_SPEED_BOOST,
                        dy/length * bullet_speed * BULLET_SPEED_BOOST,
                        dz/length * bullet_speed
                    ]
        

        bullet['position'][0] += bullet['direction'][0]
        bullet['position'][1] += bullet['direction'][1]
        bullet['position'][2] += bullet['direction'][2]
        

        if (abs(bullet['position'][0]) > BULLET_LIMIT or 
            abs(bullet['position'][1]) > BULLET_LIMIT):
            if not cheatMode:
                bMissed += 1
                if bMissed >= bulletLimit:
                    gameStatus = True
            bullet['active'] = False
            bullets_to_remove.append(i)
            continue
        

        for j in range(len(enemyList)):
            enemy = enemyList[j]
            dx = bullet['position'][0] - enemy[0]
            dy = bullet['position'][1] - enemy[1]
            distance = math.sqrt(dx*dx + dy*dy)
            height_diff = abs(bullet['position'][2] - ENEMY_HEIGHT)
            
            if distance < 60 * enemyChngRate[j] and height_diff < VERTICAL_HIT_RANGE:
                score += 1
                bullet['active'] = False
                bullets_to_remove.append(i)
                
                while True:
                    x = random.randint(-470, 470)
                    y = random.randint(-470, 470)
                    if abs(x) >= 150 or abs(y) >= 150:
                        enemyList[j] = [x, y, 0]
                        break
                break
    

    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bulletList):
            bulletList.pop(i)
    
    glutPostRedisplay()



def updateEnemyScaling():
    global enemyChngRate, scaleStatus, sTimer, scaleMin, scaleMax, scaleIncrease
    
    sTimer += 1
    if sTimer >= scaleSpan // steps:
        sTimer = 0
        
        for i in range(len(enemyChngRate)):

            newScale = enemyChngRate[i] + (scaleIncrease * scaleStatus)
            

            if newScale > scaleMax:
                newScale = scaleMax
                scaleStatus = -1
            elif newScale < scaleMin:
                newScale = scaleMin
                scaleStatus = 1
                
            enemyChngRate[i] = newScale


def resetGame():
    global playerPos, gunAngle, movAngle, score, bMissed, life
    global bulletList, gameStatus, enemyList, enemyChngRate
    global scaleStatus, sTimer, fpView, cameraPos, cameraRot, cheatMode

 
    playerPos = [0, 0, 0]
    gunAngle = 90
    movAngle = 90
    cameraPos = (0, 500, 500)
    cameraRot = 0
    

    score = 0
    bMissed = 0
    life = 5
    gameStatus = False
    cheatMode = False
    fpView = False
    scaleStatus = 1
    
    bulletList.clear()
    enemyList.clear()
    enemyChngRate.clear()
    
    for i in range(noEnemy):
        while True:
            x = random.randint(-470, 470)
            y = random.randint(-470, 470)
            if abs(x) >= 150 or abs(y) >= 150:
                enemyList.append([x, y, 0])
                enemyChngRate.append(1.0)
                break


def floor_boundary():
    glBegin(GL_QUADS)
    
    border = 600 
    height = 300  
    

    walls = [
        (0.18, 1, 0.204),
        ((0.18, 0.957, 1)),   
        ((0, 0, 1)),          
        ((1, 1, 1))           
    ]
    

    glColor3f(*walls[0])
    glVertex3f(-border,  border, height)
    glVertex3f(-border,  border, 0)
    glVertex3f(-border, -border, 0)
    glVertex3f(-border, -border, height)
    

    glColor3f(*walls[1])
    glVertex3f(-border, -border, height)
    glVertex3f(-border, -border, 0)
    glVertex3f( border, -border, 0)
    glVertex3f( border, -border, height)
    

    glColor3f(*walls[2])
    glVertex3f(border,  border, height)
    glVertex3f(border, -border, height)
    glVertex3f(border, -border, 0)
    glVertex3f(border,  border, 0)
    

    glColor3f(*walls[3])
    glVertex3f(-border, border, height)
    glVertex3f( border, border, height)
    glVertex3f( border, border, 0)
    glVertex3f(-border, border, 0)
    
    glEnd()




def gameField():
    glBegin(GL_QUADS)
    
    square_size = 100
    field_size = 600
    x_start = field_size
    y_start = -field_size
    
    for row in range(12):
        x_pos = x_start
        for col in range(12):
            if (row + col) % 2 == 0:
                glColor3f(1, 1, 1)  
            else:
                glColor3f(0.776, 0.4, 1)  
            
            glVertex3f(x_pos - square_size, y_start + square_size, 0)
            glVertex3f(x_pos, y_start + square_size, 0)
            glVertex3f(x_pos, y_start, 0)
            glVertex3f(x_pos - square_size, y_start, 0)
            
            x_pos -= square_size
        y_start += square_size
    glEnd()



def drawPlayer():
    glPushMatrix()
    glTranslatef(*playerPos)  
    glRotatef(gunAngle, 0, 0, 1)  

    if fpView:
        _draw_gun(color=(0.753, 0.753, 0.753), pos_z=100)
    else:
        _draw_body()
        _draw_head()
        _draw_legs()
        _draw_gun(color=(0.753, 0.753, 0.753), pos_z=100)
        _draw_hands()
    
    glPopMatrix()


def _draw_gun(color, pos_z):
    glColor3f(*color)
    glPushMatrix()
    glTranslatef(0, 0, pos_z)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 12, 7, 80, 10, 10)
    glPopMatrix()


def _draw_body():
    glColor3f(0.333, 0.42, 0.184) 
    glPushMatrix()
    glTranslatef(0, 0, 90)
    glutSolidCube(60) 
    glPopMatrix()


def _draw_head():
    glColor3f(0, 0, 0)  
    glPushMatrix()
    glTranslatef(0, 0, 150)
    gluSphere(gluNewQuadric(), 25, 10, 10)
    glPopMatrix()


def _draw_legs():
    leg_color = (0, 0, 1)  

    glColor3f(*leg_color)
    glPushMatrix()
    glTranslatef(-20, -15, 0)
    gluCylinder(gluNewQuadric(), 7, 12, 60, 10, 10)
    glPopMatrix()

    glColor3f(*leg_color)
    glPushMatrix()
    glTranslatef(-20, 15, 0)
    gluCylinder(gluNewQuadric(), 7, 12, 60, 10, 10)
    glPopMatrix()


def _draw_hands():
    hand_color = (1, 0.878, 0.741)

    glColor3f(*hand_color)
    glPushMatrix()
    glTranslatef(-20, -15, 100)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 6, 30, 10, 10)
    glPopMatrix()

    glColor3f(*hand_color)
    glPushMatrix()
    glTranslatef(-20, 15, 100)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 10, 6, 30, 10, 10)
    glPopMatrix()


def draw_enemies():
    for i, enemy_pos in enumerate(enemyList):
        scale = enemyChngRate[i]
        
        glPushMatrix()
 
        glTranslatef(*enemy_pos)
        glScalef(scale, scale, scale)
        glColor3f(1, 0, 0)
        gluSphere(gluNewQuadric(), 60, 10, 10)
        glColor3f(0, 0, 0)  
        glTranslatef(0, 0, 70) 
        gluSphere(gluNewQuadric(), 30, 10, 10)
        
        glPopMatrix()


def draw_bulletList():
    for bullet in bulletList:
        if not bullet['active']:
            continue
            
        glPushMatrix()

        glTranslatef(*bullet['position'])
        
        if bullet.get('targetLocked', False):
            glColor3f(1, 1, 0) 
        else:
            glColor3f(1, 0, 0)
            
        glutSolidCube(bullet_size)
        glPopMatrix()



def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    cameraSetUp()
    gameField()
    floor_boundary()
    drawPlayer()
    draw_bulletList()
    draw_enemies()

    if not gameStatus:
        _draw_game_stats()
    else:
        _draw_game_over()
    glutSwapBuffers()



def _draw_game_stats():

    y_pos = 770
    draw_text(10, y_pos, f"YOUR Life Remaining : {life}/5")
    y_pos -= 30
    draw_text(10, y_pos, f"YOUR Game Score : {score}")
    y_pos -= 30
    draw_text(10, y_pos, f"Bullets Missed : {bMissed}/{bulletLimit}")
    y_pos -= 30
    draw_text(10, y_pos, f"Cheat Mode : {'ON' if cheatMode else 'OFF'}")
    y_pos -= 30
    draw_text(10, y_pos, f"First Person View : {'ON' if fpView else 'OFF'}")

def _draw_game_over():
    draw_text(10, 770, f"game Over sweetie. Final Score is {score}")
    draw_text(10, 740, "Press '-R-' to RESTART the Game buddy")




glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(1000, 800)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"Bullet Frenzy - A 3D Game with Player Movement, Shooting, & Cheat Modes")

glClearColor(0.0, 0.0, 0.0, 1.0)




glutDisplayFunc(showScreen)
glutKeyboardFunc(keyboardListener)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutIdleFunc(idle)

glutMainLoop()