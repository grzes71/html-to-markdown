#!/usr/bin/env python3
"""
Clean up the website.md scrape of atariarchives.org into a focused
Atari 400/800/XL/XE development reference.
"""

import re
import hashlib
from collections import OrderedDict

INPUT_FILE = "output/website.md"
OUTPUT_FILE = "output/atari_development_guide.md"

# ============================================================
# EXPLICIT BLACKLIST - headers to always remove
# ============================================================
REMOVE_PATTERNS = [
    # Site meta
    r"^AtariArchives\.org",
    r"^E-mail AtariArchives",
    r"^What's new at atariarchives",
    r"^Mapping The Atari$",
    
    # APX meta
    r"^What was Atari Program Exchange\?$",
    r"^APX Catalogs$",
    r"^Atari Program Exchange: List of Software$",
    r"^Interview with Fred Thorlin$",
    
    # Archives/catalogs
    r"^Software Library$",
    r"^Mapping The Atari - Software Archive$",
    r".*- Software Archive$",
    
    # Community/SIG
    r"^Cleveland Free-Net",
    r"^About the Cleveland",
    r"^About the Atari SIG",
    r"^comp\.sys\.atari",
    r"^Old Hackers",
    
    # Non-Atari books
    r"^Digital Deli",
    r"^Artist and Computer",
    r"^Electronic Computer Projects",
    r"^Computer Controller Cookbook",
    r"^Computer Graphics Primer",
    r"^Colossal Computer Cartoon",
    r"^Computer Animation Primer",
    r"^Flight Simulator",
    r"^TTL Cookbook",
    r"^TIA-1A",
    
    # General computing / Creative Computing
    r"^Table of Contents:",
    r"^David Ahl",
    r"^BASIC Computer Games",
    r"^Big Computer Games",
    r"^More BASIC Computer Games",
    r"^The Creative Atari$",
    r".*Creative Computing",
    r".*The Best of Creative",
    r"^How To Survive",
    r"^What Is Computer Literacy",
    r"^What Sign Is The Computer",
    r"^What's Wrong With",
    r"^What's Been Going On",
    r"^What is Possible Today",
    r"^Is There an End",
    r"^Is a Picture Worth",
    r"^Is it Live",
    r"^If You're New",
    r"^Where Are All",
    r"^Where is My Robot",
    r"^Where Do We Go",
    r"^Will You Still",
    r"^Why Should I Care",
    r"^Who's Minding",
    r"^When Will the Magic",
    
    # Non-dev Atari
    r"^The Epson Connection",
    r"^SpeedScript",
    r"^\*\*\*SpeedScript",
    r"^Atari Articles$",
    r"^A Letter Quality",
    
    # Book metadata
    r".*- Cover$",
    r".*- Back Cover$",
    r".*- Title Page$",
    r".*- Copyright Information$",
    r"^Atari Basic.*How to Use",
    r"^Atari Basic.*To the Reader",
    r"^Atari Basic.*Other Wiley",
    r"^Atari Basic.*Index of Programs",
    
    # Adventure game ch 10+
    r"^Creating Adventure Games On Your Computer - Appendices$",
    r"^Creating Adventure Games On Your Computer - Chapter 1\d$",
    r"^Creating Adventure Games On Your Computer - Chapter 2\d$",
    r"^Creating Adventure Games On Your Computer - Chapter [89]$",
    
    # Adventure game sub-sections
    r"^How to Read This Book$",
    r"^Adapting the Programs",
    r"^Making Magic$",
    r"^Picking Up Treasure",
    r"^The Quartermaster",
    r"^Be Prepared$",
    r"^Taking Up Arms",
    r"^The Tumult",
    r"^Room Descriptions",
    r"^Special Handling$",
    r"^Elaborations$",
    r"^The New Scenario",
    r"^The Map$",
    r"^What Goes Up",
    r"^Room of Death",
    r"^One-Way System",
    r"^Adding It All Up",
    r"^Roll Your Own",
    r"^The Vocabulary$",
    r"^Snapshots$",
    r"^Attributes$",
    r"^The Goodies$",
    r"^Multiple Choice Death",
    r"^The Baddies$",
    r"^Compressing the Program",
    r"^The Maps$",
    r"^The Scenario$",
    r"^The Choices$",
    r"^Puzzles$",
    r"^Two-Word Sentences",
    r"^Vocabulary Handling",
    r"^Sample Run$",
    r"^\d+ Suggestions for",
    r"^\d+ Random Place",
    r"^\d+ Useful Addresses",
    
    # Number-only
    r"^\d+$",
    
    # Non-8-bit Atari
    r"^Atari ST",
    r"^Atari TT",
    r"^Atari Falcon",
    r"^Atari Jaguar",
    r"^Atari Lynx",
    r"^Atari Portfolio",
    r"^16/32",
    
    # Product profiles
    r".*Product Profiles",
    
    # Misc artifacts
    r"^\[Chapter 6",
    r"^he Upstart Atari",
    
    # General computing articles from various books
    r"^About the Author",
    r"^An Esoteric Ethical",
    r"^Sophisticated Electronic",
    r"^Soup and Crackers",
    r"^Space: 1999",
    r"^Special Chips and ROM",
    r"^Sports Special",
    r"^Star Trek",
    r"^Star-Times",
    r"^Starting with The Visitor",
    r"^Statewide Pools",
    r"^Stepping Out",
    r"^Still a Few Bugs",
    r"^Strike Force",
    r"^Structured Programming",
    r"^Summary of the ACM",
    r"^Super Star Trek",
    r"^Survey of Public",
    r"^Surveys, The Census",
    r"^Swarm",
    r"^THE APPEAL",
    r"^THINK The Story",
    r"^TI-99",
    r"^TICCIT System",
    r"^TOWARDS A THINKING",
    r"^TRS-80",
    r"^Talk is Getting",
    r"^Tank Game",
    r"^Technology.*Doomsday",
    r"^Tektronix",
    r"^Teletype Model",
    r"^Terminal Illness",
    r"^Test For System",
    r"^Test-Driving",
    r"^The 30-Minute",
    r"^The 10 Cent",
    r"^The ABC's",
    r"^The Apple of my Eye",
    r"^The Art Of Education",
    r"^The Automatic Proofreader",
    r"^The Automobile",
    r"^The Babble of Computer",
    r"^The Case of the Reader",
    r"^The Challenge is Met",
    r"^The Computer \"Glass Box\"",
    r"^The Computer Listens",
    r"^The Computer Threat",
    r"^The Computer Tree",
    r"^The Computer and Music",
    r"^The Computer: Threat",
    r"^The Conservative Computer",
    r"^The Cosmic Subway",
    r"^The Digital Computer",
    r"^The Eco-Spasm",
    r"^The Fabulous Furry",
    r"^The Final Reckoning",
    r"^The First Golden Age",
    r"^The First West Coast",
    r"^The Forty Year",
    r"^The Future of Computer",
    r"^The Government Dinosaur",
    r"^The Graphics Computer",
    r"^The Guinness Book",
    r"^The Home Banking",
    r"^The Kapro Too",
    r"^The LOGO Lineage",
    r"^The Land of Halco",
    r"^The Life and Times",
    r"^The Lighter Side",
    r"^The Mac on Skis",
    r"^The Madness Known",
    r"^The Magic Of Electronic",
    r"^The Merry Pranksters",
    r"^The Micro Menage",
    r"^The Microcomputer Inflicts",
    r"^The Mosaic 64K",
    r"^The Mystic 7",
    r"^The Parable of the Horse",
    r"^The Personal Computer as Therapist",
    r"^The Plug-In Practitioner",
    r"^The Pocket Computer",
    r"^The Polygon Fill",
    r"^The Programmer's Plight",
    r"^The Reactive Engine",
    r"^The Religion of Computers",
    r"^The Right to Know",
    r"^The Sleeping Queued",
    r"^The Sol-20",
    r"^The State of the Art",
    r"^The Technology of",
    r"^The Telephone System",
    r"^The Text Buffer",
    r"^The Thinking Computer",
    r"^The Times Goes Computer",
    r"^The Tower of Brahma",
    r"^The Transposition",
    r"^The Ultimate Color",
    r"^The Video Disk",
    r"^The Way We Work",
    r"^The World In Your Own",
    r"^The \$2\.98",
    r"^The 5 \(or 6",
    r"^The 49 Second",
    r"^Videodiscs",
    r"^Page \d+$",
    r"^Und so Weiter",
    r"^Unlucky Seven",
    r"^Updating",
    r"^User's Groups",
    r"^Using the Computer",
    r"^Using Your Home",
    r"^Very Good.*Please Continue",
    r"^WANTED",
    r"^WUMPUS",
    r"^War Games",
    r"^We Interrupt",
    r"^We're Being",
    r"^We've Got",
    r"^West Coast",
    r"^Western Union",
    r"^Where Have All",
    r"^Who's Afraid",
    r"^Who's On First",
    r"^Why Aren't",
    r"^Why Johnny",
    r"^Winding Your Way",
    r"^Witchcraft.*Medicine",
    r"^Word Processing",
    r"^Woz and Jobs",
    r"^Yankee Doodle",
    r"^You Too Can Be",
    r"^You've Come",
    r"^Your Friendly",
    r"^Your Home Computer",
    r"^Your Very Own",
    r"^Zip",
    r"^Zork",
    r"^\[.*\]\(https?://",
]

