import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Test Połączenia 🔌")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Próbujemy odczytać arkusz
    df = conn.read(ttl=0)
    st.success("✅ Udało się połączyć z Google Sheets!")
    st.write("Podgląd danych:", df)
except Exception as e:
    st.error(f"❌ Błąd połączenia: {e}")