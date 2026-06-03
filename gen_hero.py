#!/usr/bin/env python3
"""
Procedurally generate assets/hero.svg — an animated dark/cyan hero
banner for the GitHub profile README. SMIL animation only (no CSS),
because GitHub's image-proxy strips CSS animation inside SVGs.

Run:  python3 gen_hero.py
Tune the look by changing SEED, MOOD, the spark position, or the
bezier control points (P0..P3).
"""

import math
import os
import random
import xml.etree.ElementTree as ET

SEED = 7
MOOD = "veil"

W, H = 1200, 520
BG = "#05070d"
CYAN = "#27c4ff"
HALO = "#27c4ff"
PARTICLE = "#eaf6ff"

N_VEIL = 460
N_DUST = 150
N_STREAKS = 7
N_SPOKES_A = 14
N_SPOKES_B = 18

SPARK = (985, 232)

P0, P1, P2, P3 = (50, 405), (385, 415), (700, 95), (1080, 235)

OUT_DIR = "assets"
OUT = os.path.join(OUT_DIR, "hero.svg")


def bezier(t):
    u = 1 - t
    x = u**3 * P0[0] + 3 * u**2 * t * P1[0] + 3 * u * t**2 * P2[0] + t**3 * P3[0]
    y = u**3 * P0[1] + 3 * u**2 * t * P1[1] + 3 * u * t**2 * P2[1] + t**3 * P3[1]
    return x, y


def bezier_tangent(t):
    u = 1 - t
    dx = 3 * u**2 * (P1[0] - P0[0]) + 6 * u * t * (P2[0] - P1[0]) + 3 * t**2 * (P3[0] - P2[0])
    dy = 3 * u**2 * (P1[1] - P0[1]) + 6 * u * t * (P2[1] - P1[1]) + 3 * t**2 * (P3[1] - P2[1])
    return dx, dy


