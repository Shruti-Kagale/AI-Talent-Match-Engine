import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("Candidate Ranking Dashboard")

# --- File uploader section ---
st.header("Upload Files")
uploaded_file1 = st.file_uploader("Upload all_resumes_ranked.xlsx", type=["csv", "xlsx"], key="file1")
uploaded_file2 = st.file_uploader("Upload final_ranking.xlsx", type=["csv", "xlsx"], key="file2")

# --- Function to load dataset ---
def load_data(uploaded_file):
    if uploaded_file is None:
        return None

    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

# ============================================================
#                     FILE 1 SECTION
# ============================================================
if uploaded_file1:
    st.subheader("Data Preview: all_resumes_ranked.xlsx")
    df1 = load_data(uploaded_file1)

    if df1 is not None:
        st.dataframe(df1, height=1200, use_container_width=True)  # SHOW ENTIRE TABLE

        # -------- Plot 1: Final Score Distribution --------
        if "final_score" in df1.columns:
            st.subheader("Final Score Distribution (all_resumes_ranked.xlsx)")
            fig, ax = plt.subplots()
            ax.hist(df1["final_score"], bins=20)
            ax.set_xlabel("Final Score")
            ax.set_ylabel("Count")
            st.pyplot(fig)

        # -------- Plot 2: Rank Distribution --------
        if "rank" in df1.columns:
            st.subheader("Rank Distribution (all_resumes_ranked.xlsx)")
            fig2, ax2 = plt.subplots()
            ax2.hist(df1["rank"], bins=20)
            ax2.set_xlabel("Rank")
            ax2.set_ylabel("Count")
            st.pyplot(fig2)

        # -------- Plot 3: Job-wise Candidate Count --------
        if "job_id" in df1.columns:
            st.subheader("Job-wise Candidate Count (all_resumes_ranked.xlsx)")
            fig3, ax3 = plt.subplots()
            df1["job_id"].value_counts().plot(kind="bar", ax=ax3)
            ax3.set_xlabel("Job ID")
            ax3.set_ylabel("Number of Candidates")
            st.pyplot(fig3)

# ============================================================
#                     FILE 2 SECTION
# ============================================================
if uploaded_file2:
    st.subheader("Data Preview: final_ranking.xlsx")
    df2 = load_data(uploaded_file2)

    if df2 is not None:
        st.dataframe(df2, height=1200, use_container_width=True)

        # -------- Plot 1: Final Score Distribution --------
        if "final_score" in df2.columns:
            st.subheader("Final Score Distribution (final_ranking.xlsx)")
            fig4, ax4 = plt.subplots()
            ax4.hist(df2["final_score"], bins=20)
            ax4.set_xlabel("Final Score")
            ax4.set_ylabel("Count")
            st.pyplot(fig4)

        # -------- Plot 2: Rank Distribution --------
        if "rank" in df2.columns:
            st.subheader("Rank Distribution (final_ranking.xlsx)")
            fig5, ax5 = plt.subplots()
            ax5.hist(df2["rank"], bins=20)
            ax5.set_xlabel("Rank")
            ax5.set_ylabel("Count")
            st.pyplot(fig5)

        # -------- Plot 3: Job-wise Candidate Count --------
        if "job_id" in df2.columns:
            st.subheader("Job-wise Candidate Count (final_ranking.xlsx)")
            fig6, ax6 = plt.subplots()
            df2["job_id"].value_counts().plot(kind="bar", ax=ax6)
            ax6.set_xlabel("Job ID")
            ax6.set_ylabel("Number of Candidates")
            st.pyplot(fig6)

# ============================================================
#                  NO FILE UPLOADED MESSAGE
# ============================================================
if not uploaded_file1 and not uploaded_file2:
    st.info("Please upload a CSV or XLSX file to view rankings.")
