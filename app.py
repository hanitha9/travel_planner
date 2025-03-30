import streamlit as st
import re

# Custom CSS for updated aesthetics
st.markdown("""
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #00BFFF;
        text-align: center;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 20px;
        color: #00BFFF;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 26px;
        font-weight: bold;
        color: #FFD700;
        margin-top: 20px;
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
        color: #000000;
        margin-bottom: 5px;
    }
    .image-container {
        position: relative;
        width: 100%;
        height: 300px;
        background-size: cover;
        background-position: center;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .image-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
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
if "scroll_to" not in st.session_state:
    st.session_state.scroll_to = None

# Dynamic background image based on destination
destination_images = {
    "Paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=2073&auto=format&fit=crop",
    "London": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0?q=80&w=2070&auto=format&fit=crop",
    "Tokyo": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=2070&auto=format&fit=crop"
}

# Header with Dynamic Image
header_image = destination_images.get(st.session_state.preferences.get("destination", "Paris"), destination_images["Paris"])
st.markdown('<div class="title">AI-Powered Travel Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Let\'s craft your dream trip with a personalized itinerary!</div>', unsafe_allow_html=True)
st.image(header_image, caption="Explore Your Next Adventure", use_container_width=True)

# Scroll to section if set
if st.session_state.scroll_to:
    st.markdown(f"""
        <script>
        setTimeout(() => {{
            let element = document.getElementById("{st.session_state.scroll_to}");
            if (element) {{
                element.scrollIntoView({{behavior: "smooth", block: "start"}});
            }} else {{
                console.log("Element {st.session_state.scroll_to} not found");
            }}
        }}, 500);
        </script>
    """, unsafe_allow_html=True)
    st.session_state.scroll_to = None

# Stage 1: Input Refinement
if st.session_state.stage == "input_refinement":
    st.markdown('<div class="section-header" id="step1">Step 1: Tell Us About Your Trip</div>', unsafe_allow_html=True)
    with st.form(key="initial_input_form"):
        user_input = st.text_area("Share your trip details (e.g., destination, dates, budget, interests):", height=100)
        submit_button = st.form_submit_button(label="Submit Preferences")
    
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
            prefs["dates"] = "June 1-7, 2025"
        interests = []
        for interest in ["art", "food", "history", "nature", "famous", "offbeat"]:
            if interest in user_input.lower():
                interests.append(interest)
        prefs["interests"] = interests if interests else ["art", "food"]
        
        st.session_state.preferences = prefs
        
        # Check if we have minimum required info (destination and dates)
        if not prefs.get("destination"):
            st.warning("Please specify your destination (e.g., Paris, London, Tokyo)")
        elif not prefs.get("dates"):
            st.warning("Please specify your travel dates (e.g., June 1-7, 2025)")
        else:
            st.session_state.stage = "refine_preferences"
            st.session_state.scroll_to = "step2"
            st.rerun()

# Stage 2: Refine Preferences
elif st.session_state.stage == "refine_preferences":
    st.markdown('<div class="section-header" id="step2">Step 2: Refine Your Preferences</div>', unsafe_allow_html=True)
    prefs = st.session_state.preferences
    interests_str = ", ".join(prefs.get("interests", ["art", "food"]))
    
    # Image above the refinement section
    st.markdown(f"""
        <div class="image-container" style="background-image: url('{destination_images.get(prefs.get('destination', 'Paris'), destination_images['Paris'])}');">
            <div class="image-overlay">{prefs.get('destination', 'Paris')} Awaits!</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write(f"""
    Great, thanks for the details! Here's what I've gathered:
    - **Travel Dates:** {prefs.get('dates', 'June 1-7, 2025')}
    - **Starting Location:** {prefs.get('start', 'Not specified')}
    - **Destination:** {prefs.get('destination', 'Paris')}
    - **Budget:** {prefs.get('budget', 'Moderate')}
    - **Preferences:** {interests_str}
    """)
    
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
        if "landmarks" in refined_text.lower():
            specific_interests = "famous landmarks"
        dietary = "none" if "none" in refined_text or "no dietary" in refined_text else "vegetarian" if "vegetarian" in refined_text else "none"
        accommodation = "budget-friendly, central" if "budget" in refined_text or "central" in refined_text else "budget-friendly, central"
        mobility_match = re.search(r"(\d+)\s*(miles|m)", refined_text)
        mobility = mobility_match.group(1) if mobility_match else "5"
        
        st.session_state.preferences = {
            "dates": prefs.get("dates", "June 1-7, 2025"),
            "start": prefs.get("start", "New York"),
            "destination": prefs.get("destination", "Paris"),
            "budget": prefs.get("budget", "Moderate"),
            "interests": ", ".join(prefs.get("interests", ["art", "food"])) + f" ({specific_interests})",
            "accommodation": accommodation,
            "mobility": mobility,
            "dietary": dietary
        }
        st.session_state.stage = "activity_suggestions"
        st.session_state.scroll_to = "step3"
        st.rerun()
    elif confirm_button and not refined_input:
        st.error("Please provide some details before confirming!")

# Stage 3: Activity Suggestions
elif st.session_state.stage == "activity_suggestions":
    prefs = st.session_state.preferences
    st.markdown('<div class="section-header" id="step3">Step 3: Explore Activity Suggestions</div>', unsafe_allow_html=True)
    
    # Image above the suggestions section
    st.markdown(f"""
        <div class="image-container" style="background-image: url('{destination_images.get(prefs.get('destination', 'Paris'), destination_images['Paris'])}');">
            <div class="image-overlay">Discover {prefs.get('destination', 'Paris')}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("Based on your preferences, here are some exciting activities:")
    
    # Dynamic activity suggestions based on destination
    if prefs.get("destination") == "Paris":
        activities = [
            "Louvre Museum - Iconic art like the Mona Lisa (~€17)",
            "Musée d'Orsay - Impressionist masterpieces (~€14)",
            "Montmartre Art Walk - Historic artist district (~5 miles)",
            "Le Marais Food Stroll - Casual falafel and pastries (~€6-10)",
            "Musée de l'Orangerie - Monet's Water Lilies (~€12)",
            "Canal Saint-Martin Picnic - Local bites by the canal (~€10)",
            "Street Art in Belleville - Offbeat murals (~4 miles)"
        ]
    elif prefs.get("destination") == "London":
        activities = [
            "British Museum - World-famous history and artifacts (Free entry)",
            "Tower of London - Historic fortress and Crown Jewels (~£30)",
            "Westminster Abbey - Iconic Gothic church (~£29)",
            "Borough Market - Vegetarian food stalls (~£8-12)",
            "Covent Garden - Vegetarian dining options (~£10-15)",
            "Thames River Walk - Scenic walk past landmarks (~4 miles)",
            "Camden Market - Vegetarian street food (~£5-10, ~3 miles)"
        ]
    else:  # Default to Paris
        activities = [
            "Louvre Museum - Iconic art like the Mona Lisa (~€17)",
            "Musée d'Orsay - Impressionist masterpieces (~€14)",
            "Montmartre Art Walk - Historic artist district (~5 miles)",
            "Le Marais Food Stroll - Casual falafel and pastries (~€6-10)",
            "Musée de l'Orangerie - Monet's Water Lilies (~€12)",
            "Canal Saint-Martin Picnic - Local bites by the canal (~€10)",
            "Street Art in Belleville - Offbeat murals (~4 miles)"
        ]
    
    for activity in activities:
        st.markdown(f'<div class="suggestion-box">{activity}</div>', unsafe_allow_html=True)
    
    with st.form(key="approve_activities_form"):
        approve_button = st.form_submit_button(label="Approve Activities")
    
    if approve_button:
        st.session_state.activities = activities
        st.session_state.stage = "itinerary_generation"
        st.session_state.scroll_to = "step4"
        st.rerun()

# Stage 4: Itinerary Generation
elif st.session_state.stage == "itinerary_generation":
    prefs = st.session_state.preferences
    st.markdown('<div class="section-header" id="step4">Step 4: Your Personalized Itinerary</div>', unsafe_allow_html=True)
    st.write(f"Here's your tailored 7-day {prefs.get('destination', 'Paris')} itinerary:")
    
    # Dynamic itinerary based on destination
    if prefs.get("destination") == "Paris":
        itinerary = [
            f'<div class="itinerary-card"><i class="fas fa-plane-arrival"></i> <strong>Day 1: June 1 - Arrival & Le Marais</strong><br>- Afternoon: Arrive, check into {prefs.get("accommodation", "budget-friendly central")} hotel. Le Marais Food Stroll (~2 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-palette"></i> <strong>Day 2: June 2 - Louvre</strong><br>- Morning: Louvre Museum (~€17, ~2 miles walking).</div>',
            f'<div class="itinerary-card"><i class="fas fa-paint-brush"></i> <strong>Day 3: June 3 - Impressionist Art</strong><br>- Morning: Musée d\'Orsay (~€14). Afternoon: Musée de l\'Orangerie (~€12, ~2.5 miles total).</div>',
            f'<div class="itinerary-card"><i class="fas fa-walking"></i> <strong>Day 4: June 4 - Montmartre</strong><br>- Morning: Montmartre Art Walk (~5 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-utensils"></i> <strong>Day 5: June 5 - Canal Saint-Martin</strong><br>- Morning: Canal Saint-Martin Picnic (~3 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-spray-can"></i> <strong>Day 6: June 6 - Belleville</strong><br>- Morning: Street Art in Belleville (~4 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-plane-departure"></i> <strong>Day 7: June 7 - Departure</strong><br>- Morning: Depart from {prefs.get("destination", "Paris")}.</div>'
        ]
    elif prefs.get("destination") == "London":
        itinerary = [
            f'<div class="itinerary-card"><i class="fas fa-plane-arrival"></i> <strong>Day 1: June 1 - Arrival & Covent Garden</strong><br>- Afternoon: Arrive, check into {prefs.get("accommodation", "budget-friendly central")} hotel. Covent Garden for vegetarian dining (~2 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-university"></i> <strong>Day 2: June 2 - British Museum</strong><br>- Morning: British Museum (Free entry, ~2 miles walking).</div>',
            f'<div class="itinerary-card"><i class="fas fa-chess-rook"></i> <strong>Day 3: June 3 - Tower of London</strong><br>- Morning: Tower of London (~£30, ~2 miles walking).</div>',
            f'<div class="itinerary-card"><i class="fas fa-church"></i> <strong>Day 4: June 4 - Westminster Abbey</strong><br>- Morning: Westminster Abbey (~£29, ~2 miles walking).</div>',
            f'<div class="itinerary-card"><i class="fas fa-utensils"></i> <strong>Day 5: June 5 - Borough Market</strong><br>- Morning: Borough Market for vegetarian food (~3 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-walking"></i> <strong>Day 6: June 6 - Thames River Walk & Camden Market</strong><br>- Morning: Thames River Walk (~4 miles). Afternoon: Camden Market for vegetarian street food (~3 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-plane-departure"></i> <strong>Day 7: June 7 - Departure</strong><br>- Morning: Depart from {prefs.get("destination", "London")}.</div>'
        ]
    else:  # Default to Paris
        itinerary = [
            f'<div class="itinerary-card"><i class="fas fa-plane-arrival"></i> <strong>Day 1: June 1 - Arrival & Le Marais</strong><br>- Afternoon: Arrive, check into {prefs.get("accommodation", "budget-friendly central")} hotel. Le Marais Food Stroll (~2 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-palette"></i> <strong>Day 2: June 2 - Louvre</strong><br>- Morning: Louvre Museum (~€17, ~2 miles walking).</div>',
            f'<div class="itinerary-card"><i class="fas fa-paint-brush"></i> <strong>Day 3: June 3 - Impressionist Art</strong><br>- Morning: Musée d\'Orsay (~€14). Afternoon: Musée de l\'Orangerie (~€12, ~2.5 miles total).</div>',
            f'<div class="itinerary-card"><i class="fas fa-walking"></i> <strong>Day 4: June 4 - Montmartre</strong><br>- Morning: Montmartre Art Walk (~5 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-utensils"></i> <strong>Day 5: June 5 - Canal Saint-Martin</strong><br>- Morning: Canal Saint-Martin Picnic (~3 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-spray-can"></i> <strong>Day 6: June 6 - Belleville</strong><br>- Morning: Street Art in Belleville (~4 miles).</div>',
            f'<div class="itinerary-card"><i class="fas fa-plane-departure"></i> <strong>Day 7: June 7 - Departure</strong><br>- Morning: Depart from {prefs.get("destination", "Paris")}.</div>'
        ]
    
    for day in itinerary:
        st.markdown(day, unsafe_allow_html=True)
    
    with st.form(key="start_over_form"):
        start_over_button = st.form_submit_button(label="Start Over")
    
    if start_over_button:
        st.session_state.stage = "input_refinement"
        st.session_state.preferences = {}
        st.session_state.activities = []
        st.session_state.scroll_to = "step1"
        st.rerun()

# Footer
st.markdown("---")
st.write("Powered by Streamlit | Designed for your travel dreams!")
