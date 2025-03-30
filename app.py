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
    """Enhanced date parsing for multiple formats"""
    text_lower = text.lower()
    today = datetime.now()
    
    # Specific date ranges (e.g., Jun 1–4, 2025 or 06/01/2025 - 06/04/2025)
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
    
    # Month Day - Day, Year (e.g., Jun 1-4, 2025)
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
    
    # Fallback: 7-day trip starting today
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
    
    # Destination
    for city in DESTINATION_DATA.keys():
        if city.lower() in text_lower:
            prefs["destination"] = city
            break
    if "destination" not in prefs:
        prefs["destination"] = "Paris"  # Default
    
    # Dates and Duration
    date_info = parse_dates(user_input)
    prefs.update(date_info)
    
    # Budget
    if any(word in text_lower for word in ["luxury", "high-end", "expensive"]):
        prefs["budget"] = "luxury"
    elif any(word in text_lower for word in ["budget", "cheap", "affordable"]):
        prefs["budget"] = "budget"
    else:
        prefs["budget"] = "moderate"
    
    # Interests
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
    ] or ["culture"]  # Default
    
    # Origin
    origin_match = re.search(r"(from|flying from|departing from)\s+([a-zA-Z\s]+)", text_lower)
    prefs["start"] = origin_match.group(2).strip().title() if origin_match else "Not specified"
    
    # Additional preferences (default values)
    prefs["dietary"] = "none"
    prefs["mobility"] = 5  # Miles per day
    prefs["accommodation"] = "mid-range"
    
    return prefs

# Mock web search function
def search_activities(destination, interest):
    """Mock web search for activities"""
    if destination in DESTINATION_DATA and interest in DESTINATION_DATA[destination]["activities"]:
        return DESTINATION_DATA[destination]["activities"][interest]
    return [f"{interest.capitalize()} activity in {destination}"]

