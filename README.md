<h1 align="center">📝 Sentiment Analysis Platform</h1>

<p align="center">
  <b>A Hybrid Sentiment & Aspect-Based Analysis System using Machine Learning and BERT</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/ML-Logistic%20Regression-blue" />
  <img src="https://img.shields.io/badge/Deep%20Learning-BERT-yellow" />
  <img src="https://img.shields.io/badge/Backend-Django-green" />
  <img src="https://img.shields.io/badge/Frontend-HTML%2FCSS%2FBootstrap-orange" />
</p>

---

## 🚀 Project Overview

The **Sentiment Analysis Platform** is designed to analyze product reviews from e-commerce websites.  
It determines **customer sentiment (positive/negative)** and performs **aspect-based analysis** (e.g., battery, price, delivery).  
The system integrates **Machine Learning (TF-IDF + Logistic Regression)** and **Deep Learning (BERT)** models within a Django web application.

---

## 🧩 Features

<ul>
  <li><b>Sentiment Prediction:</b> Detects whether a review is positive or negative.</li>
  <li><b>Aspect-Based Analysis:</b> Extracts product-specific aspects like <i>battery</i>, <i>camera</i>, <i>price</i>, etc.</li>
  <li><b>Hybrid System:</b> Combines rule-based heuristics, classical ML, and BERT for accurate sentiment analysis.</li>
  <li><b>User Interface:</b> Simple and interactive web dashboard for real-time analysis.</li>
  <li><b>Smart Preprocessing:</b> Cleans text by removing noise, punctuation, and stopwords for better predictions.</li>
</ul>

---

## 🧠 Methodology

<ol>
  <li><b>Data Processing:</b> Imported datasets (Amazon, IMDB, Yelp) and cleaned text data.</li>
  <li><b>Feature Extraction:</b> Used TF-IDF for vectorization of reviews.</li>
  <li><b>Model Training:</b>
    <ul>
      <li><b>Classical Model:</b> Logistic Regression using TF-IDF features.</li>
      <li><b>Deep Model:</b> BERT for contextual understanding of reviews.</li>
    </ul>
  </li>
  <li><b>Evaluation:</b> Measured accuracy and performance on test data.</li>
  <li><b>Deployment:</b> Integrated both models into a Django backend for real-time analysis.</li>
</ol>

---

## ⚙️ Tech Stack

<table>
  <thead>
    <tr>
      <th>Layer</th>
      <th>Technologies</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Frontend</td>
      <td>HTML, CSS, Bootstrap</td>
    </tr>
    <tr>
      <td>Backend</td>
      <td>Python, Django</td>
    </tr>
    <tr>
      <td>Machine Learning</td>
      <td>scikit-learn, spaCy, Transformers (BERT)</td>
    </tr>
    <tr>
      <td>Storage</td>
      <td>joblib (for ML model persistence)</td>
    </tr>
    <tr>
      <td>Tools</td>
      <td>VS Code, Git, Pip, virtualenv</td>
    </tr>
  </tbody>
</table>

---

## 📊 Model Flow

<ol>
  <li>User enters a product review on the UI.</li>
  <li>Text goes through preprocessing (cleaning, tokenization, stopword removal).</li>
  <li>ML/BERT model predicts sentiment (positive/negative).</li>
  <li>Aspect keywords (e.g., "battery", "delivery") are identified.</li>
  <li>Django backend displays the final sentiment and aspect results.</li>
</ol>

---

## 🖼️ System Architecture

<div align="center">
  <img src="https://via.placeholder.com/700x400.png?text=System+Architecture+Diagram" alt="System Architecture Diagram" />
  <p><i>Frontend ↔ Backend ↔ Model Engine (ML + BERT)</i></p>
</div>

---

## ✅ Results

<ul>
  <li>📈 Achieved <b>80–85% accuracy</b> using TF-IDF + Logistic Regression.</li>
  <li>🧠 BERT improved contextual understanding for ambiguous reviews.</li>
  <li>⚡ Real-time sentiment and aspect detection through Django integration.</li>
</ul>

---

## 💡 Future Improvements

<ul>
  <li>🔁 Add feedback-based learning to continuously improve the model.</li>
  <li>🛍️ Expand datasets to cover more product categories.</li>
  <li>☁️ Deploy on cloud (AWS / Render) for public access.</li>
</ul>

---

## 📌 How to Run Locally

```bash
# Clone the repository
git clone https://github.com/your-username/sentiment-analysis-platform.git
cd sentiment-analysis-platform

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate     # (Linux/Mac)
venv\Scripts\activate        # (Windows)

# Install dependencies
pip install -r requirements.txt

# Run Django server
python manage.py runserver
