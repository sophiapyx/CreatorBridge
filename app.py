import streamlit as st
import pandas as pd
import requests
try:
    import ollama
except ImportError:
    ollama = None

from utils.google_sheets import GoogleSheetsManager
# --- SECURITY GATE ---

def check_password():
    """Only when the correct password is entered will the subsequent content be displayed"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        # Login interface configuration
        st.set_page_config(page_title="CreatorBridge Login", page_icon="🔐")
        st.title("✦ CreatorBridge")
        password = st.text_input("Enter Access Key:", type="password")

        # Password：Socialmedia
        if password == "Socialmedia":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            if password: 
                st.error("Invalid Key. Please contact Sophiayx321@gmail.com.")
            st.stop()
# Run the password check. If it fails, the execution will stop here.
check_password()

# ---------------------------------------------------

# 1. Page Configuration & Professional Theme
st.set_page_config(page_title="CreatorBridge OS", layout="wide", page_icon="✦")

THEME_CONFIG = {
    "Draft": ["#1677FF", "#E6F4FF"],      
    "Review": ["#722ED1", "#F9F0FF"],     
    "Approved": ["#52C41A", "#F6FFED"],   
    "Published": ["#FAAD14", "#FFFBE6"]   
}

def get_status_cfg(status):
    s = status.capitalize()
    cfg = THEME_CONFIG.get(s, ["#8C8C8C", "#F5F5F5"])
    icon_map = {"Draft": "◇", "Review": "◈", "Approved": "✦", "Published": "✓"}
    return {"color": cfg[0], "bg": cfg[1], "icon": icon_map.get(s, "◦")}

# AI Content Generation Function
def generate_content(source_text, platform):
    if ollama is None:
        return "Error: 'ollama' library not installed in venv."
    
    prompt = f"Rewrite the following LinkedIn post for {platform}. Use appropriate emojis and formatting: {source_text}"
    try:
        # Note: Ensure you have run 'ollama cp llama3.1 llama3' in terminal
        response = ollama.generate(model='llama3', prompt=prompt)
        return response['response']
    except Exception as e:
        return f"AI Error: {str(e)}"

@st.cache_resource
def get_manager():
    return GoogleSheetsManager()

sheet_mgr = get_manager()

def load_data():
    records = sheet_mgr.client.open_by_key(sheet_mgr.sheet_id).sheet1.get_all_records()
    df = pd.DataFrame(records)
    df.columns = [c.strip() for c in df.columns]
    return df.map(lambda x: x.strip() if isinstance(x, str) else x)

# --- Data Processing ---
df = load_data()

with st.sidebar:
    st.markdown("## ✦ CreatorBridge")
    category = st.radio("Display Mode", list(THEME_CONFIG.keys()), index=1)
    st.markdown("---")
    if st.button("🔄 Refresh OS", use_container_width=True):
        st.rerun()

# 2. Dynamic CSS Injection
theme = get_status_cfg(category)
st.markdown(f"""
    <style>
    :root {{ 
        --primary-color: {theme['color']}; 
        --bg-hover: {theme['bg']};
    }}
    .st-bc {{ border-color: var(--primary-color) !important; }}
    .st-bd {{ border-color: var(--primary-color) !important; color: #31333F !important; }}
    button[data-baseweb="tab"][aria-selected="true"] {{ 
        color: var(--primary-color) !important; 
        border-bottom-color: var(--primary-color) !important; 
    }}
    textarea, input {{ 
        color: #31333F !important; 
        -webkit-text-fill-color: #31333F !important; 
    }}
    textarea:focus, input:focus {{ 
        border-color: var(--primary-color) !important; 
        box-shadow: 0 0 0 2px {theme['bg']} !important; 
    }}
    .stExpander {{ border: 1px solid #f0f0f0 !important; border-radius: 8px !important; margin-bottom: 8px !important; }}
    textarea {{ min-height: 280px !important; border-radius: 4px !important; }}
    .schedule-label {{ font-size: 0.85rem; color: #8c8c8c; display: flex; align-items: center; gap: 4px; margin-bottom: 4px; }}
    </style>
    """, unsafe_allow_html=True)

# Data filtering
display_df = df[df['status'].str.lower() == category.lower()]
display_df = display_df.sort_values(by='id', ascending=False)

st.title(f"{theme['icon']} {category} Center")

for index, row in display_df.iterrows():
    header = f"{theme['icon']} ID: {row['id']} | {row['title']}"
    
    with st.expander(header, expanded=False):
        col_ctrl, col_main = st.columns([1.2, 3.5])
        
        # --- Left Control Column ---
        with col_ctrl:
            st.markdown("### ⚙️ Control")
            status_opts = [s.lower() for s in THEME_CONFIG.keys()]
            current_status = row['status'].lower()
            new_s = st.selectbox("Update status", status_opts, index=status_opts.index(current_status), key=f"s_{row['id']}")
            
            if st.button("Apply Changes", key=f"b_{row['id']}", use_container_width=True):
                sheet_mgr.sheet.update_cell(index + 2, df.columns.get_loc('status') + 1, new_s)
                st.rerun()
            
            st.markdown("---")

            # --- Original Notes Link (Placed above image) ---
            if row.get('original_notes_url'):
                st.link_button("📂 Open Original Notes", row['original_notes_url'], use_container_width=True)
                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

            # Media Preview
            if row.get('media_url'):
                st.image(row['media_url'], use_container_width=True)

        # --- Right Content Center ---
        with col_main:
            tabs = st.tabs(["LinkedIn", "Instagram", "Facebook", "Mastodon"])
            p_configs = [
                (tabs[0], "LinkedIn", "LI_CONTENT", "LI_time", "LI_posted", "LI"),
                (tabs[1], "Instagram", "AI_IG", "IG_time", "IG_posted", "IG"),
                (tabs[2], "Facebook", "AI_FB", "FB_time", "FB_posted", "FB"),
                (tabs[3], "Mastodon", "AI_MD", "MD_time", "MD_posted", "MD")
            ]

            for tab, p_name, c_col, t_col, post_col, l_key in p_configs:
                with tab:
                    text_val = row.get(c_col, "")
                    new_text = st.text_area("Post Content", value=text_val, key=f"t_{c_col}_{row['id']}")
                    
                    r1, r2, r3, r4 = st.columns([1, 1, 1, 1.8])
                    with r1:
                        if st.button("💾 Save", key=f"sv_{c_col}_{row['id']}", use_container_width=True):
                            sheet_mgr.sheet.update_cell(index + 2, df.columns.get_loc(c_col) + 1, new_text)
                            st.toast("Saved!")
                    
                    with r2:
                        # Only show AI Gen for Draft and Review status
                        if p_name != "LinkedIn" and current_status in ["draft", "review"]:
                            if st.button("🤖 AI Gen", key=f"ai_{c_col}_{row['id']}", use_container_width=True):
                                with st.spinner("Processing..."):
                                    res = generate_content(row['LI_CONTENT'], p_name)
                                    sheet_mgr.sheet.update_cell(index + 2, df.columns.get_loc(c_col) + 1, res)
                                    st.rerun()
                    with r3:
                        is_live = row.get(post_col) == "Yes"
                        dot = "🟢" if is_live else "⏳"
                        st.markdown(f"<div style='padding-top:5px;'>{dot} <b>{'Live' if is_live else 'Wait'}</b></div>", unsafe_allow_html=True)
                    
                    with r4:
                        live_links = str(row.get('Live_Links', ""))
                        p_link = None
                        for line in live_links.split('\n'):
                            if l_key in line and "http" in line:
                                p_link = line.split(':', 1)[-1].strip()
                        
                        if p_link:
                            st.link_button(f"🔗 View on {p_name}", p_link, use_container_width=True)

                    st.markdown(f'<div class="schedule-label">🕒 Schedule Setting</div>', unsafe_allow_html=True)
                    c_time, c_sync = st.columns([3.5, 1])
                    with c_time:
                        new_t = st.text_input("Time", value=str(row.get(t_col, "")), label_visibility="collapsed", key=f"tm_{t_col}_{row['id']}")
                    with c_sync:
                        if st.button("Sync", key=f"bt_{t_col}_{row['id']}", use_container_width=True):
                            sheet_mgr.sheet.update_cell(index + 2, df.columns.get_loc(t_col) + 1, new_t)
                            st.success("Synced")