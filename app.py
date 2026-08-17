from flask import Flask, request, jsonify, render_template_string
from PyPDF2 import PdfReader
import re

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>ResumeAI - Resume Analyzer</title>

<style>

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, Helvetica, sans-serif;
    min-height: 100vh;
    color: white;
    background:
        radial-gradient(circle at 10% 10%, #312e81 0, transparent 30%),
        radial-gradient(circle at 90% 90%, #164e63 0, transparent 30%),
        #070b18;
}

nav {
    width: 90%;
    max-width: 1100px;
    margin: auto;
    padding: 25px 0;

    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 24px;
    font-weight: bold;
}

.logo span {
    display: inline-block;
    padding: 8px 12px;
    margin-right: 8px;
    border-radius: 10px;

    background: linear-gradient(135deg, #8b5cf6, #06b6d4);
}

nav a {
    color: #aaa;
    text-decoration: none;
    margin-left: 20px;
}

nav a:hover {
    color: white;
}

.hero {
    text-align: center;
    padding: 90px 20px 70px;
}

.badge {
    display: inline-block;
    padding: 10px 18px;
    margin-bottom: 25px;

    color: #c4b5fd;
    border: 1px solid #444;
    border-radius: 30px;
}

.hero h1 {
    font-size: clamp(45px, 7vw, 80px);
    line-height: 1.05;
    margin-bottom: 25px;
}

.gradient {
    color: transparent;
    background: linear-gradient(90deg, #a78bfa, #22d3ee);
    background-clip: text;
    -webkit-background-clip: text;
}

.hero p {
    max-width: 650px;
    margin: auto;

    color: #aab2c5;
    font-size: 18px;
    line-height: 1.7;
}

section {
    width: 90%;
    max-width: 1100px;
    margin: auto;
    padding: 60px 0;
}

.title {
    text-align: center;
    margin-bottom: 35px;
}

.title small {
    color: #a78bfa;
    letter-spacing: 3px;
}

.title h2 {
    font-size: 38px;
    margin: 12px 0;
}

.title p {
    color: #9ca3af;
}

.upload-box {
    max-width: 700px;
    margin: auto;
    padding: 30px;

    border: 1px solid #30374d;
    border-radius: 20px;

    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(15px);
}

.drop-zone {
    text-align: center;
    padding: 60px 20px;

    border: 2px dashed #555;
    border-radius: 18px;

    transition: 0.3s;
}

.drop-zone:hover,
.drop-zone.active {
    border-color: #22d3ee;
    background: rgba(34, 211, 238, 0.06);
}

.upload-icon {
    font-size: 55px;
    margin-bottom: 15px;
}

.drop-zone p {
    color: #999;
    margin: 12px 0 20px;
}

input[type="file"] {
    display: none;
}

.button {
    border: none;
    padding: 14px 25px;
    border-radius: 10px;

    color: white;
    font-weight: bold;
    cursor: pointer;

    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    transition: 0.3s;
}

.button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.3);
}

.button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

#fileName {
    color: #67e8f9;
    margin-top: 20px;
}

.analyze {
    width: 100%;
    margin-top: 20px;
    font-size: 16px;
}

#results {
    display: none;
}

.cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.card {
    padding: 30px;

    border: 1px solid #30374d;
    border-radius: 20px;

    background: rgba(255, 255, 255, 0.06);
}

.score-card {
    text-align: center;
}

