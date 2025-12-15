import streamlit as st
import pandas as pd
import altair as alt
import io
from io import BytesIO
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import re

# Import utility functions (Assuming these are the final, working versions)
from utils import extract_text_from_file
from parsing import extract_contact_info, extract_name, extract_skills
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define a simple skills database (Expanded list for better matching)
SKILLS_DB = [
    "python", "java", "c++", "sql", "machine learning", "data analysis",
    "communication", "project management", "streamlit", "react", "html", "css",
    "javascript", "git", "github", "leetcode", "bootstrap", "nlp", "django", "next.js",
    "aws", "docker", "kubernetes", "tensorflow", "pytorch", "sass", "typescript"
]

st.set_page_config(page_title="Resume Intelligent Parser", layout="wide")


# --- Test Resume Mock Class & Function (Required for the Test Button to work) ---

class MockUploadedFile:
    def __init__(self, buffer, name, type):
        self.file = buffer
        self.name = name
        self.type = type

    def read(self):
        self.file.seek(0)
        return self.file.read()


def create_in_memory_resume(name, skills_str):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, name.upper())
    c.setFont("Helvetica", 10)
    c.drawString(50, 735, "Test Developer | test@example.com | +91 9999900000")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 630, "SKILLS")
    c.line(50, 625, 250, 625)
    c.setFont("Helvetica", 10)
    c.drawString(50, 610, skills_str)
    c.save()
    buffer.seek(0)
    return MockUploadedFile(buffer, f"{name.replace(' ', '_')}_Test.pdf", "application/pdf")


# --- CORE FUNCTION: TIPS GENERATION (FIXED) ---

def generate_resume_tips(name, email, phone, match_score, current_skills_set, required_skills_set):
    """
    Generates personalized resume improvement tips based on parsing results and JD match.
    FIX: Ensures dynamic numbering and unique tips based on flaws.
    """
    raw_tips = []

    # 1. Critical Format Flaws (Unique to each candidate based on parsing)
    if name == "Unknown Candidate":
        raw_tips.append(
            "**Name Extraction Failure:** Your name was difficult to extract. Use a clear, **bold font** and place it explicitly on the first line.")
    if not email:
        raw_tips.append(
            "**Missing Email:** Your professional email address is missing or unclear. Ensure it is explicitly present and easy to read.")
    if not phone:
        raw_tips.append(
            "**Missing Phone:** Your phone number was not easily found. Label it clearly (e.g., 'Mobile:') to ensure quick contact.")

    # 2. Skill Gap Analysis (Unique to each candidate and JD)
    missing_skills = required_skills_set - current_skills_set

    if missing_skills:
        top_missing = list(missing_skills)[:4]  # Show top 4 missing skills
        raw_tips.append(
            f"**Critical Skill Gap:** You are missing key required skills like: **{', '.join(top_missing).title()}**. Update your resume to include projects or experience demonstrating these abilities.")

    # 3. Match Score Optimization (Unique to score range)
    if match_score < 40:
        raw_tips.append(
            "**Low Match Score:** Your resume lacks fundamental keywords from the JD. Review the JD and integrate those specific technical skills and context (verbs, industry terms) into your bullet points to boost your score.")
    elif 40 <= match_score < 70:
        raw_tips.append(
            "**Optimization:** Your score is decent, but you must focus on **quantifying your achievements** (e.g., 'improved query speed by 25%', 'managed team of 5').")

    # 4. General Best Practice Tips (Added if fewer than 5 specific tips are found)

    # Add a tip about project clarity if the current skill set is small
    if len(current_skills_set) < 5:
        raw_tips.append(
            "**Project Detail:** Ensure you list the specific **technologies used** under each project/experience section for better parsing.")

    # Add a general, high-value tip if not enough tips are generated yet
    if len(raw_tips) < 5:
        raw_tips.append(
            "**Readability & ATS:** Keep all bullet points concise (1-2 lines). Use strong **action verbs** at the start of every sentence (e.g., Developed, Managed, Implemented).")

    # Final Conclusion for perfect match
    if match_score >= 85 and not missing_skills and name != "Unknown Candidate" and email and phone:
        return "✅ **Excellent Match!** Your resume is highly relevant and well-formatted. Focus on preparing interview questions that highlight your quantified achievements."

    # Combine tips with dynamic numbering
    numbered_tips = []
    for i, tip in enumerate(raw_tips):
        # Only add a tip if it's unique (simple check)
        if tip not in [t.split('**', 1)[1] for t in numbered_tips]:
            numbered_tips.append(f"**{i + 1}.** {tip}")

    # Ensure there are no duplicate general tips if they were added automatically

    return "<br>".join(numbered_tips)  # Use <br> for simple line breaks


# --- Main App Structure ---

st.title("📄 AI Resume Parser & Ranking System (rishi jain)")
st.markdown("Upload resumes to extract information and match against a Job Description.")