def main():
    rng = random.Random(SEED)
    out = []

    def w(s):
        out.append(s)

    w('<?xml version="1.0" encoding="UTF-8"?>')
    w(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid slice" role="img" '
        f'aria-label="animated hero — stippled veil converging on a cyan spark">'
    )

    w("<defs>")
    w(
        '<radialGradient id="vig" cx="50%" cy="50%" r="72%">'
        '<stop offset="55%" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="100%" stop-color="#000" stop-opacity="0.65"/>'
        "</radialGradient>"
    )
    w(
        '<radialGradient id="coreGrad" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>'
        '<stop offset="22%" stop-color="#dff5ff" stop-opacity="0.95"/>'
        f'<stop offset="48%" stop-color="{CYAN}" stop-opacity="0.55"/>'
        f'<stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    w(
        '<radialGradient id="haloGrad" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{HALO}" stop-opacity="0.55"/>'
        f'<stop offset="60%" stop-color="{HALO}" stop-opacity="0.12"/>'
        f'<stop offset="100%" stop-color="{HALO}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    w("</defs>")

    w(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

    w(
        f'<circle cx="{SPARK[0]}" cy="{SPARK[1]}" r="340" '
        f'fill="url(#haloGrad)" opacity="0.45"/>'
    )

    # Dust layer (background, slowest parallax drift)
    w('<g id="dust">')
    w(
        '<animateTransform attributeName="transform" type="translate" '
        'values="0,0; 6,-3; 0,0; -5,3; 0,0" dur="42s" repeatCount="indefinite"/>'
    )
    for _ in range(N_DUST):
        x = rng.uniform(0, W)
        y = rng.uniform(0, H)
        r = rng.uniform(0.4, 1.0)
        op = rng.uniform(0.08, 0.25)
        w(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
            f'fill="#ffffff" opacity="{op:.2f}"/>'
        )
    w("</g>")

    # Veil particles along the sweeping bezier, split into 3 parallax layers
    veil = []
    for _ in range(N_VEIL):
        t = rng.random() ** 0.9
        cx, cy = bezier(t)
        dx, dy = bezier_tangent(t)
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        sigma = 8 + 92 * (t**1.5)
        offset = rng.gauss(0, sigma)
        px = cx + nx * offset
        py = cy + ny * offset
        roll = rng.random()
        if roll < 0.70:
            r = rng.uniform(0.6, 1.1)
            op = rng.uniform(0.30, 0.60)
        elif roll < 0.95:
            r = rng.uniform(1.1, 1.8)
            op = rng.uniform(0.55, 0.80)
        else:
            r = rng.uniform(1.8, 2.6)
            op = rng.uniform(0.72, 0.95)
        veil.append((px, py, r, op))

    layer_specs = [
        ("layerA", "0,0; 8,-4; 0,0; -8,4; 0,0", "22s"),
        ("layerB", "0,0; -10,5; 0,0; 10,-5; 0,0", "28s"),
        ("layerC", "0,0; 5,8; 0,0; -5,-8; 0,0", "34s"),
    ]
    buckets = [[], [], []]
    for i, p in enumerate(veil):
        buckets[i % 3].append(p)

    for (gid, vals, dur), parts in zip(layer_specs, buckets):
        w(f'<g id="{gid}">')
        w(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="{vals}" dur="{dur}" repeatCount="indefinite"/>'
        )
        for (px, py, r, op) in parts:
            if op > 0.65 and rng.random() < 0.40:
                td = rng.uniform(2.2, 4.8)
                offset = rng.uniform(0, td)
                low = max(0.15, op - 0.45)
                w(
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" '
                    f'fill="{PARTICLE}" opacity="{op:.2f}">'
                    f'<animate attributeName="opacity" '
                    f'values="{op:.2f};{low:.2f};{op:.2f}" '
                    f'dur="{td:.1f}s" begin="-{offset:.1f}s" '
                    f'repeatCount="indefinite"/></circle>'
                )
            else:
                w(
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" '
                    f'fill="{PARTICLE}" opacity="{op:.2f}"/>'
                )
        w("</g>")

    # Energy streaks converging into the spark, with animated dashoffset
    w('<g id="streaks">')
    for i in range(N_STREAKS):
        ang = math.pi * (0.78 + i * (0.42 / N_STREAKS)) + rng.uniform(-0.06, 0.06)
        length = rng.uniform(280, 460)
        ox = SPARK[0] + math.cos(ang) * length
        oy = SPARK[1] + math.sin(ang) * length * 0.65
        mid_x = (ox + SPARK[0]) / 2 + rng.uniform(-30, 30)
        mid_y = (oy + SPARK[1]) / 2 + rng.uniform(-30, 30)
        d = f"M {ox:.1f} {oy:.1f} Q {mid_x:.1f} {mid_y:.1f} {SPARK[0]} {SPARK[1]}"
        dur = rng.uniform(2.6, 4.4)
        begin = rng.uniform(0, dur)
        dash_total = int(rng.uniform(280, 380))
        dash_seg = rng.randint(40, 90)
        dash = f"{dash_seg} {dash_total - dash_seg}"
        w(
            f'<path d="{d}" stroke="{CYAN}" '
            f'stroke-width="{rng.uniform(0.8,1.4):.2f}" fill="none" '
            f'stroke-linecap="round" '
            f'opacity="{rng.uniform(0.35,0.7):.2f}" '
            f'stroke-dasharray="{dash}">'
            f'<animate attributeName="stroke-dashoffset" '
            f'values="{dash_total};0" dur="{dur:.1f}s" '
            f'begin="-{begin:.1f}s" repeatCount="indefinite"/></path>'
        )
    w("</g>")

    # Rotating spokes (one set clockwise, one counter-clockwise)
    w(f'<g transform="translate({SPARK[0]} {SPARK[1]})">')
    w("<g>")
    w(
        '<animateTransform attributeName="transform" type="rotate" '
        'from="0" to="360" dur="48s" repeatCount="indefinite"/>'
    )
    for i in range(N_SPOKES_A):
        ang = 2 * math.pi * i / N_SPOKES_A
        r_in, r_out = 18, rng.uniform(70, 140)
        x1, y1 = math.cos(ang) * r_in, math.sin(ang) * r_in
        x2, y2 = math.cos(ang) * r_out, math.sin(ang) * r_out
        w(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{CYAN}" stroke-width="0.6" '
            f'opacity="{rng.uniform(0.10,0.25):.2f}"/>'
        )
    w("</g>")
    w("<g>")
    w(
        '<animateTransform attributeName="transform" type="rotate" '
        'from="0" to="-360" dur="62s" repeatCount="indefinite"/>'
    )
    for i in range(N_SPOKES_B):
        ang = 2 * math.pi * i / N_SPOKES_B + rng.uniform(-0.05, 0.05)
        r_in, r_out = 26, rng.uniform(50, 110)
        x1, y1 = math.cos(ang) * r_in, math.sin(ang) * r_in
        x2, y2 = math.cos(ang) * r_out, math.sin(ang) * r_out
        w(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="#9be3ff" stroke-width="0.5" '
            f'opacity="{rng.uniform(0.08,0.18):.2f}"/>'
        )
    w("</g>")
    w("</g>")

    # Pulsing halo
    w(
        f'<circle cx="{SPARK[0]}" cy="{SPARK[1]}" r="60" '
        f'fill="url(#haloGrad)" opacity="0.6">'
        f'<animate attributeName="r" values="56;80;56" dur="3.2s" '
        f'repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0.6;0.3;0.6" '
        f'dur="3.2s" repeatCount="indefinite"/></circle>'
    )

    # Spark core (white-hot center, cyan-fade halo via gradient)
    w(
        f'<circle cx="{SPARK[0]}" cy="{SPARK[1]}" r="36" '
        f'fill="url(#coreGrad)" opacity="0.95">'
        f'<animate attributeName="r" values="34;39;34" dur="2.6s" '
        f'repeatCount="indefinite"/></circle>'
    )
    w(
        f'<circle cx="{SPARK[0]}" cy="{SPARK[1]}" r="14" fill="#ffffff" '
        f'opacity="0.95">'
        f'<animate attributeName="opacity" values="0.9;1.0;0.9" '
        f'dur="1.8s" repeatCount="indefinite"/></circle>'
    )
    w(f'<circle cx="{SPARK[0]}" cy="{SPARK[1]}" r="6" fill="#ffffff"/>')

    # Drifting scan line
    w(
        f'<rect x="0" y="-4" width="{W}" height="1.4" fill="{CYAN}" '
        f'opacity="0.10">'
        f'<animate attributeName="y" values="-4;{H+4}" dur="9s" '
        f'repeatCount="indefinite"/></rect>'
    )

    # Vignette overlay
    w(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')

    w("</svg>")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(out))

    tree = ET.parse(OUT)
    elements = sum(1 for _ in tree.iter())
    print(f"Wrote {OUT}  ({elements} elements, well-formed XML)")


if __name__ == "__main__":
    main()
