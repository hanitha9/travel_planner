import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict

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
    """Enhanced date parsing that handles multiple formats"""
    text_lower = text.lower()
    today = datetime.now()
    
    # Specific date ranges (MM/DD/YYYY - MM/DD/YYYY)
    date_range = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s*[-to]+\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", text_lower)
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
    
    # Month Day - Day, Year (Jun 10-15, 2023)
    month_range = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s*[-]\s*(\d{1,2}),?\s+(\d{4})", text_lower)
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
    
    # Duration phrases (5 days, 1 week, weekend)
    duration_map = [
        ("weekend", 2),
        ("long weekend", 3),
        ("one week|1 week|7 days", 7),
        ("two weeks|2 weeks|14 days", 14),
        ("month|30 days", 30)
    ]
    for pattern, days in duration_map:
        if re.search(pattern, text_lower):
            end_date = today + timedelta(days=days-1)
            return {
                "dates": f"{today.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} ({days} days)",
                "duration": days,
                "start_date": today,
                "end_date": end_date
            }
    
    # Specific single dates with duration
    single_date = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s+(?:for|on)\s+(\d+)\s+(day|week)s?", text_lower)
    if single_date:
        try:
            month = single_date.group(1)[:3].title()
            day = int(single_date.group(2))
            duration = int(single_date.group(3))
            if single_date.group(4) == "week":
                duration *= 7
            year = today.year
            start_date = datetime.strptime(f"{month} {day} {year}", "%b %d %Y")
            end_date = start_date + timedelta(days=duration-1)
            return {
                "dates": f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}",
                "duration": duration,
                "start_date": start_date,
                "end_date": end_date
            }
        except:
            pass
    
    # Fallback - assume 7 day trip starting today
    end_date = today + timedelta(days=6)
    return {
        "dates": f"{today.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} (7 days)",
        "duration": 7,
        "start_date": today,
        "end_date": end_date
    }

def parse_preferences(user_input):
    """Parse all user preferences from input text"""
    prefs = {}
    text_lower = user_input.lower()
    
    # Destination
    for city in DESTINATION_DATA.keys():
        if city.lower() in text_lower:
            prefs["destination"] = city
            break
    if "destination" not in prefs:
        prefs["destination"] = random.choice(list(DESTINATION_DATA.keys()))
        prefs["auto_selected"] = True
    
    # Dates and Duration
    date_info = parse_dates(user_input)
    prefs.update(date_info)
    
    # Budget
    if any(word in text_lower for word in ["luxury", "high-end", "expensive", "premium"]):
        prefs["budget"] = "luxury"
    elif any(word in text_lower for word in ["budget", "cheap", "affordable", "economy"]):
        prefs["budget"] = "budget"
    else:
        prefs["budget"] = "moderate"
    
    # Interests
    interest_map = {
        "art": ["art", "museum", "gallery", "painting"],
        "food": ["food", "restaurant", "dining", "cuisine"],
        "history": ["history", "historical", "monument"],
        "nature": ["nature", "park", "hike", "outdoor"],
        "shopping": ["shop", "mall", "market", "boutique"],
        "adventure": ["adventure", "hiking", "trek"],
        "culture": ["culture", "local", "traditional"],
        "beach": ["beach", "coast", "shore"]
    }
    prefs["interests"] = [
        interest for interest, keywords in interest_map.items()
        if any(keyword in text_lower for keyword in keywords)
    ] or ["culture", "food"]  # Default interests
    
    # Origin
    origin_match = re.search(r"(from|flying from|departing from)\s+([a-zA-Z\s]+)", text_lower)
    prefs["start"] = origin_match.group(2).strip().title() if origin_match else "Not specified"
    
    return prefs

