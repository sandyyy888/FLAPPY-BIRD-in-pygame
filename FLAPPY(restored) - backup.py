import pygame
import sys
import time
import random
import mysql.connector

pygame.init()
pygame.font.init()
scr_width,scr_height = 400 , 800
screen = pygame.display.set_mode((scr_width,scr_height))
pygame.display.set_caption('Flappy Bird')
#icon image
icon = pygame.image.load('assets/favicon.ico').convert()
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
current_time = 0
db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'admin',
    )
cur = db.cursor(buffered = True)
#VARIABLES
FPS = 120
WHITE = (255,255,255)
RED = ( 255,20,20)
GREEN = ( 20,255,20)
BLACK = (0,0,0)
bgcolor = ( 130, 185, 235)
gravity = 0.1
bird_movement = 0
birdpos_x = 175
birdpos_y = 325
clicked = False
base_x_pos = 0
bg_x_pos = 0
game_active = True
pipe_list = []
pass_pipe = False
pipe_height = [250,300,350,400,450,500]
time_bw_pipes = 2350
score = 0
input_rect_colour = (255,255,255)
user_name_given = False
score_inserted = False
new_user = True
oldUID = None
total_games = 0
total_score = 0
table_printed = False


#ASSETS
background = pygame.image.load('assets/background-day.png').convert()
background = pygame.transform.scale(background,(400,800))

bird = pygame.image.load('assets/yellowbird-midflap.png').convert_alpha()
bird = pygame.transform.scale(bird, (70,50))

bird_rect = bird.get_rect(center= (birdpos_x,birdpos_y))

base = pygame.image.load('assets/base.png').convert_alpha()
base = pygame.transform.scale(base,(400,125))

message  = pygame.image.load("assets/message.png").convert_alpha()
message = pygame.transform.scale(message,(250,320))

game_over = pygame.image.load("assets/gameover.png").convert_alpha()
game_over = pygame.transform.scale(game_over,(330,80))

pipe_surface = pygame.image.load("assets/pipe-green.png").convert_alpha()
pipe_surface = pygame.transform.smoothscale_by(pipe_surface,1.5)

credits_font = pygame.font.Font(None, 25)
#credits_font = pygame.freetype.Font('assets/game_font.ttf', 25)
GAME_FONT_SMALL = pygame.freetype.Font("assets/game_font.ttf", 20)
GAME_FONT_BIG = pygame.freetype.Font("assets/game_font.ttf", 40 )
GAME_FONT_MEDIUM = pygame.freetype.Font("assets/game_font.ttf", 30)

input_field_font = pygame.font.Font( None,32)
input_rect = pygame.Rect(100,200,200,32)

#mysql init
users = "CREATE TABLE IF NOT EXISTS users (UID INTEGER PRIMARY KEY AUTO_INCREMENT , username VARCHAR(50) NOT NULL , last_score integer , high_score integer , average_score integer);"


cur.execute('CREATE DATABASE IF NOT EXISTS flappydata;')
cur.execute('USE flappydata')
cur.execute(users)

db.commit()


#SQL DATA FETCHING

def get_last_inserted_id():
    cur.execute('SELECT LAST_INSERT_ID();')
    result = cur.fetchone()
    return result[0] if result else None  

def user_exists(username):
    #query = "SELECT UID FROM users WHERE username = %s"
    query = "SELECT * FROM users WHERE username = %s"
    cur.execute(query, (username,))
    result = cur.fetchone()
    #print(cur.fetchone())
    return result[0] if result else None 

def get_high_score(username):
    user_id = user_exists(username)
    if user_id is not None:
        cur.execute("SELECT high_score FROM users WHERE UID = %s", (user_id,))
        high_score = cur.fetchone()
        return high_score[0] if (high_score and high_score[0] is not None) else 0
    else:
        return 0

def update_high_score(username, score):
    user_id = user_exists(username)
    if user_id is not None:
        current_high_score = get_high_score(username)
        if score > current_high_score:
            sql_query = "UPDATE users SET high_score = %s WHERE UID = %s"
            cur.execute(sql_query, (score, user_id))
            db.commit()

