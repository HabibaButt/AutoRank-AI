import streamlit as st
import pandas as pd

st.set_page_config(page_title="AutoRank AI", layout="wide")

# -----------------------------
# TITLE
# -----------------------------
st.title("AutoRank AI – Candidate Ranking Portal")
st.write("AI-powered candidate ranking based on job requirements.")
st.divider()

# -----------------------------
# FILE PATHS
# (must be in same folder)
# -----------------------------
JOBS_FILE = "AutoRank_AI_PersonA_Data - Jobs.csv"

RANKING_FILES = {
    "Data Analyst": "AutoRank_AI_PersonA_Data - Job1_Ranking.csv",
    "Marketing Manager": "AutoRank_AI_PersonA_Data - Job2_Ranking.csv",
    "Software Engineer": "AutoRank_AI_PersonA_Data - Job3_Ranking.csv"
}

# -----------------------------
# HELPERS
# -----------------------------
def safe_str(x):
    if pd.isna(x):
        return ""
    return str(x).strip()

def load_jobs():
    try:
        return pd.read_csv(JOBS_FILE)
    except:
        return None

def load_rankings(job):
    file = RANKING_FILES.get(job)
    try:
        df = pd.read_csv(file)
        return df
    except:
        return None

def find_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# -----------------------------
# SESSION STATE
# -----------------------------
if "run_clicked" not in st.session_state:
    st.session_state.run_clicked = False

jobs_df = load_jobs()

# -----------------------------
# LAYOUT
# -----------------------------
left, right = st.columns([1,2])

# -----------------------------
# LEFT PANEL
# -----------------------------
with left:

    st.subheader("Job Input")

    demo_job = st.selectbox(
        "Select Demo Job",
        ["Data Analyst","Marketing Manager","Software Engineer"]
    )

    default_title = demo_job
    default_desc = ""

    if jobs_df is not None:

        title_col = find_column(jobs_df,
            ["Job_Title","Job Title","Title"]
        )

        desc_col = find_column(jobs_df,
            ["Job_Description","Job Description","Description"]
        )

        if title_col and desc_col:

            match = jobs_df[jobs_df[title_col] == demo_job]

            if len(match) > 0:
                default_desc = safe_str(match.iloc[0][desc_col])

    job_title = st.text_input("Job Title", value=default_title)

    job_desc = st.text_area(
        "Job Description",
        value=default_desc,
        height=150
    )

    st.divider()

    st.subheader("Filter")

    tier_filter = st.radio(
        "Candidate Tier",
        ["All","High","Medium","Low"]
    )

    run = st.button("Find Candidates")

    if run:
        st.session_state.run_clicked = True

    st.divider()

    st.caption(
        "AI Confidence Score reflects skill match, experience weight and relevance scoring."
    )

# -----------------------------
# RIGHT PANEL
# -----------------------------
with right:

    st.subheader("Ranked Candidates")

    if not st.session_state.run_clicked:

        st.info(
            "Select a demo job on the left, then click Find Candidates."
        )
        st.stop()

    st.success(f"Showing results for: {job_title}")

    df = load_rankings(demo_job)

    if df is None:
        st.warning("Ranking file not found.")
        st.stop()

    # find important columns safely
    name_col = find_column(df, ["Name","Candidate","Candidate_Name"])
    score_col = find_column(df, ["Final_Score","Score"])
    tier_col = find_column(df, ["Tier"])

    matching_col = find_column(df, ["Matching"])
    missing_col = find_column(df, ["Missing"])

    if score_col:
        df = df.sort_values(by=score_col, ascending=False)

    # top candidate
    top_score = df[score_col].max() if score_col else None

    # filter tier
    if tier_filter != "All" and tier_col:
        df = df[df[tier_col].astype(str).str.contains(tier_filter)]

    for _, r in df.iterrows():

        name = safe_str(r.get(name_col,"Unknown"))

        score = r.get(score_col,0)
        score_pct = int(score * 100) if score <= 1 else int(score)

        tier = safe_str(r.get(tier_col,"Low"))

        matching = safe_str(r.get(matching_col,""))
        missing = safe_str(r.get(missing_col,""))

        if "High" in tier:
            color = "#00FF88"
        elif "Medium" in tier:
            color = "orange"
        else:
            color = "#FF4B4B"

        with st.container(border=True):

            col1, col2 = st.columns([3,1])

            with col1:

                title = f"### {name}"

                if score == top_score:
                    title += " 🥇"

                st.markdown(title)

            with col2:

                st.markdown(
                    f"<h2>{score_pct}%</h2>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<span style='color:{color};font-weight:700'>{tier}</span>",
                    unsafe_allow_html=True
                )

            st.markdown(
                "<span style='color:#00FF88;font-weight:700'>Matching skills:</span> "
                + (matching if matching else "None"),
                unsafe_allow_html=True
            )

            st.markdown(
                "<span style='color:#FF4B4B;font-weight:700'>Missing skills:</span> "
                + (missing if missing else "None"),
                unsafe_allow_html=True
            )

            st.caption("Experience calculated from skill columns.")