import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from skimage.transform import resize

def preprocess_audio(audio_data, sr=16000, target_duration=2.52, recordingMode=True):
    if recordingMode == True:
        y = audio_data[:, 0]
    else:
        y = audio_data
    vad_segments = librosa.effects.split(y, top_db=18)
    if len(vad_segments) == 0:
        return None
    word_boundaries = []
    word_count = 0
    for segment in vad_segments:
        if word_count >= 3:
            break
        if segment[1] - segment[0] > 0.16 * sr:
            word_boundaries.append(segment)
            word_count += 1
    if len(word_boundaries) == 0:
        return None
    combined_segment = np.concatenate([y[boundary[0]:boundary[1]] for boundary in word_boundaries], axis=0)
    target_samples = int(target_duration * sr)
    combined_segment = combined_segment[:target_samples]
    spectrogram = librosa.feature.melspectrogram(
        y=combined_segment, sr=sr, n_fft=512, hop_length=256, n_mels=128
    )
    log_spectrogram = librosa.power_to_db(spectrogram, ref=np.max)
    resized_spectrogram = resize(log_spectrogram, (100, 50))
    resized_spectrogram = np.expand_dims(resized_spectrogram, axis=-1)
    return resized_spectrogram

def plot_spectrogram(spectrogram):
    plt.figure(figsize=(12, 8))
    plt.imshow(spectrogram[:, :, 0], aspect='auto', origin='lower', cmap='viridis')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Izvorni spektrogram')
    plt.tight_layout()
    plt.show()
