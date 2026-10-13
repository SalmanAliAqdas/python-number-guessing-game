"""Automated tests. Run with:  python -m unittest -v"""

import random
import unittest

import guess

EASY = guess.DIFFICULTIES["1"]


def scripted(answers):
    """Make a fake 'input' that returns the given answers one by one."""
    iterator = iter(answers)
    return lambda prompt="": next(iterator)


class RuleTests(unittest.TestCase):
    def test_secret_is_inside_range_many_times(self):
        rng = random.Random(1)
        for _ in range(500):
            self.assertTrue(1 <= guess.make_secret(1, 50, rng) <= 50)

    def test_judge(self):
        self.assertEqual(guess.judge_guess(10, 5), "low")
        self.assertEqual(guess.judge_guess(10, 15), "high")
        self.assertEqual(guess.judge_guess(10, 10), "correct")

    def test_parse_guess_valid(self):
        self.assertEqual(guess.parse_guess(" 42 ", 1, 50), 42)
        self.assertEqual(guess.parse_guess("1", 1, 50), 1)
        self.assertEqual(guess.parse_guess("50", 1, 50), 50)

    def test_parse_guess_invalid(self):
        for bad in ["abc", "", "4.5", "0", "51", "-3"]:
            with self.assertRaises(guess.GuessError, msg=bad):
                guess.parse_guess(bad, 1, 50)

    def test_temperature(self):
        self.assertEqual(guess.temperature(100, 101, 1, 500), "Very hot!")
        self.assertEqual(guess.temperature(100, 112, 1, 500), "Hot")
        self.assertEqual(guess.temperature(100, 150, 1, 500), "Warm")
        self.assertEqual(guess.temperature(100, 400, 1, 500), "Cold")

    def test_rating(self):
        self.assertEqual(guess.rating(2, 10), "Outstanding!")
        self.assertEqual(guess.rating(7, 10), "Well played!")
        self.assertEqual(guess.rating(10, 10), "Close call, but you made it!")


class HintTests(unittest.TestCase):
    def test_hint_1_even_odd(self):
        self.assertIn("even", guess.give_hint(20, 1, 1, 50, 1, 50))
        self.assertIn("odd", guess.give_hint(21, 1, 1, 50, 1, 50))

    def test_hint_3_last_digit(self):
        self.assertIn("7", guess.give_hint(37, 3, 1, 50, 1, 50))

    def test_hint_2_range_always_contains_secret(self):
        for seed in range(300):
            rng = random.Random(seed)
            secret = rng.randint(1, 500)
            text = guess.give_hint(secret, 2, 1, 500, 1, 500, rng)
            numbers = [int(word) for word in text.replace(".", "").split() if word.isdigit()]
            start, end = numbers
            self.assertTrue(start <= secret <= end, (secret, text))
            self.assertTrue(1 <= start <= end <= 500)

    def test_hint_2_respects_known_bounds(self):
        rng = random.Random(5)
        text = guess.give_hint(60, 2, 1, 100, 55, 70, rng)
        start, end = [int(w) for w in text.replace(".", "").split() if w.isdigit()]
        self.assertTrue(55 <= start <= 60 <= end <= 70)

    def test_no_fourth_hint(self):
        with self.assertRaises(ValueError):
            guess.give_hint(10, 4, 1, 50, 1, 50)


class RoundTests(unittest.TestCase):
    def play(self, answers, seed=3, difficulty=EASY):
        rng = random.Random(seed)
        secret = random.Random(seed).randint(difficulty["low"], difficulty["high"])
        output = []
        result = guess.play_round(difficulty, rng, scripted(answers), output.append)
        return secret, result, "\n".join(output)

    def test_win_on_first_guess(self):
        secret = random.Random(3).randint(1, 50)
        _, result, text = self.play([str(secret)])
        self.assertTrue(result["won"])
        self.assertEqual(result["guesses"], 1)
        self.assertIn("Correct!", text)

    def test_lose_after_all_attempts(self):
        secret = random.Random(3).randint(1, 50)
        wrong = [n for n in range(1, 51) if n != secret][:10]
        _, result, text = self.play([str(n) for n in wrong])
        self.assertFalse(result["won"])
        self.assertEqual(result["guesses"], 10)
        self.assertIn("Out of attempts", text)

    def test_invalid_input_does_not_cost_attempts(self):
        secret = random.Random(3).randint(1, 50)
        answers = ["abc", "0", "999", "", str(secret)]
        _, result, text = self.play(answers)
        self.assertTrue(result["won"])
        self.assertEqual(result["guesses"], 1)
        self.assertIn("did not use an attempt", text)

    def test_repeat_guess_does_not_cost_attempt(self):
        secret = random.Random(3).randint(1, 50)
        wrong = 1 if secret != 1 else 2
        _, result, text = self.play([str(wrong), str(wrong), str(secret)])
        self.assertEqual(result["guesses"], 2)
        self.assertIn("already tried", text)

    def test_hints_are_limited_to_three(self):
        secret = random.Random(3).randint(1, 50)
        answers = ["hint"] * 4 + [str(secret)]
        _, result, text = self.play(answers)
        self.assertEqual(text.count("Hint "), 3)
        self.assertIn("used all your hints", text)
        self.assertEqual(result["guesses"], 1)   # hints never cost attempts

    def test_give_up(self):
        secret, result, text = self.play(["q"])
        self.assertFalse(result["won"])
        self.assertTrue(result["gave_up"])
        self.assertIn(str(secret), text)

    def test_range_narrows_after_guesses(self):
        secret = random.Random(3).randint(1, 50)
        low_guess = max(1, secret - 5) if secret > 1 else 1
        if secret == 1:
            self.skipTest("secret is 1 for this seed")
        _, _, text = self.play([str(low_guess), str(secret)])
        self.assertIn(f"between {low_guess + 1} and 50", text)

    def test_binary_search_always_wins_in_allowed_attempts(self):
        """A perfect strategy must be able to win every difficulty."""
        for difficulty in guess.DIFFICULTIES.values():
            for seed in range(60):
                rng = random.Random(seed)
                secret = random.Random(seed).randint(difficulty["low"], difficulty["high"])
                low, high = difficulty["low"], difficulty["high"]
                answers = []
                while True:
                    middle = (low + high) // 2
                    answers.append(str(middle))
                    if middle == secret:
                        break
                    if middle < secret:
                        low = middle + 1
                    else:
                        high = middle - 1
                result = guess.play_round(difficulty, rng, scripted(answers), lambda text: None)
                self.assertTrue(result["won"], (difficulty["name"], secret))


class StatsTests(unittest.TestCase):
    def test_stats(self):
        stats = {}
        guess.update_stats(stats, "Easy", {"won": True, "guesses": 5})
        guess.update_stats(stats, "Easy", {"won": True, "guesses": 3})
        guess.update_stats(stats, "Easy", {"won": False, "guesses": 10})
        self.assertEqual(stats["Easy"], {"played": 3, "won": 2, "best": 3})
        self.assertIn("won 2 of 3", guess.format_stats(stats))
        self.assertIn("best: 3", guess.format_stats(stats))

    def test_empty_stats(self):
        self.assertEqual(guess.format_stats({}), "No games played yet.")


if __name__ == "__main__":
    unittest.main()