# ============================================================
# WHITELIST - headers that indicate Atari development content
# ============================================================
KEEP_PATTERNS = [
    # Major books - keep everything with these prefixes
    r"^Mapping The Atari",
    r"^De Re Atari",
    r"^Atari Roots",
    r"^Inside Atari DOS",
    r"^The Master Memory Map",
    r"^The Second Book Of Machine Language",
    r"^Assembly Language Programming",
    r"^Atari Player-Missile Graphics",
    r"^Atari Graphics",
    r"^Compute!.*Atari",
    r"^COMPUTE!.*Atari",
    r"^Atari Basic",
    r"^Atari BASIC",
    r"^Machine Language For Beginners",
    r"^Creating Adventure Games On Your Computer - Chapter [1-7]",
    
    # Core dev resources
    r"^Atari Development Resources",
    r"^Atari Program Exchange Program Author",
    r"^\*\*Atari Source Code\*\*$",
    r"^\*K-DOS\*",
    r"^PAGE ONE",
    r"^PAGES TWO",
    
    # Specific articles/topics with Atari context
    r"^A New Basic.*Atari",
    r"^A Simple Screen Editor.*Atari",
    r"^ATARI BASIC Joystick",
    r"^Advantages of Assembly Language",
    r"^An Atari Library",
    r"^An Automatic Conversion",
    r"^An Introduction To Display List",
    r"^Analyze Your Program.*Atari",
    r"^Antic",
    r"^Assembl",
    r"^Atari 1200",
    r"^Atari 400",
    r"^Atari 800",
    r"^Atari BASIC String",
    r"^Atari Character Set",
    r"^Atari DOS",
    r"^Atari Diskfile",
    r"^Atari In Action",
    r"^Atari Memory",
    r"^Atari.*Cassette",
    r"^Atari.*Display",
    r"^Atari.*Graphics",
    r"^Atari.*Printer",
    r"^Atari.*Sound",
    r"^Atari.*Video",
    r"^Atari's",
    r"^Back to BASIC",
    r"^Building.*Atari",
    r"^Cassette.*Atari",
    r"^Display List",
    r"^GPRIOR",
    r"^IOCB",
    r"^Inside Atari",
    r"^Machine Language",
    r"^Mapping.*Atari",
    r"^Memory.*Atari",
    r"^Player.*Missile",
    r"^Programming.*Atari",
    r"^SIO",
    r"^The 16 Bytes.*IOCB",
    r"^The Accumulator",
    r"^The Character.*Generator",
    r"^The Character Set",
    r"^The Floating.*Atari",
    r"^The Fountains of ROM",
    r"^The Heart of the Program",
    r"^The Hexadecimal.*System",
    r"^The High Rent",
    r"^The Initializing Subroutine",
    r"^The JOURNALISM",
    r"^The Keyboard Game",
    r"^The LOMEM",
    r"^The MEMLO",
    r"^The Master Loop",
    r"^The Memory Club",
    r"^The Operating System",
    r"^The Problem.*Allocating",
    r"^The Processor Status",
    r"^The Purpose",
    r"^The Resident Disk",
    r"^The USR",
    r"^The Wastebasket",
    r"^Under the Hood.*Atari",
    r"^Understanding.*Atari",
    r"^Using Disks.*Atari",
    r"^Using the Atari Assembler",
    r"^VBLANK",
    r"^Vertical Blank",
    r"^Writing.*Programs.*Run.*Loaded",
    r"^Writing Self-booting",
    r"^Your Atari",
    r"^Your Computer.*Memory",
    r"^Your Computer.*Address",
    r"^Zero Page",
    r"^128K Memory.*Atari",
    r"^10 ATARI BASIC",
    r"^2 ANTIC",
    r"^5 DISPLAY LIST",
    r"^APPENDIX C THE ATARI",
    r"^APPENDIX D TELEVISION",
    r"^APPENDIX E GTIA",
    r"^Easy.*Atari",
    r"^Fast.*Atari",
    r"^File.*Atari",
    r"^How.*Atari",
    r"^Introduction.*Atari",
    r"^More.*Atari",
    r"^New.*Atari",
    r"^Scrolling.*Atari",
    r"^Second.*Atari",
    r"^Six.*Atari",
    r"^Special.*Atari",
    r"^Starting.*Atari",
    r"^Tutorial.*Atari",
    r"^Two.*Atari",
    r"^What.*Atari",
    r"^\*\*Foreword\*\*$",
    r"^\*\*Preface\*\*$",
]

