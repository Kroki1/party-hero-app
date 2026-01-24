import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="PartyHero 🎈", page_icon="🎈", layout="centered")

# --- CSS (Wygląd) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F6; }
    h1 { color: #FF4B4B; text-align: center; }
    .card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- SŁOWNIK JĘZYKOWY (PL, EN, SV) ---
translations = {
    "PL": {
        "title": "PartyHero 🦸‍♂️",
        "create_header": "Zorganizuj urodziny w 3 minuty!",
        "name_label": "Imię solenizanta",
        "date_label": "Data imprezy",
        "loc_label": "Miejsce",
        "theme_label": "Motyw przewodni",
        "btn_create": "Generuj Zaproszenie ✨",
        "guest_header": "Potwierdź obecność",
        "guest_name": "Twoje Imię / Imię Dziecka",
        "guest_allergy": "Alergie / Dieta",
        "guest_btn": "Wyślij potwierdzenie",
        "gdpr": "Akceptuję politykę prywatności i przetwarzanie danych.",
        "success": "Gotowe! Wyślij ten link gościom:",
        "shop_btn": "Kup prezent w stylu",
        "ads_label": "Sponsor imprezy:",
        "error_gdpr": "Musisz zaakceptować RODO!",
        "status_yes": "Będziemy! 🥳",
        "status_no": "Niestety nie 😢",
        "view_event": "Szczegóły Imprezy"
    },
    "EN": {
        "title": "PartyHero 🦸‍♂️",
        "create_header": "Organize a birthday in 3 minutes!",
        "name_label": "Birthday Child's Name",
        "date_label": "Date",
        "loc_label": "Location",
        "theme_label": "Theme",
        "btn_create": "Generate Invitation ✨",
        "guest_header": "RSVP",
        "guest_name": "Your Name / Child's Name",
        "guest_allergy": "Allergies / Diet",
        "guest_btn": "Send RSVP",
        "gdpr": "I accept the privacy policy and data processing.",
        "success": "Done! Send this link to guests:",
        "shop_btn": "Buy a gift related to",
        "ads_label": "Event Sponsor:",
        "error_gdpr": "You must accept GDPR!",
        "status_yes": "We'll be there! 🥳",
        "status_no": "Sorry, can't make it 😢",
        "view_event": "Event Details"
    },
    "SV": {
        "title": "PartyHero 🦸‍♂️",
        "create_header": "Ordna ett födelsedagskalas på 3 minuter!",
        "name_label": "Födelsedagsbarnets namn",
        "date_label": "Datum",
        "loc_label": "Plats",
        "theme_label": "Tema",
        "btn_create": "Skapa Inbjudan ✨",
        "guest_header": "OSA",
        "guest_name": "Ditt namn / Barnets namn",
        "guest_allergy": "Allergier / Kost",
        "guest_btn": "Skicka svar",
        "gdpr": "Jag godkänner integritetspolicyn och databehandling.",
        "success": "Klart! Skicka denna länk till gästerna:",
        "shop_btn": "Köp en present (Tema):",
        "ads_label": "Eventets sponsor:",
        "error_gdpr": "Du måste godkänna GDPR!",
        "status_yes": "Vi kommer! 🥳",
        "status_no": "Kan tyvärr inte 😢",
        "view_event": "Kalasinformaton"
    }
}

# --- WYBÓR JĘZYKA ---
lang_option = st.sidebar.selectbox("Language / Język / Språk", ["PL", "EN", "SV"])
t = translations[lang_option]

# --- POŁĄCZENIE Z BAZĄ ---
conn = st.connection("gsheets", type=GSheetsConnection)


def get_data(worksheet_name):
    # ttl=0 wymusza pobranie świeżych danych przy każdym odświeżeniu
    try:
        return conn.read(worksheet=worksheet_name, ttl=0)
    except:
        return pd.DataFrame()


def save_party(data_dict):
    df = get_data("Parties")
    new_row = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Parties", data=updated_df)


def save_guest(data_dict):
    df = get_data("Guests")
    new_row = pd.DataFrame([data_dict])
    updated_df = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Guests", data=updated_df)


# --- UI APLIKACJI ---
st.title(t["title"])

# Sprawdzamy ID w linku
query_params = st.query_params
current_party_id = query_params.get("id", None)

# --- SCENARIUSZ 1: GOŚĆ (Widzi zaproszenie) ---
if current_party_id:
    parties_df = get_data("Parties")

    # Sprawdzamy czy impreza istnieje w bazie
    # Konwertujemy ID na string dla pewności porównania
    if not parties_df.empty and str(current_party_id) in parties_df['id'].astype(str).values:

        # Pobieramy wiersz z imprezą
        party = parties_df[parties_df['id'].astype(str) == str(current_party_id)].iloc[0]

        st.subheader(f"🎉 {party['child_name']} Party! 🎉")

        # Karta informacyjna
        with st.container():
            st.markdown(f"""
            <div class='card'>
                <h4>📅 {t['date_label']}: {party['date']}</h4>
                <h4>📍 {t['loc_label']}: {party['location']}</h4>
                <h4>🎭 {t['theme_label']}: {party['theme']}</h4>
            </div>
            """, unsafe_allow_html=True)

        st.write("---")

        # Formularz RSVP
        st.subheader(t["guest_header"])
        with st.form("rsvp_form"):
            g_name = st.text_input(t["guest_name"])
            g_allergy = st.text_input(t["guest_allergy"])
            g_status = st.radio("Status", [t["status_yes"], t["status_no"]])
            g_gdpr = st.checkbox(t["gdpr"])

            submit_guest = st.form_submit_button(t["guest_btn"])

            if submit_guest:
                if not g_gdpr:
                    st.error(t["error_gdpr"])
                elif not g_name:
                    st.error("Name required / Imię wymagane")
                else:
                    guest_data = {
                        "party_id": current_party_id,
                        "guest_name": g_name,
                        "allergy": g_allergy,
                        "status": g_status,
                        "timestamp": str(datetime.now())
                    }
                    save_guest(guest_data)
                    st.success("Wysłano! / Sent!")
                    st.balloons()

        # --- AFILIACJA ---
        st.write("---")
        st.markdown(f"### 🎁 {t['shop_btn']} {party['theme']}")

        # Logika linku (automatyczne wyszukiwanie)
        theme_query = party['theme'].replace(" ", "+")
        # Przykładowy link do Amazon z Twoim tagiem partnerskim
        aff_link = f"https://www.amazon.se/s?k={theme_query}&tag=partyhero-20"

        st.link_button(f"👉 Amazon: {party['theme']}", aff_link)

    else:
        st.error("Event not found / Nie znaleziono imprezy.")
        if st.button("Create New"):
            st.query_params.clear()
            st.rerun()

# --- SCENARIUSZ 2: ORGANIZATOR (Tworzy imprezę) ---
else:
    st.subheader(t["create_header"])

    with st.form("create_party"):
        c_name = st.text_input(t["name_label"])
        c_date = st.date_input(t["date_label"])
        c_loc = st.text_input(t["loc_label"])
        c_theme = st.selectbox(t["theme_label"],
                               ["LEGO", "Minecraft", "Frozen", "Peppa Pig", "Spider-Man", "Barbie", "Dinozaury",
                                "Piłka Nożna"])
        c_gdpr = st.checkbox(t["gdpr"])

        submitted = st.form_submit_button(t["btn_create"])

        if submitted:
            if not c_gdpr:
                st.error(t["error_gdpr"])
            elif not c_name:
                st.error("Name required")
            else:
                new_id = str(uuid.uuid4())[:8]
                party_data = {
                    "id": new_id,
                    "child_name": c_name,
                    "date": str(c_date),
                    "location": c_loc,
                    "theme": c_theme,
                    "created_at": str(datetime.now())
                }
                save_party(party_data)

                # Generowanie linku (na razie localhost)
                # UWAGA: Po wrzuceniu do chmury, zmienisz to na swój adres .streamlit.app
                base_url = "http://localhost:8501"
                # base_url = "https://twoja-apka.streamlit.app"

                final_link = f"{base_url}/?id={new_id}"

                st.success(t["success"])
                st.code(final_link)
                st.balloons()