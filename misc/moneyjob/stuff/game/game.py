import pygame
import random
import sys
import math

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

W, H = 800, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("🚀 Space Defender")
clock = pygame.time.Clock()

# ── Palette ───────────────────────────────────────────────────────────────────
BLACK   = (5,   5,  20)
WHITE   = (255,255,255)
CYAN    = (0,  220,255)
RED     = (255, 60, 60)
GREEN   = (60, 255,100)
YELLOW  = (255,230, 30)
ORANGE  = (255,140, 30)
PURPLE  = (180, 80,255)
GRAY    = (120,120,140)
DGRAY   = ( 40, 40, 55)
LBLUE   = ( 60,130,220)

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_big   = pygame.font.SysFont("consolas", 48, bold=True)
font_med   = pygame.font.SysFont("consolas", 28, bold=True)
font_sm    = pygame.font.SysFont("consolas", 18)

# ── Stars background ──────────────────────────────────────────────────────────
stars = [(random.randint(0,W), random.randint(0,H), random.uniform(0.3,2.0))
         for _ in range(180)]

def draw_stars(surface, offset=0):
    for sx, sy, br in stars:
        sy2 = (sy + offset) % H
        c = int(br * 120)
        r = 1 if br < 1.2 else 2
        pygame.draw.circle(surface, (c, c, min(255, c+30)), (sx, int(sy2)), r)

star_offset = 0

# ── Draw helpers ──────────────────────────────────────────────────────────────
def draw_text(surf, text, font, color, cx, cy, shadow=True):
    if shadow:
        s = font.render(text, True, (0,0,0))
        surf.blit(s, s.get_rect(center=(cx+2, cy+2)))
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))

