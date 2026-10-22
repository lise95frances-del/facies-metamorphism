import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Faciès métamorphiques", layout="wide")

# ------------------------------------------------------------------
# Domaines des faciès (T en °C, P en GPa) - tracé SCHÉMATIQUE
# À ajuster avec ton cours / tes références (Bucher & Grapes, Spear...)
# ------------------------------------------------------------------
FACIES = {
    "Zéolites": {
        "poly": [(0, 0), (200, 0), (170, 0.35), (0, 0.3)],
        "color": "#cfe8f3",
    },
    "Préhnite-pumpellyite": {
        "poly": [(200, 0), (320, 0), (300, 0.5), (170, 0.35)],
        "color": "#a8d8c8",
    },
    "Schistes verts": {
        "poly": [(320, 0), (500, 0), (540, 1.1), (300, 0.5)],
        "color": "#8fd18f",
    },
    "Schistes bleus": {
        "poly": [(0, 0.3), (170, 0.35), (300, 0.5), (540, 1.1), (560, 1.6), (0, 1.2)],
        "color": "#7fa6e8",
    },
    "Amphibolite": {
        "poly": [(500, 0), (750, 0), (800, 1.0), (650, 1.4), (560, 1.6), (540, 1.1)],
        "color": "#f2c36b",
    },
    "Granulite": {
        "poly": [(750, 0), (1000, 0), (1000, 1.3), (800, 1.0)],
        "color": "#e88f6b",
    },
    "Éclogite": {
        "poly": [(0, 1.2), (560, 1.6), (650, 1.4), (800, 1.0), (1000, 1.3), (1000, 3), (0, 3)],
        "color": "#c76b6b",
    },
}

T_MAX, P_MAX = 1000, 3.0


def point_in_polygon(x, y, poly):
    """Algorithme du rayon : True si (x, y) est dans le polygone."""
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            x_inter = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_inter:
                inside = not inside
    return inside


def find_facies(T, P):
    for name, data in FACIES.items():
        if point_in_polygon(T, P, data["poly"]):
            return name
    return "Hors des domaines définis"


# ------------------------------ Interface -------------------------
st.title("Faciès métamorphiques des métabasites")
st.caption("Diagramme P-T schématique : déplace le curseur pour trouver le faciès.")

with st.sidebar:
    st.header("Conditions P-T")
    T = st.slider("Température (°C)", 0, T_MAX, 450, step=5)
    P = st.slider("Pression (GPa)", 0.0, P_MAX, 0.6, step=0.05)
    st.metric("Profondeur approx.", f"{P * 1000 / 27:.0f} km".replace(",", " "))

facies = find_facies(T, P)

# ------------------------------ Graphique -------------------------
fig = go.Figure()

for name, data in FACIES.items():
    xs = [p[0] for p in data["poly"]] + [data["poly"][0][0]]
    ys = [p[1] for p in data["poly"]] + [data["poly"][0][1]]
    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            fill="toself",
            fillcolor=data["color"],
            line=dict(color="white", width=1.5),
            name=name,
            hoverinfo="name",
            opacity=0.9,
        )
    )

# Curseur
fig.add_trace(
    go.Scatter(
        x=[T],
        y=[P],
        mode="markers",
        marker=dict(size=16, color="black", symbol="x", line=dict(width=2, color="white")),
        name="Ta position",
        hovertemplate="T = %{x} °C<br>P = %{y} GPa<extra></extra>",
    )
)

fig.update_layout(
    xaxis=dict(title="Température (°C)", range=[0, T_MAX]),
    yaxis=dict(title="Pression (GPa)", range=[P_MAX, 0]),  # P croît vers le bas
    height=600,
    margin=dict(l=20, r=20, t=20, b=20),
    legend=dict(orientation="v"),
)

col1, col2 = st.columns([3, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Résultat")
    st.success(f"**{facies}**")
    st.write(f"T = {T} °C")
    st.write(f"P = {P:.2f} GPa")

st.info(
    "Les limites sont schématiques et simplifiées. "
    "Remplace les coordonnées du dictionnaire FACIES par celles de ton diagramme de référence."
)
