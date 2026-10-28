# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

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

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
