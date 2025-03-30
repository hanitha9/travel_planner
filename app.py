import streamlit as st
import sys
import subprocess
import math
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict

# ======================
# PACKAGE IMPORT HANDLER
# ======================
class TravelPlannerFeatures:
    def __init__(self):
        self.geopy_available = True
        self.pytz_available = True
        self._initialize_features()
    
    def _initialize_features(self):
        """Handle imports with installation fallback"""
        # Try normal imports first
        try:
            import geopy.distance
            import pytz
            self.geopy = geopy.distance
            self.pytz = pytz
        except ImportError:
            # Attempt to install missing packages
            try:
                subprocess.check_call([
                    sys.executable, 
                    "-m", 
                    "pip", 
                    "install", 
                    "geopy", 
                    "pytz"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import geopy.distance
                import pytz
                self.geopy = geopy.distance
                self.pytz = pytz
            except:
                self.geopy_available = False
                self.pytz_available = False
                st.sidebar.warning(
                    "⚠️ Some map features limited - using fallback calculations. "
                    "For full functionality, please install geopy and pytz."
                )

features = TravelPlannerFeatures()

# ======================
# CORE FUNCTIONS
# ======================
def calculate_distance(coord1, coord2):
    """Robust distance calculation with automatic fallback"""
    if coord1 == (0, 0) or coord2 == (0, 0):
        return "Distance: N/A"
    
    if features.geopy_available:
        try:
            distance_km = features.geopy.distance(coord1, coord2).km
            return f"Distance: {distance_km:.1f} km"
        except:
            features.geopy_available = False
    
    # Haversine formula fallback
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat/2) * math.sin(dLat/2) +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
        math.sin(dLon/2) * math.sin(dLon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return f"Distance (approx): {R * c:.1f} km"

def get_local_time(timezone):
    """Robust timezone handling with fallback"""
    if not features.pytz_available:
        return "Local time: Timezone data unavailable"
    
    try:
        tz = features.pytz.timezone(timezone)
        return f"Local time: {datetime.now(tz).strftime('%I:%M %p')}"
    except:
        return "Local time: N/A"

# ======================
# DESTINATION DATABASE
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

DEFAULT_DESTINATION = {
    "image": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325",
    "coordinates": (0, 0), "timezone": "UTC",
    "activities": {
        "art": ["Local Art Museum", "Street Art Tour"],
        "food": ["Food Market Tour", "Local Restaurant Crawl"],
        "history": ["Historical Walking Tour", "Old Town Exploration"],
        "nature": ["City Park", "Botanical Gardens"]
    },
    "country": "Unknown", "cost_multiplier": 1.0
}

# ======================
# UI COMPONENTS
# ======================
def display_destination_info(destination):
    """Enhanced destination information display"""
    dest_data = DESTINATION_DATA.get(destination, DEFAULT_DESTINATION)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
            <div style="height: 200px; background-image: url('{dest_data["image"]}');
                background-size: cover; background-position: center; border-radius: 10px;">
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        info = f"""
        **{destination}, {dest_data.get('country', '')}**  
        📍 Coordinates: {dest_data.get('coordinates', 'N/A')}  
        {get_local_time(dest_data.get('timezone', ''))}
        """
        if 'start' in st.session_state.preferences:
            origin = st.session_state.preferences['start']
            if origin != "Not specified":
                origin_coords = DESTINATION_DATA.get(origin, {}).get('coordinates', (0,0))
                dest_coords = dest_data.get('coordinates', (0,0))
                info += f"\n✈️ From {origin}: {calculate_distance(origin_coords, dest_coords)}"
        
        st.markdown(info)

def activity_card(activity, cost, time, distance):
    """Consistent activity display card"""
    st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; 
            background-color: #f8f9fa; margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1)">
            <strong>{activity}</strong><br>
            <span style="color: #28a745;">💰 ${cost}</span> | 
            <span style="color: #fd7e14;">⏰ {time}</span> | 
            <span style="color: #6f42c1;">📏 {distance}</span>
        </div>
    """, unsafe_allow_html=True)

# ======================
# MAIN APP
# ======================
def main():
    # Initialize session state
    if "stage" not in st.session_state:
        st.session_state.stage = "input_refinement"
    if "preferences" not in st.session_state:
        st.session_state.preferences = {}
    if "activities" not in st.session_state:
        st.session_state.activities = []
    if "scroll_to" not in st.session_state:
        st.session_state.scroll_to = None

    st.title("🌍 AI-Powered Travel Planner")
    
    # Stage 1: Input Collection
    if st.session_state.stage == "input_refinement":
        with st.form("trip_input"):
            st.subheader("Plan Your Dream Trip")
            user_input = st.text_area(
                "Describe your trip (destination, dates, interests, budget):",
                placeholder="e.g., 'Romantic Paris getaway for 5 days in June, love art and fine dining'"
            )
            
            if st.form_submit_button("Plan My Trip"):
                # Parse user input (simplified example)
                destination = "Paris" if "paris" in user_input.lower() else random.choice(list(DESTINATION_DATA.keys()))
                st.session_state.preferences = {
                    "destination": destination,
                    "dates": "June 10-15, 2023",
                    "interests": ["art", "food"],
                    "budget": "moderate",
                    "start": "New York" if "from new york" in user_input.lower() else "Not specified"
                }
                st.session_state.stage = "refine_preferences"
                st.rerun()
    
    # Stage 2: Preference Refinement
    elif st.session_state.stage == "refine_preferences":
        st.subheader("Refine Your Preferences")
        prefs = st.session_state.preferences
        
        with st.form("preference_refinement"):
            # Destination selection
            current_dest_idx = list(DESTINATION_DATA.keys()).index(prefs["destination"])
            new_dest = st.selectbox(
                "Destination:",
                list(DESTINATION_DATA.keys()),
                index=current_dest_idx
            )
            
            # Date and duration
            col1, col2 = st.columns(2)
            with col1:
                new_dates = st.text_input("Dates:", value=prefs["dates"])
            with col2:
                duration = st.selectbox(
                    "Trip Duration:",
                    ["3 days", "5 days", "7 days", "10 days", "14 days"],
                    index=2
                )
            
            # Budget and interests
            budget_map = {"low": "Budget", "moderate": "Moderate", "high": "Luxury"}
            current_budget = budget_map.get(prefs["budget"], "Moderate")
            new_budget = st.selectbox(
                "Budget Level:",
                ["Budget", "Moderate", "Luxury"],
                index=["Budget", "Moderate", "Luxury"].index(current_budget)
            )
            
            interest_options = ["Adventure", "Art", "Beach", "Culture", "Food", "History", "Nature", "Shopping"]
            new_interests = st.multiselect(
                "Your Interests:",
                interest_options,
                default=[i.capitalize() for i in prefs["interests"]]
            )
            
            if st.form_submit_button("Create Itinerary"):
                st.session_state.preferences = {
                    "destination": new_dest,
                    "dates": new_dates,
                    "duration": duration,
                    "budget": new_budget.lower(),
                    "interests": [i.lower() for i in new_interests],
                    "start": prefs["start"],
                    "destination_data": DESTINATION_DATA.get(new_dest, DEFAULT_DESTINATION)
                }
                st.session_state.stage = "itinerary_generation"
                st.rerun()
    
    # Stage 3: Itinerary Generation
    elif st.session_state.stage == "itinerary_generation":
        prefs = st.session_state.preferences
        dest = prefs.get("destination", "Your Destination")
        
        st.header(f"✈️ Your {dest} Itinerary")
        display_destination_info(dest)
        
        # Sample itinerary generation
        st.subheader(f"{prefs.get('duration', '5-day')} Itinerary Overview")
        
        # Day 1 - Arrival
        st.subheader("Day 1: Arrival")
        activity_card("Airport Transfer", 50, "3:00 PM - 4:00 PM", "25 km")
        activity_card("Welcome Dinner", 80, "7:00 PM - 9:00 PM", "2 km")
        
        # Day 2 - Exploration
        st.subheader("Day 2: City Exploration")
        dest_data = prefs.get("destination_data", DEFAULT_DESTINATION)
        if "art" in prefs["interests"] and "art" in dest_data["activities"]:
            activity = random.choice(dest_data["activities"]["art"])
            activity_card(activity, 25, "10:00 AM - 12:00 PM", "5 km")
        if "food" in prefs["interests"] and "food" in dest_data["activities"]:
            activity = random.choice(dest_data["activities"]["food"])
            activity_card(activity, 60, "1:00 PM - 3:00 PM", "3 km")
        
        # Day 3 - More Activities
        st.subheader("Day 3: Cultural Experiences")
        if "culture" in prefs["interests"] and "culture" in dest_data["activities"]:
            activity = random.choice(dest_data["activities"]["culture"])
            activity_card(activity, 35, "9:30 AM - 11:30 AM", "8 km")
        
        # Add more days as needed based on duration
        
        if st.button("Plan Another Trip"):
            st.session_state.stage = "input_refinement"
            st.session_state.preferences = {}
            st.session_state.activities = []
            st.rerun()

if __name__ == "__main__":
    main()
