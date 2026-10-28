"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from src.recommender import load_songs, recommend_songs  # python -m src.main
except ModuleNotFoundError:
    from recommender import load_songs, recommend_songs  # python src/main.py


# Distinct taste profiles. Keys line up with the scored Song features
# (genre, mood, energy, acousticness).
PROFILES = {
    # Upbeat listener: happy, poppy, high-energy, mostly produced/electronic.
    "High-Energy Pop": {
        "genre": "pop",         # exact match against Song.genre
        "mood": "happy",        # exact match against Song.mood
        "energy": 0.85,         # closeness to Song.energy (0-1, high = energetic)
        "acousticness": 0.15,   # closeness to Song.acousticness (0-1, low = produced)
    },
    # Study/relax listener: calm, low-energy, fairly acoustic lofi.
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.30,
        "acousticness": 0.80,
    },
    # Heavy listener: loud, driving, intense rock with little acoustic sound.
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "acousticness": 0.10,
    },
}


# Edge-case profiles built to probe the scorer (see the notes on each).
ADVERSARIAL_PROFILES = {
    # Energy says "loud", mood/genre say "slow blues". Do the +2.0 category matches
    # overpower the energy term?
    "Conflict: High Energy + Sad": {
        "genre": "blues", "mood": "sad", "energy": 0.90, "acousticness": 0.10,
    },
    # Genre and mood point at different songs; which one wins the split?
    "Split: Pop Genre + Sad Mood": {
        "genre": "pop", "mood": "sad", "energy": 0.50, "acousticness": 0.50,
    },
    # Wants high energy AND very acoustic; no song in the catalog is both.
    "Impossible: Energetic + Acoustic": {
        "genre": "rock", "mood": "intense", "energy": 0.95, "acousticness": 0.95,
    },
    # Labels that exist nowhere in the data: only the numeric terms can score.
    "Unknown Genre/Mood": {
        "genre": "k-pop", "mood": "mystical", "energy": 0.60, "acousticness": 0.40,
    },
    # Same intent as High-Energy Pop, but capitalised: exact-match check should fail.
    "Case Mismatch: 'Pop'/'HAPPY'": {
        "genre": "Pop", "mood": "HAPPY", "energy": 0.85, "acousticness": 0.15,
    },
    # Energy outside the documented 0-1 range: energy points can go negative.
    "Out of Range: energy 2.0": {
        "genre": "edm", "mood": "euphoric", "energy": 2.0, "acousticness": 0.0,
    },
    # Dead-center numerics with no category match: near-ties, order by CSV position.
    "Neutral: All 0.5": {
        "genre": "", "mood": "", "energy": 0.50, "acousticness": 0.50,
    },
}


def print_recommendations(name: str, user_prefs: dict, songs: list, width: int = 60) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print()
    print("=" * width)
    print(f"{('TOP RECOMMENDATIONS: ' + name):^{width}}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  by {song['artist']}")
        print(f"    Score: {score:.2f} / 3.67")
        print("    Why:")
        # explanation is the scorer's reasons joined with "; "
        for reason in explanation.split("; "):
            print(f"      - {reason}")
        print("-" * width)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, user_prefs in {**PROFILES, **ADVERSARIAL_PROFILES}.items():
        print_recommendations(name, user_prefs, songs)


if __name__ == "__main__":
    main()
