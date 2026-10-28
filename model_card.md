# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeScorecard 1.0**

---

## 2. Goal and Intended Use  

**Goal.** The model suggests five songs from a small catalog that fit a user's taste. It guesses which songs a user would like best.

**Intended use.**
- Classroom exploration of how a simple recommender works.
- Learning how scoring rules turn taste into a ranked list.
- Showing the reasons behind each pick.

**What it assumes about the user.** The user can name one favorite genre and one favorite mood. The user can also give a target for energy and acousticness, each from 0 to 1.

**Not intended for.**
- Real music apps or real users.
- Judging an artist or song as good or bad.
- Making any decision that affects people, like pay or promotion.
- Users with niche or mixed tastes. It handles them poorly (see Section 6).

---

## 3. How the Model Works  

Think of the recommender as a judge holding a scorecard. You tell it what you like, it gives every song in the catalog a score out of about 3.67, and it shows you the five highest.

**What you tell it.** Four things: a favorite genre, a favorite mood, how energetic you want the music to feel (from calm to intense), and how acoustic you want it (from electronic to acoustic).

**What it looks at in each song.** The song's genre, its mood, its energy, and its acousticness. Each song also has a tempo, a danceability and a "happiness" (valence) rating, but the scorecard ignores those. Tempo and danceability mostly repeat what energy already says, and happiness is left out to keep the first version simple.

**How a song earns points.** The scorecard has four lines:

- **Energy, up to 1.17 points.** The closer the song's energy is to what you asked for, the more points it gets. A song exactly on target earns the full amount, and one at the opposite extreme earns almost nothing.
- **Mood, 1 point.** All or nothing: the song's mood either matches yours or it doesn't.
- **Genre, 1 point.** Also all or nothing. "Indie pop" does not count as a match for "pop".
- **Acousticness, up to 0.5 points.** Closer to your target earns more, like energy.

The points are added up to give the song's final score.

**Why "closeness" and not "higher is better".** Someone who wants calm music shouldn't be pushed toward loud songs just because they have more energy. Rewarding closeness to the target means the model works for people who want quiet music as well as people who want loud music.

**Picking the winners.** The judge scores every song, sorts them from highest to lowest, and shows the top five. If two songs tie, the one that appears first in the catalog goes first. Each recommendation also comes with the reasons behind its score, such as "mood matches 'happy' (+1.00)", so you can see why it was picked.

**A worked example.** For someone who wants pop, happy, high-energy, low-acoustic music, "Sunrise City" (pop, happy, energetic, not very acoustic) scores about 3.64. It earns nearly full points on all four lines. "Gym Hero" (pop, but an intense mood) scores about 2.44. It gets the genre point but misses the mood point.

**What this means in practice.** Genre and mood together are worth 2 of the roughly 3.67 points, so the labels count for more than how a song actually sounds. A song with the right labels but the wrong feel can beat a song that sounds right but has different labels.

**Changes from the starter.** The starter code only had empty placeholders for loading songs, scoring them and ranking them. I wrote all three: reading the catalog from the spreadsheet file, the four-line scorecard above, and the sort-and-pick-the-top-five step. I also made the output show the reasons next to each score.

---

## 4. Data  

The catalog is `data/songs.csv`. It has 18 songs.

**Features.** Each song has a title, artist, genre, mood, energy, tempo, valence, danceability and acousticness. The scorer only uses genre, mood, energy and acousticness.

**Coverage.** There are 15 genres and 14 moods. Lofi has 3 songs. Pop has 2. The other 13 genres have only 1 song each.

**What I changed.** The starter had fewer songs. I added more songs and more genres.

**What is missing.**
- The catalog is tiny.
- There are no lyrics, languages, years or artist popularity.
- Most genres are Western pop styles. Many world genres are absent.
- Energy and acousticness move together (r = -0.97), so they carry nearly the same signal.
- The values were set by hand, not measured from real audio or listeners.

---

## 5. Strengths  

- It works well for users whose taste matches common labels, like pop, lofi and rock.
- Baseline profiles got the pick I expected. Scores were 3.58 to 3.66 out of 3.67.
- Opposite users get opposite lists. Chill Lofi and High-Energy Pop share no songs.
- Every pick comes with reasons, so it is easy to see why a song ranked high.
- Messy input like "Pop" or "HAPPY" no longer breaks it.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

The biggest weakness I found is that the genre and mood bonuses (up to 2.0 of the 3.67 possible points) can override what the user says about energy, which I saw in the "High Energy + Sad" test profile. That profile asked for energy 0.9 but blues and sad, and the system's top pick was Blue Highway Blues, a slow song with energy 0.40, which scored 2.75 against 1.66 for the best high-energy song. The problem is made worse by the catalog: 13 of 15 genres have only one song, so a rock, jazz or metal fan gets one strong match and then a steep drop to songs that share neither their genre nor their mood, while a lofi fan gets three good matches. Doubling the energy weight and halving the genre weight shrank that blues lead from 1.09 to 0.02, which shows the category weights, not the user's numbers, were deciding the result. In practice this means users with unusual combinations of tastes, or tastes in a small genre, are served worse than users whose tastes match the most common labels.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

