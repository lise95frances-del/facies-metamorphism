import numpy as np
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Métabasites – faciès", layout="wide")

# ------------------------------------------------------------------
# Les courbes sont relevées à la main sur l'image de référence,
# en coordonnées "pixels" (x, y), puis converties en T (°C) et P (kbar).
# Étalonnage : T = 200 °C -> x = 175 ; T = 800 °C -> x = 530
#              P = 0 kbar -> y = 572 ; P = 12 kbar -> y = 140
# Pour retoucher une courbe, modifie simplement les points (x, y).
# ------------------------------------------------------------------


def to_T(x):
    return (x - 57) / 0.59


def to_P(y):
    return (572 - y) / 36


def conv(pts):
    return [(to_T(x), to_P(y)) for x, y in pts]


# Bandes grises (limites entre faciès)
G1 = conv([(50, 545), (130, 330), (165, 215), (185, 150), (205, 95), (215, 80)])   # limite gauche schiste bleu
A = conv([(215, 80), (255, 115), (280, 180), (300, 265), (312, 300),
          (315, 360), (303, 420), (285, 490), (272, 552)])                          # schiste bleu/éclogite puis schiste vert/amph. à épidote
P2 = conv([(165, 568), (193, 520), (205, 440), (203, 380), (185, 345), (150, 327), (132, 322)])  # contour préhnite-pumpellyite
P1 = conv([(95, 425), (130, 432), (170, 435), (205, 440)])                         # zéolite / préhnite-pumpellyite
D = conv([(132, 322), (150, 327), (185, 340), (330, 258), (420, 190),
          (500, 135), (590, 85), (645, 45)])                                        # diagonale (éclogite en haut)
B = conv([(445, 173), (445, 250), (425, 330), (395, 410), (375, 480), (360, 552)])  # amph. à épidote / amphibolite
C = conv([(510, 132), (505, 200), (490, 290), (470, 370), (440, 450),
          (410, 515), (395, 552)])                                                  # amphibolite / granulite

# Lignes noires (aluminosilicates)
L1 = conv([(165, 568), (370, 436)])
L2 = conv([(370, 436), (645, 62)])
L3 = conv([(370, 436), (530, 570)])

HP_BP_P = 7.0  # limite (non tracée) granulite HP / BP, en kbar

GREY = "#c9c9c9"
RED = "#e0301e"


# ------------------------- Détermination du faciès ----------------
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


G1_A = G1 + A[1:]


def find_facies(t, p):
    # à gauche de la première limite : hors domaine
    if p <= G1[-1][1] and t < T_at(G1, p):
        return "Hors domaine"

    # au-dessus de la diagonale
    if p > P_at(D, t):
        return "Schiste bleu" if t < T_at(A, p) else "Éclogite"

    # en dessous de la diagonale, à gauche du contour préhnite-pumpellyite
    if t < T_at(P2, p):
        return "Zéolite" if p < P_at(P1, t) else "Préhnite-pumpellyite"

    # puis de gauche à droite
    if t < T_at(A, p):
        return "Schiste vert"
    if t < T_at(B, p):
        return "Amphibolite à épidote"
    if t < T_at(C, p):
        return "Amphibolite"
    return "Granulite HP" if p >= HP_BP_P else "Granulite BP"


# ------------------------------ Interface -------------------------
st.title("Faciès métamorphiques des métabasites")

with st.sidebar:
    st.header("Conditions P-T")
    T = st.slider("Température (°C)", 0, 1000, 350, step=5)
    P = st.slider("Pression (kbar)", 0.0, 14.5, 6.0, step=0.1)
    show_assemblages = st.checkbox("Afficher les paragenèses", value=True)

facies = find_facies(T, P)

# ------------------------------ Graphique -------------------------
fig = go.Figure()


def grey_band(curve):
    fig.add_trace(
        go.Scatter(
            x=[c[0] for c in curve],
            y=[c[1] for c in curve],
            mode="lines",
            line=dict(color=GREY, width=14, shape="spline", smoothing=1.0),
            hoverinfo="skip",
            showlegend=False,
        )
    )