BOILERPLATE_LINES = [
    "Return to Table of Contents",
    "Previous Chapter",
    "Next Chapter",
    "[Return to Table of Contents](index.php)",
    "[Next Chapter](frontmatter.php)",
    "<< PREVIOUS",
    ">> NEXT",
    "Jump to page:",
    "Go to contents",
    "Go to thumbnails",
    "This book is",
    "also available for the Kindle",
    "[Next Article]",
    "[Previous Article]",
]


def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def split_into_sections(content):
    sections = []
    lines = content.split('\n')
    current_lines = []
    current_header = None
    in_preamble = True
    
    for line in lines:
        if line.startswith('## '):
            if current_header is not None or in_preamble:
                text = '\n'.join(current_lines).strip()
                if text:
                    sections.append({
                        'header': current_header or 'PREAMBLE',
                        'content': text,
                    })
            current_header = line[3:].strip()
            current_lines = [line]
            in_preamble = False
        else:
            current_lines.append(line)
    
    if current_lines:
        text = '\n'.join(current_lines).strip()
        if text:
            sections.append({
                'header': current_header or 'PREAMBLE',
                'content': text,
            })
    return sections


def should_keep_section(header):
    for pattern in REMOVE_PATTERNS:
        if re.match(pattern, header):
            return False
    for pattern in KEEP_PATTERNS:
        if re.match(pattern, header):
            return True
    return False


