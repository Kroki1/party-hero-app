import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="PartyHero", page_icon="🎂", layout="centered")

# --- CSS: MODERN & PROFESSIONAL DESIGN ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    .stApp {
        background-color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    h1, h2, h3 {
        color: #111827;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .stButton>button {
        background-color: #6366f1;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        border: none;
        width: 100%;
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);
        transition: all 0.2s;
    }

    .stButton>button:hover {
        background-color: #4f46e5;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
        transform: translateY(-1px);
    }

    .info-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 24px;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        padding: 10px;
        color: #374151;
    }

    .small-text {
        font-size: 0.875rem;
        color: #6B7280;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SŁOWNIK JĘZYKOWY ---
translations = {
    "PL": {
        "hero_title": "Twoje idealne przyjęcie zaczyna się tutaj.",
        "hero_sub": "Stwórz piękne zaproszenie, zbierz potwierdzenia i ogarnij prezenty. Wszystko w jednym miejscu.",
        "create_tab": "Utwórz Wydarzenie",
        "name_label": "Kto świętuje?",
        "date_label": "Kiedy?",
        "loc_label": "Miejsce (Nazwa)",
        "addr_label": "Dokładny adres",
        "theme_label": "Motyw przewodni",
        "btn_create": "Utwórz Zaproszenie",
        "guest_header": "Potwierdzenie obecności",
        "guest_sub": "Daj znać, czy będziesz świętować z nami!",
        "guest_name": "Imię i nazwisko",
        "guest_allergy": "Dieta / Alergie (opcjonalne)",
        "guest_btn": "Potwierdzam obecność",
        "gdpr": "Wyrażam zgodę na przetwarzanie danych w celu organizacji wydarzenia.",
        "success_host": "Gotowe! Twój link do zaproszeń:",
        "success_guest": "Dziękujemy! Twoja odpowiedź została zapisana.",
        "shop_header": "Pomysły na prezent",
        "status_yes": "Będę! 🎉",
        "status_no": "Niestety nie dam rady",
        "error_gdpr": "Prosimy o akceptację zgody RODO.",
        "error_fill": "Wypełnij wymagane pola.",
        "placeholder_name": "np. 5 urodziny Jasia",
        "placeholder_loc": "np. Sala Zabaw Fikołki",
        "placeholder_addr": "np. ul. Kwiatowa 5, Warszawa",
        "view_map": "Zobacz na mapie",
    },
    "EN": {
        "hero_title": "Your perfect party starts here.",
        "hero_sub": "Create beautiful invitations, track RSVPs, and manage gifts. All in one place.",
        "create_tab": "Create Event",
        "name_label": "Who is celebrating?",
        "date_label": "When?",
        "loc_label": "Venue Name",
        "addr_label": "Exact Address",
        "theme_label": "Theme",
        "btn_create": "Create Invitation",
        "guest_header": "RSVP",
        "guest_sub": "Let us know if you can make it!",
        "guest_name": "Full Name",
        "guest_allergy": "Diet / Allergies (optional)",
        "guest_btn": "Confirm Attendance",
        "gdpr": "I agree to data processing for event organization purposes.",
        "success_host": "Done! Here is your invitation link:",
        "success_guest": "Thank you! Your response has been saved.",
        "shop_header": "Gift Ideas",
        "status_yes": "I'll be there! 🎉",
        "status_no": "Can't make it",
        "error_gdpr": "Please accept the privacy policy.",
        "error_fill": "Please fill in required fields.",
        "placeholder_name": "e.g. John's 5th Birthday",
        "placeholder_loc": "e.g. Central Park",
        "placeholder_addr": "e.g. 5th Avenue, NY",
        "view_map": "View on Map",
    },
    "SV": {
        "hero_title": "Ditt perfekta kalas börjar här.",
        "hero_sub": "Skapa vackra inbjudningar, samla in svar och hantera presenter. Allt på ett ställe.",
        "create_tab": "Skapa Evenemang",
        "name_label": "Vem firar?",
        "date_label": "När?",
        "loc_label": "Plats (Namn)",
        "addr_label": "Exakt adress",
        "theme_label": "Tema",
        "btn_create": "Skapa Inbjudan",
        "guest_header": "OSA",
        "guest_sub": "Låt oss veta om du kommer!",
        "guest_name": "För- och efternamn",
        "guest_allergy": "Kost / Allergier (frivilligt)",
        "guest_btn": "Bekräfta",
        "gdpr": "Jag godkänner databehandling för detta evenemang.",
        "success_host": "Klart! Här är din länk:",
        "success_guest": "Tack! Ditt svar har sparats.",
        "shop_header": "Presenttips",
        "status_yes": "Jag kommer! 🎉",
        "status_no": "Kan tyvärr inte",
        "error_gdpr": "Vänligen godkänn integritetspolicyn.",
        "error_fill": "Fyll i alla obligatoriska fält.",
        "placeholder_name": "t.ex. Annas 5-års kalas",
        "placeholder_loc": "t.ex. Leo's Lekland",
        "placeholder_addr": "t.ex. Storgatan 1, Stockholm",
        "view_map": "Visa på karta",
    },
}

# --- HEADER ---
col_brand, col_lang = st.columns([8, 2])
with col_brand:
    st.markdown("### PartyHero 🎈")
with col_lang:
    lang_option = st.selectbox(
        "Language", ["SV", "EN", "PL"], label_visibility="collapsed"
    )

t = translations[lang_option]

# --- POŁĄCZENIE Z BAZĄ ---
conn = st.connection("gsheets", type=GSheetsConnection)


def get_data(worksheet_name):
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


# --- LOGIKA ---
query_params = st.query_params
current_party_id = query_params.get("id", None)

# === WIDOK GOŚCIA (ZAPROSZENIE) ===
if current_party_id:
    parties_df = get_data("Parties")

    if (
        not parties_df.empty
        and str(current_party_id) in parties_df["id"].astype(str).values
    ):
        party = parties_df[parties_df["id"].astype(str) == str(current_party_id)].iloc[
            0
        ]

        st.markdown(
            f"""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="margin-bottom: 10px;">🎉 {party['child_name']}</h1>
            <p style="color: #6B7280; font-size: 1.1rem;">Zaprasza na wspólną zabawę!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Generowanie linku do Google Maps
        # Łączymy nazwę miejsca i adres, zamieniamy spacje na plusy
        map_query = f"{party['location']} {party.get('address', '')}".strip().replace(
            " ", "+"
        )
        map_link = f"https://www.google.com/maps/search/?api=1&query={map_query}"

        # Karta ze szczegółami
        st.markdown(
            f"""
        <div class="info-card">
            <h4 style="margin-top:0;">📅 {party['date']}</h4>
            <h4 style="margin-top:10px; margin-bottom: 5px;">📍 {party['location']}</h4>
            <p style="color: #6B7280; font-size: 0.9rem; margin-bottom: 10px;">{party.get('address', '')}</p>
            <a href="{map_link}" target="_blank" style="color: #6366f1; text-decoration: none; font-weight: 600; font-size: 0.9rem;">🗺️ {t['view_map']}</a>
            <div style="margin-top: 15px; padding: 10px; background-color: #F3F4F6; border-radius: 6px; font-size: 0.9em;">
                🎨 <b>{t['theme_label']}:</b> {party['theme']}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Formularz RSVP
        st.markdown(f"### {t['guest_header']}")
        st.markdown(
            f"<p class='small-text'>{t['guest_sub']}</p>", unsafe_allow_html=True
        )

        with st.form("rsvp_form"):
            g_name = st.text_input(t["guest_name"])
            g_status = st.radio(
                "Decyzja",
                [t["status_yes"], t["status_no"]],
                label_visibility="collapsed",
            )
            g_allergy = st.text_input(t["guest_allergy"])
            g_gdpr = st.checkbox(t["gdpr"])

            submit_guest = st.form_submit_button(t["guest_btn"])

            if submit_guest:
                if not g_gdpr:
                    st.error(t["error_gdpr"])
                elif not g_name:
                    st.error(t["error_fill"])
                else:
                    guest_data = {
                        "party_id": current_party_id,
                        "guest_name": g_name,
                        "allergy": g_allergy,
                        "status": g_status,
                        "timestamp": str(datetime.now()),
                    }
                    save_guest(guest_data)
                    st.success(t["success_guest"])
                    st.balloons()

        # Sekcja prezentowa (Afiliacja)
        st.markdown("---")
        st.markdown(f"### 🎁 {t['shop_header']}")
        theme_query = party["theme"].replace(" ", "+")
        aff_link = f"https://www.amazon.se/s?k={theme_query}&tag=partyhero-20"

        st.markdown(
            f"""
        <a href="{aff_link}" target="_blank" style="text-decoration: none;">
            <div style="background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 15px; display: flex; align-items: center; justify-content: space-between; transition: 0.2s;">
                <span style="font-weight: 600; color: #111827;">👉 Zobacz pomysły na prezent: {party['theme']}</span>
                <span style="color: #6366f1;">➔</span>
            </div>
        </a>
        """,
            unsafe_allow_html=True,
        )

    else:
        st.error("Link nieaktywny / Invalid link.")
        if st.button("Start"):
            st.query_params.clear()
            st.rerun()

# === WIDOK ORGANIZATORA ===
else:
    st.markdown(
        f"""
    <div style="padding: 20px 0 40px 0; text-align: center;">
        <h1 style="font-size: 2.5rem; line-height: 1.2;">{t['hero_title']}</h1>
        <p style="font-size: 1.1rem; color: #4B5563; margin-top: 15px;">{t['hero_sub']}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown(f'<div class="info-card">', unsafe_allow_html=True)
        st.subheader(t["create_tab"])

        with st.form("create_party"):
            c_name = st.text_input(t["name_label"], placeholder=t["placeholder_name"])

            col1, col2 = st.columns(2)
            with col1:
                c_date = st.date_input(t["date_label"], format="DD.MM.YYYY")
            with col2:
                # Etykieta Theme teraz będzie widoczna!
                c_theme = st.selectbox(
                    t["theme_label"],
                    [
                        "LEGO",
                        "Minecraft",
                        "Frozen",
                        "Peppa Pig",
                        "Spider-Man",
                        "Barbie",
                        "Dinozaury",
                        "Piłka Nożna",
                    ],
                )

            c_loc = st.text_input(t["loc_label"], placeholder=t["placeholder_loc"])
            c_addr = st.text_input(
                t["addr_label"], placeholder=t["placeholder_addr"]
            )  # NOWE POLE

            st.markdown("---")
            c_gdpr = st.checkbox(t["gdpr"])

            submitted = st.form_submit_button(t["btn_create"])

            if submitted:
                if not c_gdpr:
                    st.error(t["error_gdpr"])
                elif not c_name:
                    st.error(t["error_fill"])
                else:
                    new_id = str(uuid.uuid4())[:8]
                    party_data = {
                        "id": new_id,
                        "child_name": c_name,
                        "date": c_date.strftime("%d.%m.%Y"),
                        "location": c_loc,
                        "address": c_addr,  # ZAPISUJEMY ADRES
                        "theme": c_theme,
                        "created_at": str(datetime.now()),
                    }
                    save_party(party_data)

                    # Pamiętaj zmienić link na swój!
                    base_url = "https://party-hero-poc.streamlit.app"

                    final_link = f"{base_url}/?id={new_id}"

                    st.success(t["success_host"])
                    st.code(final_link)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div style="text-align: center; margin-top: 40px; color: #9CA3AF; font-size: 0.9rem;">
        🔒 Secure & Private • GDPR Compliant • Free to use
    </div>
    """,
        unsafe_allow_html=True,
    )
