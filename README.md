# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version is a small, content-based music recommender. It loads an 18-song catalog from a CSV file. A user gives a favorite genre, a favorite mood, and targets for energy and acousticness. The system scores every song, sorts the scores, and shows the top five. Each pick comes with plain-language reasons, such as "mood matches 'happy' (+1.00)". I tested it with ten profiles, including seven built to trick it. The main finding is that the genre and mood bonuses can override what a user asks for in energy. See the [Model Card](model_card.md) for the full evaluation.

---

## How The System Works

Real-world recommenders like Spotify or YouTube generally work in two stages. First they predict how relevant each item is to a user, using signals such as listening history, skips, likes, what similar users enjoyed (collaborative filtering), and the attributes of the item itself (content-based filtering). Then they rank and filter those predictions into a final list, often adding rules for diversity, freshness, and removing songs the user already heard. Our version is a much smaller, content-based simulation: it has no listening history and no other users, so it works only from a user's stated preferences and the song attributes in the catalog. It prioritizes **energy** closeness first, then **mood** and **genre** as exact-match bonuses, with **acousticness** as a smaller closeness term. It favors transparency and simplicity over personalization at scale.

### What features does each `Song` use?

Each `Song` has ten fields, loaded from `data/songs.csv`:

- **Identity (not scored):** `id`, `title`, `artist`
- **Categorical (scored by exact match):** `genre`, `mood`
- **Numeric, 0–1 (scored by closeness):** `energy`, `acousticness`
- **Stored but not scored:** `tempo_bpm`, `danceability`, `valence`. Tempo and danceability largely repeat what `energy` already captures (and tempo would need rescaling); valence has no matching user preference yet.

### What information does the `UserProfile` store?

- `favorite_genre` (str): compared to `Song.genre`
- `favorite_mood` (str): compared to `Song.mood`
- `target_energy` (float, 0–1): compared to `Song.energy`
- `likes_acoustic` (bool): converted to an acousticness target (`1.0` if true, `0.0` if false) and compared to `Song.acousticness`

The profile has no valence target, so `Song.valence` is kept as data but is not part of the score yet.

`Recommender.recommend` and `Recommender.explain_recommendation` take a `UserProfile`, convert it to a preferences dict, and call the same `score_song` used everywhere else. `src/main.py` uses the functional API (`recommend_songs`) with plain dicts, which take an acousticness number directly instead of a true/false flag.

`src/main.py` defines three baseline profiles (`PROFILES`) and seven adversarial ones (`ADVERSARIAL_PROFILES`). For example, the late-night study listener:

```python
"Chill Lofi": {
    "genre": "lofi",        # exact match against Song.genre
    "mood": "chill",        # exact match against Song.mood
    "energy": 0.30,         # closeness to Song.energy (low = calm)
    "acousticness": 0.80,   # closeness to Song.acousticness (high = acoustic)
},
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

- **Labels outweigh sound.** Mood and genre together are worth 2 of about 3.67 points (54%). A song that matches both labels but is far from the target energy and acousticness can still outrank a song that matches the sound exactly. For the "Conflict: High Energy + Sad" profile (energy 0.90), Blue Highway Blues (energy 0.40) scores 2.75 and beats Storm Runner (energy 0.91) at 1.66. For Chill Lofi, Focus Flow (2.54) and Coffee Shop Stories (1.54) are about equally close in sound, but Focus Flow's lofi label puts it a full point ahead.
- **Exact-match genre is all-or-nothing.** "Indie pop" gets no credit against "pop", and "ambient" gets none against "lofi", even though they are close. Great songs in a neighboring genre are penalized.
- **The catalog is uneven.** Lofi has 3 songs and every other genre has 1 or 2, so a lofi listener gets more genre bonuses than anyone else. For most other users only one song can earn the genre bonus, and the rest of the list is decided by energy and acousticness.
- **Energy and acousticness overlap.** In this data they are almost mirror images, so the two terms partly double count the same "calm and acoustic vs loud and electronic" preference.
- **Valence is ignored.** A sad song and a happy song with similar energy look alike to the scorer. Blue Highway Blues (blues, `sad`) scores 1.53 for the Chill Lofi profile on energy and acousticness alone, only 0.01 behind the #5 pick.
- **One genre and one mood per user.** A listener who likes both lofi and jazz, or both chill and relaxed, cannot say so.
- **No diversity.** Near-identical songs appear side by side: Library Rain and Midnight Coding (both lofi and `chill`) take #1 and #2 for Chill Lofi, 0.10 apart.
- **Stated tastes only.** There is no listening history or feedback, so the system cannot learn that a user's real taste differs from what they typed.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

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

The start of the output from `python -m src.main` (run from the project root), showing the first profile, High-Energy Pop (genre `pop`, mood `happy`, energy `0.85`, acousticness `0.15`):

```
Loaded songs: 18

