import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict

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

# Enhanced Destination Database with 20+ locations
DESTINATION_DATA = {
    # Europe
    "Paris": {
        "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
        "activities": {
            "art": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou", "Rodin Museum", "Musée de l'Orangerie"],
            "landmarks": ["Eiffel Tower", "Notre-Dame Cathedral", "Arc de Triomphe", "Sacre-Coeur", "Palais Garnier"],
            "food": ["Le Marais Food Tour", "Montmartre Cafés", "Seine River Dinner Cruise", "Patisserie Tour", "Cheese & Wine Tasting"],
            "culture": ["Latin Quarter Walk", "Shakespeare & Company", "Père Lachaise Cemetery", "Moulin Rouge", "Opera Garnier Tour"]
        },
        "country": "France"
    },
    "London": {
        "image": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0",
        "activities": {
            "history": ["Tower of London", "Westminster Abbey", "Buckingham Palace", "St. Paul's Cathedral", "Churchill War Rooms"],
            "museums": ["British Museum", "Natural History Museum", "Tate Modern", "Victoria & Albert Museum", "Science Museum"],
            "food": ["Borough Market", "Afternoon Tea", "East End Food Tour", "Gin Tasting", "Sunday Roast Experience"],
            "parks": ["Hyde Park", "Regent's Park", "Kew Gardens", "Greenwich Park", "Hampstead Heath"]
        },
        "country": "UK"
    },
    "Rome": {
        "image": "https://images.unsplash.com/photo-1552832230-c0197dd311b5",
        "activities": {
            "history": ["Colosseum", "Roman Forum", "Pantheon", "Palatine Hill", "Baths of Caracalla"],
            "art": ["Vatican Museums", "Sistine Chapel", "Galleria Borghese", "Capitoline Museums"],
            "food": ["Trastevere Food Tour", "Gelato Tasting", "Pasta Making Class", "Testaccio Market"],
            "religion": ["St. Peter's Basilica", "Trevi Fountain", "Spanish Steps", "Catacombs Tour"]
        },
        "country": "Italy"
    },
    "Barcelona": {
        "image": "https://images.unsplash.com/photo-1523531294919-4bcd7c65e216",
        "activities": {
            "architecture": ["Sagrada Familia", "Park Güell", "Casa Batlló", "La Pedrera"],
            "beaches": ["Barceloneta Beach", "Bogatell Beach", "Nova Icaria Beach"],
            "food": ["La Boqueria Market", "Tapas Tour", "Paella Cooking Class"],
            "culture": ["Gothic Quarter", "Picasso Museum", "Flamenco Show"]
        },
        "country": "Spain"
    },
    "Amsterdam": {
        "image": "https://images.unsplash.com/photo-1512470876302-972faa2aa9a4",
        "activities": {
            "culture": ["Van Gogh Museum", "Anne Frank House", "Rijksmuseum"],
            "canals": ["Canal Cruise", "Jordaan District Walk", "Houseboat Museum"],
            "history": ["Rembrandt House", "Jewish Historical Museum", "Dutch Resistance Museum"],
            "unique": ["Heineken Experience", "Albert Cuyp Market", "Vondelpark Bike Tour"]
        },
        "country": "Netherlands"
    },
    "Vienna": {
        "image": "https://images.unsplash.com/photo-1516550893923-42d28e5677af",
        "activities": {
            "music": ["Vienna State Opera", "Mozart House", "Strauss Concert"],
            "palaces": ["Schönbrunn Palace", "Hofburg Palace", "Belvedere Palace"],
            "cafes": ["Sachertorte at Hotel Sacher", "Demel Cafe", "Central Cafe"],
            "museums": ["Kunsthistorisches Museum", "Albertina", "Leopold Museum"]
        },
        "country": "Austria"
    },
    "Prague": {
        "image": "https://images.unsplash.com/photo-1519677100203-a0e668c92439",
        "activities": {
            "history": ["Prague Castle", "Charles Bridge", "Old Town Square"],
            "culture": ["Astronomical Clock", "Jewish Quarter", "Kafka Museum"],
            "food": ["Beer Tasting", "Trdelník Making", "Traditional Czech Dinner"],
            "views": ["Petrin Tower", "Vltava River Cruise", "Vyšehrad Castle"]
        },
        "country": "Czech Republic"
    },
    "Istanbul": {
        "image": "https://images.unsplash.com/photo-1527838832700-5059252407fa",
        "activities": {
            "history": ["Hagia Sophia", "Blue Mosque", "Topkapi Palace", "Basilica Cistern"],
            "markets": ["Grand Bazaar", "Spice Bazaar", "Arasta Bazaar"],
            "culture": ["Bosphorus Cruise", "Turkish Bath Experience", "Whirling Dervishes Show"],
            "food": ["Kebab Tasting", "Baklava Workshop", "Turkish Coffee Reading"]
        },
        "country": "Turkey"
    },
    "Reykjavik": {
        "image": "https://images.unsplash.com/photo-1529963183134-61a90db47eaf",
        "activities": {
            "nature": ["Blue Lagoon", "Golden Circle", "Northern Lights Tour"],
            "adventure": ["Glacier Hiking", "Whale Watching", "Ice Cave Exploration"],
            "culture": ["Hallgrimskirkja", "Harpa Concert Hall", "National Museum"],
            "unique": ["Volcano Tour", "Geothermal Bakery", "Puffin Watching"]
        },
        "country": "Iceland"
    },

    # Asia
    "Tokyo": {
        "image": "https://images.unsplash.com/photo-1542051841857-5f90071e7989",
        "activities": {
            "culture": ["Senso-ji Temple", "Meiji Shrine", "Imperial Palace", "Akihabara District", "Robot Restaurant"],
            "food": ["Tsukiji Fish Market", "Ramen Tasting", "Izakaya Hopping", "Sushi Making Class", "Kaiseki Dinner"],
            "modern": ["Shibuya Crossing", "TeamLab Planets", "Tokyo Skytree", "Odaiba District", "Ghibli Museum"],
            "nature": ["Shinjuku Gyoen", "Ueno Park", "Mount Takao Hike", "Hamarikyu Gardens", "Sumida River Cruise"]
        },
        "country": "Japan"
    },
    "Bangkok": {
        "image": "https://images.unsplash.com/photo-1563492065599-3520f775eeed",
        "activities": {
            "temples": ["Grand Palace", "Wat Pho", "Wat Arun", "Wat Benchamabophit"],
            "markets": ["Chatuchak Weekend Market", "Floating Markets", "Chinatown Street Food", "Rod Fai Night Market"],
            "culture": ["Thai Cooking Class", "Muay Thai Match", "Traditional Dance Show", "Longtail Boat Tour"],
            "modern": ["Sky Bar", "ICONSIAM Mall", "Mahanakhon Skywalk", "Art in Paradise Museum"]
        },
        "country": "Thailand"
    },
    "Singapore": {
        "image": "https://images.unsplash.com/photo-1565967511849-76a60a516170",
        "activities": {
            "modern": ["Marina Bay Sands", "Gardens by the Bay", "Sentosa Island"],
            "culture": ["Chinatown", "Little India", "Kampong Glam"],
            "food": ["Hawker Centre Tour", "Chili Crab Dinner", "Singapore Sling at Raffles"],
            "nature": ["Singapore Zoo", "Botanic Gardens", "MacRitchie Reservoir"]
        },
        "country": "Singapore"
    },
    "Bali": {
        "image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4",
        "activities": {
            "temples": ["Tanah Lot", "Uluwatu Temple", "Besakih Temple"],
            "nature": ["Tegallalang Rice Terraces", "Mount Batur Sunrise", "Sekumpul Waterfall"],
            "beaches": ["Seminyak", "Nusa Dua", "Padang Padang"],
            "culture": ["Balinese Dance Show", "Silver Jewelry Making", "Ubud Monkey Forest"]
        },
        "country": "Indonesia"
    },
    "Hong Kong": {
        "image": "https://images.unsplash.com/photo-1531259683007-016a7b628fc3",
        "activities": {
            "views": ["Victoria Peak", "Star Ferry", "Ngong Ping 360"],
            "culture": ["Tian Tan Buddha", "Wong Tai Sin Temple", "Man Mo Temple"],
            "food": ["Dim Sum Tour", "Temple Street Night Market", "Egg Waffle Making"],
            "shopping": ["Causeway Bay", "Mong Kok Markets", "Stanley Market"]
        },
        "country": "China"
    },

    # North America
    "New York": {
        "image": "https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2",
        "activities": {
            "landmarks": ["Statue of Liberty", "Empire State Building", "Times Square", "Central Park", "Brooklyn Bridge"],
            "museums": ["Metropolitan Museum", "MOMA", "Natural History Museum", "Guggenheim", "Whitney Museum"],
            "food": ["Pizza Tour", "Chinatown Food Crawl", "Bagel Tasting", "Broadway Dinner Package", "Speakeasy Cocktail Tour"],
            "culture": ["Broadway Show", "High Line Walk", "Harlem Gospel Tour", "5th Avenue Shopping", "Yankees Game"]
        },
        "country": "USA"
    },
    "Cancun": {
        "image": "https://images.unsplash.com/photo-1519794206461-cccd885bf209",
        "activities": {
            "beaches": ["Playa Delfines", "Isla Mujeres", "Playa Norte", "Xpu-Ha Beach"],
            "ruins": ["Chichen Itza", "Tulum Ruins", "Coba Ruins", "Ek Balam"],
            "adventure": ["Xcaret Park", "Xel-Ha Park", "Cenote Diving", "Sian Ka'an Biosphere"],
            "nightlife": ["Coco Bongo", "Mandala Beach Club", "La Vaquita", "The City Nightclub"]
        },
        "country": "Mexico"
    },

    # Middle East
    "Dubai": {
        "image": "https://images.unsplash.com/photo-1518684079-3c830dcef090",
        "activities": {
            "modern": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah", "Dubai Marina", "Museum of the Future"],
            "culture": ["Dubai Creek", "Gold Souk", "Bastakiya Quarter", "Jumeirah Mosque"],
            "desert": ["Desert Safari", "Dune Bashing", "Camel Riding", "Sandboarding"],
            "luxury": ["Burj Al Arab", "Atlantis Waterpark", "Helicopter Tour", "Yacht Cruise"]
        },
        "country": "UAE"
    },

    # Africa
    "Cape Town": {
        "image": "https://images.unsplash.com/photo-1516026672322-bc52d61a60d0",
        "activities": {
            "nature": ["Table Mountain", "Cape Point", "Kirstenbosch Gardens", "Boulders Beach Penguins"],
            "wine": ["Stellenbosch Wine Tour", "Franschhoek Wine Tram", "Constantia Wine Route"],
            "history": ["Robben Island", "District Six Museum", "Bo-Kaap Walking Tour"],
            "adventure": ["Lion's Head Hike", "Shark Cage Diving", "Paragliding Signal Hill"]
        },
        "country": "South Africa"
    },

    # Oceania
    "Sydney": {
        "image": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9",
        "activities": {
            "landmarks": ["Sydney Opera House", "Harbour Bridge", "Bondi Beach", "The Rocks"],
            "nature": ["Blue Mountains", "Taronga Zoo", "Royal Botanic Garden", "Manly Beach Walk"],
            "food": ["Sydney Fish Market", "The Grounds of Alexandria", "Chinatown Food Tour", "Wine Tasting in Hunter Valley"],
            "culture": ["Art Gallery of NSW", "Sydney Tower Eye", "Darling Harbour", "Luna Park"]
        },
        "country": "Australia"
    },

    # South America
    "Rio de Janeiro": {
        "image": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325",
        "activities": {
            "landmarks": ["Christ the Redeemer", "Sugarloaf Mountain", "Selaron Steps"],
            "beaches": ["Copacabana", "Ipanema", "Leblon"],
            "nature": ["Tijuca Forest", "Botanical Garden", "Pedra da Gavea Hike"],
            "culture": ["Samba Show", "Favela Tour", "Museum of Tomorrow"]
        },
        "country": "Brazil"
    },
    "Cairo": {
        "image": "https://images.unsplash.com/photo-1572252009286-268acec5ca0a",
        "activities": {
            "pyramids": ["Giza Pyramids", "Sphinx", "Saqqara Pyramid"],
            "museums": ["Egyptian Museum", "Coptic Museum", "Islamic Art Museum"],
            "culture": ["Khan el-Khalili Bazaar", "Nile Dinner Cruise", "Al-Azhar Park"],
            "history": ["Dahshur Pyramids", "Memphis Ruins", "Citadel of Saladin"]
        },
        "country": "Egypt"
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
    },
    "country": "Unknown"
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
        "tok": "Tokyo",
        "ny": "New York",
        "barca": "Barcelona",
        "rio": "Rio de Janeiro"
    }
    for partial, full in partial_matches.items():
        if partial in text_lower:
            return full
    return None