def black_line(curve):
    fig.add_trace(
        go.Scatter(
            x=[c[0] for c in curve],
            y=[c[1] for c in curve],
            mode="lines",
            line=dict(color="black", width=1.3),
            hoverinfo="skip",
            showlegend=False,
        )
    )


for band in (G1_A, P2, P1, D, B, C):
    grey_band(band)
for line in (L1, L2, L3):
    black_line(line)


def label(x, y, text, color="black", size=12, bold=False):
    fig.add_annotation(
        x=to_T(x),
        y=to_P(y),
        text=f"<b>{text}</b>" if bold else text,
        showarrow=False,
        font=dict(size=size, color=color),
        align="center",
    )


# Noms des faciès
label(357, 65, "Eclogite", size=16)
label(218, 155, "Schiste<br>Bleu", size=16)
label(475, 170, "Amphibolite", size=16)
label(385, 250, "Amphibolite<br>à épidote", size=16)
label(275, 335, "Schiste<br>Vert", size=16)
label(155, 385, "Préhnite<br>Pumpellyite", size=15)
label(115, 505, "Zéolite", size=15)
label(585, 140, "Granulite<br>HP", size=16)
label(565, 410, "Granulite<br>BP", size=16)

# Aluminosilicates
label(357, 427, "Ky", size=13)
label(390, 430, "Sil", size=13)
label(366, 458, "And", size=13)

# Petites indications noires
label(160, 326, "+Gln<br>+/- Lws", size=11)
label(245, 295, "+Gln", size=11)
label(205, 438, "+Ep<br>+Act", size=11)
label(332, 303, "-Chl<br>+Hbl", size=11)
label(412, 328, "-Ep<br>Pl (olig)<br>+/- Grt", size=11)
label(490, 265, "+Cpx<br>-Hbl", size=11)
label(480, 368, "+Opx<br>-Hbl", size=11)
label(628, 22, "± Qtz", size=11)

# Paragenèses (rouge)
if show_assemblages:
    label(357, 115, "Omp Grt<br>(sans Pl)<br>±Ky<br>±Gl ±Zo", RED)
    label(192, 235, "Chl Gln<br>Ab Lws<br>±Grt<br>(Jd)<br>(Pmp)", RED)
    label(272, 228, "Gln Ep<br>Ab ±Grt<br>(Jd)", RED)
    label(472, 235, "Hbl<br>Pl<br>(An>18)<br>±Grt<br>±Cpx", RED)
    label(380, 298, "Ep<br>Hbl<br>Pl(Ab)", RED)
    label(282, 388, "Chl Ep<br>Act Pl (Ab)", RED)
    label(420, 398, "Hbl<br>Pl (An>18)<br>±Cum<br>±Cpx", RED)
    label(585, 200, "Grt<br>Cpx<br>Pl", RED)
    label(588, 302, "Grt<br>Cpx<br>Opx<br>Pl", RED)
    label(565, 470, "OPx<br>Cpx<br>Pl (An>40)", RED)

# Curseur : grosse flèche rouge dont la pointe indique (T, P)
fig.add_annotation(
    x=T,
    y=P,
    ax=0,
    ay=55,
    xref="x",
    yref="y",
    axref="pixel",
    ayref="pixel",
    showarrow=True,
    arrowhead=2,
    arrowsize=1.4,
    arrowwidth=6,
    arrowcolor="#c4161c",
    text="",
)

fig.update_layout(
    title=dict(text="METABASITES", x=0.5, font=dict(size=18)),
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=700,
    margin=dict(l=60, r=20, t=50, b=60),
    showlegend=False,
    xaxis=dict(
        title="T (°C)",
        range=[to_T(40), to_T(645)],
        tickvals=[200, 400, 600, 800],
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor="black",
        ticks="outside",
    ),
    yaxis=dict(
        title="P (kbar)",
        range=[0, to_P(40)],
        tickvals=list(range(0, 13, 2)),
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor="black",
        ticks="outside",
    ),
)

col1, col2 = st.columns([3, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Résultat")
    st.success(f"**{facies}**")
    st.write(f"T = {T} °C")
    st.write(f"P = {P:.1f} kbar")
    st.caption("≈ profondeur : " + f"{P * 3.7:.0f} km")
