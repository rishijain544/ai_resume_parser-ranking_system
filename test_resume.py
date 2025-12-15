from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def create_dummy_resume(filename):
    c = canvas.Canvas(filename, pagesize=LETTER)

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "JOHN DOE")
    c.setFont("Helvetica", 10)
    # Changed contact info for better parsing test
    c.drawString(50, 735, "Software Engineer | johndoe@example.com | +91 9876543210")

    # Profile
    c.drawString(50, 700, "PROFESSIONAL SUMMARY")
    c.line(50, 695, 250, 695)
    c.setFont("Helvetica", 10)
    c.drawString(50, 680, "Passionate Java Developer with 3 years of experience in building scalable web apps.")
    c.drawString(50, 665, "Expert in backend technologies and cloud deployment.")

    # Skills
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 630, "SKILLS")
    c.line(50, 625, 250, 625)
    c.setFont("Helvetica", 10)
    c.drawString(50, 610, "Core: Python, Java, SQL, C++")
    c.drawString(50, 595, "Frameworks: React, Django, Flask")
    c.drawString(50, 580, "Tools: Docker, Kubernetes, AWS, Git")

    # Education
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 550, "EDUCATION")
    c.line(50, 545, 250, 545)
    c.setFont("Helvetica", 10)
    c.drawString(50, 530, "B.Tech in Computer Science | Delhi University (2018-2022)")

    c.save()
    print(f"✅ Success! Test Resume created: {filename}")

if __name__ == "__main__":
    create_dummy_resume("Sample_Resume_Java_Dev.pdf")