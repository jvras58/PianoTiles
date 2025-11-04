import json
import random
import pygame
from threading import Thread

from config.objects import Tile, Square, Text, Button, Counter

pygame.init()
SCREEN = WIDTH, HEIGHT = 288, 512
TILE_WIDTH = WIDTH // 4
TILE_HEIGHT = 130

info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
else:
    win = pygame.display.set_mode(
        SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN
    )

clock = pygame.time.Clock()
FPS = 30

# COLORS *********************************************************************

WHITE = (255, 255, 255)
GRAY = (75, 75, 75)
BLUE = (30, 144, 255)

# IMAGES *********************************************************************

bg_img = pygame.image.load("config/Assets/bg.png")
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

piano_img = pygame.image.load("config/Assets/piano.png")
piano_img = pygame.transform.scale(piano_img, (212, 212))

title_img = pygame.image.load("config/Assets/title.png")
title_img = pygame.transform.scale(title_img, (200, 50))

start_img = pygame.image.load("config/Assets/start.png")
start_img = pygame.transform.scale(start_img, (120, 40))
start_rect = start_img.get_rect(center=(WIDTH // 2, HEIGHT - 80))

overlay = pygame.image.load("config/Assets/red overlay.png")
overlay = pygame.transform.scale(overlay, (WIDTH, HEIGHT))

# MUSIC **********************************************************************

buzzer_fx = pygame.mixer.Sound("config/Sounds/piano-buzzer.mp3")

pygame.mixer.music.load("config/Sounds/piano-bgmusic.mp3")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(loops=-1)

# FONTS **********************************************************************

score_font = pygame.font.Font("config/Fonts/Futura condensed.ttf", 32)
title_font = pygame.font.Font("config/Fonts/Alternity-8w7J.ttf", 30)
gameover_font = pygame.font.Font("config/Fonts/Alternity-8w7J.ttf", 40)

title_img = title_font.render("Piano Tiles", True, WHITE)

# BUTTONS ********************************************************************

close_img = pygame.image.load("config/Assets/closeBtn.png")
replay_img = pygame.image.load("config/Assets/replay.png")
sound_off_img = pygame.image.load("config/Assets/soundOffBtn.png")
sound_on_img = pygame.image.load("config/Assets/soundOnBtn.png")

close_btn = Button(close_img, (24, 24), WIDTH // 4 - 18, HEIGHT // 2 + 120)
replay_btn = Button(replay_img, (36, 36), WIDTH // 2 - 18, HEIGHT // 2 + 115)
sound_btn = Button(sound_on_img, (24, 24), WIDTH - WIDTH // 4 - 18, HEIGHT // 2 + 120)

# GROUPS & OBJECTS ***********************************************************

tile_group = pygame.sprite.Group()
square_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()

time_counter = Counter(win, gameover_font)

# FUNCTIONS ******************************************************************


def get_speed(score):
    return 200 + 5 * score


def play_notes(notePath):
    pygame.mixer.Sound(notePath).play()


def calculate_spawn_time(target_time, speed_factor):
    """
    Calcula quando um tile deve aparecer para que chegue na zona de clique no momento certo.
    target_time: tempo (ms) quando a nota deve ser tocada
    speed_factor: velocidade atual do jogo
    """
    # Tempo que leva para o tile percorrer a tela
    travel_time = (HEIGHT / speed_factor) * (1000 / FPS) if speed_factor > 0 else 3000
    return target_time - travel_time


def initialize_song(song_id):
    """Inicializa os tempos de spawn das notas para uma música."""
    global note_spawn_times, current_note_index
    
    notes_list = notes_dict[song_id]
    timing = timing_dict[song_id]
    note_interval = timing['note_interval']
    
    note_spawn_times = []
    current_time = 3000  # Começa após 3 segundos (após contagem regressiva)
    
    for i, note in enumerate(notes_list):
        note_spawn_times.append({
            'note': note,
            'target_time': current_time,
            'spawned': False
        })
        current_time += note_interval
    
    current_note_index = 0
    return notes_list


# NOTES **********************************************************************

with open("config/notes.json") as file:
    notes_data = json.load(file)
    # Compatibilidade com formato antigo
    if 'notes' in notes_data:
        notes_dict = notes_data['notes']
        timing_dict = notes_data['timing']
    else:
        notes_dict = notes_data
        # Timing padrão se não existir
        timing_dict = {str(i): {'bpm': 120, 'note_interval': 500} for i in range(1, 6)}

# VARIABLES ******************************************************************

score = 0
high_score = 0
speed = 0

clicked = False
pos = None

home_page = True
game_page = False
game_over = False
sound_on = True

count = 0
overlay_index = 0

# Variáveis para sincronização musical
game_start_time = 0
note_spawn_times = []  # Lista de tempos quando cada nota deve aparecer
current_note_index = 0
selected_song = "5"  # Música selecionada (Naruto theme)

running = True
while running:
    pos = None

    count += 1
    if count % 100 == 0:
        square = Square(win)
        square_group.add(square)
        counter = 0

    win.blit(bg_img, (0, 0))
    square_group.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            pos = event.pos

    if home_page:
        win.blit(piano_img, (WIDTH // 8, HEIGHT // 8))
        win.blit(start_img, start_rect)
        win.blit(title_img, (WIDTH // 2 - title_img.get_width() / 2 + 10, 300))

        if pos and start_rect.collidepoint(pos):
            home_page = False
            game_page = True
            
            # Inicializar música e sincronização
            notes_list = initialize_song(selected_song)
            note_count = 0
            pygame.mixer.set_num_channels(len(notes_list))
            
            game_start_time = 0  # Será definido após a contagem regressiva

            pos = None

    if game_page:
        time_counter.update()
        
        # Iniciar o jogo após contagem regressiva
        if time_counter.count <= 0 and game_start_time == 0:
            game_start_time = pygame.time.get_ticks()
        
        if time_counter.count <= 0:
            current_time = pygame.time.get_ticks() - game_start_time
            
            # Spawnar tiles baseado no tempo musical
            speed = int(get_speed(score) * (FPS / 1000))
            
            for note_data in note_spawn_times:
                if not note_data['spawned']:
                    spawn_time = calculate_spawn_time(note_data['target_time'], speed if speed > 0 else 5)
                    
                    if current_time >= spawn_time:
                        x = random.randint(0, 3)
                        t = Tile(x * TILE_WIDTH, -TILE_HEIGHT, win, 
                                note_data['note'], note_data['target_time'])
                        tile_group.add(t)
                        note_data['spawned'] = True
            
            for tile in tile_group:
                tile.update(speed)

                if pos:
                    if tile.rect.collidepoint(pos):
                        if tile.alive:
                            # Calcular diferença de tempo (janela de acerto)
                            time_diff = abs(current_time - tile.target_time)
                            
                            # Janela de tolerância: 200ms = perfeito, 400ms = bom, 600ms = ok
                            if time_diff <= 600:
                                tile.alive = False
                                
                                # Pontuação baseada na precisão
                                if time_diff <= 200:
                                    points = 3
                                    feedback = "PERFECT!"
                                elif time_diff <= 400:
                                    points = 2
                                    feedback = "GOOD!"
                                else:
                                    points = 1
                                    feedback = "OK"
                                
                                score += points
                                if score >= high_score:
                                    high_score = score

                                # Tocar a nota
                                if not tile.played and tile.note:
                                    note = tile.note.strip()
                                    th = Thread(
                                        target=play_notes, args=(f"config/Sounds/{note}.ogg",)
                                    )
                                    th.start()
                                    tile.played = True

                                tpos = tile.rect.centerx - 10, tile.rect.y
                                text = Text(f"+{points}", score_font, tpos, win)
                                text_group.add(text)

                        pos = None

                if tile.rect.bottom >= HEIGHT and tile.alive:
                    if not game_over:
                        tile.color = (255, 0, 0)
                        buzzer_fx.play()
                        game_over = True

            if pos:
                buzzer_fx.play()
                game_over = True

            text_group.update(speed)
            img1 = score_font.render(f"Score : {score}", True, WHITE)
            win.blit(img1, (70 - img1.get_width() / 2, 10))
            img2 = score_font.render(f"High : {high_score}", True, WHITE)
            win.blit(img2, (200 - img2.get_width() / 2, 10))
            for i in range(4):
                pygame.draw.line(
                    win, WHITE, (TILE_WIDTH * i, 0), (TILE_WIDTH * i, HEIGHT), 1
                )

            if game_over:
                speed = 0

                if overlay_index > 20:
                    win.blit(overlay, (0, 0))

                    img1 = gameover_font.render("Game over", True, WHITE)
                    img2 = score_font.render(f"Score : {score}", True, WHITE)
                    win.blit(img1, (WIDTH // 2 - img1.get_width() / 2, 180))
                    win.blit(img2, (WIDTH // 2 - img2.get_width() / 2, 250))

                    if close_btn.draw(win):
                        running = False

                    if replay_btn.draw(win):
                        # Reiniciar jogo
                        notes_list = initialize_song(selected_song)
                        note_count = 0
                        pygame.mixer.set_num_channels(len(notes_list))

                        text_group.empty()
                        tile_group.empty()
                        score = 0
                        speed = 0
                        overlay_index = 0
                        game_over = False
                        game_start_time = 0

                        time_counter = Counter(win, gameover_font)

                    if sound_btn.draw(win):
                        sound_on = not sound_on

                        if sound_on:
                            sound_btn.update_image(sound_on_img)
                            pygame.mixer.music.play(loops=-1)
                        else:
                            sound_btn.update_image(sound_off_img)
                            pygame.mixer.music.stop()
                else:
                    overlay_index += 1
                    if overlay_index % 3 == 0:
                        win.blit(overlay, (0, 0))

    pygame.draw.rect(win, BLUE, (0, 0, WIDTH, HEIGHT), 2)
    clock.tick(FPS)
    pygame.display.update()

pygame.quit()
