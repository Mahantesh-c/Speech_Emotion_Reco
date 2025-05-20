# Sample Datasets for Speech Emotion Recognition

This directory contains sample audio files for different speech emotion datasets. These samples can be used to test the emotion recognition system or as reference points.

## Available Datasets

### RAVDESS (Ryerson Audio-Visual Database of Emotional Speech and Song)
- **Directory**: `ravdess/`
- **Source**: [RAVDESS on Zenodo](https://zenodo.org/record/1188976)
- **License**: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License
- **File Naming Format**: modality-vocal_channel-emotion-intensity-statement-repetition-actor.wav
  - Emotion codes: 01=neutral, 02=calm, 03=happy, 04=sad, 05=angry, 06=fearful, 07=disgust, 08=surprised

### TESS (Toronto Emotional Speech Set)
- **Directory**: `tess/`
- **Source**: [TESS at University of Toronto](https://tspace.library.utoronto.ca/handle/1807/24487)
- **License**: Free for research use
- **File Naming Format**: OAF_word_emotion.wav or YAF_word_emotion.wav
  - OAF = Older Adult Female, YAF = Young Adult Female

### SAVEE (Surrey Audio-Visual Expressed Emotion)
- **Directory**: `savee/`
- **Source**: [SAVEE at University of Surrey](http://kahlan.eps.surrey.ac.uk/savee/)
- **License**: Free for research use
- **File Naming Format**: DC_a01.wav (a=anger, d=disgust, f=fear, h=happiness, n=neutral, sa=sadness, su=surprise)

### EMOVO (Italian Emotional Speech Database)
- **Directory**: `emovo/`
- **Source**: [EMOVO at Fondazione Ugo Bordoni](http://voice.fub.it/activities/corpora/emovo/index.html)
- **License**: Free for research use
- **File Naming Format**: actor-emotion-sentence.wav
  - Emotion codes: neu=neutral, gio=happy, tri=sad, rab=angry, pau=fear, dis=disgust, sor=surprised

## Adding Sample Files

To add sample files to these datasets:

1. Download samples from the official sources above (respecting their licenses)
2. Place the .wav files in the appropriate directory
3. Ensure the file naming follows the format expected by each dataset
4. The system will automatically detect and categorize the samples

Only WAV format files are supported.