.score-circle {
    width: 170px;
    height: 170px;
    margin: auto auto 20px;

    border-radius: 50%;

    display: flex;
    justify-content: center;
    align-items: center;

    background:
        radial-gradient(circle, #0b1020 58%, transparent 60%),
        conic-gradient(#8b5cf6, #22d3ee, #8b5cf6);
}

.score {
    font-size: 45px;
    font-weight: bold;
}

.muted {
    color: #9ca3af;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    align-items: center;
    text-align: center;
    gap: 15px;
}

.stat-number {
    display: block;
    font-size: 35px;
    font-weight: bold;
    color: #a78bfa;
    margin-bottom: 8px;
}

.skill-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.skill {
    padding: 8px 14px;
    border-radius: 30px;

    color: #86efac;
    border: 1px solid #166534;
    background: rgba(34, 197, 94, 0.1);
}

.section-row {
    display: flex;
    justify-content: space-between;

    padding: 11px;
    margin-bottom: 8px;

    border-radius: 8px;
    background: rgba(255, 255, 255, 0.04);
}

.present {
    color: #4ade80;
}

.missing {
    color: #fb7185;
}

.suggestions {
    grid-column: span 2;
}

.suggestions li {
    margin: 12px 0;
    color: #c1c8d5;
}

.features {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
}

.feature {
    padding: 25px;

    border: 1px solid #30374d;
    border-radius: 18px;

    background: rgba(255, 255, 255, 0.05);

    transition: 0.3s;
}

.feature:hover {
    transform: translateY(-7px);
    border-color: #7c3aed;
}

.feature-icon {
    font-size: 35px;
    margin-bottom: 15px;
}

.feature p {
    color: #9ca3af;
    line-height: 1.5;
    margin-top: 10px;
}

footer {
    text-align: center;
    color: #71798c;
    padding: 30px;
    border-top: 1px solid #202638;
}

@media (max-width: 800px) {

    .cards {
        grid-template-columns: 1fr;
    }

    .suggestions {
        grid-column: span 1;
    }

    .features {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 500px) {

    .features {
        grid-template-columns: 1fr;
    }

    .stats {
        grid-template-columns: 1fr;
        gap: 25px;
    }

    nav a {
        display: none;
    }
}

</style>
</head>

<body>

<nav>

    <div class="logo">
        <span>R</span>
        ResumeAI
    </div>

    <div>
        <a href="#analyzer">Analyzer</a>
        <a href="#features">Features</a>
    </div>

</nav>

<div class="hero">

    <div class="badge">
        ✨ Smart Resume Analyzer
    </div>

    <h1>
        Make Your Resume
        <br>
        <span class="gradient">Stand Out.</span>
    </h1>

    <p>
        Upload your resume and get an instant analysis
        of your skills, important sections and
        improvement suggestions.
    </p>

</div>

<section id="analyzer">

    <div class="title">

        <small>RESUME ANALYZER</small>

        <h2>Analyze Your Resume</h2>

        <p>
            Upload your resume as a PDF.
        </p>

    </div>

    <div class="upload-box">

        <div id="dropZone" class="drop-zone">

            <div class="upload-icon">📄</div>

            <h3>Drop your resume here</h3>

            <p>or select a PDF file</p>

            <input
                type="file"
                id="resume"
                accept=".pdf"
            >

            <button
                class="button"
                id="chooseButton"
            >
                Choose PDF
            </button>

            <div id="fileName"></div>

        </div>

        <button
            id="analyze"
            class="button analyze"
        >
            Analyze Resume
        </button>

    </div>

</section>

<section id="results">

    <div class="title">

        <small>RESULTS</small>

        <h2>Resume Analysis</h2>

    </div>

    <div class="cards">

        <div class="card score-card">

            <div class="score-circle">

                <div>

                    <span id="score" class="score">0</span>
                    <span>/100</span>

                </div>

            </div>

            <h3 id="rating">Resume Score</h3>

            <p class="muted">
                Overall quality
            </p>

        </div>

        <div class="card stats">

            <div>
                <span id="skillCount" class="stat-number">0</span>
                <span class="muted">Skills</span>
            </div>

            <div>
                <span id="sectionCount" class="stat-number">0</span>
                <span class="muted">Sections</span>
            </div>

            <div>
                <span id="suggestionCount" class="stat-number">0</span>
                <span class="muted">Suggestions</span>
            </div>

        </div>

        <div class="card">

            <h3>🛠 Skills Detected</h3>

            <br>

            <div id="skills" class="skill-list"></div>

        </div>

        <div class="card">

            <h3>📋 Resume Sections</h3>

            <br>

            <div id="sections"></div>

        </div>

        <div class="card suggestions">

            <h3>💡 Suggestions</h3>

            <br>

            <ul id="suggestions"></ul>

        </div>

    </div>

</section>

<section id="features">

    <div class="title">

        <small>FEATURES</small>

        <h2>What We Analyze</h2>

    </div>

    <div class="features">

        <div class="feature">

            <div class="feature-icon">🎯</div>

            <h3>Resume Score</h3>

            <p>
                Calculate a resume quality score.
            </p>

        </div>

        <div class="feature">

            <div class="feature-icon">🧠</div>

            <h3>Skill Detection</h3>

            <p>
                Detect technical skills in your resume.
            </p>

        </div>

        <div class="feature">

            <div class="feature-icon">📊</div>

            <h3>Section Analysis</h3>

            <p>
                Check important resume sections.
            </p>

        </div>

        <div class="feature">

            <div class="feature-icon">💡</div>

            <h3>Suggestions</h3>

            <p>
                Find areas where your resume can improve.
            </p>

        </div>

    </div>

</section>

<footer>
    ResumeAI © 2026
</footer>

<script>

const resumeInput = document.getElementById("resume");
const fileName = document.getElementById("fileName");
const chooseButton = document.getElementById("chooseButton");
const analyzeButton = document.getElementById("analyze");
const dropZone = document.getElementById("dropZone");

chooseButton.addEventListener("click", function () {
    resumeInput.click();
});

resumeInput.addEventListener("change", function () {

    if (this.files.length > 0) {

        fileName.textContent =
            "Selected: " + this.files[0].name;
    }
});

dropZone.addEventListener("dragover", function (event) {

    event.preventDefault();

    dropZone.classList.add("active");
});

dropZone.addEventListener("dragleave", function () {

    dropZone.classList.remove("active");
});

dropZone.addEventListener("drop", function (event) {

    event.preventDefault();

    dropZone.classList.remove("active");

    if (event.dataTransfer.files.length > 0) {

        resumeInput.files = event.dataTransfer.files;

        fileName.textContent =
            "Selected: " +
            event.dataTransfer.files[0].name;
    }
});

analyzeButton.addEventListener("click", async function () {

    if (!resumeInput.files.length) {

        alert("Please select a PDF resume.");

        return;
    }

    const file = resumeInput.files[0];

    if (!file.name.toLowerCase().endsWith(".pdf")) {

        alert("Only PDF files are supported.");

        return;
    }

    const formData = new FormData();

    formData.append("resume", file);

    analyzeButton.textContent = "Analyzing...";
    analyzeButton.disabled = true;

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.error || "Analysis failed."
            );
        }

        showResults(data);

    } catch (error) {

        alert(error.message);

    } finally {

        analyzeButton.textContent = "Analyze Resume";
        analyzeButton.disabled = false;
    }
});

