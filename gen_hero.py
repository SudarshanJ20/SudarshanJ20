#!/usr/bin/env python3
"""
Procedurally generate assets/hero.svg — a cinematic animated hero
banner for the GitHub profile README. SMIL only (no CSS, no JS, no
external assets) because GitHub's image proxy strips CSS animation
inside SVGs.

Run:  python3 gen_hero.py
Tune the look via the constants block below: SEED, MOOD, SPARK_X/Y,
palette, bezier control points.
"""

import math
import os
import random
import xml.etree.ElementTree as ET

# ============================================================
# Tunable constants — change these to retune the art
# ============================================================
SEED = 7
MOOD = "supernova"  # "veil" | "supernova" | "nebula" | "datastream"

W, H = 1200, 520

# Spark anchor — placed on a right-side golden-ratio point
SPARK_X = round(W * 0.764)   # 917
SPARK_Y = round(H * 0.382)   # 199

# Palette
BG_BASE  = "#03060e"   # deep near-black
BG_DEEP  = "#070d1a"   # navy core glow under bg gradient
CYAN     = "#27c4ff"   # signature cyan
CYAN_BR  = "#c8efff"   # bright cyan-white
PARTICLE = "#eaf6ff"   # warm-white particle
WHITE    = "#ffffff"

# Bezier control points — the spine the stream is drawn along
P0 = (40,  440)
P1 = (300, 470)
P2 = (600, 80)
P3 = (SPARK_X, SPARK_Y)

# Element budget knobs (mood density multiplies these)
PARTICLE_BASE = 320
STREAM_BASE   = 22

OUT_DIR = "assets"
OUT     = os.path.join(OUT_DIR, "hero.svg")

# ============================================================
# Mood presets — switch MOOD above
# ============================================================
MOODS = {
    "veil": dict(
        density=1.00, conv_speed=1.00, ray_count=22,
        spark_intensity=1.00, far_blur=1.6,
        accent="#7a4dff", grid_snap=False, shoot_count=3,
        constellation=20, hot_core=False, ambient_op=1.0,
    ),
    "supernova": dict(
        density=1.45, conv_speed=0.60, ray_count=38,
        spark_intensity=1.55, far_blur=1.1,
        accent="#ff5f3d", grid_snap=False, shoot_count=5,
        constellation=28, hot_core=True, ambient_op=1.2,
    ),
    "nebula": dict(
        density=0.65, conv_speed=2.40, ray_count=12,
        spark_intensity=0.80, far_blur=3.4,
        accent="#9b7dff", grid_snap=False, shoot_count=1,
        constellation=14, hot_core=False, ambient_op=1.6,
    ),
    "datastream": dict(
        density=1.00, conv_speed=1.00, ray_count=18,
        spark_intensity=1.00, far_blur=0.6,
        accent="#27c4ff", grid_snap=True, shoot_count=3,
        constellation=24, hot_core=False, ambient_op=0.7,
    ),
}


def bezier(t):
    u = 1 - t
    x = u**3*P0[0] + 3*u**2*t*P1[0] + 3*u*t**2*P2[0] + t**3*P3[0]
    y = u**3*P0[1] + 3*u**2*t*P1[1] + 3*u*t**2*P2[1] + t**3*P3[1]
    return x, y


def bezier_tangent(t):
    u = 1 - t
    dx = 3*u**2*(P1[0]-P0[0]) + 6*u*t*(P2[0]-P1[0]) + 3*t**2*(P3[0]-P2[0])
    dy = 3*u**2*(P1[1]-P0[1]) + 6*u*t*(P2[1]-P1[1]) + 3*t**2*(P3[1]-P2[1])
    return dx, dy


