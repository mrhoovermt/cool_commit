#!/usr/bin/env python3
"""
Generate backdated git commits to draw patterns on GitHub's contribution graph.
Years 2016-2025, each with a unique pattern.

GitHub's contribution graph:
- 7 rows: Sunday (top) through Saturday (bottom)
- ~52-53 columns per year, one per week
- The graph for a given year starts on the Sunday of the week containing Jan 1,
  and ends on the Saturday of the week containing Dec 31.
"""

import subprocess
import os
from datetime import datetime, timedelta

# ─── 5×7 BLOCK LETTER FONT ───────────────────────────────────────────────────
# Each letter is 5 columns wide × 7 rows tall (rows = days Sun-Sat)
# 1 = commit, 0 = no commit
FONT = {
    'A': [
        [0,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
    ],
    'B': [
        [1,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,0],
    ],
    'D': [
        [1,1,1,0,0],
        [1,0,0,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,1,0],
        [1,1,1,0,0],
    ],
    'E': [
        [1,1,1,1,1],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,1,1,1,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,1,1,1,1],
    ],
    'H': [
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
    ],
    'I': [
        [1,1,1,1,1],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [1,1,1,1,1],
    ],
    'K': [
        [1,0,0,1,0],
        [1,0,1,0,0],
        [1,1,0,0,0],
        [1,1,0,0,0],
        [1,0,1,0,0],
        [1,0,0,1,0],
        [1,0,0,0,1],
    ],
    'L': [
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,1,1,1,1],
    ],
    'N': [
        [1,0,0,0,1],
        [1,1,0,0,1],
        [1,0,1,0,1],
        [1,0,1,0,1],
        [1,0,0,1,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
    ],
    'O': [
        [0,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [0,1,1,1,0],
    ],
    'P': [
        [1,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
        [1,0,0,0,0],
    ],
    'R': [
        [1,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,0],
        [1,0,1,0,0],
        [1,0,0,1,0],
        [1,0,0,0,1],
    ],
    'S': [
        [0,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,0],
        [0,1,1,1,0],
        [0,0,0,0,1],
        [1,0,0,0,1],
        [0,1,1,1,0],
    ],
    'T': [
        [1,1,1,1,1],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
        [0,0,1,0,0],
    ],
    'W': [
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,1,0,1],
        [1,0,1,0,1],
        [1,1,0,1,1],
        [1,0,0,0,1],
    ],
}

# ─── PATTERN DEFINITIONS ─────────────────────────────────────────────────────

def text_to_grid(text, total_cols=52):
    """Convert a text string to a 7×total_cols grid using the block font."""
    grid = [[0]*total_cols for _ in range(7)]
    letter_width = 5
    spacing = 1
    space_width = 3  # width of a space between words

    # Calculate total width
    total_text_width = 0
    for i, ch in enumerate(text):
        if ch == ' ':
            total_text_width += space_width
        else:
            total_text_width += letter_width
        if i < len(text) - 1 and text[i+1] != ' ' and ch != ' ':
            total_text_width += spacing
    start_col = (total_cols - total_text_width) // 2  # center it

    col = start_col
    for i, ch in enumerate(text):
        if ch == ' ':
            col += space_width
            continue
        if ch not in FONT:
            col += letter_width + spacing
            continue
        glyph = FONT[ch]
        for row in range(7):
            for c in range(letter_width):
                if 0 <= col + c < total_cols:
                    grid[row][col + c] = glyph[row][c]
        col += letter_width
        if i < len(text) - 1 and text[i+1] != ' ':
            col += spacing
    return grid


# ─── YEAR → GRID MAPPING ─────────────────────────────────────────────────────

YEAR_TEXT = {
    2016: "POWER",
    2017: "TO",
    2018: "THE",
    2019: "PEOPLE",
    2020: "ALIENS",
    2021: "ARE",
    2022: "REAL",
    2023: "BE KIND",
    2024: "TO",
    2025: "OTHERS",
}


def get_year_grid(year):
    """Return the 7×N grid for a given year."""
    text = YEAR_TEXT.get(year)
    if text:
        return text_to_grid(text)
    return None


# ─── COMMIT GENERATION ────────────────────────────────────────────────────────

def get_year_sundays(year):
    """Get the first Sunday on or before Jan 1 of the given year.
    GitHub's contribution graph for a year starts on this Sunday.
    Returns list of (date, row, col) for every day in the graph year."""
    jan1 = datetime(year, 1, 1)
    # Find Sunday on or before Jan 1
    start = jan1 - timedelta(days=jan1.weekday() + 1)  # weekday(): Mon=0
    if jan1.weekday() == 6:  # Sunday
        start = jan1

    # The graph covers the entire year. We need Sundays from the week
    # containing Jan 1 through the week containing Dec 31.
    dec31 = datetime(year, 12, 31)
    # End on the Saturday of the week containing Dec 31
    end = dec31 + timedelta(days=(5 - dec31.weekday()) % 7)
    if dec31.weekday() == 6:  # If Dec 31 is Sunday
        end = dec31 + timedelta(days=6)

    days = []
    current = start
    while current <= end:
        col = (current - start).days // 7
        row = (current - start).days % 7
        if current.year == year:  # only commit in the target year
            days.append((current, row, col))
        current += timedelta(days=1)

    return days


def generate_commits():
    """Generate all the backdated commits."""
    commit_dates = []

    for year in range(2016, 2026):
        grid = get_year_grid(year)
        if grid is None:
            continue

        days = get_year_sundays(year)
        num_cols = max(col for _, _, col in days) + 1

        for date, row, col in days:
            if col < len(grid[0]) and grid[row][col] == 1:
                commit_dates.append(date)

    # Sort chronologically
    commit_dates.sort()

    print(f"Total commits to generate: {len(commit_dates)}")
    print(f"Date range: {commit_dates[0].strftime('%Y-%m-%d')} to {commit_dates[-1].strftime('%Y-%m-%d')}")
    print()

    # Generate commits
    for i, date in enumerate(commit_dates):
        date_str = date.strftime("%Y-%m-%dT12:00:00")
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str

        # Append to a simple counter file
        with open("contributions.txt", "a") as f:
            f.write(f"Commit #{i+1} on {date.strftime('%Y-%m-%d')}\n")

        subprocess.run(["git", "add", "contributions.txt"], check=True,
                       capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Contribution #{i+1}"],
            env=env, check=True, capture_output=True
        )

        if (i + 1) % 100 == 0 or i == len(commit_dates) - 1:
            print(f"  Generated {i+1}/{len(commit_dates)} commits...")

    print("\nDone! All commits generated.")


def preview_year(year):
    """Print an ASCII preview of a year's pattern."""
    grid = get_year_grid(year)
    if grid is None:
        return
    print(f"\n{'='*60}")
    print(f"  {year}")
    print(f"{'='*60}")
    day_labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    for row in range(7):
        label = day_labels[row]
        line = f"  {label} "
        for col in range(len(grid[0])):
            line += "█" if grid[row][col] else "·"
        print(line)


def preview_all():
    """Preview all years."""
    for year in range(2016, 2026):
        preview_year(year)
    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        preview_all()
        sys.exit(0)

    # Check if we're in a git repo
    result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: Not inside a git repository.")
        print("Please run: git init")
        sys.exit(1)

    # Show preview first
    preview_all()

    print("Generating commits...")
    print()
    generate_commits()
