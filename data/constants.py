# =============================================================================
# CONSTANTS
# =============================================================================

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
# END OF FILE
# =============================================================================