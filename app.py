import streamlit as st
import re

# Custom CSS for enhanced aesthetics
st.markdown("""
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
        text-shadow: 2px 2px 4px #333333;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 20px;
        color: #F0F0F0;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 26px;
        font-weight: bold;
        color: #FFD700;
        margin-top: 20px;
        text-shadow: 1px 1px 2px #555555;
    }
    .debug {
        font-size: 12px;
        color: #888888;
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
    }
    .suggestion-box {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .itinerary-card {
        background-color: #FFF8E1;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .itinerary-card:hover {
        transform: scale(1.02);
    }
    .question {
        font-size: 16px;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 5px;
        text-shadow: 1px 1px 2px #333333;
    }
    body {
        background: linear-gradient(to bottom right, #87CEEB, #4682B4);
    }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "input_refinement"
if "preferences" not in st.session_state:
    st.session_state.preferences = {}
if "activities" not in st.session_state:
    st.session_state.activities = []

# Dynamic background image based on destination
destination_images = {
    "Paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=2073&auto=format&fit=crop",
    "London": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0?q=80&w=2070&auto=format&fit=crop",
    "Tokyo": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=2070&auto=format&fit=crop"
}

# Default image if no destination yet
header_image = destination_images.get(st.session_state.preferences.get("destination", "Paris"), destination_images["Paris"])

# UI Header with Dynamic Image
st.markdown('<div class="title">AI-Powered Travel Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Let’s craft your dream trip with a personalized itinerary!</div>', unsafe_allow_html=True)
st.image(header_image, caption="Explore Your Next Adventure", use_container_width=True)

# Debug: Show current stage and preferences
with st.expander("Debug Info", expanded=False):
    st.markdown(f'<div class="debug">Current Stage: {st.session_state.stage}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="debug">Current Preferences: {st.session_state.preferences}</div>', unsafe_allow_html=True)

# Stage 1: Input Refinement - Initial Input with Bonus Challenge
if st.session_state.stage == "input_refinement":
    st.markdown('<div class="section-header">Step 1: Tell Us About Your Trip</div>', unsafe_allow_html=True)
    with st.form(key="initial_input_form"):
        user_input = st.text_area("Share your trip details (e.g., destination, dates, budget, interests):", height=100)
        submit_button = st.form_submit_button(label="Submit Preferences", help="Let’s get started!")
    
    if submit_button and user_input:
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
            prefs["dates"] = "June 1–7, 2025"
        interests = []
        for interest in ["art", "food", "history", "nature", "famous", "offbeat"]:
            if interest in user_input.lower():
                interests.append(interest)
        prefs["interests"] = interests if interests else ["art", "food"]
        
        st.session_state.preferences = prefs
        if not all(k in prefs for k in ["destination", "dates"]):
            st.warning("Hmm, I need more info. Could you clarify your destination and travel dates?")
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
    st.markdown('<div class="section-header">Step 2: Refine Your Preferences</div>', unsafe_allow_html=True)
    prefs = st.session_state.preferences
    interests_str = ", ".join(prefs.get("interests", ["art", "food"]))
    st.write(f"""
    Great, thanks for the details! Here’s what I’ve gathered:
    - **Travel Dates:** {prefs.get('dates', 'June 1–7, 2025')}
    - **Starting Location:** {prefs.get('start', 'Not specified')}
    - **Destination:** {prefs.get('destination', 'Paris')}
    - **Budget:** {prefs.get('budget', 'Moderate')}
    - **Preferences:** {interests_str}
    """)
    st.image(destination_images.get(prefs.get("destination", "Paris"), destination_images["Paris"]), caption=f"{prefs.get('destination', 'Paris')} Awaits!", use_container_width=True)
    
    st.markdown("**A few quick questions to tailor your trip:**", unsafe_allow_html=True)
    st.markdown(f'<div class="question">1. For interests like {interests_str}, any specifics (e.g., famous museums vs. hidden galleries for art)?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question">2. Any dietary preferences (e.g., vegetarian)?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question">3. Accommodation preference (e.g., budget-friendly, central)?</div>', unsafe_allow_html=True)
    st.markdown('<div class="question">4. How much walking are you comfortable with daily (in miles)?</div>', unsafe_allow_html=True)
    
    with st.form(key="refined_input_form"):
        refined_input = st.text_area("Tell me more about your preferences:", height=150, placeholder="e.g., I prefer famous museums, no dietary restrictions, budget-friendly central hotel, and about 5 miles walking daily.")
        confirm_button = st.form_submit_button(label="Confirm Details")
    
    if confirm_button and refined_input:
        refined_text = refined_input.lower()
        specific_interests = "famous museums" if "famous" in refined_text else "hidden galleries" if "hidden" in refined_text or "offbeat" in refined_text else "famous museums"
        dietary = "none" if "none" in refined_text or "no dietary" in refined_text else "vegetarian" if "vegetarian" in refined_text else "none"
        accommodation = "budget-friendly, central" if "budget" in refined_text or "central" in refined_text else "budget-friendly, central"
        mobility_match = re.search(r"(\d+)\s*(miles|m)", refined_text)
        mobility = mobility_match.group(1) if mobility_match else "5"
        
        st.session_state.preferences = {
            "dates": prefs.get("dates", "June 1–7, 2025"),
            "start": prefs.get("start", "New York"),
            "destination": prefs.get("destination", "Paris"),
            "budget": prefs.get("budget", "Moderate"),
            "interests": ", ".join(prefs.get("interests", ["art", "food"])) + f" ({specific_interests})",
            "accommodation": accommodation,
            "mobility": mobility,
            "dietary": dietary
        }
        st.session_state.stage = "activity_suggestions"
        st.rerun()
    elif confirm_button and not refined_input:
        st.error("Please provide some details before confirming!")

# Stage 3: Activity Suggestions
elif st.session_state.stage == "activity_suggestions":
    prefs = st.session_state.preferences
    st.markdown('<div class="section-header">Step 3: Explore Activity Suggestions</div>', unsafe_allow_html=True)
    st.write("Based on your preferences, here are some exciting activities:")
    st.markdown('<div class="suggestion-box">1. Louvre Museum - Iconic art like the Mona Lisa (~€17).</div>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box">2. Musée d’Orsay - Impressionist masterpieces (~€14).</div>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box">3. Montmartre Art Walk - Historic artist district (~5 miles).</div>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box">4. Le Marais Food Stroll - Casual falafel and pastries (~€6–10).</div>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box">5. Musée de l’Orangerie - Monet’s Water Lilies (~€12).</div>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box">6. Canal Saint-Martin Picnic - Local bites by the canal (~€10).</div>', unsafe_allow_html=True)
    st.markdown('<div class="suggestion-box">7. Street Art in Belleville - Offbeat murals (~4 miles).</div>', unsafe_allow_html=True)
    st.image(destination_images.get(prefs.get("destination", "Paris"), destination_images["Paris"]), caption=f"Discover {prefs.get('destination', 'Paris')}", use_container_width=True)
    
    with st.form(key="approve_activities_form"):
        approve_button = st.form_submit_button(label="Approve Activities", help="Ready for your itinerary?")
    
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
    st.markdown('<div class="section-header">Step 4: Your Personalized Itinerary</div>', unsafe_allow_html=True)
    st.write(f"Here’s your tailored 7-day {prefs.get('destination', 'Paris')} itinerary:")
    itinerary = [
        f'<div class="itinerary-card"><i class="fas fa-plane-arrival"></i> <strong>Day 1: June 1 – Arrival & Le Marais</strong><br>- Afternoon: Arrive, check into {prefs.get("accommodation", "budget-friendly central")} hotel. Le Marais Food Stroll (~2 miles).</div>',
        f'<div class="itinerary-card"><i class="fas fa-palette"></i> <strong>Day 2: June 2 – Louvre</strong><br>- Morning: Louvre Museum (~€17, ~2 miles walking).</div>',
        f'<div class="itinerary-card"><i class="fas fa-paint-brush"></i> <strong>Day 3: June 3 – Impressionist Art</strong><br>- Morning: Musée d’Orsay (~€14). Afternoon: Musée de l’Orangerie (~€12, ~2.5 miles total).</div>',
        f'<div class="itinerary-card"><i class="fas fa-walking"></i> <strong>Day 4: June 4 – Montmartre</strong><br>- Morning: Montmartre Art Walk (~5 miles).</div>',
        f'<div class="itinerary-card"><i class="fas fa-utensils"></i> <strong>Day 5: June 5 – Canal Saint-Martin</strong><br>- Morning: Canal Saint-Martin Picnic (~3 miles).</div>',
        f'<div class="itinerary-card"><i class="fas fa-spray-can"></i> <strong>Day 6: June 6 – Belleville</strong><br>- Morning: Street Art in Belleville (~4 miles).</div>',
        f'<div class="itinerary-card"><i class="fas fa-plane-departure"></i> <strong>Day 7: June 7 – Departure</strong><br>- Morning: Depart from {prefs.get("destination", "Paris")}.</div>',
    ]
    for day in itinerary:
        st.markdown(day, unsafe_allow_html=True)
    st.image(destination_images.get(prefs.get("destination", "Paris"), destination_images["Paris"]), caption="Bon Voyage!", use_container_width=True)
    
    with st.form(key="start_over_form"):
        start_over_button = st.form_submit_button(label="Start Over", help="Plan another trip!")
    
    if start_over_button:
        st.session_state.stage = "input_refinement"
        st.session_state.preferences = {}
        st.session_state.activities = []
        st.rerun()

# Footer
st.markdown("---")
st.write("Powered by Streamlit | Designed for your travel dreams!")