============================================================
            TOP RECOMMENDATIONS: High-Energy Pop            
============================================================

#1  Sunrise City  by Neon Echo
    Score: 3.62 / 3.67
    Why:
      - energy is close to your target (+1.13)
      - mood matches 'happy' (+1.00)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------

#2  Gym Hero  by Max Pulse
    Score: 2.53 / 3.67
    Why:
      - energy is close to your target (+1.08)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.45)
------------------------------------------------------------

#3  Rooftop Lights  by Indigo Parade
    Score: 2.46 / 3.67
    Why:
      - energy is close to your target (+1.06)
      - mood matches 'happy' (+1.00)
      - acousticness is close to your target (+0.40)
------------------------------------------------------------

#4  Storm Runner  by Voltline
    Score: 1.57 / 3.67
    Why:
      - energy is close to your target (+1.10)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#5  Concrete Crown  by Block Theory
    Score: 1.57 / 3.67
    Why:
      - energy is close to your target (+1.09)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------
```

The program then prints the same block for the other nine profiles.

---

## Profile Evaluation Output

Terminal output of `python -m src.main` for the three baseline profiles and the seven adversarial profiles (`PROFILES` and `ADVERSARIAL_PROFILES` in `src/main.py`), top 5 each. The banner line above each block is left out.

### High-Energy Pop

Baseline: pop + happy + high energy. Sunrise City matches everything and scores near the 3.67 ceiling.

```

#1  Sunrise City  by Neon Echo
    Score: 3.62 / 3.67
    Why:
      - energy is close to your target (+1.13)
      - mood matches 'happy' (+1.00)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------

#2  Gym Hero  by Max Pulse
    Score: 2.53 / 3.67
    Why:
      - energy is close to your target (+1.08)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.45)
------------------------------------------------------------

#3  Rooftop Lights  by Indigo Parade
    Score: 2.46 / 3.67
    Why:
      - energy is close to your target (+1.06)
      - mood matches 'happy' (+1.00)
      - acousticness is close to your target (+0.40)
------------------------------------------------------------

#4  Storm Runner  by Voltline
    Score: 1.57 / 3.67
    Why:
      - energy is close to your target (+1.10)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#5  Concrete Crown  by Block Theory
    Score: 1.57 / 3.67
    Why:
      - energy is close to your target (+1.09)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------
```

### Chill Lofi

Baseline: two lofi/chill tracks lead, then partial matches (mood-only, genre-only).

```

#1  Library Rain  by Paper Lanterns
    Score: 3.58 / 3.67
    Why:
      - energy is close to your target (+1.11)
      - mood matches 'chill' (+1.00)
      - genre matches 'lofi' (+1.00)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#2  Midnight Coding  by LoRoom
    Score: 3.48 / 3.67
    Why:
      - energy is close to your target (+1.03)
      - mood matches 'chill' (+1.00)
      - genre matches 'lofi' (+1.00)
      - acousticness is close to your target (+0.45)
------------------------------------------------------------

#3  Spacewalk Thoughts  by Orbit Bloom
    Score: 2.59 / 3.67
    Why:
      - energy is close to your target (+1.15)
      - mood matches 'chill' (+1.00)
      - acousticness is close to your target (+0.44)
------------------------------------------------------------

#4  Focus Flow  by LoRoom
    Score: 2.54 / 3.67
    Why:
      - energy is close to your target (+1.05)
      - genre matches 'lofi' (+1.00)
      - acousticness is close to your target (+0.49)
------------------------------------------------------------

