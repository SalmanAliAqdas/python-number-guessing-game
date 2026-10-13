# Number Guessing Game

A command-line number guessing game written in Python. The computer picks a secret number, and you try to guess it before you run out of attempts.

## Features
- Three difficulty levels with different number ranges and attempt limits
- "Too high" / "Too low" feedback, plus hot/cold feedback showing how close you are
- The range of possible numbers narrows after every guess
- Up to 3 hints per game, which do not use up attempts
- Invalid input, out-of-range numbers and repeated guesses never cost an attempt
- Give up at any time to reveal the number
- Session statistics: games won and your best score per difficulty
- Every difficulty can be won with a smart strategy (verified by an automated test)
- Automated tests (21)

## Requirements
- Python 3 installed
- No extra packages needed

## How to run
```
python guess.py
```
If `python` is not recognized on Windows, use `py guess.py`.

## How to play
Choose a difficulty from the menu:

| Level | Range | Attempts |
|---|---|---|
| Easy | 1 to 50 | 10 |
| Medium | 1 to 100 | 7 |
| Hard | 1 to 500 | 9 |

Type a number and press Enter. You can also type:
- `hint` for a hint (3 per game: even or odd, then a narrower range, then the last digit)
- `q` to give up

Example round:
```
Easy mode: I am thinking of a number from 1 to 50.
You have 10 attempts and 3 hints. Type 'hint' for a hint, or 'q' to give up.

Attempts left: 10. Your guess: 25
Too high. Warm
The number is now between 1 and 24.

Attempts left: 9. Your guess: hint
Hint 1 of 3: The number is odd.
```

## Tip
The best strategy is to always guess the middle of the remaining range. This is called binary search, and it is how computers find things quickly in huge lists.

## Running the tests
```
python -m unittest -v
```

## How it works
- `make_secret` picks the random number
- `judge_guess` and `temperature` give the feedback
- `give_hint` creates the three hints
- `play_round` runs one full game
- The game logic is separate from the keyboard input, so it can be tested automatically

## Project structure
- `guess.py`: the game
- `test_guess.py`: automated tests
- `.gitignore`: files Git should ignore
- `readme.md`: this file

## Possible future improvements
- Save high scores to a file
- Two-player mode
- A graphical or web version
