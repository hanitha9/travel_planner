import streamlit as st

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

# Stage 1: Input Refinement - Initial Input
if st.session_state.stage == "input_refinement":
    with st.form(key="initial_input_form"):
        user_input = st.text_area("Tell me about your trip (e.g., destination, dates, budget, interests):", height=100)
        submit_button = st.form_submit_button(label="Submit Preferences")
    
    if submit_button and user_input:
        st.session_state.preferences["initial_input"] = user_input
        st.session_state.stage = "refine_preferences"
        st.rerun()

# Stage 2: Refine Preferences - Additional Questions
elif st.session_state.stage == "refine_preferences":
    st.write("""
    Great, thanks for the details! Here’s what I’ve gathered:
    - Travel Dates: June 1–7, 2025 (7 days, 6 nights)
    - Starting Location: New York
    - Destination: Paris
    - Budget: Moderate
    - Preferences: Art and food
    
    A few quick questions:
    1. For art, do you prefer famous museums (e.g., Louvre) or hidden galleries?
    2. Any dietary preferences (e.g., vegetarian)?
    3. Accommodation preference (e.g., budget-friendly, central)?
    4. How much walking are you comfortable with daily?
    """)
    
    with st.form(key="refined_input_form"):
        refined_input = st.text_area("Answer the questions to refine your preferences:", height=100)
        confirm_button = st.form_submit_button(label="Confirm Details")
    
    if confirm_button and refined_input:
        st.session_state.preferences = {
            "dates": "June 1–7, 2025",
            "start": "New York",
            "destination": "Paris",
            "budget": "Moderate",
            "interests": "Art (famous museums), casual food",
            "accommodation": "budget-friendly, central",
            "mobility": "5–7 miles/day"
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
    st.write("Here’s your personalized 7-day Paris itinerary:")
    st.write("""
    **Day 1: June 1 – Arrival & Le Marais**
    - Afternoon: Arrive, check into budget-friendly central hotel. Le Marais Food Stroll (~2 miles).
    
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
    - Morning: Depart from Paris.
    """)
    
    with st.form(key="start_over_form"):
        start_over_button = st.form_submit_button(label="Start Over")
    
    if start_over_button:
        st.session_state.stage = "input_refinement"
        st.session_state.preferences = {}
        st.session_state.activities = []
        st.rerun()
