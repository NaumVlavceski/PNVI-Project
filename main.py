# -*- coding: utf-8 -*-
import pygame
import random
import sys
import math
import os

ICON_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")

# ================= CONFIG =================
WIDTH, HEIGHT = 900, 600
FPS = 60

# Colors (soft & kid-friendly)
BG = (245, 247, 250)
GRID_COLOR = (230, 233, 237)
WHITE = (255, 255, 255)
BLACK = (40, 40, 40)
GREEN = (46, 204, 113)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
PURPLE = (155, 89, 182)
ORANGE = (243, 156, 18)
YELLOW = (241, 196, 15)
GRAY = (149, 165, 166)
LIGHT_BLUE = (173, 216, 230)

# Gradients
GRADIENT_BLUE = [(52, 152, 219), (41, 128, 185)]
GRADIENT_PURPLE = [(155, 89, 182), (142, 68, 173)]
GRADIENT_GREEN = [(46, 204, 113), (39, 174, 96)]
GRADIENT_ORANGE = [(243, 156, 18), (230, 126, 34)]

PAD_W, PAD_H = 16, 120
BALL_R = 12

# ================= QUESTIONS =================
QUESTIONS = [
    ("Добиваш порака од непознат човек што бара да му пратиш слика.", False,
     "Не праќај слики на непознати. Кажи му на родител или наставник."),

    ("На интернет користиш надимак (никнејм) наместо вистинско име.", True,
     "Подобро е да не ги откриваш личните податоци јавно."),

    ("Кликаш на линк што вели: „Освои iPhone, само внеси податоци!“", False,
     "Ова често е измама. Не внесувај податоци и не кликај на сомнителни линкови."),

    ("Го прашуваш родителот пред да инсталираш нова игра/апликација.", True,
     "Возрасните можат да проверат дали е безбедна и соодветна."),

    ("Му даваш лозинка на другар за да ти го среди профилот.", False,
     "Лозинките се лични. Дури ни другари не треба да ги знаат."),

    ("Користиш силна лозинка (подолга и со букви/броеви) и ја чуваш тајна.", True,
     "Силна лозинка го штити профилот од хакирање."),

    ("Објавуваш домашна адреса или број на телефон на социјални мрежи.", False,
     "Тоа се приватни информации и може да биде опасно."),

    ("Ако некој те навредува онлајн, го пријавуваш и блокираш.", True,
     "Блокирање и пријавување е најбезбедно. Не се расправај."),

    ("Отвораш прилог (attachment) од непознат мејл.", False,
     "Може да има вирус или измама. Прво прашај возрасен."),

    ("Пред да внесеш лозинка, проверуваш дали страницата е вистинска.", True,
     "Лажни страници изгледаат слично, но крадат лозинки."),
]

# ================= INIT =================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Safe Internet Pong")
clock = pygame.time.Clock()

# Load fonts (with fallback)
try:
    title_font = pygame.font.Font(None, 72)
    big_font = pygame.font.Font(None, 48)
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    tiny_font = pygame.font.Font(None, 24)
except:
    # Fallback to default
    title_font = pygame.font.SysFont('Arial', 72)
    big_font = pygame.font.SysFont('Arial', 48)
    font = pygame.font.SysFont('Arial', 36)
    small_font = pygame.font.SysFont('Arial', 28)
    tiny_font = pygame.font.SysFont('Arial', 24)


# Load icons
def load_icon(filename, size):
    """Load a PNG icon (with alpha) and scale it."""
    try:
        path = os.path.join(ICON_DIR, filename)
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except:
        # Create a placeholder if icon is missing
        print(f"Warning: Could not load icon {filename}")
        placeholder = pygame.Surface(size, pygame.SRCALPHA)
        placeholder.fill((255, 0, 255, 128))  # Magenta placeholder
        return placeholder


icons = {
    "gamepad": load_icon("gamepad.png", (56, 56)),
    "star": load_icon("star.png", (26, 26)),
    "trophy": load_icon("trophy.png", (24, 24)),
    "heart": load_icon("heart.png", (24, 24)),
    "pause": load_icon("pause.png", (48, 48)),
    "question": load_icon("question.png", (48, 48)),
    "check": load_icon("check.png", (22, 22)),
    "cross": load_icon("cross.png", (22, 22)),
    "warning": load_icon("warning.png", (48, 48)) if os.path.exists(os.path.join(ICON_DIR, "warning.png")) else None,
    "book": load_icon("book.png", (48, 48)) if os.path.exists(os.path.join(ICON_DIR, "book.png")) else None,
    "smile": load_icon("smile.png", (30, 30)) if os.path.exists(os.path.join(ICON_DIR, "smile.png")) else None,
}

