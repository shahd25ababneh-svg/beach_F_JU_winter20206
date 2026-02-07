import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import plotly.express as px

engine = create_engine('sqlite:///beach_volley_live_2026.db')

st.set_page_config(page_title="JU Live Scout 2026", layout="wide")


st.sidebar.header("📋 Match Setup")
t1_name = st.sidebar.text_input("Home Team Name", value="Team 1")
t2_name = st.sidebar.text_input("Away Team Name", value="Team 2")
match_stage = st.sidebar.radio("Match Stage", ["Group Stage", "Final"])


stats_keys = [
    'T1_P1_digs', 'T1_P2_digs', 'T1_P1_atk', 'T1_P2_atk', 'T1_P1_ace', 'T1_P2_ace', 'T1_P1_miss', 'T1_P2_miss',
    'T2_P1_digs', 'T2_P2_digs', 'T2_P1_atk', 'T2_P2_atk', 'T2_P1_ace', 'T2_P2_ace', 'T2_P1_miss', 'T2_P2_miss',
    'Score_T1', 'Score_T2'
]

if 'score_history' not in st.session_state:
    st.session_state.score_history = []

for key in stats_keys:
    if key not in st.session_state:
        st.session_state[key] = 0

# --- دالة التحكم بالإحصائيات (الزيادة والنقصان) ---
def stat_module(label, key):
    st.write(f"**{label}: {st.session_state[key]}**")
    c_inc, c_dec = st.columns(2)
    if c_inc.button("➕", key=f"inc_{key}"):
        st.session_state[key] += 1
        st.rerun()
    if c_dec.button("➖", key=f"dec_{key}"):
        if st.session_state[key] > 0:
            st.session_state[key] -= 1
            st.rerun()

st.title(f"🏐 {t1_name} VS {t2_name}")
st.caption(f"Tournament Stage: {match_stage}")

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.metric(t1_name, st.session_state.Score_T1)
    if st.button(f"Point {t1_name} ➕", key="p1", use_container_width=True):
        st.session_state.Score_T1 += 1
        st.session_state.score_history.append({"Time": datetime.now(), t1_name: st.session_state.Score_T1, t2_name: st.session_state.Score_T2})
        st.rerun()
    if st.button(f"Undo {t1_name} ➖", key="u1"):
        if st.session_state.Score_T1 > 0: st.session_state.Score_T1 -= 1
        st.rerun()

with col_s2:
    st.metric(t2_name, st.session_state.Score_T2)
    if st.button(f"Point {t2_name} ➕", key="p2", use_container_width=True):
        st.session_state.Score_T2 += 1
        st.session_state.score_history.append({"Time": datetime.now(), t1_name: st.session_state.Score_T1, t2_name: st.session_state.Score_T2})
        st.rerun()
    if st.button(f"Undo {t2_name} ➖", key="u2"):
        if st.session_state.Score_T2 > 0: st.session_state.Score_T2 -= 1
        st.rerun()

st.divider()
st.header("📊 Detailed Player Stats")
tab1, tab2 = st.tabs([f"{t1_name} Players", f"{t2_name} Players"])

with tab1:
    p1, p2 = st.columns(2)
    with p1:
        st.subheader("Player 1")
        stat_module("Digs", "T1_P1_digs")
        stat_module("Attacks", "T1_P1_atk")
        stat_module("Aces", "T1_P1_ace")
        stat_module("Missed Srv", "T1_P1_miss")
    with p2:
        st.subheader("Player 2")
        stat_module("Digs", "T1_P2_digs")
        stat_module("Attacks", "T1_P2_atk")
        stat_module("Aces", "T1_P2_ace")
        stat_module("Missed Srv", "T1_P2_miss")

with tab2:
    p3, p4 = st.columns(2)
    with p3:
        st.subheader("Player 1")
        stat_module("Digs", "T2_P1_digs")
        stat_module("Attacks", "T2_P1_atk")
        stat_module("Aces", "T2_P1_ace")
        stat_module("Missed Srv", "T2_P1_miss")
    with p4:
        st.subheader("Player 2")
        stat_module("Digs", "T2_P2_digs")
        stat_module("Attacks", "T2_P2_atk")
        stat_module("Aces", "T2_P2_ace")
        stat_module("Missed Srv", "T2_P2_miss")

st.divider()
if st.session_state.score_history:
    df_h = pd.DataFrame(st.session_state.score_history)
    fig = px.line(df_h, x="Time", y=[t1_name, t2_name], title="Match Momentum", markers=True)
    st.plotly_chart(fig, use_container_width=True)


st.sidebar.divider()
if st.sidebar.button("💾 SAVE MATCH"):
    final_data = {k: [st.session_state[k]] for k in stats_keys}
    final_data.update({'Team_1': t1_name, 'Team_2': t2_name, 'Stage': match_stage, 'Date': datetime.now()})
    pd.DataFrame(final_data).to_sql('championship_archive', con=engine, if_exists='append', index=False)
    st.sidebar.success("Saved!")

if st.sidebar.button("🧹 New Match"):
    for k in stats_keys: st.session_state[k] = 0
    st.session_state.score_history = []
    st.rerun()