# ======================
# DESTINATION DATABASE (Subset for brevity)
# ======================
DESTINATION_DATA = {
    # Europe (8 destinations)
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
    "London": {
        "image": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0",
        "coordinates": (51.5074, -0.1278), "timezone": "Europe/London",
        "activities": {
            "history": ["Tower of London", "Westminster Abbey", "Buckingham Palace"],
            "museums": ["British Museum", "Natural History Museum", "Tate Modern"],
            "food": ["Borough Market", "Afternoon Tea", "East End Food Tour"],
            "parks": ["Hyde Park", "Regent's Park", "Kew Gardens"]
        },
        "country": "UK", "cost_multiplier": 1.4
    },
    "Rome": {
        "image": "https://images.unsplash.com/photo-1552832230-c0197dd311b5",
        "coordinates": (41.9028, 12.4964), "timezone": "Europe/Rome",
        "activities": {
            "history": ["Colosseum", "Roman Forum", "Pantheon", "Palatine Hill"],
            "art": ["Vatican Museums", "Sistine Chapel", "Galleria Borghese"],
            "food": ["Trastevere Food Tour", "Gelato Tasting", "Pasta Making Class"],
            "religion": ["St. Peter's Basilica", "Trevi Fountain", "Spanish Steps"]
        },
        "country": "Italy", "cost_multiplier": 1.2
    },
    "Barcelona": {
        "image": "https://images.unsplash.com/photo-1523531294919-4bcd7c65e216",
        "coordinates": (41.3851, 2.1734), "timezone": "Europe/Madrid",
        "activities": {
            "architecture": ["Sagrada Familia", "Park Güell", "Casa Batlló"],
            "beaches": ["Barceloneta Beach", "Bogatell Beach", "Nova Icaria"],
            "food": ["La Boqueria Market", "Tapas Tour", "Paella Cooking Class"],
            "culture": ["Gothic Quarter", "Picasso Museum", "Flamenco Show"]
        },
        "country": "Spain", "cost_multiplier": 1.1
    },
    "Amsterdam": {
        "image": "https://images.unsplash.com/photo-1512470876302-972faa2aa9a4",
        "coordinates": (52.3676, 4.9041), "timezone": "Europe/Amsterdam",
        "activities": {
            "culture": ["Van Gogh Museum", "Anne Frank House", "Rijksmuseum"],
            "canals": ["Canal Cruise", "Jordaan District Walk", "Houseboat Museum"],
            "history": ["Rembrandt House", "Jewish Historical Museum"],
            "unique": ["Heineken Experience", "Albert Cuyp Market"]
        },
        "country": "Netherlands", "cost_multiplier": 1.2
    },
    "Vienna": {
        "image": "https://images.unsplash.com/photo-1516550893923-42d28e5677af",
        "coordinates": (48.2082, 16.3738), "timezone": "Europe/Vienna",
        "activities": {
            "music": ["Vienna State Opera", "Mozart House", "Strauss Concert"],
            "palaces": ["Schönbrunn Palace", "Hofburg Palace", "Belvedere Palace"],
            "cafes": ["Sachertorte at Hotel Sacher", "Demel Cafe", "Central Cafe"],
            "museums": ["Kunsthistorisches Museum", "Albertina", "Leopold Museum"]
        },
        "country": "Austria", "cost_multiplier": 1.1
    },
    "Prague": {
        "image": "https://images.unsplash.com/photo-1519677100203-a0e668c92439",
        "coordinates": (50.0755, 14.4378), "timezone": "Europe/Prague",
        "activities": {
            "history": ["Prague Castle", "Charles Bridge", "Old Town Square"],
            "culture": ["Astronomical Clock", "Jewish Quarter", "Kafka Museum"],
            "food": ["Beer Tasting", "Trdelník Making", "Traditional Czech Dinner"],
            "views": ["Petrin Tower", "Vltava River Cruise", "Vyšehrad Castle"]
        },
        "country": "Czech Republic", "cost_multiplier": 0.9
    },
    "Istanbul": {
        "image": "https://images.unsplash.com/photo-1527838832700-5059252407fa",
        "coordinates": (41.0082, 28.9784), "timezone": "Europe/Istanbul",
        "activities": {
            "history": ["Hagia Sophia", "Blue Mosque", "Topkapi Palace"],
            "markets": ["Grand Bazaar", "Spice Bazaar", "Arasta Bazaar"],
            "culture": ["Bosphorus Cruise", "Turkish Bath Experience"],
            "food": ["Kebab Tasting", "Baklava Workshop", "Turkish Coffee Reading"]
        },
        "country": "Turkey", "cost_multiplier": 0.8
    },
    "Reykjavik": {
        "image": "https://images.unsplash.com/photo-1529963183134-61a90db47eaf",
        "coordinates": (64.1466, -21.9426), "timezone": "Atlantic/Reykjavik",
        "activities": {
            "nature": ["Blue Lagoon", "Golden Circle", "Northern Lights Tour"],
            "adventure": ["Glacier Hiking", "Whale Watching", "Ice Cave Exploration"],
            "culture": ["Hallgrimskirkja", "Harpa Concert Hall", "National Museum"],
            "unique": ["Volcano Tour", "Geothermal Bakery", "Puffin Watching"]
        },
        "country": "Iceland", "cost_multiplier": 1.5
    },
    # Asia (5 destinations)
    "Tokyo": {
        "image": "https://images.unsplash.com/photo-1542051841857-5f90071e7989",
        "coordinates": (35.6762, 139.6503), "timezone": "Asia/Tokyo",
        "activities": {
            "culture": ["Senso-ji Temple", "Meiji Shrine", "Imperial Palace"],
            "food": ["Tsukiji Fish Market", "Ramen Tasting", "Sushi Making Class"],
            "modern": ["Shibuya Crossing", "TeamLab Planets", "Tokyo Skytree"],
            "nature": ["Shinjuku Gyoen", "Ueno Park", "Mount Takao Hike"]
        },
        "country": "Japan", "cost_multiplier": 1.4
    },
    "Bangkok": {
        "image": "https://images.unsplash.com/photo-1563492065599-3520f775eeed",
        "coordinates": (13.7563, 100.5018), "timezone": "Asia/Bangkok",
        "activities": {
            "temples": ["Grand Palace", "Wat Pho", "Wat Arun"],
            "markets": ["Chatuchak Weekend Market", "Floating Markets"],
            "culture": ["Thai Cooking Class", "Muay Thai Match"],
            "modern": ["Sky Bar", "ICONSIAM Mall", "Mahanakhon Skywalk"]
        },
        "country": "Thailand", "cost_multiplier": 0.7
    },
    "Singapore": {
        "image": "https://images.unsplash.com/photo-1565967511849-76a60a516170",
        "coordinates": (1.3521, 103.8198), "timezone": "Asia/Singapore",
        "activities": {
            "modern": ["Marina Bay Sands", "Gardens by the Bay", "Sentosa Island"],
            "culture": ["Chinatown", "Little India", "Kampong Glam"],
            "food": ["Hawker Centre Tour", "Chili Crab Dinner"],
            "nature": ["Singapore Zoo", "Botanic Gardens"]
        },
        "country": "Singapore", "cost_multiplier": 1.3
    },
    "Bali": {
        "image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4",
        "coordinates": (-8.3405, 115.0920), "timezone": "Asia/Makassar",
        "activities": {
            "temples": ["Tanah Lot", "Uluwatu Temple", "Besakih Temple"],
            "nature": ["Tegallalang Rice Terraces", "Mount Batur Sunrise"],
            "beaches": ["Seminyak", "Nusa Dua", "Padang Padang"],
            "culture": ["Balinese Dance Show", "Silver Jewelry Making"]
        },
        "country": "Indonesia", "cost_multiplier": 0.6
    },
    "Hong Kong": {
        "image": "https://images.unsplash.com/photo-1531259683007-016a7b628fc3",
        "coordinates": (22.3193, 114.1694), "timezone": "Asia/Hong_Kong",
        "activities": {
            "views": ["Victoria Peak", "Star Ferry", "Ngong Ping 360"],
            "culture": ["Tian Tan Buddha", "Wong Tai Sin Temple"],
            "food": ["Dim Sum Tour", "Temple Street Night Market"],
            "shopping": ["Causeway Bay", "Mong Kok Markets"]
        },
        "country": "China", "cost_multiplier": 1.2
    },
    # North America (2 destinations)
    "New York": {
        "image": "https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2",
        "coordinates": (40.7128, -74.0060), "timezone": "America/New_York",
        "activities": {
            "landmarks": ["Statue of Liberty", "Empire State Building", "Times Square"],
            "museums": ["Metropolitan Museum", "MOMA", "Natural History Museum"],
            "food": ["Pizza Tour", "Chinatown Food Crawl", "Bagel Tasting"],
            "culture": ["Broadway Show", "High Line Walk", "5th Avenue Shopping"]
        },
        "country": "USA", "cost_multiplier": 1.5
    },
    "Cancun": {
        "image": "https://images.unsplash.com/photo-1519794206461-cccd885bf209",
        "coordinates": (21.1619, -86.8515), "timezone": "America/Cancun",
        "activities": {
            "beaches": ["Playa Delfines", "Isla Mujeres", "Playa Norte"],
            "ruins": ["Chichen Itza", "Tulum Ruins", "Coba Ruins"],
            "adventure": ["Xcaret Park", "Xel-Ha Park", "Cenote Diving"],
            "nightlife": ["Coco Bongo", "Mandala Beach Club"]
        },
        "country": "Mexico", "cost_multiplier": 0.9
    },
    # Middle East (1 destination)
    "Dubai": {
        "image": "https://images.unsplash.com/photo-1518684079-3c830dcef090",
        "coordinates": (25.2048, 55.2708), "timezone": "Asia/Dubai",
        "activities": {
            "modern": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah"],
            "culture": ["Dubai Creek", "Gold Souk", "Bastakiya Quarter"],
            "desert": ["Desert Safari", "Dune Bashing", "Camel Riding"],
            "luxury": ["Burj Al Arab", "Atlantis Waterpark"]
        },
        "country": "UAE", "cost_multiplier": 1.6
    },
    # Africa (1 destination)
    "Cape Town": {
        "image": "https://images.unsplash.com/photo-1516026672322-bc52d61a60d0",
        "coordinates": (-33.9249, 18.4241), "timezone": "Africa/Johannesburg",
        "activities": {
            "nature": ["Table Mountain", "Cape Point", "Kirstenbosch Gardens"],
            "wine": ["Stellenbosch Wine Tour", "Franschhoek Wine Tram"],
            "history": ["Robben Island", "District Six Museum"],
            "adventure": ["Lion's Head Hike", "Shark Cage Diving"]
        },
        "country": "South Africa", "cost_multiplier": 0.8
    },
    # Oceania (1 destination)
    "Sydney": {
        "image": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9",
        "coordinates": (-33.8688, 151.2093), "timezone": "Australia/Sydney",
        "activities": {
            "landmarks": ["Sydney Opera House", "Harbour Bridge", "Bondi Beach"],
            "nature": ["Blue Mountains", "Taronga Zoo", "Royal Botanic Garden"],
            "food": ["Sydney Fish Market", "Chinatown Food Tour"],
            "culture": ["Art Gallery of NSW", "Darling Harbour"]
        },
        "country": "Australia", "cost_multiplier": 1.3
    },
    # South America (2 destinations)
    "Rio de Janeiro": {
        "image": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325",
        "coordinates": (-22.9068, -43.1729), "timezone": "America/Sao_Paulo",
        "activities": {
            "landmarks": ["Christ the Redeemer", "Sugarloaf Mountain"],
            "beaches": ["Copacabana", "Ipanema", "Leblon"],
            "nature": ["Tijuca Forest", "Botanical Garden"],
            "culture": ["Samba Show", "Favela Tour"]
        },
        "country": "Brazil", "cost_multiplier": 0.9
    },
    "Cairo": {
        "image": "https://images.unsplash.com/photo-1572252009286-268acec5ca0a",
        "coordinates": (30.0444, 31.2357), "timezone": "Africa/Cairo",
        "activities": {
            "pyramids": ["Giza Pyramids", "Sphinx", "Saqqara Pyramid"],
            "museums": ["Egyptian Museum", "Coptic Museum"],
            "culture": ["Khan el-Khalili Bazaar", "Nile Dinner Cruise"],
            "history": ["Dahshur Pyramids", "Memphis Ruins"]
        },
        "country": "Egypt", "cost_multiplier": 0.7
    }
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

    # Stage 2: Preference Refinement
    elif st.session_state.stage == "refine_preferences":
        prefs = st.session_state.preferences
        
        st.subheader("Refine Your Preferences")
        
        with st.form("preference_refinement"):
            # Destination
            dest_options = sorted(list(DESTINATION_DATA.keys()))
            current_dest = prefs.get("destination", "Paris")
            new_dest = st.selectbox(
                "Destination:",
                dest_options,
                index=dest_options.index(current_dest) if current_dest in dest_options else 0
            )
            
            # Origin
            new_start = st.text_input(
                "Traveling from:",
                value=prefs.get("start", "Not specified")
            )
            
            # Calendar-style Dates
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date:",
                    value=prefs.get("start_date", datetime.now()),
                    min_value=datetime.now()
                )
            with col2:
                end_date = st.date_input(
                    "End Date:",
                    value=prefs.get("end_date", datetime.now() + timedelta(days=6)),
                    min_value=start_date
                )
            new_duration = (end_date - start_date).days + 1
            new_dates = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
            
            # Budget
            budget_options = ["Luxury", "Moderate", "Budget"]
            current_budget = prefs.get("budget", "moderate").capitalize()
            new_budget = st.selectbox(
                "Budget Level:",
                budget_options,
                index=budget_options.index(current_budget)
            )
            
            # Interests
            interest_options = sorted(["Adventure", "Art", "Beach", "Culture", "Food", "History", "Nature", "Shopping"])
            current_interests = [i.capitalize() for i in prefs.get("interests", ["culture"])]
            new_interests = st.multiselect(
                "Your Interests:",
                interest_options,
                default=current_interests
            )
            
            # Additional Preferences
            new_dietary = st.selectbox(
                "Dietary Preference:",
                ["None", "Vegetarian", "Vegan"],
                index=["None", "Vegetarian", "Vegan"].index(prefs.get("dietary", "none").capitalize())
            )
            new_mobility = st.slider(
                "Walking Tolerance (miles/day):",
                1, 10, prefs.get("mobility", 5)
            )
            new_accommodation = st.selectbox(
                "Accommodation Preference:",
                ["Budget", "Mid-range", "Luxury"],
                index=["Budget", "Mid-range", "Luxury"].index(prefs.get("accommodation", "mid-range").capitalize())
            )
            
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

    # Stage 3: Activity Suggestions
    elif st.session_state.stage == "activity_suggestions":
        prefs = st.session_state.preferences
        st.subheader(f"Activity Suggestions for {prefs['destination']}")
        
        # Generate suggestions
        suggestions = []
        for interest in prefs["interests"]:
            activities = search_activities(prefs["destination"], interest)
            suggestions.extend(activities[:3])  # Limit to 3 per interest
        
        with st.form("activity_selection"):
            selected_activities = st.multiselect(
                "Choose activities you like:",
                suggestions,
                default=suggestions[:min(3 * len(prefs["interests"]), len(suggestions))]
            )
            if st.form_submit_button("Generate Itinerary"):
                if not selected_activities:
                    st.error("Please select at least one activity.")
                else:
                    st.session_state.activities = selected_activities
                    st.session_state.stage = "itinerary_display"
                    st.rerun()

    # Stage 4: Itinerary Display
    elif st.session_state.stage == "itinerary_display":
        prefs = st.session_state.preferences
        dest = prefs["destination"]
        duration = prefs["duration"]
        dest_data = prefs["destination_data"]
        
        st.header(f"✈️ Your {duration}-Day Trip to {dest}")
        st.subheader(f"📅 {prefs['dates']}")
        
        # Display destination info
        if dest_data and "image" in dest_data:
            st.image(dest_data["image"], use_container_width=True)
        st.markdown(f"**{dest}, {dest_data.get('country', '')}**")
        if prefs["start"] != "Not specified":
            st.markdown(f"*Traveling from: {prefs['start']}*")
        
        # Full itinerary
        st.markdown("---")
        st.subheader("Your Complete Itinerary")
        used_activities = set()
        selected_activities = st.session_state.activities
        fallback_options = ["Free time", "Explore local markets", "Relax at a park"]
        
        for day in range(1, duration + 1):
            current_date = (prefs["start_date"] + timedelta(days=day-1)).strftime("%A, %b %d")
            st.markdown(f"#### Day {day}: {current_date}")
            
            # Morning
            if selected_activities and day <= len(selected_activities):
                activity = selected_activities[day-1]
                st.markdown(f"- **Morning (9AM-12PM):** {activity}")
                used_activities.add(activity)
            else:
                st.markdown(f"- **Morning (9AM-12PM):** {random.choice(fallback_options)}")
            
            # Lunch with dietary consideration
            lunch_base = random.choice(["Local cafe", "Recommended restaurant", "Street food"])
            dietary_note = f" ({prefs['dietary']} options)" if prefs['dietary'] != "none" else ""
            st.markdown(f"- **Lunch (12PM-1PM):** {lunch_base}{dietary_note}")
            
            # Afternoon
            available_activities = [a for a in selected_activities if a not in used_activities]
            if available_activities:
                activity = random.choice(available_activities)
                st.markdown(f"- **Afternoon (2PM-5PM):** {activity}")
                used_activities.add(activity)
            else:
                st.markdown(f"- **Afternoon (2PM-5PM):** {random.choice(fallback_options)}")
            
            # Evening (skip first day)
            if day > 1:
                available_activities = [a for a in selected_activities if a not in used_activities]
                if available_activities:
                    activity = random.choice(available_activities)
                    st.markdown(f"- **Evening (7PM-10PM):** {activity}")
                    used_activities.add(activity)
                else:
                    st.markdown(f"- **Evening (7PM-10PM):** {random.choice(fallback_options)}")
            
            st.markdown("---")
        
        # Trip Summary
        st.markdown("---")
        st.subheader("Trip Summary")
        cols = st.columns(4)
        cols[0].metric("Destination", dest)
        cols[1].metric("Duration", f"{duration} days")
        cols[2].metric("Budget", prefs["budget"].capitalize())
        cols[3].metric("Walking", f"{prefs['mobility']} miles/day")
        
        st.markdown(f"**Travel Dates:** {prefs['dates']}")
        st.markdown(f"**Interests:** {', '.join([i.capitalize() for i in prefs['interests']])}")
        st.markdown(f"**Dietary:** {prefs['dietary'].capitalize()}")
        st.markdown(f"**Accommodation:** {prefs['accommodation'].capitalize()}")
        
        if st.button("Plan Another Trip"):
            st.session_state.stage = "input_refinement"
            st.session_state.preferences = {}
            st.session_state.activities = []
            st.rerun()

if __name__ == "__main__":
    main()