# ================= STATES =================
START, GAME, QUIZ, PAUSE, GAME_OVER, EXTRA_CHANCE, INSTRUCTIONS = "start", "game", "quiz", "pause", "game_over", "extra_chance", "instructions"
state = START

# ================= GAME VARS =================
p1_y = HEIGHT // 2 - PAD_H // 2
p2_y = p1_y
p1_speed = 0
p2_speed = 0

ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 5, 5

score = 0
high_score = 0
lives = 3
quiz_question = None
extra_chance_questions = []
current_extra_question = 0
extra_chance_correct = 0
particles = []
effects = []
pulse_time = 0

# ====== STREAK / BONUS QUIZ ======
BONUS_RALLY = 5          # колку удари треба за бонус прашање
rally_hits = 0           # тековна серија
quiz_mode = "goal"       # "goal" или "bonus"


# ====== GAMEPLAY MODIFIERS (power-ups / penalties) ======
BASE_PAD_H = PAD_H

p1_h = BASE_PAD_H
p2_h = BASE_PAD_H

ball_speed_factor = 1.0  # множител за брзина на топчето (1.0 = нормално)

buff = None    # пример: {"type":"big_paddle", "end": <ms>}
debuff = None  # пример: {"type":"fast_ball", "end": <ms>}
shield = False # ако е True -> еднаш те спасува од гол


# ================= UI ELEMENTS =================
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface):
        color = self.color
        if self.hover:
            # Make color slightly brighter on hover
            color = tuple(min(255, c + 20) for c in self.color)

        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=20)

        # Draw main button
        pygame.draw.rect(surface, color, self.rect, border_radius=20)

        # Draw border
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=20)

        # Draw text
        draw_text(self.text, self.rect.centerx, self.rect.centery, font, WHITE)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# Create buttons
