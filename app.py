import streamlit as st
import re

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
        # Parse initial input flexibly
        prefs = {}
        if "from" in user_input.lower():
            match = re.search(r"from\s+([A-Za-z\s]+)", user_input, re.IGNORECASE)
            if match:
                prefs["start"] = match.group(1).strip()
        cities = ["Paris", "London", "Tokyo"]
        destination = next((city.capitalize() for city in cities if city.lower() in user_input.lower()), None)
        if destination:
            prefs["destination"] = destination
        if "budget" in user_input.lower():
            match = re.search(r"budget\s*[:\-\s]*(\w+)", user_input, re.IGNORECASE)
            if match:
                prefs["budget"] = match.group(1).strip()
        if any(date in user_input.lower() for date in ["june", "july", "2025"]):
            prefs["dates"] = "June 1–7, 2025"  # Hardcoded for demo
        # Flexible interest parsing (not strict list)
        interests = []
        for interest in ["art", "food", "history", "nature", "famous", "offbeat"]:
            if interest in user_input.lower():
                interests.append(interest)
        prefs["interests"] = interests if interests else ["art", "food"]  # Default if none found
        
        st.session_state.preferences = prefs
        # Bonus Challenge: Handle vague/incomplete inputs
        if not all(k in prefs for k in ["destination", "dates"]):
            st.write("Hmm, I need more info. Could you clarify your destination and travel dates?")
            with st.form(key="clarify_form"):
                clarification = st.text_area("Clarify your destination and dates:", height=100)
                clarify_button = st.form_submit_button(label="Submit Clarification")
            if clarify_button and clarification:
                if "from" in clarification.lower():
                    match = re.search(r"from\s+([A-Za-z\s]+)", clarification, re.IGNORECASE)
                    if match:
                        prefs["start"] = match.group(1).strip()
                destination = next((city.capitalize() for city in cities if city.lower() in clarification.lower()), None)
                if destination:
                    prefs["destination"] = destination
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
    interests_str = ", ".join(prefs.get("interests", ["art", "food"]))
    st.write(f"""
    Great, thanks for the details! Here’s what I’ve gathered:
    - Travel Dates: {prefs.get('dates', 'June 1–7, 2025')}
    - Starting Location: {prefs.get('start', 'New York')}
    - Destination: {prefs.get('destination', 'Paris')}
    - Budget: {prefs.get('budget', 'Moderate')}
    - Preferences: {interests_str}
    
    A few quick questions:
    1. For interests like {interests_str}, any specifics (e.g., famous museums vs. hidden galleries for art)?
    2. Any dietary preferences (e.g., vegetarian)?
    3. Accommodation preference (e.g., budget-friendly, central)?
    4. How much walking are you comfortable with daily?
    """)
    
    with st.form(key="refined_input_form"):
        refined_input = st.text_area("Answer the questions to refine your preferences:", height=100)
        confirm_button = st.form_submit_button(label="Confirm Details")
    
    if confirm_button and refined_input:
        refined_lines = [line.strip() for line in refined_input.split("\n") if line.strip()]
        specific_interests = refined_lines[0].lower() if refined_lines else "famous museums"
        dietary = refined_lines[1].lower() if len(refined_lines) > 1 and "none" not in refined_lines[1].lower() else "none"
        accommodation = refined_lines[2].lower() if len(refined_lines) > 2 else "budget-friendly, central"
        mobility = re.search(r"(\d+)", refined_lines[3]).group(1) if len(refined_lines) > 3 and re.search(r"(\d+)", refined_lines[3]) else "5"
        
        st.session_state.preferences = {
            "dates": prefs.get("dates", "June 1–7, 2025"),
            "start": prefs.get("start", "New York"),
            "destination": prefs.get("destination", "Paris"),
            "budget": prefs.get("budget", "Moderate"),
            "interests": f"{', '.join(prefs.get('interests', ['art', 'food']))} ({specific_interests})",
            "accommodation": accommodation,
            "mobility": mobility,
            "dietary": dietary
        }
        st.session_state.stage = "activity_suggestions"
        st.rerun()
    elif confirm_button and not refined_input:
        st.write("Please provide answers to the questions before confirming!")

# Stage 3: Activity Suggestions
elif st.session_state.stage == "activity_suggestions":
    st.write("Based on your preferences, here are some activity suggestions:")
    st.write("""
    1. Louvre Museum - Iconic art like the Mona Lisa (~€17).
    2. Musée d’Orsay - Impressionist masterpieces (~€14).
    3. Montmartre Art Walk - Historic artist district (~5 miles).
    4. Le Marais Food Stroll - Casual falafel and pastries (~€6–10).
    5. Musée de l’Orangerie - Monet’s Water Lilies (~€12).
    6. Canal Saint-Martin Picnic - Local bites by the canal (~€10).
    7. Street Art in Belleville - Offbeat murals (~4 miles).
    """)
    
    with st.form(key="approve_activities_form"):
        approve_button = st.form_submit_button(label="Approve Activities")
    
    if approve_button:
        st.session_state.activities = [
            "Louvre Museum", "Musée d’Orsay", "Montmartre Art Walk",
            "Le Marais Food Stroll", "Musée de l’Orangerie",
            "Canal Saint-Martin Picnic", "Street Art in Belleville"
        ]
        st.session_state.stage = "itinerary_generation"
        st.rerun()

# Stage 4: Itinerary Generation
elif st.session_state.stage == "itinerary_generation":
    prefs = st.session_state.preferences
    st.write(f"Here’s your personalized 7-day {prefs.get('destination', 'Paris')} itinerary:")
    st.write(f"""
    **Day 1: June 1 – Arrival & Le Marais**
    - Afternoon: Arrive, check into {prefs.get('accommodation', 'budget-friendly central')} hotel. Le Marais Food Stroll (~2 miles).
    
    **Day 2: June 2 – Louvre**
    - Morning: Louvre Museum (~€17, ~2 miles walking).
    
    **Day 3: June 3 – Impressionist Art**
    - Morning: Musée d’Orsay (~€14). Afternoon: Musée de l’Orangerie (~€12, ~2.5 miles total).
    
    **Day 4: June 4 – Montmartre**
    - Morning: Montmartre Art Walk (~5 miles).
    
    **Day 5: June 5 – Canal Saint-Martin**
    - Morning: Canal Saint-Martin Picnic (~3 miles).
    
    **Day 6: June 6 – Belleville**
    - Morning: Street Art in Belleville (~4 miles).
    
    **Day 7: June 7 – Departure**
    - Morning: Depart from {prefs.get('destination', 'Paris')}.
    """)
    
    with st.form(key="start_over_form"):
        start_over_button = st.form_submit_button(label="Start Over")
    
    if start_over_button:
        st.session_state.stage = "input_refinement"
        st.session_state.preferences = {}
        st.session_state.activities = []
        st.rerun()
