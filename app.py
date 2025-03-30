import streamlit as st
import re  # For basic input parsing

# Simulated web-search database (replace with real API in a production setting)
ACTIVITIES_DB = {
    "Paris": {
        "art": [
            {"name": "Louvre Museum", "desc": "Iconic art like the Mona Lisa (~€17)", "miles": 2, "type": "famous"},
            {"name": "Musée d’Orsay", "desc": "Impressionist masterpieces (~€14)", "miles": 1.5, "type": "famous"},
            {"name": "Montmartre Art Walk", "desc": "Historic artist district (~5 miles)", "miles": 5, "type": "offbeat"},
            {"name": "Musée de l’Orangerie", "desc": "Monet’s Water Lilies (~€12)", "miles": 1, "type": "famous"},
            {"name": "Street Art in Belleville", "desc": "Offbeat murals (~4 miles)", "miles": 4, "type": "offbeat"}
        ],
        "food": [
            {"name": "Le Marais Food Stroll", "desc": "Casual falafel and pastries (~€6–10)", "miles": 2},
            {"name": "Canal Saint-Martin Picnic", "desc": "Local bites by the canal (~€10)", "miles": 3}
        ]
    }
}

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "input_refinement"
if "preferences" not in st.session_state:
    st.session_state.preferences = {}
if "activities" not in st.session_state:
    st.session_state.activities = []

# UI Header
st.title("AI-Powered Travel Planner")
st.write("Let’s plan your perfect trip! Tell me your preferences, and I’ll create a personalized itinerary.")

# Debug: Show current stage and preferences
st.write(f"Debug - Current Stage: {st.session_state.stage}")
st.write(f"Debug - Current Preferences: {st.session_state.preferences}")

# Stage 1: Input Refinement - Initial Input with Bonus Challenge
if st.session_state.stage == "input_refinement":
    with st.form(key="initial_input_form"):
        user_input = st.text_area("Tell me about your trip (e.g., destination, dates, budget, interests):", height=100)
        submit_button = st.form_submit_button(label="Submit Preferences")
    
    if submit_button and user_input:
        # Basic parsing for flexibility
        prefs = {}
        if "from" in user_input.lower():
            prefs["start"] = re.search(r"from\s+([A-Za-z\s]+)", user_input, re.IGNORECASE).group(1).strip()
        if any(city in user_input.lower() for city in ["paris", "london", "tokyo"]):  # Add more destinations as needed
            prefs["destination"] = next(city.capitalize() for city in ["Paris", "London", "Tokyo"] if city in user_input.lower())
        if "budget" in user_input.lower():
            prefs["budget"] = re.search(r"budget\s*[:\-\s]*(\w+)", user_input, re.IGNORECASE).group(1).strip()
        if any(date in user_input.lower() for date in ["june", "july", "2025"]):
            prefs["dates"] = "June 1–7, 2025"  # Hardcoded for demo; could parse dynamically
        prefs["interests"] = [i.strip() for i in user_input.lower().split(",") if i.strip() in ["art", "food", "history", "nature"]]
        
        st.session_state.preferences = prefs
        # Bonus Challenge: Handle vague/incomplete inputs
        if not all(k in prefs for k in ["destination", "dates"]):
            st.write("Hmm, I need a bit more info. Could you clarify your destination and travel dates?")
            with st.form(key="clarify_form"):
                clarification = st.text_area("Clarify your destination and dates:", height=100)
                clarify_button = st.form_submit_button(label="Submit Clarification")
            if clarify_button and clarification:
                if "from" in clarification.lower():
                    prefs["start"] = re.search(r"from\s+([A-Za-z\s]+)", clarification, re.IGNORECASE).group(1).strip()
                if any(city in clarification.lower() for city in ["paris", "london", "tokyo"]):
                    prefs["destination"] = next(city.capitalize() for city in ["Paris", "London", "Tokyo"] if city in clarification.lower())
                if any(date in clarification.lower() for date in ["june", "july", "2025"]):
                    prefs["dates"] = "June 1–7, 2025"
                st.session_state.preferences = prefs
                if "destination" in prefs and "dates" in prefs:
                    st.session_state.stage = "refine_preferences"
                    st.rerun()
        else:
            st.session_state.stage = "refine_preferences"
            st.rerun()