start_button = Button(WIDTH // 2 - 100, 350, 200, 70, "ПОЧНИ", GREEN)
instructions_button = Button(WIDTH // 2 - 100, 440, 200, 70, "ИНСТРУКЦИИ", BLUE)
restart_button = Button(WIDTH // 2 - 100, 350, 200, 70, "НОВА ИГРА", GREEN)
continue_button = Button(WIDTH // 2 - 100, 350, 200, 70, "ПРОДОЛЖИ", BLUE)
quit_button = Button(WIDTH // 2 - 100, 440, 200, 70, "ИЗЛЕЗИ", RED)
back_button = Button(WIDTH // 2 - 100, 500, 200, 70, "НАЗАД", PURPLE)
yes_button = Button(250, 450, 180, 60, "ДА!", GREEN)
no_button = Button(470, 450, 180, 60, "НЕ", RED)
true_button = Button(200, 380, 220, 70, "БЕЗБЕДНО", GREEN)
false_button = Button(480, 380, 220, 70, "НЕ БЕЗБЕДНО", RED)
next_question_button = Button(WIDTH // 2 - 100, 450, 200, 60, "СЛЕДНО ПРАШАЊЕ", BLUE)


# ================= HELPERS =================
def draw_gradient_rect(surface, rect, colors):
    """Draw a vertical gradient rectangle"""
    top_color, bottom_color = colors
    for i in range(rect.height):
        ratio = i / rect.height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surface, (r, g, b),
                         (rect.x, rect.y + i),
                         (rect.x + rect.width, rect.y + i))


def draw_text(text, x, y, font_obj, color=BLACK, center=True, shadow=False):
    if shadow:
        shadow_img = font_obj.render(text, True, (0, 0, 0, 100))
        shadow_rect = shadow_img.get_rect(center=(x + 2, y + 2) if center else (x + 2, y + 2))
        screen.blit(shadow_img, shadow_rect)

    img = font_obj.render(text, True, color)
    rect = img.get_rect(center=(x, y) if center else (x, y))
    screen.blit(img, rect)


def draw_icon_text(icon_surf, text, center_x, center_y, font_obj, text_color=BLACK, gap=10, shadow=False):
    """Draw [icon][text] as one centered row."""
    txt = font_obj.render(text, True, text_color)
    iw, ih = icon_surf.get_size()
    tw, th = txt.get_size()
    total_w = iw + gap + tw

    left_x = center_x - total_w // 2
    icon_pos = (left_x, center_y - ih // 2)
    text_pos = (left_x + iw + gap, center_y - th // 2)

    if shadow:
        shadow_s = pygame.Surface((total_w, max(ih, th)), pygame.SRCALPHA)
        shadow_s.fill((0, 0, 0, 100))
        screen.blit(shadow_s, (left_x + 2, center_y - max(ih, th) // 2 + 2))

    screen.blit(icon_surf, icon_pos)
    screen.blit(txt, text_pos)


def create_particles(x, y, color, count=10):
    for _ in range(count):
        particles.append({
            'x': x,
            'y': y,
            'vx': random.uniform(-3, 3),
            'vy': random.uniform(-3, 3),
            'color': color,
            'life': 30
        })


def create_effect(x, y, text, color):
    effects.append({
        'x': x,
        'y': y,
        'text': text,
        'color': color,
        'life': 60,
        'vy': -2
    })


def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx = random.choice([-5, 5])
    ball_dy = random.uniform(-4, 4)

def _now_ms():
    return pygame.time.get_ticks()

def grant_powerup():
    """Give a random gameplay bonus on correct answer."""
    global buff, shield
    now = _now_ms()

    kind = random.choice(["big_paddle", "slow_ball", "shield"])

    if kind == "big_paddle":
        buff = {"type": "big_paddle", "end": now + 10000}  # 10s
        create_effect(WIDTH // 2, HEIGHT // 2+50, "POWER-UP: ГОЛЕМА ПАНДАЛКА!", GREEN)

    elif kind == "slow_ball":
        buff = {"type": "slow_ball", "end": now + 6000}    # 6s
        create_effect(WIDTH // 2, HEIGHT // 2+50, "POWER-UP: УСПОРЕНО ТОПЧЕ!", BLUE)

    elif kind == "shield":
        shield = True
        create_effect(WIDTH // 2, HEIGHT // 2+50, "POWER-UP: ШТИТ (1x)!", PURPLE)

def apply_penalty():
    """Apply a random gameplay penalty on wrong answer."""
    global debuff
    now = _now_ms()

    kind = random.choice(["small_paddle", "fast_ball"])

    if kind == "small_paddle":
        debuff = {"type": "small_paddle", "end": now + 6000}  # 6s
        create_effect(WIDTH // 2, HEIGHT // 2-50, "КАЗНА: МАЛА ПАНДАЛКА!", RED)

    elif kind == "fast_ball":
        debuff = {"type": "fast_ball", "end": now + 6000}     # 6s
        create_effect(WIDTH // 2, HEIGHT // 2-50, "КАЗНА: БРЗО ТОПЧЕ!", ORANGE)

def update_modifiers():
    """Update timers and compute current paddle height + ball speed factor."""
    global buff, debuff, p1_h, p2_h, ball_speed_factor, p1_y, p2_y

    now = _now_ms()
    if buff and now >= buff["end"]:
        buff = None
    if debuff and now >= debuff["end"]:
        debuff = None

    # Compute current modifiers
    paddle_scale = 1.0
    ball_factor = 1.0

    if buff:
        if buff["type"] == "big_paddle":
            paddle_scale *= 1.4
        elif buff["type"] == "slow_ball":
            ball_factor *= 0.7

    if debuff:
        if debuff["type"] == "small_paddle":
            paddle_scale *= 0.7
        elif debuff["type"] == "fast_ball":
            ball_factor *= 1.25

    p1_h = int(BASE_PAD_H * paddle_scale)
    p2_h = BASE_PAD_H
    ball_speed_factor = ball_factor

    # keep paddles inside screen if their size changed
    p1_y = max(0, min(HEIGHT - p1_h, p1_y))
    p2_y = max(0, min(HEIGHT - p2_h, p2_y))

def draw_modifiers_hud():
    """Small HUD text for active effects."""
    now = _now_ms()
    x = WIDTH - 50
    y = 25

    if shield:
        draw_text("ШТИТ: 1x", x, y, tiny_font, PURPLE, center=False)
        y += 22

    if buff:
        secs = max(0, (buff["end"] - now) // 1000)
        label = "BUFF"
        if buff["type"] == "big_paddle":
            label = "ГОЛЕМА ПАНДАЛКА"
        elif buff["type"] == "slow_ball":
            label = "УСПОРЕНО ТОПЧЕ"
        draw_text(f"{label}: {secs}s", x, y, tiny_font, GREEN, center=False)
        y += 22

    if debuff:
        secs = max(0, (debuff["end"] - now) // 1000)
        label = "КАЗНА"
        if debuff["type"] == "small_paddle":
            label = "МАЛА ПАНДАЛКА"
        elif debuff["type"] == "fast_ball":
            label = "БРЗО ТОПЧЕ"
        draw_text(f"{label}: {secs}s", x, y, tiny_font, RED, center=False)



def start_quiz():
    global quiz_question, state, quiz_mode, rally_hits
    quiz_question = random.choice(QUESTIONS)
    quiz_mode = "goal"
    rally_hits = 0
    state = QUIZ


def start_bonus_quiz():
    global quiz_question, state, quiz_mode, rally_hits
    quiz_question = random.choice(QUESTIONS)
    quiz_mode = "bonus"
    rally_hits = 0
    create_effect(WIDTH // 2, HEIGHT // 2, "БОНУС ПРАШАЊЕ!", ORANGE)
    state = QUIZ



def start_extra_chance():
    global extra_chance_questions, current_extra_question, extra_chance_correct, state
    # Избере 3 случајни прашања
    extra_chance_questions = random.sample(QUESTIONS, 3)
    current_extra_question = 0
    extra_chance_correct = 0
    state = EXTRA_CHANCE


def check_extra_chance_answer(answer):
    global current_extra_question, extra_chance_correct, state, lives, score

    correct = extra_chance_questions[current_extra_question][1]

    if answer == correct:
        extra_chance_correct += 1
        create_effect(WIDTH // 2, HEIGHT // 2, "ТОЧНО! ", GREEN)
    else:
        create_effect(WIDTH // 2, HEIGHT // 2, "ГРЕШКА! ", RED)

    current_extra_question += 1

    if current_extra_question >= len(extra_chance_questions):
        # Сите прашања одговорени
        if extra_chance_correct == len(extra_chance_questions):
            # Сите точни - добива дополнителен живот
            lives = 1
            score = max(0, score - 100)  # Малку казна за загуба
            reset_ball()
            state = GAME
            create_effect(WIDTH // 2, HEIGHT // 2, "БРАВО! Доби дополнителен живот! ", GREEN)
            pygame.time.wait(1000)  # Кратка пауза за ефектот
        else:
            # Не успеал - играта завршува
            state = GAME_OVER


def draw_score():
    # Score background
    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 120, 10, 240, 60), border_radius=15)
    pygame.draw.rect(screen, BLUE, (WIDTH // 2 - 120, 10, 240, 60), 3, border_radius=15)

    # Score text with star icon
    screen.blit(icons["star"], (WIDTH // 2 - 100, 18))
    draw_text(f"ПОЕНИ: {score}", WIDTH // 2 + 20, 25, font, BLUE, shadow=True)

    # High score with trophy icon
    screen.blit(icons["trophy"], (WIDTH // 2 - 100, 45))
    draw_text(f"РЕКОРД: {high_score}", WIDTH // 2 + 25, 55, small_font, PURPLE)

    # Lives with heart icons
    for i in range(lives):
        screen.blit(icons["heart"], (20 + i * 34, 22))

    draw_modifiers_hud()
    draw_text(f"СЕРИЈА: {rally_hits}/{BONUS_RALLY}", WIDTH // 2, 85, small_font, ORANGE)


# ================= MAIN LOOP =================
running = True
while running:
    clock.tick(FPS)
    screen.fill(BG)
    mouse_pos = pygame.mouse.get_pos()
    pulse_time += 1

    # Draw background pattern
    for x in range(0, WIDTH, 40):
        for y in range(0, HEIGHT, 40):
            if (x // 40 + y // 40) % 2 == 0:
                pygame.draw.circle(screen, GRID_COLOR, (x, y), 1)

    # Animated center line
    for i in range(0, HEIGHT, 30):
        offset = (pulse_time // 2) % 30
        alpha = abs(math.sin((i + offset) * 0.1))
        color = (200, 200, 255, int(alpha * 150))
        pygame.draw.line(screen, color, (WIDTH // 2, i - offset),
                         (WIDTH // 2, i + 15 - offset), 3)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if state == GAME:
                    state = PAUSE
                elif state == PAUSE:
                    state = GAME
                elif state == INSTRUCTIONS:
                    state = START
                else:
                    running = False
            elif e.key == pygame.K_p and state == GAME:
                state = PAUSE
            elif e.key == pygame.K_SPACE and state == PAUSE:
                state = GAME

        # START SCREEN CLICK
        if state == START and e.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(e.pos):
                state = GAME
                score = 0
                lives = 3
                reset_ball()
            elif instructions_button.is_clicked(e.pos):
                state = INSTRUCTIONS

        # INSTRUCTIONS SCREEN CLICK
        elif state == INSTRUCTIONS and e.type == pygame.MOUSEBUTTONDOWN:
            if back_button.is_clicked(e.pos):
                state = START

        # GAME OVER SCREEN CLICK
        elif state == GAME_OVER and e.type == pygame.MOUSEBUTTONDOWN:
            if restart_button.is_clicked(e.pos):
                state = GAME
                score = 0
                lives = 3
                reset_ball()
            elif quit_button.is_clicked(e.pos):
                running = False

        # PAUSE SCREEN CLICK
        elif state == PAUSE and e.type == pygame.MOUSEBUTTONDOWN:
            if continue_button.is_clicked(e.pos):
                state = GAME
            elif quit_button.is_clicked(e.pos):
                running = False

        # EXTRA CHANCE QUESTION SCREEN CLICK
        elif state == EXTRA_CHANCE and e.type == pygame.MOUSEBUTTONDOWN:
            if true_button.is_clicked(e.pos):
                check_extra_chance_answer(True)
                pygame.display.flip()
                pygame.time.wait(500)  # Кратка пауза за ефектот
            elif false_button.is_clicked(e.pos):
                check_extra_chance_answer(False)
                pygame.display.flip()
                pygame.time.wait(500)  # Кратка пауза за ефектот

        # EXTRA CHANCE OFFER SCREEN CLICK (when game over)
        elif state == "extra_chance_offer" and e.type == pygame.MOUSEBUTTONDOWN:
            if yes_button.is_clicked(e.pos):
                start_extra_chance()
            elif no_button.is_clicked(e.pos):
                state = GAME_OVER

        # QUIZ CLICK (normal during game)
        elif state == QUIZ and e.type == pygame.MOUSEBUTTONDOWN:
            correct = quiz_question[1]

            picked = None
            if true_button.is_clicked(e.pos):
                picked = True
            elif false_button.is_clicked(e.pos):
                picked = False

            if picked is not None:
                if picked == correct:
                    # BONUS прашање дава повеќе поени
                    gained = 150 if quiz_mode == "bonus" else 100
                    score += gained
                    create_effect(WIDTH // 2, HEIGHT // 2, f"+{gained}!", GREEN)
                    grant_powerup()
                else:
                    # BONUS прашање: помала казна (поблага)
                    loss = 20 if quiz_mode == "bonus" else 50
                    score = max(0, score - loss)
                    create_effect(WIDTH // 2, HEIGHT // 2, f"-{loss}!", RED)
                    apply_penalty()

                reset_ball()
                state = GAME

    # Update button hover states
    if state == START:
        start_button.check_hover(mouse_pos)
        instructions_button.check_hover(mouse_pos)
    elif state == INSTRUCTIONS:
        back_button.check_hover(mouse_pos)
    elif state == GAME_OVER:
        restart_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
    elif state == PAUSE:
        continue_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
    elif state == EXTRA_CHANCE:
        true_button.check_hover(mouse_pos)
        false_button.check_hover(mouse_pos)
    elif state == "extra_chance_offer":
        yes_button.check_hover(mouse_pos)
        no_button.check_hover(mouse_pos)
    elif state == QUIZ:
        true_button.check_hover(mouse_pos)
        false_button.check_hover(mouse_pos)

    # ================= INSTRUCTIONS SCREEN =================
    if state == INSTRUCTIONS:
        # Instructions background
        pygame.draw.rect(screen, WHITE, (50, 50, WIDTH - 100, HEIGHT - 100), border_radius=30)
        pygame.draw.rect(screen, BLUE, (50, 50, WIDTH - 100, HEIGHT - 100), 5, border_radius=30)

        # Draw book icon if available, otherwise use text
        if icons.get("book"):
            screen.blit(icons["book"], (WIDTH // 2 - 180, 75))
        draw_text("ИНСТРУКЦИИ ЗА ИГРАТА", WIDTH // 2, 100, title_font, BLUE, shadow=True)

        # Instructions content box
        pygame.draw.rect(screen, (240, 245, 255), (80, 150, 740, 320), border_radius=15)
        pygame.draw.rect(screen, LIGHT_BLUE, (80, 150, 740, 320), 3, border_radius=15)

        # Instructions text
        if icons.get("gamepad"):
            screen.blit(icons["gamepad"], (WIDTH // 2 - 220, 170))
        draw_text("КАКО СЕ ИГРА?", WIDTH // 2, 180, big_font, PURPLE)
        draw_text("• Користи ги копчињата W и S за да ја движиш левата пандалка", WIDTH // 2, 220, small_font)
        draw_text("• Топчето не смее да ти помине покрај пандалката", WIDTH // 2, 250, small_font)
        draw_text("• При секој гол што го примиш, мораш да одговориш на прашање", WIDTH // 2, 280, small_font)

        draw_text("ПРАШАЊА ЗА БЕЗБЕДНОСТ", WIDTH // 2, 320, big_font, PURPLE)
        draw_icon_text(icons["check"], "Точно одговорено: +100 поени", WIDTH // 2, 360, small_font, GREEN)
        draw_icon_text(icons["cross"], "Погрешно одговорено: -50 поени", WIDTH // 2, 390, small_font, RED)

        draw_text("ДОПОЛНИТЕЛНА ШАНСА", WIDTH // 2, 430, big_font, PURPLE)
        if icons.get("warning"):
            screen.blit(icons["warning"], (WIDTH // 2 - 220, 445))
        draw_text("• Ако ги изгубиш сите животи, добиваш шанса за дополнителен живот", WIDTH // 2, 460, small_font)

        # Back button
        back_button.draw(screen)

        # Footer
        draw_text("Притисни ESC за да се вратиш назад", WIDTH // 2, 590, tiny_font, GRAY)

        pygame.display.flip()
        continue

    # ================= START SCREEN =================
    if state == START:
        # Animated title
        title_y = 100 + math.sin(pulse_time * 0.05) * 5

        # Draw gamepad icon
        screen.blit(icons["gamepad"], (WIDTH // 2 -30, int(title_y) - 80))
        draw_text("SAFE INTERNET PONG", WIDTH // 2, int(title_y), title_font, PURPLE, shadow=True)

        # Draw smile icon if available
        if icons.get("smile"):
            screen.blit(icons["smile"], (WIDTH // 2 - 180, 170))
        draw_text("Играј и учи како да бидеш безбеден онлајн", WIDTH // 2, 180, font, BLUE)

        # Instructions box
        pygame.draw.rect(screen, WHITE, (100, 220, 700, 100), border_radius=20)
        pygame.draw.rect(screen, BLUE, (100, 220, 700, 100), 3, border_radius=20)

        draw_icon_text(icons["gamepad"], "Кога ќе примиш гол одговори прашање", WIDTH // 2, 250, font)
        draw_icon_text(icons["check"], "Точно: +100 поени | ", WIDTH // 2 -130, 290, font, GREEN)
        draw_icon_text(icons["cross"], "Грешно: -50 поени", WIDTH // 2 + 150, 290, font, RED)

        # Buttons
        start_button.draw(screen)
        instructions_button.draw(screen)

        # Footer
        draw_text("Притисни ESC за излез", WIDTH // 2, 530, small_font, GRAY)

        pygame.display.flip()
        continue

    # ================= QUIZ =================
    elif state == QUIZ:
        # Quiz background
        pygame.draw.rect(screen, WHITE, (50, 50, WIDTH - 100, HEIGHT - 100), border_radius=30)
        pygame.draw.rect(screen, PURPLE, (50, 50, WIDTH - 100, HEIGHT - 100), 5, border_radius=30)

        # Draw question icon
        screen.blit(icons["question"], (WIDTH // 2 -20, 50))
        draw_text("ПРАШАЊЕ ЗА БЕЗБЕДНОСТ", WIDTH // 2, 120, title_font, BLUE, shadow=True)

        # Question box
        pygame.draw.rect(screen, (240, 240, 250), (100, 180, 700, 120), border_radius=15)
        pygame.draw.rect(screen, BLUE, (100, 180, 700, 120), 3, border_radius=15)

        draw_text(quiz_question[0], WIDTH // 2, 240, small_font, BLACK)

        # Buttons
        true_button.draw(screen)
        false_button.draw(screen)

        # Hint
        draw_text("Избери дали мислиш дека тврдењето е безбедно или не",
                  WIDTH // 2, 480, small_font, GRAY)

        pygame.display.flip()
        continue

    # ================= EXTRA CHANCE SCREEN =================
    elif state == EXTRA_CHANCE:
        # Quiz background
        pygame.draw.rect(screen, WHITE, (50, 50, WIDTH - 100, HEIGHT - 100), border_radius=30)
        pygame.draw.rect(screen, ORANGE, (50, 50, WIDTH - 100, HEIGHT - 100), 5, border_radius=30)

        # Draw warning icon if available
        if icons.get("warning"):
            screen.blit(icons["warning"], (WIDTH // 2 - 180, 75))
        draw_text(f"ДОПОЛНИТЕЛНА ШАНСА ({current_extra_question + 1}/3)", WIDTH // 2, 120, title_font, ORANGE,
                  shadow=True)

        # Progress bar
        progress_width = 600
        progress_filled = (current_extra_question / 3) * progress_width
        pygame.draw.rect(screen, GRAY, (WIDTH // 2 - progress_width // 2, 160, progress_width, 20), border_radius=10)
        pygame.draw.rect(screen, GREEN, (WIDTH // 2 - progress_width // 2, 160, progress_filled, 20), border_radius=10)

        # Correct answers counter
        if current_extra_question > 0:
            draw_text(f"Точни одговори: {extra_chance_correct}/{current_extra_question}", WIDTH // 2, 190, small_font,
                      BLUE)
        else:
            draw_text("Започни со првото прашање", WIDTH // 2, 190, small_font, BLUE)

        question = extra_chance_questions[current_extra_question]

        # Question box
        pygame.draw.rect(screen, (255, 250, 240), (100, 220, 700, 120), border_radius=15)
        pygame.draw.rect(screen, ORANGE, (100, 220, 700, 120), 3, border_radius=15)

        draw_text(question[0], WIDTH // 2, 280, small_font, BLACK)

        # Buttons
        true_button.draw(screen)
        false_button.draw(screen)

        # Instructions
        draw_text("Одговори точно на сите 3 прашања за да добиеш дополнителен живот!",
                  WIDTH // 2, 480, small_font, ORANGE)

        pygame.display.flip()
        continue

    # ================= EXTRA CHANCE OFFER SCREEN =================
    elif state == "extra_chance_offer":
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Offer box
        pygame.draw.rect(screen, WHITE, (100, 150, 700, 350), border_radius=30)
        pygame.draw.rect(screen, YELLOW, (100, 150, 700, 350), 5, border_radius=30)

        # Draw warning icon
        if icons.get("warning"):
            screen.blit(icons["warning"], (WIDTH // 2 - 24, 170))
        draw_text("ГИ ИЗГУБИ СИТЕ ЖИВОТИ!", WIDTH // 2, 230, title_font, ORANGE, shadow=True)

        # Score with star icon
        draw_icon_text(icons["star"], f"Твојот резултат: {score} поени", WIDTH // 2, 280, big_font, BLUE)

        draw_text("Сакаш да пробаш дополнителна шанса?", WIDTH // 2, 330, font, BLACK)

        # Rules box
        pygame.draw.rect(screen, (255, 250, 240), (150, 360, 600, 80), border_radius=10)
        pygame.draw.rect(screen, YELLOW, (150, 360, 600, 80), 2, border_radius=10)
        draw_text("Одговори точно на 3 прашања и добиваш дополнителен живот!",
                  WIDTH // 2, 380, tiny_font, ORANGE)
        draw_text("Ако згрешиш на било кое прашање, играта завршува.",
                  WIDTH // 2, 400, tiny_font, ORANGE)

        # Buttons
        yes_button.draw(screen)
        no_button.draw(screen)

        pygame.display.flip()
        continue

    # ================= PAUSE SCREEN =================
    elif state == PAUSE:
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Draw pause icon
        screen.blit(icons["pause"], (WIDTH // 2 - 24, 105))
        draw_text("ПАУЗИРАНО", WIDTH // 2, 175, title_font, WHITE, shadow=True)

        # Score with star icon
        draw_icon_text(icons["star"], f"ТЕКОВНИ ПОЕНИ: {score}", WIDTH // 2, 220, big_font, YELLOW)

        # High score with trophy icon
        draw_icon_text(icons["trophy"], f"РЕКОРД: {high_score}", WIDTH // 2, 270, font, WHITE)

        continue_button.draw(screen)
        quit_button.draw(screen)

        draw_text("Притисни SPACE или кликни 'ПРОДОЛЖИ' за да продолжиш",
                  WIDTH // 2, 530, small_font, WHITE)

        pygame.display.flip()
        continue

    # ================= GAME OVER SCREEN =================
    elif state == GAME_OVER:
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Game over box
        pygame.draw.rect(screen, WHITE, (100, 150, 700, 300), border_radius=30)
        pygame.draw.rect(screen, RED, (100, 150, 700, 300), 5, border_radius=30)

        draw_text("ИГРАТА ЗАВРШИ!", WIDTH // 2, 200, title_font, RED, shadow=True)

        # Final score with star icon
        draw_icon_text(icons["star"], f"КОНАЧЕН РЕЗУЛТАТ: {score} поени", WIDTH // 2, 260, big_font, PURPLE)

        if score > high_score:
            draw_text("НОВ РЕКОРД!", WIDTH // 2, 310, font, YELLOW)
            high_score = score

        restart_button.draw(screen)
        quit_button.draw(screen)

        draw_text("Започни нова игра или излези", WIDTH // 2, 580, small_font, GRAY)

        pygame.display.flip()
        continue

    # ================= GAME =================
    # Update high score
    if score > high_score:
        high_score = score

    # Draw score and lives
    draw_score()

    update_modifiers()


    # Player controls
    keys = pygame.key.get_pressed()
    p1_speed = 0
    if keys[pygame.K_w] and p1_y > 0:
        p1_speed = -7
    if keys[pygame.K_s] and p1_y < HEIGHT - p1_h:
        p1_speed = 7

    # AI with slight randomness
    ai_speed = 5 + score // 500  # AI gets faster as score increases
    if ball_y > p2_y + p2_h // 2 + random.randint(-10, 10):
        p2_speed = ai_speed
    elif ball_y < p2_y + p2_h // 2 + random.randint(-10, 10):
        p2_speed = -ai_speed
    else:
        p2_speed = 0

    # Update positions
    p1_y += p1_speed
    p2_y += p2_speed

    # Keep paddles on screen
    p1_y = max(0, min(HEIGHT - p1_h, p1_y))
    p2_y = max(0, min(HEIGHT - p2_h, p2_y))


    # Ball movement
    ball_x += ball_dx * ball_speed_factor
    ball_y += ball_dy * ball_speed_factor


    # Wall collision with visual effect
    if ball_y <= BALL_R:
        ball_dy = abs(ball_dy)
        create_particles(ball_x, ball_y, BLUE)
    elif ball_y >= HEIGHT - BALL_R:
        ball_dy = -abs(ball_dy)
        create_particles(ball_x, ball_y, BLUE)

    # Paddle collision
    if ball_x <= PAD_W + BALL_R:
        if p1_y < ball_y < p1_y + p1_h:
            ball_dx = abs(ball_dx) * 1.1
            ball_dy += p1_speed * 0.3
            create_particles(ball_x, ball_y, BLUE)

            rally_hits += 1
            if rally_hits >= BONUS_RALLY:
                start_bonus_quiz()

    elif ball_x >= WIDTH - PAD_W - BALL_R:
        if p2_y < ball_y < p2_y + p2_h:
            ball_dx = -abs(ball_dx) * 1.05
            ball_dy += p2_speed * 0.3
            create_particles(ball_x, ball_y, ORANGE)

    # Score point for AI
    if ball_x <= 0:
        if shield:
            shield = False
            reset_ball()
            create_effect(WIDTH // 2, HEIGHT // 2, "ШТИТ ТЕ СПАСИ!", PURPLE)
        else:
            rally_hits = 0
            lives -= 1
            if lives <= 0:
                state = "extra_chance_offer"
            else:
                start_quiz()

    # Score point for player
    if ball_x >= WIDTH:
        score += 10
        rally_hits = 0
        reset_ball()
        create_effect(WIDTH // 2, HEIGHT // 2, "+10!", GREEN)

    # Update particles
    for particle in particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['life'] -= 1

        if particle['life'] > 0:
            alpha = particle['life'] / 30 * 255
            pygame.draw.circle(screen, particle['color'] + (int(alpha),),
                               (int(particle['x']), int(particle['y'])),
                               particle['life'] // 10)
        else:
            particles.remove(particle)

    # Update effects
    for effect in effects[:]:
        effect['y'] += effect['vy']
        effect['life'] -= 1

        if effect['life'] > 0:
            alpha = min(255, effect['life'] * 4)
            draw_text(effect['text'], effect['x'], effect['y'], font,
                      effect['color'] + (alpha,), center=True)
        else:
            effects.remove(effect)

    # Draw paddles with gradient
    draw_gradient_rect(screen, pygame.Rect(0, p1_y, PAD_W, p1_h), GRADIENT_BLUE)
    draw_gradient_rect(screen, pygame.Rect(WIDTH - PAD_W, p2_y, PAD_W, p2_h), GRADIENT_ORANGE)


    # Draw ball with shine effect
    pygame.draw.circle(screen, PURPLE, (int(ball_x), int(ball_y)), BALL_R)
    pygame.draw.circle(screen, WHITE, (int(ball_x) - 4, int(ball_y) - 4), 3)

    # Draw controls hint
    draw_text("W/S - Движи пандалка | P - Пауза | ESC - Излез",
              WIDTH // 2, HEIGHT - 30, small_font, GRAY)

    pygame.display.flip()

pygame.quit()
sys.exit()