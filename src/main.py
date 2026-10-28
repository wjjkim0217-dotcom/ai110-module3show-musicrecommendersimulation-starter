"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Default taste profile: an upbeat listener who wants happy, poppy, high-energy,
    # mostly electronic music.
    # Keys line up with the scored Song features (genre, mood, energy, acousticness).
    user_prefs = {
        "genre": "pop",         # exact match against Song.genre
        "mood": "happy",        # exact match against Song.mood
        "energy": 0.80,         # closeness to Song.energy (0-1, high = energetic)
        "acousticness": 0.20,   # closeness to Song.acousticness (0-1, low = produced/electronic)
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    width = 60
    print()
    print("=" * width)
    print(f"{'TOP RECOMMENDATIONS':^{width}}")
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{rank}  {song['title']}  by {song['artist']}")
        print(f"    Score: {score:.2f} / 3.67")
        print("    Why:")
        # explanation is the scorer's reasons joined with "; "
        for reason in explanation.split("; "):
            print(f"      - {reason}")
        print("-" * width)


if __name__ == "__main__":
    main()
