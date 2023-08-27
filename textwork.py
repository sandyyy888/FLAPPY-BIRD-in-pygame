import pygame_textinput
import pygame
pygame.init()

# Create TextInput-object
username_input = pygame_textinput.TextInputVisualizer()

input_screen = pygame.display.set_mode((400, 200))
clock = pygame.time.Clock()

while True:
    input_screen.fill((130, 160, 250))

    events = pygame.event.get()

    # Feed it with events every frame
    username_input.update(events)
    # Blit its surface onto the screen
    input_screen.blit(username_input.surface, (10, 10))

   
    pygame.display.update()
    clock.tick(30)