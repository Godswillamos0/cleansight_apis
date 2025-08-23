# CleanSight

CleanSight is an AI-powered application that encourages environmental cleanliness by allowing users to capture **before-and-after images** of cleaned areas.  
The system verifies location, detects waste, calculates a cleanliness score, and rewards users with tokens.  

This repository contains the backend APIs, computer vision models, and web templates for the project.

## 📂 Project Structure


cleansight_apis/
 │── app/
 │ ├── cv_model/ # Computer vision models (.pt + utilities)
 │ ├── routers/ # API routes/endpoints
 │ ├── weights/ # Pre-trained model weights
 │ ├── data.db # POSTGRESQL database
 │ ├── main.py # Application entry point
 │ ├── models.py # Database models/schema
 │ ├── requirements.txt # Python dependencies
 │
 │── templates/
 │ ├── badge.html # User reward badge page
 │ ├── index.html # Home/landing page
 │ ├── login.html # Login page
 │ ├── signup.html # Signup page
 │ ├── verify.html # Location/image verification page
 │
 │── requirements.txt # Global project dependencies

## ⚙️ Setup Instructions

Follow these steps to recreate the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/cleansight_apis.git
cd cleansight_apis

2. Create and Activate a Virtual Environment
python -m venv venv
# Activate
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

3. Install Dependencies
Install the required Python packages:
pip install -r requirements.txt

4. Database Setup
The project uses POSTGRESQL as the default database.
 The database file data.db is already included inside the app/ folder.
 If you want to reset it:
rm app/data.db   # (optional - only if you want a fresh start)

Then run migrations (if defined in models.py) or reinitialize as needed.
5. Running the Application
Navigate to the app folder and start the application:
cd app
uvicorn main:app --reload

The API will now be running at:
 https://amosgodswill00-cleansightapp.hf.space
6. Accessing the Web Templates
The templates/ folder provides frontend pages rendered by the backend via FastAPI.
Home Page → /


Login Page → /login


Signup Page → /signup


Verification Page → /verify


Badge Page → /badge


AI Workflow
Upload before-and-after images


Location Verification – confirms images were captured at the target site.


Waste Detection – AI model identifies cleaned waste regions.


Cleanliness Score Calculation – (Pre - Post) / Pre formula.


Reward System – users receive tokens + digital badge (via badge.html).


Continuous Learning – user images are stored, labeled, and used to retrain models.


Deployment
For cloud deployment (e.g., AWS or Render):
Push repo to GitHub


Use services like Render


Configure environment variables for production


Run with:

 uvicorn main:app --host 0.0.0.0 --port 8000
Requirements
Python 3.9+


FastAPI


Uvicorn


POSTGRESQL


.pt


Other dependencies listed in requirements.txt


Contributors
Team members / collaborators: Nunsi Shiaki, Godswill Amos, Oluwaferanmi Oladepo, Ayomipo Agbaje, Abisoye Durojaiye 
License
This project is licensed under the MIT License – see the LICENSE file for details.