def update_user_scores(username, score):
    global user_id
    user_id = user_exists(username)
    if user_id is not None:
        # User already exists, update the scores
        current_high_score = get_high_score(username)
        if score > current_high_score:
            # Update high score
            cur.execute("UPDATE users SET high_score = %s WHERE UID = %s", (score, user_id))
            db.commit()
        
        # Update average score
        cur.execute("SELECT average_score FROM users WHERE UID = %s", (user_id,))
        result = cur.fetchone()
        current_average_score =  result[0]
        new_average_score = (current_average_score + score) / 2
        cur.execute("UPDATE users SET average_score = %s WHERE UID = %s",
                    (new_average_score, user_id))
        # Update last score
        cur.execute("UPDATE users SET last_score = %s WHERE UID = %s", (score, user_id))
        
        db.commit()
    else:
        # User does not exist, create a new record
        cur.execute("INSERT INTO users (username, high_score, average_score, last_score) VALUES (%s, %s, %s, %s)",
                    (username, score, score, score))
        db.commit()
 
#display functions

def welcome_screen():
    screen.fill((0, 0, 0))
    global user_text
    global oldUID
    global NewID
    user_text = ''
    text_surface = input_field_font.render(user_text , True , (255,255,255) )
    


    paused = True
    while paused:
        user_input_text = input_field_font.render(user_text , False , (255,255,255) )
        pygame.draw.rect(screen , input_rect_colour, input_rect , 1 )
        screen.blit(user_input_text, ((input_rect.x + 5 , input_rect.y + 5)))
        text_surface = input_field_font.render("Enter Username",False, (255, 255, 255))
        screen.blit(text_surface, (100,170))
        credits_surface = credits_font.render("Developed By Bhupendra", False, (255, 255, 255))
        screen.blit(credits_surface, (180, 760))
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()        
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = False       

                elif event.key == pygame.K_DELETE:
                    pygame.quit()
                    quit()                  
                if event.type == pygame.KEYDOWN:
                    user_text += event.unicode

                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-2:1]
                    print(user_text)

                if event.key == pygame.K_RETURN:
                    text_surface= input_field_font.render("PRESS SPACE TO START",False, (255, 255, 255))
                    screen.blit(text_surface, (65,470))
                    print ( 'username entered:', user_text )

                    if user_exists(user_text) == None:
                        new_user = True
                        print('New user')
                        cur.execute("INSERT INTO users (username, high_score, average_score) VALUES('{}',0,0)".format( usertext))
                        NewID = get_last_inserted_id()
                        

                        cur.execute('SELECT * FROM USERS WHERE UID = {};'.format(NewID))
                        a = cur.fetchone()
                        print(a)
                        #oldUID = NewID
                        print(oldUID)   
                        db.commit()  

                        user_text = ''
                        
                    else:
                        oldUID = user_exists(user_text)
                        print(oldUID)
                        print('User already exists')

                        
                     
                         
        pygame.display.flip()
    pygame.display.update()

#PAUSING GAME
def pause():


    paused = True
    while paused:
        pause_text1, rect = GAME_FONT_BIG.render("GAME PAUSED", (0, 0, 0))
        pause_text2, rect = GAME_FONT_SMALL.render("press [SPACE] to continue", (0, 0, 0))      
        pause_text3, rect = GAME_FONT_SMALL.render("press [DELETE] to quit", (0, 0, 0)) 
        screen.blit(pause_text1, (75, 250))
        screen.blit(pause_text2, (50, 400))
        screen.blit(pause_text3, (65, 460))
        pygame.display.flip()

        
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()        
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = False       

                elif event.key == pygame.K_DELETE:
                    pygame.quit()
                    quit()
                       

#MAKING PIPES
def create_pipe():
    random_pipe_pos = random.choice(pipe_height)
    top_pipe = pipe_surface.get_rect(midbottom =(600,random_pipe_pos - 90))
    bottom_pipe = pipe_surface.get_rect(midtop =(600,random_pipe_pos + 120))
    return bottom_pipe , top_pipe

spawnpipe = pygame.USEREVENT
pygame.time.set_timer(spawnpipe,time_bw_pipes)

#PIPE MOVEMENT

def pipe_movement (pipes):
    for pipe in pipes:
        pipe.centerx -= 2
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 600:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.rotate(pipe_surface,180)
            screen.blit(flip_pipe, pipe)



#FLOOR & BG MOVEMENT
def floor():
    screen.blit(base,(base_x_pos,675))
    screen.blit(base,(base_x_pos + 400,675))


def bg():
    screen.blit(background,(bg_x_pos,0))
    screen.blit(background,(bg_x_pos + 400,0))