def clean_boilerplate(content):
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if any(bp in stripped for bp in BOILERPLATE_LINES):
            continue
        if stripped == '|':
            continue
        cleaned.append(line)
    while cleaned and cleaned[-1].strip() == '':
        cleaned.pop()
    return '\n'.join(cleaned)


def normalize_content(text):
    lines = text.split('\n')
    norm = []
    prev_empty = False
    for line in lines:
        s = line.strip()
        if s == '':
            if not prev_empty:
                norm.append('')
                prev_empty = True
        else:
            norm.append(s)
            prev_empty = False
    return '\n'.join(norm)


def content_hash(content, method='normalized_first_2000'):
    n = normalize_content(content)
    sample = n if method == 'full' else n[:2000]
    return hashlib.md5(sample.encode('utf-8')).hexdigest()


def dedup_headers(sections):
    seen = set()
    unique = []
    removed = 0
    for s in sections:
        if s['header'] not in seen:
            seen.add(s['header'])
            unique.append(s)
        else:
            removed += 1
    print(f"  Header duplicates: {removed}")
    return unique


def dedup_exact(sections):
    seen = set()
    unique = []
    removed = 0
    for s in sections:
        h = content_hash(s['content'], 'full')
        if h not in seen:
            seen.add(h)
            unique.append(s)
        else:
            removed += 1
    print(f"  Exact duplicates: {removed}")
    return unique