def parse_dates(text):
    text_lower = text.lower()
    
    # Try to extract specific date ranges first
    date_range_patterns = [
        # MM/DD/YYYY - MM/DD/YYYY
        (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s*[-–to]+\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", "%m/%d/%Y - %m/%d/%Y"),
        # Month Day - Day, Year
        (r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s*[-–to]+\s*(\d{1,2}),?\s+(\d{4})\b", "%b %d-%d, %Y"),
        # Month Day - Month Day, Year
        (r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s*[-–to]+\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})\b", "%b %d - %b %d, %Y"),
    ]
    
    for pattern, fmt in date_range_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if fmt == "%b %d-%d, %Y":
                    month = match.group(1)
                    start_day = match.group(2)
                    end_day = match.group(3)
                    year = match.group(4)
                    return f"{month[:3].title()} {start_day}-{end_day}, {year}"
                elif fmt == "%b %d - %b %d, %Y":
                    start_month = match.group(1)
                    start_day = match.group(2)
                    end_month = match.group(3)
                    end_day = match.group(4)
                    year = match.group(5)
                    return f"{start_month[:3].title()} {start_day} - {end_month[:3].title()} {end_day}, {year}"
                else:
                    return match.group(0).title()
            except:
                continue
    
    # Try single dates with duration
    single_date_patterns = [
        # Starting MM/DD/YYYY for X days
        (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\s+(?:for|on)\s+(\d+)\s+(day|week)s?\b", "%m/%d/%Y for %d %s"),
        # Starting Month Day for X days
        (r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})\s+(?:for|on)\s+(\d+)\s+(day|week)s?\b", "%b %d for %d %s"),
    ]
    
    for pattern, fmt in single_date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if fmt == "%b %d for %d %s":
                    month = match.group(1)
                    day = match.group(2)
                    duration = int(match.group(3))
                    unit = match.group(4)
                    if unit == "week":
                        duration *= 7
                    end_date = (datetime.strptime(f"{day} {month} {datetime.now().year}", "%d %b %Y") + timedelta(days=duration-1))
                    return f"{month[:3].title()} {day} - {end_date.strftime('%b %d, %Y')} ({duration} days)"
            except:
                continue
    
    # Relative dates with duration
    relative_patterns = [
        (r"\bnext\s+week\s+(?:for|on)\s+(\d+)\s+days\b", "Next week for %d days"),
        (r"\b(\d+)\s+(?:day|night)s?\s+(?:trip|stay|visit)\b", "%d-day trip"),
    ]
    
    for pattern, fmt in relative_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                duration = int(match.group(1))
                today = datetime.now()
                end_date = today + timedelta(days=duration-1)
                return f"{today.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} ({duration} days)"
            except:
                continue
    
    # Common phrases
    common_phrases = {
        "weekend": "Weekend getaway (2 days)",
        "long weekend": "Long weekend (3-4 days)",
        "next week": "Next week (7 days)",
        "next month": "Next month (30 days)",
        "summer vacation": "Summer vacation (7-14 days)",
        "winter break": "Winter break (7-14 days)",
    }
    
    for phrase, result in common_phrases.items():
        if phrase in text_lower:
            return result
    
    # Final fallback - ask for duration
    return "Duration not specified"

def parse_budget(text):
    text_lower = text.lower()
    budget_keywords = {
        "luxury": ["luxury", "high-end", "expensive", "5-star", "premium"],
        "moderate": ["moderate", "mid-range", "average", "comfortable"],
        "budget": ["budget", "cheap", "affordable", "low-cost", "economy"]
    }
    for level, keywords in budget_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return level
    return "moderate"

def parse_interests(text):
    interest_map = {
        "art": ["art", "museum", "gallery", "painting", "sculpture", "exhibition"],
        "food": ["food", "restaurant", "cuisine", "dining", "eat", "drink", "culinary"],
        "history": ["history", "historical", "monument", "landmark", "ancient", "archaeology"],
        "nature": ["nature", "park", "garden", "hike", "outdoor", "walk", "wildlife"],
        "shopping": ["shop", "mall", "market", "boutique", "store", "souvenir"],
        "adventure": ["adventure", "hiking", "trek", "explore", "active", "sport"],
        "culture": ["culture", "local", "traditional", "festival", "heritage"],
        "beach": ["beach", "coast", "shore", "island", "ocean"]
    }
    
    interests = []
    text_lower = text.lower()
    for interest, keywords in interest_map.items():
        if any(keyword in text_lower for keyword in keywords):
            interests.append(interest)
    return interests if interests else ["culture", "food"]

# Helper function for default interests
def get_default_interests(prefs):
    if "interests" in prefs:
        return [i.capitalize() for i in prefs["interests"]]
    return []

# Helper function to get duration from dates string
def get_duration_from_dates(dates_str):
    # Extract duration from patterns like "(7 days)"
    duration_match = re.search(r"\((\d+)\s+day", dates_str)
    if duration_match:
        return int(duration_match.group(1))
    
    # Calculate from date range
    date_range_match = re.search(r"(\w+\s+\d+)\s*[-–]\s*(\w+\s+\d+)", dates_str)
    if date_range_match:
        try:
            start_date = datetime.strptime(date_range_match.group(1), "%b %d")
            end_date = datetime.strptime(date_range_match.group(2), "%b %d")
            return (end_date - start_date).days + 1
        except:
            pass
    
    # Default durations for common phrases
    common_durations = {
        "weekend": 2,
        "long weekend": 4,
        "next week": 7,
        "next month": 30
    }
    for phrase, days in common_durations.items():
        if phrase.lower() in dates_str.lower():
            return days
    
    return 7  # Default to one week

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
            <div class="image-overlay">{prefs.get('destination', 'Your Destination')}, {dest_data.get('country', '')}</div>
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
            sorted(list(DESTINATION_DATA.keys())),
            index=list(DESTINATION_DATA.keys()).index(prefs["destination"]) if prefs["destination"] in DESTINATION_DATA else 0
        )
        
        col1, col2 = st.columns(2)
        new_dates = col1.text_input("Travel Dates:", value=prefs["dates"])
        
        # Add duration selector if dates aren't specific
        duration_days = 7  # Default
        if "not specified" in prefs["dates"].lower() or "duration" in prefs["dates"].lower():
            duration_options = {
                "Weekend (2-3 days)": 3,
                "Short trip (4-5 days)": 5,
                "One week (7 days)": 7,
                "Two weeks (14 days)": 14,
                "Month-long (30 days)": 30
            }
            selected_duration = col2.selectbox(
                "Trip Duration:",
                options=list(duration_options.keys()),
                index=2  # Default to one week
            )
            duration_days = duration_options[selected_duration]
            today = datetime.now()
            end_date = today + timedelta(days=duration_days-1)
            new_dates = f"{today.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} ({duration_days} days)"
        else:
            # If dates are specified, calculate duration
            duration_days = get_duration_from_dates(prefs["dates"])
            if duration_days > 30:  # Cap at 30 days
                duration_days = 30
        
        new_budget = col2.selectbox(
            "Budget Level:",
            ["Budget", "Moderate", "Luxury"],
            index=["budget", "moderate", "luxury"].index(prefs["budget"])
        )
        
        interest_options = ["Art", "Food", "History", "Nature", "Shopping", "Adventure", "Culture", "Beach"]
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
            "start": prefs.get("start", "Not specified"),
            "duration": duration_days
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
    
    st.write(f"### Based on your preferences, here are some great activities for your {prefs.get('duration', 7)}-day trip:")
    
    # Generate activity suggestions
    activities = []
    for interest in prefs.get("interests", ["culture", "food"]):
        if interest in dest_data["activities"]:
            activities.extend(dest_data["activities"][interest])
    
    # Ensure we have enough activities (minimum 2 per day)
    min_activities = prefs.get("duration", 7) * 2
    if len(activities) < min_activities:
        all_activities = []
        for interest_acts in dest_data["activities"].values():
            all_activities.extend(interest_acts)
        additional_needed = min_activities - len(activities)
        activities.extend(random.sample([act for act in all_activities if act not in activities], 
                                      min(additional_needed, len(all_activities))))
    
    # Display activities with tags
    for i, activity in enumerate(activities[:min_activities*2]):  # Show max 2x min activities
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