# ======================
# DESTINATION DATABASE
# ======================
DESTINATION_DATA = {
    "Paris": {
        "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
        "coordinates": (48.8566, 2.3522), "timezone": "Europe/Paris",
        "activities": {
            "art": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou", "Rodin Museum"],
            "landmarks": ["Eiffel Tower", "Notre-Dame Cathedral", "Arc de Triomphe"],
            "food": ["Le Marais Food Tour", "Montmartre Cafés", "Seine River Dinner"],
            "culture": ["Latin Quarter Walk", "Shakespeare & Company", "Père Lachaise"]
        },
        "country": "France", "cost_multiplier": 1.3
    },
    "New York": {
        "image": "https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2",
        "coordinates": (40.7128, -74.0060), "timezone": "America/New_York",
        "activities": {
            "art": ["Metropolitan Museum", "MOMA", "Guggenheim"],
            "food": ["Pizza Tour", "Chinatown Food Crawl", "Bagel Tasting"],
            "culture": ["Broadway Show", "High Line Walk", "5th Avenue Shopping"]
        },
        "country": "USA", "cost_multiplier": 1.5
    },
    # Other destinations would follow the same format
}

# ======================
# MAIN APP
# ======================
def main():
    st.title("🌍 AI-Powered Travel Planner")
    
    # Stage 1: Input Collection
    if st.session_state.stage == "input_refinement":
        with st.form("trip_input"):
            st.subheader("Plan Your Dream Trip")
            user_input = st.text_area(
                "Describe your trip (destination, dates, interests, budget):",
                value="Paris from New York, June 1–7, 2025, moderate budget, art and food",
                height=150
            )
            
            if st.form_submit_button("Plan My Trip") and user_input:
                try:
                    st.session_state.preferences = parse_preferences(user_input)
                    st.session_state.stage = "refine_preferences"
                    st.rerun()
                except Exception as e:
                    st.error(f"Error parsing your input: {str(e)}")

    # Stage 2: Preference Refinement
    elif st.session_state.stage == "refine_preferences":
        prefs = st.session_state.preferences
        
        st.subheader("Refine Your Preferences")
        
        with st.form("preference_refinement"):
            # Destination
            current_dest = prefs.get("destination", "")
            dest_options = sorted(list(DESTINATION_DATA.keys()))
            current_dest_idx = dest_options.index(current_dest) if current_dest in dest_options else 0
            new_dest = st.selectbox(
                "Destination:",
                dest_options,
                index=current_dest_idx
            )
            
            # Origin
            new_start = st.text_input(
                "Traveling from:",
                value=prefs.get("start", "Not specified")
            )
            
            # Dates and Duration
            col1, col2 = st.columns(2)
            with col1:
                new_dates = st.text_input(
                    "Travel Dates:",
                    value=prefs.get("dates", "")
                )
            with col2:
                duration_options = {
                    "Weekend (2-3 days)": 3,
                    "Short trip (4-5 days)": 5,
                    "One week (7 days)": 7,
                    "Two weeks (14 days)": 14,
                    "Month-long (30 days)": 30,
                    "Custom duration": "custom"
                }
                current_duration = prefs.get("duration", 7)
                new_duration = st.selectbox(
                    "Trip Duration:",
                    list(duration_options.keys()),
                    index=list(duration_options.values()).index(
                        current_duration if current_duration in duration_options.values() else 7
                    )
                )
                
                if new_duration == "Custom duration":
                    custom_days = st.number_input(
                        "Enter number of days:",
                        min_value=1,
                        max_value=60,
                        value=current_duration
                    )
            
            # Budget
            budget_map = {"luxury": "Luxury", "moderate": "Moderate", "budget": "Budget"}
            current_budget = budget_map.get(prefs.get("budget", "moderate"), "Moderate")
            new_budget = st.selectbox(
                "Budget Level:",
                ["Luxury", "Moderate", "Budget"],
                index=["Luxury", "Moderate", "Budget"].index(current_budget)
            )
            
            # Interests
            interest_options = sorted(["Adventure", "Art", "Beach", "Culture", "Food", "History", "Nature", "Shopping"])
            current_interests = [i.capitalize() for i in prefs.get("interests", ["culture", "food"])]
            new_interests = st.multiselect(
                "Your Interests:",
                interest_options,
                default=current_interests
            )
            
            if st.form_submit_button("Create My Itinerary"):
                # Calculate final duration
                final_duration = custom_days if new_duration == "Custom duration" else duration_options[new_duration]
                
                # Update preferences
                st.session_state.preferences = {
                    "destination": new_dest,
                    "start": new_start,
                    "dates": new_dates,
                    "duration": final_duration,
                    "budget": new_budget.lower(),
                    "interests": [i.lower() for i in new_interests],
                    "start_date": prefs.get("start_date", datetime.now()),
                    "end_date": prefs.get("start_date", datetime.now()) + timedelta(days=final_duration-1),
                    "destination_data": DESTINATION_DATA.get(new_dest)
                }
                st.session_state.stage = "itinerary_display"
                st.rerun()

    # Stage 3: Itinerary Display
    elif st.session_state.stage == "itinerary_display":
        prefs = st.session_state.preferences
        dest = prefs.get("destination", "Your Destination")
        duration = prefs.get("duration", 7)
        dest_data = prefs.get("destination_data")
        
        st.header(f"✈️ Your {duration}-Day Trip to {dest}")
        st.subheader(f"📅 {prefs.get('dates', '')}")
        
        # Display destination info
        if dest_data and "image" in dest_data:
            st.image(dest_data["image"], use_container_width=True)
        st.markdown(f"**{dest}, {dest_data.get('country', '') if dest_data else ''}**")
        
        if prefs.get("start", "Not specified") != "Not specified":
            st.markdown(f"*Traveling from: {prefs['start']}*")
        
        # Display full itinerary without expanders
        st.markdown("---")
        st.subheader("Your Complete Itinerary")
        
        # Track used activities to avoid repetition
        used_activities = defaultdict(list)
        
        for day in range(1, duration + 1):
            current_date = (prefs["start_date"] + timedelta(days=day-1)).strftime("%A, %b %d")
            st.markdown(f"#### Day {day}: {current_date}")
            
            # Get available activities for interests
            available_activities = []
            for interest in prefs["interests"]:
                if dest_data and interest in dest_data["activities"]:
                    available_activities.extend([
                        act for act in dest_data["activities"][interest] 
                        if act not in used_activities[interest]
                    ])
            
            # Morning activity (only on odd days for art)
            if "art" in prefs["interests"] and day % 2 == 1 and available_activities:
                art_activities = [
                    act for act in available_activities 
                    if act in dest_data["activities"].get("art", [])
                ]
                if art_activities:
                    activity = random.choice(art_activities)
                    st.markdown(f"- **Morning (9AM-12PM):** {activity}")
                    used_activities["art"].append(activity)
            
            # Lunch
            lunch_options = ["Local cafe", "Recommended restaurant", "Traditional eatery"]
            st.markdown(f"- **Lunch (12PM-1PM):** {random.choice(lunch_options)}")
            
            # Afternoon activity (only on even days for food)
            if "food" in prefs["interests"] and day % 2 == 0 and available_activities:
                food_activities = [
                    act for act in available_activities 
                    if act in dest_data["activities"].get("food", [])
                ]
                if food_activities:
                    activity = random.choice(food_activities)
                    st.markdown(f"- **Afternoon (2PM-5PM):** {activity}")
                    used_activities["food"].append(activity)
            
            # Evening activity (skip first day)
            if day > 1 and "culture" in prefs["interests"] and available_activities:
                culture_activities = [
                    act for act in available_activities 
                    if act in dest_data["activities"].get("culture", [])
                ]
                if culture_activities:
                    activity = random.choice(culture_activities)
                    st.markdown(f"- **Evening (7PM-10PM):** {activity}")
                    used_activities["culture"].append(activity)
            
            st.markdown("---")
        
        # Trip Summary
        st.markdown("---")
        st.subheader("Trip Summary")
        cols = st.columns(3)
        cols[0].metric("Destination", dest)
        cols[1].metric("Duration", f"{duration} days")
        cols[2].metric("Budget Level", prefs.get("budget", "moderate").title())
        
        st.markdown(f"**Travel Dates:** {prefs.get('dates', 'Not specified')}")
        st.markdown(f"**Interests:** {', '.join([i.capitalize() for i in prefs.get('interests', [])])}")
        
        if st.button("Plan Another Trip"):
            st.session_state.stage = "input_refinement"
            st.session_state.preferences = {}
            st.rerun()

if __name__ == "__main__":
    main()
