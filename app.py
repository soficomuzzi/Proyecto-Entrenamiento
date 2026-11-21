"""A TU RITMO — formulario conversacional y generador de rutinas (Streamlit).
Ejecutar: streamlit run app.py
"""
from concurrent.futures import ThreadPoolExecutor
import copy, hashlib, html, io, json, math, os, random, re, time
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import streamlit as st

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

st.set_page_config(page_title="A TU RITMO", page_icon="💪", layout="centered")

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root { color-scheme: light; }
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background:#F1E7D7!important;color:#1A3532!important;font-family:'Plus Jakarta Sans',sans-serif!important
}
[data-testid="stHeader"] {background:transparent!important}
[data-testid="stMainBlockContainer"] {max-width:820px;padding-top:4.25rem!important;padding-bottom:4rem!important}
h1,h2,h3 {font-family:'Outfit',sans-serif!important;color:#174D47!important;letter-spacing:-.02em}
h1 {font-size:clamp(2rem,5vw,2.7rem)!important;margin-top:.2rem!important}

[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label,
[data-testid="stMarkdownContainer"] > p, [data-testid="stMarkdownContainer"] > ul li,
[data-testid="stMarkdownContainer"] > ol li, [data-testid="stText"],
[data-testid="stRadio"] label, [data-testid="stRadio"] label *,
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] label *,
[data-testid="stAlert"] * {color:#1A3532!important}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {color:#3E5B53!important}
[data-testid="stCheckbox"] label span:first-child {border-color:#174D47!important}

/* Regla global de botones:
   - Secundario activo: fondo oscuro (#202522) -> letra blanca (#FFFFFF)
   - Primario activo: fondo claro (#C9E98B) -> letra oscura (#1A3532)
   - Deshabilitado: fondo claro (#E3ECE0) -> letra oscura (#607A71) */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button {
    background:#202522!important;background-color:#202522!important;color:#FFFFFF!important;
    border:1px solid #202522!important;border-bottom:3px solid #0E1210!important;border-radius:15px!important;
    min-height:46px;width:100%;font-weight:700!important;font-family:'Plus Jakarta Sans',sans-serif!important;
    transition:transform .1s ease,box-shadow .14s ease,background .14s ease;box-shadow:0 4px 10px #14271d1a
}
[data-testid="stButton"] button *, [data-testid="stDownloadButton"] button *, [data-testid="stFormSubmitButton"] button * {
    color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important
}
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
    background:#2F4338!important;background-color:#2F4338!important;border-color:#2F4338!important;
    border-bottom-color:#174D47!important;transform:translateY(-2px);box-shadow:0 7px 16px #14271d28
}
[data-testid="stButton"] button:active, [data-testid="stDownloadButton"] button:active, [data-testid="stFormSubmitButton"] button:active {
    transform:translateY(2px)!important;border-bottom-width:1px!important;box-shadow:0 2px 5px #14271d18!important
}
[data-testid="stButton"] button[kind="primary"] {
    background:#C9E98B!important;background-color:#C9E98B!important;
    border-color:#174D47!important;border-bottom:3px solid #174D47!important;color:#1A3532!important
}
[data-testid="stButton"] button[kind="primary"] * {color:#1A3532!important;-webkit-text-fill-color:#1A3532!important}
[data-testid="stButton"] button[kind="primary"]:hover {
    background:#BCE274!important;background-color:#BCE274!important;border-color:#174D47!important
}
[data-testid="stButton"] button:disabled, [data-testid="stButton"] button[disabled],
[data-testid="stDownloadButton"] button:disabled, [data-testid="stFormSubmitButton"] button:disabled {
    background:#E3ECE0!important;background-color:#E3ECE0!important;
    border:1px solid #C5D4C6!important;border-bottom:2px solid #B5C7B6!important;
    color:#607A71!important;-webkit-text-fill-color:#607A71!important;
    opacity:1!important;transform:none!important;box-shadow:none!important;cursor:not-allowed!important
}
[data-testid="stButton"] button:disabled *, [data-testid="stButton"] button[disabled] * {
    color:#607A71!important;-webkit-text-fill-color:#607A71!important
}

/* Campos de texto y número: fondo oscuro (#174D47) -> letra blanca (#FFFFFF) */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-testid="stNumberInputContainer"] {
    background:#174D47!important;background-color:#174D47!important;border-color:#377368!important;color:#FFFFFF!important
}
[data-baseweb="input"], [data-baseweb="textarea"] {border:1px solid #377368!important;border-radius:13px!important}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stNumberInput"] input,
[data-baseweb="base-input"] input, [data-baseweb="textarea"] textarea {
    background:#174D47!important;background-color:#174D47!important;color:#FFFFFF!important;-webkit-text-fill-color:#FFFFFF!important;caret-color:#C9E98B!important
}
[data-testid="stTextArea"] textarea::placeholder, [data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder, [data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {color:#D2E4DC!important;-webkit-text-fill-color:#D2E4DC!important}
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {border-color:#BDE583!important;box-shadow:0 0 0 3px #BDE58355!important}
[data-baseweb="base-input"] button, [data-testid="stNumberInput"] button {
    background:#174D47!important;background-color:#174D47!important;color:#F8F4E9!important;border-color:#2C685C!important
}
[data-baseweb="base-input"] button svg, [data-testid="stNumberInput"] button svg {fill:#F8F4E9!important;color:#F8F4E9!important}

/* Selectbox y Multiselect: caja en fondo claro (#FAF6EE) -> letra oscura (#1A3532) */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-baseweb="select"] > div {
    background:#FAF6EE!important;background-color:#FAF6EE!important;
    border:1.5px solid #8FA89B!important;border-radius:13px!important;color:#1A3532!important
}
[data-baseweb="select"] > div > div,
[data-baseweb="select"] [role="combobox"],
[data-baseweb="select"] input {
    background:transparent!important;background-color:transparent!important;
    color:#1A3532!important;-webkit-text-fill-color:#1A3532!important
}
[data-baseweb="select"] svg {fill:#174D47!important;color:#174D47!important}

/* Pills/Tags dentro de Multiselect: fondo oscuro verde bosque (#174D47) -> letra clara (#F8F4E9) */
[data-testid="stMultiSelect"] [data-baseweb="tag"],
[data-baseweb="select"] [data-baseweb="tag"],
span[data-baseweb="tag"] {
    background:#174D47!important;background-color:#174D47!important;
    border:1px solid #2C685C!important;border-radius:999px!important;color:#F8F4E9!important
}
[data-baseweb="tag"] span, [data-baseweb="tag"] div, span[data-baseweb="tag"] span {
    background:transparent!important;background-color:transparent!important;
    color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important;font-weight:600!important
}
[data-baseweb="tag"] svg, span[data-baseweb="tag"] svg {fill:#C9E98B!important;color:#C9E98B!important}
[data-baseweb="tag"] svg:hover {fill:#FFFFFF!important;color:#FFFFFF!important}

/* Menú desplegable y calendario: fondo claro (#FAF6EE) -> letra oscura (#1A3532) */
[data-baseweb="popover"], [data-baseweb="popover"] > div,
[data-baseweb="menu"], [data-baseweb="menu"] ul, [role="listbox"] {
    background:#FAF6EE!important;background-color:#FAF6EE!important;border:1px solid #8FA89B!important;color:#1A3532!important
}
[data-baseweb="menu"] li, [role="option"] {
    background:#FAF6EE!important;background-color:#FAF6EE!important;color:#1A3532!important;-webkit-text-fill-color:#1A3532!important
}
[data-baseweb="menu"] li:hover, [role="option"]:hover, [role="option"][aria-selected="true"] {
    background:#E3ECE0!important;background-color:#E3ECE0!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important
}
[data-baseweb="calendar"], [data-baseweb="calendar"] div, [data-baseweb="calendar"] button {
    background:#FAF6EE!important;background-color:#FAF6EE!important;color:#1A3532!important
}
[data-baseweb="calendar"] [aria-selected="true"] {
    background:#174D47!important;background-color:#174D47!important;color:#F8F4E9!important
}

/* Expanders y mensajes de chat: fondo claro (#FAF6EE) -> letra oscura (#174D47 / #1A3532) */
[data-testid="stExpander"], [data-testid="stChatMessage"] {
    background:#FAF6EE!important;background-color:#FAF6EE!important;border:1px solid #C5D4C6!important;border-radius:16px!important;margin-bottom:.7rem!important
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary:focus,
[data-testid="stExpander"] summary:active,
[data-testid="stExpander"] details[open] > summary {
    background:#FAF6EE!important;background-color:#FAF6EE!important;
    color:#174D47!important;-webkit-text-fill-color:#174D47!important;border-radius:15px!important
}
[data-testid="stExpander"] summary:hover {
    background:#EDF3E9!important;background-color:#EDF3E9!important;
    color:#174D47!important;-webkit-text-fill-color:#174D47!important
}
[data-testid="stExpander"] summary svg {fill:#174D47!important;color:#174D47!important}
[data-testid="stExpander"] p, [data-testid="stExpander"] label, [data-testid="stExpander"] strong,
[data-testid="stChatMessage"] * {color:#1A3532!important;-webkit-text-fill-color:#1A3532!important}
[data-testid="stAlert"] {border-radius:14px!important}

/* Insignia superior completa sin cortes */
.brand-wrap {display:flex;align-items:center;margin:0 0 .85rem 0;padding-top:.2rem}
.brand {
    display:inline-flex!important;align-items:center!important;gap:.5rem!important;
    font-family:'Outfit',sans-serif!important;font-weight:800!important;letter-spacing:.16em!important;
    font-size:.9rem!important;line-height:1.3!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important;
    background:#E3ECE0!important;border:1px solid #B7CCB8!important;border-radius:999px!important;padding:.38rem .95rem!important
}
.brand-arrow {
    background:#174D47!important;color:#C9E98B!important;-webkit-text-fill-color:#C9E98B!important;
    border-radius:999px;width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center;font-size:.82rem;letter-spacing:0
}

.kicker {color:#3E5B53!important;font-size:.83rem;font-weight:700;letter-spacing:.06em;margin-bottom:.5rem}
.progress {height:10px;background:#D1DCC5;border-radius:100px;overflow:hidden;margin:.8rem 0 1.6rem}
.progress > div {height:100%;background:linear-gradient(90deg,#174D47,#8FBE67);border-radius:100px;transition:width .25s ease}

.question-card, [data-testid="stMarkdownContainer"] .question-card {
    background:#174D47!important;border:1px solid #2C685C!important;border-radius:22px!important;
    padding:1.65rem 1.4rem!important;box-shadow:0 12px 30px #14271d14!important;margin-bottom:1.1rem!important;text-align:center!important
}
.question-card h2, [data-testid="stMarkdownContainer"] .question-card h2 {
    font-family:'Outfit',sans-serif!important;font-size:clamp(1.4rem,4vw,1.9rem)!important;margin:0!important;color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important;text-align:center!important
}
.question-card p, [data-testid="stMarkdownContainer"] .question-card p {
    color:#E2EFE5!important;-webkit-text-fill-color:#E2EFE5!important;margin:.6rem 0 0!important;text-align:center!important
}

.quick-bar {
    background:#FAF6EE!important;border:1px solid #C5D4C6!important;border-radius:16px!important;
    padding:.75rem 1rem!important;margin:.4rem 0 .6rem!important;display:flex;flex-wrap:wrap;gap:.45rem;align-items:center
}
.quick-pill {
    background:#E3ECE0!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important;
    border:1px solid #C2D4C0!important;border-radius:999px!important;padding:.24rem .75rem!important;font-size:.82rem!important;font-weight:700!important
}

.day-card-info {
    background:#FAF6EE!important;border:1px solid #C5D4C6!important;border-radius:14px!important;
    padding:.55rem .75rem!important;margin-bottom:.35rem!important;text-align:center!important
}
.day-card-info.active {background:#174D47!important;border-color:#174D47!important}
.day-card-title {font-family:'Outfit',sans-serif!important;font-weight:700!important;font-size:.95rem!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important}
.day-card-info.active .day-card-title {color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important}
.day-card-sub {font-size:.78rem!important;font-weight:600!important;color:#3E5B53!important;-webkit-text-fill-color:#3E5B53!important;margin-top:.15rem!important}
.day-card-info.active .day-card-sub {color:#C9E98B!important;-webkit-text-fill-color:#C9E98B!important}

.routine-summary, [data-testid="stMarkdownContainer"] .routine-summary {
    background:#174D47!important;color:#F8F4E9!important;border-radius:20px!important;padding:1.25rem 1.4rem!important;margin:.85rem 0!important
}
.routine-summary-kicker {font-size:.76rem!important;font-weight:800!important;letter-spacing:.12em!important;color:#C9E98B!important;-webkit-text-fill-color:#C9E98B!important;text-transform:uppercase!important}
.routine-summary-title {font-family:'Outfit',sans-serif!important;font-size:1.32rem!important;font-weight:700!important;color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important;margin:.2rem 0 0!important}
.routine-summary-note {margin:.55rem 0 0!important;padding-top:.55rem!important;border-top:1px solid #2C685C!important;font-size:.93rem!important;color:#E6F2E9!important;-webkit-text-fill-color:#E6F2E9!important}

.workout-progress-box {
    background:#FAF6EE!important;border:1px solid #C5D4C6!important;border-radius:16px!important;
    padding:.85rem 1.1rem!important;margin:.6rem 0 .8rem!important
}
.workout-progress-box.done {background:#174D47!important;border-color:#C9E98B!important}
.workout-progress-top {display:flex;justify-content:space-between;align-items:center;font-size:.88rem!important;font-weight:700!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important;margin-bottom:.42rem!important}
.workout-progress-box.done .workout-progress-top {color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important}
.workout-progress-track {height:10px;background:#DCE6D5;border-radius:999px;overflow:hidden}
.workout-progress-box.done .workout-progress-track {background:#2C685C}
.workout-progress-fill {height:100%;background:linear-gradient(90deg,#174D47,#7BB657);border-radius:999px;transition:width .25s ease}
.workout-progress-box.done .workout-progress-fill {background:#C9E98B}

.timer-card {
    background:#174D47!important;border:2px solid #C9E98B!important;border-radius:18px!important;
    padding:1rem 1.25rem!important;margin:.6rem 0 .85rem!important;box-shadow:0 8px 20px #14271d22!important
}
.timer-top {display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap}
.timer-label {font-size:.84rem!important;font-weight:700!important;color:#C9E98B!important;-webkit-text-fill-color:#C9E98B!important;text-transform:uppercase!important;letter-spacing:.06em!important}
.timer-sub {font-size:.95rem!important;font-weight:600!important;color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important;margin-top:.15rem!important}
.timer-digits {font-family:'Outfit',sans-serif!important;font-size:2.1rem!important;font-weight:800!important;color:#C9E98B!important;-webkit-text-fill-color:#C9E98B!important;font-variant-numeric:tabular-nums}
.timer-track {height:7px;background:#2C685C;border-radius:999px;overflow:hidden;margin-top:.65rem}
.timer-fill {height:100%;background:#C9E98B;border-radius:999px;transition:width .4s linear}

.exercise-card {
    background:#FAF6EE!important;border:1px solid #C5D4C6!important;border-left:6px solid #174D47!important;
    border-radius:18px!important;padding:.95rem 1.1rem!important;margin:.7rem 0 .35rem!important;
    display:flex;gap:1rem;align-items:center;transition:border-color .2s,background .2s
}
.exercise-card.completed {border-left-color:#7BB657!important;background:#F1F8EA!important}
.exercise-thumb-wrap {
    width:96px;height:96px;min-width:96px;border-radius:14px;overflow:hidden;
    border:1px solid #C5D4C6;background:#E8EFE3;display:flex;align-items:center;justify-content:center
}
.exercise-thumb-wrap img {width:100%;height:100%;object-fit:cover;display:block}
.exercise-thumb-fallback {
    width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;
    background:#E3ECE0!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important;font-size:1.55rem!important;font-weight:800!important
}
.exercise-body {flex:1;min-width:0}
.exercise-card-header {display:flex;align-items:center;gap:.6rem;margin-bottom:.38rem}
.exercise-badge {
    background:#174D47!important;color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important;
    font-family:'Outfit',sans-serif!important;font-weight:800!important;font-size:.84rem!important;
    min-width:28px!important;height:28px!important;border-radius:999px!important;
    display:inline-flex!important;align-items:center!important;justify-content:center!important
}
.exercise-title {font-family:'Outfit',sans-serif!important;font-size:1.08rem!important;font-weight:700!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important}
.exercise-tags {display:flex;flex-wrap:wrap;gap:.35rem;margin-bottom:.58rem}
.exercise-tag {background:#E3ECE0!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important;border:1px solid #C2D4C0!important;border-radius:999px!important;padding:.15rem .62rem!important;font-size:.77rem!important;font-weight:650!important}
.exercise-metrics {display:grid;grid-template-columns:repeat(4,1fr);gap:.42rem}
.metric-box {background:#EDF3E9!important;border:1px solid #D0DDD0!important;border-radius:11px!important;padding:.38rem .3rem!important;text-align:center!important}
.metric-label {font-size:.68rem!important;font-weight:700!important;text-transform:uppercase!important;color:#3E5B53!important;-webkit-text-fill-color:#3E5B53!important}
.metric-value {font-family:'Outfit',sans-serif!important;font-size:.96rem!important;font-weight:800!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important;margin-top:.08rem!important}

.feedback-card {
    background:#FAF6EE!important;border:1px solid #C5D4C6!important;border-radius:18px!important;
    padding:1.1rem 1.25rem!important;margin:1rem 0 .7rem!important
}
.feedback-title {font-family:'Outfit',sans-serif!important;font-size:1.1rem!important;font-weight:700!important;color:#174D47!important;-webkit-text-fill-color:#174D47!important;margin-bottom:.25rem!important}
.feedback-sub {font-size:.88rem!important;color:#3E5B53!important;-webkit-text-fill-color:#3E5B53!important}

@keyframes pulseSlide {0%{background-position:200% 0}100%{background-position:-200% 0}}
@keyframes tipFadeIn {0%{opacity:.2;transform:translateY(4px)}100%{opacity:1;transform:translateY(0)}}
.waiting-card {
    background:#174D47!important;border:1px solid #2C685C!important;border-radius:20px!important;
    padding:1.45rem 1.5rem!important;margin:1rem 0!important;box-shadow:0 10px 24px #14271d18!important
}
.waiting-title {font-family:'Outfit',sans-serif!important;font-size:1.15rem!important;font-weight:700!important;color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important;margin-bottom:.35rem!important}
.waiting-sub {font-size:.9rem!important;color:#C9E98B!important;-webkit-text-fill-color:#C9E98B!important;margin-bottom:.85rem!important}
.waiting-bar {
    height:8px;border-radius:999px;margin-bottom:.9rem;
    background:linear-gradient(90deg,#2C685C 25%,#C9E98B 50%,#2C685C 75%);background-size:200% 100%;
    animation:pulseSlide 1.8s linear infinite
}
.waiting-tip {
    background:#215E57!important;border:1px solid #357A71!important;border-radius:14px!important;padding:.85rem 1rem!important;
    font-size:.94rem!important;color:#F8F4E9!important;-webkit-text-fill-color:#F8F4E9!important;line-height:1.45!important;
    animation:tipFadeIn .35s ease
}
.waiting-tip-meta {
    font-size:.74rem!important;font-weight:700!important;letter-spacing:.08em!important;text-transform:uppercase!important;
    color:#C9E98B!important;-webkit-text-fill-color:#C9E98B!important;margin-bottom:.3rem!important
}
@media(max-width:640px){
    [data-testid="stMainBlockContainer"]{padding:4rem .85rem 3rem!important}
    .exercise-card{flex-direction:column;align-items:stretch}
    .exercise-thumb-wrap{width:100%;height:140px}
    .exercise-metrics{grid-template-columns:repeat(2,1fr)}
}
#MainMenu, footer {visibility:hidden}
</style>''', unsafe_allow_html=True)

A = st.session_state.setdefault("respuestas", {})
st.session_state.setdefault("indice_pregunta", 0)
st.session_state.setdefault("perfil_finalizado", False)
st.session_state.setdefault("etapa_plan", 4)
st.session_state.setdefault("borrador_plan", {})

OBJ = ["Ganar masa muscular", "Ganar fuerza", "Mejorar resistencia", "Acondicionamiento general", "Otro"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_CORTOS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
EQUIPO_OPCIONES = ["Sin equipamiento", "Mancuernas", "Bandas", "Barra y discos", "Banco", "Máquinas", "Poleas", "Pesas rusas", "Otro"]
MUSCULOS_OPCIONES = ["Piernas", "Glúteos", "Espalda", "Pecho", "Hombros", "Brazos", "Abdomen", "Sin preferencia / cuerpo completo"]
BASE_IMAGENES_GITHUB = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"

MODELOS_GEMMA = [
    "google/gemma-4-31b-it:free", "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free", "nvidia/nemotron-3.5-lightning:free",
    "xingchen-agi/xing4.0-29b-a4b:free", "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/free", "openrouter/free",
]

CONSEJOS_ESPERA = [
    "💧 Hidratación deportiva: tomá sorbos chicos de agua entre series en lugar de grandes cantidades de golpe.",
    "🫁 Respiración en fuerza: exhalá al empujar o levantar la carga e inhalá de forma controlada al bajar.",
    "⏱️ Descansos inteligentes: respetar la pausa entre series recupera energía muscular y mejora tu rendimiento.",
    "🔥 Entrada en calor: 5 minutos de movilidad articular lubrican las articulaciones y reducen el riesgo de lesión.",
    "🎯 Técnica sobre carga: dominar el recorrido completo del movimiento activa más fibras que usar peso excesivo.",
    "🦴 Postura lumbar: activá el abdomen antes de cada repetición para proteger la columna en sentadillas y remos.",
    "🛌 Recuperación muscular: el músculo crece y se repara mientras dormís, no solo mientras entrenás.",
    "📈 Sobrecarga progresiva: cuando completes todas las repeticiones con buena forma, subí de a poco el estímulo.",
    "👟 Calzado estable: para sentadillas y peso muerto, elegí zapatillas de suela firme que te den buen apoyo.",
    "🥗 Energía post-entreno: combinar proteínas y carbohidratos después de entrenar acelera la recuperación.",
    "🧘 Movilidad activa: estirar suavemente al finalizar ayuda a bajar las pulsaciones y relajar la tensión.",
    "⚡ Fase excéntrica: bajá el peso en 2 o 3 segundos; controlar el descenso multiplica el estímulo muscular.",
    "🩺 Escuchá tu cuerpo: la fatiga muscular es normal, pero ante un pinchazo articular frená y cambiá el ejercicio.",
    "🔄 Simetría corporal: en ejercicios a un brazo o una pierna, empezá siempre por tu lado menos hábil.",
]

TRAD = {
    "quadriceps": "Cuádriceps", "hamstrings": "Isquiotibiales", "calves": "Gemelos", "abductors": "Abductores",
    "adductors": "Aductores", "glutes": "Glúteos", "lats": "Dorsales", "middle back": "Espalda media",
    "lower back": "Zona lumbar", "traps": "Trapecios", "chest": "Pecho", "shoulders": "Hombros",
    "biceps": "Bíceps", "triceps": "Tríceps", "forearms": "Antebrazos", "abdominals": "Abdomen", "neck": "Cuello",
    "body only": "Peso corporal", "dumbbell": "Mancuernas", "bands": "Bandas elásticas", "barbell": "Barra y discos",
    "cable": "Poleas", "kettlebells": "Pesas rusas", "machine": "Máquina", "exercise ball": "Pelota de estabilidad",
    "foam roll": "Rodillo de espuma", "medicine ball": "Pelota medicinal", "e-z curl bar": "Barra Z", "other": "Otro elemento",
    "beginner": "Principiante", "intermediate": "Intermedio", "expert": "Avanzado",
    "strength": "Fuerza", "stretching": "Movilidad / Estiramiento", "plyometrics": "Pliometría / Dinámico",
    "cardio": "Cardio", "powerlifting": "Fuerza máxima", "strongman": "Fuerza funcional", "olympic weightlifting": "Halterofilia",
}

KEYWORDS_MUSCULOS = {
    "Piernas": ("pierna", "cuadricep", "cuádricep", "isquio", "femoral", "gemelo", "pantorrilla", "abductor", "aductor", "tren inferior"),
    "Glúteos": ("gluteo", "glúteo", "cola", "cadera", "tren inferior"),
    "Espalda": ("espalda", "dorsal", "lumbar", "trapecio", "remo", "tren superior"),
    "Pecho": ("pecho", "pectoral", "flexion", "flexión", "tren superior"),
    "Hombros": ("hombro", "deltoide", "elevacion lateral", "elevación lateral", "press militar", "tren superior"),
    "Brazos": ("brazo", "bicep", "bícep", "tricep", "trícep", "antebrazo", "tren superior"),
    "Abdomen": ("abdomen", "abdominal", "core", "zona media", "plancha", "oblicuo"),
}

MUSCULOS_CATALOGO = {
    "Piernas": {"quadriceps", "hamstrings", "calves", "abductors", "adductors"},
    "Glúteos": {"glutes"}, "Espalda": {"lats", "middle back", "lower back", "traps"},
    "Pecho": {"chest"}, "Hombros": {"shoulders"},
    "Brazos": {"biceps", "triceps", "forearms"}, "Abdomen": {"abdominals"},
}
EQUIPO_CATALOGO = {"Mancuernas": "dumbbell", "Bandas": "bands", "Barra y discos": "barbell", "Poleas": "cable", "Pesas rusas": "kettlebells"}


def nombre_usuario():
    p = st.session_state.get("perfil", {}).get("general", {})
    return (p.get("nombre") or A.get("nombre") or "").strip()


def nombre_ia():
    p = st.session_state.get("perfil", {}).get("general", {})
    return (p.get("nombre_ia") or A.get("nombre_ia") or "").strip() or "Gemma"


def tr(val):
    if isinstance(val, list):
        return ", ".join(TRAD.get(x.casefold(), x.replace("_", " ").capitalize()) for x in val)
    return TRAD.get(str(val).casefold(), str(val).replace("_", " ").capitalize()) if val else ""


def formatear_duracion(segundos):
    mins, segs = divmod(max(0, int(segundos)), 60)
    return f"{mins} min {segs:02d} s" if mins and segs else (f"{mins} min" if mins else f"{segs} s")


def formatear_reloj(segundos):
    mins, segs = divmod(max(0, int(segundos)), 60)
    return f"{mins:02d}:{segs:02d}"


def rango_tiempo_segundos(minutos):
    """Rango permitido: mínimo -5% y máximo +3% del tiempo pedido."""
    objetivo = int(minutos) * 60
    return math.ceil(objetivo * 0.95), math.floor(objetivo * 1.03)


def detectar_musculos_en_texto(texto):
    t = (texto or "").casefold()
    if any(f in t for f in ("cuerpo completo", "todo el cuerpo", "otros musculos", "otros músculos", "de todo un poco")):
        return list(KEYWORDS_MUSCULOS)
    return [g for g, claves in KEYWORDS_MUSCULOS.items() if any(c in t for c in claves)]


def detectar_nivel_en_texto(texto):
    t = (texto or "").casefold()
    if any(w in t for w in ("principiante", "basico", "básico", "basicos", "básicos", "facil", "fácil", "suave", "inicial")):
        return "Básicos / Principiante"
    if any(w in t for w in ("complejo", "complejos", "avanzado", "avanzados", "dificil", "difícil", "exigente", "intenso")):
        return "Más complejos / Avanzado"
    return "Intermedio" if "intermedio" in t else None


def q(key, title, kind, options=None, required=True, hint="", **extra):
    return dict(key=key, title=title, kind=kind, options=options or [], required=required, hint=hint, **extra)


# Etapa 1: Perfil personalizado (nombre, nombre de IA, experiencia, equipo y restricciones).
def preguntas():
    p = [
        q("nombre", "¿Cómo te llamás?", "text", required=False, hint="Opcional: lo usamos para personalizar tus rutinas."),
        q("nombre_ia", "¿Qué nombre querés darle a tu asistente?", "text", required=False, hint="Opcional: por defecto se llama Gemma."),
        q("experiencia", "¿Qué experiencia tenés entrenando?", "single", ["Nunca entrené", "Principiante", "Intermedio", "Avanzado"]),
        q("equipo", "¿Qué equipamiento tenés disponible?", "multi", EQUIPO_OPCIONES),
    ]
    if "Máquinas" in A.get("equipo", []) or "Otro" in A.get("equipo", []):
        p.append(q("detalle_equipo", "¿Qué máquinas u otros elementos tenés?", "textarea", hint="Por ejemplo: prensa de piernas, bicicleta fija."))
    p.append(q("restricciones", "¿Tenés alguna restricción para hacer ejercicio o indicaciones profesionales que deban respetarse?", "single", ["No", "Sí", "No estoy segura/o"]))
    return p


def error_de(p):
    key, val = p["key"], A.get(p["key"])
    if p["required"] and (val is None or val == "" or val == [] or isinstance(val, str) and not val.strip()):
        return "Completá esta respuesta para continuar."
    if key == "equipo" and isinstance(val, list) and "Sin equipamiento" in val and len(val) > 1:
        return "Elegí «Sin equipamiento» o las demás opciones, no ambas."
    return None


def siguiente():
    lista = preguntas()
    claves = [x["key"] for x in lista]
    actual = st.session_state.get("clave_pregunta_actual")
    nuevo = (claves.index(actual) + 1) if actual in claves else (st.session_state["indice_pregunta"] + 1)
    if nuevo >= len(lista):
        st.session_state["perfil"] = {
            "general": {
                "nombre": A.get("nombre", "").strip(),
                "nombre_ia": A.get("nombre_ia", "").strip() or "Gemma",
                "experiencia": A.get("experiencia"),
            },
            "lugar": {
                "equipamiento": A.get("equipo", []),
                "detalle_equipamiento": A.get("detalle_equipo", "").strip() if any(x in A.get("equipo", []) for x in ["Máquinas", "Otro"]) else "",
            },
            "actividad": {"restricciones": A.get("restricciones")},
        }
        st.session_state["perfil_finalizado"] = True
    else:
        st.session_state["indice_pregunta"] = nuevo
    st.rerun()


def franjas_validas(texto):
    if not texto.strip() or texto.strip().casefold() == "sin preferencia":
        return True
    for parte in texto.split(","):
        m = re.fullmatch(r"\s*([01]\d|2[0-3]):([0-5]\d)\s*-\s*([01]\d|2[0-3]):([0-5]\d)\s*", parte)
        if not m or int(m[3]) * 60 + int(m[4]) <= int(m[1]) * 60 + int(m[2]):
            return False
    return True


def plan_val(k, default=None):
    return st.session_state["borrador_plan"].get(k, default)


def plan_set(k, v):
    st.session_state["borrador_plan"][k] = v


# Etapa 2: Planificación directa sin preguntas repetidas.
def plan_preguntas():
    periodo = st.session_state["periodo_elegido"]
    mes, hoy = periodo == "Cuatro semanas", periodo == "Una sesión para hoy"
    p = [q("plan_objetivo", "¿Cuál es tu objetivo para este plan?", "single", OBJ)]
    if plan_val("plan_objetivo") == "Otro":
        p.append(q("plan_otro_objetivo", "Describí tu objetivo para este plan", "text"))
    p += [
        q("plan_prioridades", "¿Qué músculos querés priorizar en este plan?", "multi", MUSCULOS_OPCIONES),
        q("plan_cambiar_equipo", "¿Querés cambiar el equipamiento habitual para este plan?", "single", ["No, mantener mi perfil", "Sí, cambiarlo"]),
    ]
    if plan_val("plan_cambiar_equipo") == "Sí, cambiarlo":
        p.append(q("plan_equipo", "¿Qué equipamiento vas a usar?", "multi", EQUIPO_OPCIONES))
        if any(x in plan_val("plan_equipo", []) for x in ("Máquinas", "Otro")):
            p.append(q("plan_detalle_equipo", "¿Qué máquinas u otros elementos vas a usar?", "textarea"))
    if hoy:
        p += [
            q("plan_minutos_hoy", "¿Cuántos minutos tenés hoy?", "number", minimum=1),
            q("plan_hora_hoy", "¿A qué hora preferís empezar?", "text", required=False, hint="Opcional: HH:MM o dejalo vacío (Sin preferencia)"),
        ]
    else:
        p.append(q("plan_inicio", "¿Cuándo querés empezar el plan?", "date"))
        if mes:
            p.append(q("plan_misma_disponibilidad", "¿Tu disponibilidad se mantiene las cuatro semanas?", "single", ["Sí", "No, quiero ajustar cada semana"]))
        semanas = 4 if mes and plan_val("plan_misma_disponibilidad") == "No, quiero ajustar cada semana" else 1
        for i in range(semanas):
            p.append(q(f"plan_dias_{i}", f"¿Qué días vas a entrenar en la semana {i+1}?" if semanas > 1 else "¿Qué días vas a entrenar?", "multi", DIAS))
            if plan_val(f"plan_dias_{i}"):
                p.append(q(f"plan_disponibilidad_{i}", "¿Cuánto tiempo y en qué horarios podés entrenar?", "availability", week=i, hint="Completá los días seleccionados en una sola pantalla."))
        p.append(q("plan_excepciones_equipo", "¿Querés cambiar el equipamiento en alguna sesión?", "single", ["No", "Sí"]))
        if plan_val("plan_excepciones_equipo") == "Sí":
            p.append(q("plan_excepciones", "¿Qué sesiones necesitan cambios?", "exceptions", required=False, hint="Solo modificá las sesiones que lo necesiten."))
    p.append(q("plan_sin_reciente", "¿Entrenaste recientemente?", "single", ["Sí", "No entrené recientemente"]))
    if plan_val("plan_sin_reciente") == "Sí":
        p += [
            q("plan_ultima_fecha", "¿Cuándo fue tu última sesión?", "date_past"),
            q("plan_ultimos_musculos", "¿Qué músculos trabajaste en esa sesión?", "multi", MUSCULOS_OPCIONES[:-1] + ["Cuerpo completo"]),
        ]
    p.append(q("plan_otras", "¿Vas a realizar otras actividades físicas en este período?", "textarea", required=False, hint="Opcional: indicá actividad, días y duración."))
    if hoy:
        p += [
            q("plan_energia", "¿Cómo sentís tu energía hoy?", "single", ["Baja", "Media", "Alta"]),
            q("plan_molestias", "¿Tenés molestias musculares por entrenamientos anteriores?", "single", ["No", "Sí, molestias musculares habituales", "Tengo dolor o una lesión", "No estoy segura/o"]),
        ]
        if plan_val("plan_molestias") == "Sí, molestias musculares habituales":
            p.append(q("plan_zona", "¿En qué zona sentís esas molestias?", "text"))
    p.append(q("plan_preferencias_ejercicios", "¿Querés evitar o incluir algún ejercicio en particular?", "avoid_include", required=False, hint="Opcional: completá uno, ambos o continuá sin escribir nada."))
    if mes:
        p.append(q("plan_variedad", "¿Preferís una estructura similar o variar ejercicios entre semanas?", "single", ["Estructura similar", "Mayor variedad", "Sin preferencia"]))
    return p


def iniciar_plan():
    perfil = st.session_state["perfil"]
    st.session_state["borrador_plan"] = {
        "plan_cambiar_equipo": "No, mantener mi perfil",
        "plan_equipo": list(perfil["lugar"]["equipamiento"]),
        "plan_detalle_equipo": perfil["lugar"]["detalle_equipamiento"],
        "plan_inicio": date.today(), "plan_misma_disponibilidad": "Sí",
        "plan_excepciones_equipo": "No", "plan_ultima_fecha": date.today(),
    }
    st.session_state["indice_plan"], st.session_state["etapa_plan"] = 0, 5


def plan_error(p):
    key, val = p["key"], plan_val(p["key"])
    if p["kind"] in ("availability", "exceptions", "avoid_include"):
        return None
    if p["required"] and (val is None or val == "" or val == [] or isinstance(val, str) and not val.strip()):
        return "Completá esta respuesta para continuar."
    if key == "plan_prioridades" and "Sin preferencia / cuerpo completo" in val and len(val) > 1:
        return "Elegí músculos específicos o Sin preferencia, no ambos."
    if key == "plan_equipo" and "Sin equipamiento" in val and len(val) > 1:
        return "Elegí Sin equipamiento o los elementos disponibles, no ambos."
    if key == "plan_hora_hoy" and val and val.strip().casefold() != "sin preferencia" and not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", val.strip()):
        return "Usá HH:MM o dejalo vacío."
    if key == "plan_inicio" and val < date.today():
        return "La fecha de inicio no puede ser anterior a hoy."
    if key == "plan_ultima_fecha" and val > date.today():
        return "La última sesión no puede estar en el futuro."
    return None


def distribuir_enfoque_semanal(sesiones, prioridades):
    """Asigna enfoque muscular diario en planes multi-sesión evitando repetir grupos en días seguidos."""
    if not sesiones:
        return sesiones
    grupos = [m for m in (prioridades or []) if m in MUSCULOS_CATALOGO]
    n = len(sesiones)
    if n == 1:
        sesiones[0]["prioridades_dia"] = list(prioridades or ["Sin preferencia / cuerpo completo"])
        sesiones[0]["etiqueta_enfoque"] = ", ".join(grupos) if grupos else "Cuerpo completo"
        return sesiones

    if not grupos:
        bloques_base = [
            (["Piernas", "Glúteos"], "Piernas y Glúteos"),
            (["Pecho", "Hombros", "Brazos"], "Empuje (Pecho/Hombros)"),
            (["Espalda", "Abdomen"], "Tracción (Espalda/Core)"),
            (["Piernas", "Abdomen"], "Tren inferior y Core"),
        ]
        if n == 2:
            bloques_base = [
                (["Piernas", "Glúteos", "Abdomen"], "Tren inferior y Core"),
                (["Espalda", "Pecho", "Hombros", "Brazos"], "Tren superior"),
            ]
        for idx, ses in enumerate(sesiones):
            pr, etq = bloques_base[idx % len(bloques_base)]
            ses["prioridades_dia"] = list(pr)
            ses["etiqueta_enfoque"] = etq
        return sesiones

    if len(grupos) == 1:
        for ses in sesiones:
            ses["prioridades_dia"] = [grupos[0]]
            ses["etiqueta_enfoque"] = grupos[0]
        return sesiones

    tam_bloque = 2 if len(grupos) >= 4 else 1
    bloques = [grupos[i:i + tam_bloque] for i in range(0, len(grupos), tam_bloque)]
    for idx, ses in enumerate(sesiones):
        elegido = bloques[idx % len(bloques)]
        ses["prioridades_dia"] = list(elegido)
        ses["etiqueta_enfoque"] = " y ".join(elegido)
    return sesiones


def plan_sesiones():
    periodo, perfil = st.session_state["periodo_elegido"], st.session_state["perfil"]
    equipo = list(plan_val("plan_equipo", [])) if plan_val("plan_cambiar_equipo") == "Sí, cambiarlo" else list(perfil["lugar"]["equipamiento"])
    prioridades = list(plan_val("plan_prioridades", []))
    if periodo == "Una sesión para hoy":
        sesiones = [{"fecha": date.today().isoformat(), "dia": DIAS[date.today().weekday()], "minutos": int(plan_val("plan_minutos_hoy")),
                     "horario_preferido": (plan_val("plan_hora_hoy") or "").strip() or "Sin preferencia", "equipamiento": equipo}]
        return distribuir_enfoque_semanal(sesiones, prioridades)
    inicio = plan_val("plan_inicio", date.today())
    n = 4 if periodo == "Cuatro semanas" else 1
    diferente = n == 4 and plan_val("plan_misma_disponibilidad") == "No, quiero ajustar cada semana"
    sesiones = []
    for d_idx in range(n * 7):
        fecha = inicio + timedelta(days=d_idx)
        i = (d_idx // 7) if diferente else 0
        dia = DIAS[fecha.weekday()]
        if dia in plan_val(f"plan_dias_{i}", []):
            datos = plan_val(f"plan_disponibilidad_{i}", {}).get(dia, {})
            ses = {"fecha": fecha.isoformat(), "dia": dia, "minutos": int(datos["minutos"]) if datos.get("minutos") else None,
                   "franjas_disponibles": datos.get("franjas") or "Sin preferencia", "equipamiento": list(equipo)}
            cambio = plan_val("plan_excepciones", {}).get(fecha.isoformat(), {})
            if cambio.get("cambiar"):
                ses["equipamiento"] = cambio.get("equipo", list(equipo))
                ses["detalle_equipamiento"] = cambio.get("detalle", "")
            sesiones.append(ses)
    return distribuir_enfoque_semanal(sesiones, prioridades)


def construir_planificacion():
    perfil, periodo = st.session_state["perfil"], st.session_state["periodo_elegido"]
    cambio = plan_val("plan_cambiar_equipo") == "Sí, cambiarlo"
    equipo = list(plan_val("plan_equipo", [])) if cambio else list(perfil["lugar"]["equipamiento"])
    detalle = plan_val("plan_detalle_equipo", "") if cambio else perfil["lugar"]["detalle_equipamiento"]
    objetivo = plan_val("plan_otro_objetivo", "").strip() if plan_val("plan_objetivo") == "Otro" else (plan_val("plan_objetivo") or "")
    errores = []
    if not equipo or ("Sin equipamiento" in equipo and len(equipo) > 1):
        errores.append("Revisá el equipamiento del plan.")
    if any(x in equipo for x in ("Máquinas", "Otro")) and not detalle.strip():
        errores.append("Detallá las máquinas u otros elementos.")
    sesiones = plan_sesiones()
    if not sesiones:
        errores.append("Seleccioná al menos un día de entrenamiento.")
    for s in sesiones:
        if not s.get("minutos") or int(s["minutos"]) < 1:
            errores.append(f"Indicá los minutos disponibles para el {s['fecha']}.")
        if not s["equipamiento"] or ("Sin equipamiento" in s["equipamiento"] and len(s["equipamiento"]) > 1):
            errores.append(f"Revisá el equipamiento del {s['fecha']}.")
        if any(x in s["equipamiento"] for x in ("Máquinas", "Otro")) and not str(s.get("detalle_equipamiento", detalle)).strip():
            errores.append(f"Detallá el equipamiento del {s['fecha']}.")
    plan = {
        "periodo": periodo, "objetivo": objetivo, "prioridades": list(plan_val("plan_prioridades", [])),
        "equipamiento": equipo, "detalle_equipamiento": detalle, "sesiones": sesiones,
        "ultima_sesion": {"fecha": plan_val("plan_ultima_fecha").isoformat(), "musculos": list(plan_val("plan_ultimos_musculos", []))} if plan_val("plan_sin_reciente") == "Sí" else None,
        "otras_actividades": (plan_val("plan_otras") or "").strip() or "Ninguna",
        "energia": plan_val("plan_energia") if periodo == "Una sesión para hoy" else None,
        "molestias": plan_val("plan_molestias") if periodo == "Una sesión para hoy" else None,
        "zona_molestias": plan_val("plan_zona", "") if periodo == "Una sesión para hoy" else "",
        "evitar": (plan_val("plan_evitar") or "").strip(), "incluir": (plan_val("plan_incluir") or "").strip(),
        "variedad": plan_val("plan_variedad") if periodo == "Cuatro semanas" else None,
    }
    return plan, errores


def plan_siguiente():
    lista = plan_preguntas()
    claves = [x["key"] for x in lista]
    actual = st.session_state.get("clave_plan_actual")
    nuevo = (claves.index(actual) + 1) if actual in claves else (st.session_state["indice_plan"] + 1)
    st.session_state["indice_plan"] = nuevo
    if nuevo >= len(lista):
        plan, errores = construir_planificacion()
        if errores:
            st.session_state["indice_plan"] = max(0, len(lista) - 1)
            st.session_state["error_plan"] = " ".join(errores)
        else:
            st.session_state["planificacion"], st.session_state["etapa_plan"] = plan, 6
    st.rerun()


def mostrar_planificacion():
    ia = nombre_ia()
    if st.session_state["etapa_plan"] == 6:
        plan = st.session_state["planificacion"]
        st.markdown('<div class="question-card"><h2>Revisá tu planificación</h2></div>', unsafe_allow_html=True)
        st.write(f"**Período:** {plan['periodo']} · **Objetivo:** {plan['objetivo']}")
        st.write("**Prioridades:** " + ", ".join(plan["prioridades"]))
        vista_ses = [{k: v for k, v in s.items() if k != "prioridades_dia"} for s in plan["sesiones"]]
        st.dataframe(vista_ses, hide_index=True, use_container_width=True)
        st.write("**Otras actividades:** " + plan["otras_actividades"])
        st.write(f"**Evitar:** {plan['evitar'] or 'Sin preferencias'} · **Incluir:** {plan['incluir'] or 'Sin preferencias'}")
        if st.checkbox("Ver todos los datos de esta planificación", key="ver_plan_completo"):
            st.json(plan)
        st.caption(f"Al confirmar vas a poder armar tu rutina con {ia}.")
        izq, _, der = st.columns([1, 1.4, 1])
        with izq:
            if st.button("← Anterior", key="volver_revision"):
                st.session_state["etapa_plan"], st.session_state["indice_plan"] = 5, max(0, len(plan_preguntas()) - 1)
                st.rerun()
        with der:
            if st.button("Confirmar →", key="confirmar_plan", type="primary"):
                if st.session_state["perfil"]["actividad"]["restricciones"] != "No" or plan["molestias"] in ["Tengo dolor o una lesión", "No estoy segura/o"]:
                    st.warning("No está habilitada la generación automática para restricciones médicas, dolor, lesión o dudas al respecto.")
                else:
                    st.session_state["planificacion_confirmada"], st.session_state["etapa_plan"] = copy.deepcopy(plan), 7
                    st.rerun()
        return

    lista = plan_preguntas()
    indice = min(st.session_state.setdefault("indice_plan", 0), len(lista) - 1)
    st.session_state["indice_plan"] = indice
    p = lista[indice]
    key = p["key"]
    st.session_state["clave_plan_actual"] = key
    progreso = round(indice / len(lista) * 100)
    st.markdown(f'<div class="kicker">TU PLAN · PREGUNTA {indice+1} DE {len(lista)} · {progreso}%</div><div class="progress"><div style="width:{progreso}%"></div></div>', unsafe_allow_html=True)
    ayuda = html.escape(p["hint"])
    st.markdown(f'<div class="question-card"><h2>{html.escape(p["title"])}</h2>' + (f'<p>{ayuda}</p>' if ayuda else '') + '</div>', unsafe_allow_html=True)

    if p["kind"] in ("single", "multi"):
        opciones = p["options"]
        for i in range(0, len(opciones), 2):
            pareja = opciones[i:i + 2]
            cols = st.columns([1, 2, 1], gap="small")[1:2] if len(pareja) == 1 else st.columns(2, gap="small")
            for col, op in zip(cols, pareja):
                with col:
                    actual = plan_val(key, [] if p["kind"] == "multi" else None)
                    marcado = (actual == op) if p["kind"] == "single" else (op in actual)
                    if st.button(("✓  " if marcado else "") + op, key=f"plan_op_{key}_{op}", type="primary" if marcado else "secondary", use_container_width=True):
                        if p["kind"] == "single":
                            plan_set(key, op)
                            if (err := plan_error(p)):
                                st.session_state["error_plan"] = err
                                st.rerun()
                            plan_siguiente()
                        else:
                            act = list(plan_val(key, []))
                            act.remove(op) if op in act else act.append(op)
                            plan_set(key, act)
                            st.rerun()
    elif p["kind"] in ("text", "textarea", "number", "date", "date_past"):
        wk = "plan_widget_" + key
        if wk not in st.session_state:
            d = plan_val(key)
            st.session_state[wk] = d if d is not None else (None if p["kind"] == "number" else "")
        if p["kind"] == "text":
            st.text_input("Tu respuesta" if p["required"] else "Tu respuesta (opcional)", key=wk)
        elif p["kind"] == "textarea":
            st.text_area("Tu respuesta" if p["required"] else "Tu respuesta (opcional)", key=wk)
        elif p["kind"] == "number":
            st.number_input("Minutos disponibles", min_value=1, step=1, value=None, key=wk)
        else:
            st.date_input("Fecha", key=wk, min_value=date.today() if p["kind"] == "date" else None, max_value=date.today() if p["kind"] == "date_past" else None)
    elif p["kind"] == "avoid_include":
        st.session_state.setdefault("plan_widget_plan_evitar", plan_val("plan_evitar", ""))
        st.session_state.setdefault("plan_widget_plan_incluir", plan_val("plan_incluir", ""))
        st.text_area("Ejercicios que preferís evitar (opcional)", key="plan_widget_plan_evitar", placeholder="Ej.: burpees, saltos...")
        st.text_area("Ejercicios que te gustaría incluir (opcional)", key="plan_widget_plan_incluir", placeholder="Ej.: hip thrust, plancha...")
    elif p["kind"] == "availability":
        i = p["week"]
        for dia in plan_val(f"plan_dias_{i}", []):
            st.markdown(f"**{dia}**")
            c1, c2 = st.columns(2)
            actual = plan_val(key, {}).get(dia, {})
            with c1:
                st.number_input("Minutos · " + dia, min_value=1, step=1, value=int(actual.get("minutos") or 45), key=f"dispo_min_{i}_{dia}")
            with c2:
                st.text_input("Horarios · " + dia, value=actual.get("franjas", "Sin preferencia"), key=f"dispo_franja_{i}_{dia}", help="HH:MM-HH:MM o Sin preferencia")
    elif p["kind"] == "exceptions":
        cambios = plan_val(key, {})
        for ses in plan_sesiones():
            fecha = ses["fecha"]
            with st.expander("Sesión del " + fecha):
                actual = cambios.get(fecha, {})
                st.checkbox("Modificar equipamiento en esta sesión", value=actual.get("cambiar", False), key=f"exc_check_{fecha}")
                if st.session_state[f"exc_check_{fecha}"]:
                    st.multiselect("Equipamiento", EQUIPO_OPCIONES, default=actual.get("equipo", ses["equipamiento"]), key=f"exc_equipo_{fecha}")
                    st.text_input("Detalle de máquinas u otros elementos", value=actual.get("detalle", ""), key=f"exc_detalle_{fecha}")

    if st.session_state.get("error_plan"):
        st.error(st.session_state.pop("error_plan"))
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    izq, _, der = st.columns([1, 1.4, 1], gap="medium")
    with izq:
        if st.button("← Anterior", key="plan_atras", use_container_width=True):
            claves = [x["key"] for x in lista]
            pos = claves.index(key) if key in claves else indice
            if pos == 0:
                st.session_state["etapa_plan"] = 4
            else:
                st.session_state["indice_plan"] = pos - 1
            st.rerun()
    with der:
        if p["kind"] != "single" and st.button("Continuar →", key="plan_continuar", use_container_width=True):
            if p["kind"] in ("text", "textarea", "number", "date", "date_past"):
                plan_set(key, st.session_state["plan_widget_" + key])
            elif p["kind"] == "avoid_include":
                plan_set("plan_evitar", st.session_state.get("plan_widget_plan_evitar", ""))
                plan_set("plan_incluir", st.session_state.get("plan_widget_plan_incluir", ""))
            elif p["kind"] == "availability":
                i, datos, errs = p["week"], {}, []
                for dia in plan_val(f"plan_dias_{i}", []):
                    m, f = st.session_state.get(f"dispo_min_{i}_{dia}"), st.session_state.get(f"dispo_franja_{i}_{dia}", "")
                    if not m or int(m) < 1:
                        errs.append(f"Indicá los minutos para {dia}.")
                    if not franjas_validas(f):
                        errs.append(f"Revisá el horario de {dia}: HH:MM-HH:MM o Sin preferencia.")
                    datos[dia] = {"minutos": int(m) if m else None, "franjas": f.strip() or "Sin preferencia"}
                plan_set(key, datos)
                if errs:
                    st.session_state["error_plan"] = " ".join(errs)
                    st.rerun()
            elif p["kind"] == "exceptions":
                cambios, errs = {}, []
                for ses in plan_sesiones():
                    fecha = ses["fecha"]
                    if st.session_state.get(f"exc_check_{fecha}"):
                        eq, det = st.session_state[f"exc_equipo_{fecha}"], st.session_state[f"exc_detalle_{fecha}"]
                        if not eq or ("Sin equipamiento" in eq and len(eq) > 1):
                            errs.append(f"Revisá el equipamiento del {fecha}.")
                        if any(x in eq for x in ("Máquinas", "Otro")) and not det.strip():
                            errs.append(f"Detallá las máquinas u otros elementos para el {fecha}.")
                        cambios[fecha] = {"cambiar": True, "equipo": eq, "detalle": det}
                if errs:
                    st.session_state["error_plan"] = " ".join(errs)
                    st.rerun()
                plan_set(key, cambios)
            if (err := plan_error(p)):
                st.session_state["error_plan"] = err
                st.rerun()
            plan_siguiente()
    st.caption("Las respuestas se conservan durante esta sesión.")


# Catálogo y preselección con flexibilización progresiva.
def niveles_desde_preferencia(experiencia, nivel_ajuste=None):
    mapa = {
        "Básicos / Principiante": {"beginner"},
        "Intermedio": {"beginner", "intermediate"},
        "Más complejos / Avanzado": {"intermediate", "expert"},
        "Cualquier nivel": {"beginner", "intermediate", "expert"},
    }
    if nivel_ajuste in mapa:
        return mapa[nivel_ajuste]
    return {"beginner"} | ({"intermediate"} if experiencia in ("Intermedio", "Avanzado") else set()) | ({"expert"} if experiencia == "Avanzado" else set())


def filtrar_catalogo(catalogo, perfil, plan, sesion, min_candidatos=5, prioridades_override=None, nivel_ajuste=None):
    niveles_base = niveles_desde_preferencia(perfil["general"]["experiencia"], nivel_ajuste)
    equipo = sesion["equipamiento"]
    disponibles = {"body only"} | {EQUIPO_CATALOGO[e] for e in equipo if e in EQUIPO_CATALOGO}
    prioridades = prioridades_override if prioridades_override is not None else (sesion.get("prioridades_dia") or plan["prioridades"])
    grupos_activos = [m for m in prioridades if m in MUSCULOS_CATALOGO]
    musculos = set().union(*(MUSCULOS_CATALOGO[m] for m in grupos_activos)) if grupos_activos else set()

    descartados = {"equipamiento": 0, "músculo": 0, "nivel": 0}
    compatibles_eq, revisar_eq = [], []

    for e in catalogo:
        eq, motivo = e.get("equipment"), None
        if not eq:
            motivo = "El catálogo no informa equipamiento."
        elif eq in ("machine", "other"):
            if (eq == "machine" and "Máquinas" in equipo) or (eq == "other" and "Otro" in equipo):
                motivo = "Hay que comprobar el elemento o máquina concreta."
            else:
                descartados["equipamiento"] += 1
                continue
        elif eq not in disponibles:
            descartados["equipamiento"] += 1
            continue

        faltantes = [a for a in (e.get("requiredAccessories") or []) if isinstance(a, str) and a.strip() and not (a.casefold() == "banco" and "Banco" in equipo)]
        if faltantes and not motivo:
            motivo = f"Requiere accesorio no declarado ({', '.join(faltantes)})."

        prim, sec = set(e.get("primaryMuscles") or []), set(e.get("secondaryMuscles") or [])
        es_prim = not musculos or bool(musculos.intersection(prim))
        es_sec = bool(musculos) and not es_prim and bool(musculos.intersection(sec))
        solo_banco = ("bench" in (e.get("name", "") + " " + " ".join(e.get("instructions") or [])).casefold()) and ("Banco" not in equipo)

        fila = {
            "ID": e.get("id", ""), "Ejercicio": e.get("name", ""),
            "Músculos": tr(e.get("primaryMuscles") or []), "Secundarios": tr(e.get("secondaryMuscles") or []),
            "PrimariosRaw": prim, "SecundariosRaw": sec,
            "Nivel": tr(e.get("level", "")), "NivelRaw": e.get("level", ""),
            "Equipamiento": tr(eq) or "Sin información",
            "Categoría": tr(e.get("category", "")), "CategoriaRaw": e.get("category", ""),
            "InstruccionesEn": list(e.get("instructions") or []),
            "Imagenes": list(e.get("images") or []),
        }
        reg = {"fila": fila, "es_prim": es_prim, "es_sec": es_sec, "solo_banco": solo_banco, "motivo": motivo}
        (revisar_eq if motivo else compatibles_eq).append(reg)

    usar_sec, permitir_banco, cats, niveles, pasos = False, False, {"strength"}, set(niveles_base), []

    def faltan():
        if not grupos_activos:
            return sum(1 for r in compatibles_eq if r["fila"]["NivelRaw"] in niveles and r["fila"]["CategoriaRaw"] in cats and not (r["solo_banco"] and not permitir_banco)) < min_candidatos
        for g in grupos_activos:
            sg = MUSCULOS_CATALOGO[g]
            if sum(1 for r in compatibles_eq if r["fila"]["NivelRaw"] in niveles and r["fila"]["CategoriaRaw"] in cats and not (r["solo_banco"] and not permitir_banco) and (sg.intersection(r["fila"]["PrimariosRaw"]) or (usar_sec and sg.intersection(r["fila"]["SecundariosRaw"])))) < min_candidatos:
                return True
        return False

    if faltan():
        usar_sec = permitir_banco = True
        pasos.append("músculos secundarios y mención de banco")
    if faltan():
        cats.update({"plyometrics", "stretching"})
        pasos.append("pliometría y movilidad")
    if faltan() and len(niveles) < 3:
        for nv, et in (("intermediate", "nivel intermedio"), ("beginner", "nivel principiante"), ("expert", "nivel avanzado")):
            if nv not in niveles:
                niveles.add(nv)
                pasos.append(et)
                break

    candidatos, revisar = [], []
    for r in compatibles_eq:
        f = r["fila"]
        if not (r["es_prim"] or (usar_sec and r["es_sec"])):
            descartados["músculo"] += 1
            continue
        if f["NivelRaw"] not in niveles:
            descartados["nivel"] += 1
            continue
        if r["solo_banco"] and not permitir_banco:
            revisar.append(dict(f, Motivo="El texto menciona un banco que no declaraste."))
            continue
        etiquetas = ["Músculo principal" if r["es_prim"] else "Músculo secundario"]
        if f["CategoriaRaw"] != "strength":
            etiquetas.append(f["Categoría"])
        if f["NivelRaw"] not in niveles_base:
            etiquetas.append(f"Nivel {f['Nivel']}")
        candidatos.append(dict(f, Coincidencia=" · ".join(etiquetas)))

    for r in revisar_eq:
        f = r["fila"]
        if (r["es_prim"] or (usar_sec and r["es_sec"])) and f["NivelRaw"] in niveles:
            revisar.append(dict(f, Motivo=r["motivo"]))

    candidatos.sort(key=lambda c: (0 if c["Coincidencia"].startswith("Músculo principal") else 1, 0 if c["CategoriaRaw"] == "strength" else 1, c["ID"]))
    return candidatos, revisar, descartados, {"pasos_aplicados": pasos, "categorias": sorted(cats)}


def obtener_imagenes_ejercicio(rutas_relativas):
    """Busca primero imágenes locales en el proyecto y, si no están, usa las URLs del catálogo."""
    if not rutas_relativas:
        return []
    base_dir = Path(__file__).resolve().parent
    fuentes = []
    for rel in rutas_relativas:
        if not isinstance(rel, str) or not rel.strip():
            continue
        limpia = rel.strip().lstrip("/\\")
        if limpia.startswith(("http://", "https://")):
            fuentes.append(limpia)
            continue
        locales = [base_dir / "exercises" / limpia, base_dir / "images" / limpia, base_dir / limpia]
        encontrada = next((str(p) for p in locales if p.is_file()), None)
        fuentes.append(encontrada or (BASE_IMAGENES_GITHUB + limpia.replace("\\", "/")))
    return fuentes


def obtener_url_miniatura(rutas_relativas):
    """Devuelve URL pública para miniatura HTML directa dentro de la tarjeta."""
    if not rutas_relativas:
        return ""
    for rel in rutas_relativas:
        if isinstance(rel, str) and rel.strip():
            limpia = rel.strip().lstrip("/\\").replace("\\", "/")
            return limpia if limpia.startswith(("http://", "https://")) else (BASE_IMAGENES_GITHUB + limpia)
    return ""


def obtener_api_key():
    try:
        clave = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        clave = ""
    return str(clave or os.getenv("OPENROUTER_API_KEY", "")).strip().strip('"').strip("'")


def extraer_json_gemma(texto):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Respuesta vacía sin texto.")
    limpio = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(limpio)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", limpio, flags=re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise ValueError("JSON inválido.")


def resolver_id_candidato(id_bruto, candidatos):
    if not isinstance(id_bruto, str):
        return None
    limpio = id_bruto.strip()
    for campo in ("ID", "Ejercicio"):
        mapa = {e[campo].casefold(): e["ID"] for e in candidatos}
        if limpio.casefold() in mapa:
            return mapa[limpio.casefold()]
    norm = re.sub(r"[^a-z0-9]", "", limpio.casefold())
    return {re.sub(r"[^a-z0-9]", "", e["ID"].casefold()): e["ID"] for e in candidatos}.get(norm)


def recalcular_tiempo_fila(fila):
    fila["Tiempo (s)"] = 4 * int(fila["Series"]) * int(fila["Repeticiones"]) + (int(fila["Series"]) - 1) * int(fila["Descanso (s)"])
    return fila


def construir_fila_rutina(base, nombre_es, series, reps, descanso, instrucciones_es=None):
    return {
        "ID": base["ID"],
        "Ejercicio": (nombre_es or base["Ejercicio"]).replace("_", " ").strip(),
        "NombreCatalogo": base["Ejercicio"],
        "Músculos": base["Músculos"], "Nivel": base["Nivel"],
        "Equipamiento": base["Equipamiento"], "Categoría": base["Categoría"],
        "Series": series, "Repeticiones": reps, "Descanso (s)": descanso,
        "Tiempo (s)": 4 * series * reps + (series - 1) * descanso,
        "Instrucciones": instrucciones_es or list(base.get("InstruccionesEn") or []),
        "Imagenes": list(base.get("Imagenes") or []),
    }


def total_rutina_segundos(filas):
    return sum(f["Tiempo (s)"] for f in filas) + 60 * max(0, len(filas) - 1)


def ajustar_tiempos_rutina(filas, candidatos, minutos):
    """Calibra series/reps/descansos o ejercicios si la IA quedó fuera de [-5%, +3%]."""
    min_seg, max_seg = rango_tiempo_segundos(minutos)
    por_id = {e["ID"]: e for e in candidatos}
    usados = {f["ID"] for f in filas}
    total = total_rutina_segundos(filas)

    for cand in candidatos:
        if total >= min_seg or len(filas) >= min(12, len(candidatos)):
            break
        if cand["ID"] in usados:
            continue
        for s, r, d in ((3, 10, 60), (2, 10, 45), (2, 8, 30)):
            nueva = construir_fila_rutina(cand, cand["Ejercicio"], s, r, d)
            if total + 60 + nueva["Tiempo (s)"] <= max_seg:
                filas.append(nueva)
                usados.add(cand["ID"])
                total = total_rutina_segundos(filas)
                break

    while total < min_seg:
        cambio = False
        for f in filas:
            if f["Series"] < 5:
                cand_t = total + (4 * f["Repeticiones"] + f["Descanso (s)"])
                if cand_t <= max_seg:
                    f.update(construir_fila_rutina(por_id[f["ID"]], f["Ejercicio"], f["Series"] + 1, f["Repeticiones"], f["Descanso (s)"], f["Instrucciones"]))
                    total, cambio = cand_t, True
                    if total >= min_seg:
                        break
        if total >= min_seg:
            break
        for f in filas:
            if f["Repeticiones"] < 30:
                inc = 2 if f["Repeticiones"] <= 28 else 1
                cand_t = total + 4 * f["Series"] * inc
                if cand_t <= max_seg:
                    f.update(construir_fila_rutina(por_id[f["ID"]], f["Ejercicio"], f["Series"], f["Repeticiones"] + inc, f["Descanso (s)"], f["Instrucciones"]))
                    total, cambio = cand_t, True
                    if total >= min_seg:
                        break
        if total >= min_seg:
            break
        for f in filas:
            if f["Series"] > 1 and f["Descanso (s)"] < 150:
                cand_t = total + 15 * (f["Series"] - 1)
                if cand_t <= max_seg:
                    f.update(construir_fila_rutina(por_id[f["ID"]], f["Ejercicio"], f["Series"], f["Repeticiones"], f["Descanso (s)"] + 15, f["Instrucciones"]))
                    total, cambio = cand_t, True
                    if total >= min_seg:
                        break
        if not cambio:
            break

    while total > max_seg:
        cambio = False
        for f in filas:
            if f["Series"] > 1 and f["Descanso (s)"] >= 45:
                f.update(construir_fila_rutina(por_id[f["ID"]], f["Ejercicio"], f["Series"], f["Repeticiones"], f["Descanso (s)"] - 15, f["Instrucciones"]))
                total, cambio = total_rutina_segundos(filas), True
                if total <= max_seg:
                    break
        if total <= max_seg:
            break
        for f in filas:
            if f["Series"] > 1:
                f.update(construir_fila_rutina(por_id[f["ID"]], f["Ejercicio"], f["Series"] - 1, f["Repeticiones"], f["Descanso (s)"], f["Instrucciones"]))
                total, cambio = total_rutina_segundos(filas), True
                if total <= max_seg:
                    break
        if total <= max_seg:
            break
        for f in filas:
            if f["Repeticiones"] > 6:
                f.update(construir_fila_rutina(por_id[f["ID"]], f["Ejercicio"], f["Series"], f["Repeticiones"] - 2, f["Descanso (s)"], f["Instrucciones"]))
                total, cambio = total_rutina_segundos(filas), True
                if total <= max_seg:
                    break
        if total > max_seg and not cambio and len(filas) > 1:
            filas.pop()
            total, cambio = total_rutina_segundos(filas), True
        if not cambio:
            break

    return filas, total_rutina_segundos(filas)


def validar_rutina_gemma(datos, candidatos, minutos, permitir_deduplicar=False, exigir_rango_tiempo=True):
    if not isinstance(datos, dict) or "ejercicios" not in datos:
        raise ValueError("La respuesta JSON no contiene 'ejercicios'.")
    por_id = {e["ID"]: e for e in candidatos}
    max_ej = min(12, len(candidatos))
    ejercicios = datos["ejercicios"]
    if not isinstance(ejercicios, list) or not ejercicios:
        raise ValueError("La rutina debe tener al menos 1 ejercicio.")
    filas, usados = [], set()
    for e in ejercicios:
        if not isinstance(e, dict) or not {"id", "series", "reps", "descanso"}.issubset(e):
            raise ValueError("Cada ejercicio debe tener id, series, reps y descanso.")
        id_e = resolver_id_candidato(e["id"], candidatos)
        if not id_e:
            raise ValueError(f"El ejercicio '{e['id']}' no está en candidatos.")
        if id_e in usados:
            if permitir_deduplicar:
                continue
            raise ValueError(f"El ejercicio '{id_e}' está repetido.")
        s, r, d = e["series"], e["reps"], e["descanso"]
        if any(isinstance(n, bool) or not isinstance(n, (int, float)) or not float(n).is_integer() for n in (s, r, d)):
            raise ValueError("Series, reps y descanso deben ser enteros.")
        s, r, d = int(s), int(r), int(d)
        if not (1 <= s <= 5 and 1 <= r <= 30 and 0 <= d <= 180):
            raise ValueError("Parámetros fuera de rango (series 1-5, reps 1-30, descanso 0-180).")
        usados.add(id_e)
        inst_raw = e.get("instrucciones_es")
        inst = [str(x).strip() for x in inst_raw if str(x).strip()] if isinstance(inst_raw, list) else (
            [x.strip() for x in inst_raw.splitlines() if x.strip()] if isinstance(inst_raw, str) else []
        )
        filas.append(construir_fila_rutina(por_id[id_e], str(e.get("nombre_es") or ""), s, r, d, inst))

    if not 1 <= len(filas) <= max_ej:
        raise ValueError(f"Debe haber entre 1 y {max_ej} ejercicios distintos.")

    total = total_rutina_segundos(filas)
    min_seg, max_seg = rango_tiempo_segundos(minutos)
    max_teorico = len(candidatos) * 1320 + max(0, len(candidatos) - 1) * 60
    if exigir_rango_tiempo:
        if total > max_seg:
            raise ValueError(f"La rutina dura {formatear_duracion(total)} y supera el máximo de {formatear_duracion(max_seg)} (+3% de {minutos} min).")
        if total < min_seg and max_teorico >= min_seg:
            raise ValueError(f"La rutina dura {formatear_duracion(total)} y es menor al mínimo de {formatear_duracion(min_seg)} (-5% de {minutos} min).")
    return filas, total


def consultar_gemma(contexto, temperatura=0.25, api_key=""):
    """Consulta únicamente modelos gratuitos en OpenRouter sin llamar a st.* (thread-safe)."""
    if not api_key:
        raise RuntimeError("Falta OPENROUTER_API_KEY en .streamlit/secrets.toml o en las variables de entorno.")

    minutos = int(contexto["minutos"])
    min_seg, max_seg = rango_tiempo_segundos(minutos)
    max_ej = int(contexto.get("max_ejercicios", 12))
    ia = contexto.get("nombre_asistente") or "Gemma"
    usuario = contexto.get("nombre_usuario") or ""
    saludo_ctx = f'El usuario se llama "{usuario}" y eligió llamarte "{ia}". ' if usuario else f'El usuario eligió llamarte "{ia}". '

    instrucciones = (
        f'Sos {ia}, asistente de entrenamiento. {saludo_ctx}'
        'Armá o revisá una sesión en español seleccionando ejercicios EXCLUSIVAMENTE de "candidatos". '
        'REGLA 1: copiá cada "id" carácter por carácter desde "candidatos". Prohibido inventar ejercicios. '
        f'REGLA 2: devolvé entre 1 y {max_ej} ejercicios SIN REPETIR NINGÚN ID. '
        f'REGLA 3 (DURACIÓN EXACTA OBLIGATORIA): el usuario pidió {minutos} minutos ({minutos*60} s). '
        f'La duración total DEBE quedar entre {formatear_duracion(min_seg)} ({min_seg} s, -5%) y {formatear_duracion(max_seg)} ({max_seg} s, +3%). '
        'Fórmula exacta: cada ejercicio suma (4 * series * reps) + ((series - 1) * descanso) segundos, más 60 segundos entre ejercicios. '
        'Ajustá cantidad de ejercicios, series (1-5), reps (1-30) y descanso (0-180) para cumplir ese rango exacto. '
        'REGLA 4 (CASTELLANO): devolvé "nombre_es" en castellano natural e "instrucciones_es" con 2 a 4 pasos breves en castellano. '
        'REGLA 5 (EDICIONES Y MÚSCULOS): si recibís "rutina_actual" y "nuevo_pedido", modificá "ejercicios" aplicando lo pedido (incluyendo agregar otros músculos desde "candidatos") y recalibrá tiempos para seguir dentro de [-5%, +3%]. '
        'Respondé ÚNICAMENTE JSON válido sin markdown: '
        '{"mensaje":"explicación breve y cercana en castellano","ejercicios":[{"id":"ID exacto","nombre_es":"Nombre","series":3,"reps":10,"descanso":60,"instrucciones_es":["Paso 1","Paso 2"]}]}.'
    )

    contenido = instrucciones + "\nDatos: " + json.dumps(contexto, ensure_ascii=False)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "HTTP-Referer": "http://localhost:8501", "X-Title": "A TU RITMO"}
    errores, todos_429 = [], True

    for modelo in MODELOS_GEMMA:
        if not modelo.endswith(":free") and modelo != "openrouter/free":
            continue
        for usar_reasoning in (True, False):
            datos = {"model": modelo, "max_tokens": 8192, "temperature": temperatura, "messages": [{"role": "user", "content": contenido}]}
            if usar_reasoning:
                datos["reasoning"] = {"effort": "low"}
            req = Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(datos).encode("utf-8"), headers=headers, method="POST")
            try:
                with urlopen(req, timeout=50) as resp:
                    cuerpo = json.load(resp)
                if "error" in cuerpo and cuerpo["error"]:
                    msg = cuerpo["error"].get("message", str(cuerpo["error"])) if isinstance(cuerpo["error"], dict) else str(cuerpo["error"])
                    if "429" not in msg and "rate" not in msg.casefold():
                        todos_429 = False
                    errores.append(f"{modelo}: {msg}")
                    break
                choices = cuerpo.get("choices") or []
                texto = (choices[0].get("message") or {}).get("content") if choices else None
                if isinstance(texto, list):
                    texto = "\n".join(b.get("text", "") for b in texto if isinstance(b, dict))
                if not isinstance(texto, str) or not texto.strip():
                    todos_429 = False
                    errores.append(f"{modelo}: respuesta vacía")
                    break
                return extraer_json_gemma(texto)
            except HTTPError as err:
                try:
                    det = json.loads(err.read().decode("utf-8", errors="ignore")).get("error", {}).get("message", f"HTTP {err.code}")
                except Exception:
                    det = f"HTTP {err.code}"
                if err.code == 401:
                    raise RuntimeError(f"API Key inválida en OpenRouter: {det}")
                if err.code == 400 and usar_reasoning and ("reasoning" in det.casefold() or "effort" in det.casefold()):
                    continue
                if err.code != 429:
                    todos_429 = False
                errores.append(f"{modelo} (HTTP {err.code}): {det}")
                break
            except (URLError, ValueError, KeyError, IndexError, TypeError, AttributeError) as err:
                todos_429 = False
                errores.append(f"{modelo}: {err}")
                break

    if errores and todos_429:
        raise RuntimeError("Los modelos gratuitos alcanzaron su límite temporal (20/min o 50/día). Esperá un minuto o usá el borrador manual al pie.")
    raise RuntimeError("No se pudo obtener respuesta de los modelos gratuitos:\n- " + "\n- ".join(errores))


def _cargar_fuente(tamano, negrita=False):
    rutas = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
        if negrita else
        ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Helvetica.ttc"]
    )
    for ruta in rutas:
        if Path(ruta).is_file():
            try:
                return ImageFont.truetype(ruta, tamano)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=tamano)
    except TypeError:
        return ImageFont.load_default()


def _envolver_texto(draw, texto, fuente, ancho_max):
    palabras = (texto or "").split()
    if not palabras:
        return []
    lineas, actual = [], palabras[0]
    for pal in palabras[1:]:
        prueba = f"{actual} {pal}"
        if draw.textlength(prueba, font=fuente) <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = pal
    lineas.append(actual)
    return lineas


def _rect_redondeado(draw, coords, radio, fill, outline=None, width=1):
    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle(coords, radius=radio, fill=fill, outline=outline, width=width)
    else:
        draw.rectangle(coords, fill=fill, outline=outline, width=width)


def generar_archivos_rutina(estado, plan, sesion, ia, usuario):
    """Genera la ficha estética de la rutina en PNG y PDF con la identidad visual de A TU RITMO."""
    if not PIL_DISPONIBLE:
        return None, None
    ancho = 1080
    margen = 56
    ancho_util = ancho - margen * 2

    f_kicker = _cargar_fuente(20, True)
    f_titulo = _cargar_fuente(42, True)
    f_sub = _cargar_fuente(24, False)
    f_nota = _cargar_fuente(22, False)
    f_ej = _cargar_fuente(28, True)
    f_tag = _cargar_fuente(20, False)
    f_m_lbl = _cargar_fuente(17, True)
    f_m_val = _cargar_fuente(26, True)
    f_badge = _cargar_fuente(24, True)

    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lineas_nota = _envolver_texto(dummy, estado.get("mensaje") or "", f_nota, ancho_util - 64)[:4]
    tarjetas_info = []
    for f in estado["filas"]:
        lineas_ej = _envolver_texto(dummy, f["Ejercicio"], f_ej, ancho_util - 120)
        alto_tarjeta = 152 + max(1, len(lineas_ej)) * 36
        tarjetas_info.append((f, lineas_ej, alto_tarjeta))

    alto_header = 250
    alto_nota = (44 + len(lineas_nota) * 30) if lineas_nota else 0
    alto_cuerpo = sum(h + 22 for _, _, h in tarjetas_info)
    alto_total = max(900, 56 + alto_header + (24 + alto_nota if alto_nota else 0) + 28 + alto_cuerpo + 74)

    img = Image.new("RGB", (ancho, alto_total), "#F1E7D7")
    draw = ImageDraw.Draw(img)

    y = 56
    _rect_redondeado(draw, [margen, y, ancho - margen, y + alto_header], 32, fill="#174D47")
    draw.text((margen + 36, y + 30), "A TU RITMO  ·  SESIÓN PERSONALIZADA", fill="#C9E98B", font=f_kicker)
    titulo_rutina = f"RUTINA DE {usuario.upper()}" if usuario else "TU RUTINA DEL DÍA"
    draw.text((margen + 36, y + 66), titulo_rutina, fill="#F8F4E9", font=f_titulo)
    resumen_tiempo = f"{sesion['fecha']}  ·  {formatear_duracion(estado['total'])} de {sesion['minutos']} min  ·  {len(estado['filas'])} ejercicios"
    draw.text((margen + 36, y + 126), resumen_tiempo, fill="#E2EFE5", font=f_sub)

    objetivo_txt = f"Objetivo: {plan['objetivo']}"
    ancho_pill = min(ancho_util - 72, int(draw.textlength(objetivo_txt, font=f_kicker)) + 44)
    _rect_redondeado(draw, [margen + 36, y + 174, margen + 36 + ancho_pill, y + 216], 18, fill="#C9E98B")
    draw.text((margen + 58, y + 184), objetivo_txt, fill="#1A3532", font=f_kicker)
    y += alto_header

    if lineas_nota:
        y += 24
        _rect_redondeado(draw, [margen, y, ancho - margen, y + alto_nota], 22, fill="#FAF6EE", outline="#C5D4C6", width=2)
        for idx_l, linea in enumerate(lineas_nota):
            draw.text((margen + 32, y + 20 + idx_l * 30), linea, fill="#1A3532", font=f_nota)
        y += alto_nota

    y += 28
    for idx, (f, lineas_ej, alto_t) in enumerate(tarjetas_info, start=1):
        _rect_redondeado(draw, [margen, y, ancho - margen, y + alto_t], 24, fill="#FAF6EE", outline="#C5D4C6", width=2)
        _rect_redondeado(draw, [margen, y, margen + 12, y + alto_t], 8, fill="#174D47")

        bx, by = margen + 34, y + 26
        draw.ellipse([bx, by, bx + 44, by + 44], fill="#174D47")
        num_str = str(idx)
        nw = draw.textlength(num_str, font=f_badge)
        draw.text((bx + (44 - nw) / 2, by + 9), num_str, fill="#F8F4E9", font=f_badge)

        ty = y + 26
        for linea in lineas_ej:
            draw.text((bx + 62, ty), linea, fill="#174D47", font=f_ej)
            ty += 36

        sub_ej = f"{f['Músculos'] or 'General'}  ·  {f['Equipamiento']}"
        draw.text((bx + 62, ty + 4), sub_ej, fill="#3E5B53", font=f_tag)

        my = y + alto_t - 84
        gap = 14
        ancho_box = (ancho_util - 68 - gap * 3) // 4
        metricas = [
            ("SERIES", str(f["Series"])),
            ("REPS", str(f["Repeticiones"])),
            ("DESCANSO", f"{f['Descanso (s)']} s"),
            ("DURACIÓN", formatear_duracion(f["Tiempo (s)"])),
        ]
        for m_i, (lbl, val) in enumerate(metricas):
            mx = margen + 34 + m_i * (ancho_box + gap)
            _rect_redondeado(draw, [mx, my, mx + ancho_box, my + 64], 14, fill="#EDF3E9", outline="#D0DDD0", width=1)
            lw = draw.textlength(lbl, font=f_m_lbl)
            vw = draw.textlength(val, font=f_m_val)
            draw.text((mx + (ancho_box - lw) / 2, my + 10), lbl, fill="#3E5B53", font=f_m_lbl)
            draw.text((mx + (ancho_box - vw) / 2, my + 31), val, fill="#174D47", font=f_m_val)

        y += alto_t + 22

    pie = f"Armada con {ia}  ·  A TU RITMO"
    pw = draw.textlength(pie, font=f_tag)
    draw.text(((ancho - pw) / 2, y + 12), pie, fill="#3E5B53", font=f_tag)

    buf_png, buf_pdf = io.BytesIO(), io.BytesIO()
    img.save(buf_png, format="PNG")
    img.save(buf_pdf, format="PDF", resolution=150.0)
    return buf_png.getvalue(), buf_pdf.getvalue()


def iniciar_cronometro(segundos, etiqueta):
    st.session_state["timer_total"] = max(5, int(segundos))
    st.session_state["timer_fin"] = time.time() + max(5, int(segundos))
    st.session_state["timer_label"] = etiqueta


def _render_contenido_cronometro():
    fin = st.session_state.get("timer_fin")
    if not fin:
        return
    total = max(1, int(st.session_state.get("timer_total", 60)))
    restante = max(0, int(math.ceil(fin - time.time())))
    etiqueta = st.session_state.get("timer_label", "Descanso activo")
    pct = max(0, min(100, round(restante / total * 100)))
    estado_txt = "🔔 ¡Tiempo cumplido! Listo para la siguiente serie." if restante == 0 else etiqueta
    st.markdown(
        f'<div class="timer-card">'
        f'  <div class="timer-top">'
        f'    <div><div class="timer-label">⏱️ Cronómetro de descanso</div><div class="timer-sub">{html.escape(estado_txt)}</div></div>'
        f'    <div class="timer-digits">{formatear_reloj(restante)}</div>'
        f'  </div>'
        f'  <div class="timer-track"><div class="timer-fill" style="width:{pct}%"></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    b1, b2, b3, b4 = st.columns(4, gap="small")
    with b1:
        if st.button("+15 s", key="timer_plus15", use_container_width=True):
            st.session_state["timer_fin"] = max(time.time(), fin) + 15
            st.session_state["timer_total"] = total + 15
            st.rerun()
    with b2:
        if st.button("45 s", key="timer_45", use_container_width=True):
            iniciar_cronometro(45, etiqueta)
            st.rerun()
    with b3:
        if st.button("60 s", key="timer_60", use_container_width=True):
            iniciar_cronometro(60, etiqueta)
            st.rerun()
    with b4:
        if st.button("⏹️ Detener", key="timer_stop", use_container_width=True):
            st.session_state.pop("timer_fin", None)
            st.rerun()


def mostrar_cronometro_vivo():
    if not st.session_state.get("timer_fin"):
        return
    if hasattr(st, "fragment"):
        @st.fragment(run_every=1)
        def _frag_timer():
            _render_contenido_cronometro()
        _frag_timer()
    else:
        _render_contenido_cronometro()


def mostrar_espera_ia(placeholder, ia, usuario, minutos, paso_texto, consejo, tip_num=1, total_tips=14):
    saludo = f", {html.escape(usuario)}" if usuario else ""
    min_seg, max_seg = rango_tiempo_segundos(minutos)
    placeholder.markdown(
        f'<div class="waiting-card">'
        f'  <div class="waiting-title">⏳ {html.escape(ia)} está armando tu rutina{saludo}…</div>'
        f'  <div class="waiting-sub">{html.escape(paso_texto)} · Objetivo: {minutos} min ({formatear_duracion(min_seg)} a {formatear_duracion(max_seg)})</div>'
        f'  <div class="waiting-bar"></div>'
        f'  <div class="waiting-tip">'
        f'    <div class="waiting-tip-meta">Salud deportiva & Gimnasio · Tip {tip_num}/{total_tips}</div>'
        f'    {html.escape(consejo)}'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def renderizar_tarjeta_ejercicio(numero, fila, rutas_img, completado=False):
    tag_nivel = f'<span class="exercise-tag">📊 {html.escape(fila["Nivel"])}</span>' if fila["Nivel"] else ""
    url_thumb = obtener_url_miniatura(rutas_img)
    if url_thumb:
        thumb_html = (
            f'<div class="exercise-thumb-wrap">'
            f'  <img src="{html.escape(url_thumb)}" alt="{html.escape(fila["Ejercicio"])}" loading="lazy" '
            f'       onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\';">'
            f'  <div class="exercise-thumb-fallback" style="display:none;">💪</div>'
            f'</div>'
        )
    else:
        thumb_html = '<div class="exercise-thumb-wrap"><div class="exercise-thumb-fallback">💪</div></div>'

    check_txt = "✓ " if completado else ""
    clase_comp = " completed" if completado else ""
    st.markdown(
        f'<div class="exercise-card{clase_comp}">'
        f'  {thumb_html}'
        f'  <div class="exercise-body">'
        f'    <div class="exercise-card-header"><span class="exercise-badge">{numero}</span><span class="exercise-title">{check_txt}{html.escape(fila["Ejercicio"])}</span></div>'
        f'    <div class="exercise-tags"><span class="exercise-tag">💪 {html.escape(fila["Músculos"] or "General")}</span><span class="exercise-tag">🏋️ {html.escape(fila["Equipamiento"])}</span>{tag_nivel}</div>'
        f'    <div class="exercise-metrics">'
        f'      <div class="metric-box"><div class="metric-label">Series</div><div class="metric-value">{fila["Series"]}</div></div>'
        f'      <div class="metric-box"><div class="metric-label">Reps</div><div class="metric-value">{fila["Repeticiones"]}</div></div>'
        f'      <div class="metric-box"><div class="metric-label">Descanso</div><div class="metric-value">{fila["Descanso (s)"]} s</div></div>'
        f'      <div class="metric-box"><div class="metric-label">Duración</div><div class="metric-value">{html.escape(formatear_duracion(fila["Tiempo (s)"]))}</div></div>'
        f'    </div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def serializar_candidatos(lista):
    return [{"id": e["ID"], "nombre_en": e["Ejercicio"], "musculos": e["Músculos"], "secundarios": e.get("Secundarios", ""),
             "categoria": e["Categoría"], "nivel": e["Nivel"], "equipamiento": e["Equipamiento"], "instrucciones_en": e.get("InstruccionesEn", [])[:6]} for e in lista]


def mostrar_rutina_gemma(candidatos, catalogo, plan, sesion, excluidos_ids=None):
    ia, usuario = nombre_ia(), nombre_usuario()
    st.subheader(f"Tu rutina personalizada con {ia}")
    if not candidatos:
        st.info("No hay ejercicios compatibles para armar una rutina en esta sesión.")
        return

    perfil = st.session_state["perfil"]
    minutos = int(sesion["minutos"])
    min_seg, max_seg = rango_tiempo_segundos(minutos)
    prioridades_sesion = sesion.get("prioridades_dia") or plan["prioridades"]
    feedbacks = st.session_state.get("feedback_sesiones", {})
    ultimo_fb = list(feedbacks.values())[-1] if feedbacks else None

    contexto_base = {
        "nombre_usuario": usuario, "nombre_asistente": ia, "minutos": minutos,
        "duracion_minima_segundos": min_seg, "duracion_maxima_segundos": max_seg,
        "max_ejercicios": min(12, len(candidatos)), "objetivo": plan["objetivo"],
        "experiencia": perfil["general"]["experiencia"], "prioridades": prioridades_sesion,
        "ultima_sesion": plan.get("ultima_sesion"), "energia": plan.get("energia"),
        "molestias": plan.get("molestias"), "zona_molestias": plan.get("zona_molestias"),
        "otras_actividades": plan.get("otras_actividades"), "variedad": plan.get("variedad"),
        "incluir": plan.get("incluir"), "evitar": plan.get("evitar"),
        "feedback_sesion_anterior": ultimo_fb,
        "candidatos": serializar_candidatos(candidatos),
    }
    clave = hashlib.sha256(json.dumps([sesion["fecha"], contexto_base], ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:20]
    estados = st.session_state.setdefault("rutinas_gemma", {})
    estado = estados.get(clave)

    def actualizar(pedido=None, mensaje_usuario=None, nueva_variante=False, nivel_seleccionado=None):
        estado_actual = estados.get(clave)
        historial_previo = list(estado_actual["historial"]) if estado_actual else []
        textos = [m for rol, m in historial_previo if rol == "user"] + ([pedido] if pedido else [])
        musculos_extra = list(dict.fromkeys(m for t in textos for m in detectar_musculos_en_texto(t)))
        nivel_efectivo = detectar_nivel_en_texto(pedido or "") or nivel_seleccionado or "Según mi perfil"

        if musculos_extra or nivel_efectivo != "Según mi perfil":
            prios = list(dict.fromkeys([m for m in list(prioridades_sesion) + musculos_extra if m != "Sin preferencia / cuerpo completo"])) or list(prioridades_sesion)
            ampliados, _, _, _ = filtrar_catalogo(catalogo, perfil, plan, sesion, min_candidatos=4, prioridades_override=prios, nivel_ajuste=nivel_efectivo)
            excl = set(excluidos_ids or [])
            por_id = {e["ID"]: e for e in candidatos if e["ID"] not in excl}
            for e in ampliados:
                if e["ID"] not in excl and e["ID"] not in por_id:
                    por_id[e["ID"]] = e
            cand_ef = list(por_id.values())
        else:
            cand_ef = candidatos

        max_ej = min(12, len(cand_ef))
        entrada = dict(contexto_base, max_ejercicios=max_ej, candidatos=serializar_candidatos(cand_ef))
        if musculos_extra:
            entrada["musculos_solicitados_en_chat"] = musculos_extra
        if nivel_efectivo != "Según mi perfil":
            entrada["nivel_preferido_ajuste"] = nivel_efectivo
        if estado_actual and (pedido or nueva_variante):
            entrada["rutina_actual"] = [{"id": f["ID"], "nombre_es": f["Ejercicio"], "musculos": f["Músculos"], "series": f["Series"], "reps": f["Repeticiones"], "descanso": f["Descanso (s)"]} for f in estado_actual["filas"]]
            entrada["cambios"] = historial_previo[-8:]
        if pedido:
            entrada["nuevo_pedido"] = pedido
        if nueva_variante:
            entrada["nueva_variante"] = True
            entrada["nuevo_pedido"] = "Armá una combinación alternativa distinta usando otros candidatos y cumpliendo el tiempo exacto."

        ids_validos = [e["ID"] for e in cand_ef]
        temp = 0.45 if nueva_variante else 0.25
        api_key = obtener_api_key()
        espera_box = st.empty()
        consejos_ciclo = random.sample(CONSEJOS_ESPERA, len(CONSEJOS_ESPERA))
        t_global = time.time()
        try:
            propuesta = filas = total = ultimo_error = None
            for intento in range(3):
                paso_txt = "Seleccionando ejercicios y armando estructura…" if intento == 0 else f"Ajustando tiempos y ejercicios (paso {intento + 1}/3)…"
                if intento > 0 and ultimo_error is not None:
                    payload_llamada = dict(entrada, propuesta_rechazada=propuesta, correccion_requerida=(
                        f"Propuesta rechazada: {ultimo_error} Devolvé máximo {max_ej} ejercicios SIN repetir IDs, "
                        f"duración total entre {min_seg} s y {max_seg} s, usando solo IDs de: {json.dumps(ids_validos)}"
                    ))
                else:
                    payload_llamada = entrada

                with ThreadPoolExecutor(max_workers=1) as executor:
                    futuro = executor.submit(consultar_gemma, payload_llamada, temp, api_key)
                    ultimo_tip_mostrado = -1
                    while not futuro.done():
                        idx_tip = int((time.time() - t_global) // 5.5) % len(consejos_ciclo)
                        if idx_tip != ultimo_tip_mostrado:
                            ultimo_tip_mostrado = idx_tip
                            mostrar_espera_ia(
                                espera_box, ia, usuario, minutos, paso_txt,
                                consejos_ciclo[idx_tip], idx_tip + 1, len(consejos_ciclo),
                            )
                        time.sleep(0.25)
                    propuesta = futuro.result()

                try:
                    filas, total = validar_rutina_gemma(propuesta, cand_ef, minutos, permitir_deduplicar=(intento == 2 and len(cand_ef) <= 2), exigir_rango_tiempo=(intento < 2))
                    if intento == 2:
                        filas, total = ajustar_tiempos_rutina(filas, cand_ef, minutos)
                    ultimo_error = None
                    break
                except ValueError as err_val:
                    ultimo_error = err_val
            if ultimo_error is not None:
                raise ultimo_error
            historial = (historial_previo if (pedido or nueva_variante) else [])
            if (etq := mensaje_usuario or pedido):
                historial.append(("user", etq))
            msg_ia = str(propuesta.get("mensaje") or "Rutina lista.")
            historial.append(("assistant", msg_ia))
            estados[clave] = {"propuesta": propuesta, "filas": filas, "total": total, "mensaje": msg_ia, "historial": historial}
            st.session_state["rutina_por_fecha"][sesion["fecha"]] = clave
        except (RuntimeError, ValueError) as error:
            st.warning(str(error))
        finally:
            espera_box.empty()
        if clave in estados and ultimo_error is None:
            st.rerun()

    if st.session_state.pop("auto_generar_sesion", False) and not estado:
        actualizar()
        return

    if not estado:
        if st.button(f"✨ Armar mi rutina con {ia}", key="generar_" + clave, type="primary", use_container_width=True):
            actualizar()
        return

    saludo_resumen = f" para {html.escape(usuario)}" if usuario else ""
    st.markdown(
        f'<div class="routine-summary">'
        f'  <div class="routine-summary-kicker">Sesión lista{saludo_resumen} · {len(estado["filas"])} ejercicio(s)</div>'
        f'  <div class="routine-summary-title">Duración estimada: {formatear_duracion(estado["total"])} de {minutos} min pedidos</div>'
        f'  <div class="routine-summary-note">{html.escape(estado.get("mensaje") or "")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    png_bytes, pdf_bytes = generar_archivos_rutina(estado, plan, sesion, ia, usuario)
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        if st.button("✨ Otra combinación", key="variante_" + clave, use_container_width=True):
            actualizar(mensaje_usuario="Pediste una combinación alternativa", nueva_variante=True)
    with c2:
        if png_bytes:
            st.download_button("🖼️ Descargar imagen", png_bytes, file_name=f"rutina_{sesion['fecha']}.png", mime="image/png", key="png_" + clave, use_container_width=True)
    with c3:
        if pdf_bytes:
            st.download_button("📄 Descargar PDF", pdf_bytes, file_name=f"rutina_{sesion['fecha']}.pdf", mime="application/pdf", key="pdf_" + clave, use_container_width=True)

    # Modo "Entrenar ahora": progreso de series + cronómetro de descanso en vivo
    total_series = sum(int(f["Series"]) for f in estado["filas"])
    series_hechas = sum(
        1
        for f in estado["filas"]
        for s_num in range(1, int(f["Series"]) + 1)
        if st.session_state.get(f"serie_chk_{clave}_{f['ID']}_{s_num}", False)
    )
    pct_sesion = round(series_hechas / total_series * 100) if total_series else 0
    sesion_terminada = total_series > 0 and series_hechas == total_series
    if sesion_terminada and not st.session_state.get(f"celebrado_{clave}"):
        st.session_state[f"celebrado_{clave}"] = True
        st.balloons()
    elif not sesion_terminada:
        st.session_state.pop(f"celebrado_{clave}", None)

    titulo_prog = f"🏆 ¡Entrenamiento completado al 100%! Excelente trabajo{saludo_resumen}" if sesion_terminada else "🏋️ Modo entrenar ahora · Tildá tus series"
    st.markdown(
        f'<div class="workout-progress-box {"done" if sesion_terminada else ""}">'
        f'  <div class="workout-progress-top"><span>{titulo_prog}</span><span>{series_hechas}/{total_series} series ({pct_sesion}%)</span></div>'
        f'  <div class="workout-progress-track"><div class="workout-progress-fill" style="width:{pct_sesion}%"></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    mostrar_cronometro_vivo()

    por_id_cat = {e.get("id"): e for e in catalogo if e.get("id")}
    total_ejercicios = len(estado["filas"])
    for idx, fila in enumerate(estado["filas"], start=1):
        rutas_img = fila.get("Imagenes") or (por_id_cat.get(fila["ID"], {}).get("images") or [])
        n_series = int(fila["Series"])
        ej_completo = all(st.session_state.get(f"serie_chk_{clave}_{fila['ID']}_{s_num}", False) for s_num in range(1, n_series + 1))
        renderizar_tarjeta_ejercicio(idx, fila, rutas_img, completado=ej_completo)

        # Checklist de series por ejercicio
        cols_series = st.columns(min(5, n_series), gap="small")
        for s_num in range(1, n_series + 1):
            with cols_series[(s_num - 1) % len(cols_series)]:
                st.checkbox(f"Serie {s_num}", key=f"serie_chk_{clave}_{fila['ID']}_{s_num}")

        # Barra táctil de acciones del ejercicio: Cómo hacerlo | Descanso | -/+ Serie | Orden | Cambiar
        col_i, col_t, col_s_menos, col_s_mas, col_up, col_dn, col_swap = st.columns([1.35, 0.9, 0.72, 0.72, 0.45, 0.45, 0.95], gap="small")
        with col_i:
            with st.expander("📖 Cómo hacerlo"):
                imagenes = obtener_imagenes_ejercicio(rutas_img)
                if imagenes:
                    cols_img = st.columns(min(2, len(imagenes)), gap="small")
                    etiquetas_paso = ["Posición inicial", "Ejecución"]
                    for i_img, src_img in enumerate(imagenes[:2]):
                        with cols_img[i_img]:
                            try:
                                st.image(src_img, caption=etiquetas_paso[i_img] if i_img < 2 else f"Paso {i_img + 1}", use_container_width=True)
                            except Exception:
                                pass
                if fila["Instrucciones"]:
                    for n, paso in enumerate(fila["Instrucciones"], start=1):
                        st.markdown(f"**{n}.** {paso}")
                else:
                    st.write("Sin instrucciones detalladas.")
        with col_t:
            if st.button(f"⏱️ {fila['Descanso (s)']}s", key=f"rest_{clave}_{idx}_{fila['ID']}", help="Iniciar cronómetro de descanso", use_container_width=True):
                iniciar_cronometro(fila["Descanso (s)"], f"Descanso · {fila['Ejercicio']}")
                st.rerun()
        with col_s_menos:
            if st.button("➖S", key=f"sminus_{clave}_{idx}_{fila['ID']}", disabled=n_series <= 1, help="Quitar 1 serie", use_container_width=True):
                fila["Series"] = n_series - 1
                recalcular_tiempo_fila(fila)
                estado["total"] = total_rutina_segundos(estado["filas"])
                st.rerun()
        with col_s_mas:
            if st.button("➕S", key=f"splus_{clave}_{idx}_{fila['ID']}", disabled=n_series >= 5, help="Sumar 1 serie", use_container_width=True):
                fila["Series"] = n_series + 1
                recalcular_tiempo_fila(fila)
                estado["total"] = total_rutina_segundos(estado["filas"])
                st.rerun()
        with col_up:
            if st.button("⬆️", key=f"up_{clave}_{idx}_{fila['ID']}", disabled=idx == 1, help="Subir orden", use_container_width=True):
                estado["filas"][idx - 2], estado["filas"][idx - 1] = estado["filas"][idx - 1], estado["filas"][idx - 2]
                st.rerun()
        with col_dn:
            if st.button("⬇️", key=f"dn_{clave}_{idx}_{fila['ID']}", disabled=idx == total_ejercicios, help="Bajar orden", use_container_width=True):
                estado["filas"][idx - 1], estado["filas"][idx] = estado["filas"][idx], estado["filas"][idx - 1]
                st.rerun()
        with col_swap:
            if st.button("🔄 Cambiar", key=f"swap_{clave}_{idx}_{fila['ID']}", use_container_width=True):
                actualizar(pedido=f"Reemplazá únicamente '{fila['Ejercicio']}' (id: {fila['ID']}) por otro candidato distinto manteniendo los demás y el rango de tiempo.", mensaje_usuario=f"Cambiar «{fila['Ejercicio']}»")

    # Cierre y feedback post-sesión
    st.markdown(
        '<div class="feedback-card">'
        '  <div class="feedback-title">🏁 Cierre de sesión · ¿Cómo sentiste el entrenamiento?</div>'
        '  <div class="feedback-sub">Tu respuesta ayuda a calibrar la intensidad de las próximas sesiones.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    fb_store = st.session_state.setdefault("feedback_sesiones", {})
    fb_actual = fb_store.get(sesion["fecha"])
    fb1, fb2, fb3 = st.columns(3, gap="small")
    opciones_fb = [
        ("🟢 Liviana", "Liviana (podía dar más)"),
        ("🟡 Justa", "Justa (esfuerzo ideal)"),
        ("🔴 Muy exigente", "Muy exigente (costó terminarla)"),
    ]
    for col_fb, (etq_btn, val_fb) in zip((fb1, fb2, fb3), opciones_fb):
        with col_fb:
            marcado_fb = fb_actual == val_fb
            if st.button(("✓ " if marcado_fb else "") + etq_btn, key=f"fb_{sesion['fecha']}_{etq_btn}", type="primary" if marcado_fb else "secondary", use_container_width=True):
                fb_store[sesion["fecha"]] = val_fb
                st.rerun()

    if fb_actual:
        if fb_actual.startswith("Liviana"):
            st.success(f"Registrado como **Liviana**. {ia} tendrá esto en cuenta para aumentar progresivamente el estímulo en tu próxima sesión.")
            if st.button("⬆️ Subir intensidad de esta rutina ahora", key="subir_int_" + clave, use_container_width=True):
                actualizar(pedido="El usuario sintió la rutina liviana: subí ligeramente la intensidad (agregando 1 serie o 2 repeticiones en ejercicios clave) manteniendo el tiempo dentro del rango permitido.", mensaje_usuario="Subir intensidad de la sesión")
        elif fb_actual.startswith("Justa"):
            st.info(f"¡Excelente! Registrado como **Justa**. {ia} mantendrá este nivel de carga y descanso en tus próximas sesiones.")
        else:
            st.warning(f"Registrado como **Muy exigente**. {ia} priorizará mayor recuperación y volumen moderado en las próximas sesiones.")
            if st.button("⬇️ Suavizar esta rutina ahora", key="bajar_int_" + clave, use_container_width=True):
                actualizar(pedido="El usuario sintió la rutina muy exigente: moderá el volumen o ampliá ligeramente los descansos manteniendo el tiempo dentro del rango permitido.", mensaje_usuario="Suavizar exigencia de la sesión")

    st.markdown(f"### Ajustá tu rutina con {ia} en 1 clic o por chat")
    chips_rapidos = [
        ("🔥 Más intensa", "Hacé la rutina un poco más exigente aumentando repeticiones o complejidad sin salir del tiempo permitido."),
        ("🧘 Más suave", "Hacé la rutina un poco más llevadera reduciendo ligeramente el volumen o aumentando descansos dentro del tiempo permitido."),
        ("⚡ Menos descanso", "Reducí los tiempos de descanso entre series para hacer la sesión más dinámica y sumá repeticiones si sobra tiempo."),
        ("🍑 + Piernas/Glúteos", "Agregá 1 o 2 ejercicios de piernas o glúteos ajustando series y descansos para respetar el tiempo."),
        ("💪 + Tren superior", "Agregá 1 o 2 ejercicios de espalda, pecho, hombros o brazos respetando el tiempo de la sesión."),
        ("🧱 + Abdomen/Core", "Incluí 1 o 2 ejercicios de abdomen / zona media ajustando los tiempos de la sesión."),
    ]
    for row_i in range(0, len(chips_rapidos), 3):
        cols_chip = st.columns(3, gap="small")
        for col_c, (label_c, prompt_c) in zip(cols_chip, chips_rapidos[row_i:row_i + 3]):
            with col_c:
                if st.button(label_c, key=f"chip_{clave}_{label_c}", use_container_width=True):
                    actualizar(pedido=prompt_c, mensaje_usuario=label_c)

    for rol, msg in estado["historial"]:
        with st.chat_message(rol):
            st.markdown(msg)

    nivel_ajuste = st.selectbox("Nivel de ejercicios al agregar o ajustar", ["Según mi perfil", "Básicos / Principiante", "Intermedio", "Más complejos / Avanzado", "Cualquier nivel"], key="nivel_ajuste_" + clave)
    with st.form("chat_" + clave, clear_on_submit=True):
        pedido = st.text_input(f"¿Qué querés pedirle a {ia}?", placeholder="Ej.: agregá 2 ejercicios básicos de hombros, o sumá algo de espalda", max_chars=500)
        if st.form_submit_button("Enviar cambio") and pedido.strip():
            actualizar(pedido=pedido.strip(), nivel_seleccionado=nivel_ajuste)


def mostrar_borrador(candidatos, catalogo, plan, sesion, cats_permitidas):
    c1, c2 = st.columns(2)
    with c1:
        series = st.number_input("Series por ejercicio", 1, 10, 2, key="sesion_series")
        reps = st.number_input("Repeticiones por serie", 1, 50, 8, key="sesion_reps")
        segs = st.number_input("Segundos por repetición", 1, 15, 4, key="sesion_segundos")
        limite = st.number_input("Máximo de ejercicios", 1, 12, 5, key="sesion_limite")
    with c2:
        desc = st.number_input("Descanso entre series (s)", 0, 600, 60, 15, key="sesion_descanso")
        trans = st.number_input("Cambio de ejercicio (s)", 0, 600, 60, 15, key="sesion_transicion")
        reserva = st.number_input("Minutos preparación/cierre", 0, 120, 5, key="sesion_reserva")
    por_id = {e["id"]: e for e in catalogo if e.get("id")}
    validos = [e for e in candidatos if por_id.get(e["ID"], {}).get("category") in set(cats_permitidas or {"strength"})]
    costo = series * reps * segs + (series - 1) * desc
    presupuesto = max(0, int(sesion["minutos"]) * 60 - reserva * 60)
    elegidos, usados, grupos = [], set(), set()
    while len(elegidos) < limite:
        ops = sorted([e for e in validos if e["ID"] not in usados], key=lambda e: (-len(set(por_id[e["ID"]].get("primaryMuscles", [])) - grupos), e["ID"]))
        extra = costo + (trans if elegidos else 0)
        if not ops or extra > presupuesto:
            break
        el = ops[0]
        usados.add(el["ID"])
        grupos.update(por_id[el["ID"]].get("primaryMuscles", []))
        elegidos.append({"Ejercicio": el["Ejercicio"].replace("_", " "), "Músculos": el["Músculos"], "Series": series, "Reps": reps, "Descanso (s)": desc, "Tiempo (s)": costo})
        presupuesto -= extra
    if not elegidos:
        st.warning("No alcanza el tiempo o no hay candidatos compatibles con estos parámetros.")
        return
    total = reserva * 60 + len(elegidos) * costo + max(0, len(elegidos) - 1) * trans
    st.write(f"**Borrador: {len(elegidos)} ejercicios · {formatear_duracion(total)} de {sesion['minutos']} min**")
    st.dataframe(elegidos, hide_index=True, use_container_width=True)


def agrupar_sesiones_por_semana(sesiones):
    semanas, mapa = [], {}
    for idx, ses in enumerate(sesiones):
        f = date.fromisoformat(ses["fecha"])
        clave_sem = (f.isocalendar()[0], f.isocalendar()[1])
        if clave_sem not in mapa:
            mapa[clave_sem] = []
            semanas.append(mapa[clave_sem])
        mapa[clave_sem].append((idx, ses))
    return semanas


def mostrar_catalogo():
    usuario = nombre_usuario()
    titulo_dia = f"Tu plan de entrenamiento, {usuario}" if usuario else "Tu plan de entrenamiento"
    st.markdown(f'<div class="question-card"><h2>{html.escape(titulo_dia)}</h2><p>Armado con tus preferencias, tiempo y equipamiento.</p></div>', unsafe_allow_html=True)
    if st.button("← Volver a la planificación", key="volver_catalogo"):
        st.session_state["etapa_plan"] = 6
        st.rerun()
    try:
        catalogo = json.loads((Path(__file__).resolve().parent / "exercises.json").read_text(encoding="utf-8-sig"))
    except Exception as error:
        st.error(f"No se pudo leer exercises.json: {error}")
        return

    plan, perfil = st.session_state["planificacion_confirmada"], st.session_state["perfil"]
    sesiones = plan["sesiones"]
    st.session_state.setdefault("rutina_por_fecha", {})
    idx_sel = min(st.session_state.get("sesion_activa_idx", 0), len(sesiones) - 1)
    st.session_state["sesion_activa_idx"] = idx_sel

    if len(sesiones) > 1:
        semanas = agrupar_sesiones_por_semana(sesiones)
        sem_activa = next((w_i for w_i, items in enumerate(semanas) if any(i == idx_sel for i, _ in items)), 0)
        if len(semanas) > 1:
            cols_sem = st.columns(len(semanas), gap="small")
            for w_i, col_w in enumerate(cols_sem):
                with col_w:
                    if st.button(f"Semana {w_i + 1}", key=f"tab_sem_{w_i}", type="primary" if w_i == sem_activa else "secondary", use_container_width=True):
                        st.session_state["sesion_activa_idx"] = semanas[w_i][0][0]
                        st.rerun()

        items_semana = semanas[sem_activa]
        cols_dias = st.columns(len(items_semana), gap="small")
        for col_d, (s_idx, s_item) in zip(cols_dias, items_semana):
            f_obj = date.fromisoformat(s_item["fecha"])
            dia_corto = DIAS_CORTOS[f_obj.weekday()]
            enfoque = s_item.get("etiqueta_enfoque") or ", ".join(s_item.get("prioridades_dia") or plan["prioridades"])
            ya_lista = s_item["fecha"] in st.session_state["rutina_por_fecha"]
            activa = s_idx == idx_sel
            with col_d:
                st.markdown(
                    f'<div class="day-card-info {"active" if activa else ""}">'
                    f'  <div class="day-card-title">{"✓ " if ya_lista else ""}{dia_corto} {f_obj.day:02d}/{f_obj.month:02d}</div>'
                    f'  <div class="day-card-sub">{html.escape(enfoque)} · {s_item["minutos"]}m</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button("Viendo" if activa else "Elegir", key=f"tab_dia_{s_idx}_{s_item['fecha']}", type="primary" if activa else "secondary", use_container_width=True):
                    st.session_state["sesion_activa_idx"] = s_idx
                    st.rerun()

    sesion = sesiones[idx_sel]
    enfoque_actual = sesion.get("prioridades_dia") or plan["prioridades"]

    st.markdown(
        f'<div class="quick-bar">'
        f'  <span class="quick-pill">📅 {sesion["fecha"]}</span>'
        f'  <span class="quick-pill">⏱️ {sesion["minutos"]} min</span>'
        f'  <span class="quick-pill">🎯 {html.escape(plan["objetivo"])}</span>'
        f'  <span class="quick-pill">💪 {html.escape(", ".join(enfoque_actual))}</span>'
        f'  <span class="quick-pill">🏋️ {html.escape(", ".join(sesion["equipamiento"]))}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.expander("⚡ Ajuste rápido de parámetros (sin volver al cuestionario)", expanded=False):
        qe1, qe2 = st.columns(2, gap="small")
        with qe1:
            nuevo_obj = st.selectbox("Objetivo", OBJ, index=OBJ.index(plan["objetivo"]) if plan["objetivo"] in OBJ else 0, key=f"qe_obj_{idx_sel}")
            nuevos_musc = st.multiselect("Músculos de esta sesión", MUSCULOS_OPCIONES, default=[m for m in enfoque_actual if m in MUSCULOS_OPCIONES] or ["Sin preferencia / cuerpo completo"], key=f"qe_musc_{idx_sel}")
        with qe2:
            nuevos_min = st.number_input("Minutos de esta sesión", min_value=10, max_value=180, value=int(sesion["minutos"]), step=5, key=f"qe_min_{idx_sel}")
            nuevo_eq = st.multiselect("Equipamiento disponible", EQUIPO_OPCIONES, default=[e for e in sesion["equipamiento"] if e in EQUIPO_OPCIONES] or ["Sin equipamiento"], key=f"qe_eq_{idx_sel}")
        if st.button("✅ Aplicar cambios y regenerar sesión", key=f"qe_apply_{idx_sel}", type="primary", use_container_width=True):
            if not nuevos_musc:
                st.error("Elegí al menos un grupo muscular o Sin preferencia.")
            elif not nuevo_eq or ("Sin equipamiento" in nuevo_eq and len(nuevo_eq) > 1):
                st.error("Elegí «Sin equipamiento» o los elementos disponibles, no ambos.")
            else:
                plan["objetivo"] = nuevo_obj
                sesion["minutos"] = int(nuevos_min)
                sesion["equipamiento"] = list(nuevo_eq)
                sesion["prioridades_dia"] = list(nuevos_musc)
                sesion["etiqueta_enfoque"] = "Cuerpo completo" if "Sin preferencia / cuerpo completo" in nuevos_musc else ", ".join(nuevos_musc)
                st.session_state["auto_generar_sesion"] = True
                st.rerun()

    brutos, revisar, descartados, info = filtrar_catalogo(catalogo, perfil, plan, sesion, prioridades_override=enfoque_actual)
    por_id = {e["ID"]: e for e in brutos}
    excl_key = f"excluir_catalogo_{sesion['fecha']}"
    excluidos = [x for x in st.session_state.get(excl_key, []) if x in por_id]
    candidatos = [e for e in brutos if e["ID"] not in excluidos]

    mostrar_rutina_gemma(candidatos, catalogo, plan, sesion, excluidos)
    st.divider()
    with st.expander(f"🔍 Ver candidatos iniciales del catálogo y excluir ejercicios ({len(candidatos)} disponibles)"):
        st.multiselect("¿Querés excluir alguno?", list(por_id), default=excluidos, format_func=lambda x: por_id[x]["Ejercicio"].replace("_", " "), key=excl_key)
        ocultas = {"ID", "Secundarios", "NivelRaw", "CategoriaRaw", "InstruccionesEn", "PrimariosRaw", "SecundariosRaw", "Imagenes"}
        vista = [{k: (v.replace("_", " ") if k == "Ejercicio" else v) for k, v in e.items() if k not in ocultas} for e in candidatos]
        if vista:
            st.dataframe(vista, hide_index=True, use_container_width=True)
        st.caption("Descartados: " + ", ".join(f"{k}: {v}" for k, v in descartados.items()))
    with st.expander("⚙️ Alternativa: armar borrador manual sin IA"):
        mostrar_borrador(candidatos, catalogo, plan, sesion, info["categorias"])


st.markdown('<div class="brand-wrap"><span class="brand"><span class="brand-arrow">↗</span>A TU RITMO</span></div>', unsafe_allow_html=True)
st.title("Tu entrenamiento, a tu ritmo")
st.caption("Un plan que se adapte a vos, a tus objetivos y al tiempo que tenés.")

if st.session_state["perfil_finalizado"] and st.session_state["etapa_plan"] == 7:
    mostrar_catalogo()
elif st.session_state["perfil_finalizado"] and st.session_state["etapa_plan"] in [5, 6]:
    mostrar_planificacion()
elif st.session_state["perfil_finalizado"]:
    u = nombre_usuario()
    saludo = f"¿Qué organizamos, {html.escape(u)}?" if u else "¿Qué organizamos?"
    st.markdown(f'<div class="question-card"><h2>{saludo}</h2><p>¡Tu perfil está listo! Elegí cómo querés organizarte.</p></div>', unsafe_allow_html=True)
    periodo = st.session_state.get("periodo_elegido")
    opciones_p = ["Una sesión para hoy", "Una semana", "Cuatro semanas"]
    for i in range(0, len(opciones_p), 2):
        pareja = opciones_p[i:i + 2]
        cols = st.columns([1, 2, 1], gap="small")[1:2] if len(pareja) == 1 else st.columns(2, gap="small")
        for col, op in zip(cols, pareja):
            with col:
                if st.button(("✓  " if periodo == op else "") + op, key="periodo_" + op, type="primary" if periodo == op else "secondary", use_container_width=True):
                    st.session_state["periodo_elegido"] = op
                    st.session_state.pop("planificacion_confirmada", None)
                    st.rerun()
    if st.checkbox("Ver el perfil guardado"):
        st.json(st.session_state["perfil"])
    if st.button("Elegir este plan →", type="primary"):
        if not periodo:
            st.error("Seleccioná un período.")
        elif st.session_state["perfil"]["actividad"]["restricciones"] != "No":
            st.warning("Este prototipo no genera automáticamente rutinas adaptadas a restricciones médicas.")
        else:
            iniciar_plan()
            st.rerun()
    st.download_button("Descargar mi perfil (JSON)", json.dumps(st.session_state["perfil"], ensure_ascii=False, indent=2), file_name="mi_perfil_atu_ritmo.json", mime="application/json")
else:
    lista = preguntas()
    indice = min(st.session_state["indice_pregunta"], len(lista) - 1)
    st.session_state["indice_pregunta"] = indice
    p = lista[indice]
    key = p["key"]
    st.session_state["clave_pregunta_actual"] = key
    progreso = round(indice / len(lista) * 100)
    st.markdown(f'<div class="kicker">TU PERFIL · PREGUNTA {indice + 1} DE {len(lista)} · {progreso}%</div><div class="progress"><div style="width:{progreso}%"></div></div>', unsafe_allow_html=True)
    ayuda = html.escape(p["hint"])
    st.markdown(f'<div class="question-card"><h2>{html.escape(p["title"])}</h2>' + (f'<p>{ayuda}</p>' if ayuda else '') + '</div>', unsafe_allow_html=True)

    if p["kind"] in ("single", "multi"):
        opciones = p["options"]
        for i in range(0, len(opciones), 2):
            pareja = opciones[i:i + 2]
            cols = st.columns([1, 2, 1], gap="small")[1:2] if len(pareja) == 1 else st.columns(2, gap="small")
            for col, op in zip(cols, pareja):
                with col:
                    marcado = (A.get(key) == op) if p["kind"] == "single" else (op in A.get(key, []))
                    if st.button(("✓  " if marcado else "") + op, key=f"respuesta_{key}_{op}", type="primary" if marcado else "secondary", use_container_width=True):
                        if p["kind"] == "single":
                            A[key] = op
                            if (err := error_de(p)):
                                st.session_state["error_actual"] = err
                                st.rerun()
                            st.session_state.pop("error_actual", None)
                            siguiente()
                        else:
                            act = list(A.get(key, []))
                            act.remove(op) if op in act else act.append(op)
                            A[key] = act
                            st.rerun()
    elif p["kind"] in ("text", "textarea"):
        wk = "widget_" + key
        st.session_state.setdefault(wk, A.get(key) or "")
        ph = "Por defecto: Gemma" if key == "nombre_ia" else "Escribí acá..."
        if p["kind"] == "text":
            st.text_input("Tu respuesta (opcional)" if not p["required"] else "Tu respuesta", key=wk, placeholder=ph)
        else:
            st.text_area("Tu respuesta", key=wk, placeholder=ph)

    if key == "restricciones" and A.get(key) in ["Sí", "No estoy segura/o"]:
        st.warning("Podés guardar tu perfil, pero este prototipo no generará automáticamente una rutina adaptada a restricciones médicas.")
    if st.session_state.get("error_actual"):
        st.error(st.session_state.pop("error_actual"))
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    nav_izq, _, nav_der = st.columns([1, 1.4, 1], gap="medium")
    with nav_izq:
        if indice > 0 and st.button("← Anterior", key="anterior", use_container_width=True):
            st.session_state.pop("error_actual", None)
            claves = [x["key"] for x in lista]
            pos = claves.index(key) if key in claves else indice
            st.session_state["indice_pregunta"] = max(0, pos - 1)
            st.rerun()
    with nav_der:
        if p["kind"] != "single" and st.button("Continuar →", key="continuar", use_container_width=True):
            if p["kind"] in ("text", "textarea"):
                A[key] = st.session_state.get("widget_" + key, "")
            if (err := error_de(p)):
                st.session_state["error_actual"] = err
                st.rerun()
            st.session_state.pop("error_actual", None)
            siguiente()
    st.caption("Tus respuestas se conservan durante esta sesión.")