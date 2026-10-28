import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for this user, best first, using score_song."""
        prefs = _profile_to_prefs(user)
        # sorted() is stable, so tied scores keep catalog order.
        return sorted(self.songs, key=lambda song: score_song(prefs, asdict(song))[0], reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain a song's score for this user as the scorer's reasons joined with '; '."""
        _, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return "; ".join(reasons) if reasons else "no preferences matched this song"

def _profile_to_prefs(user: UserProfile) -> Dict:
    """Convert a UserProfile into the prefs dict score_song expects.

    likes_acoustic becomes an acousticness target: 1.0 if True, 0.0 if False.
    """
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "acousticness": 1.0 if user.likes_acoustic else 0.0,
    }

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file as dicts, converting id to int and numeric features to float."""
    int_fields = ("id",)
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def _clean_label(value) -> str:
    """Normalize a genre/mood label so 'Pop ' and 'pop' compare equal."""
    return str(value).strip().lower() if value is not None else ""

def _clamp01(value) -> Optional[float]:
    """Clamp a numeric preference to 0-1; return None if it is missing or not a number."""
    try:
        return min(1.0, max(0.0, float(value)))
    except (TypeError, ValueError):
        return None

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences, returning (score, reasons).

    Preferences are forgiving: labels are case/whitespace-insensitive, numeric targets
    are clamped to 0-1, and a missing preference simply earns no points for that term.
    """
    score = 0.0
    reasons: List[str] = []

    energy_target = _clamp01(user_prefs.get("energy"))
    if energy_target is not None:
        energy_points = 1.17 * (1 - abs(energy_target - song["energy"]))
        score += energy_points
        reasons.append(f"energy is close to your target (+{energy_points:.2f})")

    mood = _clean_label(user_prefs.get("mood"))
    if mood and _clean_label(song["mood"]) == mood:
        score += 1.0
        reasons.append(f"mood matches '{song['mood']}' (+1.00)")

    genre = _clean_label(user_prefs.get("genre"))
    if genre and _clean_label(song["genre"]) == genre:
        score += 1.0
        reasons.append(f"genre matches '{song['genre']}' (+1.00)")

    acoustic_target = _clamp01(user_prefs.get("acousticness"))
    if acoustic_target is not None:
        acoustic_points = 0.5 * (1 - abs(acoustic_target - song["acousticness"]))
        score += acoustic_points
        reasons.append(f"acousticness is close to your target (+{acoustic_points:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song and return the top k as (song, score, explanation), best first."""
    scored = (
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    )
    # sorted() is stable, so tied scores keep CSV order.
    return sorted(scored, key=lambda rec: rec[1], reverse=True)[:k]
