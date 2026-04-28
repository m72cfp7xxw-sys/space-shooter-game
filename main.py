
import pygame
from os.path import join
from random import randint, uniform

#general setup
#initialize pygame
pygame.init()
#visual on the screen
window_width, window_height = 1289, 729
display_surface = pygame.display.set_mode((window_width, window_height))
#change the title of the window
pygame.display.set_caption('Space shooter')
#use a boolean variable to control the game loop
running = True
clock = pygame.time.Clock()

#import
meteor_surf = pygame.image.load(join('meteor1.png')).convert_alpha()
laser_surf = pygame.image.load(join('laser.png')).convert_alpha()
star_surf = pygame.image.load(join('star.png')).convert_alpha()

font = pygame.font.Font(None, 40)

term = 0
gain = 0
blood = 25
start_time = pygame.time.get_ticks()
#control
game_state = 'start'
#restart counter
tendency = 0
#time limit
time_limit = 90

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (window_width / 2, window_height / 2))
        self.direction = pygame.Vector2()
        self.speed = 300
        #cooldown (seconds unit)
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]) #output T or F >> int way 1 or 0
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        self.laser_timer()

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, window_width), randint(0, window_height)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
    #move laser up
    def update(self,dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400,500)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

#sprite collision
def collisions():
    global game_state, gain, term, blood
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True)
    if collision_sprites:
        term += 1
        blood -= 5
        if blood <= 0:
            game_state = 'game over'
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            gain += 5
            blood += 2

#values: term, gain, blood
def display_terms():
    global term, gain, blood
    text_surf1 = font.render(str(term), True, (240, 240, 240))
    text_rect1 = text_surf1.get_frect(midbottom = (window_width /2 -50, window_height - 50))
    display_surface.blit(text_surf1, text_rect1)

    text_surf2 = font.render(str(gain), True, (240, 240, 240))
    text_rect2 = text_surf2.get_frect(midbottom = (window_width /2 -100, window_height -50))
    display_surface.blit(text_surf2, text_rect2)

    text_surf3 = font.render(str(blood), True, 'pink')
    text_rect3 = text_surf3.get_frect(midbottom = (window_width /2 + 50, window_height -50))
    display_surface.blit(text_surf3, text_rect3)

#time limit
def display_score():
    global game_state, term, start_time
    current_time = (pygame.time.get_ticks() - start_time) // 1000
    text_surf = font.render(str(current_time), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom = (window_width / 2, window_height - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,20), 5,10)
    if current_time >= time_limit and game_state == 'playing':
        term += 1
        game_state = 'game over'  

def display_start_screen():
    title_surf = font.render('Space Shooter', True, (240, 240, 240))
    title_rect = title_surf.get_frect(center = (window_width / 2, window_height / 2 - 50))
    display_surface.blit(title_surf, title_rect)
    start_surf = font.render('Press SPACE to Start', True, (200,200,200))
    start_rect = start_surf.get_frect(center = (window_width / 2, window_height / 2 + 50))
    display_surface.blit(start_surf, start_rect)

def display_pause():
    text = font.render('Paused', True, (255, 255, 0))
    text_rect = text.get_frect(center = (window_width / 2, window_height / 2))
    display_surface.blit(text, text_rect)

#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
player = Player(all_sprites)
for i in range(20):
    Star(all_sprites, star_surf)

def display_game_over():
    global tendency
    text_surf = font.render('Game Over', True, (240, 240, 240))
    text_rect = text_surf.get_frect(center = (window_width / 2, window_height / 2 - 30))
    display_surface.blit(text_surf, text_rect)
    #restart remindder
    restart_surf = font.render('Press R to Restart', True, (200,200,200))
    restart_rect = restart_surf.get_frect(center = (window_width / 2, window_height / 2 + 50))
    display_surface.blit(restart_surf, restart_rect) 
    tend_surf = font.render(f'Tendency: {tendency}', True, (240, 240, 240))
    tend_rect = tend_surf.get_frect(center = (window_width / 2, window_height / 2 + 100))
    display_surface.blit(tend_surf, tend_rect)

def reset_game():
    global term, gain, blood, start_time, game_state, tendency
    term = 0
    gain = 0
    blood = 25
    game_state = 'playing'

    tendency += 1

    meteor_sprites.empty()
    laser_sprites.empty()
    player.rect.center = (window_width / 2, window_height / 2)
    start_time = pygame.time.get_ticks()

#custom: meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 1000)

#game loop: make sure to break the game inside loop
#several conditions controlled,end the loop intentially
while running:
    dt = clock.tick() / 1000
    #background
    display_surface.fill('black')

    #increase difficulty by time (in mainloop)
    elapsed = pygame.time.get_ticks() - start_time
    spawn_delay = max(200, 1000 - elapsed // 5)
    # only update occasionally
    if elapsed % 1000 < 20:
        pygame.time.set_timer(meteor_event, spawn_delay)

    #event loop: to close the game
    for event in pygame.event.get():
        #check the type of event
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = randint(0, window_width), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
        if event.type == pygame.KEYDOWN:
            if game_state == 'start' and event.key == pygame.K_SPACE:
                reset_game()
            elif event.key == pygame.K_p and game_state == 'playing':
                game_state = 'paused'
            elif event.key == pygame.K_p and game_state == 'paused':
                game_state = 'playing'
            elif event.key == pygame.K_r and game_state == 'game over':
                game_state = 'playing'
                reset_game()
    
    #update and draw
    if game_state == 'start':
        display_start_screen()
    elif game_state == 'paused':
        all_sprites.draw(display_surface)
        display_pause()
    elif game_state == 'playing':
        all_sprites.update(dt)
        all_sprites.draw(display_surface)
        collisions()
        #display time
        display_score()
        #display term
        display_terms()
    elif game_state == 'game over':
        display_game_over()
   
    pygame.display.update()
    

pygame.quit()