def main():
    rng = random.Random(SEED)
    cfg = MOODS[MOOD]
    accent = cfg["accent"]
    si     = cfg["spark_intensity"]

    out = []
    w = out.append

    w('<?xml version="1.0" encoding="UTF-8"?>')
    w(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" '
        f'role="img" aria-label="cinematic hero — particle stream converging on a cyan spark">'
    )

    # ---------- defs ----------
    w("<defs>")
    w(
        f'<radialGradient id="bgGrad" cx="62%" cy="40%" r="78%">'
        f'<stop offset="0%" stop-color="{BG_DEEP}"/>'
        f'<stop offset="100%" stop-color="{BG_BASE}"/>'
        f"</radialGradient>"
    )
    aop = cfg["ambient_op"]
    w(
        f'<radialGradient id="hazeUL" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{accent}" stop-opacity="{0.10*aop:.3f}"/>'
        f'<stop offset="100%" stop-color="{accent}" stop-opacity="0"/>'
        f"</radialGradient>"
    )
    w(
        f'<radialGradient id="hazeLL" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{CYAN}" stop-opacity="{0.07*aop:.3f}"/>'
        f'<stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>'
        f"</radialGradient>"
    )
    w(
        f'<radialGradient id="bloomOuter" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{CYAN}" stop-opacity="0.50"/>'
        f'<stop offset="55%" stop-color="{CYAN}" stop-opacity="0.10"/>'
        f'<stop offset="100%" stop-color="{accent}" stop-opacity="0"/>'
        f"</radialGradient>"
    )
    w(
        f'<radialGradient id="rimGrad" cx="50%" cy="50%" r="50%">'
        f'<stop offset="40%" stop-color="{accent}" stop-opacity="0"/>'
        f'<stop offset="78%" stop-color="{accent}" stop-opacity="0.20"/>'
        f'<stop offset="100%" stop-color="{accent}" stop-opacity="0"/>'
        f"</radialGradient>"
    )
    hot_inner = "#fff4d8" if cfg["hot_core"] else "#ffffff"
    w(
        f'<radialGradient id="coreGrad" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%"   stop-color="{hot_inner}" stop-opacity="1"/>'
        f'<stop offset="18%"  stop-color="{CYAN_BR}"   stop-opacity="0.95"/>'
        f'<stop offset="48%"  stop-color="{CYAN}"      stop-opacity="0.55"/>'
        f'<stop offset="100%" stop-color="{CYAN}"      stop-opacity="0"/>'
        f"</radialGradient>"
    )
    w(
        f'<radialGradient id="haloGrad" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%"   stop-color="{CYAN}" stop-opacity="0.70"/>'
        f'<stop offset="60%"  stop-color="{CYAN}" stop-opacity="0.15"/>'
        f'<stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>'
        f"</radialGradient>"
    )
    w(
        '<linearGradient id="lensFlare" x1="0%" y1="50%" x2="100%" y2="50%">'
        '<stop offset="0%"   stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="48%"  stop-color="#ffffff" stop-opacity="0.85"/>'
        '<stop offset="52%"  stop-color="#ffffff" stop-opacity="0.85"/>'
        '<stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>'
        "</linearGradient>"
    )
    w(
        '<radialGradient id="vig" cx="50%" cy="50%" r="78%">'
        '<stop offset="55%" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="100%" stop-color="#000" stop-opacity="0.70"/>'
        "</radialGradient>"
    )

    # Filters
    w(
        f'<filter id="blurFar" x="-5%" y="-5%" width="110%" height="110%">'
        f'<feGaussianBlur stdDeviation="{cfg["far_blur"]:.2f}"/></filter>'
    )
    w(
        '<filter id="blurMid" x="-5%" y="-5%" width="110%" height="110%">'
        '<feGaussianBlur stdDeviation="0.7"/></filter>'
    )
    w(
        '<filter id="bloomBlur" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="22"/></filter>'
    )
    w(
        f'<filter id="grain" x="0%" y="0%" width="100%" height="100%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="1.3" numOctaves="2" '
        f'seed="{SEED}" stitchTiles="stitch"/>'
        f'<feColorMatrix values="0 0 0 0 0.75  0 0 0 0 0.82  0 0 0 0 0.95  0 0 0 0.55 0"/>'
        f'</filter>'
    )

    # Flow path for animateMotion
    w(
        f'<path id="flowPath" d="M {P0[0]},{P0[1]} '
        f'C {P1[0]},{P1[1]} {P2[0]},{P2[1]} {P3[0]},{P3[1]}" '
        f'fill="none" stroke="none"/>'
    )

    # Shooting-particle paths (off-screen → off-screen arcs)
    shoots = [
        "M -120,90 Q 600,40 1320,170",
        "M 1320,440 Q 700,490 -120,340",
        "M -80,510 Q 600,160 1320,60",
        "M 1320,80 Q 700,280 -80,460",
        "M -100,260 Q 500,30 1320,360",
    ]
    for i, d in enumerate(shoots):
        w(f'<path id="shoot{i}" d="{d}" fill="none" stroke="none"/>')

    w("</defs>")

    # ---------- background & atmosphere ----------
    w(f'<rect width="{W}" height="{H}" fill="url(#bgGrad)"/>')
    # Fill upper-left / lower-left dead space with faint haze
    w(f'<ellipse cx="180" cy="80"  rx="380" ry="220" fill="url(#hazeUL)"/>')
    w(f'<ellipse cx="220" cy="500" rx="420" ry="200" fill="url(#hazeLL)"/>')
    # Pre-spark soft bloom underlay
    w(
        f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="320" '
        f'fill="url(#bloomOuter)" opacity="{0.55*si:.2f}"/>'
    )

    # ---------- parallax dot layers (back → front) ----------
    # (id, count_fraction, r_min, r_max, op_min, op_max, drift_dur, drift_amt, filter, color)
    layer_defs = [
        ("layerFar",  0.30, 0.30, 0.75, 0.10, 0.28, 64,  4, "blurFar", "#ffffff"),
        ("layerMidF", 0.30, 0.45, 1.00, 0.18, 0.45, 48,  6, "blurMid", "#ffffff"),
        ("layerMid",  0.36, 0.70, 1.30, 0.30, 0.65, 36,  8, None,      PARTICLE),
        ("layerMidN", 0.24, 1.00, 1.70, 0.45, 0.82, 28, 10, None,      PARTICLE),
        ("layerNear", 0.12, 1.30, 2.20, 0.60, 0.95, 22, 14, None,      "#ffffff"),
    ]
    base_count = int(PARTICLE_BASE * cfg["density"])
    bright_pool = []

    for li, (lid, frac, rmin, rmax, omin, omax, dur, amt, fblur, color) in enumerate(layer_defs):
        n = max(1, int(base_count * frac))
        dx1 = amt
        dy1 = -amt * 0.5 if li % 2 == 0 else amt * 0.5
        vals = f"0,0; {dx1},{dy1}; 0,0; {-dx1},{-dy1}; 0,0"
        fattr = f' filter="url(#{fblur})"' if fblur else ""
        w(f'<g id="{lid}"{fattr}>')
        w(
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="{vals}" dur="{dur}s" repeatCount="indefinite"/>'
        )
        for _ in range(n):
            t = rng.random() ** 0.9
            cx_, cy_ = bezier(t)
            dx, dy = bezier_tangent(t)
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L, dx / L
            sigma = 14 + 110 * (t ** 1.4)
            offset = rng.gauss(0, sigma)
            # 30% of dots are pure background scatter (not tied to bezier)
            if rng.random() < 0.30:
                px = rng.uniform(0, W)
                py = rng.uniform(0, H)
            else:
                px = cx_ + nx * offset
                py = cy_ + ny * offset
            px = max(-8, min(W + 8, px))
            py = max(-8, min(H + 8, py))
            r  = rng.uniform(rmin, rmax)
            op = rng.uniform(omin, omax)
            if li >= 3 and op > 0.70 and r > 1.1:
                bright_pool.append((px, py))
            # Twinkle a subset of brighter particles
            if li >= 2 and op > 0.55 and rng.random() < 0.28:
                td   = rng.uniform(2.4, 5.2)
                offs = rng.uniform(0, td)
                low  = max(0.10, op - 0.50)
                w(
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" '
                    f'fill="{color}" opacity="{op:.2f}">'
                    f'<animate attributeName="opacity" '
                    f'values="{op:.2f};{low:.2f};{op:.2f}" '
                    f'dur="{td:.1f}s" begin="-{offs:.1f}s" '
                    f'repeatCount="indefinite"/></circle>'
                )
            else:
                w(
                    f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.2f}" '
                    f'fill="{color}" opacity="{op:.2f}"/>'
                )
        w("</g>")

    # ---------- constellation lines ----------
    if bright_pool and cfg["constellation"] > 0:
        rng2 = random.Random(SEED + 11)
        pool = bright_pool[:]
        rng2.shuffle(pool)
        n_target = min(cfg["constellation"], len(pool) // 2)
        w('<g id="constellation">')
        used = 0
        for i in range(len(pool) - 1):
            if used >= n_target:
                break
            x1, y1 = pool[i]
            best, best_d = None, 1e9
            for j in range(i + 1, min(i + 14, len(pool))):
                x2, y2 = pool[j]
                d = math.hypot(x2 - x1, y2 - y1)
                if 50 < d < 170 and d < best_d:
                    best_d = d
                    best   = (x2, y2)
            if best is None:
                continue
            x2, y2 = best
            op_mid = rng2.uniform(0.10, 0.24)
            dur    = rng2.uniform(5.0, 9.5)
            offs   = rng2.uniform(0, dur)
            w(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="{CYAN}" stroke-width="0.4" opacity="0">'
                f'<animate attributeName="opacity" '
                f'values="0;{op_mid:.2f};{op_mid:.2f};0" '
                f'keyTimes="0;0.3;0.7;1" dur="{dur:.1f}s" '
                f'begin="-{offs:.1f}s" repeatCount="indefinite"/></line>'
            )
            used += 1
        w("</g>")

    # ---------- converging stream particles (animateMotion along flowPath) ----------
    n_stream = int(STREAM_BASE * cfg["density"])
    w('<g id="stream">')
    for i in range(n_stream):
        dur   = rng.uniform(3.8, 7.4) * cfg["conv_speed"]
        begin = rng.uniform(0, dur)
        r     = rng.uniform(1.0, 2.1)
        op_max = rng.uniform(0.70, 0.98)
        color = WHITE if rng.random() < 0.7 else CYAN_BR
        jx = rng.uniform(-14, 14)
        jy = rng.uniform(-14, 14)
        if cfg["grid_snap"]:
            steps    = 10
            keytimes = ";".join(f"{k/steps:.3f}" for k in range(steps + 1))
            keypts   = ";".join(f"{k/steps:.3f}" for k in range(steps + 1))
            motion = (
                f'<animateMotion dur="{dur:.2f}s" begin="-{begin:.2f}s" '
                f'repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="{keytimes}" keyPoints="{keypts}">'
                f'<mpath xlink:href="#flowPath"/></animateMotion>'
            )
        else:
            motion = (
                f'<animateMotion dur="{dur:.2f}s" begin="-{begin:.2f}s" '
                f'repeatCount="indefinite">'
                f'<mpath xlink:href="#flowPath"/></animateMotion>'
            )
        w(
            f'<g transform="translate({jx:.1f} {jy:.1f})">'
            f'<circle cx="0" cy="0" r="{r:.2f}" fill="{color}" opacity="0">'
            f'<animate attributeName="opacity" '
            f'values="0;{op_max:.2f};{op_max:.2f};0" '
            f'keyTimes="0;0.18;0.88;1" '
            f'dur="{dur:.2f}s" begin="-{begin:.2f}s" repeatCount="indefinite"/>'
            f'{motion}</circle></g>'
        )
    w("</g>")

    # ---------- shooting particles ----------
    w('<g id="shoot">')
    for i in range(cfg["shoot_count"]):
        path_id = f"shoot{i % len(shoots)}"
        dur     = rng.uniform(8.5, 14.0)
        begin   = rng.uniform(0, dur * 1.4)
        rx      = rng.uniform(16, 28)
        mid     = rng.uniform(0.38, 0.62)
        k0, k1, k2, k3 = max(0, mid - 0.07), max(0, mid - 0.03), \
                         min(1, mid + 0.03), min(1, mid + 0.10)
        w(
            f'<ellipse cx="0" cy="0" rx="{rx:.1f}" ry="0.9" fill="#ffffff" opacity="0">'
            f'<animateMotion dur="{dur:.1f}s" begin="-{begin:.1f}s" rotate="auto" '
            f'repeatCount="indefinite"><mpath xlink:href="#{path_id}"/></animateMotion>'
            f'<animate attributeName="opacity" '
            f'values="0;0;0.95;0;0" '
            f'keyTimes="0;{k0:.3f};{mid:.3f};{k2:.3f};1" '
            f'dur="{dur:.1f}s" begin="-{begin:.1f}s" repeatCount="indefinite"/>'
            f'</ellipse>'
        )
    w("</g>")

    # ---------- energy streaks (animated dash flowing toward spark) ----------
    N_STREAKS = 7
    w('<g id="streaks">')
    for i in range(N_STREAKS):
        ang    = math.pi * (0.78 + i * (0.42 / N_STREAKS)) + rng.uniform(-0.06, 0.06)
        length = rng.uniform(280, 460)
        ox     = SPARK_X + math.cos(ang) * length
        oy     = SPARK_Y + math.sin(ang) * length * 0.65
        mx     = (ox + SPARK_X) / 2 + rng.uniform(-30, 30)
        my     = (oy + SPARK_Y) / 2 + rng.uniform(-30, 30)
        d      = f"M {ox:.1f} {oy:.1f} Q {mx:.1f} {my:.1f} {SPARK_X} {SPARK_Y}"
        dur    = rng.uniform(2.6, 4.4)
        begin  = rng.uniform(0, dur)
        dtot   = int(rng.uniform(280, 380))
        dseg   = rng.randint(40, 90)
        dash   = f"{dseg} {dtot - dseg}"
        w(
            f'<path d="{d}" stroke="{CYAN}" stroke-width="{rng.uniform(0.8,1.4):.2f}" '
            f'fill="none" stroke-linecap="round" '
            f'opacity="{rng.uniform(0.30,0.60):.2f}" stroke-dasharray="{dash}">'
            f'<animate attributeName="stroke-dashoffset" values="{dtot};0" '
            f'dur="{dur:.1f}s" begin="-{begin:.1f}s" repeatCount="indefinite"/></path>'
        )
    w("</g>")

    # ---------- spark bloom (back → front of the spark stack) ----------
    # Big outer blurred bloom
    w(
        f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="240" '
        f'fill="url(#bloomOuter)" filter="url(#bloomBlur)" '
        f'opacity="{0.85*si:.2f}">'
        f'<animate attributeName="opacity" '
        f'values="{0.70*si:.2f};{0.95*si:.2f};{0.70*si:.2f}" '
        f'dur="6.4s" repeatCount="indefinite"/></circle>'
    )
    # Accent rim halo
    w(
        f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="180" '
        f'fill="url(#rimGrad)" opacity="{0.85*si:.2f}"/>'
    )
    # Pulsing mid halo
    w(
        f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="70" '
        f'fill="url(#haloGrad)" opacity="{0.7*si:.2f}">'
        f'<animate attributeName="r" values="62;90;62" dur="3.2s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" '
        f'values="{0.55*si:.2f};{0.85*si:.2f};{0.55*si:.2f}" '
        f'dur="3.2s" repeatCount="indefinite"/></circle>'
    )

    # God rays — rotating spokes around the spark, varying length
    w(f'<g transform="translate({SPARK_X} {SPARK_Y})">')
    # Outer set, slow CW
    w("<g>")
    w(
        '<animateTransform attributeName="transform" type="rotate" '
        'from="0" to="360" dur="58s" repeatCount="indefinite"/>'
    )
    nr = cfg["ray_count"]
    for i in range(nr):
        ang   = 2 * math.pi * i / nr + rng.uniform(-0.03, 0.03)
        r_in  = 22
        r_out = rng.uniform(60, 180) * si
        x1, y1 = math.cos(ang) * r_in,  math.sin(ang) * r_in
        x2, y2 = math.cos(ang) * r_out, math.sin(ang) * r_out
        opp   = rng.uniform(0.08, 0.28) * si
        sw    = rng.choice([0.4, 0.5, 0.6, 0.8])
        w(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{CYAN}" stroke-width="{sw}" opacity="{opp:.2f}"/>'
        )
    w("</g>")
    # Inner set, slow CCW
    w("<g>")
    w(
        '<animateTransform attributeName="transform" type="rotate" '
        'from="0" to="-360" dur="72s" repeatCount="indefinite"/>'
    )
    nr_in = max(8, nr // 2)
    for i in range(nr_in):
        ang   = 2 * math.pi * i / nr_in + rng.uniform(-0.05, 0.05)
        r_in  = 30
        r_out = rng.uniform(45, 110) * si
        x1, y1 = math.cos(ang) * r_in,  math.sin(ang) * r_in
        x2, y2 = math.cos(ang) * r_out, math.sin(ang) * r_out
        opp   = rng.uniform(0.10, 0.22) * si
        w(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="#9be3ff" stroke-width="0.5" opacity="{opp:.2f}"/>'
        )
    w("</g>")
    w("</g>")

    # Horizontal lens-flare streak across the spark
    flare_w = 340 * si
    w(
        f'<ellipse cx="{SPARK_X}" cy="{SPARK_Y}" rx="{flare_w:.0f}" ry="2.2" '
        f'fill="url(#lensFlare)" opacity="{0.55*si:.2f}">'
        f'<animate attributeName="opacity" '
        f'values="{0.35*si:.2f};{0.75*si:.2f};{0.35*si:.2f}" '
        f'dur="3.4s" repeatCount="indefinite"/>'
        f'<animate attributeName="rx" '
        f'values="{flare_w*0.9:.0f};{flare_w*1.10:.0f};{flare_w*0.9:.0f}" '
        f'dur="3.4s" repeatCount="indefinite"/></ellipse>'
    )

    # Core stages — white-hot center → cyan via gradient
    core_r = 40 * si
    w(
        f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="{core_r:.1f}" '
        f'fill="url(#coreGrad)" opacity="0.95">'
        f'<animate attributeName="r" '
        f'values="{core_r*0.92:.1f};{core_r*1.10:.1f};{core_r*0.92:.1f}" '
        f'dur="2.6s" repeatCount="indefinite"/></circle>'
    )
    w(
        f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="{15*si:.1f}" fill="#ffffff" opacity="0.95">'
        f'<animate attributeName="opacity" values="0.85;1.0;0.85" '
        f'dur="1.8s" repeatCount="indefinite"/></circle>'
    )
    w(f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="{6*si:.1f}" fill="#ffffff"/>')

    # Surge pulse — expanding ring every ~10s
    surge_dur = 10.0
    w(
        f'<circle cx="{SPARK_X}" cy="{SPARK_Y}" r="42" fill="none" '
        f'stroke="{CYAN_BR}" stroke-width="1.6" opacity="0">'
        f'<animate attributeName="r" values="42;220" '
        f'keyTimes="0;1" dur="{surge_dur}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" '
        f'values="0;0;0.9;0.4;0;0" '
        f'keyTimes="0;0.40;0.46;0.55;0.70;1" '
        f'dur="{surge_dur}s" repeatCount="indefinite"/>'
        f'<animate attributeName="stroke-width" values="2.2;0.4" '
        f'keyTimes="0;1" dur="{surge_dur}s" repeatCount="indefinite"/></circle>'
    )

    # ---------- grain + vignette ----------
    w(f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.06"/>')
    w(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')

    w("</svg>")

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(out))

    tree = ET.parse(OUT)
    elements = sum(1 for _ in tree.iter())
    size = os.path.getsize(OUT)
    print(
        f"Wrote {OUT}  mood={MOOD}  "
        f"({elements} elements, {size:,} bytes, well-formed XML)"
    )


if __name__ == "__main__":
    main()
