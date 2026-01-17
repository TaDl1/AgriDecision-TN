import re
import logging

class DerjaVoiceParser:
    """
    Simplified parser for harvest numbers and crop keywords.
    Focuses on high reliability for specific inputs.
    """

    # Lexicon for numbers in Tunisian Arabic, French, and common English
    NUMBERS_LEXICON = {
        # Tunisian / Arabic Base & Variations
        'wahed': 1, 'whed': 1, '1': 1, 'واحد': 1, 'وحد': 1,
        'tnin': 2, 'ithnin': 2, 'zouz': 2, '2': 2, 'اثنين': 2, 'إثنين': 2, 'زوج': 2, 'زوز': 2,
        'thletha': 3, 'thltha': 3, 'tlata': 3, 'tleta': 3, '3': 3, 'ثلاثة': 3, 'ثلاثه': 3, 'ثلاث': 3,
        'arba': 4, 'arb3a': 4, 'rab3a': 4, '4': 4, 'أربعة': 4, 'اربعة': 4, 'أربعه': 4, 'اربعة': 4,
        'khamsa': 5, 'khmsa': 5, '5': 5, 'خمسة': 5, 'خمسه': 5,
        'setta': 6, 'sitta': 6, '6': 6, 'ستة': 6, 'سته': 6,
        'saba': 7, 'sab3a': 7, '7': 7, 'سبعة': 7, 'سبعه': 7,
        'thmenya': 8, 'tmanya': 8, 'thmanya': 8, '8': 8, 'ثمانية': 8, 'ثمانيه': 8,
        'tesa': 9, 'tes3a': 9, 'ts3a': 9, '9': 9, 'تسعة': 9, 'تسعه': 9,
        'ashra': 10, '3ashra': 10, '3achra': 10, '10': 10, 'عشرة': 10, 'عشره': 10,
        'hdech': 11, 'tnach': 12, 'thlotach': 13, 'arbatach': 14, 'khomstach': 15,
        'eshrin': 20, '3eshrin': 20, '20': 20, 'عشرين': 20,
        'thlethin': 30, '30': 30, 'ثلاثين': 30,
        'arbain': 40, '40': 40, 'اربعين': 40,
        'khamsin': 50, '50': 50, 'خمسين': 50,
        'miya': 100, 'mya': 100, 'méya': 100, '100': 100, 'مائة': 100, 'مية': 100,
        'miaatayn': 200, 'miateyn': 200, 'mitayn': 200, '200': 200, 'مائتين': 200,
        'alf': 1000, '1000': 1000, 'ألف': 1000,
        'alfayn': 2000, 'alfin': 2000, 'alfeyn': 2000, '2000': 2000, 'ألفين': 2000,
        'khamslaf': 5000, '5000': 5000,
        'tes3in': 90, '90': 90,
        # Arabic-Indic Digits
        '٠': 0, '١': 1, '٢': 2, '٣': 3, '٤': 4, '٥': 5, '٦': 6, '٧': 7, '٨': 8, '٩': 9,
        
        # French & Phonetic variations
        'un': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5,
        'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9, 'dix': 10,
        'onze': 11, 'douze': 12, 'treize': 13, 'quatorze': 14, 'quinze': 15, 'seize': 16,
        'dix-sept': 17, 'dix-huit': 18, 'dix-neuf': 19,
        'vingt': 20, 'vingt-et-un': 21, 'vingt-deux': 22, 'vingt-trois': 23,
        'trente': 30, 'trente-et-un': 31,
        'quarante': 40, 'quarante-et-un': 41,
        'cinquante': 50, 'cinquante-et-un': 51,
        'soixante': 60, 'soixante-et-un': 61,
        'soixante-dix': 70, 'septante': 70,
        'quatre-vingt': 80, 'quatre-vingts': 80, 'huitante': 80,
        'quatre-vingt-dix': 90, 'nonante': 90,
        'cent': 100, 'mille': 1000,
        'mil': 1000, 'milyoun': 1000000,
        'zero': 0, 'sifr': 0, 'صفر': 0,
        # Phonetic French (if trailing "s" or "t" is missed)
        'troi': 3, 'quattre': 4, 'cing': 5, 'sep': 7, 'hui': 8, 'neu': 9,
        'thamanya': 8, 'thmanya': 8, 'thmania': 8, 'tmanya': 8, 'thmenya': 8, 'thmania': 8, 'thmaniya': 8,
        'thltha': 3, 'thalatha': 3, 'tleta': 3, 'tlata': 3, 'thlata': 3, 'thelta': 3,
        'arbaa': 4, 'arba3a': 4, 'rab3a': 4, 'arba': 4,
        'tesaa': 9, 'tes3a': 9, 'tsaa': 9, 'ts3a': 9,
        'achra': 10, 'ashra': 10, '3ashra': 10, '3achra': 10,
        'zouz': 2, 'zoz': 2, 'jouz': 2, 'zouze': 2,
    }

    # Keyword mapping for crop selection
    CROP_KEYWORDS = {
        'Olive': ['zitoun', 'زيتون', 'olive', 'zitun'],
        'Tomato': ['tmatem', 'طماطم', 'tomate', 'tmatim'],
        'Pepper': ['felfel', 'فلفل', 'poivron', 'pepper'],
        'Potato': ['batata', 'batat', 'بطاطا', 'pomme de terre', 'potato'],
        'Wheat': ['qamh', 'gammh', 'قمح', 'ble', 'wheat', '9am7'],
        'Watermelon': ['dalle3', 'دلاع', 'pasteque', 'watermelon'],
        'Dates': ['degla', 'tmar', 'دڨلة', 'dattes', 'dates'],
        'Citrus': ['qares', 'lemon', 'قارص', 'citron', 'citrus'],
        'Onion': ['bsal', 'بصل', 'oignon', 'onion'],
        'Garlic': ['thoum', 'ثوم', 'ail', 'garlic']
    }

    def parse(self, text):
        # 0. Cleanup and Normalization
        text = text.lower().strip()
        # Remove punctuation BUT keep hyphens for French compound words (dix-sept, etc.)
        # Also preserve Arabic characters
        text = re.sub(r'[^a-z0-9\-\u0600-\u06FF\s]', ' ', text)
        text = " " + " ".join(text.split()) + " "
        
        logging.info(f"🎤 Voice shortcut input: {text}")
        
        result = {
            'crop_name': None,
            'numbers': [],
            'raw_text': text.strip()
        }

        # 1. Extract Crop Keywords
        for canonical, keywords in self.CROP_KEYWORDS.items():
            if any(re.search(r'[\s]' + re.escape(k) + r'[\s]', text) for k in keywords):
                result['crop_name'] = canonical
                break

        # 2. Extract Numerical digits (e.g. "50", "100")
        digit_matches = re.finditer(r'[\s](\d+)[\s]', text)
        for m in digit_matches:
            result['numbers'].append(float(m.group(1)))

        # 3. Extract Number words from longest to shortest (to catch compound words first)
        # We replace spaces with hyphens in the lexicon search for French consistency
        sorted_lexicon = sorted(self.NUMBERS_LEXICON.items(), key=lambda x: len(x[0]), reverse=True)
        
        # We'll use a copy of the text to "mask" matched words
        temp_text = " " + text + " "
        
        for word, val in sorted_lexicon:
            # Check for both "vingt-et-un" and "vingt et un"
            variations = [word, word.replace('-', ' ')]
            for variant in set(variations):
                pattern = r'[\s]' + re.escape(variant) + r'[\s]'
                if re.search(pattern, temp_text):
                    result['numbers'].append(float(val))
                    # Mask out the matched word to prevent sub-matches (mask with length-equivalent)
                    mask = " " + ("#" * len(variant)) + " "
                    temp_text = re.sub(pattern, mask, temp_text)
                    break # Skip other variants once matched
        
        # Deduplicate and sort numbers (preserving order)
        if result['numbers']:
            result['numbers'] = list(dict.fromkeys(result['numbers']))

        return result
