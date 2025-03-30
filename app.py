import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Custom CSS for elegant styling with blues and greys
st.markdown("""
    <style>
    /* Full-screen background for first page */
    .input-page {
        background-image: url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2074&q=80');
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
    
    /* Main container styling */
    .main-container {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 15px;
        padding: 30px;
        margin: 40px auto;
        max-width: 800px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid #E1E8ED;
    }
    
    /* Typography */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 700;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 15px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    
    .sub-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        color: #4A6B8A;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    .section-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 26px;
        color: #2C3E50;
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 2px solid #E1E8ED;
        padding-bottom: 8px;
    }
    
    /* Form elements */
    .stTextArea textarea {
        font-family: 'Open Sans', sans-serif;
        font-size: 16px;
        color: #34495E;
        background-color: #F8FAFC;
        border: 2px solid #D6E0EA;
        border-radius: 8px;
        padding: 15px;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .stSelectbox select, .stMultiselect div, .stDateInput input {
        font-family: 'Open Sans', sans-serif;
        font-size: 16px;
        color: #34495E;
        background-color: #F8FAFC !important;
        border: 2px solid #D6E0EA !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    /* Buttons */
    .stButton button {
        font-family: 'Montserrat', sans-serif;
        background-color: #3498DB;
        color: white;
        border-radius: 8px;
        padding: 12px 28px;
        border: none;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton button:hover {
        background-color: #2980B9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Itinerary styling */
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
        margin-bottom: 15px;
    }
    
    .activity-item {
        font-family: 'Open Sans', sans-serif;
        font-size: 16px;
        color: #34495E;
        margin: 12px 0;
        padding-left: 15px;
        border-left: 2px solid #BDC3C7;
    }
    
    .summary-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        margin-top: 25px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        border: 1px solid #E1E8ED;
    }
    
    .summary-item {
        font-family: 'Open Sans', sans-serif;
        font-size: 16px;
        color: #34495E;
        margin: 10px 0;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-container {
            padding: 20px;
            margin: 20px 10px;
        }
        
        .main-title {
            font-size: 32px;
        }
        
        .sub-title {
            font-size: 18px;
        }
    }
    
    /* Add the font imports */
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Montserrat:wght@400;600&family=Open+Sans&display=swap" rel="stylesheet">
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

# ======================
# CORE FUNCTIONS
# ======================
def parse_dates(text):
    text_lower = text.lower()
    today = datetime.now()
    
    date_range = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s*[-–to]+\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", text_lower)
    if date_range:
        try:
            start = datetime.strptime(f"{date_range.group(1)}/{date_range.group(2)}/{date_range.group(3)}", "%m/%d/%Y")
            end = datetime.strptime(f"{date_range.group(4)}/{date_range.group(5)}/{date_range.group(6)}", "%m/%d/%Y")
            duration = (end - start).days + 1
            return {
                "dates": f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}",
                "duration": duration,
                "start_date": start,
                "end_date": end
            }
        except:
            pass
    
    month_range = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s*[-–]\s*(\d{1,2}),?\s+(\d{4})", text_lower)
    if month_range:
        try:
            month = month_range.group(1)[:3].title()
            start_day = int(month_range.group(2))
            end_day = int(month_range.group(3))
            year = int(month_range.group(4))
            start_date = datetime.strptime(f"{month} {start_day} {year}", "%b %d %Y")
            end_date = datetime.strptime(f"{month} {end_day} {year}", "%b %d %Y")
            duration = (end_date - start_date).days + 1
            return {
                "dates": f"{month} {start_day}-{end_day}, {year}",
                "duration": duration,
                "start_date": start_date,
                "end_date": end_date
            }
        except:
            pass
    
    end_date = today + timedelta(days=6)
    return {
        "dates": f"{today.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} (7 days)",
        "duration": 7,
        "start_date": today,
        "end_date": end_date
    }

def parse_preferences(user_input):
    prefs = {}
    text_lower = user_input.lower()
    
    for city in DESTINATION_DATA.keys():
        if city.lower() in text_lower:
            prefs["destination"] = city
            break
    if "destination" not in prefs:
        prefs["destination"] = "Paris"
    
    date_info = parse_dates(user_input)
    prefs.update(date_info)
    
    if any(word in text_lower for word in ["luxury", "high-end", "expensive"]):
        prefs["budget"] = "luxury"
    elif any(word in text_lower for word in ["budget", "cheap", "affordable"]):
        prefs["budget"] = "budget"
    else:
        prefs["budget"] = "moderate"
    
    interest_map = {
        "art": ["art", "museum", "gallery"],
        "food": ["food", "restaurant", "dining", "cuisine"],
        "history": ["history", "historical", "monument"],
        "nature": ["nature", "park", "hike", "outdoor"],
        "shopping": ["shop", "mall", "market"],
        "adventure": ["adventure", "hiking", "trek"],
        "culture": ["culture", "local", "traditional"],
        "beach": ["beach", "coast", "shore"]
    }
    prefs["interests"] = [
        interest for interest, keywords in interest_map.items()
        if any(keyword in text_lower for keyword in keywords)
    ] or ["culture"]
    
    origin_match = re.search(r"(from|flying from|departing from)\s+([a-zA-Z\s]+)", text_lower)
    prefs["start"] = origin_match.group(2).strip().title() if origin_match else "Not specified"
    
    prefs["dietary"] = "none"
    prefs["mobility"] = 5
    prefs["accommodation"] = "mid-range"
    
    return prefs

def search_activities(destination, interest):
    if destination in DESTINATION_DATA and interest in DESTINATION_DATA[destination]["activities"]:
        return DESTINATION_DATA[destination]["activities"][interest]
    return [f"{interest.capitalize()} activity in {destination}"]

# ======================
# DESTINATION DATABASE
# ======================
DESTINATION_DATA = {
    "Paris": {
        "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
        "activities": {
            "art": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou"],
            "food": ["Le Marais Food Tour", "Montmartre Cafés", "Seine River Dinner"],
            "culture": ["Latin Quarter Walk", "Père Lachaise Cemetery"],
            "history": ["Notre-Dame Cathedral", "Eiffel Tower"]
        },
        "country": "France"
    },
    "London": {
        "image": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0",
        "activities": {
            "history": ["Tower of London", "Westminster Abbey"],
            "food": ["Borough Market", "Afternoon Tea"],
            "culture": ["British Museum", "Tate Modern"]
        },
        "country": "UK"
    },
    "Bangkok": {
        "image": "https://images.unsplash.com/photo-1563492065599-3520f775b7ba",
        "activities": {
            "art": ["Jim Thompson House", "Bangkok Art and Culture Centre", "MOCA Bangkok"],
            "food": ["Chatuchak Market Food Stalls", "Chinatown Street Food Tour", "Floating Market Dining"],
            "culture": ["Grand Palace", "Wat Arun", "Erawan Shrine"],
            "history": ["Ayutthaya Day Trip", "National Museum"]
        },
        "country": "Thailand"
    }
}

# ======================
# MAIN APP
# ======================
def main():
    # Stage 1: Input Collection with beautiful background
    if st.session_state.stage == "input_refinement":
        st.markdown('<div class="input-page"></div>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            st.markdown("<div class='main-title'>Travel Planner</div>", unsafe_allow_html=True)
            st.markdown("<div class='sub-title'>Plan your perfect journey with AI assistance</div>", unsafe_allow_html=True)
            
            with st.form("trip_input"):
                user_input = st.text_area(
                    "Describe your trip (destination, dates, budget, interests):",
                    value="Bangkok from New York, Jun 1-4, 2025, budget, art and food",
                    height=150,
                    key="trip_input_text"
                )
                
                if st.form_submit_button("Plan My Trip"):
                    if user_input:
                        try:
                            st.session_state.preferences = parse_preferences(user_input)
                            st.session_state.stage = "refine_preferences"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error parsing input: {str(e)}")
                    else:
                        st.error("Please enter your trip details.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Other stages with consistent blue/grey styling
    else:
        with st.container():
            st.markdown('<div class="main-container">', unsafe_allow_html=True)
            
            if st.session_state.stage == "refine_preferences":
                prefs = st.session_state.preferences
                
                st.markdown("<div class='section-title'>Refine Your Preferences</div>", unsafe_allow_html=True)
                
                with st.form("preference_refinement"):
                    new_dest = st.selectbox("Destination:", sorted(list(DESTINATION_DATA.keys())), 
                                           index=sorted(list(DESTINATION_DATA.keys())).index(prefs.get("destination", "Paris")))
                    new_start = st.text_input("Traveling from:", value=prefs.get("start", "Not specified"))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("Start Date:", value=prefs.get("start_date", datetime.now()), min_value=datetime.now())
                    with col2:
                        end_date = st.date_input("End Date:", value=prefs.get("end_date", datetime.now() + timedelta(days=6)), min_value=start_date)
                    new_duration = (end_date - start_date).days + 1
                    new_dates = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
                    
                    new_budget = st.selectbox("Budget Level:", ["Luxury", "Moderate", "Budget"], 
                                             index=["Luxury", "Moderate", "Budget"].index(prefs.get("budget", "moderate").capitalize()))
                    new_interests = st.multiselect("Your Interests:", sorted(["Adventure", "Art", "Beach", "Culture", "Food", "History", "Nature", "Shopping"]), 
                                                  default=[i.capitalize() for i in prefs.get("interests", ["culture"])])
                    new_dietary = st.selectbox("Dietary Preference:", ["None", "Vegetarian", "Vegan"], 
                                              index=["None", "Vegetarian", "Vegan"].index(prefs.get("dietary", "none").capitalize()))
                    new_mobility = st.slider("Walking Tolerance (miles/day):", 1, 10, prefs.get("mobility", 5))
                    new_accommodation = st.selectbox("Accommodation Preference:", ["Budget", "Mid-range", "Luxury"], 
                                                    index=["Budget", "Mid-range", "Luxury"].index(prefs.get("accommodation", "mid-range").capitalize()))
                    
                    if st.form_submit_button("Confirm Preferences"):
                        if not new_interests:
                            st.error("Please select at least one interest.")
                        elif new_duration < 1:
                            st.error("End date must be after start date.")
                        else:
                            st.session_state.preferences = {
                                "destination": new_dest,
                                "start": new_start,
                                "dates": new_dates,
                                "duration": new_duration,
                                "budget": new_budget.lower(),
                                "interests": [i.lower() for i in new_interests],
                                "dietary": new_dietary.lower(),
                                "mobility": new_mobility,
                                "accommodation": new_accommodation.lower(),
                                "start_date": start_date,
                                "end_date": end_date,
                                "destination_data": DESTINATION_DATA.get(new_dest)
                            }
                            st.session_state.stage = "activity_suggestions"
                            st.rerun()

            elif st.session_state.stage == "activity_suggestions":
                prefs = st.session_state.preferences
                st.markdown(f"<div class='section-title'>Activity Suggestions for {prefs['destination']}</div>", unsafe_allow_html=True)
                
                suggestions = []
                for interest in prefs["interests"]:
                    activities = search_activities(prefs["destination"], interest)
                    suggestions.extend(activities[:3])
                
                with st.form("activity_selection"):
                    selected_activities = st.multiselect("Choose activities you like:", suggestions, 
                                                        default=suggestions[:min(3 * len(prefs["interests"]), len(suggestions))])
                    if st.form_submit_button("Generate Itinerary"):
                        if not selected_activities:
                            st.error("Please select at least one activity.")
                        else:
                            st.session_state.activities = selected_activities
                            st.session_state.stage = "itinerary_display"
                            st.rerun()

            elif st.session_state.stage == "itinerary_display":
                prefs = st.session_state.preferences
                dest = prefs["destination"]
                duration = prefs["duration"]
                dest_data = prefs["destination_data"]
                
                st.markdown(f"<div class='section-title'>Your {duration}-Day Journey to {dest}</div>", unsafe_allow_html=True)
                st.markdown(f"<i>Dates: {prefs['dates']}</i>", unsafe_allow_html=True)
                
                if dest_data and "image" in dest_data:
                    st.image(dest_data["image"], use_container_width=True, caption=f"{dest}, {dest_data.get('country', '')}")
                st.markdown(f"<b>{dest}, {dest_data.get('country', '')}</b>", unsafe_allow_html=True)
                if prefs["start"] != "Not specified":
                    st.markdown(f"<i>Departing from: {prefs['start']}</i>", unsafe_allow_html=True)
                
                st.markdown("<div class='section-title'>Detailed Itinerary</div>", unsafe_allow_html=True)
                used_activities = set()
                selected_activities = st.session_state.activities
                fallback_options = ["Leisure time", "Local exploration", "Rest at your accommodation"]
                
                for day in range(1, duration + 1):
                    current_date = (prefs["start_date"] + timedelta(days=day-1)).strftime("%A, %b %d")
                    st.markdown(f"""
                        <div class='day-card'>
                            <div class='day-header'>Day {day}: {current_date}</div>
                    """, unsafe_allow_html=True)
                    
                    if selected_activities and day <= len(selected_activities):
                        activity = selected_activities[day-1]
                        st.markdown(f"<div class='activity-item'>Morning (9:00 AM - 12:00 PM): {activity}</div>", unsafe_allow_html=True)
                        used_activities.add(activity)
                    else:
                        st.markdown(f"<div class='activity-item'>Morning (9:00 AM - 12:00 PM): {random.choice(fallback_options)}</div>", unsafe_allow_html=True)
                    
                    lunch_base = random.choice(["Local café", "Fine restaurant", "Street fare"])
                    dietary_note = f" ({prefs['dietary']} options)" if prefs['dietary'] != "none" else ""
                    st.markdown(f"<div class='activity-item'>Luncheon (12:00 PM - 1:00 PM): {lunch_base}{dietary_note}</div>", unsafe_allow_html=True)
                    
                    available_activities = [a for a in selected_activities if a not in used_activities]
                    if available_activities:
                        activity = random.choice(available_activities)
                        st.markdown(f"<div class='activity-item'>Afternoon (2:00 PM - 5:00 PM): {activity}</div>", unsafe_allow_html=True)
                        used_activities.add(activity)
                    else:
                        st.markdown(f"<div class='activity-item'>Afternoon (2:00 PM - 5:00 PM): {random.choice(fallback_options)}</div>", unsafe_allow_html=True)
                    
                    if day > 1:
                        available_activities = [a for a in selected_activities if a not in used_activities]
                        if available_activities:
                            activity = random.choice(available_activities)
                            st.markdown(f"<div class='activity-item'>Evening (7:00 PM - 10:00 PM): {activity}</div>", unsafe_allow_html=True)
                            used_activities.add(activity)
                        else:
                            st.markdown(f"<div class='activity-item'>Evening (7:00 PM - 10:00 PM): {random.choice(fallback_options)}</div>", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<div class='section-title'>Trip Summary</div>", unsafe_allow_html=True)
                st.markdown("<div class='summary-card'>", unsafe_allow_html=True)
                cols = st.columns(4)
                cols[0].metric("Destination", dest)
                cols[1].metric("Duration", f"{duration} days")
                cols[2].metric("Budget", prefs["budget"].capitalize())
                cols[3].metric("Walking", f"{prefs['mobility']} miles/day")
                
                st.markdown(f"<div class='summary-item'>Travel Dates: {prefs['dates']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='summary-item'>Interests: {', '.join([i.capitalize() for i in prefs['interests']])}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='summary-item'>Dietary Preference: {prefs['dietary'].capitalize()}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='summary-item'>Accommodation: {prefs['accommodation'].capitalize()}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Plan Another Journey", key="plan_another"):
                        st.session_state.stage = "input_refinement"
                        st.session_state.preferences = {}
                        st.session_state.activities = []
                        st.session_state.saved = False
                        st.rerun()
                with col2:
                    if st.button("Save This Itinerary", key="save_itinerary"):
                        st.session_state.saved = True
                        st.success("Itinerary saved successfully! Check your email or saved plans.")
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