**Profiles tested.** I ran ten profiles through `src/main.py` and recorded the top 5 for each (full output is in the README under "Profile Evaluation Output"):
- Three baseline profiles: High-Energy Pop, Chill Lofi and Deep Intense Rock.
- Seven adversarial profiles meant to trick the scorer: High Energy + Sad (conflicting preferences), Pop Genre + Sad Mood (genre and mood pointing at different songs), Energetic + Acoustic (a combination no song satisfies), Unknown Genre/Mood, Case Mismatch ("Pop"/"HAPPY"), Out of Range (energy 2.0) and Neutral (everything 0.5).

**What I looked for.** For the baselines, whether the #1 song matched my intuition and whether the "Why" lines explained it. For the adversarial profiles, whether the scorer would be fooled, crash, or return results that did not match what the user asked for.

**What worked.** All three baselines gave the expected #1 (Sunrise City, Library Rain, Storm Runner), with scores of 3.58 to 3.66 out of 3.67. Every song also reached a top 5 across 3,780 generated profiles, and no single song dominated #1 (the most common, Island Sunday, took 9%).

**What surprised me.**
- A user asking for energy 0.9 who also picked blues and sad got Blue Highway Blues (energy 0.40) at 2.75, against 1.66 for the best high-energy song, because the genre and mood bonuses (2.0 together) outweigh the energy term (at most 1.17).
- Energy and acousticness correlate at r = -0.97 in the catalog, so the acousticness term adds little beyond energy, and the "Energetic + Acoustic" profile earned only +0.08 for its acoustic request.
- 13 of 15 genres have a single song, so rock, jazz and metal fans get one strong match and then a steep drop, while a lofi fan gets three.

**Comparisons and fixes.**
- Weight shift: doubling the energy weight and halving the genre weight left every #1 unchanged but cut the blues lead in the conflicting profile from 1.09 to 0.02, and pushed both pop songs out of the top 3 in the split profile.
- Input robustness: the Case Mismatch profile lost all its category points (top score 1.62 instead of 3.62), the Out of Range profile produced a negative energy term (-0.06), and an empty or incomplete profile raised a `KeyError`. I fixed these in `score_song` by lowercasing and trimming labels, clamping targets to 0-1, and skipping missing preferences. After the fix, the Case Mismatch profile matches High-Energy Pop exactly (3.62), and Out of Range scores 3.59.

**Profile-to-profile comparisons.** Each pair below changes one idea, so the difference in output shows what that preference actually tests. Scores are out of 3.67, and the outputs are after the input-robustness fix.

1. **High-Energy Pop vs Chill Lofi.** The two top 5 lists share no songs. Pop gets Sunrise City (energy 0.82, acousticness 0.18) and lofi gets Library Rain (energy 0.35, acousticness 0.86), at nearly equal top scores (3.62 vs 3.58). This makes sense: the profiles sit at opposite ends of both numeric scales, and both users are served equally well. It is also the cleanest evidence that the energy and acousticness terms steer results in the right direction.
2. **High-Energy Pop vs Deep Intense Rock.** Both want loud songs, so they share Gym Hero and Storm Runner, but for different reasons. Gym Hero is #2 for the pop user because of its genre match (pop) and #2 for the rock user because of its mood match (intense). The rock list also adds Pulse Cathedral and Iron Requiem (energy 0.95 and 0.97), which are not pop. This is valid, because the pop list is held up by the genre/mood bonuses and the rock list only by the numbers once the one rock song is used up.
3. **Chill Lofi vs Deep Intense Rock.** Again no overlap, and the top 5 lists mirror each other: low energy and high acousticness versus high energy and low acousticness. This makes sense and confirms the scorer has no hidden preference for loud or quiet music.
4. **Deep Intense Rock vs Energetic + Acoustic.** The only change is acousticness (0.10 to 0.95). Storm Runner stays #1 but drops from 3.66 to 3.20, and Rooftop Lights (acousticness 0.35) enters the top 5. The result is only partly valid: the score moved in the right direction, but the user still got loud, non-acoustic songs, because genre and mood still dominate and no song is both energetic and acoustic (energy and acousticness correlate at r = -0.97).
5. **High-Energy Pop vs Case Mismatch ("Pop"/"HAPPY").** After normalising labels these two return identical results (3.62, 2.53, 2.46). Before the fix, the mismatch profile's top score was 1.62 because it earned no category points. This is the output I want, since "Pop" and "pop" mean the same thing to a user.
6. **High-Energy Pop vs Unknown Genre/Mood.** Without a genre or mood match, the top score falls from 3.62 to 1.62 and the picks become mid-energy songs (Island Sunday, Velvet Hours). That makes sense, since only the numeric terms are left and the profile asks for energy 0.60. The comparison is not perfectly controlled, because its energy and acousticness targets also differ from the pop profile, and the system gives no warning that "k-pop" matched nothing.
7. **Deep Intense Rock vs High Energy + Sad.** Both want high energy, so the other four slots in each list are filled by nearly the same loud songs (Storm Runner, Gym Hero, Pulse Cathedral, Iron Requiem). The main difference is that Blue Highway Blues takes #1 in the sad profile at 2.75, since it earns 2.0 points from genre and mood even though its energy is 0.40. The energy half of this makes sense. The #1 pick does not, because the user asked for energy 0.9.
8. **High Energy + Sad vs Pop Genre + Sad Mood.** Blue Highway Blues wins both. In the first it matches genre and mood; in the second it matches only mood and beats Sunrise City (genre only) 2.42 to 2.14, because its energy (0.40) and acousticness (0.76) are closer to the 0.5 targets. This is only half valid: the winner is decided by the numeric terms, so a genre match and a mood match are treated as equal, which makes the outcome somewhat arbitrary.
9. **Unknown Genre/Mood vs Neutral (all 0.5).** Neither profile matches a category, so only energy and acousticness count. Shifting the target from energy 0.50 to 0.60 swaps #1 from Velvet Hours (energy 0.52) to Island Sunday (energy 0.58), and both lists are filled with the same mid-energy songs (Velvet Hours, Island Sunday, Dusty Porch Light). This is valid: a small move in the target slightly reorders the same neighbourhood. It also shows the Neutral ranking is nearly a coin flip, since its top five are within 0.17 of each other.
10. **Deep Intense Rock vs Out of Range (energy 2.0).** After clamping, the out-of-range profile behaves like energy 1.0. It returns Pulse Cathedral first (3.59, the only edm/euphoric song), then the highest-energy songs (Iron Requiem 1.62, Gym Hero 1.56), while the rock profile puts Storm Runner first. This makes sense, since both want the loudest songs and differ only in which genre and mood they name. Before the fix this profile showed a negative energy term and a top score of 2.42.