#5  Coffee Shop Stories  by Slow Stereo
    Score: 1.54 / 3.67
    Why:
      - energy is close to your target (+1.09)
      - acousticness is close to your target (+0.46)
------------------------------------------------------------
```

### Deep Intense Rock

Baseline: Storm Runner is the only rock song; Gym Hero follows on the intense mood alone.

```

#1  Storm Runner  by Voltline
    Score: 3.66 / 3.67
    Why:
      - energy is close to your target (+1.16)
      - mood matches 'intense' (+1.00)
      - genre matches 'rock' (+1.00)
      - acousticness is close to your target (+0.50)
------------------------------------------------------------

#2  Gym Hero  by Max Pulse
    Score: 2.63 / 3.67
    Why:
      - energy is close to your target (+1.16)
      - mood matches 'intense' (+1.00)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#3  Pulse Cathedral  by Helix Drop
    Score: 1.60 / 3.67
    Why:
      - energy is close to your target (+1.13)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#4  Iron Requiem  by Grave Engine
    Score: 1.58 / 3.67
    Why:
      - energy is close to your target (+1.11)
      - acousticness is close to your target (+0.46)
------------------------------------------------------------

#5  Sunrise City  by Neon Echo
    Score: 1.51 / 3.67
    Why:
      - energy is close to your target (+1.05)
      - acousticness is close to your target (+0.46)
------------------------------------------------------------
```

### Conflict: High Energy + Sad

Adversarial: wants energy 0.9 but blues/sad. The slow Blue Highway Blues (energy 0.40) still wins because genre + mood give 2.0 points versus at most 1.17 for energy.

```

#1  Blue Highway Blues  by Delta Mercy
    Score: 2.75 / 3.67
    Why:
      - energy is close to your target (+0.58)
      - mood matches 'sad' (+1.00)
      - genre matches 'blues' (+1.00)
      - acousticness is close to your target (+0.17)
------------------------------------------------------------

#2  Storm Runner  by Voltline
    Score: 1.66 / 3.67
    Why:
      - energy is close to your target (+1.16)
      - acousticness is close to your target (+0.50)
------------------------------------------------------------

#3  Gym Hero  by Max Pulse
    Score: 1.61 / 3.67
    Why:
      - energy is close to your target (+1.13)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#4  Pulse Cathedral  by Helix Drop
    Score: 1.58 / 3.67
    Why:
      - energy is close to your target (+1.11)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#5  Iron Requiem  by Grave Engine
    Score: 1.55 / 3.67
    Why:
      - energy is close to your target (+1.09)
      - acousticness is close to your target (+0.46)
------------------------------------------------------------
```

### Split: Pop Genre + Sad Mood

Adversarial: genre and mood point to different songs. The mood match (Blue Highway Blues) edges out the genre match (Sunrise City) on the numeric terms.

```

#1  Blue Highway Blues  by Delta Mercy
    Score: 2.42 / 3.67
    Why:
      - energy is close to your target (+1.05)
      - mood matches 'sad' (+1.00)
      - acousticness is close to your target (+0.37)
------------------------------------------------------------

#2  Sunrise City  by Neon Echo
    Score: 2.14 / 3.67
    Why:
      - energy is close to your target (+0.80)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.34)
------------------------------------------------------------

#3  Gym Hero  by Max Pulse
    Score: 1.94 / 3.67
    Why:
      - energy is close to your target (+0.67)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.28)
------------------------------------------------------------

#4  Velvet Hours  by Maya Lune
    Score: 1.59 / 3.67
    Why:
      - energy is close to your target (+1.15)
      - acousticness is close to your target (+0.44)
------------------------------------------------------------

#5  Island Sunday  by Sol Tide
    Score: 1.55 / 3.67
    Why:
      - energy is close to your target (+1.08)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------
```

### Impossible: Energetic + Acoustic

Adversarial: no song is both high-energy and acoustic. Storm Runner wins on categories; the 0.95 acousticness request earns only +0.08.

```

#1  Storm Runner  by Voltline
    Score: 3.20 / 3.67
    Why:
      - energy is close to your target (+1.12)
      - mood matches 'intense' (+1.00)
      - genre matches 'rock' (+1.00)
      - acousticness is close to your target (+0.08)
------------------------------------------------------------

