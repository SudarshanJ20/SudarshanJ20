import random, math

random.seed(73)  # reproducible composition

W, H = 1200, 520
parts = []

def esc(v): return f"{v:.1f}"

# ---- 1. THE VEIL: a billowing diagonal swath of stippled particles ----
# center curve sweeps from lower-left up toward the spark on the right
def veil_center(x):
    t = x / W
    return H*0.78 - 360*math.sin(t*1.5) * (0.4+0.6*t)  # arcs upward to the right

veil = []
N = 460
for _ in range(N):
    # bias x toward left-center, thinning to the right
    x = (random.random()**0.7) * (W*0.92)
    spread = 26 + 150*(x/W)            # billows wider as it travels
    y = veil_center(x) + random.gauss(0, spread)
    if 6 < y < H-6:
        b = random.random()
        r = 0.6 + b*1.6
        op = 0.10 + b*0.78
        veil.append((x, y, r, op))

# ---- 2. BACKGROUND DUST: sparse faint stars ----
dust = []
for _ in range(150):
    x = random.random()*W
    y = random.random()*H
    dust.append((x, y, 0.5+random.random()*0.9, 0.05+random.random()*0.28))

# ---- 3. distribute into 3 parallax layers ----
def layer_of(op):
    if op < 0.30: return 0
    if op < 0.60: return 1
    return 2

layers = {0:[],1:[],2:[]}
for p in veil+dust:
    layers[layer_of(p[3])].append(p)

drift = {0:("-6", "10s"), 1:("9", "14s"), 2:("-4", "8s")}

svg = []
svg.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">')
svg.append('''<defs>
  <radialGradient id="vig" cx="62%" cy="50%" r="75%">
    <stop offset="55%" stop-color="#05070d" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0.9"/>
  </radialGradient>
  <radialGradient id="core" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#ffffff"/>
    <stop offset="22%" stop-color="#eaf9ff"/>
    <stop offset="55%" stop-color="#27c4ff" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="#27c4ff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="halo" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#27c4ff" stop-opacity="0.30"/>
    <stop offset="100%" stop-color="#27c4ff" stop-opacity="0"/>
  </radialGradient>
  <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="1.1"/>
  </filter>
</defs>''')
svg.append(f'<rect width="{W}" height="{H}" fill="#05070d"/>')

SPARK_X, SPARK_Y = 1012, 236

# ---- converging energy streaks toward the spark ----
svg.append('<g stroke="#bfeeff" fill="none" stroke-width="0.8">')
for _ in range(7):
    sx = 120 + random.random()*620
    sy = veil_center(sx) + random.gauss(0, 40)
    cx = (sx+SPARK_X)/2
    cy = min(sy, SPARK_Y) - 60 - random.random()*80
    d = f"M{esc(sx)} {esc(sy)} Q{esc(cx)} {esc(cy)} {esc(SPARK_X)} {esc(SPARK_Y)}"
    dur = 3.5+random.random()*3
    svg.append(f'<path d="{d}" stroke-opacity="0.18" stroke-dasharray="3 10">'
               f'<animate attributeName="stroke-dashoffset" values="80;0" dur="{dur}s" repeatCount="indefinite"/></path>')
svg.append('</g>')

# ---- particle layers ----
for li in (0,1,2):
    dx, dur = drift[li]
    svg.append(f'<g fill="#ffffff"><animateTransform attributeName="transform" type="translate" '
               f'values="0 0;{dx} {("3" if li!=1 else "-5")};0 0" dur="{dur}" repeatCount="indefinite"/>')
    twinkle = 0
    for (x,y,r,op) in layers[li]:
        # twinkle a fraction of brighter dots
        if op > 0.45 and twinkle < 60 and random.random() < 0.4:
            twinkle += 1
            d = 1.8+random.random()*3.2
            lo = max(0.05, op*0.25)
            svg.append(f'<circle cx="{esc(x)}" cy="{esc(y)}" r="{esc(r)}" opacity="{op:.2f}">'
                       f'<animate attributeName="opacity" values="{op:.2f};{lo:.2f};{op:.2f}" dur="{d:.1f}s" repeatCount="indefinite"/></circle>')
        else:
            svg.append(f'<circle cx="{esc(x)}" cy="{esc(y)}" r="{esc(r)}" opacity="{op:.2f}"/>')
    svg.append('</g>')

# ---- THE SPARK ----
svg.append(f'<g transform="translate({SPARK_X},{SPARK_Y})">')
# halo
svg.append('<circle r="120" fill="url(#halo)"><animate attributeName="r" values="108;130;108" dur="4s" repeatCount="indefinite"/>'
           '<animate attributeName="opacity" values="0.9;0.55;0.9" dur="4s" repeatCount="indefinite"/></circle>')
# rotating rays
svg.append('<g opacity="0.9"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="26s" repeatCount="indefinite"/>')
for k in range(6):
    ang = k*60
    svg.append(f'<g transform="rotate({ang})"><path d="M0 0 L2.2 -78 L-2.2 -78 Z" fill="#dff7ff" opacity="0.5">'
               f'<animate attributeName="opacity" values="0.5;0.12;0.5" dur="{2.5+k*0.3:.1f}s" repeatCount="indefinite"/></path></g>')
svg.append('</g>')
# counter-rotating fine rays
svg.append('<g opacity="0.7"><animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="34s" repeatCount="indefinite"/>')
for k in range(4):
    ang = 45+k*90
    svg.append(f'<g transform="rotate({ang})"><rect x="-0.5" y="-58" width="1" height="48" fill="#9fe9ff" opacity="0.4"/></g>')
svg.append('</g>')
# hot core
svg.append('<circle r="44" fill="url(#core)"><animate attributeName="r" values="40;48;40" dur="3s" repeatCount="indefinite"/></circle>')
svg.append('<circle r="6" fill="#ffffff"><animate attributeName="opacity" values="1;0.6;1" dur="1.6s" repeatCount="indefinite"/></circle>')
svg.append('</g>')

# scanning shimmer line (subtle life)
svg.append(f'<rect x="0" y="0" width="{W}" height="1.5" fill="#27c4ff" opacity="0.05">'
           f'<animate attributeName="y" values="-10;{H};-10" dur="11s" repeatCount="indefinite"/></rect>')

svg.append(f'<rect width="{W}" height="{H}" fill="url(#vig)"/>')
svg.append('</svg>')

out = "\n".join(svg)
with open("/mnt/user-data/outputs/assets/hero.svg","w") as f:
    f.write(out)
print("particles:", len(veil)+len(dust), "| bytes:", len(out))
