import streamlit as st
import re
from fuzzywuzzy import process

# Custom CSS for updated aesthetics
st.markdown("""
    <style>
    .title {
        font-size: 40px;
        font-weight: bold;
        color: #00BFFF; /* Deep Sky Blue for bright title */
        text-align: center;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 20px;
        color: #00BFFF; /* Deep Sky Blue to match title */
        text-align: center;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 26px;
        font-weight: bold;
        color: #FFD700; /* Gold */
        margin-top: 20px;
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
        color: #000000; /* Black for questions */
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
        background: rgba(0, 0, 0, 0.5); /* Semi-transparent black overlay */
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

# Travel data structure (subset for demonstration)
travel_data = {
    "Europe": {
        "France": {
            "Paris": {
                "activities": {
                    "art": [
                        {"name": "Louvre Museum", "description": "Iconic art like the Mona Lisa", "cost": "€17", "walking": "2 miles"},
                        {"name": "Musée d’Orsay", "description": "Impressionist masterpieces", "cost": "€14", "walking": "2 miles"},
                        {"name": "Musée de l’Orangerie", "description": "Monet’s Water Lilies", "cost": "€12", "walking": "1 mile"}
                    ],
                    "food": [
                        {"name": "Le Marais Food Stroll", "description": "Casual falafel and pastries", "cost": "€6–10", "walking": "2 miles"},
                        {"name": "Canal Saint-Martin Picnic", "description": "Local bites by the canal", "cost": "€10", "walking": "3 miles"}
                    ],
                    "history": [
                        {"name": "Montmartre Art Walk", "description": "Historic artist district", "cost": "Free", "walking": "5 miles"}
                    ],
                    "offbeat": [
                        {"name": "Street Art in Belleville", "description": "Offbeat murals", "cost": "Free", "walking": "4 miles"}
                    ]
                }
            }
        },
        "United Kingdom": {
            "England": {
                "London": {
                    "activities": {
                        "history": [
                            {"name": "British Museum", "description": "World-famous history and artifacts", "cost": "Free", "walking": "2 miles"},
                            {"name": "Tower of London", "description": "Historic fortress and Crown Jewels", "cost": "£30", "walking": "2 miles"},
                            {"name": "Westminster Abbey", "description": "Iconic Gothic church", "cost": "£29", "walking": "2 miles"}
                        ],
                        "food": [
                            {"name": "Borough Market", "description": "Vegetarian food stalls like Ethiopian wraps", "cost": "£8–12", "walking": "3 miles"},
                            {"name": "Covent Garden", "description": "Vegetarian dining options like The Barbary Next Door", "cost": "£10–15", "walking": "2 miles"},
                            {"name": "Camden Market", "description": "Vegetarian street food and history", "cost": "£5–10", "walking": "3 miles"}
                        ],
                        "nature": [
                            {"name": "Thames River Walk", "description": "Scenic walk past landmarks", "cost": "Free", "walking": "4 miles"}
                        ]
                    }
                }
            }
        }
    },
    "Asia": {
        "Japan": {
            "Tokyo": {
                "activities": {
                    "culture": [
                        {"name": "Senso-ji Temple", "description": "Historic Buddhist temple", "cost": "Free", "walking": "2 miles"},
                        {"name": "Meiji Shrine", "description": "Serene Shinto shrine", "cost": "Free", "walking": "3 miles"}
                    ],
                    "food": [
                        {"name": "Tsukiji Market", "description": "Fresh sushi and street food", "cost": "¥1000–2000", "walking": "2 miles"},
                        {"name": "Dotonbori Food Tour", "description": "Street food like takoyaki", "cost": "¥1500–2500", "walking": "3 miles"}
                    ],
                    "nature": [
                        {"name": "Shinjuku Gyoen National Garden", "description": "Beautiful gardens and greenery", "cost": "¥500", "walking": "3 miles"}
                    ]
                }
            }
        }
    }
}

# Dynamic background image based on destination
destination_images = {
    "Paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=2073&auto=format&fit=crop",
    "London": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0?q=80&w=2070&auto=format&fit=crop",
    "Tokyo": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?q=80&w=2070&auto=format&fit=crop"
}

# Initialize session state
if "stage" not in st.session_state:
    st.session_state.stage = "input_refinement"
if "preferences" not in st.session_state:
    st.session_state.preferences = {}
if "activities" not in st.session_state:
    st.session_state.activities = []
if "scroll_to" not in st.session_state:
    st.session_state.scroll_to = None

# Helper function to find destination in travel_data
def find_destination(user_input):
    user_input = user_input.lower()
    # Check for continents
    continents = list(travel_data.keys())
    continent_match = next((c for c in continents if c.lower() in user_input), None)
    
    if continent_match:
        # If continent is specified, narrow down to countries and cities
        countries = list(travel_data[continent_match].keys())
        country_match = next((c for c in countries if c.lower() in user_input), None)
        
        if country_match:
            cities = list(travel_data[continent_match][country_match].keys())
            city_match = next((city for city in cities if city.lower() in user_input), None)
            
            if city_match:
                return continent_match, country_match, city_match
            else:
                # Default to the first city in the country
                return continent_match, country_match, cities[0]
        else:
            # Default to the first country and city in the continent
            country = countries[0]
            city = list(travel_data[continent_match][country].keys())[0]
            return continent_match, country, city
    else:
        # Check for countries and cities directly
        for continent, countries in travel_data.items():
            for country, cities in countries.items():
                for city in cities.keys():
                    if city.lower() in user_input:
                        return continent, country, city
                if country.lower() in user_input:
                    city = list(cities.keys())[0]
                    return continent, country, city
    # Default to Paris if no match
    return "Europe", "France", "Paris"

# Header with Dynamic Image
header_image = destination_images.get(st.session_state.preferences.get("city", "Paris"), destination_images["Paris"])
st.markdown('<div class="title">AI-Powered Travel Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Let’s craft your dream trip with a personalized itinerary!</div>', unsafe_allow_html=True)
st.image(header_image, caption="Explore Your Next Adventure", use_container_width=True)

# Debug: Show current stage and preferences
with st.expander("Debug Info", expanded=False):
    st.markdown(f'<div class="debug">Current Stage: {st.session_state.stage}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="debug">Current Preferences: {st.session_state.preferences}</div>', unsafe_allow_html=True)

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
        submit_button = st.form_submit_button(label="Submit Preferences", help="Let’s get started!")
    
    if submit_button and user_input:
        prefs = {}
        # Parse starting location
        if "from" in user_input.lower():
            match = re.search(r"from\s+([A-Za-z\s]+)", user_input, re.IGNORECASE)
            if match:
                prefs["start"] = match.group(1).strip()
        
        # Parse destination (continent, country, city)
        continent, country, city = find_destination(user_input)
        prefs["continent"] = continent
        prefs["country"] = country
        prefs["city"] = city
        
        # Parse budget
        if "budget" in user_input.lower():
            match = re.search(r"budget\s*[:\-\s]*(\w+)", user_input, re.IGNORECASE)
            if match:
                prefs["budget"] = match.group(1).strip()
        
        # Parse dates
        if any(date in user_input.lower() for date in ["june", "july", "2025"]):
            prefs["dates"] = "June 1–7, 2025"
        
        # Parse interests
        interests = []
        for interest in ["art", "food", "history", "nature", "culture", "adventure", "famous", "offbeat"]:
            if interest in user_input.lower():
                interests.append(interest)
        prefs["interests"] = interests if interests else ["art", "food"]
        
        st.session_state.preferences = prefs
        if not all(k in prefs for k in ["city", "dates"]):
            st.warning("Hmm, I need more info. Could you clarify your destination and dates?")
            with st.form(key="clarify_form"):
                clarification = st.text_area("Clarify your destination and dates:", height=100)
                clarify_button = st.form_submit_button(label="Submit Clarification")
            
            # Add validation for empty clarification
            if clarify_button:
                if not clarification:
                    st.error("Please provide clarification details before submitting.")
                else:
                    if "from" in clarification.lower():
                        match = re.search(r"from\s+([A-Za-z\s]+)", clarification, re.IGNORECASE)
                        if match:
                            prefs["start"] = match.group(1).strip()
                    continent, country, city = find_destination(clarification)
                    prefs["continent"] = continent
                    prefs["country"] = country
                    prefs["city"] = city
                    if any(date in clarification.lower() for date in ["june", "july", "2025"]):
                        prefs["dates"] = "June 1–7, 2025"
                    st.session_state.preferences = prefs
                    if "city" in prefs and "dates" in prefs:
                        st.session_state.stage = "refine_preferences"
                        st.session_state.scroll_to = "step2"
                        st.rerun()
                    else:
                        st.warning("Still missing some details. Please ensure you provide both destination and dates.")
        else:
            st.session_state.stage = "refine_preferences"
            st.session_state.scroll_to = "step2"
            st.rerun()
    elif submit_button and not user_input:
        st.error("Please provide some details before submitting!")

# Stage 2: Refine Preferences
elif st.session_state.stage == "refine_preferences":
    st.markdown('<div class="section-header" id="step2">Step 2: Refine Your Preferences</div>', unsafe_allow_html=True)
    prefs = st.session_state.preferences
    interests_str = ", ".join(prefs.get("interests", ["art", "food"]))
    
    # Image above the refinement section
    st.markdown(f"""
        <div class="image-container" style="background-image: url('{destination_images.get(prefs.get('city', 'Paris'), destination_images['Paris'])}');">
            <div class="image-overlay">{prefs.get('city', 'Paris')} Awaits!</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write(f"""
    Great, thanks for the details! Here’s what I’ve gathered:
    - **Travel Dates:** {prefs.get('dates', 'June 1–7, 2025')}
    - **Starting Location:** {prefs.get('start', 'Not specified')}
    - **Destination:** {prefs.get('city', 'Paris')} ({prefs.get('country', 'France')}, {prefs.get('continent', 'Europe')})
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
            "dates": prefs.get("dates", "June 1–7, 2025"),
            "start": prefs.get("start", "Not specified"),
            "continent": prefs.get("continent", "Europe"),
            "country": prefs.get("country", "France"),
            "city": prefs.get("city", "Paris"),
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
        <div class="image-container" style="background-image: url('{destination_images.get(prefs.get('city', 'Paris'), destination_images['Paris'])}');">
            <div class="image-overlay">Discover {prefs.get('city', 'Paris')}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("Based on your preferences, here are some exciting activities:")
    
    # Fetch activities based on destination and preferences
    continent = prefs.get("continent")
    country = prefs.get("country")
    city = prefs.get("city")
    interests = prefs.get("interests").split(", ")[0].split(", ")  # e.g., ["art", "food"]
    specific_interests = prefs.get("interests").split("(")[1].strip(")") if "(" in prefs.get("interests") else ""
    dietary = prefs.get("dietary")
    mobility = int(prefs.get("mobility"))
    
    activities = []
    try:
        city_activities = travel_data[continent][country][city]["activities"]
        for interest in interests:
            if interest in city_activities:
                for activity in city_activities[interest]:
                    # Filter by specific interests (e.g., famous museums)
                    if specific_interests in activity["description"].lower() or not specific_interests:
                        # Filter by walking distance
                        activity_walking = int(activity["walking"].split()[0])
                        if activity_walking <= mobility:
                            # Filter by dietary preferences
                            if dietary == "vegetarian" and "food" in interest:
                                if "vegetarian" in activity["description"].lower():
                                    activities.append(activity)
                            else:
                                activities.append(activity)
    except KeyError:
        st.error("Sorry, we don’t have activities for this destination yet. Please try another city.")
        activities = []
    
    # Display activities
    if activities:
        for idx, activity in enumerate(activities[:7], 1):  # Limit to 7 activities
            st.markdown(f'<div class="suggestion-box">{idx}. {activity["name"]} - {activity["description"]} (~{activity["cost"]}, ~{activity["walking"]}).</div>', unsafe_allow_html=True)
    else:
        st.write("No activities match your preferences. Please adjust your preferences or try another destination.")
    
    with st.form(key="approve_activities_form"):
        approve_button = st.form_submit_button(label="Approve Activities", help="Ready for your itinerary?")
    
    if approve_button:
        st.session_state.activities = [activity["name"] for activity in activities[:7]]
        st.session_state.stage = "itinerary_generation"
        st.session_state.scroll_to = "step4"
        st.rerun()

# Stage 4: Itinerary Generation
elif st.session_state.stage == "itinerary_generation":
    prefs = st.session_state.preferences
    st.markdown('<div class="section-header" id="step4">Step 4: Your Personalized Itinerary</div>', unsafe_allow_html=True)
    st.write(f"Here’s your tailored 7-day {prefs.get('city', 'Paris')} itinerary:")
    
    # Generate itinerary
    activities = st.session_state.activities
    if not activities:
        st.error("No activities available to create an itinerary. Please go back and select some activities.")
    else:
        itinerary = []
        # Day 1: Arrival
        itinerary.append(f'<div class="itinerary-card"><i class="fas fa-plane-arrival"></i> <strong>Day 1: June 1 – Arrival</strong><br>- Afternoon: Arrive, check into {prefs.get("accommodation", "budget-friendly central")} hotel.</div>')
        
        # Days 2–6: Activities
        for day, activity in enumerate(activities[:5], 2):  # Spread 5 activities over days 2–6
            itinerary.append(f'<div class="itinerary-card"><i class="fas fa-star"></i> <strong>Day {day}: June {day} – {activity}</strong><br>- Morning: {activity}.</div>')
        
        # Day 7: Departure
        itinerary.append(f'<div class="itinerary-card"><i class="fas fa-plane-departure"></i> <strong>Day 7: June 7 – Departure</strong><br>- Morning: Depart from {prefs.get("city", "Paris")}.</div>')
        
        for day in itinerary:
            st.markdown(day, unsafe_allow_html=True)
    
    with st.form(key="start_over_form"):
        start_over_button = st.form_submit_button(label="Start Over", help="Plan another trip!")
    
    if start_over_button:
        st.session_state.stage = "input_refinement"
        st.session_state.preferences = {}
        st.session_state.activities = []
        st.session_state.scroll_to = "step1"
        st.rerun()

# Footer
st.markdown("---")
st.write("Powered by Streamlit | Designed for your travel dreams!")