# Stage 4: Itinerary Generation (Optimized Version)
elif st.session_state.stage == "itinerary_generation":
    prefs = st.session_state.preferences
    activities = st.session_state.activities
    
    st.markdown('<div class="section-header" id="step4">Step 4: Your Personalized Itinerary</div>', unsafe_allow_html=True)
    st.write(f"### Here's your customized {prefs.get('duration', 7)}-day {prefs.get('destination', 'trip')} itinerary:")
    
    # Get duration from preferences
    num_days = prefs.get("duration", 7)
    
    # Optimized itinerary generation
    def generate_itinerary(activities, num_days):
        # Group activities by interest categories
        activity_groups = defaultdict(list)
        for act in activities:
            for interest in prefs.get("interests", []):
                if interest.lower() in act.lower():
                    activity_groups[interest].append(act)
        
        # Create a pool of all activities
        activity_pool = activities.copy()
        random.shuffle(activity_pool)
        
        daily_plans = {}
        used_activities = set()
        
        for day in range(1, min(num_days, 30) + 1):  # Max 30 days
            daily_plans[day] = []
            
            # Try to get one activity from each interest group first
            for interest in random.sample(list(activity_groups.keys()), len(activity_groups)):
                available = [act for act in activity_groups[interest] if act not in used_activities]
                if available and len(daily_plans[day]) < 2:
                    selected = random.choice(available)
                    daily_plans[day].append(selected)
                    used_activities.add(selected)
            
            # Fill remaining slots with unused activities
            remaining = [act for act in activity_pool if act not in used_activities]
            while len(daily_plans[day]) < 2 and remaining:
                selected = remaining.pop()
                daily_plans[day].append(selected)
                used_activities.add(selected)
            
            # If still not enough, reuse least used activities
            if len(daily_plans[day]) < 2:
                activity_usage = {act: sum(1 for d in daily_plans.values() if act in d) for act in activities}
                least_used = sorted(activity_usage.items(), key=lambda x: x[1])[:5]
                for act, count in least_used:
                    if len(daily_plans[day]) < 2:
                        daily_plans[day].append(act)
        
        return daily_plans
    
    itinerary = generate_itinerary(activities, num_days)
    
    # Display itinerary
    for day_num, day_acts in itinerary.items():
        day_title = f"Day {day_num}"
        if day_num == 1:
            day_title += " - Arrival"
        elif day_num == num_days:
            day_title += " - Departure"
        
        st.markdown(f"""
            <div class="itinerary-card">
                <i class="fas fa-calendar-day"></i> <strong>{day_title}</strong><br>
                - {'<br>- '.join(day_acts)}
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
