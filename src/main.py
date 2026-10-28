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

    # Taste profile: a late-night study listener who wants calm, mostly acoustic music.
    # Keys line up with the scored Song features (genre, mood, energy, acousticness).
    user_prefs = {
        "genre": "lofi",        # exact match against Song.genre
        "mood": "chill",        # exact match against Song.mood
        "energy": 0.40,         # closeness to Song.energy (0-1, low = calm)
        "acousticness": 0.80,   # closeness to Song.acousticness (0-1, high = acoustic)
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