#2  Gym Hero  by Max Pulse
    Score: 2.20 / 3.67
    Why:
      - energy is close to your target (+1.15)
      - mood matches 'intense' (+1.00)
      - acousticness is close to your target (+0.05)
------------------------------------------------------------

#3  Pulse Cathedral  by Helix Drop
    Score: 1.21 / 3.67
    Why:
      - energy is close to your target (+1.17)
      - acousticness is close to your target (+0.05)
------------------------------------------------------------

#4  Iron Requiem  by Grave Engine
    Score: 1.19 / 3.67
    Why:
      - energy is close to your target (+1.15)
      - acousticness is close to your target (+0.04)
------------------------------------------------------------

#5  Rooftop Lights  by Indigo Parade
    Score: 1.15 / 3.67
    Why:
      - energy is close to your target (+0.95)
      - acousticness is close to your target (+0.20)
------------------------------------------------------------
```

### Unknown Genre/Mood

Adversarial: labels absent from the catalog. Only numeric terms score, so the top score is just 1.62 and nothing warns the user.

```

#1  Island Sunday  by Sol Tide
    Score: 1.62 / 3.67
    Why:
      - energy is close to your target (+1.15)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#2  Velvet Hours  by Maya Lune
    Score: 1.57 / 3.67
    Why:
      - energy is close to your target (+1.08)
      - acousticness is close to your target (+0.49)
------------------------------------------------------------

#3  Rooftop Lights  by Indigo Parade
    Score: 1.46 / 3.67
    Why:
      - energy is close to your target (+0.98)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#4  Night Drive Loop  by Neon Echo
    Score: 1.40 / 3.67
    Why:
      - energy is close to your target (+0.99)
      - acousticness is close to your target (+0.41)
------------------------------------------------------------

#5  Dusty Porch Light  by Hollow Creek
    Score: 1.32 / 3.67
    Why:
      - energy is close to your target (+1.03)
      - acousticness is close to your target (+0.29)
------------------------------------------------------------
```

### Case Mismatch: 'Pop'/'HAPPY'

Adversarial: same intent as High-Energy Pop, but capitalised. Labels are now normalised (lowercased and trimmed) before comparing, so this matches the High-Energy Pop output exactly. Before the fix, exact string matching awarded no category points and the top score was 1.62.

```

#1  Sunrise City  by Neon Echo
    Score: 3.62 / 3.67
    Why:
      - energy is close to your target (+1.13)
      - mood matches 'happy' (+1.00)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------

#2  Gym Hero  by Max Pulse
    Score: 2.53 / 3.67
    Why:
      - energy is close to your target (+1.08)
      - genre matches 'pop' (+1.00)
      - acousticness is close to your target (+0.45)
------------------------------------------------------------

#3  Rooftop Lights  by Indigo Parade
    Score: 2.46 / 3.67
    Why:
      - energy is close to your target (+1.06)
      - mood matches 'happy' (+1.00)
      - acousticness is close to your target (+0.40)
------------------------------------------------------------

#4  Storm Runner  by Voltline
    Score: 1.57 / 3.67
    Why:
      - energy is close to your target (+1.10)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#5  Concrete Crown  by Block Theory
    Score: 1.57 / 3.67
    Why:
      - energy is close to your target (+1.09)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------
```

### Out of Range: energy 2.0

Adversarial: energy outside 0-1 is now clamped to 1.0, so the energy term stays between 0 and 1.17 and scores remain meaningful. Before the fix the energy term went negative (+-0.06) and the top score was 2.42.

```

#1  Pulse Cathedral  by Helix Drop
    Score: 3.59 / 3.67
    Why:
      - energy is close to your target (+1.11)
      - mood matches 'euphoric' (+1.00)
      - genre matches 'edm' (+1.00)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------

#2  Iron Requiem  by Grave Engine
    Score: 1.62 / 3.67
    Why:
      - energy is close to your target (+1.13)
      - acousticness is close to your target (+0.48)
------------------------------------------------------------

#3  Gym Hero  by Max Pulse
    Score: 1.56 / 3.67
    Why:
      - energy is close to your target (+1.09)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#4  Storm Runner  by Voltline
    Score: 1.51 / 3.67
    Why:
      - energy is close to your target (+1.06)
      - acousticness is close to your target (+0.45)
