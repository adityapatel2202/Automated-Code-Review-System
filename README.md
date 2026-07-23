# Automated Code Review System

An automated code quality assessment and refactoring assistant. This platform evaluates uploaded Python code using static analysis, deep learning-based semantic evaluation, machine learning classifiers, and generative refactoring.

---

## 🚀 Key Features

*   **Static Analysis Engine:** Uses Python's Abstract Syntax Trees (AST) and Pylint to count syntax structures and flag code errors.
*   **Rule-Based Scoring:** Calculates a dynamic 100-point code quality score applying custom deductions based on linting severities.
*   **Deep Learning Semantic Analyzer:** Embeds code strings using **CodeBERT** (`microsoft/codebert-base`) to calculate semantic similarity scores.
*   **Machine Learning Predictor:** Predicts code quality labels (*Excellent, Good, Average, Poor*) using a **Random Forest Classifier** trained on CodeSearchNet features.
*   **AI Code Refactoring Assistant:** Generates three compiler-ready versions of the code (Clean, Best Practices, and Optimized) using **Qwen2.5-Coder-0.5B-Instruct**.
*   **Interactive Review Dashboard:** Rich user dashboard with summary statistics, past submission history tables, and interactive **Chart.js** code quality trend graphs.
*   **Downloadable HTML Reports:** Generates structured, print-friendly reports for offline sharing.

---

## 🛠️ Tech Stack

*   **Backend:** Flask 3.1.3, SQLAlchemy, SQLite (Development), PostgreSQL (Production)
*   **Frontend:** HTML5, CSS3, Bootstrap 5.3, PrismJS, Chart.js
*   **Machine Learning:** scikit-learn, Pandas, Joblib, Numpy
*   **Deep Learning / AI:** HuggingFace Transformers, PyTorch, Tokenizers

---

## 📂 Project Structure

```text
Automated-Code-Review-System/
├── app/
│   ├── ai/                    # CodeT5/Qwen generation models & prompts
│   ├── analysis/              # AST, Pylint analyzers & score calculators
│   ├── auth/                  # Authentication blueprints & registration
│   ├── dashboard/             # Main history dashboard logic
│   ├── ml/                    # Feature engineering & Random Forest training
│   ├── models/                # SQLAlchemy database models (User, Review)
│   ├── prediction/            # API routes for ML predictions
│   ├── reports/               # HTML report exporters & download routes
│   ├── semantic/              # CodeBERT semantic analysis & embeddings
│   ├── static/                # CSS grids & Chart.js JS scripts
│   ├── templates/             # Jinja2 HTML layouts & result blocks
│   └── upload/                # Python file upload blueprints
├── config.py                  # Environment config Loader
├── run.py                     # App entry point
├── requirements.txt           # Dependency requirements list
├── Dockerfile                 # Container image builder
└── .dockerignore              # Docker context ignore list
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/adityapatel2202/Automated-Code-Review-System.git
cd Automated-Code-Review-System
```

### 2. Set up virtual environment
```bash
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the Random Forest Classifier
To train the classifier on the CodeSearchNet python features:
```bash
python app/ml/train_random_forest.py
```

### 5. Launch the Flask App
```bash
python run.py
```
Open `http://127.0.0.1:5000` in your web browser.

---

## 🐳 Docker & AWS Deployment

### 1. Build and Run Container Locally
```bash
# Build
docker build -t automated-code-reviewer .

# Run
docker run -p 5000:5000 -e SECRET_KEY="test" automated-code-reviewer
```

### 2. Deploy on AWS EC2 & RDS
*   **EC2 Instance:** Deploy on at least a **`t3.medium` (4GB RAM)**.
*   **RDS Database:** Configure PostgreSQL and inject the connection string via the `DATABASE_URL` environment variable:
```bash
docker run -d -p 80:5000 \
  -e DATABASE_URL="postgresql://<user>:<password>@<rds-endpoint>:5432/<dbname>" \
  -e SECRET_KEY="your-secure-secret-key" \
  <aws-account-id>.dkr.ecr.<region>.amazonaws.com/automated-code-reviewer:latest
```
