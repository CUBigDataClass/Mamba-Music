# Mamba Magenta

These files and folders contain the code for our ML models.

These models include:

- MelodyRNN - Generates simple melodies.
- PerformanceRNN - Akin to a reasonably good piano player messing around on the keys.
- ImprovRNN - Generates melodies under an underlying chord progression.
- Pianoroll RNN Nade - Interesting model.
- Polyphony RNN - Generates Bach-like music.
- Music VAE - Generates multi group melodies under chord progressions.
- Music Transformer - The **best** model of them al.

We use a cron-job to automate the process of music generation. Check out
`cron_generation.sh` for a sample script that can be used to generate music.
It goes through all 7 models and generates music in random genres.
