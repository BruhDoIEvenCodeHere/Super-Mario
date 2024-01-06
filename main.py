print("HELLO WORLD")
import turtle
import sys, os
import pygame
from pygame.locals import QUIT, KEYUP

pygame.init()

sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()
enemies = pygame.sprite.Group()

#hello world :D

screenWidth = 500
screenHeight = 500
screen = pygame.display.set_mode((screenWidth, screenHeight))

meteorStrike = list()
lastFrame = 0
frameDelay = 100

dir = "meteorStrike"

for fileName in os.listdir(dir):
  image = os.path.join(dir, fileName)
  meteorStrike.append(pygame.image.load(image))

brickImage = pygame.image.load("abcdefghijklmnopqrstuvwxyz.png")
freakinGoomba = pygame.image.load("freakinGoomba.png")
koopa = pygame.image.load("koopaTroopaYouAreDead.png")
koopaShell = pygame.image.load("koopaTroopaShellYouAreDead.png")

class Block(pygame.sprite.Sprite):
    size = (screenWidth // 10, screenHeight // 10)
    def __init__(self, img, pos):
        super().__init__(sprites, blocks)
        self.image = pygame.transform.scale(img, Block.size)
        self.pos = pos
        self.rect = self.image.get_rect(center = self.pos)
    def draw(self):
      self.rect = self.image.get_rect(center = self.pos)
      screen.blit(self.image, self.rect)
    def update(self):
      self.draw()
      
class Player(pygame.sprite.Sprite):
  def __init__(self, pos):
    super().__init__(sprites)
    self.state = "idle"
    self.currFrame = 0
    self.lastFrame = 0
    self.pos = pos
    self.moveSpeed = 5
    self.isFacingRight = True
    self.dy = 0
    self.accY = 0
    self.size = tuple(dim * 2 for dim in Block.size)
    self.image = pygame.transform.scale(meteorStrike[self.currFrame], self.size)
    self.rect = self.image.get_rect(center = self.pos)
    self.onGround = False
  def move(self):
    self.dy += self.accY
    if K[LEFT]:
      self.pos.x -= self.moveSpeed
      self.isFacingRight = False
    if K[RIGHT]:
      self.pos.x += self.moveSpeed
      self.isFacingRight = True
    if K[JUMP] and self.onGround:
      self.dy = -15
    self.pos.y += self.dy
  def collision(self):
    self.onGround = False
    self.accY = 1
    for block in blocks:
        if pygame.sprite.collide_mask(self, block):
          self.onGround = True
          self.accY = 0
          self.pos.y = block.rect.top - (Block.size[0] + 10)
    for enemy in enemies:
      if self.rect.colliderect(enemy.rectBody) and currTime > 1000:
        self.kill()
  def animate(self):
    if K[LEFT] or K[RIGHT]:
      if self.lastFrame < currTime - frameDelay:
        self.lastFrame = currTime
        self.currFrame = self.currFrame + 1 if self.currFrame < len(meteorStrike) - 1 else 0
  def draw(self):
    self.rect.scale_by_ip(0.50, 0.50)
    #pygame.draw.rect(screen, white, self.rect) 
    self.image = pygame.transform.scale(meteorStrike[self.currFrame], self.size)
    self.rect = self.image.get_rect(center = self.pos)
    flippedImage = pygame.transform.flip(self.image, True, False)
    if self.isFacingRight:
      screen.blit(self.image, self.rect)
    else:
      screen.blit(flippedImage, self.rect)
  def update(self):
    self.collision()
    self.move()
    self.animate()
    self.draw()

class Enemy(pygame.sprite.Sprite):
  def __init__(self, name, pos, headScale, headPos, bodyScale, bodyPos, image, imageScale):
    super().__init__(sprites, enemies)
    self.size = tuple(dim * imageScale for dim in Block.size)
    self.image = image
    self.pos = pos
    self.name = name
    self.rect = self.image.get_rect(center = pos)
    self.dY = 0
    self.accY = 0
    self.onGround = False
    self.debug = False
    self.headScale = headScale
    self.headPos = headPos
    self.bodyScale = bodyScale
    self.bodyPos = bodyPos
    self.head = EnemyHead(self.pos, self.size, self)
    self.rectBody = self.rect.copy()
  def move(self):
    if self.dY != 38:
      self.dY += self.accY
    self.pos.y += self.dY
    if self.onGround:
      self.pos.x -= 0.5
  def draw(self):
    self.image = pygame.transform.scale(self.image, self.size)
    self.rect = self.image.get_rect(center = self.pos)
    self.rectBody = self.rect.copy()
    self.rectBody.scale_by_ip(self.bodyScale[0], self.bodyScale[1]) #0.1, 0.1
    self.rectBody.move_ip(self.bodyPos[0], self.bodyPos[1]) #0, 0
    if self.debug:
      pygame.draw.rect(screen, white, self.rectBody) 
    screen.blit(self.image, self.rect)
  def falling(self):
    self.accY = 1
    for block in blocks:
      if pygame.sprite.collide_mask(self, block):
        self.accY = 0
        self.pos.y = block.rect.top - (Block.size[0] + 10)
        self.onGround = True
  def update(self):
    self.head.pos = self.pos.copy() + self.headPos
    self.falling()
    self.move()
    self.draw()

class EnemyHead(pygame.sprite.Sprite):
  def __init__(self, pos, size, parent):
    super().__init__(sprites)
    self.parent = parent 
    self.pos = pos
    self.size = size
    self.rect = pygame.Rect(self.pos, self.size)
  def draw(self):
    self.rect = pygame.Rect(self.pos, self.size)
    #self.rect.scale_by_ip(0.1, 0.25)
    self.rect.scale_by_ip(self.parent.headScale[0], self.parent.headScale[1])
    if self.parent.debug:
      pygame.draw.rect(screen, white, self.rect) 
  def collision(self):
      if player.rect.colliderect(self.rect):
        self.parent.kill()
        self.kill()
        player.dy = -15
        shellSize = 10
        Shell(self.pos, V(0,0), 1)
        
  def update(self):
    self.draw()
    self.collision()

class Shell(pygame.sprite.Sprite):
  def __init__(self, pos, offset, imageScale):
    super().__init__(sprites)
    self.pos = pos + offset
    self.size = tuple(dim * imageScale for dim in Block.size)
    self.image = koopaShell
    self.rect = self.image.get_rect(center = self.pos)
  def draw(self):
    self.image = pygame.transform.scale(self.image, self.size)
    self.rect = self.image.get_rect(center = self.pos)
    screen.blit(self.image, self.rect)
  def update(self):
    self.draw()

LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_UP

black = (0, 0, 0)
white = (255, 255, 255)

V = pygame.Vector2
startPosition = V(screenWidth // 3 * 1, screenHeight // 2)
player = Player(startPosition)

for i in range(10):
  if i == 7:
      for j in range(7):
        Block(brickImage, V(i * 50 + 25, screenHeight - 25 - j * 50))
  else:
      for j in range(2):
        Block(brickImage, V(i * 50 + 25, screenHeight - 25 - j * 50))

Enemy("Koopa", V(screenWidth // 3 * 2, 0), (0.1, 0.1),V(-50, -75), (0.3, 0.1), (0, 0), koopa, 2)
#Enemy(V(screenWidth // 3 * 2 + 50, 0), V(-25, -40), (0.1, 0.1), (0, 0),freakinGoomba, 1)
#Enemy(V(screenWidth // 3 * 2 + 100, 0), V(-25, -40), )

while True:
  pygame.time.Clock().tick(60)
  screen.fill(black)
  currTime = pygame.time.get_ticks()
  K = pygame.key.get_pressed()
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      sys.exit()
  sprites.update()
  pygame.display.update()