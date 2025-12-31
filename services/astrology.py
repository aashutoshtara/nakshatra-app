"""
Nakshatra Astrology Service
Core Vedic Astrology calculations using PyJHora
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import pytz

# Try tzfpy first, fallback to manual lookup
try:
    from tzfpy import get_tz
    _use_tzfpy = True
except ImportError:
    _use_tzfpy = False

# PyJHora imports
from jhora.panchanga import drik
from jhora.horoscope.dhasa.graha import vimsottari
from jhora import utils


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Location:
    """Geographic location"""
    name: str
    latitude: float
    longitude: float
    timezone: str

    @property
    def tz_offset(self) -> float:
        """Get timezone offset in hours"""
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        return now.utcoffset().total_seconds() / 3600


@dataclass
class BirthData:
    """Birth data for a person"""
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location: Location

    @property
    def datetime(self) -> datetime:
        return datetime(self.year, self.month, self.day, self.hour, self.minute)


# =============================================================================
# CONSTANTS
# =============================================================================

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _safe_int(value, default=0):
    """Safely convert value to int, handling nested lists"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return default
        return _safe_int(value[0], default)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def _safe_float(value, default=0.0):
    """Safely convert value to float, handling nested lists"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)):
        if len(value) == 0:
            return default
        return _safe_float(value[0], default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _get_value(data, index, default=None):
    """Safely get value from list/tuple at index"""
    if data is None:
        return default
    if isinstance(data, (list, tuple)):
        if len(data) > index:
            val = data[index]
            # Handle nested lists
            if isinstance(val, (list, tuple)) and len(val) > 0:
                return val[0]
            return val
    return default


RASHI_NAMES = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)",
    "Karka (Cancer)", "Simha (Leo)", "Kanya (Virgo)",
    "Tula (Libra)", "Vrishchika (Scorpio)", "Dhanu (Sagittarius)",
    "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

RASHI_NAMES_SHORT = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


# =============================================================================
# 27 NAKSHATRAS - COMPLETE INTERPRETATIONS
# =============================================================================

NAKSHATRAS = {
    "Ashwini": {
        "index": 1,
        "deity": "Ashwini Kumaras (Divine Physicians)",
        "symbol": "Horse's Head",
        "ruling_planet": "Ketu",
        "element": "Earth",
        "guna": "Sattva",
        "animal": "Horse",
        "lucky_color": "Blood Red",
        "lucky_number": 7,
        "lucky_stone": "Cat's Eye",
        "personality": "You are a natural healer with swift energy and initiative. Like the divine Ashwini Kumaras, you possess the ability to bring quick solutions and healing to others. Your pioneering spirit makes you excellent at starting new ventures.",
        "strengths": ["Quick thinking", "Healing abilities", "Pioneering spirit", "Energetic", "Independent"],
        "challenges": ["Impatience", "Impulsiveness", "Difficulty completing tasks"],
        "career": ["Medicine", "Emergency services", "Sports", "Entrepreneurship"]
    },

    "Bharani": {
        "index": 2,
        "deity": "Yama (God of Death/Dharma)",
        "symbol": "Yoni",
        "ruling_planet": "Venus",
        "element": "Earth",
        "guna": "Rajas",
        "animal": "Elephant",
        "lucky_color": "Blood Red",
        "lucky_number": 6,
        "lucky_stone": "Diamond",
        "personality": "You carry the energy of transformation and rebirth. With Yama as your deity, you understand the deeper cycles of life. You have a strong sense of duty and can bear heavy responsibilities.",
        "strengths": ["Endurance", "Transformative power", "Sense of duty", "Creative", "Nurturing"],
        "challenges": ["Extremism", "Jealousy", "Moral rigidity"],
        "career": ["Publishing", "Film", "Hospitality", "Occult sciences"]
    },

    "Krittika": {
        "index": 3,
        "deity": "Agni (Fire God)",
        "symbol": "Razor/Flame",
        "ruling_planet": "Sun",
        "element": "Fire",
        "guna": "Rajas",
        "animal": "Goat",
        "lucky_color": "White",
        "lucky_number": 1,
        "lucky_stone": "Ruby",
        "personality": "You possess the purifying fire of Agni. Your sharp intellect can cut through illusion and get to the truth. You are determined, dignified, and have strong leadership qualities.",
        "strengths": ["Sharp intellect", "Determination", "Leadership", "Courage", "Purifying nature"],
        "challenges": ["Criticism", "Stubbornness", "Harsh speech"],
        "career": ["Military", "Cooking/Chef", "Spiritual teacher", "Metallurgy"]
    },

    "Rohini": {
        "index": 4,
        "deity": "Brahma (Creator)",
        "symbol": "Chariot/Ox Cart",
        "ruling_planet": "Moon",
        "element": "Earth",
        "guna": "Rajas",
        "animal": "Serpent",
        "lucky_color": "White",
        "lucky_number": 2,
        "lucky_stone": "Pearl",
        "personality": "You embody beauty, creativity, and abundance. As the favorite nakshatra of the Moon, you have magnetic charm and artistic talents. You appreciate luxury and can manifest material prosperity.",
        "strengths": ["Beauty", "Creativity", "Magnetic charm", "Abundance", "Artistic talents"],
        "challenges": ["Materialism", "Possessiveness", "Jealousy"],
        "career": ["Arts", "Fashion", "Agriculture", "Banking", "Beauty industry"]
    },

    "Mrigashira": {
        "index": 5,
        "deity": "Soma (Moon God)",
        "symbol": "Deer's Head",
        "ruling_planet": "Mars",
        "element": "Earth",
        "guna": "Tamas",
        "animal": "Serpent",
        "lucky_color": "Silver Grey",
        "lucky_number": 9,
        "lucky_stone": "Red Coral",
        "personality": "You are a seeker, always searching for knowledge and new experiences. Like a deer, you are gentle, alert, and quick. You have a curious mind that loves to explore.",
        "strengths": ["Curiosity", "Gentleness", "Quick mind", "Perceptive", "Romantic"],
        "challenges": ["Restlessness", "Fickleness", "Suspicion"],
        "career": ["Research", "Travel", "Writing", "Textiles", "Real estate"]
    },

    "Ardra": {
        "index": 6,
        "deity": "Rudra (Storm God)",
        "symbol": "Teardrop/Diamond",
        "ruling_planet": "Rahu",
        "element": "Water",
        "guna": "Tamas",
        "animal": "Dog",
        "lucky_color": "Green",
        "lucky_number": 4,
        "lucky_stone": "Hessonite (Gomed)",
        "personality": "You carry the transformative power of storms. Ardra brings destruction that leads to renewal. You have intense emotions and deep understanding of suffering, giving you compassion.",
        "strengths": ["Intensity", "Transformation", "Compassion", "Research ability", "Truthful"],
        "challenges": ["Destructive tendencies", "Ingratitude", "Arrogance"],
        "career": ["Software", "Electrical work", "Pharmaceuticals", "Research", "Psychology"]
    },

    "Punarvasu": {
        "index": 7,
        "deity": "Aditi (Mother of Gods)",
        "symbol": "Bow and Quiver",
        "ruling_planet": "Jupiter",
        "element": "Water",
        "guna": "Sattva",
        "animal": "Cat",
        "lucky_color": "Yellow",
        "lucky_number": 3,
        "lucky_stone": "Yellow Sapphire",
        "personality": "You have the gift of renewal and restoration. Like Aditi, you are nurturing and can provide safe haven for others. You bounce back from setbacks and help others do the same.",
        "strengths": ["Resilience", "Nurturing", "Wisdom", "Optimism", "Philosophical"],
        "challenges": ["Over-simplification", "Lack of ambition", "Indecision"],
        "career": ["Teaching", "Counseling", "Writing", "Import/Export", "Spirituality"]
    },

    "Pushya": {
        "index": 8,
        "deity": "Brihaspati (Jupiter/Divine Priest)",
        "symbol": "Lotus/Cow's Udder",
        "ruling_planet": "Saturn",
        "element": "Water",
        "guna": "Tamas",
        "animal": "Goat",
        "lucky_color": "Black/Dark Blue",
        "lucky_number": 8,
        "lucky_stone": "Blue Sapphire",
        "personality": "You are considered the most auspicious nakshatra. Like Brihaspati, you embody wisdom, nourishment, and spiritual growth. Your presence brings blessings to others.",
        "strengths": ["Nourishing", "Wise", "Generous", "Spiritual", "Stable"],
        "challenges": ["Over-cautious", "Stubbornness", "Orthodoxy"],
        "career": ["Politics", "Priesthood", "Dairy", "Counseling", "Management"]
    },

    "Ashlesha": {
        "index": 9,
        "deity": "Nagas (Serpent Deities)",
        "symbol": "Coiled Serpent",
        "ruling_planet": "Mercury",
        "element": "Water",
        "guna": "Sattva",
        "animal": "Cat",
        "lucky_color": "Black-Red",
        "lucky_number": 5,
        "lucky_stone": "Emerald",
        "personality": "You possess the mystical energy of the serpent. With deep intuition and psychological insight, you can see beneath the surface. You have kundalini power and hypnotic presence.",
        "strengths": ["Intuition", "Mystical abilities", "Hypnotic", "Shrewd", "Leadership"],
        "challenges": ["Deception", "Manipulation", "Coldness"],
        "career": ["Psychology", "Occult", "Politics", "Law", "Petroleum"]
    },

    "Magha": {
        "index": 10,
        "deity": "Pitris (Ancestors)",
        "symbol": "Royal Throne",
        "ruling_planet": "Ketu",
        "element": "Water",
        "guna": "Tamas",
        "animal": "Rat",
        "lucky_color": "Ivory/Cream",
        "lucky_number": 7,
        "lucky_stone": "Cat's Eye",
        "personality": "You carry the power of royalty and ancestral blessings. Magha connects you to your lineage and gives you natural authority. You are noble and generous with leadership qualities.",
        "strengths": ["Leadership", "Nobility", "Generosity", "Respect for tradition", "Authority"],
        "challenges": ["Arrogance", "Attachment to status", "Domineering"],
        "career": ["Government", "Administration", "History", "Archaeology", "Family business"]
    },

    "Purva Phalguni": {
        "index": 11,
        "deity": "Bhaga (God of Delight)",
        "symbol": "Hammock/Front legs of bed",
        "ruling_planet": "Venus",
        "element": "Water",
        "guna": "Rajas",
        "animal": "Rat",
        "lucky_color": "Light Brown",
        "lucky_number": 6,
        "lucky_stone": "Diamond",
        "personality": "You are blessed with the energy of pleasure, relaxation, and creative expression. Bhaga gives you the ability to enjoy life's pleasures and share joy with others.",
        "strengths": ["Charisma", "Creativity", "Generosity", "Romantic", "Artistic"],
        "challenges": ["Laziness", "Vanity", "Over-indulgence"],
        "career": ["Entertainment", "Arts", "Photography", "Cosmetics", "Event planning"]
    },

    "Uttara Phalguni": {
        "index": 12,
        "deity": "Aryaman (God of Patronage)",
        "symbol": "Back legs of bed",
        "ruling_planet": "Sun",
        "element": "Fire",
        "guna": "Rajas",
        "animal": "Bull",
        "lucky_color": "Bright Blue",
        "lucky_number": 1,
        "lucky_stone": "Ruby",
        "personality": "You embody leadership through service and patronage. Aryaman blesses you with the ability to help others rise. You are warm, generous, and have strong organizational abilities.",
        "strengths": ["Leadership", "Service", "Warmth", "Organizational skills", "Reliability"],
        "challenges": ["Stubbornness", "Resentment", "Over-confidence"],
        "career": ["Social work", "HR", "Healing", "Marriage counseling", "Administration"]
    },

    "Hasta": {
        "index": 13,
        "deity": "Savitar (Sun God of creativity)",
        "symbol": "Hand/Palm",
        "ruling_planet": "Moon",
        "element": "Fire",
        "guna": "Rajas",
        "animal": "Buffalo",
        "lucky_color": "Deep Green",
        "lucky_number": 2,
        "lucky_stone": "Pearl",
        "personality": "You have skilled hands and a clever mind. Savitar blesses you with the ability to manifest your ideas into reality. You are dexterous, witty, and have healing abilities.",
        "strengths": ["Skill", "Cleverness", "Healing hands", "Wit", "Resourceful"],
        "challenges": ["Cunning", "Selfishness", "Over-criticism"],
        "career": ["Crafts", "Healing arts", "Comedy", "Astrology", "Magic/Illusion"]
    },

    "Chitra": {
        "index": 14,
        "deity": "Vishwakarma (Divine Architect)",
        "symbol": "Bright Jewel/Pearl",
        "ruling_planet": "Mars",
        "element": "Fire",
        "guna": "Tamas",
        "animal": "Tiger",
        "lucky_color": "Black",
        "lucky_number": 9,
        "lucky_stone": "Red Coral",
        "personality": "You are the cosmic artist, blessed by the divine architect. Chitra gives you the ability to create beautiful and lasting works. You have an eye for aesthetics.",
        "strengths": ["Artistic vision", "Structural thinking", "Charisma", "Elegance", "Dynamic"],
        "challenges": ["Vanity", "Self-centeredness", "Judgmental"],
        "career": ["Architecture", "Design", "Fashion", "Jewelry", "Engineering"]
    },

    "Swati": {
        "index": 15,
        "deity": "Vayu (Wind God)",
        "symbol": "Shoot of plant/Coral",
        "ruling_planet": "Rahu",
        "element": "Fire",
        "guna": "Tamas",
        "animal": "Buffalo",
        "lucky_color": "Black",
        "lucky_number": 4,
        "lucky_stone": "Hessonite (Gomed)",
        "personality": "You carry the free-flowing energy of the wind. Swati gives you independence, flexibility, and the ability to adapt to any situation. Like a young plant, you are resilient.",
        "strengths": ["Independence", "Adaptability", "Diplomacy", "Business acumen", "Fairness"],
        "challenges": ["Restlessness", "Indecision", "Scattered energy"],
        "career": ["Business", "Trade", "Law", "Politics", "Travel industry"]
    },

    "Vishakha": {
        "index": 16,
        "deity": "Indra-Agni (Chief Gods)",
        "symbol": "Triumphal Gateway/Potter's Wheel",
        "ruling_planet": "Jupiter",
        "element": "Fire",
        "guna": "Sattva",
        "animal": "Tiger",
        "lucky_color": "Golden Yellow",
        "lucky_number": 3,
        "lucky_stone": "Yellow Sapphire",
        "personality": "You are blessed with determination and the energy to achieve your goals. The combined power of Indra and Agni gives you ambition and fire to succeed through persistence.",
        "strengths": ["Determination", "Goal-oriented", "Courage", "Intelligence", "Leadership"],
        "challenges": ["Jealousy", "Frustration", "Quarrelsome"],
        "career": ["Military", "Research", "Politics", "Business leadership", "Religion"]
    },

    "Anuradha": {
        "index": 17,
        "deity": "Mitra (God of Friendship)",
        "symbol": "Lotus/Triumphant Gateway",
        "ruling_planet": "Saturn",
        "element": "Fire",
        "guna": "Tamas",
        "animal": "Deer",
        "lucky_color": "Reddish Brown",
        "lucky_number": 8,
        "lucky_stone": "Blue Sapphire",
        "personality": "You embody the spirit of friendship and cooperation. Mitra blesses you with the ability to form lasting bonds. You are devoted, hardworking, and can succeed in foreign lands.",
        "strengths": ["Friendship", "Devotion", "Organization", "Success abroad", "Cooperation"],
        "challenges": ["Jealousy", "Controlling", "Melancholy"],
        "career": ["Organizations", "Travel", "Mining", "Statistics", "Occult sciences"]
    },

    "Jyeshtha": {
        "index": 18,
        "deity": "Indra (King of Gods)",
        "symbol": "Umbrella/Earring",
        "ruling_planet": "Mercury",
        "element": "Air",
        "guna": "Sattva",
        "animal": "Deer",
        "lucky_color": "Cream",
        "lucky_number": 5,
        "lucky_stone": "Emerald",
        "personality": "You carry the energy of the chief, the eldest, the most powerful. Indra gives you protective abilities and leadership qualities. You can be a defender of the weak.",
        "strengths": ["Protective", "Courageous", "Resourceful", "Intelligent", "Generous"],
        "challenges": ["Arrogance", "Premature aging", "Hidden anger"],
        "career": ["Military", "Police", "Government", "Occult", "Antiques"]
    },

    "Mula": {
        "index": 19,
        "deity": "Nirrti (Goddess of Dissolution)",
        "symbol": "Bunch of roots/Lion's tail",
        "ruling_planet": "Ketu",
        "element": "Air",
        "guna": "Tamas",
        "animal": "Dog",
        "lucky_color": "Brown-Yellow",
        "lucky_number": 7,
        "lucky_stone": "Cat's Eye",
        "personality": "You are connected to the root of existence. Mula gives you the power to get to the bottom of things, to uproot and transform. You are a seeker of truth.",
        "strengths": ["Truth-seeking", "Investigation", "Spiritual depth", "Independence", "Determination"],
        "challenges": ["Destruction", "Arrogance", "Self-destruction"],
        "career": ["Research", "Medicine", "Herbalism", "Philosophy", "Investigation"]
    },

    "Purva Ashadha": {
        "index": 20,
        "deity": "Apas (Water Goddess)",
        "symbol": "Elephant tusk/Fan",
        "ruling_planet": "Venus",
        "element": "Air",
        "guna": "Rajas",
        "animal": "Monkey",
        "lucky_color": "Black",
        "lucky_number": 6,
        "lucky_stone": "Diamond",
        "personality": "You have the invincible spirit that leads to victory. Apas blesses you with purification and rejuvenation abilities. You are proud and can influence others.",
        "strengths": ["Invincibility", "Influence", "Pride", "Intelligence", "Purification"],
        "challenges": ["Over-confidence", "Uncompromising", "Boastful"],
        "career": ["Shipping", "Water-related", "Entertainment", "Law", "Debate"]
    },

    "Uttara Ashadha": {
        "index": 21,
        "deity": "Vishvadevas (Universal Gods)",
        "symbol": "Elephant tusk/Small bed",
        "ruling_planet": "Sun",
        "element": "Air",
        "guna": "Rajas",
        "animal": "Mongoose",
        "lucky_color": "Copper",
        "lucky_number": 1,
        "lucky_stone": "Ruby",
        "personality": "You carry the energy of final victory after long effort. The Universal Gods bless you with qualities that make you unstoppable once you commit. Sincere and deeply grateful.",
        "strengths": ["Final victory", "Sincerity", "Commitment", "Gratitude", "Leadership"],
        "challenges": ["Multiple marriages", "Loneliness", "Apathetic"],
        "career": ["Government", "Military leadership", "Psychology", "Pioneering work"]
    },

    "Shravana": {
        "index": 22,
        "deity": "Vishnu (The Preserver)",
        "symbol": "Ear/Three footprints",
        "ruling_planet": "Moon",
        "element": "Air",
        "guna": "Rajas",
        "animal": "Monkey",
        "lucky_color": "Light Blue",
        "lucky_number": 2,
        "lucky_stone": "Pearl",
        "personality": "You are the listener, the one who receives divine knowledge. Vishnu blesses you with the ability to preserve and protect wisdom. You learn through hearing.",
        "strengths": ["Listening", "Learning", "Teaching", "Connection", "Preservation"],
        "challenges": ["Gossip", "Over-sensitivity", "Narrow-mindedness"],
        "career": ["Teaching", "Media", "Counseling", "Music", "Languages"]
    },

    "Dhanishta": {
        "index": 23,
        "deity": "Vasus (Eight elemental Gods)",
        "symbol": "Drum/Flute",
        "ruling_planet": "Mars",
        "element": "Ether",
        "guna": "Tamas",
        "animal": "Lion",
        "lucky_color": "Silver Grey",
        "lucky_number": 9,
        "lucky_stone": "Red Coral",
        "personality": "You resonate with the rhythm of the cosmos. The Vasus bless you with wealth, fame, and musical abilities. You are ambitious and can achieve great abundance.",
        "strengths": ["Wealth", "Fame", "Musical ability", "Adaptability", "Ambition"],
        "challenges": ["Materialism", "Carelessness", "Aggression"],
        "career": ["Music", "Real estate", "Surgery", "Sports", "Technology"]
    },

    "Shatabhisha": {
        "index": 24,
        "deity": "Varuna (God of Cosmic Waters)",
        "symbol": "Empty circle/100 flowers",
        "ruling_planet": "Rahu",
        "element": "Ether",
        "guna": "Tamas",
        "animal": "Horse",
        "lucky_color": "Blue-Green",
        "lucky_number": 4,
        "lucky_stone": "Hessonite (Gomed)",
        "personality": "You are the hundred healers in one. Varuna gives you the power to heal and access secret knowledge. You are a mystic who achieves extraordinary insights.",
        "strengths": ["Healing", "Mystical knowledge", "Independence", "Truthfulness", "Persistence"],
        "challenges": ["Loneliness", "Secrecy", "Addictions"],
        "career": ["Healing", "Astrology", "Space science", "Electricity", "Research"]
    },

    "Purva Bhadrapada": {
        "index": 25,
        "deity": "Aja Ekapada (One-footed Goat)",
        "symbol": "Sword/Two-faced man",
        "ruling_planet": "Jupiter",
        "element": "Ether",
        "guna": "Sattva",
        "animal": "Lion",
        "lucky_color": "Silver Grey",
        "lucky_number": 3,
        "lucky_stone": "Yellow Sapphire",
        "personality": "You carry the fire of transformation and spiritual evolution. This fierce nakshatra gives you the power to burn away negativity. You are intense and deeply spiritual.",
        "strengths": ["Spiritual fire", "Transformation", "Passion", "Intelligence", "Wealth"],
        "challenges": ["Cynicism", "Dark moods", "Impulsiveness"],
        "career": ["Occult", "Astrology", "Death-related", "Metal work", "Spiritual teaching"]
    },

    "Uttara Bhadrapada": {
        "index": 26,
        "deity": "Ahir Budhnya (Serpent of the Depths)",
        "symbol": "Twins/Back legs of funeral cot",
        "ruling_planet": "Saturn",
        "element": "Ether",
        "guna": "Tamas",
        "animal": "Cow",
        "lucky_color": "Purple",
        "lucky_number": 8,
        "lucky_stone": "Blue Sapphire",
        "personality": "You have access to the deepest wisdom of the cosmos. The serpent of the depths gives you kundalini power and ability to access hidden knowledge. Wise and spiritually powerful.",
        "strengths": ["Deep wisdom", "Kundalini power", "Compassion", "Endurance", "Spirituality"],
        "challenges": ["Laziness", "Irresponsibility", "Aloofness"],
        "career": ["Yoga", "Charity", "Imports", "Non-profit", "Philosophy"]
    },

    "Revati": {
        "index": 27,
        "deity": "Pushan (Nourisher/Protector of travelers)",
        "symbol": "Fish/Drum",
        "ruling_planet": "Mercury",
        "element": "Ether",
        "guna": "Sattva",
        "animal": "Elephant",
        "lucky_color": "Brown",
        "lucky_number": 5,
        "lucky_stone": "Emerald",
        "personality": "You are the final nakshatra, representing completion and the journey home. Pushan blesses you with the ability to guide and nourish others. Compassionate and protective.",
        "strengths": ["Compassion", "Creativity", "Protection", "Nourishment", "Spiritual completion"],
        "challenges": ["Over-giving", "Disappointment", "Stubbornness"],
        "career": ["Travel", "Orphanages", "Spirituality", "Entertainment", "Time-keeping"]
    }
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_timezone_from_coords(lat: float, lng: float) -> str:
    """Get timezone string from coordinates"""
    if _use_tzfpy:
        try:
            # tzfpy uses (longitude, latitude) order
            tz = get_tz(lng, lat)
            return tz or "Asia/Kolkata"
        except:
            pass
    
    # Fallback: Simple lookup for India (most users)
    # India spans roughly 68-97°E longitude
    if 68 <= lng <= 97 and 8 <= lat <= 37:
        return "Asia/Kolkata"
    
    # Basic fallback for other regions
    if lng < -30:
        return "America/New_York"  # Americas
    elif lng < 30:
        return "Europe/London"  # Europe/Africa
    elif lng < 60:
        return "Europe/Moscow"  # Middle East
    elif lng < 100:
        return "Asia/Kolkata"  # South Asia
    else:
        return "Asia/Shanghai"  # East Asia
    
    return "UTC"


def format_time(hours: float) -> str:
    """Convert decimal hours to HH:MM format"""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h:02d}:{m:02d}"


def get_rashi_name(index: int) -> str:
    """Get Rashi name from index (0-11)"""
    return RASHI_NAMES[index % 12]


def get_rashi_name_short(index: int) -> str:
    """Get short Rashi name from index (0-11)"""
    return RASHI_NAMES_SHORT[index % 12]


def get_nakshatra_name(index: int) -> str:
    """Get Nakshatra name from index (0-26)"""
    return NAKSHATRA_NAMES[index % 27]


def get_nakshatra_data(name: str) -> Optional[Dict]:
    """Get nakshatra interpretation data by name"""
    return NAKSHATRAS.get(name)


def get_nakshatra_by_index(index: int) -> Dict:
    """Get nakshatra data by index (1-27)"""
    names = list(NAKSHATRAS.keys())
    idx = (index - 1) % 27
    name = names[idx]
    return {"name": name, **NAKSHATRAS[name]}


# =============================================================================
# MAIN CALCULATION CLASS
# =============================================================================

class JyotishEngine:
    """
    Main Jyotish calculation engine
    Wraps PyJHora with a clean API
    """

    def __init__(self):
        """Initialize the engine"""
        pass  # PyJHora doesn't need initialization

    def _create_place(self, location: Location):
        """Create PyJHora Place object"""
        return drik.Place(
            location.name,
            location.latitude,
            location.longitude,
            location.tz_offset
        )

    def _get_julian_day(self, birth: BirthData) -> float:
        """Get Julian Day number from birth data"""
        dob = (birth.year, birth.month, birth.day)
        tob = (birth.hour, birth.minute, 0)
        return utils.julian_day_number(dob, tob)

    # -------------------------------------------------------------------------
    # PANCHANGA
    # -------------------------------------------------------------------------

    def calculate_panchanga(self, date: datetime, location: Location) -> Dict[str, Any]:
        """
        Calculate Panchanga for a given date and location

        Returns dict with tithi, nakshatra, sunrise, sunset, rahu_kala
        """
        place = self._create_place(location)
        dob = (date.year, date.month, date.day)
        tob = (date.hour, date.minute, 0)
        jd = utils.julian_day_number(dob, tob)

        # Calculate elements
        tithi_data = drik.tithi(jd, place)
        nakshatra_data = drik.nakshatra(jd, place)
        karana_data = drik.karana(jd, place)
        sunrise_data = drik.sunrise(jd, place)
        sunset_data = drik.sunset(jd, place)
        rahu_kala = drik.raahu_kaalam(jd, place)

        # Parse tithi
        tithi_index = _safe_int(_get_value(tithi_data, 0), 1) - 1
        tithi_name = TITHI_NAMES[tithi_index % 15]
        paksha = "Shukla" if tithi_index < 15 else "Krishna"

        # Parse nakshatra
        nak_index = _safe_int(_get_value(nakshatra_data, 0), 1) - 1
        nak_pada = _safe_int(_get_value(nakshatra_data, 1), 1)

        return {
            "tithi": {
                "index": tithi_index + 1,
                "name": tithi_name,
                "paksha": paksha
            },
            "nakshatra": {
                "index": nak_index + 1,
                "name": get_nakshatra_name(nak_index),
                "pada": nak_pada
            },
            "karana": {
                "index": _safe_int(_get_value(karana_data, 0), 1),
            },
            "sunrise": format_time(_safe_float(_get_value(sunrise_data, 0), 6.0)),
            "sunset": format_time(_safe_float(_get_value(sunset_data, 0), 18.0)),
            "rahu_kala": f"{format_time(_safe_float(_get_value(rahu_kala, 0), 7.5))} - {format_time(_safe_float(_get_value(rahu_kala, 1), 9.0))}" if rahu_kala else ""
        }

    # -------------------------------------------------------------------------
    # BIRTH CHART
    # -------------------------------------------------------------------------

    def calculate_chart(self, birth: BirthData) -> Dict[str, Any]:
        """
        Calculate birth chart (Kundali)

        Returns dict with ascendant, moon_sign, sun_sign, nakshatra, planets
        """
        import logging
        logger = logging.getLogger(__name__)
        
        place = self._create_place(birth.location)
        jd = self._get_julian_day(birth)
        
        logger.info(f"PyJHora: place={place}, jd={jd}")

        # Ascendant
        asc_data = drik.ascendant(jd, place)
        logger.info(f"PyJHora ascendant raw: {asc_data}, type: {type(asc_data)}")
        logger.info(f"Ascendant elements: [0]={_get_value(asc_data, 0)}, [1]={_get_value(asc_data, 1)}, [2]={_get_value(asc_data, 2)}, [3]={_get_value(asc_data, 3)}")
        
        # PyJHora ascendant format: [constellation (0-indexed), degree, nakshatra (1-indexed), pada]
        asc_rashi = _safe_int(_get_value(asc_data, 0), 0)  # 0-indexed, no subtraction needed
        asc_degree = _safe_float(_get_value(asc_data, 1), 0)
        
        logger.info(f"Parsed ascendant: rashi_index={asc_rashi} ({get_rashi_name_short(asc_rashi)}), degree={asc_degree}")

        # All planet positions
        planet_positions = drik.planetary_positions(jd, place)
        logger.info(f"PyJHora planets raw: {planet_positions}, type: {type(planet_positions)}")

        planets = {}
        moon_data = None
        sun_data = None

        for i, name in enumerate(PLANET_NAMES):
            if i < len(planet_positions):
                pos = planet_positions[i]
                logger.debug(f"Planet {name} raw pos: {pos}")
                
                # PyJHora format: [planet_index, degree, rashi_index]
                # rashi_index is at position 2, already 0-indexed
                degree = _safe_float(_get_value(pos, 1), 0)
                rashi_index = _safe_int(_get_value(pos, 2), 0)  # Use index 2, no -1 needed

                # Calculate nakshatra from absolute longitude
                abs_long = rashi_index * 30 + degree
                nak_index = int(abs_long / 13.333) % 27

                planets[name] = {
                    "rashi_index": rashi_index,
                    "rashi": get_rashi_name(rashi_index),
                    "rashi_short": get_rashi_name_short(rashi_index),
                    "degree": round(degree, 2),
                    "nakshatra": get_nakshatra_name(nak_index)
                }

                if name == "Moon":
                    moon_data = planets[name]
                elif name == "Sun":
                    sun_data = planets[name]

        # Moon's nakshatra (for predictions)
        moon_long = (moon_data["rashi_index"] * 30 + moon_data["degree"]) if moon_data else 0
        moon_nak_index = int(moon_long / 13.333) % 27
        moon_nak_pada = int((moon_long % 13.333) / 3.333) + 1

        return {
            "ascendant": {
                "rashi_index": asc_rashi,
                "rashi": get_rashi_name(asc_rashi),
                "rashi_short": get_rashi_name_short(asc_rashi),
                "degree": round(asc_degree, 2)
            },
            "moon_sign": {
                "rashi_index": moon_data["rashi_index"] if moon_data else 0,
                "rashi": moon_data["rashi"] if moon_data else "Unknown",
                "rashi_short": moon_data["rashi_short"] if moon_data else "Unknown"
            },
            "sun_sign": {
                "rashi_index": sun_data["rashi_index"] if sun_data else 0,
                "rashi": sun_data["rashi"] if sun_data else "Unknown",
                "rashi_short": sun_data["rashi_short"] if sun_data else "Unknown"
            },
            "nakshatra": {
                "index": moon_nak_index + 1,
                "name": get_nakshatra_name(moon_nak_index),
                "pada": moon_nak_pada
            },
            "planets": planets
        }

    # -------------------------------------------------------------------------
    # DASHA
    # -------------------------------------------------------------------------

    def calculate_dasha(self, birth: BirthData, num_periods: int = 10) -> Dict[str, Any]:
        """
        Calculate Vimshottari Dasha

        Returns dict with current_mahadasha, current_antardasha, upcoming_periods
        """
        import logging
        from datetime import datetime
        logger = logging.getLogger(__name__)
        
        place = self._create_place(birth.location)
        jd = self._get_julian_day(birth)

        try:
            dasha_data = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
            logger.info(f"PyJHora dasha raw type: {type(dasha_data)}, len: {len(dasha_data) if dasha_data else 0}")
            if dasha_data:
                logger.info(f"Dasha[0] (metadata): {dasha_data[0]}")
                if len(dasha_data) > 1:
                    logger.info(f"Dasha[1] (periods, first 3): {dasha_data[1][:3] if isinstance(dasha_data[1], list) else dasha_data[1]}")
        except Exception as e:
            logger.error(f"Dasha calculation error: {e}")
            return {
                "current_mahadasha": {"lord": "Unknown", "start": "", "end": ""},
                "current_antardasha": {"lord": "Unknown", "start": "", "end": ""},
                "upcoming_periods": []
            }

        if not dasha_data or len(dasha_data) < 2:
            return {
                "current_mahadasha": {"lord": "Unknown"},
                "current_antardasha": {"lord": "Unknown"},
                "upcoming_periods": []
            }

        # dasha_data[0] is metadata tuple, dasha_data[1] is list of periods
        # Period format: [mahadasha_lord_index, antardasha_lord_index, 'YYYY-MM-DD HH:MM:SS']
        periods = dasha_data[1] if isinstance(dasha_data[1], list) else []
        
        # Dasha lord indices: 0=Sun, 1=Moon, 2=Mars, 3=Mercury, 4=Jupiter, 5=Venus, 6=Saturn, 7=Rahu, 8=Ketu
        dasha_lords = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        
        # Find current period based on today's date
        today = datetime.now()
        logger.info(f"Finding current dasha for today: {today.strftime('%Y-%m-%d')}")
        
        current_md = None
        current_ad = None
        upcoming = []
        
        for i, period in enumerate(periods):
            if len(period) >= 3:
                md_idx = _safe_int(period[0], 0)
                ad_idx = _safe_int(period[1], 0)
                start_str = str(period[2])
                
                try:
                    # Parse the date
                    start_date = datetime.strptime(start_str.split()[0], "%Y-%m-%d")
                except:
                    start_date = None
                
                md_lord = dasha_lords[md_idx % 9]
                ad_lord = dasha_lords[ad_idx % 9]
                
                # Get end date from next period
                end_str = ""
                if i + 1 < len(periods) and len(periods[i + 1]) >= 3:
                    end_str = str(periods[i + 1][2]).split()[0]
                
                period_info = {
                    "mahadasha": md_lord,
                    "antardasha": ad_lord,
                    "start": start_str.split()[0] if start_str else "",
                    "end": end_str
                }
                
                # Check if this is current period
                if start_date and start_date <= today:
                    # Check if next period hasn't started yet
                    if i + 1 < len(periods) and len(periods[i + 1]) >= 3:
                        try:
                            next_start = datetime.strptime(str(periods[i + 1][2]).split()[0], "%Y-%m-%d")
                            if next_start > today:
                                current_md = {"lord": md_lord, "start": start_str.split()[0], "end": end_str}
                                current_ad = {"lord": ad_lord, "start": start_str.split()[0], "end": end_str}
                        except:
                            pass
                
                # Add to upcoming if in future
                if start_date and start_date > today and len(upcoming) < num_periods:
                    upcoming.append(period_info)
        
        # Fallback if current not found
        if not current_md and periods:
            md_idx = _safe_int(periods[0][0], 0)
            ad_idx = _safe_int(periods[0][1], 0)
            current_md = {"lord": dasha_lords[md_idx % 9]}
            current_ad = {"lord": dasha_lords[ad_idx % 9]}
        
        logger.info(f"Current dasha: {current_md}, {current_ad}")

        return {
            "current_mahadasha": current_md or {"lord": "Unknown"},
            "current_antardasha": current_ad or {"lord": "Unknown"},
            "upcoming_periods": upcoming
        }

    # -------------------------------------------------------------------------
    # FULL ANALYSIS
    # -------------------------------------------------------------------------

    def full_analysis(self, birth: BirthData) -> Dict[str, Any]:
        """
        Complete birth chart analysis

        Returns comprehensive analysis dictionary
        """
        chart = self.calculate_chart(birth)
        dasha = self.calculate_dasha(birth)
        panchanga = self.calculate_panchanga(birth.datetime, birth.location)

        # Get nakshatra interpretation
        nak_name = chart["nakshatra"]["name"]
        nak_info = get_nakshatra_data(nak_name) or {}

        return {
            "name": birth.name,
            "birth_details": {
                "date": f"{birth.day:02d}/{birth.month:02d}/{birth.year}",
                "time": f"{birth.hour:02d}:{birth.minute:02d}",
                "place": birth.location.name
            },
            "chart": chart,
            "dasha": dasha,
            "panchanga": panchanga,
            "nakshatra_info": nak_info
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Create a singleton engine instance
_engine = JyotishEngine()


def get_engine() -> JyotishEngine:
    """Get the Jyotish engine instance"""
    return _engine


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def calculate_birth_chart(
    name: str,
    year: int, month: int, day: int,
    hour: int, minute: int,
    place_name: str,
    latitude: float,
    longitude: float,
    timezone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to calculate birth chart

    Args:
        name: Person's name
        year, month, day: Birth date
        hour, minute: Birth time (24-hour)
        place_name: Birth place name
        latitude, longitude: Coordinates
        timezone: Optional timezone (auto-detected if not provided)

    Returns:
        Complete analysis dictionary
    """
    if timezone is None:
        timezone = get_timezone_from_coords(latitude, longitude)

    location = Location(
        name=place_name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone
    )

    birth = BirthData(
        name=name,
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        location=location
    )

    return _engine.full_analysis(birth)


def get_today_panchanga(
    latitude: float = 19.0760,
    longitude: float = 72.8777,
    place_name: str = "Mumbai",
    timezone: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get today's panchanga for a location

    Args:
        latitude, longitude: Coordinates (default: Mumbai)
        place_name: Location name
        timezone: Optional timezone

    Returns:
        Panchanga dictionary
    """
    if timezone is None:
        timezone = get_timezone_from_coords(latitude, longitude)

    location = Location(
        name=place_name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone
    )

    return _engine.calculate_panchanga(datetime.now(), location)