import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict

# Custom CSS for classic styling
st.markdown("""
    <style>
    .itinerary-header {
        font-family: 'Georgia', serif;
        font-size: 28px;
        font-weight: bold;
        color: #4A2E2A;
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 2px solid #8B5A2B;
        padding-bottom: 5px;
    }
    .subheader {
        font-family: 'Georgia', serif;
        font-size: 20px;
        color: #4A2E2A;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    .day-box {
        background-color: #F5F1E9;
        border: 1px solid #8B5A2B;
        border-radius: 5px;
        padding: 15px;
        margin: 15px 0;
    }
    .day-title {
        font-family: 'Georgia', serif;
        font-size: 18px;
        color: #4A2E2A;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .time-slot {
        font-family: 'Times New Roman', serif;
        font-size: 16px;
        color: #3C2F2F;
        margin: 8px 0;
        padding-left: 10px;
        border-left: 2px solid #A67B5B;
    }
    .summary-box {
        background-color: #FDF6E3;
        border: 1px dashed #8B5A2B;
        border-radius: 5px;
        padding: 15px;
        margin-top: 20px;
    }
    .summary-text {
        font-family: 'Times New Roman', serif;
        font-size: 16px;
        color: #3C2F2F;
        margin: 5px 0;
    }
    .button-style {
        font-family: 'Georgia', serif;
        background-color: #8B5A2B;
        color: white;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        display: block;
        width: 200px;
        margin: 20px auto;
        border: none;
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

# ======================
# CORE FUNCTIONS
# ======================
def parse_dates(text):
    """Enhanced date parsing for multiple formats"""
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
    """Parse user preferences from input text"""
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
    """Mock web search for activities"""
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
    }
}

# ======================
# MAIN APP
# ======================
def main():
    st.title("Travel Planner")
    
    if st.session_state.stage == "input_refinement":
        with st.form("trip_input"):
            st.subheader("Plan Your Journey")
            user_input = st.text_area(
                "Describe your trip (e.g., destination, dates, budget, interests):",
                value="Paris from New York, Jun 1-4, 2025, moderate budget, art and food",
                height=150
            )
            
            if st.form_submit_button("Plan My Trip") and user_input:
                try:
                    st.session_state.preferences = parse_preferences(user_input)
                    st.session_state.stage = "refine_preferences"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error parsing input: {str(e)}")

    elif st.session_state.stage == "refine_preferences":
        prefs = st.session_state.preferences
        
        st.subheader("Refine Your Preferences")
        
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
        st.subheader(f"Activity Suggestions for {prefs['destination']}")
        
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
        
        # Classic header
        st.markdown(f"<div class='itinerary-header'>Your {duration}-Day Journey to {dest}</div>", unsafe_allow_html=True)
        st.markdown(f"<i>Dates: {prefs['dates']}</i>", unsafe_allow_html=True)
        
        if dest_data and "image" in dest_data:
            st.image(dest_data["image"], use_container_width=True, caption=f"{dest}, {dest_data.get('country', '')}")
        st.markdown(f"<b>{dest}, {dest_data.get('country', '')}</b>", unsafe_allow_html=True)
        if prefs["start"] != "Not specified":
            st.markdown(f"<i>Departing from: {prefs['start']}</i>", unsafe_allow_html=True)
        
        # Itinerary with classic styling
        st.markdown("<div class='subheader'>Detailed Itinerary</div>", unsafe_allow_html=True)
        used_activities = set()
        selected_activities = st.session_state.activities
        fallback_options = ["Leisure time", "Local exploration", "Rest at your accommodation"]
        
        for day in range(1, duration + 1):
Fh            current_date = (prefs["start_date"] + timedelta(days=day-1)).strftime("%A, %b %d")
            st.markdown(f"""
                <div class='day-box'>
                    <div class='day-title'>Day {day}: {current_date}</div>
            """, unsafe_allow_html=True)
            
            if selected_activities and day <= len(selected_activities):
                activity = selected_activities[day-1]
                st.markdown(f"<div class='time-slot'>Morning (9:00 AM - 12:00 PM): {activity}</div>", unsafe_allow_html=True)
                used_activities.add(activity)
            else:
                st.markdown(f"<div class='time-slot'>Morning (9:00 AM - 12:00 PM): {random.choice(fallback_options)}</div>", unsafe_allow_html=True)
            
            lunch_base = random.choice(["Local café", "Fine restaurant", "Street fare"])
            dietary_note = f" ({prefs['dietary']} options)" if prefs['dietary'] != "none" else ""
            st.markdown(f"<div class='time-slot'>Luncheon (12:00 PM - 1:00 PM): {lunch_base}{dietary_note}</div>", unsafe_allow_html=True)
            
            available_activities = [a for a in selected_activities if a not in used_activities]
            if available_activities:
                activity = random.choice(available_activities)
                st.markdown(f"<div class='time-slot'>Afternoon (2:00 PM - 5:00 PM): {activity}</div>", unsafe_allow_html=True)
                used_activities.add(activity)
            else:
                st.markdown(f"<div class='time-slot'>Afternoon (2:00 PM - 5:00 PM): {random.choice(fallback_options)}</div>", unsafe_allow_html=True)
            
            if day > 1:
                available_activities = [a for a in selected_activities if a not in used_activities]
                if available_activities:
                    activity = random.choice(available_activities)
                    st.markdown(f"<div class='time-slot'>Evening (7:00 PM - 10:00 PM): {activity}</div>", unsafe_allow_html=True)
                    used_activities.add(activity)
                else:
                    st.markdown(f"<div class='time-slot'>Evening (7:00 PM - 10:00 PM): {random.choice(fallback_options)}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Summary with classic styling
        st.markdown("<div class='subheader'>Trip Summary</div>", unsafe_allow_html=True)
        st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
        cols = st.columns(4)
        cols[0].metric("Destination", dest)
        cols[1].metric("Duration", f"{duration} days")
        cols[2].metric("Budget", prefs["budget"].capitalize())
        cols[3].metric("Walking", f"{prefs['mobility']} miles/day")
        
        st.markdown(f"<div class='summary-text'>Travel Dates: {prefs['dates']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>Interests: {', '.join([i.capitalize() for i in prefs['interests']])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>Dietary Preference: {prefs['dietary'].capitalize()}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='summary-text'>Accommodation: {prefs['accommodation'].capitalize()}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Plan Another Journey", key="plan_another"):
            st.session_state.stage = "input_refinement"
            st.session_state.preferences = {}
            st.session_state.activities = []
            st.rerun()

if __name__ == "__main__":
    main()