------------------------------------------------------------

#5  Sunrise City  by Neon Echo
    Score: 1.37 / 3.67
    Why:
      - energy is close to your target (+0.96)
      - acousticness is close to your target (+0.41)
------------------------------------------------------------
```

### Neutral: All 0.5

Adversarial: no category match and mid-range numerics. The top five are within 0.17 of each other, so the ranking is close to arbitrary.

```

#1  Velvet Hours  by Maya Lune
    Score: 1.59 / 3.67
    Why:
      - energy is close to your target (+1.15)
      - acousticness is close to your target (+0.44)
------------------------------------------------------------

#2  Island Sunday  by Sol Tide
    Score: 1.55 / 3.67
    Why:
      - energy is close to your target (+1.08)
      - acousticness is close to your target (+0.47)
------------------------------------------------------------

#3  Dusty Porch Light  by Hollow Creek
    Score: 1.49 / 3.67
    Why:
      - energy is close to your target (+1.15)
      - acousticness is close to your target (+0.34)
------------------------------------------------------------

#4  Midnight Coding  by LoRoom
    Score: 1.47 / 3.67
    Why:
      - energy is close to your target (+1.08)
      - acousticness is close to your target (+0.40)
------------------------------------------------------------

#5  Blue Highway Blues  by Delta Mercy
    Score: 1.42 / 3.67
    Why:
      - energy is close to your target (+1.05)
      - acousticness is close to your target (+0.37)