# Sidebar for Job Description
st.sidebar.header("1. Job Description")
job_description = st.sidebar.text_area("Paste the Job Description (JD) here:", height=300)

# File Uploader
st.sidebar.header("2. Upload Resumes")
if 'uploaded_files_list' not in st.session_state:
    st.session_state.uploaded_files_list = []

uploaded_files = st.sidebar.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    current_names = [f.name for f in st.session_state.uploaded_files_list]
    for file in uploaded_files:
        if file.name not in current_names:
            st.session_state.uploaded_files_list.append(file)
            current_names.append(file.name)

# --- TEST FEATURE ---
st.sidebar.markdown("---")
st.sidebar.header("3. Test Feature")

if st.sidebar.button("Use Test Resume: JOHN DOE"):
    test_resume = create_in_memory_resume("JOHN DOE", "Python, Java, React, SQL, Docker")
    if test_resume.name not in [f.name for f in st.session_state.uploaded_files_list]:
        st.session_state.uploaded_files_list.append(test_resume)
        st.sidebar.success(f"Test Resume '{test_resume.name}' added for processing!")
    else:
        st.sidebar.warning(f"Test Resume '{test_resume.name}' already added.")

files_to_process = st.session_state.uploaded_files_list

if files_to_process and job_description:
    st.header("Ranking & Analysis")

    results = []
    processed_files_map = {}

    # --- STEP 1: Determine Required Skills from JD ---
    jd_tokens = set(re.findall(r'\b\w+\b', job_description.lower()))
    required_skills = jd_tokens.intersection([s.lower() for s in SKILLS_DB])

    if not required_skills:
        st.warning("No relevant technical skills detected in the Job Description based on the defined SKILLS_DB.")
    else:
        st.info(f"**Required Skills Detected:** {', '.join(sorted(required_skills)).title()}")

    for file in files_to_process:
        if file.name in processed_files_map:
            results.append(processed_files_map[file.name])
            continue

        try:
            # 1. Extract Text
            text = extract_text_from_file(file)

            # 2. Parse Info
            contact = extract_contact_info(text)
            name = extract_name(text)
            raw_skills = extract_skills(text, SKILLS_DB)

            # 3. Match with JD (Cosine Similarity)
            text_list = [text, job_description]
            cv = CountVectorizer()
            count_matrix = cv.fit_transform(text_list)
            match_percentage = cosine_similarity(count_matrix)[0][1] * 100

            # 4. Generate Tips
            tips = generate_resume_tips(
                name=name,
                email=contact['email'],
                phone=contact['phone'],
                match_score=match_percentage,
                current_skills_set=set(raw_skills),
                required_skills_set=required_skills
            )

            result = {
                "Name": name,
                "Email": contact['email'],
                "Phone": contact['phone'],
                "Skills Found": ", ".join(raw_skills),
                "Match Score": match_percentage,
                "Tips for Improvement": tips
            }
            results.append(result)
            processed_files_map[file.name] = result

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")

    # Display Results in a DataFrame
    df = pd.DataFrame(results)

    if not df.empty:
        df = df.sort_values(by="Match Score", ascending=False)
        df['Match Score Display'] = df['Match Score'].apply(lambda x: f"{x:.2f}%")

        # --- 1. VISUAL COMPARISON GRAPH ---
        st.subheader("📊 Candidate Comparison")

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Name', sort=alt.EncodingSortField(field='Match Score', op='average', order='descending')),
            y=alt.Y('Match Score', title='Match Score (%)'),
            tooltip=['Name', 'Match Score Display']
        ).properties(title="Match Score by Candidate").interactive()

        st.altair_chart(chart, use_container_width=True)

        # --- 2. DETAILED RANKING TABLE ---
        st.subheader("🏆 Detailed Rankings")

        # Display ranking table without the Tips column
        st.dataframe(
            df[["Name", "Match Score Display", "Phone", "Email", "Skills Found"]].rename(
                columns={"Match Score Display": "Match Score"}
            ),
            use_container_width=True,
            hide_index=True
        )

        # --- 3. SEPARATE TIPS SECTION (NEW) ---
        st.markdown("---")
        st.subheader("💡 Personalized Improvement Tips")

        # Loop through the DataFrame to display tips for each candidate
        for index, row in df.iterrows():
            # Use an expander for clean display
            # Check if the tip is the default 'Excellent Match' message
            is_excellent_match = row["Tips for Improvement"].startswith('✅')

            if is_excellent_match:
                st.success(
                    f"Tips for: **{row['Name']}** (Score: {row['Match Score Display']}): {row['Tips for Improvement']}")
            else:
                if st.checkbox(f"Show Tips for: **{row['Name']}** (Score: {row['Match Score Display']})",
                               key=f"tip_box_{index}"):
                    st.markdown(row["Tips for Improvement"], unsafe_allow_html=True)
                    st.markdown("---")  # Separator for neatness

elif files_to_process and not job_description:
    st.info("Please add a Job Description in the sidebar to start ranking.")