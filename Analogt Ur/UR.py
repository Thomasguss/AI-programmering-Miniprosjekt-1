import pygame
import math
from datetime import datetime
import os

pygame.init()
screen_size = (700, 700)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Vinyl-klokke")
clock = pygame.time.Clock()

home_center = (350, 350)
clock_radius = 300  # ytre sirkel


def safe_load_image(filename):
    if not os.path.exists(filename):
        print(f"Image file not found: {filename}")
        return pygame.Surface((1, 1), pygame.SRCALPHA)
    return pygame.image.load(filename).convert_alpha()

def make_vinyl_fit_circle(img_surf, radius, pad=3, trim_alpha=True):
    """
    Trimmer transparent kant og skalerer vinylen så den fyller en sirkel
    med gitt radius (minus 'pad'). Bevarer aspect ratio.
    """
    surf = img_surf
    if trim_alpha:
        rect = img_surf.get_bounding_rect(min_alpha=1)
        if rect.width > 0 and rect.height > 0:
            surf = img_surf.subsurface(rect).copy()

    target_diam = max(1, int(2 * (radius - pad)))

    w, h = surf.get_size()
    scale = target_diam / max(w, h)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    scaled = pygame.transform.smoothscale(surf, new_size)

    out = pygame.Surface((target_diam, target_diam), pygame.SRCALPHA)
    out.blit(scaled, scaled.get_rect(center=(target_diam // 2, target_diam // 2)))
    return out

def polar(center, radius, angle_deg):
    """Return (x, y) for en vinkel i grader og radius fra center."""
    angle_rad = math.radians(angle_deg)
    return (center[0] + radius * math.cos(angle_rad),
            center[1] + radius * math.sin(angle_rad))

def draw_flame_sweep(surf, center, r_inner, r_outer, speed=4.0):
    """
    Animerte flammer i en ring mellom r_inner og r_outer (r_inner < r_outer).
    """
    cx, cy = center
    t = pygame.time.get_ticks() / 1000.0
    for a in range(0, 360, 8):
        h = 10 + 12 * math.sin(math.radians(a * 3) + t * speed)
        mid = a + 4
        tip_r = r_outer + h

        p1 = polar((cx, cy), r_inner, a)
        p2 = polar((cx, cy), r_inner, a + 8)
        tip = polar((cx, cy), tip_r, mid)
        pygame.draw.polygon(surf, (200, 40, 10, 120), [p1, p2, tip])

        tip2 = polar((cx, cy), r_outer + h * 0.6, mid)
        pygame.draw.polygon(surf, (255, 200, 60, 160), [p1, p2, tip2])

def blit_hand(surface, image, center, angle_rad):
    """
    Plasser midten av bunnen av bildet i center og roter slik at toppen peker ut.
    angle_rad forventes i RADIANS.
    """
    w, h = image.get_size()
    temp_surf = pygame.Surface((w, h * 2), pygame.SRCALPHA)
    temp_surf.blit(image, (0, h))
    rotated_image = pygame.transform.rotate(temp_surf, -math.degrees(angle_rad))
    rotated_rect = rotated_image.get_rect()
    rotated_rect.center = center
    surface.blit(rotated_image, rotated_rect)


vinyl_img_raw = safe_load_image("/Users/thomas/Desktop/AI Programmering/Analogt Ur/Vinyl.png")
sec_img_raw   = safe_load_image("/Users/thomas/Desktop/AI Programmering/Analogt Ur/Les paul.png")
min_img_raw   = safe_load_image("/Users/thomas/Desktop/AI Programmering/Analogt Ur/stratocaster 3.png")
hr_img_raw    = safe_load_image("/Users/thomas/Desktop/AI Programmering/Analogt Ur/Telecaster.png")

vinyl_fit = make_vinyl_fit_circle(vinyl_img_raw, clock_radius, pad=0, trim_alpha=True)

sec_img = pygame.transform.smoothscale(sec_img_raw, (130, 280))
min_img = pygame.transform.smoothscale(min_img_raw, (120, 200))
hr_img  = pygame.transform.smoothscale(hr_img_raw,  (150, 150))

print("vinyl size:", vinyl_fit.get_size())
print("sec_img size:", sec_img.get_size())
print("min_img size:", min_img.get_size())
print("hr_img size:", hr_img.get_size())


run_flag = True
while run_flag:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_flag = False

    screen.fill((255, 255, 255))

    screen.blit(vinyl_fit, vinyl_fit.get_rect(center=home_center))

    # Roter vinyl
    spin = (pygame.time.get_ticks()/1000.0) * 12  # grader/sek
    vinyl_rot = pygame.transform.rotozoom(vinyl_fit, -spin, 1)
    screen.blit(vinyl_rot, vinyl_rot.get_rect(center=home_center))

    # Flammering
    draw_flame_sweep(screen, home_center, clock_radius, clock_radius +20, speed=4.0)

    # Klokkering, SENTER
    pygame.draw.circle(screen, (0, 0, 0), home_center, clock_radius, 3)
    pygame.draw.circle(screen, (0, 0, 0), home_center, 10)

    # Timemarkeringer
    for i in range(12):
        angle = math.radians(360 / 12 * i + 90)  # +90 for å starte på toppen
        x_outer = home_center[0] + clock_radius * math.cos(angle)
        y_outer = home_center[1] + clock_radius * math.sin(angle)
        x_inner = home_center[0] + (clock_radius - 30) * math.cos(angle)
        y_inner = home_center[1] + (clock_radius - 30) * math.sin(angle)
        pygame.draw.line(screen, (245, 205, 5), (x_inner, y_inner), (x_outer, y_outer), 5)

    # TID OG VINKLER
    now = datetime.now()
    hour = now.hour % 12
    minute = now.minute
    second = now.second

    # Vend bilder
    hour_angle   = math.radians((360 / 12) * (hour + minute / 60) + 180)
    minute_angle = math.radians((360 / 60) * (minute + second / 60) + 180)
    sec_angle    = math.radians(360 / 60 * second + 180)

    # Bilder som viser tid
    blit_hand(screen, hr_img,  home_center, hour_angle)
    blit_hand(screen, min_img, home_center, minute_angle)
    blit_hand(screen, sec_img, home_center, sec_angle)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
