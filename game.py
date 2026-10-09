from pygame import *
from random import *
import sounddevice as sd
import numpy as np

sr = 16000
block = 256
mic_level = 0.0

def audio_cb(indata, frames, time, status):
    global mic_level
    if status:
        return
    rms = float(np.sqrt(np.mean(indata**2)))
    mic_level = 0.85 * mic_level + 0.15 * rms

init()

window_size = 1000, 600
window = display.set_mode(window_size)
clock = time.Clock()

player_rect = Rect(150, window_size[1] // 2 - 100, 80, 80)
pipe_speed = 10
main_font = font.Font(None, 100)
score = 0
lose = False
y_vel = 0.0

wait = 40
gravity = 0.5
shum = 0.001
impulse = -5
freeze_timer = 5

def generate_pipes(count, pipe_width=140, gap=280, min_height=50,
                   max_height=440, distance=650):
    pipes = []
    start_x = window_size[0]
    for i in range(count):
        height = randint(min_height, max_height)
        top_pipe = Rect(start_x, 0, pipe_width, height)
        bottom_pipe = Rect(start_x, height + gap, pipe_width,
                           window_size[1] - (height + gap))
        pipes.extend([top_pipe, bottom_pipe])
        start_x += distance
    return pipes

pies = generate_pipes(150)

with sd.InputStream(samplerate=sr, channels=1, blocksize=block, callback=audio_cb):
    while True:
        for e in event.get():
            if e.type == QUIT:
                quit()
        window.fill("lightblue")
        draw.rect(window, "red", player_rect)

        if mic_level > shum:
            y_vel = impulse
        y_vel += gravity
        player_rect.y += int(y_vel)

        for pie in pies[:]:
            if not lose:
                pie.x -= pipe_speed
            draw.rect(window, "green", pie)
            if pie.x <= -100:
                pies.remove(pie)
                score += 0.5

            if player_rect.colliderect(pie):
                if player_rect.centerx > pie.centerx:
                    player_rect.left = pie.right + 5
                else:
                    lose = True

        if len(pies) < 8:
            pies += generate_pipes(150)

        score_text = main_font.render(f"{int(score)}", 1, "black")
        center_text = window_size[0] // 2 - score_text.get_rect().w // 2
        window.blit(score_text, (center_text, 40))

        keys = key.get_pressed()
        if keys[K_r] and lose:
            lose = False
            score = 0
            pipes = generate_pipes(150)
            player_rect.y = window_size[1]//2-100
            y_vel = 0.0

        if player_rect.bottom > window_size[1]:
            player_rect.bottom = window_size[1]
            y_vel = 0.0
        if player_rect.top < 0:
            player_rect.top = 0
            if y_vel < 0:
                y_vel = 0.0

        if lose:
            if freeze_timer > 0:
                freeze_timer -= 1
            elif wait > 1:
                for pie in pies:
                    pie.x += 8
                wait -= 1
            else:
                lose = False
                wait = 40
                freeze_timer = 5

        display.update()
        clock.tick(60)