#RESET LOGIC
def reset_game():
    global bird_movement, bird_rect, base_x_pos, bg_x_pos, pipe_list, game_active, score, score_inserted
    bird_movement = 0
    bird_rect.center = (birdpos_x, birdpos_y)
    base_x_pos = 0
    bg_x_pos = 0
    pipe_list = []
    game_active = True
    score = 0
    score_inserted = False
    if user_text:  # Check if a username is available
        score_to_store = int(score_counter())
        update_user_scores(user_text, score_to_store)
    
    
    #COLLISION LOGIC
def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe) or bird_rect.bottom >= 675 or bird_rect.top <= - 100:
            return False
    return True

#SCORE COUNTER 
def score_counter():
    score = 0
    score = (len(pipe_list)/2)-1
    return (score)

    

#DISPLAY LOGIC
run = True
welcome_screen()
while run:
    clock.tick(FPS)
    

    #EVENT HANDLERS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                clicked = True
                bird_movement = 0
                bird_movement -= 5
            if event.key == pygame.K_SPACE and game_active == False:
                bird_movement = 0
                bird_rect.center = (birdpos_x,birdpos_y)
                game_active = True
                pipe_list.clear()
            if event.key == pygame.K_ESCAPE and game_active:
                pause() 
        if event.type == spawnpipe and game_active == True:
            pipe_list.extend(create_pipe())
            #print(pipe_list)

        game_active = check_collision(pipe_list)

    #scene movement logic
    if game_active == True:

        base_x_pos -= 2
        bg_x_pos -= 0.25
    else:
        base_x_pos -= 0
        bg_x_pos -= 0.0
    bg()
    if bg_x_pos <= -400:
        bg_x_pos = 0

    #floor() 
    
    if base_x_pos <= -400:
        base_x_pos = 0

#EVENT HANDLERS CONT


    if game_active:
        bird_movement += gravity    
        bird_rect.centery += bird_movement
        screen.blit(bird, bird_rect)
        text_surface, rect = GAME_FONT_MEDIUM.render("Score:", (0, 0, 0))
        screen.blit(text_surface, (220, 50))
        
        
        score_to_display = str(int(score_counter()))
        text_surface,rect = GAME_FONT_MEDIUM.render(score_to_display, (0, 0, 0))
              
        screen.blit(text_surface, (330, 50))
        

        game_active = check_collision(pipe_list) 
        p_list = pipe_movement(pipe_list)
        draw_pipes(p_list)
        floor()   

    else:
        
        screen.blit(game_over, (40, 150))
        text_surface, rect = GAME_FONT_MEDIUM.render("Score:", (0,0,0))
        screen.blit(text_surface, (120, 400))
        text_surface,rect = GAME_FONT_MEDIUM.render(score_to_display, (0,0,0))    
        screen.blit(text_surface, (250, 400))
        cur.execute('select * from users')
        #SCORE DETERMINATION
        prev_average_score = cur.execute('SELECT average_score from users where UID = %s',(oldUID,))
        x = cur.fetchone()[0]
        score_to_store = int(score_counter())
        average_score = (score_to_store + x)/2

        if score_inserted == False:

            update_user_scores(user_text, int(score_counter()))
        
            score_inserted = True

        high_score = str(get_high_score(user_text))
        
        text_surface, rect = GAME_FONT_SMALL.render("High Score:", (0, 0, 0))
        screen.blit(text_surface, (20, 650))

        text_surface, rect = GAME_FONT_SMALL.render(high_score, (0, 0, 0))
        screen.blit(text_surface, (245, 652))   


        cur.execute('SELECT average_score from users where UID = %s', (user_id,))
        result = cur.fetchone()
        average_score = result[0] if (result and result[0] is not None) else 0
        text_surface, rect = GAME_FONT_SMALL.render("Average Score:", (0, 0, 0))
        screen.blit(text_surface, (20, 700))
        text_surface, rect = GAME_FONT_SMALL.render(str(average_score), (0, 0, 0))
        screen.blit(text_surface, (245, 702))

        text_surface, rect = GAME_FONT_SMALL.render("press [SPACE] to play again", (0, 0, 0))
        screen.blit(text_surface, (40, 275))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active == False:
                    reset_game()
                elif event.key == pygame.K_ESCAPE and game_active == False :
                    pygame.quit()
                    break
                elif event.key == pygame.K_DELETE and game_active == False :
                    pygame.quit()
                    break
        if table_printed == False:
            cur.execute("select * from users;")
            
            for i in cur:
                print(i)
        pygame.display.flip()
        table_printed = True
        
    pygame.display.update()
    
pygame.quit()


