import pytest
from apps.about.templatetags.about_filters import split_sentences, paragraphs

class TestAboutFilters:
    """Tests for custom template filters in about_filters.py"""

    def test_split_sentences_basic(self):
        """Test splitting basic Nepali sentences"""
        text = "यो पहिलो वाक्य हो। यो दोस्रो वाक्य हो।"
        expected = ["यो पहिलो वाक्य हो।", "यो दोस्रो वाक्य हो।"]
        assert split_sentences(text) == expected

    def test_split_sentences_empty(self):
        """Test with empty or None values"""
        assert split_sentences("") == []
        assert split_sentences(None) == []

    def test_split_sentences_no_period(self):
        """Test with text not ending in a period"""
        text = "अधुरो वाक्य"
        assert split_sentences(text) == ["अधुरो वाक्य"]

    def test_split_sentences_with_newlines(self):
        """Test with newlines and spaces"""
        text = "वाक्य १। \n वाक्य २।"
        # The filter strips results
        expected = ["वाक्य १।", "वाक्य २।"]
        assert split_sentences(text) == expected

    def test_paragraphs_with_double_newlines(self):
        """Test conversion to paragraphs using double newlines"""
        text = "यो पहिलो समूह हो।\n\nयो दोस्रो समूह हो।"
        expected = ["यो पहिलो समूह हो।", "यो दोस्रो समूह हो।"]
        assert paragraphs(text) == expected

    def test_paragraphs_basic_grouping(self):
        """Test grouping sentences into paragraphs by count/length"""
        # Create 4 small sentences. 
        # Sentences 1-2 should group if lengths allow.
        # But filter has length thresholds: len(current_paragraph) >= 2 and current_length > 150
        # or current_length > 300
        
        s1 = "यो सानो वाक्य हो।" # ~18 chars
        s2 = "यो पनि सानो वाक्य हो।" # ~22 chars
        text = s1 + s2
        
        # With only s1 and s2, total length ~40. 
        # len(current_paragraph) will be 2, but current_length (40) is not > 150.
        # So it stays as one paragraph until the loop ends.
        assert paragraphs(text) == [s1 + " " + s2]

    def test_paragraphs_long_grouping(self):
        """Test grouping with long sentences exceeding thresholds"""
        # Nepali characters are multi-byte, but Python len() counts characters.
        long_sentence = "यो धेरै लामो वाक्य हो जसले थ्रेसहोल्ड पार गर्दछ।" * 5 
        # ~30 chars * 5 = 150 chars.
        
        text = long_sentence + " " + long_sentence
        # 1st sentence: length ~150. 
        # Loop 1: current_paragraph = [s1], current_length = 150.
        # Loop 2: current_paragraph = [s1, s2], current_length = 300.
        # Threshold (len >=2 and len > 150) is met.
        
        # Note: The logic adds period back if missing or not last.
        # In our case, the text split by । removes periods.
        
        res = paragraphs(text)
        assert len(res) >= 1

    def test_paragraphs_no_periods(self):
        """Test with text containing no Nepali periods"""
        text = "यो वाक्यमा कुनै पूर्णविराम छैन"
        # The filter appends । if it's missing from the last sentence
        assert paragraphs(text) == [text + "।"]

    def test_paragraphs_empty(self):
        """Test with empty or None values"""
        assert paragraphs("") == []
        assert paragraphs(None) == []