function showResults(data) {

    document.getElementById("results").style.display = "block";

    document.getElementById("score").textContent =
        data.score;

    document.getElementById("rating").textContent =
        data.rating;

    document.getElementById("skillCount").textContent =
        data.skills.length;

    const sectionCount =
        Object.values(data.sections).filter(Boolean).length;

    document.getElementById("sectionCount").textContent =
        sectionCount;

    document.getElementById("suggestionCount").textContent =
        data.suggestions.length;

    const skillsContainer =
        document.getElementById("skills");

    skillsContainer.innerHTML = "";

    if (data.skills.length === 0) {

        skillsContainer.innerHTML =
            '<span class="muted">No skills detected.</span>';

    } else {

        data.skills.forEach(function (skill) {

            const span = document.createElement("span");

            span.className = "skill";

            span.textContent = skill;

            skillsContainer.appendChild(span);
        });
    }

    const sectionNames = {

        email: "Email",
        phone: "Phone",
        education: "Education",
        experience: "Experience",
        projects: "Projects",
        certifications: "Certifications",
        summary: "Professional Summary"
    };

    const sectionsContainer =
        document.getElementById("sections");

    sectionsContainer.innerHTML = "";

    Object.entries(data.sections).forEach(function ([key, value]) {

        const row = document.createElement("div");

        row.className = "section-row";

        const name = document.createElement("span");

        name.textContent = sectionNames[key];

        const status = document.createElement("span");

        status.textContent =
            value ? "✓ Present" : "✗ Missing";

        status.className =
            value ? "present" : "missing";

        row.appendChild(name);
        row.appendChild(status);

        sectionsContainer.appendChild(row);
    });

    const suggestionsContainer =
        document.getElementById("suggestions");

    suggestionsContainer.innerHTML = "";

    if (data.suggestions.length === 0) {

        suggestionsContainer.innerHTML =
            "<li>Your resume looks good!</li>";

    } else {

        data.suggestions.forEach(function (item) {

            const li = document.createElement("li");

            li.textContent = item;

            suggestionsContainer.appendChild(li);
        });
    }

    document.getElementById("results").scrollIntoView({
        behavior: "smooth"
    });
}

