import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict

# ======================
# CUSTOM CSS STYLING
# ======================
st.markdown("""
    <style>
    /* NYC Background with overlay */
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Overlay to improve readability */
    .overlay {
        background-color: rgba(255, 255, 255, 0.88);
        border-radius: 15px;
        padding: 40px;
        margin: 5% auto;
        max-width: 800px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        border: 1px solid #e0e0e0;
    }
    
    /* Typography */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 42px;
        font-weight: 700;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 15px;
    }
    
    .sub-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 20px;
        color: #4A6B8A;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* Form elements */
    .stTextArea textarea {
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        color: #34495E;
        background-color: #F8FAFC;
        border: 2px solid #D6E0EA;
        border-radius: 10px;
        padding: 15px;
    }
    
    .stButton button {
        font-family: 'Montserrat', sans-serif;
        background-color: #3498DB;
        color: white;
        border-radius: 10px;
        padding: 12px 30px;
        border: none;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #2980B9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .overlay {
            padding: 25px;
            margin: 10% 5%;
        }
        
        .main-title {
            font-size: 32px;
        }
    }
    
    /* Font imports */
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Montserrat:wght@400;500;600&display=swap" rel="stylesheet">
    </style>
""", unsafe_allow_html=True)

# ======================
# INITIALIZATION
# ======================
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "prefs" not in st.session_state:
    st.session_state.prefs = {}

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
# ======================
# HELPER FUNCTIONS
# ======================
def parse_dates(text):
    text_lower = text.lower()
    today = datetime.now()
    
    # Try to parse date range (Jun 1-4, 2025)
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
    
    # Fallback to 4-day trip starting today
    end_date = today + timedelta(days=3)
    return {
        "dates": f"{today.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}",
        "duration": 4,
        "start_date": today,
        "end_date": end_date
    }

def parse_preferences(user_input):
    prefs = {}
    text_lower = user_input.lower()
    
    # Destination
    for city in DESTINATION_DATA.keys():
        if city.lower() in text_lower:
            prefs["destination"] = city
            break
    if "destination" not in prefs:
        prefs["destination"] = "New York"
    
    # Dates
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
        "food": ["food", "restaurant", "dining"],
        "culture": ["culture", "local", "traditional"],
        "history": ["history", "historical", "monument"]
    }
    prefs["interests"] = [
        interest for interest, keywords in interest_map.items()
        if any(keyword in text_lower for keyword in keywords)
    ] or ["culture"]
    
    # Origin
    origin_match = re.search(r"(from|flying from|departing from)\s+([a-zA-Z\s]+)", text_lower)
    prefs["start"] = origin_match.group(2).strip().title() if origin_match else "Not specified"
    
    return prefs

# ======================
# MAIN APP PAGES
# ======================
def input_page():
    """Initial input page with NYC background"""
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        st.markdown('<div class="overlay">', unsafe_allow_html=True)
        
        st.markdown("<div class='main-title'>New York Travel Planner</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>Plan your perfect NYC adventure</div>", unsafe_allow_html=True)
        
        with st.form("trip_input"):
            user_input = st.text_area(
                "Describe your trip (dates, budget, interests):",
                value="New York, Jun 1-4, 2025, luxury, art and food",
                height=150
            )
            
            if st.form_submit_button("Plan My Trip"):
                if user_input:
                    st.session_state.prefs = parse_preferences(user_input)
                    st.session_state.stage = "itinerary"
                    st.rerun()
                else:
                    st.error("Please describe your trip")
        
        st.markdown('</div>', unsafe_allow_html=True)

def itinerary_page():
    """Itinerary display page"""
    prefs = st.session_state.prefs
    dest_data = DESTINATION_DATA.get(prefs["destination"], {})
    
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        st.markdown('<div class="overlay">', unsafe_allow_html=True)
        
        st.markdown(f"<div class='main-title'>Your {prefs['duration']}-Day NYC Itinerary</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub-title'>{prefs['dates']}</div>", unsafe_allow_html=True)
        
        if "image" in dest_data:
            st.image(dest_data["image"], use_container_width=True, caption=f"{prefs['destination']}, {dest_data.get('country', '')}")
        
        st.markdown(f"""
            <div style="text-align: center; margin: 20px 0 30px; font-family: Montserrat; color: #4A6B8A;">
                <b>Budget:</b> {prefs['budget'].capitalize()} • 
                <b>Interests:</b> {', '.join([i.capitalize() for i in prefs['interests'])} • 
                <b>From:</b> {prefs['start'] if prefs['start'] != 'Not specified' else 'Not specified'}
            </div>
        """, unsafe_allow_html=True)
        
        # Generate sample itinerary
        st.markdown("### Sample Itinerary")
        
        activities = []
        for interest in prefs["interests"]:
            if interest in dest_data.get("activities", {}):
                activities.extend(dest_data["activities"][interest])
        
        random.shuffle(activities)
        num_days = prefs["duration"]
        
        for day in range(1, num_days + 1):
            date = (prefs["start_date"] + timedelta(days=day-1)).strftime("%A, %b %d")
            
            st.markdown(f"""
                <div style="background: white; border-radius: 10px; padding: 20px; margin: 15px 0; border-left: 4px solid #3498DB;">
                    <div style="font-family: Playfair Display; font-size: 20px; color: #2C3E50; margin-bottom: 15px;">Day {day}: {date}</div>
                    <div style="font-family: Montserrat; margin: 10px 0; padding-left: 15px; border-left: 2px solid #EAEAEA;">
                        🌅 <b>Morning:</b> {activities.pop() if activities else "Explore local area"}
                    </div>
                    <div style="font-family: Montserrat; margin: 10px 0; padding-left: 15px; border-left: 2px solid #EAEAEA;">
                        ☀️ <b>Afternoon:</b> {activities.pop() if activities else "Leisure time"}
                    </div>
                    <div style="font-family: Montserrat; margin: 10px 0; padding-left: 15px; border-left: 2px solid #EAEAEA;">
                        🌙 <b>Evening:</b> {random.choice(["Dinner at recommended restaurant", "Night tour", "Broadway show"]) if day > 1 else "Rest after travel"}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        if st.button("Plan Another Trip", key="new_trip"):
            st.session_state.stage = "input"
            st.session_state.prefs = {}
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ======================
# APP ROUTING
# ======================
def main():
    if st.session_state.stage == "input":
        input_page()
    elif st.session_state.stage == "itinerary":
        itinerary_page()

if __name__ == "__main__":
    main()
