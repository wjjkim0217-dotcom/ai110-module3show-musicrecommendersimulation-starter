# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify or YouTube generally work in two stages. First they predict how relevant each item is to a user, using signals such as listening history, skips, likes, what similar users enjoyed (collaborative filtering), and the attributes of the item itself (content-based filtering). Then they rank and filter those predictions into a final list, often adding rules for diversity, freshness, and removing songs the user already heard. Our version is a much smaller, content-based simulation: it has no listening history and no other users, so it works only from a user's stated preferences and the song attributes in the catalog. It prioritizes **energy** closeness first, then **mood** and **genre** as exact-match bonuses, with **acousticness** as a smaller closeness term. It favors transparency and simplicity over personalization at scale.

### What features does each `Song` use?

Each `Song` has ten fields, loaded from `data/songs.csv`:

- **Identity (not scored):** `id`, `title`, `artist`
- **Categorical (scored by exact match):** `genre`, `mood`
- **Numeric, 0–1 (scored by closeness):** `energy`, `acousticness`, `valence`
- **Stored but not scored:** `tempo_bpm`, `danceability`. Both largely repeat what `energy` already captures, and tempo would need rescaling.

### What information does the `UserProfile` store?

- `favorite_genre` (str): compared to `Song.genre`
- `favorite_mood` (str): compared to `Song.mood`
- `target_energy` (float, 0–1): compared to `Song.energy`
- `likes_acoustic` (bool): converted to an acousticness target (`1.0` if true, `0.0` if false) and compared to `Song.acousticness`

The profile has no valence target, so `Song.valence` is kept as data but is not part of the score yet.

The taste profile used for comparisons (in `src/main.py`) is a late-night study listener:

```python
user_prefs = {
    "genre": "lofi",        # exact match against Song.genre
    "mood": "chill",        # exact match against Song.mood
    "energy": 0.40,         # closeness to Song.energy (low = calm)
    "acousticness": 0.80,   # closeness to Song.acousticness (high = acoustic)
}
```

### How does the `Recommender` compute a score for each song?

The **Scoring Rule** judges one song against one user profile. Each feature contributes points, and the contributions are summed:

```
score = 1.17 * energy_closeness
      + 1.00 * mood_match
      + 1.00 * genre_match
      + 0.50 * acoustic_closeness
```

- `energy_closeness = 1 - abs(target_energy - song.energy)`
- `acoustic_closeness = 1 - abs(acoustic_target - song.acousticness)`
- `mood_match` and `genre_match` are `1` for an exact match and `0` otherwise

A mood match and a genre match are worth 1 point each; energy and acousticness are scaled from the earlier weights relative to mood. The maximum score is about 3.67. Closeness is used for the numeric features, instead of "higher is better", so a user who wants chill music is not pushed toward loud songs. The scoring rule also returns a list of reasons, one per contributing term (for example, "energy is close to your target").

### How do you choose which songs to recommend?

The **Ranking Rule** works on the whole catalog:

1. Load all songs from the CSV.
2. Run the scoring rule on every song.
3. Sort by score, highest first.
4. Return the top *k* songs, each with its score and explanation.

The two rules are kept separate: scoring answers "how good is this one song for this user?", and ranking answers "which songs do we show, and in what order?".

### Algorithm Recipe

**Data flow:** Input (user prefs) -> Process (judge every song in the CSV) -> Output (top *k*).

```
INPUT     user_prefs {genre, mood, energy, acousticness} + k
   |
LOAD      load_songs("data/songs.csv")  ->  18 song dicts
   |
PROCESS   for each song:
   |         score_song(user_prefs, song) -> (score, reasons)
   |
OUTPUT    sort by score (highest first) -> top k as (song, score, explanation)
```

**Finalized rules:**

1. **Energy (up to 1.17 points):** `1.17 * (1 - abs(user.energy - song.energy))`. Closer to the target scores higher.
2. **Mood (1 point):** `1` if `user.mood == song.mood`, else `0`.
3. **Genre (1 point):** `1` if `user.genre == song.genre`, else `0`.
4. **Acousticness (up to 0.5 points):** `0.5 * (1 - abs(user.acousticness - song.acousticness))`.
5. **Total:** add the four parts (maximum about 3.67). Each part that earns points adds a reason string.
6. **Rank:** score every song, sort highest first, and return the top *k*. Tied scores keep CSV order.

`valence`, `tempo_bpm` and `danceability` are not scored.

### Potential Biases

- **Labels outweigh sound.** Mood and genre together are worth 2 of about 3.67 points (54%). A song that matches both labels but is far from the target energy and acousticness can still outrank a song that matches the sound exactly. For the lofi/chill profile, Focus Flow (lofi, `focused`) already ranks above Spacewalk Thoughts (ambient, `chill`), even though a chill listener may prefer the second.
- **Exact-match genre is all-or-nothing.** "Indie pop" gets no credit against "pop", and "ambient" gets none against "lofi", even though they are close. Great songs in a neighboring genre are penalized.
- **The catalog is uneven.** Lofi has 3 songs and every other genre has 1 or 2, so a lofi listener gets more genre bonuses than anyone else. For most other users only one song can earn the genre bonus, and the rest of the list is decided by energy and acousticness.
- **Energy and acousticness overlap.** In this data they are almost mirror images, so the two terms partly double count the same "calm and acoustic vs loud and electronic" preference.
- **Valence is ignored.** A sad song and a happy song with similar energy look alike to the scorer. Blue Highway Blues (blues, `sad`) ranks fifth for the chill lofi profile mostly on energy and acousticness.
- **One genre and one mood per user.** A listener who likes both lofi and jazz, or both chill and relaxed, cannot say so.
- **No diversity.** Near-identical songs such as Midnight Coding and Library Rain (scores within 0.02) will appear side by side.
- **Stated tastes only.** There is no listening history or feedback, so the system cannot learn that a user's real taste differs from what they typed.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



