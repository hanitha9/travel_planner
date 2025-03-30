import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Custom CSS for elegant styling with blues and greys
st.markdown("""
    <style>
    .input-page {
        background-image: url('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTXRAy6k-QSMzI7SJaqUt7amfFHOprsraWSw&s');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
    }
    .main-container {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 15px;
        padding: 30px;
        margin: 40px auto;
        max-width: 800px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid #E1E8ED;
    }
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 700;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 15px;
    }
    .sub-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        color: #4A6B8A;
        text-align: center;
        margin-bottom: 30px;
    }
    .section-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 26px;
        color: #2C3E50;
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 2px solid #E1E8ED;
    }
    .stTextArea textarea {
        font-family: 'Open Sans', sans-serif;
        font-size: 16px;
        color: #34495E;
        background-color: #F8FAFC;
        border: 2px solid #D6E0EA;
        border-radius: 8px;
    }
    .stButton button {
        font-family: 'Montserrat', sans-serif;
        background-color: #3498DB;
        color: white;
        border-radius: 8px;
        padding: 12px 28px;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #2980B9;
    }
    .day-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #3498DB;
    }
    .day-header {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        color: #2C3E50;
        font-weight: 600;
    }
    .activity-item {
        font-family: 'Open Sans', sans-serif;
        font-size: 16px;
        color: #34495E;
        margin: 12px 0;
    }
    .summary-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        margin-top: 25px;
        border: 1px solid #E1E8ED;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "input_refinement"
if "preferences" not in st.session_state:
    st.session_state.preferences = {}
if "activities" not in st.session_state:
    st.session_state.activities = []
if "saved" not in st.session_state:
    st.session_state.saved = False

# Simulated web-search function (mocking real-time data retrieval)
def web_search_activities(destination, interest):
    # Mock database (expandable with real API in production)
    MOCK_DATA = {
        "Bangkok": {
            "art": ["Jim Thompson House", "Bangkok Art & Culture Centre", "MOCA Bangkok"],
            "food": ["Chinatown Street Food Tour", "Floating Market Dining", "Chatuchak Market"],
            "culture": ["Grand Palace", "Wat Arun", "Thai Cooking Class"]
        },
        "Paris": {
            "art": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou"],
            "food": ["Le Marais Food Tour", "Seine River Dinner", "Montmartre Cafés"],
            "culture": ["Notre-Dame", "Latin Quarter Walk", "Père Lachaise"]
        }
    }
    # Simulate web search with randomization for freshness
    base_activities = MOCK_DATA.get(destination, {}).get(interest, [f"{interest.capitalize()} in {destination}"])
    return random.sample(base_activities + [f"Explore {interest} at {destination}"], min(3, len(base_activities) + 1))

# AI Prompt System
def ai_prompt_handler(prompt_type, user_input=None, prefs=None):
    if prompt_type == "initial_parse":
        system_prompt = """
        You are a travel planner AI. Extract the following from the user's input:
        - Destination
        - Starting location
        - Travel dates or duration
        - Budget (luxury, moderate, budget)
        - Interests (e.g., art, food, culture)
        - Purpose (e.g., vacation, business)
        If any detail is missing or vague, ask clarifying questions.
        """
        user_prompt = f"User input: '{user_input}'"
        response = f"""
        From your input '{user_input}', I’ve extracted:
        - Destination: {prefs.get('destination', 'Not specified')}
        - Starting Location: {prefs.get('start', 'Not specified')}
        - Dates: {prefs.get('dates', 'Not specified')}
        - Budget: {prefs.get('budget', 'moderate').capitalize()}
        - Interests: {', '.join(prefs.get('interests', ['culture']))}
        - Purpose: {prefs.get('purpose', 'Not specified')}
        Please clarify any missing details (e.g., purpose, specific interests).
        """
        return system_prompt, user_prompt, response

    elif prompt_type == "refine_preferences":
        system_prompt = """
        You are a travel planner AI refining user preferences. Given the current preferences,
        ask the user to confirm or provide:
        - Dietary preferences (e.g., none, vegetarian, vegan)
        - Mobility tolerance (miles/day)
        - Accommodation type (budget, mid-range, luxury)
        - Specific interests within their stated preferences
        Provide options and context to guide their response.
        """
        user_prompt = f"Current preferences: {prefs}"
        response = f"""
        Let’s refine your trip to {prefs['destination']}:
        - Dietary preferences: What are your needs? (None, Vegetarian, Vegan)
        - Mobility: How far can you walk daily? (1-10 miles)
        - Accommodation: Budget, Mid-range, or Luxury?
        - Interests: You mentioned {', '.join(prefs['interests'])}. Any specific activities (e.g., museums for art, street food for food)?
        """
        return system_prompt, user_prompt, response

    elif prompt_type == "activity_suggestions":
        system_prompt = """
        You are a travel planner AI. Using web-search results, suggest 3-5 activities for the
        destination based on the user’s interests. Ensure suggestions are personalized and
        include a mix of famous and offbeat options if requested. Present them clearly.
        """
        user_prompt = f"Destination: {prefs['destination']}, Interests: {prefs['interests']}"
        activities = [web_search_activities(prefs['destination'], interest) for interest in prefs['interests']]
        flat_activities = list(set([item for sublist in activities for item in sublist]))
        response = f"Here are some activity suggestions for {prefs['destination']}:\n" + "\n".join([f"- {act}" for act in flat_activities[:5]])
        return system_prompt, user_prompt, response

    elif prompt_type == "generate_itinerary":
        system_prompt = """
        You are a travel planner AI. Create a detailed n-day itinerary for the user based on:
        - Destination: {prefs['destination']}
        - Dates: {prefs['dates']}
        - Duration: {prefs['duration']} days
        - Interests: {prefs['interests']}
        - Selected Activities: {st.session_state.activities}
        - Budget, Dietary, Mobility, Accommodation preferences
        Structure it with Morning, Afternoon, Evening slots, including meals and rest.
        """
        user_prompt = f"Generate an itinerary for {prefs['destination']} from {prefs['start']}."
        response = "Itinerary generated below."  # Actual generation happens in UI
        return system_prompt, user_prompt, response

# Parse initial input
def parse_initial_input(user_input):
    prefs = {}
    text_lower = user_input.lower()
    
    for city in ["Bangkok", "Paris", "Tokyo"]:  # Simplified for demo
        if city.lower() in text_lower:
            prefs["destination"] = city
            break
    if "destination" not in prefs:
        prefs["destination"] = "Paris"
    
    date_info = parse_dates(text_lower)
    prefs.update(date_info)
    
    if "luxury" in text_lower:
        prefs["budget"] = "luxury"
    elif "budget" in text_lower or "cheap" in text_lower:
        prefs["budget"] = "budget"
    else:
        prefs["budget"] = "moderate"
    
    interests = ["art", "food", "culture", "history"]
    prefs["interests"] = [i for i in interests if i in text_lower] or ["culture"]
    
    origin_match = re.search(r"(from|flying from)\s+([a-zA-Z\s]+)", text_lower)
    prefs["start"] = origin_match.group(2).strip().title() if origin_match else "Not specified"
    
    purpose_match = re.search(r"(vacation|business|family|adventure trip)", text_lower)
    prefs["purpose"] = purpose_match.group(0) if purpose_match else "vacation"
    
    return prefs

def parse_dates(text):
    today = datetime.now()
    month_range = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s*[-–]\s*(\d{1,2}),?\s+(\d{4})", text.lower())
    if month_range:
        month = month_range.group(1)[:3].title()
        start_day = int(month_range.group(2))
        end_day = int(month_range.group(3))
        year = int(month_range.group(4))
        start_date = datetime.strptime(f"{month} {start_day} {year}", "%b %d %Y")
        end_date = datetime.strptime(f"{month} {end_day} {year}", "%b %d %Y")
        duration = (end_date - start_date).days + 1
        return {"dates": f"{month} {start_day}-{end_day}, {year}", "duration": duration, "start_date": start_date, "end_date": end_date}
    end_date = today + timedelta(days=6)
    return {"dates": f"{today.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}", "duration": 7, "start_date": today, "end_date": end_date}

# Main App
def main():
    if st.session_state.stage == "input_refinement":
        st.markdown('<div class="input-page"></div>', unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            st.markdown("<div class='main-title'>Travel Planner</div>", unsafe_allow_html=True)
            st.markdown("<div class='sub-title'>Plan your perfect journey with AI assistance</div>", unsafe_allow_html=True)
            
            with st.form("trip_input"):
                user_input = st.text_area("Describe your trip (e.g., destination, dates, budget, interests):", "Bangkok from New York, Jun 1-4, 2025, budget, art and food")
                if st.form_submit_button("Plan My Trip"):
                    prefs = parse_initial_input(user_input)
                    st.session_state.preferences = prefs
                    sys_prompt, usr_prompt, response = ai_prompt_handler("initial_parse", user_input, prefs)
                    st.write(response)
                    st.session_state.stage = "refine_preferences"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "refine_preferences":
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            st.markdown("<div class='section-title'>Refine Your Preferences</div>", unsafe_allow_html=True)
            prefs = st.session_state.preferences
            sys_prompt, usr_prompt, response = ai_prompt_handler("refine_preferences", prefs=prefs)
            st.write(response)
            
            with st.form("preference_refinement"):
                dietary = st.selectbox("Dietary Preference:", ["None", "Vegetarian", "Vegan"])
                mobility = st.slider("Walking Tolerance (miles/day):", 1, 10, 5)
                accommodation = st.selectbox("Accommodation Preference:", ["Budget", "Mid-range", "Luxury"])
                specific_interests = st.text_input("Specific interests (e.g., museums, street food):", ", ".join(prefs["interests"]))
                
                if st.form_submit_button("Confirm Preferences"):
                    prefs.update({
                        "dietary": dietary.lower(),
                        "mobility": mobility,
                        "accommodation": accommodation.lower(),
                        "interests": specific_interests.split(", ")
                    })
                    st.session_state.preferences = prefs
                    st.session_state.stage = "activity_suggestions"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "activity_suggestions":
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            prefs = st.session_state.preferences
            st.markdown(f"<div class='section-title'>Activity Suggestions for {prefs['destination']}</div>", unsafe_allow_html=True)
            sys_prompt, usr_prompt, response = ai_prompt_handler("activity_suggestions", prefs=prefs)
            st.write(response)
            
            suggestions = [item for sublist in [web_search_activities(prefs['destination'], i) for i in prefs['interests']] for item in sublist]
            with st.form("activity_selection"):
                selected_activities = st.multiselect("Choose activities:", suggestions, default=suggestions[:3])
                if st.form_submit_button("Generate Itinerary"):
                    st.session_state.activities = selected_activities
                    st.session_state.stage = "itinerary_display"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.stage == "itinerary_display":
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            prefs = st.session_state.preferences
            sys_prompt, usr_prompt, response = ai_prompt_handler("generate_itinerary", prefs=prefs)
            st.markdown(f"<div class='section-title'>Your {prefs['duration']}-Day Journey to {prefs['destination']}</div>", unsafe_allow_html=True)
            st.write(f"Dates: {prefs['dates']}")
            st.write(f"Departing from: {prefs['start']}")
            
            for day in range(1, prefs["duration"] + 1):
                current_date = (prefs["start_date"] + timedelta(days=day-1)).strftime("%A, %b %d")
                st.markdown(f"""
                    <div class='day-card'>
                        <div class='day-header'>Day {day}: {current_date}</div>
                        <div class='activity-item'>Morning (9:00 AM - 12:00 PM): {st.session_state.activities[day-1] if day-1 < len(st.session_state.activities) else 'Leisure time'}</div>
                        <div class='activity-item'>Luncheon (12:00 PM - 1:00 PM): Local café ({prefs['dietary']} options)</div>
                        <div class='activity-item'>Afternoon (2:00 PM - 5:00 PM): {st.session_state.activities[day] if day < len(st.session_state.activities) else 'Local exploration'}</div>
                        <div class='activity-item'>Evening (7:00 PM - 10:00 PM): {st.session_state.activities[day+1] if day+1 < len(st.session_state.activities) else 'Rest at accommodation'}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
            st.write(f"Destination: {prefs['destination']}")
            st.write(f"Duration: {prefs['duration']} days")
            st.write(f"Budget: {prefs['budget'].capitalize()}")
            st.write(f"Interests: {', '.join(prefs['interests'])}")
            st.write(f"Dietary: {prefs['dietary'].capitalize()}")
            st.write(f"Accommodation: {prefs['accommodation'].capitalize()}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("Plan Another Journey"):
                st.session_state.stage = "input_refinement"
                st.session_state.preferences = {}
                st.session_state.activities = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
