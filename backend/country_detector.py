# DesiFriend AI - Country Detector Module
"""
Country detection module for DesiFriend AI.
Detects user's country from device locale or IP address to adapt voice accent.
"""

import requests
from typing import Optional
import re


class CountryDetector:
    """
    Detects the user's country for accent adaptation.
    Supports detection via device locale and IP-based geolocation.
    """
    
    # Supported countries for accent adaptation
    SUPPORTED_COUNTRIES = {
        'IN': 'India',
        'US': 'USA',
        'GB': 'UK',
        'OTHER': 'Other'
    }
    
    def __init__(self):
        """Initialize the Country Detector."""
        self.geolocation_api = "https://ipapi.co/{}/json/"
    
    def detect_country(self, device_locale: Optional[str] = None, 
                      ip_address: Optional[str] = None) -> str:
        """
        Detect the user's country from device locale or IP address.
        
        Args:
            device_locale: Device locale string (e.g., 'en-IN', 'en-US', 'en-GB')
            ip_address: User's IP address for geolocation fallback
            
        Returns:
            Country code: 'IN', 'US', 'GB', or 'OTHER'
        """
        # Try device locale first
        if device_locale:
            country_code = self._parse_locale(device_locale)
            if country_code in ['IN', 'US', 'GB']:
                return country_code
        
        # Fallback to IP-based geolocation
        if ip_address:
            country_code = self._detect_by_ip(ip_address)
            if country_code in ['IN', 'US', 'GB']:
                return country_code
        
        # Default to India (Indian accent)
        return 'IN'
    
    def _parse_locale(self, locale: str) -> Optional[str]:
        """
        Parse device locale string to extract country code.
        
        Args:
            locale: Locale string (e.g., 'en-IN', 'en_US', 'en-GB')
            
        Returns:
            Country code or None if parsing fails
        """
        if not locale:
            return None
        
        # Common locale formats: en-IN, en_IN, en-US, en_US, etc.
        # Extract the country code (last 2 characters after separator)
        match = re.search(r'[-_]([A-Z]{2})$', locale.upper())
        if match:
            country_code = match.group(1)
            # Map common variations
            if country_code == 'UK':
                return 'GB'
            return country_code
        
        return None
    
    def _detect_by_ip(self, ip_address: str) -> Optional[str]:
        """
        Detect country using IP-based geolocation.
        
        Args:
            ip_address: User's IP address
            
        Returns:
            Country code or None if detection fails
        """
        try:
            # Use ipapi.co for geolocation (free tier available)
            url = self.geolocation_api.format(ip_address)
            response = requests.get(url, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('country_code')
                
                # Map UK variations
                if country_code == 'UK':
                    return 'GB'
                
                return country_code
            
        except (requests.RequestException, ValueError, KeyError):
            # Silently fail and return None
            pass
        
        return None
    
    def get_country_name(self, country_code: str) -> str:
        """
        Get the full country name from country code.
        
        Args:
            country_code: Country code ('IN', 'US', 'GB', 'OTHER')
            
        Returns:
            Full country name
        """
        return self.SUPPORTED_COUNTRIES.get(country_code, 'Other')
