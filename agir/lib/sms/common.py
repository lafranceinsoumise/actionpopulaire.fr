from collections import namedtuple
from math import ceil

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import number_type, PhoneNumberType
from unidecode import unidecode

from agir.people.models import PersonQueryset

GSM7_CODEPOINTS = {
    0x0040: 1,  # 	COMMERCIAL AT
    0x00A3: 1,  # 	POUND SIGN
    0x0024: 1,  # 	DOLLAR SIGN
    0x00A5: 1,  # 	YEN SIGN
    0x00E8: 1,  # 	LATIN SMALL LETTER E WITH GRAVE
    0x00E9: 1,  # 	LATIN SMALL LETTER E WITH ACUTE
    0x00F9: 1,  # 	LATIN SMALL LETTER U WITH GRAVE
    0x00EC: 1,  # 	LATIN SMALL LETTER I WITH GRAVE
    0x00F2: 1,  # 	LATIN SMALL LETTER O WITH GRAVE
    0x00C7: 1,  # 	LATIN CAPITAL LETTER C WITH CEDILLA (see note above)
    0x000A: 1,  # 	LINE FEED
    0x00D8: 1,  # 	LATIN CAPITAL LETTER O WITH STROKE
    0x00F8: 1,  # 	LATIN SMALL LETTER O WITH STROKE
    0x000D: 1,  # 	CARRIAGE RETURN
    0x00C5: 1,  # 	LATIN CAPITAL LETTER A WITH RING ABOVE
    0x00E5: 1,  # 	LATIN SMALL LETTER A WITH RING ABOVE
    0x0394: 1,  # 	GREEK CAPITAL LETTER DELTA
    0x005F: 1,  # 	LOW LINE
    0x03A6: 1,  # 	GREEK CAPITAL LETTER PHI
    0x0393: 1,  # 	GREEK CAPITAL LETTER GAMMA
    0x039B: 1,  # 	GREEK CAPITAL LETTER LAMDA
    0x03A9: 1,  # 	GREEK CAPITAL LETTER OMEGA
    0x03A0: 1,  # 	GREEK CAPITAL LETTER PI
    0x03A8: 1,  # 	GREEK CAPITAL LETTER PSI
    0x03A3: 1,  # 	GREEK CAPITAL LETTER SIGMA
    0x0398: 1,  # 	GREEK CAPITAL LETTER THETA
    0x039E: 1,  # 	GREEK CAPITAL LETTER XI
    0x00A0: 1,  # 	ESCAPE TO EXTENSION TABLE (or displayed as NBSP, see note above)
    0x000C: 2,  # 	FORM FEED
    0x005E: 2,  # 	CIRCUMFLEX ACCENT
    0x007B: 2,  # 	LEFT CURLY BRACKET
    0x007D: 2,  # 	RIGHT CURLY BRACKET
    0x005C: 2,  # 	REVERSE SOLIDUS
    0x005B: 2,  # 	LEFT SQUARE BRACKET
    0x007E: 2,  # 	TILDE
    0x005D: 2,  # 	RIGHT SQUARE BRACKET
    0x007C: 2,  # 	VERTICAL LINE
    0x20AC: 2,  # 	EURO SIGN
    0x00C6: 1,  # 	LATIN CAPITAL LETTER AE
    0x00E6: 1,  # 	LATIN SMALL LETTER AE
    0x00DF: 1,  # 	LATIN SMALL LETTER SHARP S (German)
    0x00C9: 1,  # 	LATIN CAPITAL LETTER E WITH ACUTE
    0x0020: 1,  # 	SPACE
    0x0021: 1,  # 	EXCLAMATION MARK
    0x0022: 1,  # 	QUOTATION MARK
    0x0023: 1,  # 	NUMBER SIGN
    0x00A4: 1,  # 	CURRENCY SIGN
    0x0025: 1,  # 	PERCENT SIGN
    0x0026: 1,  # 	AMPERSAND
    0x0027: 1,  # 	APOSTROPHE
    0x0028: 1,  # 	LEFT PARENTHESIS
    0x0029: 1,  # 	RIGHT PARENTHESIS
    0x002A: 1,  # 	ASTERISK
    0x002B: 1,  # 	PLUS SIGN
    0x002C: 1,  # 	COMMA
    0x002D: 1,  # 	HYPHEN-MINUS
    0x002E: 1,  # 	FULL STOP
    0x002F: 1,  # 	SOLIDUS
    0x0030: 1,  # 	DIGIT ZERO
    0x0031: 1,  # 	DIGIT ONE
    0x0032: 1,  # 	DIGIT TWO
    0x0033: 1,  # 	DIGIT THREE
    0x0034: 1,  # 	DIGIT FOUR
    0x0035: 1,  # 	DIGIT FIVE
    0x0036: 1,  # 	DIGIT SIX
    0x0037: 1,  # 	DIGIT SEVEN
    0x0038: 1,  # 	DIGIT EIGHT
    0x0039: 1,  # 	DIGIT NINE
    0x003A: 1,  # 	COLON
    0x003B: 1,  # 	SEMICOLON
    0x003C: 1,  # 	LESS-THAN SIGN
    0x003D: 1,  # 	EQUALS SIGN
    0x003E: 1,  # 	GREATER-THAN SIGN
    0x003F: 1,  # 	QUESTION MARK
    0x00A1: 1,  # 	INVERTED EXCLAMATION MARK
    0x0041: 1,  # 	LATIN CAPITAL LETTER A
    0x0042: 1,  # 	LATIN CAPITAL LETTER B
    0x0043: 1,  # 	LATIN CAPITAL LETTER C
    0x0044: 1,  # 	LATIN CAPITAL LETTER D
    0x0045: 1,  # 	LATIN CAPITAL LETTER E
    0x0046: 1,  # 	LATIN CAPITAL LETTER F
    0x0047: 1,  # 	LATIN CAPITAL LETTER G
    0x0048: 1,  # 	LATIN CAPITAL LETTER H
    0x0049: 1,  # 	LATIN CAPITAL LETTER I
    0x004A: 1,  # 	LATIN CAPITAL LETTER J
    0x004B: 1,  # 	LATIN CAPITAL LETTER K
    0x004C: 1,  # 	LATIN CAPITAL LETTER L
    0x004D: 1,  # 	LATIN CAPITAL LETTER M
    0x004E: 1,  # 	LATIN CAPITAL LETTER N
    0x004F: 1,  # 	LATIN CAPITAL LETTER O
    0x0050: 1,  # 	LATIN CAPITAL LETTER P
    0x0051: 1,  # 	LATIN CAPITAL LETTER Q
    0x0052: 1,  # 	LATIN CAPITAL LETTER R
    0x0053: 1,  # 	LATIN CAPITAL LETTER S
    0x0054: 1,  # 	LATIN CAPITAL LETTER T
    0x0055: 1,  # 	LATIN CAPITAL LETTER U
    0x0056: 1,  # 	LATIN CAPITAL LETTER V
    0x0057: 1,  # 	LATIN CAPITAL LETTER W
    0x0058: 1,  # 	LATIN CAPITAL LETTER X
    0x0059: 1,  # 	LATIN CAPITAL LETTER Y
    0x005A: 1,  # 	LATIN CAPITAL LETTER Z
    0x00C4: 1,  # 	LATIN CAPITAL LETTER A WITH DIAERESIS
    0x00D6: 1,  # 	LATIN CAPITAL LETTER O WITH DIAERESIS
    0x00D1: 1,  # 	LATIN CAPITAL LETTER N WITH TILDE
    0x00DC: 1,  # 	LATIN CAPITAL LETTER U WITH DIAERESIS
    0x00A7: 1,  # 	SECTION SIGN
    0x00BF: 1,  # 	INVERTED QUESTION MARK
    0x0061: 1,  # 	LATIN SMALL LETTER A
    0x0062: 1,  # 	LATIN SMALL LETTER B
    0x0063: 1,  # 	LATIN SMALL LETTER C
    0x0064: 1,  # 	LATIN SMALL LETTER D
    0x0065: 1,  # 	LATIN SMALL LETTER E
    0x0066: 1,  # 	LATIN SMALL LETTER F
    0x0067: 1,  # 	LATIN SMALL LETTER G
    0x0068: 1,  # 	LATIN SMALL LETTER H
    0x0069: 1,  # 	LATIN SMALL LETTER I
    0x006A: 1,  # 	LATIN SMALL LETTER J
    0x006B: 1,  # 	LATIN SMALL LETTER K
    0x006C: 1,  # 	LATIN SMALL LETTER L
    0x006D: 1,  # 	LATIN SMALL LETTER M
    0x006E: 1,  # 	LATIN SMALL LETTER N
    0x006F: 1,  # 	LATIN SMALL LETTER O
    0x0070: 1,  # 	LATIN SMALL LETTER P
    0x0071: 1,  # 	LATIN SMALL LETTER Q
    0x0072: 1,  # 	LATIN SMALL LETTER R
    0x0073: 1,  # 	LATIN SMALL LETTER S
    0x0074: 1,  # 	LATIN SMALL LETTER T
    0x0075: 1,  # 	LATIN SMALL LETTER U
    0x0076: 1,  # 	LATIN SMALL LETTER V
    0x0077: 1,  # 	LATIN SMALL LETTER W
    0x0078: 1,  # 	LATIN SMALL LETTER X
    0x0079: 1,  # 	LATIN SMALL LETTER Y
    0x007A: 1,  # 	LATIN SMALL LETTER Z
    0x00E4: 1,  # 	LATIN SMALL LETTER A WITH DIAERESIS
    0x00F6: 1,  # 	LATIN SMALL LETTER O WITH DIAERESIS
    0x00F1: 1,  # 	LATIN SMALL LETTER N WITH TILDE
    0x00FC: 1,  # 	LATIN SMALL LETTER U WITH DIAERESIS
    0x00E0: 1,  # 	LATIN SMALL LETTER A WITH GRAVE
}

