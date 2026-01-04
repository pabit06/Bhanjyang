"""
Custom template filters for the About app.
"""
from django import template

register = template.Library()


@register.filter(name='split_sentences')
def split_sentences(value):
    """
    Split text by Nepali period (।) and return list of sentences.
    Used to create paragraphs from long text.
    """
    if not value:
        return []
    
    # Split by Nepali period followed by space or newline
    sentences = []
    current_sentence = ""
    
    for char in value:
        current_sentence += char
        if char == '।':
            sentences.append(current_sentence.strip())
            current_sentence = ""
    
    # Add remaining text if any
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
    
    return sentences


@register.filter(name='paragraphs')
def paragraphs(value):
    """
    Convert text into paragraphs by splitting on Nepali periods (।).
    Groups sentences into readable paragraphs (2-3 sentences each).
    Returns a list of paragraph strings.
    """
    if not value:
        return []
    
    # First, try splitting by double newlines (explicit paragraph breaks)
    if '\n\n' in value:
        return [p.strip() for p in value.split('\n\n') if p.strip()]
    
    # Split by Nepali period (।) - handle both with and without space after
    text = value.replace('। ', '।').replace('।', '। ')
    parts = [p.strip() for p in text.split('।') if p.strip()]
    
    if not parts:
        return [value]
    
    # Group sentences into paragraphs
    paragraphs_list = []
    current_paragraph = []
    current_length = 0
    
    for i, part in enumerate(parts):
        sentence = part.strip()
        if not sentence:
            continue
            
        # Add period back (except for last sentence if it doesn't have one)
        if i < len(parts) - 1 or not sentence.endswith('।'):
            sentence += '।'
        
        current_paragraph.append(sentence)
        current_length += len(sentence)
        
        # Create a paragraph if:
        # 1. We have 2-3 sentences, OR
        # 2. Current paragraph is getting long (>250 chars), OR
        # 3. This is the last sentence
        if (len(current_paragraph) >= 2 and current_length > 150) or \
           current_length > 300 or \
           i == len(parts) - 1:
            paragraphs_list.append(' '.join(current_paragraph))
            current_paragraph = []
            current_length = 0
    
    # Add any remaining sentences
    if current_paragraph:
        paragraphs_list.append(' '.join(current_paragraph))
    
    return paragraphs_list if paragraphs_list else [value]

