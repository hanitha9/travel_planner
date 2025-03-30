# Travel Planner AI

## Overview
Travel Planner AI is an AI-powered web application built with Streamlit to assist users in creating personalized travel itineraries. It guides users through a conversational process to gather preferences, suggests activities using a simulated web-search tool, and generates a detailed day-by-day itinerary. This project was developed as part of an AI/ML Internship Assignment to prototype an AI-agentic system for travel planning.

## Features
- **Input Parsing:** Extracts key travel details (destination, dates, budget, interests, purpose) from free-form input.
- **Preference Refinement:** Clarifies dietary preferences, mobility tolerance, accommodation type, and specific interests.
- **Activity Suggestions:** Provides personalized activity recommendations using a mock web-search function.
- **Itinerary Generation:** Creates a structured n-day itinerary with timed slots (Morning, Afternoon, Evening).
- **Elegant UI:** Styled with classic blues and greys, featuring a travel-themed background.
- **Bonus Features:** Handles flexible and vague inputs with clarification prompts.

## Project Structure
```
travel-planner-ai/
├── app.py          # Main Streamlit application code
├── README.md       # Project documentation (this file)
└── requirements.txt # Dependencies for the project
```

## Prerequisites
- Python: 3.8 or higher
- Streamlit: For running and deploying the application
- Git: For version control and deployment
- Streamlit Community Cloud Account: For hosting the app

## Setup Instructions

### Local Installation
#### Clone the Repository:
```bash
git clone https://github.com/your-username/travel-planner-ai.git
cd travel-planner-ai
```

#### Create a Virtual Environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies:
Create a `requirements.txt` file with the following content:
```
streamlit==1.36.0
```
Then run:
```bash
pip install -r requirements.txt
```

#### Run the Application Locally:
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501` to view the app.

### Deployment on Streamlit Community Cloud
#### Push to GitHub:
Create a GitHub repository (e.g., travel-planner-ai).
Push the project files:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

#### Deploy via Streamlit Cloud:
- Log in to Streamlit Community Cloud.
- Click "New app" and connect your GitHub repository.
- Set the app file to `app.py`.
- Deploy the app and note the URL (e.g., `https://travel-planner-ai.streamlit.app`).

## Usage Guide
1. **Input Your Trip Details:**
   - On the homepage, enter details like "Bangkok from New York, Jun 1-4, 2025, budget, art and food" in the text area.
   - Click "Plan My Trip" to proceed.
2. **Refine Preferences:**
   - Review the parsed details and provide additional preferences (dietary, mobility, accommodation, specific interests).
   - Submit to move forward.
3. **Select Activities:**
   - Choose from suggested activities tailored to your interests (e.g., "Jim Thompson House", "Chinatown Street Food Tour").
   - Click "Generate Itinerary" to finalize.
4. **View Your Itinerary:**
   - See a detailed day-by-day plan with timed slots.
   - Option to "Plan Another Journey" resets the process.

## Deliverables

### Final Set of Prompts
#### Initial Parse
- **System Prompt:** "You are a travel planner AI. Extract the following from the user's input: Destination, Starting location, Travel dates or duration, Budget, Interests, Purpose. If any detail is missing or vague, ask clarifying questions."
- **User Prompt:** "User input: 'Bangkok from New York, Jun 1-4, 2025, budget, art and food'"
- **Model Response:** "From your input 'Bangkok from New York, Jun 1-4, 2025, budget, art and food', I’ve extracted: Destination: Bangkok, Starting Location: New York, Dates: Jun 1-4, 2025, Budget: Budget, Interests: art, food, Purpose: vacation. Please clarify any missing details (e.g., purpose, specific interests)."

#### Refine Preferences
- **System Prompt:** "You are a travel planner AI refining user preferences. Given the current preferences, ask the user to confirm or provide: Dietary preferences, Mobility tolerance, Accommodation type, Specific interests within their stated preferences."

#### Activity Suggestions
- **System Prompt:** "You are a travel planner AI. Using web-search results, suggest 3-5 activities for the destination based on the user’s interests."

#### Generate Itinerary
- **System Prompt:** "You are a travel planner AI. Create a detailed n-day itinerary for the user based on: Destination, Dates, Duration, Interests, Selected Activities, Budget, Dietary, Mobility, Accommodation preferences."

## Live Application
**Deployed URL:** [`https://travelplanner-7axnmyx9s9nrnpy9xaexsy.streamlit.app/`]

## Technologies Used
- **Python:** Core programming language (v3.8+).
- **Streamlit:** Web framework for building and deploying the app.
- **HTML/CSS:** Custom styling with blues and greys for an elegant UI.
- **Regex:** For parsing dates and text input.


## Future Enhancements
- Integrate a real web-search API (e.g., Google Places, TripAdvisor) for dynamic activity suggestions.
- Expand the destination database to cover more cities globally.
- Add cost estimation based on budget and activities.
- Implement user authentication to save itineraries.

## Contact
For questions or feedback, reach out to [hanitharajreswari9@gmail.com] or open an issue on GitHub.

