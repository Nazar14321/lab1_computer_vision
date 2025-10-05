from graphics import *
import time
import numpy as np
import math as mt

# ───────── допоміжні: 2D однорідні матриці ─────────
def H_translate(tx, ty):
    return np.array([[1, 0, tx],
                            [0, 1, ty],
                            [0, 0,  1]], float)

def H_scale(sx, sy):
    return np.array([[sx, 0, 0],
                     [0, sy, 0],
                     [0,  0, 1]], float)

def H_rotate(theta):
    c, s = mt.cos(theta), mt.sin(theta)
    return np.array([[ c, -s, 0],
                     [ s,  c, 0],
                     [ 0,  0, 1]], float)

def H_scale_about(k, cx, cy):
    return H_translate(cx, cy) @ H_scale(k, k) @ H_translate(-cx, -cy)

def H_rotate_about(theta, cx, cy):
    return H_translate(cx, cy) @ H_rotate(theta) @ H_translate(-cx, -cy)

def H_screen(yw):
    # мат. → екранні координати (інверсія Y для graphics.py)
    return np.array([[1,  0, 0],
                     [0, -1, yw],
                     [0,  0, 1]], float)

def apply_H(pts2, H):
    P = np.c_[np.asarray(pts2, float), np.ones((len(pts2),1))]
    S = P @ H.T
    return S[:, :2]

def inside_window_scr(pts_scr, xw, yw):
    pts_scr = np.asarray(pts_scr, float)
    x_ok = (pts_scr[:,0] >= 0) & (pts_scr[:,0] <= xw)
    y_ok = (pts_scr[:,1] >= 0) & (pts_scr[:,1] <= yw)
    return bool(np.all(x_ok & y_ok))

def draw_poly(win, pts_scr, col="black", width=2):
    poly = Polygon(*[Point(float(x), float(y)) for x,y in pts_scr])
    poly.setOutline(col); poly.setWidth(width); poly.setFill("")
    poly.draw(win)
    return poly

# ---------------- Параметри сцени ----------------
xw = 600; yw = 600    # розміри графічного вікна
dx = 10; dy = 10      # кроки зсуву (у мат. координатах)
k  = 1.1              # множник масштабування
theta_deg = 5         # кут для обертання (градуси)
theta = mt.radians(theta_deg)

# Базовий шістикутник (мат. координати, вісь Y вгору)
hex0 = np.array([[10,10],
                 [20,10],
                 [30,20],
                 [20,30],
                 [10,30],
                 [ 0,20]], dtype=float)

Hscr = H_screen(yw)   # одна екранна матриця для всього

# ==============================================================================
# 0) Побудова статичного об’єкта
# ==============================================================================
win = GraphWin("2D проєкції — статичний шістикутник", xw, yw)
win.setBackground('white')

S0 = apply_H(hex0, Hscr)
draw_poly(win, S0)
win.getMouse(); win.close()

# ==============================================================================
# 1) Переміщення (скалярна форма)
# ==============================================================================
win = GraphWin("Переміщення (скалярно): тиражування", xw, yw)
win.setBackground('white')

xy1 = hex0.copy()
Hstep = H_translate(dx, dy)

while True:
    time.sleep(0.3)
    xy1 = apply_H(xy1, Hstep)
    S = apply_H(xy1, Hscr)
    if not inside_window_scr(S, xw, yw): break
    draw_poly(win, S)

win.getMouse()
win.close()

# ==============================================================================
# 2) Переміщення (скалярна форма)
# ==============================================================================
win = GraphWin("Переміщення (скалярно): анімація", xw, yw)
win.setBackground('white')

xy2 = hex0.copy()
poly = draw_poly(win, apply_H(xy2, Hscr))
while True:
    time.sleep(0.3)
    xy2 = apply_H(xy2, Hstep)
    S = apply_H(xy2, Hscr)
    if not inside_window_scr(S, xw, yw): break
    poly.undraw()
    poly = draw_poly(win, S)

win.getMouse()
win.close()

# ==============================================================================
# 3) Масштабування (скалярна форма)
# ==============================================================================
win = GraphWin("Масштабування (скалярно): тиражування", xw, yw)
win.setBackground('white')

xy3 = np.array([[295,290],[305,290],[315,300],[305,310],[295,310],[285,300]], float)
center = np.array([xw/2, yw/2], float)

HstepS = H_scale_about(k, center[0], center[1])

S = apply_H(xy3, Hscr); draw_poly(win, S)
while True:
    time.sleep(0.25)
    xy3 = apply_H(xy3, HstepS)
    S = apply_H(xy3, Hscr)
    if not inside_window_scr(S, xw, yw): break
    draw_poly(win, S)

win.getMouse()
win.close()

# ==============================================================================
# 4) Масштабування (скалярна форма)
# ==============================================================================
win = GraphWin("Масштабування (скалярно): анімація", xw, yw)
win.setBackground('white')

xy4 = np.array([[295,290],[305,290],[315,300],[305,310],[295,310],[285,300]], float)
HstepS = H_scale_about(k, center[0], center[1])

poly = draw_poly(win, apply_H(xy4, Hscr))
while True:
    xy4_next = apply_H(xy4, HstepS)
    Snext = apply_H(xy4_next, Hscr)
    if not inside_window_scr(Snext, xw, yw): break
    time.sleep(0.25)
    poly.undraw()
    xy4 = xy4_next
    poly = draw_poly(win, Snext)

win.getMouse()
win.close()

# ==============================================================================
# 5) Обертання (матрична форма, 2×2)
# ==============================================================================
win = GraphWin("Обертання (матрично): тиражування", xw, yw)
win.setBackground('white')

xy5 = np.array([[295,290],[305,290],[315,300],[305,310],[295,310],[285,300]], float)
HstepR = H_rotate_about(theta, center[0], center[1])

for _ in range(20):
    time.sleep(0.3)
    xy5 = apply_H(xy5, HstepR)
    S = apply_H(xy5, Hscr)
    draw_poly(win, S)

win.getMouse(); win.close()

# ==============================================================================
# 6) Обертання (матрична форма, 2×2)
# ==============================================================================
win = GraphWin("Обертання (матрично): анімація", xw, yw)
win.setBackground('white')

xy6 = np.array([[295,290],[305,290],[315,300],[305,310],[295,310],[285,300]], float)
center_fixed = np.array([300., 300.], float)
HstepR_fixed = H_rotate_about(theta, center_fixed[0], center_fixed[1])

poly = draw_poly(win, apply_H(xy6, Hscr))
for _ in range(20):
    time.sleep(0.3)
    xy6 = apply_H(xy6, HstepR_fixed)
    poly.undraw()
    poly = draw_poly(win, apply_H(xy6, Hscr))

win.getMouse()
win.close()
