"""
VedAstro XML Query Helper
Direct access to VedAstro interpretation data

Usage:
    from data.vedastro import vedastro
    
    result = vedastro.get_planet_in_sign("Sun", "Aries")
    print(result["description"])
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


class VedAstroXML:
    """Direct XML query for VedAstro data files"""
    
    def __init__(self, horoscope_file: str = None, event_file: str = None):
        self.horoscope_tree = None
        self.event_tree = None
        
        if horoscope_file and Path(horoscope_file).exists():
            self.horoscope_tree = ET.parse(horoscope_file)
        
        if event_file and Path(event_file).exists():
            self.event_tree = ET.parse(event_file)
    
    def get_prediction(self, name: str) -> Optional[dict]:
        """Get any prediction by name from either file"""
        
        # Search horoscope file first
        if self.horoscope_tree:
            for event in self.horoscope_tree.findall('.//Event'):
                name_elem = event.find('Name')
                if name_elem is not None and name_elem.text == name:
                    return self._parse_event(event)
        
        # Then search event file
        if self.event_tree:
            for event in self.event_tree.findall('.//Event'):
                name_elem = event.find('Name')
                if name_elem is not None and name_elem.text == name:
                    return self._parse_event(event)
        
        return None
    
    def _parse_event(self, event) -> dict:
        """Extract fields from an Event element"""
        return {
            "name": self._get_text(event, 'Name'),
            "nature": self._get_text(event, 'Nature'),
            "description": self._get_text(event, 'Description'),
            "tag": self._get_text(event, 'Tag'),
            "condition": self._get_text(event, 'ConditionDescription'),
        }
    
    def _get_text(self, event, tag: str) -> str:
        """Safely get text from an element"""
        elem = event.find(tag)
        if elem is not None and elem.text:
            return ' '.join(elem.text.split())  # Clean whitespace
        return ""
    
    # =========================================================================
    # HOROSCOPE QUERIES
    # =========================================================================
    
    def get_planet_in_sign(self, planet: str, sign: str) -> Optional[dict]:
        """
        Get interpretation for planet in sign
        
        Args:
            planet: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
            sign: Aries, Taurus, Gemini, Cancer, Leo, Virgo, 
                  Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces
        """
        return self.get_prediction(f"{planet}In{sign}")
    
    def get_house_lord(self, from_house: int, to_house: int) -> Optional[dict]:
        """
        Get interpretation for house lord placement
        
        Args:
            from_house: 1-12 (which house's lord)
            to_house: 1-12 (placed in which house)
        """
        return self.get_prediction(f"House{from_house}LordInHouse{to_house}")
    
    def get_yoga(self, yoga_name: str) -> Optional[dict]:
        """Get a specific yoga by name"""
        return self.get_prediction(yoga_name)
    
    # =========================================================================
    # EVENT/MUHURTHA QUERIES
    # =========================================================================
    
    def get_dasha_effect(self, sign: str, planet: str, level: int = 1) -> Optional[dict]:
        """
        Get dasha period effect
        
        Args:
            sign: Sign where planet is placed
            planet: Dasha lord planet
            level: PD level (1-8)
        """
        return self.get_prediction(f"{sign}{planet}PD{level}")
    
    def get_muhurtha(self, name: str) -> Optional[dict]:
        """Get specific muhurtha event"""
        return self.get_prediction(name)
    
    # =========================================================================
    # SEARCH FUNCTIONS
    # =========================================================================
    
    def search_by_tag(self, tag: str) -> list:
        """
        Find all events with a specific tag
        
        Tags: Yoga, Travel, Marriage, Building, Agriculture, Medical, 
              Gochara, Tarabala, Personal, Horoscope, etc.
        """
        results = []
        
        for tree in [self.horoscope_tree, self.event_tree]:
            if tree:
                for event in tree.findall('.//Event'):
                    tag_elem = event.find('Tag')
                    if tag_elem is not None and tag in (tag_elem.text or ""):
                        results.append(self._parse_event(event))
        
        return results
    
    def search_description(self, keyword: str) -> list:
        """Search events by keyword in description"""
        keyword = keyword.lower()
        results = []
        
        for tree in [self.horoscope_tree, self.event_tree]:
            if tree:
                for event in tree.findall('.//Event'):
                    desc_elem = event.find('Description')
                    if desc_elem is not None and desc_elem.text:
                        if keyword in desc_elem.text.lower():
                            results.append(self._parse_event(event))
        
        return results
    
    def get_all_yogas(self) -> list:
        """Get all yogas"""
        return self.search_by_tag("Yoga")
    
    def get_good_events(self, tag: str = None) -> list:
        """Get events with 'Good' nature, optionally filtered by tag"""
        if tag:
            events = self.search_by_tag(tag)
        else:
            events = []
            for tree in [self.horoscope_tree, self.event_tree]:
                if tree:
                    for event in tree.findall('.//Event'):
                        events.append(self._parse_event(event))
        
        return [e for e in events if e.get("nature") == "Good"]
    
    def get_bad_events(self, tag: str = None) -> list:
        """Get events with 'Bad' nature, optionally filtered by tag"""
        if tag:
            events = self.search_by_tag(tag)
        else:
            events = []
            for tree in [self.horoscope_tree, self.event_tree]:
                if tree:
                    for event in tree.findall('.//Event'):
                        events.append(self._parse_event(event))
        
        return [e for e in events if e.get("nature") == "Bad"]


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Auto-load from data/ folder (adjust paths as needed)
_data_dir = Path(__file__).parent

vedastro = VedAstroXML(
    horoscope_file=str(_data_dir / "HoroscopeDataList.xml"),
    event_file=str(_data_dir / "EventDataList.xml")
)