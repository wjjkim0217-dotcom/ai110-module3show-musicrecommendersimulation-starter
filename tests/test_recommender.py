from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_recommend_ranks_by_score_not_catalog_order():
    user = UserProfile(
        favorite_genre="lofi",
        favorite_mood="chill",
        target_energy=0.4,
        likes_acoustic=True,
    )
    rec = make_small_recommender()  # pop song comes first in the catalog
    results = rec.recommend(user, k=2)

    assert results[0].genre == "lofi"
    assert results[1].genre == "pop"


def test_explain_recommendation_reflects_scoring():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()

    match = rec.explain_recommendation(user, rec.songs[0])
    assert "genre matches 'pop'" in match
    assert "mood matches 'happy'" in match

    mismatch = rec.explain_recommendation(user, rec.songs[1])
    assert "genre matches" not in mismatch
    assert "mood matches" not in mismatch


# --- Tests for the functional scoring and ranking API ---

from src.recommender import score_song, recommend_songs

POP_SONG = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
LOFI_SONG = {"genre": "lofi", "mood": "chill", "energy": 0.4, "acousticness": 0.9}
POP_PREFS = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}


def test_score_song_perfect_match_is_max_score():
    score, reasons = score_song(POP_PREFS, POP_SONG)
    assert abs(score - 3.67) < 1e-9
    assert len(reasons) == 4


def test_score_song_rewards_closer_energy():
    close = {**POP_SONG, "energy": 0.8}
    far = {**POP_SONG, "energy": 0.2}
    assert score_song(POP_PREFS, close)[0] > score_song(POP_PREFS, far)[0]


def test_score_song_normalizes_case_and_clamps_inputs():
    messy = {"genre": " POP ", "mood": "Happy", "energy": 0.8, "acousticness": 0.2}
    assert score_song(messy, POP_SONG)[0] == score_song(POP_PREFS, POP_SONG)[0]
    out_of_range = {**POP_PREFS, "energy": 2.0}
    assert score_song(out_of_range, POP_SONG)[0] >= 0


def test_score_song_handles_empty_profile():
    score, reasons = score_song({}, POP_SONG)
    assert score == 0.0
    assert reasons == []


def test_recommend_songs_sorted_best_first_and_limited_to_k():
    results = recommend_songs(POP_PREFS, [LOFI_SONG, POP_SONG], k=1)
    assert len(results) == 1
    song, score, explanation = results[0]
    assert song is POP_SONG
    assert "genre matches" in explanation


def test_recommend_songs_differs_by_profile():
    lofi_prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4, "acousticness": 0.9}
    songs = [POP_SONG, LOFI_SONG]
    assert recommend_songs(POP_PREFS, songs)[0][0] is POP_SONG
    assert recommend_songs(lofi_prefs, songs)[0][0] is LOFI_SONG