MESSAGE_LENGTH = namedtuple("MessageLength", ["encoding", "byte_length", "messages"])


def to_7bit_string(string):
    # Remove non 7bit characters from message to avoid errors
    return unidecode(string).encode("ascii", errors="replace").decode("utf-8")


def to_phone_number(n):
    return PhoneNumber.from_string(n, region="FR") if isinstance(n, str) else n


def compute_sms_length_information(message):
    if any(ord(c) not in GSM7_CODEPOINTS for c in message):
        return MESSAGE_LENGTH(
            "UCS-2",
            2 * len(message),
            1 if len(message) <= 70 else ceil(len(message) / 67),
        )

    encoding = (
        "GSM7-EXT" if any(GSM7_CODEPOINTS[ord(c)] == 2 for c in message) else "GSM7"
    )
    base_length = sum(GSM7_CODEPOINTS[ord(c)] for c in message)
    byte_length = ceil(base_length * 7 / 8)
    messages = 1 if byte_length <= 140 else ceil(byte_length / 134)

    return MESSAGE_LENGTH(encoding, byte_length, messages)


def numeros_mobiles(qs: PersonQueryset):
    """Renvoie les numéros de mobile des personnes du queryset.

    Déduplique les numéros (tout en gardant l'ordre) et élimine les numéros invalides
    et les numéros fixes.
    """
    numeros = [
        PhoneNumber.from_string(n)
        for n in qs.exclude(contact_phone="").values_list("contact_phone", flat=True)
    ]

    # caster en set ferait perdre l'ordre initial. Cette astuce permet de le garder.
    # (NB. seen.add renvoie toujours None)
    seen = set()
    numeros_uniques = [n for n in numeros if n not in seen and not seen.add(n)]

    return [
        n
        for n in numeros_uniques
        if n.is_valid()
        and number_type(n)
        in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE_OR_MOBILE)
    ]


class SMSException(Exception):
    pass


class SMSSendException(SMSException):
    def __init__(self, *args, sent=None, invalid=None):
        super().__init__(*args)

        if sent is None:
            sent = frozenset()
        else:
            sent = frozenset(sent)
        if invalid is None:
            invalid = frozenset()
        else:
            invalid = frozenset(invalid)

        self.sent = sent
        self.invalid = invalid
