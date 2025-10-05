from graphics import *
import numpy as np
import math as mt
import random, time

# ---------- 4×4 матриці (3D) ----------
def M4_rotate_x(a):
    c,s = mt.cos(a), mt.sin(a)
    return np.array([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]], float)

def M4_rotate_y(a):
    c,s = mt.cos(a), mt.sin(a)
    return np.array([[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]], float)

def M4_rotate_z(a):
    c,s = mt.cos(a), mt.sin(a)
    return np.array([[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]], float)

def apply_M4(points_xyz, M4):
    P = np.c_[np.asarray(points_xyz, float), np.ones((len(points_xyz),1))]
    return P @ M4.T   # N×4

# ---------- 3×3 екранна матриця (без масштабу) ----------
def H2_screen(cx=0.0, cy=0.0):
    # тільки інверсія Y і перенос у (cx, cy)
    return np.array([[ 1.0,  0.0, cx],
                            [ 0.0, -1.0, cy],
                            [ 0.0,  0.0, 1.0]], float)

def to_screen_2d(pts2, H2):
    P = np.c_[np.asarray(pts2, float), np.ones((len(pts2),1))]
    S = P @ H2.T
    return S[:, :2]

# ---------- геометрія ----------
def pyramid_points(base=160, h=180):
    b = base/2
    A = np.array([-b,-b,0], float)
    B = np.array([ b,-b,0], float)
    C = np.array([ b, b,0], float)
    D = np.array([-b, b,0], float)
    S = np.array([ 0, 0,h], float)
    V = np.vstack([A,B,C,D,S])  # 5×3
    E = [(0,1),(1,2),(2,3),(3,0),(0,4),(1,4),(2,4),(3,4)]
    return V, E

def draw_edges(win, pts_scr, edges, col="black", width=2):
    lines=[]
    for i,j in edges:
        p1 = Point(pts_scr[i,0], pts_scr[i,1]); p2 = Point(pts_scr[j,0], pts_scr[j,1])
        ln = Line(p1,p2); ln.setOutline(col); ln.setWidth(width); ln.draw(win)
        lines.append(ln)
    return lines

def undraw_edges(lines):
    for ln in lines: ln.undraw()

def fade_lines(lines, start_gray, end_gray, steps, wait):
    for t in range(steps):
        g = int(np.interp(t, [0, steps-1], [start_gray, end_gray]))
        col = color_rgb(g,g,g)
        for ln in lines: ln.setOutline(col)
        time.sleep(wait)

# ===================== ГОЛОВНА =====================
xw, yw = 1200, 900
win = GraphWin("Піраміда", xw, yw)
win.setBackground("white")

V0, E = pyramid_points(base=160, h=180)

# Обертаємо навколо центроїда вершин моделі
center_model = V0.mean(axis=0)
V_centered   = V0 - center_model

# --- ФІКСОВАНА МЕРТВА ЗОНА ---
DEAD_ZONE = 180   # <-- Рамка вікна в якій не спавняться фігури

FADE_STEPS = 20
DWELL = 0.2

for _ in range(20):
    # 1) випадкові кути
    ax = mt.radians(random.uniform(-50, 50))
    ay = mt.radians(random.uniform(-70, 70))
    az = mt.radians(random.uniform(-30, 30))
    M_model = M4_rotate_z(az) @ M4_rotate_y(ay) @ M4_rotate_x(ax)
    # 2) 3D -> 2D (ортографія)
    Q4 = apply_M4(V_centered, M_model)
    P2 = Q4[:, :2]

    # 3) випадковий центр у межах фіксованої мертвої зони
    cx = random.uniform(DEAD_ZONE, xw - DEAD_ZONE)
    cy = random.uniform(DEAD_ZONE, yw - DEAD_ZONE)

    # 4) екранна матриця
    Hscr = H2_screen(cx=cx, cy=cy)
    S2   = to_screen_2d(P2, Hscr)
    # 5) малювання
    lines = draw_edges(win, S2, E, col=color_rgb(0,0,0), width=2)
    fade_lines(lines, start_gray=0, end_gray=180, steps=FADE_STEPS, wait=DWELL)
    undraw_edges(lines)

win.getMouse()
win.close()