def draw_ship(surf, x, y, w=40, h=30, color=CYAN, engine=True):
    # Body
    pts = [(x, y-h//2), (x-w//2, y+h//2), (x, y+h//3), (x+w//2, y+h//2)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, WHITE, pts, 1)
    # Cockpit
    pygame.draw.ellipse(surf, LBLUE, (x-7, y-8, 14, 12))
    # Engine glow
    if engine and random.random() > 0.3:
        eg = random.randint(8,18)
        pygame.draw.polygon(surf, ORANGE, [
            (x-8, y+h//2), (x+8, y+h//2), (x, y+h//2+eg)])
        pygame.draw.polygon(surf, YELLOW, [
            (x-4, y+h//2), (x+4, y+h//2), (x, y+h//2+eg//2)])

def draw_enemy(surf, x, y, kind, anim):
    if kind == 0:   # UFO
        pygame.draw.ellipse(surf, RED,    (x-20, y-8,  40, 16))
        pygame.draw.ellipse(surf, ORANGE, (x-10, y-16, 20, 12))
        pygame.draw.ellipse(surf, YELLOW, (x-4,  y-13,  8,  6))
        # pulsing lights
        for i in range(3):
            lx = x - 14 + i*14
            pygame.draw.circle(surf, YELLOW if (anim+i)%4<2 else RED, (lx, y+2), 3)
    elif kind == 1:  # Wedge
        pts = [(x, y+15), (x-18, y-15), (x+18, y-15)]
        pygame.draw.polygon(surf, PURPLE, pts)
        pygame.draw.polygon(surf, WHITE, pts, 1)
        pygame.draw.circle(surf, RED if anim%6<3 else ORANGE, (x, y), 5)
    else:           # Heavy
        pygame.draw.rect(surf, (180,30,30), (x-18, y-18, 36, 36), border_radius=5)
        pygame.draw.rect(surf, RED,         (x-18, y-18, 36, 36), 2, border_radius=5)
        pygame.draw.rect(surf, ORANGE, (x-8, y-8, 16, 16), border_radius=3)
        for dx in (-14, 14):
            pygame.draw.rect(surf, GRAY, (x+dx-4, y-6, 8, 12))

# ── Particles ─────────────────────────────────────────────────────────────────
particles = []

def spawn_explosion(x, y, color=ORANGE, n=20):
    for _ in range(n):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 5)
        particles.append({
            'x': float(x), 'y': float(y),
            'vx': math.cos(angle)*speed, 'vy': math.sin(angle)*speed,
            'life': random.randint(20,45),
            'color': color,
            'r': random.randint(2,5)
        })

def update_particles(surf):
    global particles
    alive = []
    for p in particles:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.12
        p['life'] -= 1
        alpha = max(0, p['life'] / 45)
        c = tuple(int(ch*alpha) for ch in p['color'])
        if 0 <= p['x'] <= W and 0 <= p['y'] <= H:
            pygame.draw.circle(surf, c, (int(p['x']), int(p['y'])), p['r'])
        if p['life'] > 0:
            alive.append(p)
    particles = alive

# ── Floating score texts ───────────────────────────────────────────────────────
floaties = []

def add_floaty(text, x, y, color=YELLOW):
    floaties.append({'text': text, 'x': float(x), 'y': float(y),
                     'life': 55, 'color': color})

def update_floaties(surf):
    global floaties
    alive = []
    for f in floaties:
        f['y'] -= 1.0
        f['life'] -= 1
        alpha = f['life'] / 55
        img = font_sm.render(f['text'], True, f['color'])
        img.set_alpha(int(255*alpha))
        surf.blit(img, img.get_rect(center=(int(f['x']), int(f['y']))))
        if f['life'] > 0:
            alive.append(f)
    floaties = alive

# ── HUD ───────────────────────────────────────────────────────────────────────
def draw_hud(surf, score, hp, max_hp, level, shield):
    # Top bar background
    pygame.draw.rect(surf, DGRAY, (0, 0, W, 50))
    pygame.draw.line(surf, CYAN, (0,50), (W,50), 1)

    # Score
    draw_text(surf, f"SCORE: {score:06d}", font_med, CYAN, 130, 26, shadow=True)

    # Level
    draw_text(surf, f"LVL {level}", font_med, YELLOW, W//2, 26)

    # HP bar
    bar_x, bar_y, bar_w, bar_h = W-220, 12, 180, 26
    pygame.draw.rect(surf, (60,10,10), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    fill = int(bar_w * max(0,hp) / max_hp)
    col  = GREEN if hp/max_hp > 0.5 else YELLOW if hp/max_hp > 0.25 else RED
    if fill > 0:
        pygame.draw.rect(surf, col, (bar_x, bar_y, fill, bar_h), border_radius=4)
    pygame.draw.rect(surf, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)
    draw_text(surf, f"HP {hp}/{max_hp}", font_sm, WHITE, bar_x+bar_w//2, bar_y+13)

    # Shield
    if shield > 0:
        pygame.draw.rect(surf, DGRAY, (0, H-36, W, 36))
        pygame.draw.line(surf, PURPLE, (0, H-36), (W, H-36), 1)
        sw = int(W * shield / 300)
        pygame.draw.rect(surf, PURPLE, (0, H-32, sw, 28), border_radius=3)
        draw_text(surf, "SHIELD", font_sm, WHITE, 50, H-18)

# ── Game state ────────────────────────────────────────────────────────────────
def new_game():
    return {
        'score': 0,
        'hp': 3, 'max_hp': 3,
        'shield': 0,         # frames of invincibility
        'level': 1,
        'wave_timer': 0,
        'ship_x': W//2,
        'ship_speed': 5,
        'bullets': [],        # {x,y}
        'enemies': [],        # {x,y,kind,speed,hp}
        'bonuses': [],        # {x,y,kind}
        'shoot_cd': 0,
        'anim': 0,
        'state': 'play',      # play | dead | win
        'enemy_bullet_cd': 0,
        'enemy_bullets': [],  # {x,y}
    }

g = new_game()

# ── Spawn enemy ───────────────────────────────────────────────────────────────
def spawn_wave(g):
    lvl = g['level']
    n = 3 + lvl * 2
    for _ in range(n):
        kind = random.choices([0,1,2], weights=[5,3,2-(lvl<3)])[0]
        hp   = [1, 2, 3][kind] + (lvl-1)//2
        spd  = random.uniform(0.8+lvl*0.15, 1.5+lvl*0.3)
        x    = random.randint(40, W-40)
        y    = random.randint(-200, -30)
        g['enemies'].append({'x':float(x),'y':float(y),'kind':kind,
                             'speed':spd,'hp':hp,'anim':0})

def maybe_spawn_bonus(x, y):
    if random.random() < 0.18:
        kind = random.choice(['life','pts','shield'])
        bonuses.append({'x':float(x),'y':float(y),'kind':kind,'anim':0})

bonuses = []

def draw_bonus(surf, b):
    x, y = int(b['x']), int(b['y'])
    pulse = abs(math.sin(b['anim']*0.12))*0.4 + 0.6
    r = int(16*pulse)
    if b['kind'] == 'life':
        pygame.draw.circle(surf, (int(60*pulse), int(255*pulse), int(80*pulse)), (x,y), r)
        draw_text(surf, "♥", font_sm, WHITE, x, y)
    elif b['kind'] == 'pts':
        pygame.draw.circle(surf, (int(255*pulse), int(200*pulse), 0), (x,y), r)
        draw_text(surf, "★", font_sm, WHITE, x, y)
    else:
        pygame.draw.circle(surf, (int(120*pulse), int(60*pulse), int(255*pulse)), (x,y), r)
        draw_text(surf, "⛡", font_sm, WHITE, x, y)

# ── Screens ───────────────────────────────────────────────────────────────────
def draw_start(surf, anim):
    surf.fill(BLACK)
    draw_stars(surf, anim*0.3)
    draw_ship(surf, W//2, H//2-60, w=60, h=45, color=CYAN)
    draw_text(surf, "SPACE DEFENDER", font_big, CYAN, W//2, H//2+30)
    draw_text(surf, "← → Move    SPACE Shoot", font_sm, GRAY, W//2, H//2+80)
    blink = (anim//30)%2 == 0
    if blink:
        draw_text(surf, "[ PRESS ENTER TO START ]", font_med, YELLOW, W//2, H//2+120)

def draw_gameover(surf, score, anim):
    surf.fill(BLACK)
    draw_stars(surf, anim*0.2)
    draw_text(surf, "GAME OVER", font_big, RED, W//2, H//2-60)
    draw_text(surf, f"SCORE: {score:06d}", font_med, YELLOW, W//2, H//2)
    blink = (anim//30)%2 == 0
    if blink:
        draw_text(surf, "[ ENTER - Play Again ]", font_med, WHITE, W//2, H//2+60)

# ── Main loop ─────────────────────────────────────────────────────────────────
state = 'start'
anim  = 0

while True:
    dt = clock.tick(60)
    anim += 1
    star_offset = (star_offset + 0.4) % H

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if state == 'start' and event.key == pygame.K_RETURN:
                g = new_game()
                bonuses.clear(); particles.clear(); floaties.clear()
                spawn_wave(g)
                state = 'play'
            elif state == 'dead' and event.key == pygame.K_RETURN:
                g = new_game()
                bonuses.clear(); particles.clear(); floaties.clear()
                spawn_wave(g)
                state = 'play'

    # ── Start / Game-over screens ────────────────────────────────────────────
    if state == 'start':
        draw_start(screen, anim)
        pygame.display.flip(); continue

    if state == 'dead':
        draw_gameover(screen, g['score'], anim)
        update_particles(screen)
        pygame.display.flip(); continue

    # ── PLAY ─────────────────────────────────────────────────────────────────
    keys = pygame.key.get_pressed()

    # Move ship
    sx = g['ship_x']
    if keys[pygame.K_LEFT]  or keys[pygame.K_a]: sx -= g['ship_speed']
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: sx += g['ship_speed']
    g['ship_x'] = max(30, min(W-30, sx))

    # Shoot
    g['shoot_cd'] = max(0, g['shoot_cd']-1)
    if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and g['shoot_cd'] == 0:
        g['bullets'].append({'x': float(g['ship_x']), 'y': float(H-80)})
        g['shoot_cd'] = 18

    # Enemy shoot
    g['enemy_bullet_cd'] = max(0, g['enemy_bullet_cd']-1)
    if g['enemy_bullet_cd'] == 0 and g['enemies']:
        shooter = random.choice(g['enemies'])
        g['enemy_bullets'].append({'x': shooter['x'], 'y': shooter['y']})
        g['enemy_bullet_cd'] = max(30, 90 - g['level']*8)

    # Move bullets
    g['bullets'] = [b for b in g['bullets'] if b['y'] > 0]
    for b in g['bullets']: b['y'] -= 12

    # Move enemy bullets
    g['enemy_bullets'] = [b for b in g['enemy_bullets'] if b['y'] < H]
    for b in g['enemy_bullets']: b['y'] += 5 + g['level']*0.3

    # Move enemies
    for e in g['enemies']:
        e['y'] += e['speed']
        e['anim'] += 1

    # Move bonuses
    for b in bonuses:
        b['y'] += 1.2
        b['anim'] += 1

    # Bullet ↔ enemy collision
    new_bullets, new_enemies = [], []
    hit_set = set()
    for bi, bul in enumerate(g['bullets']):
        hit = False
        for ei, e in enumerate(g['enemies']):
            if ei in hit_set: continue
            if abs(bul['x']-e['x']) < 22 and abs(bul['y']-e['y']) < 22:
                e['hp'] -= 1
                spawn_explosion(e['x'], e['y'],
                    [RED, PURPLE, ORANGE][e['kind']], n=12)
                if e['hp'] <= 0:
                    pts = [100, 200, 350][e['kind']] * g['level']
                    g['score'] += pts
                    add_floaty(f"+{pts}", e['x'], e['y'])
                    maybe_spawn_bonus(e['x'], e['y'])
                    spawn_explosion(e['x'], e['y'],
                        [RED, PURPLE, ORANGE][e['kind']], n=25)
                    hit_set.add(ei)
                hit = True; break
        if not hit:
            new_bullets.append(bul)
    g['bullets'] = new_bullets
    g['enemies']  = [e for i,e in enumerate(g['enemies']) if i not in hit_set]

    # Enemy reaches bottom → damage
    passed = [e for e in g['enemies'] if e['y'] > H-55]
    g['enemies'] = [e for e in g['enemies'] if e['y'] <= H-55]
    for e in passed:
        if g['shield'] == 0:
            g['hp'] -= 1
            spawn_explosion(g['ship_x'], H-80, RED, n=15)
        g['shield'] = max(g['shield'], 0)

    # Enemy bullet ↔ ship
    ship_rect = pygame.Rect(g['ship_x']-20, H-100, 40, 40)
    new_eb = []
    for b in g['enemy_bullets']:
        bRect = pygame.Rect(b['x']-4, b['y']-8, 8, 16)
        if ship_rect.colliderect(bRect) and g['shield'] == 0:
            g['hp'] -= 1
            spawn_explosion(g['ship_x'], H-80, RED, n=12)
        else:
            new_eb.append(b)
    g['enemy_bullets'] = new_eb

    # Shield cooldown
    if g['shield'] > 0: g['shield'] -= 1

    # Bonus ↔ ship
    new_bonuses = []
    for b in bonuses:
        br = pygame.Rect(b['x']-16, b['y']-16, 32, 32)
        if ship_rect.colliderect(br):
            if b['kind'] == 'life':
                g['hp'] = min(g['hp']+1, g['max_hp'])
                add_floaty("♥ +1 HP", b['x'], b['y'], GREEN)
                spawn_explosion(b['x'], b['y'], GREEN, 18)
            elif b['kind'] == 'pts':
                pts = 500 * g['level']
                g['score'] += pts
                add_floaty(f"★ +{pts}", b['x'], b['y'], YELLOW)
                spawn_explosion(b['x'], b['y'], YELLOW, 18)
            else:
                g['shield'] = 300
                add_floaty("⛡ SHIELD!", b['x'], b['y'], PURPLE)
                spawn_explosion(b['x'], b['y'], PURPLE, 18)
        elif b['y'] < H:
            new_bonuses.append(b)
    bonuses = new_bonuses

    # Wave clear → next level
    g['wave_timer'] += 1
    if not g['enemies'] and g['wave_timer'] > 60:
        g['level'] += 1
        g['wave_timer'] = 0
        g['hp'] = min(g['hp']+1, g['max_hp'])
        g['max_hp'] = 3 + (g['level']-1)//2
        add_floaty(f"LEVEL {g['level']}!", W//2, H//2, CYAN)
        spawn_wave(g)

    # Death check
    if g['hp'] <= 0:
        spawn_explosion(g['ship_x'], H-80, RED, n=40)
        state = 'dead'

    # ── DRAW ─────────────────────────────────────────────────────────────────
    screen.fill(BLACK)
    draw_stars(screen, star_offset)

    # Grid glow at bottom
    pygame.draw.rect(screen, (10,30,60), (0, H-60, W, 60))
    pygame.draw.line(screen, LBLUE, (0, H-60), (W, H-60), 1)

    # Enemies
    for e in g['enemies']:
        draw_enemy(screen, int(e['x']), int(e['y']), e['kind'], e['anim'])
        # HP mini-bar
        if e['hp'] > 1:
            bw = 32
            pygame.draw.rect(screen, (80,0,0),  (int(e['x'])-bw//2, int(e['y'])+20, bw, 4))
            fill_hp = int(bw * e['hp'] / ([1,2,3][e['kind']] + (g['level']-1)//2))
            pygame.draw.rect(screen, RED, (int(e['x'])-bw//2, int(e['y'])+20, fill_hp, 4))

    # Bonuses
    for b in bonuses:
        draw_bonus(screen, b)

    # Player bullets
    for b in g['bullets']:
        bx, by = int(b['x']), int(b['y'])
        pygame.draw.rect(screen, CYAN,  (bx-3, by-10, 6, 18), border_radius=3)
        pygame.draw.rect(screen, WHITE, (bx-1, by-10, 2, 10))

    # Enemy bullets
    for b in g['enemy_bullets']:
        bx, by = int(b['x']), int(b['y'])
        pygame.draw.rect(screen, RED,    (bx-3, by-8, 6, 14), border_radius=2)
        pygame.draw.rect(screen, ORANGE, (bx-1, by-6, 2, 8))

    # Ship (with shield effect)
    if g['shield'] > 0:
        sp = math.sin(anim*0.3)*0.4+0.6
        pygame.draw.circle(screen, (int(100*sp),int(50*sp),int(255*sp)),
                           (g['ship_x'], H-80), 35, 3)
    draw_ship(screen, g['ship_x'], H-80)

    # Particles & floaties
    update_particles(screen)
    update_floaties(screen)

    # HUD
    draw_hud(screen, g['score'], g['hp'], g['max_hp'], g['level'], g['shield'])

    pygame.display.flip()