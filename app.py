import streamlit as st
import re
from datetime import datetime, timedelta
import random
from collections import defaultdict
import math

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
    "activities": {
        "art": ["Local Art Museum", "Street Art Tour"],
        "food": ["Food Market Tour", "Local Restaurant Crawl"],
        "history": ["Historical Walking Tour", "Old Town Exploration"],
        "nature": ["City Park", "Botanical Gardens"]
    },
    "country": "Unknown",
    "cost_multiplier": 1.0
}

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
    
    st.title("🌍 AI-Powered Travel Planner")
    
    # Stage 1: Input Collection
    if st.session_state.stage == "input_refinement":
        with st.form("trip_input"):
            st.subheader("Plan Your Dream Trip")
            user_input = st.text_area(
                "Describe your trip (destination, dates, interests, budget):",
                placeholder="e.g., 'Romantic Paris getaway from June 10-15, love art and fine dining with luxury budget'",
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
        
        # Display what we understood
        st.write("Here's what we understood from your input:")
        cols = st.columns(3)
        cols[0].metric("Destination", prefs.get("destination", "Not specified"))
        cols[1].metric("Dates", prefs.get("dates", "Not specified"))
        cols[2].metric("Duration", f"{prefs.get('duration', '?')} days")
        
        with st.form("preference_refinement"):
            st.markdown("### Adjust your preferences:")
            
            # Destination
            current_dest = prefs.get("destination", "")
            dest_options = sorted(list(DESTINATION_DATA.keys()))
            current_dest_idx = dest_options.index(current_dest) if current_dest in dest_options else 0
            new_dest = st.selectbox(
                "Destination:",
                dest_options,
                index=current_dest_idx
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
                default_duration = next(
                    (k for k,v in duration_options.items() if v == current_duration),
                    "One week (7 days)"
                )
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
                    "dates": new_dates,
                    "duration": final_duration,
                    "start_date": prefs.get("start_date", datetime.now()),
                    "end_date": prefs.get("start_date", datetime.now()) + timedelta(days=final_duration-1),
                    "budget": new_budget.lower(),
                    "interests": [i.lower() for i in new_interests],
                    "start": prefs.get("start", "Not specified"),
                    "destination_data": DESTINATION_DATA.get(new_dest, DEFAULT_DESTINATION)
                }
                st.session_state.stage = "itinerary_generation"
                st.rerun()
    
    # Stage 3: Itinerary Generation
    elif st.session_state.stage == "itinerary_generation":
        prefs = st.session_state.preferences
        dest = prefs.get("destination", "Your Destination")
        duration = prefs.get("duration", 7)
        
        st.header(f"✈️ Your {duration}-Day {dest} Itinerary")
        st.subheader(f"📅 {prefs.get('dates', '')}")
        
        # Display destination info
        dest_data = prefs.get("destination_data", DEFAULT_DESTINATION)
        st.image(dest_data["image"], use_column_width=True)
        st.markdown(f"**{dest}, {dest_data.get('country', '')}**")
        
        if prefs.get("start", "Not specified") != "Not specified":
            st.markdown(f"*Traveling from: {prefs['start']}*")
        
        # Generate and display itinerary
        st.markdown("---")
        st.subheader("Your Personalized Itinerary")
        
        # Create daily itinerary
        for day in range(1, duration + 1):
            current_date = (prefs["start_date"] + timedelta(days=day-1)).strftime("%A, %b %d")
            
            with st.expander(f"Day {day}: {current_date}"):
                # Morning activity
                if day == 1:
                    st.markdown("**Arrival Day**")
                    activity_card("Airport Transfer", "12:00 PM - 1:00 PM", 50, "25 km")
                else:
                    if "art" in prefs["interests"] and day % 2 == 1:
                        activity = random.choice(dest_data["activities"].get("art", ["Art Gallery Visit"]))
                        activity_card(activity, "9:00 AM - 12:00 PM", 25, "5 km")
                
                # Afternoon activity
                if "food" in prefs["interests"]:
                    activity = random.choice(dest_data["activities"].get("food", ["Local Restaurant"]))
                    activity_card(activity, "1:00 PM - 3:00 PM", 40, "2 km")
                
                # Evening activity
                if day > 1:  # Skip first evening
                    if "culture" in prefs["interests"]:
                        activity = random.choice(dest_data["activities"].get("culture", ["Cultural Show"]))
                        activity_card(activity, "6:00 PM - 9:00 PM", 35, "3 km")
        
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

def activity_card(activity, time, cost, distance):
    """Display an activity card with consistent formatting"""
    st.markdown(f"""
        <div style="padding: 12px; border-radius: 8px; background-color: #f8f9fa; 
            margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1)">
            <div style="font-weight: bold; font-size: 1.1rem;">{activity}</div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                <span>⏰ {time}</span>
                <span>💰 ${cost}</span>
                <span>📏 {distance}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