</script>

</body>
</html>
"""


def extract_text(file):
    reader = PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def analyze_resume(text):

    text_lower = text.lower()

    skills = [
        "python",
        "java",
        "javascript",
        "html",
        "css",
        "react",
        "node.js",
        "flask",
        "django",
        "sql",
        "mysql",
        "mongodb",
        "git",
        "github",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "linux",
        "c",
        "c++",
        "machine learning",
        "data science",
        "tensorflow",
        "pandas",
        "numpy",
        "devops",
        "jenkins",
        "terraform"
    ]

    found_skills = []

    for skill in skills:

        if skill.lower() in text_lower:
            found_skills.append(skill)

    sections = {

        "email": bool(
            re.search(
                r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                text
            )
        ),

        "phone": bool(
            re.search(
                r"\+?\d[\d\s\-()]{8,}\d",
                text
            )
        ),

        "education": any(
            word in text_lower
            for word in [
                "education",
                "university",
                "college",
                "degree",
                "b.tech",
                "bachelor"
            ]
        ),

        "experience": any(
            word in text_lower
            for word in [
                "experience",
                "work experience",
                "employment",
                "internship"
            ]
        ),

        "projects": "projects" in text_lower,

        "certifications": any(
            word in text_lower
            for word in [
                "certification",
                "certifications",
                "certificate"
            ]
        ),

        "summary": any(
            word in text_lower
            for word in [
                "summary",
                "objective",
                "profile"
            ]
        )
    }

    score = 0

    if sections["email"]:
        score += 10

    if sections["phone"]:
        score += 10

    for section in [
        "education",
        "experience",
        "projects",
        "certifications",
        "summary"
    ]:

        if sections[section]:
            score += 10

    score += min(len(found_skills) * 3, 35)

    score = min(score, 100)

    if score >= 80:
        rating = "Excellent"
    elif score >= 60:
        rating = "Good"
    elif score >= 40:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    suggestions = []

    if not sections["email"]:
        suggestions.append(
            "Add a professional email address."
        )

    if not sections["phone"]:
        suggestions.append(
            "Add a contact phone number."
        )

    if not sections["summary"]:
        suggestions.append(
            "Add a professional summary."
        )

    if not sections["experience"]:
        suggestions.append(
            "Add work experience or internship experience."
        )

    if not sections["projects"]:
        suggestions.append(
            "Add relevant projects with technologies used."
        )

    if not sections["education"]:
        suggestions.append(
            "Add your education details."
        )

    if len(found_skills) < 5:
        suggestions.append(
            "Add more relevant technical skills."
        )

    if not sections["certifications"]:
        suggestions.append(
            "Consider adding relevant certifications."
        )

    return {
        "score": score,
        "rating": rating,
        "skills": found_skills,
        "sections": sections,
        "suggestions": suggestions
    }


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/analyze", methods=["POST"])
def analyze():

    if "resume" not in request.files:

        return jsonify({
            "error": "No resume uploaded."
        }), 400

    file = request.files["resume"]

    if file.filename == "":

        return jsonify({
            "error": "Please select a resume."
        }), 400

    if not file.filename.lower().endswith(".pdf"):

        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    try:

        text = extract_text(file)

        if not text.strip():

            return jsonify({
                "error":
                "Could not extract text from this PDF."
            }), 400

        result = analyze_resume(text)

        return jsonify(result)

    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
