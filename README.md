# ai_resume_parser-ranking_system

An advanced AI-powered tool designed to automate the recruitment process. This system extracts key information (Name, Email, Phone, and Skills) from resumes in **PDF** and **DOCX** formats and ranks them against a specific Job Description (JD) using Natural Language Processing (NLP).

## ✨ Key Features

  * **Automated Extraction:** Automatically identifies candidate names, contact details, and technical skills.
  * **Intelligent Ranking:** Uses **Cosine Similarity** to compare resume content with the Job Description and provides a match percentage.
  * **Skill Gap Analysis:** Identifies which required skills are missing from the candidate's resume.
  * **Personalized Feedback:** Generates dynamic "Tips for Improvement" based on specific flaws found in the resume.
  * **Visual Comparison:** Includes interactive charts to compare multiple candidates visually.
  * **Batch Processing:** Upload and analyze multiple resumes simultaneously.

-----

## 🚀 Installation & Setup

Follow these steps to set up the project on your local machine:

### 1\. Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/your-username/ai_resume_parser-ranking_system.git
cd ai_resume_parser-ranking_system
```

### 2\. Create a Virtual Environment (Recommended)

This keeps your project dependencies organized:

```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on Mac/Linux:
source venv/bin/activate
```

### 3\. Install Dependencies

Install all required Python libraries:

```bash
pip install -r requirements.txt
```

### 4\. Download the NLP Model

The system uses the Spacy `en_core_web_sm` model for entity recognition and skill extraction. Download it by running:

```bash
python -m spacy download en_core_web_sm
```

-----

## 💻 How to Use

1.  **Launch the App:**
    Run the following command in your terminal:
    ```bash
    streamlit run app.py
    ```
2.  **Input Job Description:**
    In the sidebar, paste the Job Description (JD) of the role you are hiring for.
3.  **Upload Resumes:**
    Upload one or more resumes (PDF or DOCX). You can also click the **"Use Test Resume"** button to see how the system works with a sample profile.
4.  **Analyze Results:**
      * View the **Ranking Table** to see candidates sorted by their match score.
      * Check the **Comparison Chart** for a visual breakdown.
      * Expand the **Personalized Tips** section to see specific advice for each candidate.

-----

## 🛠️ Project Structure

  * `app.py`: The main entry point containing the Streamlit UI logic.
  * `parsing.py`: Contains NLP logic for extracting names, contact info, and skills.
  * `utils.py`: Helper functions for extracting text from PDF and DOCX files.
  * `requirements.txt`: List of all Python packages required to run the project.

-----

## 📦 Tech Stack

  * **Frontend:** [Streamlit](https://streamlit.io/)
  * **NLP:** [Spacy](https://spacy.io/)
  * **Text Processing:** Pdfminer.six, Docx2txt
  * **Data Science:** Pandas, Scikit-learn (CountVectorizer & Cosine Similarity)
  * **Visualization:** Altair

-----

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

-----

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

-----

**Tip:** If you face any issues during the installation of Spacy, ensure you have the latest version of `pip` by running `pip install --upgrade pip`.
