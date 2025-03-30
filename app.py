import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict
import geopy.distance
import pytz

# Custom CSS for updated aesthetics
st.markdown("""
    <style>
    /* [Previous CSS styles remain exactly the same] */
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

# Enhanced Destination Database with all 20+ locations
DESTINATION_DATA = {
    # Europe
    "Paris": {
        "image": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34",
        "coordinates": (48.8566, 2.3522),
        "timezone": "Europe/Paris",
        "activities": {
            "art": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou", "Rodin Museum", "Musée de l'Orangerie"],
            "landmarks": ["Eiffel Tower", "Notre-Dame Cathedral", "Arc de Triomphe", "Sacre-Coeur", "Palais Garnier"],
            "food": ["Le Marais Food Tour", "Montmartre Cafés", "Seine River Dinner Cruise", "Patisserie Tour", "Cheese & Wine Tasting"],
            "culture": ["Latin Quarter Walk", "Shakespeare & Company", "Père Lachaise Cemetery", "Moulin Rouge", "Opera Garnier Tour"]
        },
        "country": "France",
        "cost_multiplier": 1.3
    },
    "London": {
        "image": "https://images.unsplash.com/photo-1529655682523-44aca611b2d0",
        "coordinates": (51.5074, -0.1278),
        "timezone": "Europe/London",
        "activities": {
            "history": ["Tower of London", "Westminster Abbey", "Buckingham Palace", "St. Paul's Cathedral", "Churchill War Rooms"],
            "museums": ["British Museum", "Natural History Museum", "Tate Modern", "Victoria & Albert Museum", "Science Museum"],
            "food": ["Borough Market", "Afternoon Tea", "East End Food Tour", "Gin Tasting", "Sunday Roast Experience"],
            "parks": ["Hyde Park", "Regent's Park", "Kew Gardens", "Greenwich Park", "Hampstead Heath"]
        },
        "country": "UK",
        "cost_multiplier": 1.4
    },
    "Rome": {
        "image": "https://images.unsplash.com/photo-1552832230-c0197dd311b5",
        "coordinates": (41.9028, 12.4964),
        "timezone": "Europe/Rome",
        "activities": {
            "history": ["Colosseum", "Roman Forum", "Pantheon", "Palatine Hill", "Baths of Caracalla"],
            "art": ["Vatican Museums", "Sistine Chapel", "Galleria Borghese", "Capitoline Museums"],
            "food": ["Trastevere Food Tour", "Gelato Tasting", "Pasta Making Class", "Testaccio Market"],
            "religion": ["St. Peter's Basilica", "Trevi Fountain", "Spanish Steps", "Catacombs Tour"]
        },
        "country": "Italy",
        "cost_multiplier": 1.2
    },
    "Barcelona": {
        "image": "https://images.unsplash.com/photo-1523531294919-4bcd7c65e216",
        "coordinates": (41.3851, 2.1734),
        "timezone": "Europe/Madrid",
        "activities": {
            "architecture": ["Sagrada Familia", "Park Güell", "Casa Batlló", "La Pedrera"],
            "beaches": ["Barceloneta Beach", "Bogatell Beach", "Nova Icaria Beach"],
            "food": ["La Boqueria Market", "Tapas Tour", "Paella Cooking Class"],
            "culture": ["Gothic Quarter", "Picasso Museum", "Flamenco Show"]
        },
        "country": "Spain",
        "cost_multiplier": 1.1
    },
    "Amsterdam": {
        "image": "https://images.unsplash.com/photo-1512470876302-972faa2aa9a4",
        "coordinates": (52.3676, 4.9041),
        "timezone": "Europe/Amsterdam",
        "activities": {
            "culture": ["Van Gogh Museum", "Anne Frank House", "Rijksmuseum"],
            "canals": ["Canal Cruise", "Jordaan District Walk", "Houseboat Museum"],
            "history": ["Rembrandt House", "Jewish Historical Museum", "Dutch Resistance Museum"],
            "unique": ["Heineken Experience", "Albert Cuyp Market", "Vondelpark Bike Tour"]
        },
        "country": "Netherlands",
        "cost_multiplier": 1.2
    },
    "Vienna": {
        "image": "https://images.unsplash.com/photo-1516550893923-42d28e5677af",
        "coordinates": (48.2082, 16.3738),
        "timezone": "Europe/Vienna",
        "activities": {
            "music": ["Vienna State Opera", "Mozart House", "Strauss Concert"],
            "palaces": ["Schönbrunn Palace", "Hofburg Palace", "Belvedere Palace"],
            "cafes": ["Sachertorte at Hotel Sacher", "Demel Cafe", "Central Cafe"],
            "museums": ["Kunsthistorisches Museum", "Albertina", "Leopold Museum"]
        },
        "country": "Austria",
        "cost_multiplier": 1.1
    },
    "Prague": {
        "image": "https://images.unsplash.com/photo-1519677100203-a0e668c92439",
        "coordinates": (50.0755, 14.4378),
        "timezone": "Europe/Prague",
        "activities": {
            "history": ["Prague Castle", "Charles Bridge", "Old Town Square"],
            "culture": ["Astronomical Clock", "Jewish Quarter", "Kafka Museum"],
            "food": ["Beer Tasting", "Trdelník Making", "Traditional Czech Dinner"],
            "views": ["Petrin Tower", "Vltava River Cruise", "Vyšehrad Castle"]
        },
        "country": "Czech Republic",
        "cost_multiplier": 0.9
    },
    "Istanbul": {
        "image": "https://images.unsplash.com/photo-1527838832700-5059252407fa",
        "coordinates": (41.0082, 28.9784),
        "timezone": "Europe/Istanbul",
        "activities": {
            "history": ["Hagia Sophia", "Blue Mosque", "Topkapi Palace", "Basilica Cistern"],
            "markets": ["Grand Bazaar", "Spice Bazaar", "Arasta Bazaar"],
            "culture": ["Bosphorus Cruise", "Turkish Bath Experience", "Whirling Dervishes Show"],
            "food": ["Kebab Tasting", "Baklava Workshop", "Turkish Coffee Reading"]
        },
        "country": "Turkey",
        "cost_multiplier": 0.8
    },
    "Reykjavik": {
        "image": "https://images.unsplash.com/photo-1529963183134-61a90db47eaf",
        "coordinates": (64.1466, -21.9426),
        "timezone": "Atlantic/Reykjavik",
        "activities": {
            "nature": ["Blue Lagoon", "Golden Circle", "Northern Lights Tour"],
            "adventure": ["Glacier Hiking", "Whale Watching", "Ice Cave Exploration"],
            "culture": ["Hallgrimskirkja", "Harpa Concert Hall", "National Museum"],
            "unique": ["Volcano Tour", "Geothermal Bakery", "Puffin Watching"]
        },
        "country": "Iceland",
        "cost_multiplier": 1.5
    },

    # Asia
    "Tokyo": {
        "image": "https://images.unsplash.com/photo-1542051841857-5f90071e7989",
        "coordinates": (35.6762, 139.6503),
        "timezone": "Asia/Tokyo",
        "activities": {
            "culture": ["Senso-ji Temple", "Meiji Shrine", "Imperial Palace", "Akihabara District", "Robot Restaurant"],
            "food": ["Tsukiji Fish Market", "Ramen Tasting", "Izakaya Hopping", "Sushi Making Class", "Kaiseki Dinner"],
            "modern": ["Shibuya Crossing", "TeamLab Planets", "Tokyo Skytree", "Odaiba District", "Ghibli Museum"],
            "nature": ["Shinjuku Gyoen", "Ueno Park", "Mount Takao Hike", "Hamarikyu Gardens", "Sumida River Cruise"]
        },
        "country": "Japan",
        "cost_multiplier": 1.4
    },
    "Bangkok": {
        "image": "https://images.unsplash.com/photo-1563492065599-3520f775eeed",
        "coordinates": (13.7563, 100.5018),
        "timezone": "Asia/Bangkok",
        "activities": {
            "temples": ["Grand Palace", "Wat Pho", "Wat Arun", "Wat Benchamabophit"],
            "markets": ["Chatuchak Weekend Market", "Floating Markets", "Chinatown Street Food", "Rod Fai Night Market"],
            "culture": ["Thai Cooking Class", "Muay Thai Match", "Traditional Dance Show", "Longtail Boat Tour"],
            "modern": ["Sky Bar", "ICONSIAM Mall", "Mahanakhon Skywalk", "Art in Paradise Museum"]
        },
        "country": "Thailand",
        "cost_multiplier": 0.7
    },
    "Singapore": {
        "image": "https://images.unsplash.com/photo-1565967511849-76a60a516170",
        "coordinates": (1.3521, 103.8198),
        "timezone": "Asia/Singapore",
        "activities": {
            "modern": ["Marina Bay Sands", "Gardens by the Bay", "Sentosa Island"],
            "culture": ["Chinatown", "Little India", "Kampong Glam"],
            "food": ["Hawker Centre Tour", "Chili Crab Dinner", "Singapore Sling at Raffles"],
            "nature": ["Singapore Zoo", "Botanic Gardens", "MacRitchie Reservoir"]
        },
        "country": "Singapore",
        "cost_multiplier": 1.3
    },
    "Bali": {
        "image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4",
        "coordinates": (-8.3405, 115.0920),
        "timezone": "Asia/Makassar",
        "activities": {
            "temples": ["Tanah Lot", "Uluwatu Temple", "Besakih Temple"],
            "nature": ["Tegallalang Rice Terraces", "Mount Batur Sunrise", "Sekumpul Waterfall"],
            "beaches": ["Seminyak", "Nusa Dua", "Padang Padang"],
            "culture": ["Balinese Dance Show", "Silver Jewelry Making", "Ubud Monkey Forest"]
        },
        "country": "Indonesia",
        "cost_multiplier": 0.6
    },
    "Hong Kong": {
        "image": "https://images.unsplash.com/photo-1531259683007-016a7b628fc3",
        "coordinates": (22.3193, 114.1694),
        "timezone": "Asia/Hong_Kong",
        "activities": {
            "views": ["Victoria Peak", "Star Ferry", "Ngong Ping 360"],
            "culture": ["Tian Tan Buddha", "Wong Tai Sin Temple", "Man Mo Temple"],
            "food": ["Dim Sum Tour", "Temple Street Night Market", "Egg Waffle Making"],
            "shopping": ["Causeway Bay", "Mong Kok Markets", "Stanley Market"]
        },
        "country": "China",
        "cost_multiplier": 1.2
    },

    # North America
    "New York": {
        "image": "https://images.unsplash.com/photo-1499092346589-b9b6be3e94b2",
        "coordinates": (40.7128, -74.0060),
        "timezone": "America/New_York",
        "activities": {
            "landmarks": ["Statue of Liberty", "Empire State Building", "Times Square", "Central Park", "Brooklyn Bridge"],
            "museums": ["Metropolitan Museum", "MOMA", "Natural History Museum", "Guggenheim", "Whitney Museum"],
            "food": ["Pizza Tour", "Chinatown Food Crawl", "Bagel Tasting", "Broadway Dinner Package", "Speakeasy Cocktail Tour"],
            "culture": ["Broadway Show", "High Line Walk", "Harlem Gospel Tour", "5th Avenue Shopping", "Yankees Game"]
        },
        "country": "USA",
        "cost_multiplier": 1.5
    },
    "Cancun": {
        "image": "https://images.unsplash.com/photo-1519794206461-cccd885bf209",
        "coordinates": (21.1619, -86.8515),
        "timezone": "America/Cancun",
        "activities": {
            "beaches": ["Playa Delfines", "Isla Mujeres", "Playa Norte", "Xpu-Ha Beach"],
            "ruins": ["Chichen Itza", "Tulum Ruins", "Coba Ruins", "Ek Balam"],
            "adventure": ["Xcaret Park", "Xel-Ha Park", "Cenote Diving", "Sian Ka'an Biosphere"],
            "nightlife": ["Coco Bongo", "Mandala Beach Club", "La Vaquita", "The City Nightclub"]
        },
        "country": "Mexico",
        "cost_multiplier": 0.9
    },

    # Middle East
    "Dubai": {
        "image": "https://images.unsplash.com/photo-1518684079-3c830dcef090",
        "coordinates": (25.2048, 55.2708),
        "timezone": "Asia/Dubai",
        "activities": {
            "modern": ["Burj Khalifa", "Dubai Mall", "Palm Jumeirah", "Dubai Marina", "Museum of the Future"],
            "culture": ["Dubai Creek", "Gold Souk", "Bastakiya Quarter", "Jumeirah Mosque"],
            "desert": ["Desert Safari", "Dune Bashing", "Camel Riding", "Sandboarding"],
            "luxury": ["Burj Al Arab", "Atlantis Waterpark", "Helicopter Tour", "Yacht Cruise"]
        },
        "country": "UAE",
        "cost_multiplier": 1.6
    },

    # Africa
    "Cape Town": {
        "image": "https://images.unsplash.com/photo-1516026672322-bc52d61a60d0",
        "coordinates": (-33.9249, 18.4241),
        "timezone": "Africa/Johannesburg",
        "activities": {
            "nature": ["Table Mountain", "Cape Point", "Kirstenbosch Gardens", "Boulders Beach Penguins"],
            "wine": ["Stellenbosch Wine Tour", "Franschhoek Wine Tram", "Constantia Wine Route"],
            "history": ["Robben Island", "District Six Museum", "Bo-Kaap Walking Tour"],
            "adventure": ["Lion's Head Hike", "Shark Cage Diving", "Paragliding Signal Hill"]
        },
        "country": "South Africa",
        "cost_multiplier": 0.8
    },

    # Oceania
    "Sydney": {
        "image": "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9",
        "coordinates": (-33.8688, 151.2093),
        "timezone": "Australia/Sydney",
        "activities": {
            "landmarks": ["Sydney Opera House", "Harbour Bridge", "Bondi Beach", "The Rocks"],
            "nature": ["Blue Mountains", "Taronga Zoo", "Royal Botanic Garden", "Manly Beach Walk"],
            "food": ["Sydney Fish Market", "The Grounds of Alexandria", "Chinatown Food Tour", "Wine Tasting in Hunter Valley"],
            "culture": ["Art Gallery of NSW", "Sydney Tower Eye", "Darling Harbour", "Luna Park"]
        },
        "country": "Australia",
        "cost_multiplier": 1.3
    },

    # South America
    "Rio de Janeiro": {
        "image": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325",
        "coordinates": (-22.9068, -43.1729),
        "timezone": "America/Sao_Paulo",
        "activities": {
            "landmarks": ["Christ the Redeemer", "Sugarloaf Mountain", "Selaron Steps"],
            "beaches": ["Copacabana", "Ipanema", "Leblon"],
            "nature": ["Tijuca Forest", "Botanical Garden", "Pedra da Gavea Hike"],
            "culture": ["Samba Show", "Favela Tour", "Museum of Tomorrow"]
        },
        "country": "Brazil",
        "cost_multiplier": 0.9
    },
    "Cairo": {
        "image": "https://images.unsplash.com/photo-1572252009286-268acec5ca0a",
        "coordinates": (30.0444, 31.2357),
        "timezone": "Africa/Cairo",
        "activities": {
            "pyramids": ["Giza Pyramids", "Sphinx", "Saqqara Pyramid"],
            "museums": ["Egyptian Museum", "Coptic Museum", "Islamic Art Museum"],
            "culture": ["Khan el-Khalili Bazaar", "Nile Dinner Cruise", "Al-Azhar Park"],
            "history": ["Dahshur Pyramids", "Memphis Ruins", "Citadel of Saladin"]
        },
        "country": "Egypt",
        "cost_multiplier": 0.7
    }
}

# [Rest of the code remains exactly the same as in the previous version]
# [All the functions, parsing logic, and UI components stay identical]
# [Only the DESTINATION_DATA dictionary has been expanded as shown above]

# Footer
st.markdown("---")
st.write("Powered by Streamlit | Designed for your travel dreams!")
