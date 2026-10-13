"""Number guessing game.

The computer picks a secret number. You have a limited number of attempts
to guess it. After each wrong guess you get a higher/lower clue and a
hot/cold clue, and you can ask for up to 3 extra hints per game.
"""

import random

DIFFICULTIES = {
    "1": {"name": "Easy", "low": 1, "high": 50, "attempts": 10},
    "2": {"name": "Medium", "low": 1, "high": 100, "attempts": 7},
    "3": {"name": "Hard", "low": 1, "high": 500, "attempts": 9},
}
MAX_HINTS = 3


class GuessError(Exception):
    """Input that is not a valid guess (it does not cost an attempt)."""


# ---------- Game rules (pure functions, easy to test) ----------

def make_secret(low, high, rng=random):
    return rng.randint(low, high)


def parse_guess(text, low, high):
    """Turn typed text into a whole number inside the allowed range."""
    try:
        number = int(text.strip())
    except ValueError:
        raise GuessError("Please type a whole number, 'hint', or 'q' to give up.")
    if number < low or number > high:
        raise GuessError(f"Your guess must be between {low} and {high}.")
    return number


def judge_guess(secret, guess):
    if guess < secret:
        return "low"
    if guess > secret:
        return "high"
    return "correct"


def temperature(secret, guess, low, high):
    """How close is the guess? Based on the size of the range."""
    distance = abs(secret - guess)
    fraction = distance / (high - low + 1)
    if fraction <= 0.02:
        return "Very hot!"
    if fraction <= 0.05:
        return "Hot"
    if fraction <= 0.15:
        return "Warm"
    return "Cold"


def give_hint(secret, level, low, high, known_low, known_high, rng=random):
    """Hint 1: even or odd. Hint 2: a narrower range. Hint 3: the last digit."""
    if level == 1:
        return f"The number is {'even' if secret % 2 == 0 else 'odd'}."
    if level == 2:
        width = max(6, (high - low + 1) // 5)
        start = secret - rng.randint(0, width - 1)
        start = max(start, known_low)
        end = min(start + width - 1, known_high)
        start = max(min(start, secret), known_low)
        end = max(end, secret)
        return f"The number is between {start} and {end}."
    if level == 3:
        return f"The last digit of the number is {secret % 10}."
    raise ValueError("No more hints.")


def rating(guesses, attempts):
    used = guesses / attempts
    if used <= 0.5:
        return "Outstanding!"
    if used <= 0.8:
        return "Well played!"
    return "Close call, but you made it!"


# ---------- One round of the game ----------

def play_round(difficulty, rng=random, ask=input, show=print):
    """Play one game. Returns a dict describing the result."""
    low, high, attempts = difficulty["low"], difficulty["high"], difficulty["attempts"]
    secret = make_secret(low, high, rng)
    known_low, known_high = low, high
    guesses_made = []
    hints_used = 0

    show(f"\n{difficulty['name']} mode: I am thinking of a number from {low} to {high}.")
    show(f"You have {attempts} attempts and {MAX_HINTS} hints. Type 'hint' for a hint, or 'q' to give up.")

    while len(guesses_made) < attempts:
        left = attempts - len(guesses_made)
        text = ask(f"\nAttempts left: {left}. Your guess: ").strip().lower()

        if text in ("q", "quit", "give up"):
            show(f"You gave up. The number was {secret}.")
            return {"won": False, "guesses": len(guesses_made), "secret": secret, "gave_up": True}

        if text == "hint":
            if hints_used >= MAX_HINTS:
                show("You have used all your hints.")
                continue
            hints_used += 1
            show(f"Hint {hints_used} of {MAX_HINTS}: " + give_hint(secret, hints_used, low, high, known_low, known_high, rng))
            continue

        try:
            guess = parse_guess(text, low, high)
        except GuessError as error:
            show(f"{error} (This did not use an attempt.)")
            continue

        if guess in guesses_made:
            show("You already tried that number. (This did not use an attempt.)")
            continue

        guesses_made.append(guess)
        result = judge_guess(secret, guess)

        if result == "correct":
            show(f"\nCorrect! The number was {secret}. You needed {len(guesses_made)} guess(es). "
                 f"{rating(len(guesses_made), attempts)}")
            return {"won": True, "guesses": len(guesses_made), "secret": secret, "gave_up": False}

        if result == "low":
            known_low = max(known_low, guess + 1)
            show(f"Too low. {temperature(secret, guess, low, high)}")
        else:
            known_high = min(known_high, guess - 1)
            show(f"Too high. {temperature(secret, guess, low, high)}")
        show(f"The number is now between {known_low} and {known_high}.")

    show(f"\nOut of attempts! The number was {secret}.")
    return {"won": False, "guesses": len(guesses_made), "secret": secret, "gave_up": False}


# ---------- Menu and statistics ----------

MENU_TEXT = """\
Number Guessing Game
  1. Easy    (1-50,  10 attempts)
  2. Medium  (1-100,  7 attempts)
  3. Hard    (1-500,  9 attempts)
  q. Quit"""


def update_stats(stats, difficulty_name, result):
    entry = stats.setdefault(difficulty_name, {"played": 0, "won": 0, "best": None})
    entry["played"] += 1
    if result["won"]:
        entry["won"] += 1
        if entry["best"] is None or result["guesses"] < entry["best"]:
            entry["best"] = result["guesses"]


def format_stats(stats):
    if not stats:
        return "No games played yet."
    lines = ["Your results this session:"]
    for name, entry in stats.items():
        best = f", best: {entry['best']} guess(es)" if entry["best"] else ""
        lines.append(f"  {name}: won {entry['won']} of {entry['played']}{best}")
    return "\n".join(lines)


def main():
    stats = {}
    while True:
        print()
        print(MENU_TEXT)
        choice = input("Your choice: ").strip().lower()
        if choice in ("q", "quit", "exit"):
            print()
            print(format_stats(stats))
            print("Thanks for playing. Goodbye!")
            break
        if choice not in DIFFICULTIES:
            print("Please choose 1, 2, 3 or q.")
            continue
        difficulty = DIFFICULTIES[choice]
        result = play_round(difficulty)
        update_stats(stats, difficulty["name"], result)
        print()
        print(format_stats(stats))
        input("\nPress Enter to go back to the menu...")


if __name__ == "__main__":
    main()
