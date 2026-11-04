import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Métabasites – faciès", layout="wide")

# ==================================================================
# 1) COURBES DU DIAGRAMME
# Relevées sur l'image de référence en coordonnées pixels (x, y),
# puis converties en T (°C) et P (kbar).
# Étalonnage ajusté sur les graduations de l'image :
#   T = (x - 53.3) / 0.5958      P = (573.5 - y) / 36.2
# Pour retoucher une courbe, modifie simplement ses points (x, y).
# ==================================================================
X0, KX = 53.3, 0.5958
Y0, KY = 573.5, 36.2


def to_T(x):
    return (x - X0) / KX


def to_P(y):
    return (Y0 - y) / KY


def conv(pts):
    return [(to_T(x), to_P(y)) for x, y in pts]


def smooth_curve(curve, sigma=9.0, step=2.0):
    """Lisse une courbe [(T, P), ...] : rééchantillonnage régulier puis moyenne gaussienne
    le long de la courbe (calculée en pixels), extrémités conservées."""
    px = np.array([(X0 + KX * t, Y0 - KY * p) for t, p in curve])
    seg = np.hypot(*np.diff(px, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(int(s[-1] / step), 2)
    su = np.linspace(0, s[-1], n + 1)
    x = np.interp(su, s, px[:, 0])
    y = np.interp(su, s, px[:, 1])
    k = min(int(3 * sigma / step), n - 1)
    w = np.exp(-0.5 * (np.arange(-k, k + 1) * step / sigma) ** 2)
    w /= w.sum()

    def sm(v):
        left = 2 * v[0] - v[1:k + 1][::-1]
        right = 2 * v[-1] - v[-k - 1:-1][::-1]
        return np.convolve(np.concatenate([left, v, right]), w, mode="valid")

    x, y = sm(x), sm(y)
    return [(to_T(a), to_P(b)) for a, b in zip(x, y)]


# Limite gauche (schiste bleu) -> sommet de l'arche
G1 = conv([(58, 535), (63, 520), (68, 505), (73, 490), (78, 475), (82, 460), (87, 445),
           (92, 430), (100, 400), (106, 385), (111, 370), (116, 355), (121, 340), (130, 310),
           (135, 295), (140, 280), (145, 265), (149, 250), (154, 235), (159, 220), (164, 205),
           (168, 190), (173, 175), (178, 160), (183, 145), (188, 130), (192, 115), (197, 100),
           (202, 85), (209, 70), (212, 55), (215, 40), (217, 20)])
# Descente de l'arche : schiste bleu / éclogite, puis schiste vert / amphibolite à épidote
A = conv([(217, 20), (217, 45), (218, 62), (223, 85), (235, 100), (246, 115), (256, 130), (266, 145),
          (276, 160), (285, 175), (294, 190), (302, 205), (310, 220), (318, 235), (326, 265),
          (329, 280), (333, 295), (335, 310), (337, 325), (339, 340), (340, 355), (340, 370),
          (339, 385), (338, 400), (336, 415), (336, 430), (332, 445), (322, 460), (318, 475),
          (311, 490), (304, 505), (297, 520), (289, 535), (282, 550)])
# Contour du domaine préhnite-pumpellyite (voûte puis côté droit)
P2 = conv([(128, 317), (135, 319), (155, 320), (172, 326), (185, 333), (192, 345), (194, 355),
           (201, 370), (206, 385), (210, 400), (210, 415), (208, 430), (206, 460), (202, 475),
           (195, 490), (189, 505), (184, 520), (180, 535), (174, 550), (164, 565)])
# Zéolite / préhnite-pumpellyite
P1 = conv([(100, 418), (118, 424), (140, 432), (162, 445), (174, 460), (181, 475),
           (189, 490), (193, 497)])
# Diagonale (éclogite au-dessus) : voûte + droite
D_LINE = conv([(192, 340), (600, 26)])
D_CLS = conv([(128, 317), (135, 319), (155, 320), (172, 326), (185, 333), (192, 340), (600, 26)])
# Amphibolite à épidote / amphibolite (rejoint la courbe A en bas)
B = conv([(443, 148), (443, 160), (443, 175), (442, 190), (440, 205), (438, 220), (437, 235),
          (432, 250), (429, 265), (424, 280), (420, 295), (414, 310), (408, 325), (402, 340),
          (396, 355), (388, 370), (380, 385), (370, 400), (359, 415), (349, 430), (340, 441)])
# Amphibolite / granulite
C = conv([(509, 100), (513, 115), (512, 130), (512, 145), (512, 160), (510, 190), (508, 205),
          (506, 220), (505, 235), (502, 265), (496, 280), (493, 295), (490, 310), (487, 325),
          (483, 340), (480, 355), (475, 370), (471, 385), (466, 400), (460, 415), (454, 430),
          (448, 445), (440, 460), (432, 475), (422, 490), (413, 505), (403, 520), (393, 535),
          (388, 545)])

# --- Lissage des courbes relevées à la main (supprime les petits tremblements) ---
_ga = smooth_curve(G1 + A[1:], sigma=10)
_apex = int(np.argmax([p for _, p in _ga]))
G1 = _ga[:_apex + 1]
A = _ga[_apex:]
P2 = smooth_curve(P2, sigma=8)
P1 = smooth_curve(P1, sigma=8)
B = smooth_curve(B, sigma=9)
C = smooth_curve(C, sigma=9)
_i = next(i for i, (t, p) in enumerate(P2) if p < to_P(340))
D_CLS = P2[:_i] + [(to_T(192), to_P(340)), (to_T(600), to_P(26))]

# Lignes noires : aluminosilicates (And / Ky / Sil)
L1 = conv([(158.5, 573.5), (368.7, 434.8)])
L2 = conv([(368.7, 434.8), (645, 63.8)])
L3 = conv([(368.5, 435.3), (535.9, 573.5)])

HP_BP_P = 6.0  # limite (non tracée) granulite HP / BP, en kbar

GREY = "#b9b9b9"
RED = "#c4161c"
BLACK = "#000000"
KM_PER_KBAR = 3.7

# ==================================================================
# 2) GRADIENTS MÉTAMORPHIQUES (indicatifs) : listes (T °C, P kbar)
# ==================================================================
GRADIENTS = {
    "Subduction (≈ 5–8 °C/km)": dict(
        color="#1d4ed8",
        pts=[(10, 0), (50, 2), (100, 4), (140, 6), (175, 8), (205, 10), (235, 12), (260, 14.5)]),
    "Collision continentale – Barrovien (≈ 20–30 °C/km)": dict(
        color="#d97706",
        pts=[(10, 0), (150, 1), (300, 2), (400, 3), (470, 4), (530, 5), (580, 6),
             (670, 8), (740, 10), (800, 12)]),
    "Divergence continentale / rift (≈ 40–60 °C/km)": dict(
        color="#7c3aed",
        pts=[(10, 0), (230, 1), (420, 2), (580, 3), (710, 4), (820, 5), (900, 6)]),
    "Dorsale océanique (> 100 °C/km)": dict(
        color="#0f766e",
        pts=[(10, 0), (150, 0.4), (300, 0.8), (430, 1.2), (540, 1.6), (640, 2.0)]),
}

# ==================================================================
# 3) PARAGENÈSES (d'après le diagramme)
# ==================================================================


def paragenese(facies, T, P):
    if facies == "Zéolite":
        return ["Zéolites (laumontite…), Ab, Chl, Qtz", "(non indiqué sur le diagramme)"]
    if facies == "Préhnite-pumpellyite":
        return ["Prh, Pmp, Chl, Ab, Qtz", "+Ep +Act vers le schiste vert"]
    if facies == "Schiste vert":
        return ["Chl, Ep, Act, Pl (Ab)"]
    if facies == "Schiste bleu":
        if T < 300:
            return ["Chl, Gln, Ab, Lws, ±Grt, (Jd), (Pmp)"]
        return ["Gln, Ep, Ab, ±Grt, (Jd)"]
    if facies == "Éclogite":
        return ["Omp, Grt (sans Pl), ±Ky, ±Gl, ±Zo", "± Qtz"]
    if facies == "Amphibolite à épidote":
        return ["Ep, Hbl, Pl (Ab)"]
    if facies == "Amphibolite":
        if P >= 6:
            return ["Hbl, Pl (An>18), ±Grt, ±Cpx"]
        return ["Hbl, Pl (An>18), ±Cum, ±Cpx"]
    if facies == "Granulite HP":
        if P >= 9.5:
            return ["Grt, Cpx, Pl"]
        return ["Grt, Cpx, Opx, Pl"]
    if facies == "Granulite BP":
        return ["Opx, Cpx, Pl (An>40)"]
    return ["Hors du domaine représenté"]


# ==================================================================
# 4) DÉTERMINATION DU FACIÈS
# ==================================================================
def T_at(curve, p):
    ps = np.array([c[1] for c in curve])
    ts = np.array([c[0] for c in curve])
    o = np.argsort(ps)
    return float(np.interp(p, ps[o], ts[o]))


def P_at(curve, t):
    ps = np.array([c[1] for c in curve])
    ts = np.array([c[0] for c in curve])
    o = np.argsort(ts)
    return float(np.interp(t, ts[o], ps[o]))


B_PMIN = min(c[1] for c in B)


def T_B(p):
    # sous son extrémité, la courbe B se confond avec la courbe A
    return T_at(A, p) if p < B_PMIN else T_at(B, p)


def find_facies(t, p):
    if t < T_at(G1, p):
        return "Hors domaine"
    if p > P_at(D_CLS, t):  # au-dessus de la diagonale
        return "Schiste bleu" if t < T_at(A, p) else "Éclogite"
    if t < T_at(P2, p):  # à gauche du contour préhnite-pumpellyite
        return "Zéolite" if p < P_at(P1, t) else "Préhnite-pumpellyite"
    if t < T_at(A, p):
        return "Schiste vert"
    if t < T_B(p):
        return "Amphibolite à épidote"
    if t < T_at(C, p):
        return "Amphibolite"
    return "Granulite HP" if p >= HP_BP_P else "Granulite BP"


# ==================================================================
# 5) INTERFACE
# ==================================================================
st.title("Faciès métamorphiques des métabasites")

with st.sidebar:
    st.header("Curseur P-T")
    mode = st.radio("Mode", ["Libre", "Le long d'un gradient"])
    followed = None
    if mode == "Libre":
        T = st.slider("Température (°C)", 0, 1000, 350, step=5)
        P = st.slider("Pression (kbar)", 0.0, 14.5, 6.0, step=0.1)
    else:
        followed = st.selectbox("Gradient suivi", list(GRADIENTS))
        pg = [pt[1] for pt in GRADIENTS[followed]["pts"]]
        tg = [pt[0] for pt in GRADIENTS[followed]["pts"]]
        P = st.slider("Pression (kbar)", 0.0, float(max(pg)), min(5.0, float(max(pg))), step=0.1)
        T = float(np.interp(P, pg, tg))
        st.write(f"Température correspondante : **{T:.0f} °C**")

    st.header("Affichage")
    show_assemblages = st.checkbox("Afficher les paragenèses (assemblages minéralogiques)", value=True)
    shown = st.multiselect("Gradients métamorphiques à tracer", list(GRADIENTS), default=[])
    if followed and followed not in shown:
        shown.append(followed)

facies = find_facies(T, P)

# ------------------------------ Graphique -------------------------
fig = go.Figure()


def add_line(curve, color, width, spline=True, name=None, dash=None, hover=False):
    fig.add_trace(
        go.Scatter(
            x=[c[0] for c in curve],
            y=[c[1] for c in curve],
            mode="lines",
            name=name or "",
            showlegend=bool(name),
            line=dict(color=color, width=width, dash=dash,
                      shape="spline" if spline else "linear", smoothing=1.0),
            hovertemplate=(f"{name}<br>T = %{{x:.0f}} °C<br>P = %{{y:.1f}} kbar<extra></extra>"
                           if hover else None),
            hoverinfo=None if hover else "skip",
        )
    )


for band in (G1 + A[1:], P2, P1, D_LINE, B, C):
    add_line(band, GREY, 15, spline=False)
for ln in (L1, L2, L3):
    add_line(ln, BLACK, 1.5, spline=False)

# Gradients métamorphiques
for gname in shown:
    g = GRADIENTS[gname]
    add_line(smooth_curve(list(g["pts"]), sigma=12, step=3), g["color"], 4,
             spline=False, name=gname, dash="dash", hover=True)


def label(x, y, text, color=BLACK, size=13, bold=False, key=None):
    """Place un texte aux coordonnées pixel (x, y) de l'image de référence."""
    active = key is not None and key == facies
    fig.add_annotation(
        x=to_T(x), y=to_P(y),
        text=f"<b>{text}</b>" if bold else text,
        showarrow=False,
        font=dict(size=size, color=color, family="Arial"),
        align="center",
        bgcolor="#fff176" if active else None,
        bordercolor="black" if active else None,
        borderwidth=2 if active else 0,
        borderpad=3,
    )


# Noms des faciès
label(357, 66, "Eclogite", size=18, bold=True, key="Éclogite")
label(218, 155, "Schiste<br>Bleu", size=18, bold=True, key="Schiste bleu")
label(475, 170, "Amphibolite", size=18, bold=True, key="Amphibolite")
label(385, 248, "Amphibolite<br>à épidote", size=18, bold=True, key="Amphibolite à épidote")
label(275, 343, "Schiste<br>Vert", size=18, bold=True, key="Schiste vert")
label(155, 385, "Préhnite<br>Pumpellyite", size=17, bold=True, key="Préhnite-pumpellyite")
label(115, 505, "Zéolite", size=17, bold=True, key="Zéolite")
label(585, 140, "Granulite<br>HP", size=18, bold=True, key="Granulite HP")
label(565, 418, "Granulite<br>BP", size=18, bold=True, key="Granulite BP")

# Aluminosilicates
label(357, 428, "Ky", size=14, bold=True)
label(390, 430, "Sil", size=14, bold=True)
label(366, 458, "And", size=14, bold=True)

# Indications noires
for (x, y, txt) in [(158, 328, "+Gln<br>+/- Lws"), (247, 296, "+Gln"), (205, 438, "+Ep<br>+Act"),
                    (332, 303, "-Chl<br>+Hbl"), (412, 328, "-Ep<br>Pl (olig)<br>+/- Grt"),
                    (505, 264, "+Cpx<br>-Hbl"), (482, 368, "+Opx<br>-Hbl"), (622, 22, "± Qtz")]:
    label(x, y, txt, size=12)

# Paragenèses en rouge
if show_assemblages:
    for (x, y, txt) in [
        (355, 113, "Omp Grt<br>(sans Pl)<br>±Ky<br>±Gl ±Zo"),
        (190, 226, "Chl Gln<br>Ab Lws<br>±Grt<br>(Jd)<br>(Pmp)"),
        (272, 226, "Gln Ep<br>Ab ±Grt<br>(Jd)"),
        (472, 236, "Hbl<br>Pl<br>(An>18)<br>±Grt<br>±Cpx"),
        (380, 297, "Ep<br>Hbl<br>Pl(Ab)"),
        (282, 384, "Chl Ep<br>Act Pl (Ab)"),
        (420, 398, "Hbl<br>Pl (An>18)<br>±Cum<br>±Cpx"),
        (585, 190, "Grt<br>Cpx<br>Pl"),
        (588, 302, "Grt<br>Cpx<br>Opx<br>Pl"),
        (565, 470, "Opx<br>Cpx<br>Pl (An>40)"),
    ]:
        label(x, y, txt, color=RED, size=13, bold=True)

# Curseur : repères pointillés + gros point jaune cerclé de noir (pas de flèche)
x_min = to_T(40)
fig.add_trace(go.Scatter(x=[T, T], y=[0, P], mode="lines", hoverinfo="skip", showlegend=False,
                         line=dict(color="black", width=1.5, dash="dot")))
fig.add_trace(go.Scatter(x=[x_min, T], y=[P, P], mode="lines", hoverinfo="skip", showlegend=False,
                         line=dict(color="black", width=1.5, dash="dot")))
fig.add_trace(
    go.Scatter(
        x=[T], y=[P], mode="markers", showlegend=False, name="Curseur",
        marker=dict(size=18, color="#ffeb3b", line=dict(color="black", width=3)),
        hovertemplate=f"{facies}<br>T = %{{x:.0f}} °C<br>P = %{{y:.1f}} kbar<extra></extra>",
    )
)

fig.update_layout(
    font=dict(color="black", family="Arial", size=14),
    title=dict(text="<b>MÉTABASITES</b>", x=0.5, font=dict(size=22, color="black")),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=760,
    margin=dict(l=70, r=20, t=60, b=110 if shown else 60),
    showlegend=bool(shown),
    legend=dict(orientation="h", x=0, y=-0.1, font=dict(size=14, color="black"),
                bgcolor="white", bordercolor="black", borderwidth=1),
    xaxis=dict(
        title=dict(text="<b>T (°C)</b>", font=dict(size=16, color="black")),
        range=[to_T(40), to_T(645)],
        tickvals=[200, 400, 600, 800],
        tickfont=dict(size=15, color="black"),
        showgrid=False, zeroline=False, showline=True, linecolor="black", linewidth=1.5,
        ticks="outside", tickcolor="black",
    ),
    yaxis=dict(
        title=dict(text="<b>P (kbar)</b>", font=dict(size=16, color="black")),
        range=[0, to_P(40)],
        tickvals=list(range(0, 13, 2)),
        tickfont=dict(size=15, color="black"),
        showgrid=False, zeroline=False, showline=True, linecolor="black", linewidth=1.5,
        ticks="outside", tickcolor="black",
    ),
)

col1, col2 = st.columns([3, 1])
with col1:
    # theme=None : empêche Streamlit de recolorer le graphique (texte pâle en thème sombre)
    st.plotly_chart(fig, width="stretch", theme=None)

with col2:
    st.subheader("Résultat")
    st.success(f"**{facies}**")
    st.write(f"**T** = {T:.0f} °C  \n**P** = {P:.1f} kbar")
    depth = P * KM_PER_KBAR
    st.write(f"**Profondeur ≈** {depth:.0f} km")
    if depth > 1:
        st.write(f"**Gradient apparent ≈** {T / depth:.0f} °C/km")

    st.markdown("**Paragenèse à cet endroit**")
    for line in paragenese(facies, T, P):
        st.info(line)

    with st.expander("Toutes les paragenèses"):
        for f in ["Zéolite", "Préhnite-pumpellyite", "Schiste vert", "Schiste bleu", "Éclogite",
                  "Amphibolite à épidote", "Amphibolite", "Granulite HP", "Granulite BP"]:
            st.markdown(f"**{f}** : " + " / ".join(paragenese(f, 200 if f == "Schiste bleu" else 0,
                                                              10 if f == "Granulite HP" else 7)))

st.caption(
    "Limites des faciès relevées sur le diagramme de référence ; gradients indicatifs "
    "(1 kbar ≈ 3,7 km de profondeur)."
)