def dedup_near(sections):
    seen = set()
    unique = []
    removed = 0
    for s in sections:
        h = content_hash(s['content'], 'normalized_first_2000')
        if h not in seen:
            seen.add(h)
            unique.append(s)
        else:
            removed += 1
    print(f"  Near duplicates: {removed}")
    return unique


def sort_sections(sections):
    preferred = [
        'Mapping The Atari-Memory Map',
        'Mapping The Atari-Introduction',
        "Mapping The Atari-Author's Preface",
        "Mapping The Atari-Author's Preface To The Revised Edition",
        'Mapping The Atari - Front Matter',
        'Mapping The Atari - Index By Label',
        'Mapping The Atari - Index By Subject',
        'Mapping The Atari - XL/XE Index',
        'PAGE ONE: THE STACK',
        'PAGES TWO TO FOUR',
    ]
    ordered = []
    remaining = list(sections)
    for pref in preferred:
        for i, s in enumerate(remaining):
            if s['header'] == pref:
                ordered.append(s)
                remaining.pop(i)
                break
    remaining.sort(key=lambda s: s['header'].lower())
    ordered.extend(remaining)
    return ordered


def main():
    print(f"Reading {INPUT_FILE}...")
    content = read_file(INPUT_FILE)
    print(f"Read {len(content.splitlines())} lines")
    
    print("Splitting into sections...")
    sections = split_into_sections(content)
    print(f"Found {len(sections)} sections")
    print(f"Unique headers: {len(set(s['header'] for s in sections))}")
    
    print("\nFiltering...")
    kept = []
    removed = []
    for s in sections:
        if s['header'] == 'PREAMBLE':
            kept.append(s)
            continue
        if should_keep_section(s['header']):
            kept.append(s)
        else:
            removed.append(s['header'])
    
    unique_removed = sorted(set(removed))
    print(f"Kept: {len(kept)}, Removed types: {len(unique_removed)}")
    
    print("\nCleaning boilerplate...")
    for s in kept:
        s['content'] = clean_boilerplate(s['content'])
    
    print("\nDeduplicating...")
    print(f"  Before: {len(kept)}")
    kept = dedup_headers(kept)
    kept = dedup_exact(kept)
    kept = dedup_near(kept)
    print(f"  After: {len(kept)}")
    
    print("\nSorting...")
    kept = sort_sections(kept)
    
    print(f"\nWriting {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# Atari System Development Guide\n\n")
        f.write("*Compiled and cleaned from atariarchives.org resources.*\n")
        f.write("*Comprehensive reference for Atari 400/800/XL/XE system programming.*\n\n")
        f.write("---\n\n## Table of Contents\n\n")
        for i, s in enumerate(kept):
            if s['header'] != 'PREAMBLE':
                anchor = re.sub(r'[^a-z0-9-]', '', s['header'].lower().replace(' ', '-'))
                f.write(f"{i}. [{s['header']}](#{anchor})\n")
        f.write("\n---\n\n")
        for s in kept:
            f.write(s['content'] + '\n\n---\n\n')
    
    lines = sum(1 for _ in open(OUTPUT_FILE, 'r', encoding='utf-8'))
    print(f"\nDone! {OUTPUT_FILE} ({lines} lines)")
    
    headers = [s['header'] for s in kept if s['header'] != 'PREAMBLE']
    print(f"\n{len(headers)} sections:")
    for h in headers:
        print(f"  - {h}")


if __name__ == '__main__':
    main()
