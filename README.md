# 🚀 GenMail Classifier

## 📌 Table of Contents
- [Introduction](#introduction)
- [Demo](#demo)
- [What It Does](#what-it-does)
- [How We Built It](#how-we-built-it)
- [Challenges We Faced](#challenges-we-faced)
- [How to Run](#how-to-run)
- [Tech Stack](#tech-stack)
- [Team](#team)

---

## 🎯 Introduction
**Problem Statement**
Commercial bank lending service teams handle a high volume of servicing requests via email, often with attachments. The current manual triage process involves reading emails, classifying requests, extracting key attributes, and assigning them to the appropriate teams. This approach is inefficient, time-consuming, and prone to errors, especially at scale.
**Approach**
To address this challenge, we propose an AI-driven solution leveraging Generative AI (LLMs) and Vector DB to automate email classification and data extraction. The system will intelligently classify requests, extract relevant banking attributes, and enable skill-based routing, improving efficiency, accuracy, and turnaround time while reducing manual intervention.


## 🎥 Demo

🔗 [Live Demo](#) (if applicable)  
📹 [Video Demo](https://github.com/ewfx/gaied-ai-innovators/blob/main/artifacts/demo/Email_Processing_System_Demo.mp4)
    [[Power-Point Presentation](https://github.com/ewfx/gaied-ai-innovators/blob/main/artifacts/arch/Email_Processing_System_Presentation.pptx)]

🖼️ Screenshots: 
    [[Architecture Flow PoC](https://github.com/ewfx/gaied-ai-innovators/blob/main/artifacts/arch/PoC-Flow-Diagram.jpg)]
    [[Architecture Target State](https://github.com/ewfx/gaied-ai-innovators/blob/main/artifacts/arch/High%20Level%20Solution%20Arch.jpg)] 

## ⚙️ What It Does
Email Extraction, Request & Sub Request Classification using LLM, Duplicate Service Request Identifier using Vector DB

## 🛠️ How We Built It
We used a backend python-based Django app which uses python libraries like pyPdf and Tesseract to extract content from email which are passed to the LLM for classification and checked for duplication in Vector DB.   

## 🚧 Challenges We Faced
LLM Identification, Finding OpenSource Vector DB which suits our use-case. 

## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaied-ai-innovators
   ```
2. Install dependencies  
   ```sh
   pip install -r requirements.txt (for Python)
   ```
3. Run the project (Get inside the folder EmailClassifierService 
   ```sh
   python manage.py runserver
   ```

## 🏗️ Tech Stack
- 🔹 Frontend: Angular
- 🔹 Backend: Django
- 🔹 Database: Qdrant Vector DB
- 🔹 Other: Gemini, Tesseract OCR
