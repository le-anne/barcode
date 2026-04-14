import streamlit as st

def apply_mobile_first_style():
    """Injects custom CSS to create a centered, mobile-first cinematic look."""
    css = """
    <style>
        /* 1. Overall Page Style: Cinematic Dark Mode */
        .stApp {
            background-color: #0F0F0F; /* Deep charcoal */
            color: #FFFFFF; /* Crisp white */
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }

        /* 2. MOBILE-FIRST CONTAINER: 
           This makes the content 90% wide on mobile, 
           but limits it to 1000px on desktop so it isn't too wide. 
           It also centers everything. */
        .block-container {
            padding: 1rem 1rem !important;
            max-width: 1000px !important;
            margin: auto !important;
        }

        /* 3. CENTER EVERY IMAGE */
        div[data-testid="stImage"] {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: auto !important;
        }

        /* 4. Center Titles and Inputs */
        div[data-testid="stTextInput"], div[data-testid="stButton"] {
            margin: auto !important;
        }
        
        div[data-testid="stHeader"], div[data-testid="stSubheader"], div[data-testid="stCaption"] {
            text-align: center !important;
            margin: auto !important;
        }

        /* 5. Mobile-Responsive Columns: 
           If the screen is small (mobile), force columns to stack. */
        @media (max-width: 600px) {
            div[data-testid="stHorizontalBlock"] > div {
                min-width: 100% !important;
                margin-top: 10px !important;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)