# Stage 2: Refine Preferences - Additional Questions
elif st.session_state.stage == "refine_preferences":
    prefs = st.session_state.preferences
    st.write(f"""
    Great, thanks for the details! Here’s what I’ve gathered:
    - Travel Dates: {prefs.get('dates', 'Not specified')}
    - Starting Location: {prefs.get('start', 'Not specified')}
    - Destination: {prefs.get('destination', 'Not specified')}
    - Budget: {prefs.get('budget', 'Not specified')}
    - Preferences: {', '.join(prefs.get('interests', [])) or 'Not specified'}
    
    A few quick questions:
    1. For interests like {', '.join(prefs.get('interests', []))}, any specifics (e.g., famous museums vs. hidden gems for art)?
    2. Any dietary preferences (e.g., vegetarian)?
    3. Accommodation preference (e.g., budget-friendly, central, luxury)?
    4. How much walking are you comfortable with daily (in miles)?
    """)
    
    with st.form(key="refined_input_form"):
        refined_input = st.text_area("Answer the questions to refine your preferences:", height=100)
        confirm_button = st.form_submit_button(label="Confirm Details")
    
    if confirm_button and refined_input:
        # Parse refined input dynamically
        refined_lines = [line.strip() for line in refined_input.split("\n") if line.strip()]
        if len(refined_lines) >= 4:
            specific_interests = refined_lines[0].lower()
            if "famous" in specific_interests:
                prefs["specific_interests"] = "famous"
            elif "hidden" in specific_interests or "offbeat" in specific_interests:
                prefs["specific_interests"] = "offbeat"
            prefs["dietary"] = refined_lines[1].lower() if "none" not in refined_lines[1].lower() else "none"
            prefs["accommodation"] = refined_lines[2].lower()
            prefs["mobility"] = re.search(r"(\d+)", refined_lines[3]).group(1) if re.search(r"(\d+)", refined_lines[3]) else "5"
        st.session_state.preferences = prefs
        st.session_state.stage = "activity_suggestions"
        st.rerun()
    elif confirm_button and not refined_input:
        st.write("Please answer all questions before confirming!")

# Stage 3: Activity Suggestions
elif st.session_state.stage == "activity_suggestions":
    prefs = st.session_state.preferences
    dest = prefs.get("destination", "Paris")
    interests = prefs.get("interests", [])
    specific = prefs.get("specific_interests", "famous")
    budget = prefs.get("budget", "moderate").lower()
    mobility = int(prefs.get("mobility", 5))
    
    st.write("Based on your preferences, here are some activity suggestions:")
    suggestions = []
    for interest in interests:
        if interest in ACTIVITIES_DB.get(dest, {}):
            acts = ACTIVITIES_DB[dest][interest]
            # Filter by specific interests and mobility
            filtered_acts = [act for act in acts if (specific in act.get("type", "") or interest != "art") and act["miles"] <= mobility]
            # Budget filter (simple heuristic: moderate = <€20)
            if budget == "moderate":
                filtered_acts = [act for act in filtered_acts if "€" not in act["desc"] or int(re.search(r"€(\d+)", act["desc"]).group(1)) <= 20]
            suggestions.extend(filtered_acts[:3])  # Limit to 3 per interest
    
    for i, act in enumerate(suggestions, 1):
        st.write(f"{i}. {act['name']} - {act['desc']}")
    
    with st.form(key="approve_activities_form"):
        approve_button = st.form_submit_button(label="Approve Activities")
    
    if approve_button:
        st.session_state.activities = [act["name"] for act in suggestions]
        st.session_state.stage = "itinerary_generation"
        st.rerun()

# Stage 4: Itinerary Generation
elif st.session_state.stage == "itinerary_generation":
    prefs = st.session_state.preferences
    acts = st.session_state.activities
    st.write(f"Here’s your personalized {prefs.get('dates', 'n-day')} itinerary for {prefs.get('destination', 'Paris')}:")
    
    itinerary = [
        f"**Day 1: {prefs.get('dates', '').split('–')[0]} – Arrival & Initial Exploration**",
        f"- Afternoon: Arrive, check into {prefs.get('accommodation', 'budget-friendly central')} hotel. {acts[0] if acts else 'Explore locally'} (~2 miles).",
    ]
    for i, act in enumerate(acts[1:], 2):
        date = f"June {i}" if "June" in prefs.get('dates', '') else f"Day {i}"
        itinerary.append(f"**Day {i}: {date} – {act.split(' - ')[0]}**")
        itinerary.append(f"- Morning: {act} (~{ACTIVITIES_DB[prefs.get('destination', 'Paris')][next(i for i in prefs.get('interests', []) if act in [a['name'] for a in ACTIVITIES_DB[prefs.get('destination', 'Paris')][i]])]['miles']} miles).")
    itinerary.append(f"**Day {len(acts) + 1}: {prefs.get('dates', '').split('–')[1]} – Departure**")
    itinerary.append("- Morning: Depart from Paris.")
    
    st.write("\n".join(itinerary))
    
    with st.form(key="start_over_form"):
        start_over_button = st.form_submit_button(label="Start Over")
    
    if start_over_button:
        st.session_state.stage = "input_refinement"
        st.session_state.preferences = {}
        st.session_state.activities = []
        st.rerun()
