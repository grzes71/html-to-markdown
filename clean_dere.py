"""
Clean dere.md - remove duplicates, navigation blocks, non-De Re Atari content,
and clean up formatting.
"""
import re

INPUT = r"c:\Users\grzes\Documents\Projects\html-to-markdown\out\dere.md"
OUTPUT = r"c:\Users\grzes\Documents\Projects\html-to-markdown\out\dere.md"

with open(INPUT, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original line count: {len(lines)}")

# -----------------------------------------------------------
# Step 1: Find where De Re Atari content ends
# The Software chapter is the last De Re Atari section.
# After it, "The Second Book Of Machine Language" starts.
# -----------------------------------------------------------
software_start = None
other_books_start = None
for i, line in enumerate(lines):
    if line.strip() == '## De Re Atari - Software':
        software_start = i
    if software_start and line.strip().startswith('## The Second Book Of Machine Language'):
        other_books_start = i
        break

if other_books_start:
    print(f"De Re Atari Software chapter at line {software_start+1}")
    print(f"Other books start at line {other_books_start+1}")
    # Find the nav block + --- before "The Second Book" to include in removal
    cut_point = other_books_start
    # Walk back past the nav block and ---
    for j in range(other_books_start - 1, max(0, other_books_start - 10), -1):
        stripped = lines[j].strip()
        if stripped == '---' or stripped in ('Return to Table of Contents', 'Back to previous page', ''):
            cut_point = j
        else:
            break
    print(f"Cut point for non-DeReAtari content: line {cut_point+1}")
else:
    cut_point = len(lines)
    print("No other books found - keeping all content")

# -----------------------------------------------------------
# Step 2: Remove the second copy of De Re Atari title/TOC (line ~11319+)
# and the Program Listing sections that follow it
# Find the second "## De Re Atari" (not "De Re Atari - Chapter")
# -----------------------------------------------------------
second_copy_start = None
found_first_dere = False
for i, line in enumerate(lines):
    s = line.strip()
    if s == '## De Re Atari':
        if not found_first_dere:
            found_first_dere = True
        else:
            second_copy_start = i
            break

if second_copy_start:
    print(f"Second De Re Atari copy starts at line {second_copy_start+1}")
    # Walk back to find the --- separator
    for j in range(second_copy_start - 1, max(0, second_copy_start - 5), -1):
        if lines[j].strip() == '---':
            second_copy_start = j
            break
    print(f"Cut point for second copy: line {second_copy_start+1}")
    if second_copy_start < cut_point:
        cut_point = second_copy_start

# Now truncate: keep lines[0:cut_point]
lines = lines[:cut_point]
print(f"After truncation: {len(lines)} lines")

# -----------------------------------------------------------
# Step 3: Remove navigation link blocks
# Patterns:
#   [Return to Table of Contents](URL)|
#   [Previous Chapter](URL)|
#   [Next Chapter](URL)
#   [Previous Section](URL)|
#   [Next Section](URL)
#   [Previous Page](URL)|
#   [Next Page](URL)
#   Return to Table of Contents   (non-link)
#   Back to previous page
#   [Return to Table of Contents](URL)
# -----------------------------------------------------------
nav_patterns = [
    re.compile(r'^\[Return to Table of Contents\]\(https?://[^)]+\)\|?$'),
    re.compile(r'^\[Previous Chapter\]\(https?://[^)]+\)\|?\s*$'),
    re.compile(r'^\[Next Chapter\]\(https?://[^)]+\)\s*$'),
    re.compile(r'^\[Previous Section\]\(https?://[^)]+\)\|?\s*$'),
    re.compile(r'^\[Next Section\]\(https?://[^)]+\)\s*$'),
    re.compile(r'^\[Previous Page\]\(https?://[^)]+\)\|?\s*$'),
    re.compile(r'^\[Next Page\]\(https?://[^)]+\)\s*$'),
    re.compile(r'^\[Next Chapter\]\(https?://[^)]+\)\|?\s*$'),
    re.compile(r'^Return to Table of Contents$'),
    re.compile(r'^Back to previous page$'),
]

nav_lines_to_remove = set()
for i, line in enumerate(lines):
    stripped = line.strip()
    for pat in nav_patterns:
        if pat.match(stripped):
            nav_lines_to_remove.add(i)
            break

print(f"Navigation lines to remove: {len(nav_lines_to_remove)}")

# Also remove --- lines that are DIRECTLY between nav blocks and chapter headers
# (i.e., --- that separates nav from next chapter)
hr_after_nav = set()
for i in nav_lines_to_remove:
    # Check if next non-empty line after this nav line is ---
    for j in range(i + 1, min(i + 5, len(lines))):
        s = lines[j].strip()
        if s == '':
            continue
        if s == '---':
            hr_after_nav.add(j)
        break

print(f"HR lines after nav to remove: {len(hr_after_nav)}")

# Build cleaned lines
cleaned = []
for i, line in enumerate(lines):
    if i in nav_lines_to_remove or i in hr_after_nav:
        continue
    cleaned.append(line)

lines = cleaned
print(f"After nav removal: {len(lines)} lines")

# -----------------------------------------------------------
# Step 4: Remove the site intro + email block between TOC and Chapter 1
# Lines matching "## AtariArchives.org" and "## E-mail AtariArchives.org"
# and everything between them until the next ## De Re Atari
# -----------------------------------------------------------
site_info_blocks = []
in_site_block = False
block_start = 0
for i, line in enumerate(lines):
    s = line.strip()
    if s.startswith('## AtariArchives.org') or s.startswith('## E-mail AtariArchives'):
        in_site_block = True
        block_start = i
    elif in_site_block and s.startswith('## De Re Atari'):
        site_info_blocks.append((block_start, i))
        in_site_block = False

print(f"Site info blocks to remove: {len(site_info_blocks)}")
for start, end in site_info_blocks:
    print(f"  Lines {start+1} to {end}")

# Remove those blocks
to_remove = set()
for start, end in site_info_blocks:
    for i in range(start, end):
        to_remove.add(i)

cleaned = []
for i, line in enumerate(lines):
    if i in to_remove:
        continue
    cleaned.append(line)

lines = cleaned
print(f"After site info removal: {len(lines)} lines")

# -----------------------------------------------------------
# Step 5: Clean up formatting
# - Collapse 3+ consecutive blank lines to 2
# - Collapse 2+ consecutive --- lines to 1
# - Remove blank lines immediately after ---
# - Remove trailing whitespace
# -----------------------------------------------------------

# First pass: strip trailing whitespace
lines = [l.rstrip() for l in lines]

# Second pass: collapse blank lines and --- lines
cleaned = []
prev_was_blank = False
prev_was_hr = False
blank_count = 0
hr_count = 0

for line in lines:
    s = line.strip()
    
    if s == '---':
        if not prev_was_hr:
            # Only keep --- if previous wasn't also ---
            # But first, if we had accumulated blank lines, add just one
            if blank_count > 0:
                cleaned.append('')
                blank_count = 0
            cleaned.append(line)
            prev_was_hr = True
            prev_was_blank = False
            hr_count = 1
        else:
            hr_count += 1
        continue
    
    if s == '':
        blank_count += 1
        prev_was_hr = False
        continue
    
    # Non-empty, non-HR line
    prev_was_hr = False
    
    # Add appropriate blank line separator
    if blank_count > 0:
        cleaned.append('')  # One blank line max between content
        blank_count = 0
    
    cleaned.append(line)

lines = cleaned

# Remove very first line if it's blank
while lines and lines[0].strip() == '':
    lines.pop(0)

# Remove trailing blank lines
while lines and lines[-1].strip() == '':
    lines.pop()

print(f"After formatting cleanup: {len(lines)} lines")

# -----------------------------------------------------------
# Write output
# -----------------------------------------------------------
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f"\nDone! Output written to {OUTPUT}")
print(f"Lines: {len(lines)}")