------------------------------------------------------------
```

---

## Experiments You Tried

### Weight shift: double energy, halve genre

**Change:** energy weight `1.17` → `2.34`, genre weight `1.0` → `0.5`. Mood (`1.0`) and acousticness (`0.5`) stayed the same. I ran this on a scratch copy of `score_song`, so `src/recommender.py` still uses the original weights. Max possible score becomes 4.34.

The #1 song stayed the same for all ten profiles. The rest of the ranking moved in the profiles below:

| Profile | Original top 3 | Shifted top 3 | What changed |
|---|---|---|---|
| High-Energy Pop | Sunrise City 3.62, Gym Hero 2.53, Rooftop Lights 2.46 | Sunrise City 4.25, Rooftop Lights 3.53, Gym Hero 3.10 | #2 and #3 swap. Gym Hero's genre match is now worth half as much, so Rooftop Lights' mood match wins. |
| Deep Intense Rock | Storm Runner 3.66, Gym Hero 2.63, Pulse Cathedral 1.60 | Storm Runner 4.32, Gym Hero 3.79, Pulse Cathedral 2.74 | The order is unchanged. The gap between #2 and #3 is about the same (1.03 before, 1.05 after). |
| Conflict: High Energy + Sad | Blue Highway Blues 2.75, Storm Runner 1.66, Gym Hero 1.61 | Blue Highway Blues 2.84, Storm Runner 2.82, Gym Hero 2.74 | The sad blues song still wins, but its lead over Storm Runner falls from 1.09 to 0.02. It is now close to a tie. |
| Split: Pop Genre + Sad Mood | Blue Highway Blues 2.42, Sunrise City 2.14, Gym Hero 1.94 | Blue Highway Blues 3.48, Velvet Hours 2.73, Dusty Porch Light 2.63 | Both pop songs fall out of the top 3. Genre is now worth only 0.5, so mid-energy songs with no category match outrank them. |
| Out of Range: energy 2.0 (measured before input clamping was added) | Pulse Cathedral 2.42, Iron Requiem 0.45 | Pulse Cathedral 1.86, Iron Requiem 0.41 | Doubling the energy weight made the out-of-range energy penalty worse (Sunrise City went to -0.01). Input clamping has since removed this problem. |

**Takeaways:**
- The system is sensitive to this change in the cases where categories and numbers disagree. The conflicting-preference profile went from an overwhelming genre/mood win to a near tie, which is closer to what the user's energy request implies.
- Profiles where one song matches everything (Chill Lofi, Deep Intense Rock) are robust: the #1 song stays the same.
- Halving genre makes genre almost irrelevant when it is the only match. In "Split: Pop Genre + Sad Mood", two pop songs dropped out of the top 5 entirely, so genre-loyal users would likely be less happy.
- Doubling energy did not fix the unvalidated-input problem; it amplified it. That problem is now fixed separately by clamping inputs to 0-1 in `score_song`.

Other experiment still to try: adding tempo or valence to the score. (Clamping and lowercasing inputs are already done in `score_song`.)

---

## Limitations and Risks

I reviewed `src/recommender.py` and `data/songs.csv` for filter bubbles and bias, and checked each suspicion with a script (3,780 generated profiles covering every catalog genre and mood across six energy targets and three acousticness targets). Findings, most serious first:

1. **Uneven service by genre.** 13 of 15 genres and 11 of 14 moods have exactly one song. A lofi fan gets three strong matches (all above 2.5), but a rock, jazz or metal fan gets one strong match and then a steep drop (rock: 3.47, then 2.42, then 1.42). The second pick for a jazz or metal fan shares neither genre nor mood with them. Users of well-represented genres get a much fuller experience.
2. **Categories are all-or-nothing.** Genre and mood are exact string matches worth up to 2.0 of 3.67 points, and related labels get no partial credit: `pop` vs `indie pop`, `sad` vs `melancholic`, `chill` vs `relaxed`. Only 17 of the 210 possible genre+mood pairs exist in the catalog, so most combinations of tastes can never score above 2.67 (one category match plus perfect numeric closeness). There is also no diversity rule, so the top 5 can repeat an artist (Neon Echo and LoRoom each appear twice).
3. **Energy and acousticness are the same signal.** In the catalog, energy and acousticness correlate at r = -0.97. Acousticness adds almost nothing beyond energy, and a user who wants both high energy and high acousticness (acoustic rock, unplugged sets) cannot be served: the energy term wins, and the acoustic request earns only +0.08 (see "Impossible: Energetic + Acoustic").
4. **The energy gap is symmetric and favors the middle of the catalog.** The gap is fair in direction, but the catalog is not: only 4 of 18 songs have energy below 0.4 and none lies between 0.58 and 0.75. With no category match, a user targeting energy 0.6 gets a best score of 1.62 and one targeting 0.0 gets 1.19, so very low-energy users (sleep, ambient) are served worst. A single target number also cannot express a range, such as someone who likes both calm and intense music.
5. **Tempo, valence and danceability are ignored.** Two songs with identical energy and acousticness but very different feel look the same. For example, a user who wants sad but danceable music cannot say so.
6. **No feedback loop yet, so no true filter bubble.** The recommender is stateless: it does not learn from what a user plays, so it cannot narrow their taste over time. If it were extended with listening history, the all-or-nothing genre bonus and the missing diversity rule (points 1 and 2) would make that feedback loop narrow quickly.


Not a problem: every song can reach a top-5 (none are unreachable), and no single song dominates the #1 spot (the most frequent #1, Island Sunday, takes 9% of profiles).

Possible fixes: lower the genre and mood weights or add partial credit through a related-label table, drop or reweight acousticness, add tempo or valence, add an artist/genre diversity penalty to the top-k. You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

**How recommenders turn data into predictions.** My recommender turns a user's taste into a score for every song, then shows the top five. Each song earns points for matching the user's genre and mood, and for being close to their energy and acousticness targets. There is no learning. It is only matching and distance. Even so, it felt like a real recommender. Sunrise City came first for a pop fan and Library Rain came first for a lofi fan. The "Why" lines made the picks feel understood. I also learned that the weights matter more than the code. Genre and mood were worth 2.0 points and energy at most 1.17, so a slow blues song beat every loud song for a user who asked for loud music. Halving the genre weight and doubling the energy weight cut that lead from 1.09 to 0.02.

**Where bias or unfairness could show up.** The biggest problem is the data. 13 of 15 genres have only one song. A lofi fan gets three good matches, but a rock, jazz or metal fan gets one and then a steep drop. Users with common tastes are served better than users with niche or mixed tastes. Exact-match labels make it worse, because "pop" gets no credit for "indie pop". The catalog was also made by hand and leans toward Western pop styles. If this system learned from listening history, these gaps would grow into a real filter bubble. A diversity rule, partial credit for related labels and a much bigger catalog would help. See the [Model Card](model_card.md) for the full evaluation and my engineering reflection.


