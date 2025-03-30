import streamlit as st
import re
from datetime import datetime, timedelta
import random

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
    .tag {
        display: inline-block;
        background-color: #00BFFF;
        color: white;
        padding: 3px 8px;
        border-radius: 15px;
        font-size: 12px;
        margin-right: 5px;
        margin-bottom: 5px;
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

# Enhanced destination database with images and activities
DESTINATION_DATA = {
    "Paris": {
        "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
        "activities": {
            "art": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou"],
            "food": ["Le Marais Food Tour", "Montmartre Cafés", "Seine River Dinner Cruise"],
            "history": ["Eiffel Tower", "Notre-Dame", "Arc de Triomphe"],
            "nature": ["Luxembourg Gardens", "Bois de Boulogne", "Seine River Walk"]
        }
    },
    "London": {
        "image": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0",
        "activities": {
            "art": ["Tate Modern", "National Gallery", "Victoria and Albert Museum"],
            "food": ["Borough Market", "Afternoon Tea", "East End Food Tour"],
            "history": ["Tower of London", "Westminster Abbey", "Buckingham Palace"],
            "nature": ["Hyde Park", "Kew Gardens", "Thames Path Walk"]
        }
    },
    "Tokyo": {
        "image": "https://images.unsplash.com/photo-1542051841857-5f90071e7989",
        "activities": {
            "art": ["Mori Art Museum", "TeamLab Planets", "Edo-Tokyo Museum"],
            "food": ["Tsukiji Fish Market", "Ramen Tasting", "Izakaya Hopping"],
            "history": ["Senso-ji Temple", "Meiji Shrine", "Imperial Palace"],
            "nature": ["Shinjuku Gyoen", "Ueno Park", "Mount Takao Hike"]
        }
    }
}

# Fallback for unknown destinations
DEFAULT_DESTINATION = {
    "image": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325",
    "activities": {
        "art": ["Local Art Museum", "Street Art Tour", "Gallery Visits"],
        "food": ["Food Market Tour", "Cooking Class", "Local Restaurant Crawl"],
        "history": ["Historical Walking Tour", "Old Town Exploration", "Landmark Visits"],
        "nature": ["City Park", "Botanical Gardens", "Scenic Walk"]
    }
}

# Enhanced input parsing functions
def parse_destination(text):
    text_lower = text.lower()
    for city in DESTINATION_DATA.keys():
        if city.lower() in text_lower:
            return city
    # Try to match partial names
    partial_matches = {
        "par": "Paris",
        "lon": "London",
        "tok": "Tokyo"
    }
    for partial, full in partial_matches.items():
        if partial in text_lower:
            return full
    return None

def parse_dates(text):
    # Try different date patterns
    patterns = [
        (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", "%m/%d/%Y"),  # MM/DD/YYYY
        (r"\b(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\b", "%d %b %Y"),
        (r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s*-\s*(\d{1,2})\b", "%b %d-%d")
    ]
    
    text_lower = text.lower()
    for pattern, fmt in patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if fmt == "%b %d-%d":
                    month = match.group(1)
                    start_day = match.group(2)
                    end_day = match.group(3)
                    year = datetime.now().year
                    return f"{month[:3].title()} {start_day}-{end_day}, {year}"
                else:
                    return match.group(0).title()
            except:
                continue
    
    # Relative dates
    if "next week" in text_lower:
        today = datetime.now()
        next_week = today + timedelta(days=7)
        return f"{today.strftime('%b %d')} - {next_week.strftime('%b %d, %Y')}"
    elif "next month" in text_lower:
        today = datetime.now()
        next_month = today + timedelta(days=30)
        return f"{today.strftime('%b %d')} - {next_month.strftime('%b %d, %Y')}"
    
    return "Within next month"  # Final fallback

def parse_budget(text):
    text_lower = text.lower()
    budget_keywords = {
        "luxury": ["luxury", "high-end", "expensive", "5-star"],
        "moderate": ["moderate", "mid-range", "average"],
        "budget": ["budget", "cheap", "affordable", "low-cost"]
    }
    for level, keywords in budget_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return level
    return "moderate"

def parse_interests(text):
    interest_map = {
        "art": ["art", "museum", "gallery", "painting", "sculpture"],
        "food": ["food", "restaurant", "cuisine", "dining", "eat", "drink"],
        "history": ["history", "historical", "monument", "landmark", "ancient"],
        "nature": ["nature", "park", "garden", "hike", "outdoor", "walk"],
        "shopping": ["shop", "mall", "market", "boutique", "store"],
        "adventure": ["adventure", "hiking", "trek", "explore", "active"]
    }
    
    interests = []
    text_lower = text.lower()
    for interest, keywords in interest_map.items():
        if any(keyword in text_lower for keyword in keywords):
            interests.append(interest)
    return interests if interests else ["art", "food"]

# Helper function for default interests
def get_default_interests(prefs):
    if "interests" in prefs:
        return [i.capitalize() for i in prefs["interests"]]
    return []

# Header with Dynamic Image
st.markdown('<div class="title">AI-Powered Travel Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Let\'s craft your dream trip with a personalized itinerary!</div>', unsafe_allow_html=True)

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
        user_input = st.text_area(
            "Share your trip details in any format:",
            height=150,
            placeholder="e.g., 'Visiting Paris from NY June 1-7, love art and good food with moderate budget' or 'Weekend in London for shopping'"
        )
        submit_button = st.form_submit_button(label="Plan My Trip")
    
    if submit_button and user_input:
        prefs = {
            "raw_input": user_input,
            "destination": parse_destination(user_input),
            "dates": parse_dates(user_input),
            "budget": parse_budget(user_input),
            "interests": parse_interests(user_input)
        }
        
        # Detect origin
        origin_match = re.search(
            r"(from|flying from|departing from|traveling from)\s+([a-zA-Z\s]+)", 
            user_input, 
            re.IGNORECASE
        )
        if origin_match:
            prefs["start"] = origin_match.group(2).strip().title()
        
        # Handle cases where destination isn't specified
        if not prefs["destination"]:
            prefs["destination"] = random.choice(list(DESTINATION_DATA.keys()))
            prefs["auto_selected"] = True
        
        st.session_state.preferences = prefs
        st.session_state.stage = "refine_preferences"
        st.session_state.scroll_to = "step2"
        st.rerun()

# Stage 2: Refine Preferences
elif st.session_state.stage == "refine_preferences":
    prefs = st.session_state.preferences
    st.markdown('<div class="section-header" id="step2">Step 2: Refine Your Preferences</div>', unsafe_allow_html=True)
    
    # Get destination data or use default
    dest_data = DESTINATION_DATA.get(prefs.get("destination"), DEFAULT_DESTINATION)
    image_url = dest_data["image"]
    
    # Display destination image
    st.markdown(f"""
        <div class="image-container" style="background-image: url('{image_url}');">
            <div class="image-overlay">{prefs.get('destination', 'Your Destination')} Awaits!</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Show detected preferences
    st.write("### Here's what I understood:")
    cols = st.columns(4)
    cols[0].markdown(f"**Destination:** {prefs.get('destination', 'Not specified')}")
    cols[1].markdown(f"**Dates:** {prefs.get('dates', 'Not specified')}")
    cols[2].markdown(f"**Budget:** {prefs.get('budget', 'Not specified').title()}")
    cols[3].markdown(f"**Interests:** {', '.join(prefs.get('interests', []))}")
    
    if prefs.get("auto_selected"):
        st.warning("I couldn't detect your destination, so I selected one for you. Feel free to change it below!")
    
    # Allow refinement
    with st.form(key="refine_form"):
        st.write("### Adjust as needed:")
        
        new_dest = st.selectbox(
            "Destination:",
            list(DESTINATION_DATA.keys()),
            index=list(DESTINATION_DATA.keys()).index(prefs["destination"]) if prefs["destination"] in DESTINATION_DATA else 0
        )
        
        col1, col2 = st.columns(2)
        new_dates = col1.text_input("Travel Dates:", value=prefs["dates"])
        new_budget = col2.selectbox(
            "Budget Level:",
            ["Budget", "Moderate", "Luxury"],
            index=["budget", "moderate", "luxury"].index(prefs["budget"])
        )
        
        interest_options = ["Art", "Food", "History", "Nature", "Shopping", "Adventure"]
        default_interests = get_default_interests(prefs)
        new_interests = st.multiselect(
            "Your Interests:",
            interest_options,
            default=default_interests
        )
        
        confirm_button = st.form_submit_button("Confirm Preferences")
    
    if confirm_button:
        st.session_state.preferences = {
            "destination": new_dest,
            "dates": new_dates,
            "budget": new_budget.lower(),
            "interests": [i.lower() for i in new_interests],
            "start": prefs.get("start", "Not specified")
        }
        st.session_state.stage = "activity_suggestions"
        st.session_state.scroll_to = "step3"
        st.rerun()

# Stage 3: Activity Suggestions
elif st.session_state.stage == "activity_suggestions":
    prefs = st.session_state.preferences
    st.markdown('<div class="section-header" id="step3">Step 3: Explore Activity Suggestions</div>', unsafe_allow_html=True)
    
    dest_data = DESTINATION_DATA.get(prefs.get("destination"), DEFAULT_DESTINATION)
    image_url = dest_data["image"]
    
    st.markdown(f"""
        <div class="image-container" style="background-image: url('{image_url}');">
            <div class="image-overlay">Discover {prefs.get('destination', 'Your Destination')}</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("### Based on your preferences, here are some great activities:")
    
    # Generate activity suggestions
    activities = []
    for interest in prefs.get("interests", ["art", "food"]):
        if interest in dest_data["activities"]:
            activities.extend(dest_data["activities"][interest])
    
    # Ensure we have enough activities
    if len(activities) < 5:
        all_activities = []
        for interest_acts in dest_data["activities"].values():
            all_activities.extend(interest_acts)
        activities.extend(random.sample(all_activities, min(5 - len(activities), len(all_activities))))
    
    # Display activities with tags
    for i, activity in enumerate(activities[:7]):  # Show max 7 activities
        related_interests = [
            interest for interest in prefs.get("interests", []) 
            if any(act.lower() in activity.lower() for act in dest_data["activities"].get(interest, []))
        ]
        
        tags = " ".join([f'<span class="tag">{interest.capitalize()}</span>' for interest in related_interests[:2]])
        st.markdown(f"""
            <div class="suggestion-box">
                <strong>{i+1}. {activity}</strong><br>
                {tags}
            </div>
        """, unsafe_allow_html=True)
    
    with st.form(key="approve_activities_form"):
        st.write("### Ready to create your itinerary?")
        approve_button = st.form_submit_button("Create My Itinerary")
    
    if approve_button:
        st.session_state.activities = activities
        st.session_state.stage = "itinerary_generation"
        st.session_state.scroll_to = "step4"
        st.rerun()

# Stage 4: Itinerary Generation
elif st.session_state.stage == "itinerary_generation":
    prefs = st.session_state.preferences
    activities = st.session_state.activities
    
    st.markdown('<div class="section-header" id="step4">Step 4: Your Personalized Itinerary</div>', unsafe_allow_html=True)
    st.write(f"### Here's your customized {prefs.get('destination', 'trip')} itinerary:")
    
    # Parse dates to determine duration
    try:
        if "-" in prefs["dates"]:
            date_parts = re.split(r"\s*-\s*", prefs["dates"])
            if len(date_parts) == 2:
                start_date = datetime.strptime(date_parts[0] + " " + date_parts[1].split(",")[-1].strip(), "%b %d %Y")
                end_date = datetime.strptime(date_parts[1].replace(",", ""), "%b %d %Y")
                num_days = (end_date - start_date).days + 1
            else:
                num_days = 5  # Default
        else:
            num_days = 3 if "weekend" in prefs["dates"].lower() else 7
    except:
        num_days = 5
    
    # Distribute activities across days
    daily_activities = {}
    for i in range(min(num_days, 7)):  # Max 7 days
        day_num = i + 1
        daily_activities[day_num] = []
        # Try to include at least one activity per interest
        for interest in prefs.get("interests", []):
            matching_acts = [act for act in activities if interest.lower() in act.lower()]
            if matching_acts and len(daily_activities[day_num]) < 2:
                daily_activities[day_num].append(random.choice(matching_acts))
        # Fill remaining slots
        while len(daily_activities[day_num]) < 2 and activities:
            act = random.choice(activities)
            if act not in daily_activities[day_num]:
                daily_activities[day_num].append(act)
    
    # Generate itinerary cards
    for day_num, day_activities in daily_activities.items():
        day_title = f"Day {day_num}"
        if day_num == 1:
            day_title += " - Arrival"
        elif day_num == num_days:
            day_title += " - Departure"
        
        activities_html = "<br>- " + "<br>- ".join(day_activities)
        
        st.markdown(f"""
            <div class="itinerary-card">
                <i class="fas fa-calendar-day"></i> <strong>{day_title}</strong>
                {activities_html}
            </div>
        """, unsafe_allow_html=True)
    
    # Final actions
    with st.form(key="final_actions_form"):
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("Save Itinerary")
        with col2:
            start_over_button = st.form_submit_button("Plan Another Trip")
        
        if save_button:
            st.success("Itinerary saved! Check your email for a copy.")
        if start_over_button:
            st.session_state.stage = "input_refinement"
            st.session_state.preferences = {}
            st.session_state.activities = []
            st.session_state.scroll_to = "step1"
            st.rerun()

# Footer
st.markdown("---")
st.write("Powered by Streamlit | Designed for your travel dreams!")