Across all ten, the output moves the way the preferences say it should in the numeric terms (pairs 1, 3, 9 and 10) and in the genre and mood matches (pair 2). The invalid results come from places where those terms disagree with each other (pairs 4, 7 and 8) or where the input is not recognised (pairs 5 and 6).

**Limits of this evaluation.** The catalog has only 18 songs and I tested by reading results, not with a held-out set of real listeners, so these checks show how the scoring behaves and not whether real users would be happy. The pytest suite (8 tests, all passing) checks `score_song` and `recommend_songs` on small hand-made cases, but it does not replace testing with real listeners.

---

## 8. Future Work  

1. **Rebalance the weights.** Give energy more weight and genre less. Then a genre or mood label can't override what the user asked for.
2. **Add more songs.** Get several songs per genre. Then small genres stop dropping off a cliff after one match.
3. **Support mixed tastes.** Let users pick several genres or moods. Add valence and tempo too.
4. **Mix up the top five.** Avoid five near-identical songs in one list.
5. **Warn on unknown input.** Tell the user when a genre like "k-pop" matches nothing.

---

## 9. Personal Reflection  

**Biggest learning moment.** Weights decide everything. The scorer looked fine on normal profiles. Then I ran "High Energy + Sad". A slow blues song (energy 0.40) beat every loud song, even though the user asked for energy 0.9. Genre and mood were worth 2.0 points. Energy was worth at most 1.17. I had picked those numbers early and never questioned them. Halving the genre weight and doubling the energy weight fixed the gap. So the lesson is simple. Test the weird cases, not just the happy path.

**How AI helped.** I used an AI assistant to:
- Draft the scoring and ranking code.
- Generate the adversarial profiles.
- Run the profile comparisons.
- Write up the results.

It was fast and it gave me a lot to look at. That made it easy to see patterns, like the 3,780 generated profiles.

**When I had to double-check it.**
- Numbers in the write-up. Scores, ranks and correlations (like r = -0.97) need to match the real output. I re-ran them.
- Tests. The starter tests did not cover `score_song`, so I added tests for it and for `recommend_songs`. A passing story is not a passing test.
- Bugs it only found after I probed. "Pop" and "pop" scored differently. Energy 2.0 gave a negative score. An empty profile crashed. The first draft of the code did not handle any of these.
- Explanations. The AI can sound sure about why a result happened. I checked by changing one weight and watching the output.

**What surprised me.** A scorecard with four lines still felt like a real recommender. Sunrise City came up first for a pop fan. Library Rain came up first for a lofi fan. The "Why" lines made it feel even smarter. But there is no learning in it. It is only distance and matching labels. The feeling of being understood comes from the explanation and from a good first match. It also hides how thin the catalog is. Most genres have one song, so the "recommendation" is often just the only choice.

**What I would try next.**
- Rebalance the weights and compare results again.
- Grow the catalog to several songs per genre.
- Let users pick more than one genre or mood.
- Use valence and tempo.
- Ask a few real people to rate the top five. Then I would learn if the scores match what people like, not just what I expect.
