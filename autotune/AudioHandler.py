from autotune import *


class AudioHandler:
    NOTE_NAMES = ["Co", "C#o/Dbo", "Do", "D#o/Ebo", "Eo", "Fo", "F#o/Gbo",
                  "Go", "G#o/Abo", "Ao", "A#o/Bbo", "Bo"]

    SCALES = {}
    with open("autotune/ScalePresets.txt", "r") as f:
        scales_raw = f.read()

    for scale in scales_raw.split("\n"):
        if scale:
            colon_index = scale.index(":")
            scale_name = scale[:colon_index]
            scale_notes = scale[colon_index + 2:].split(",")
            SCALES[scale_name] = scale_notes

    @staticmethod
    def play_audio(data, sample_rate):
        sd.play(data, sample_rate)

    @staticmethod
    def calc_frequencies(normalized_tone, sample_rate, step_size, sample_size):
        yf_list = []
        for i in range(0, len(normalized_tone), step_size):
            sub_sample = normalized_tone[i:i + sample_size]
            if len(sub_sample) == sample_size:
                yf = np.real(fft(sub_sample))
                yf_list.append(yf)
        xf = fftfreq(len(yf_list[0]), 1 / sample_rate)

        return xf[xf > 0], np.array(yf_list, dtype=np.float64)[:, xf > 0]

    @staticmethod
    def calc_dom_frequencies(xf, yf_array, max_freq=3000, k=4, n=5):
        """
        Selects top k frequencies from 'local average'.
        Local average gets calculated using the n following samples.
        Then figures out dominant frequency.
        """
        yf_averages = np.array([np.mean(np.abs(yf_array[i:i + n]), axis=0) for i in range(len(yf_array))])
        yf_sorted = np.sort(np.abs(yf_averages), axis=1)
        idx = [[np.where(np.abs(yf_averages[i]) == yf_sorted[i][-j]) for j in range(1, k + 1)] for i in
               range(len(yf_sorted))]
        dominant_freqs = xf[np.array(idx)].reshape(-1, k)

        final_freqs = []
        prev_freq = None
        for i, freqs in enumerate(dominant_freqs):
            if prev_freq is None:
                freq = np.min(freqs)
            else:
                diff = np.abs(freqs - prev_freq)
                freq = freqs[np.where(diff == np.min(diff))][0]

            if np.min(freqs) - freq / 2 < 10:
                freq = np.min(freqs)

            if freq > max_freq:
                freq = prev_freq

            final_freqs.append(freq)
            prev_freq = freq

        final_freqs[:5] = [final_freqs[5]] * 5

        return np.array(final_freqs).reshape(-1)

    @staticmethod
    def revert_sequence(xf, yf_array, sample_rate, n, dominant_freqs=None, target_freqs=None):
        time_array = np.zeros(shape=(n // 100, yf_array.shape[1]))
        for i, frequency in enumerate(xf):
            wavelength = sample_rate / frequency
            max_value = n / wavelength * 2 * math.pi
            time_array[:, i] = np.linspace(0, max_value, time_array.shape[0])
        time_stretched = cv2.resize(time_array, dsize=(time_array.shape[1], n))

        if target_freqs is not None:
            freq_multipliers = (target_freqs / np.array(dominant_freqs)).reshape(-1, 1)
            freq_multipliers_stretched = cv2.resize(freq_multipliers, dsize=(time_stretched.shape[1], n))
            time_stretched *= freq_multipliers_stretched

        sine_array = np.sin(time_stretched)
        yf_stretched = cv2.resize(yf_array, dsize=(yf_array.shape[1], n))
        multiplied = yf_stretched * sine_array
        new_data = np.sum(multiplied, axis=1)

        return ((new_data - new_data.min()) / (new_data.max() - new_data.min())) * 2 - 1

    @staticmethod
    def calculate_note_name(freq, return_closest_note_freq=False, scale=None):
        up_from_c0 = math.log2(freq / 16.35) * 12
        semitones_up_, cents_up = divmod(up_from_c0, 1)
        semitones_up_ += round(cents_up) * return_closest_note_freq
        octaves_up, semitones_up = divmod(semitones_up_, 12)

        if return_closest_note_freq:
            scale_indices = np.arange(0, 12)[list(scale.values())]

            diff1 = np.abs(scale_indices - semitones_up)
            diff2 = np.abs(scale_indices - semitones_up + 12)
            diff = np.min(np.array([diff1, diff2]), axis=0)
            min_ = np.min(diff)
            index = np.where(diff == min_)[0][0]
            if min_ in diff2:
                octaves_up += 1
            note = AudioHandler.NOTE_NAMES[scale_indices[index]].replace("o", str(int(octaves_up)))
            semitones_up_ = scale_indices[index] + octaves_up * 12

            closest_note_freq = 16.35 * 2 ** (semitones_up_ / 12)
            return f"{note}", closest_note_freq

        cents_up = int(cents_up * 100)
        note = AudioHandler.NOTE_NAMES[int(semitones_up)].replace("o", str(int(octaves_up)))

        return f"{note} {cents_up}\xa2"

    @staticmethod
    def closest_note_freq(freq, scale):
        return AudioHandler.calculate_note_name(freq, return_closest_note_freq=True, scale=scale)[1]
