from autotune import *


class Autotune:
    def __init__(self, sample_file="test.wav"):
        self.SAMPLE_RATE = None
        self.N = None
        self.DURATION = None
        self.record_duration = 3
        self.STEP_SIZE = 1500  # Note: Some STEP_SIZE values may result in incorrect frequencies
        self.SAMPLE_SIZE = 1500
        self.FREQUENCY_RANGE = [0, 3000]
        self.frequency_diff = self.FREQUENCY_RANGE[1] - self.FREQUENCY_RANGE[0]
        self.normalized_tone = None
        self.xf = None
        self.yf_array = None
        self.dominant_freqs_ = None
        self.dominant_freqs_x = None
        self.dominant_freqs_y = None
        self.dom_freqs_line = None
        self.target_freqs_ = None
        self.target_freqs_x = None
        self.target_freqs_y = None
        self.target_freqs_line = None
        self.scale = {note_name.replace("o", ""): True for note_name in AudioHandler.NOTE_NAMES}

        self.fig = plt.gcf()
        self.ax_spectrogram = plt.axes([0.07, 0.07, 0.81, 0.9])
        self.canvas = self.ax_spectrogram.figure.canvas
        self.fig.set_size_inches(11, 6)
        self.fig.canvas.set_window_title('AutoTune')

        self.ax_play = plt.axes([0.87, 0.9, 0.06, 0.06])
        self.icon_play = plt.imread('autotune/play.png')
        self.icon_play2 = plt.imread('autotune/play2.png')
        b_play = Button(self.ax_play, '', image=self.icon_play, color="white", hovercolor="lightgrey")
        b_play.on_clicked(self.play_spectrogram)
        for spine in self.ax_play.spines.values():
            spine.set_visible(False)

        plt.rcParams.update({'font.size': 9})

        ax_load = plt.axes([0.89, 0.82, 0.094, 0.05])
        b_load = Button(ax_load, 'Load Sample', color="lavender", hovercolor="whitesmoke")
        b_load.on_clicked(self.load_spectrogram)
        for spine in ax_load.spines.values():
            spine.set_color("grey")

        ax_record = plt.axes([0.89, 0.755, 0.094, 0.05])
        b_record = Button(ax_record, 'Record Sample', color="lavender", hovercolor="snow")
        b_record.on_clicked(self.record_spectrogram)
        for spine in ax_record.spines.values():
            spine.set_color("grey")

        ax_duration = plt.axes([0.95, 0.70, 0.03, 0.04])
        text_duration = TextBox(ax_duration, 'Duration: ', initial="3")
        text_duration.on_text_change(self.update_duration)
        for spine in ax_duration.spines.values():
            spine.set_color("grey")

        ax_calc_freqs = plt.axes([0.89, 0.55, 0.09, 0.05])
        b_calc_freqs = Button(ax_calc_freqs, 'Calc. Freqs', color="xkcd:off white", hovercolor="snow")
        b_calc_freqs.on_clicked(self.calc_dominant_freqs)
        for spine in ax_calc_freqs.spines.values():
            spine.set_color("grey")

        ax_copy_freqs = plt.axes([0.89, 0.48, 0.09, 0.05])
        b_copy_freqs = Button(ax_copy_freqs, 'Copy Freqs', color="xkcd:off white", hovercolor="snow")
        b_copy_freqs.on_clicked(self.copy_dominant_freqs)
        for spine in ax_copy_freqs.spines.values():
            spine.set_color("grey")

        ax_reset_freqs = plt.axes([0.89, 0.41, 0.09, 0.05])
        b_reset_freqs = Button(ax_reset_freqs, 'Reset Freqs', color="xkcd:off white", hovercolor="snow")
        b_reset_freqs.on_clicked(self.reset_freqs)
        for spine in ax_reset_freqs.spines.values():
            spine.set_color("grey")

        ax_snap_freqs = plt.axes([0.89, 0.34, 0.09, 0.05])
        b_snap_freqs = Button(ax_snap_freqs, 'Snap Freqs', color="xkcd:off white", hovercolor="snow")
        b_snap_freqs.on_clicked(self.snap_freqs)
        for spine in ax_snap_freqs.spines.values():
            spine.set_color("grey")

        ax_scale = plt.axes([0.89, 0.27, 0.09, 0.05])
        b_scale = Button(ax_scale, 'Select Scale', color="xkcd:off white", hovercolor="snow")
        b_scale.on_clicked(lambda x: ExtraWindow(self))
        for spine in ax_scale.spines.values():
            spine.set_color("grey")

        self.fig.text(0.888, 0.19, "Indication Shown:", fontweight="demibold", fontsize=8)
        ax_indication = plt.axes([0.838, 0.07, 0.16, 0.12])
        ax_indication.set_aspect(1)
        ax_indication.patch.set_alpha(0)
        for spine in ax_indication.spines.values():
            spine.set_visible(False)
        b_indication = RadioButtons(ax_indication, ('None', 'Freq indication', 'Note indication'), activecolor="0.3")
        b_indication.on_clicked(self.update_indication_status)
        b_indication.set_active(1)
        self.indication_status = "Freq indication"

        plt.rcParams.update({'font.size': 10})

        ax_select = plt.axes([0.7, 0.84, 0.16, 0.12])
        ax_select.set_aspect(1)
        ax_select.patch.set_alpha(0)
        for spine in ax_select.spines.values():
            spine.set_visible(False)
        b_select = RadioButtons(ax_select, ('None', 'Dominant Freqs', 'Target Freqs'), activecolor="white")
        b_select.on_clicked(self.update_editing_status)
        for child in ax_select.get_children():
            if isinstance(child, mpl.text.Text) or isinstance(child, mpl.patches.Circle):
                child.set_color("0.8")
        b_select.set_active(0)
        self.editing_status = "None"

        self.status_text = self.fig.text(0.02, 0.01, "", fontsize=10)

        self.load_file(filename=sample_file)
        plt.show()

    def load_file(self, filename=None, data=None):
        if data is None:
            self.SAMPLE_RATE, data = wavfile.read(filename)
            self.N = len(data)
            if len(data.shape) == 2:
                data = np.mean(data, axis=1)
            data = data.astype(np.int64)
        self.normalized_tone = ((data - data.min()) / (data.max() - data.min())) * 2 - 1
        self.DURATION = self.N / self.SAMPLE_RATE

        self.xf, self.yf_array = AudioHandler.calc_frequencies(self.normalized_tone, self.SAMPLE_RATE,
                                                               self.STEP_SIZE, self.SAMPLE_SIZE)
        idx = (self.xf > self.FREQUENCY_RANGE[0]) * (self.xf < self.FREQUENCY_RANGE[1])
        spectrogram = cv2.transpose(cv2.flip(abs(self.yf_array[:, idx]), 1))
        self.ax_spectrogram.cla()
        self.ax_spectrogram.imshow(spectrogram, cmap='viridis', extent=[0, 1 * self.N, 0, self.frequency_diff],
                                   aspect='auto')

        self.reset_freqs(None, update=False)

        self.dom_freqs_line = AdjustableLine(self, "Dominant Freqs", self.dominant_freqs_x, self.dominant_freqs_y,
                                             self.fig, self.ax_spectrogram, "r")
        self.target_freqs_line = AdjustableLine(self, "Target Freqs", self.target_freqs_x, self.target_freqs_y,
                                                self.fig, self.ax_spectrogram, "lightskyblue")

    def record(self, sample_rate, duration):
        N = duration * sample_rate
        data = sd.rec(int(N), samplerate=sample_rate, channels=1)
        sd.wait()
        normalized_tone = data.reshape(-1)

        return normalized_tone

    def simplify_freq_list(self, x_data_, y_data_):
        prev = None
        x_data = []
        y_data = []
        for i, (x_value, y_value) in enumerate(zip(x_data_, y_data_)):
            if y_value != prev or (i < len(y_data_) - 1 and y_data_[i + 1] != y_value) or i == len(y_data_) - 1:
                x_data.append(x_value)
                y_data.append(y_value)
            prev = y_value

        return x_data, y_data

    def calc_dominant_freqs(self, event):
        self.dominant_freqs_ = AudioHandler.calc_dom_frequencies(self.xf, self.yf_array, max_freq=self.FREQUENCY_RANGE[1])

        x_data = np.linspace(0, self.N, len(self.dominant_freqs_))
        y_data = self.dominant_freqs_
        self.dominant_freqs_x, self.dominant_freqs_y = self.simplify_freq_list(x_data, y_data)

        self.update_freq_lines()

    def copy_dominant_freqs(self, event):
        self.target_freqs_x = self.dominant_freqs_x.copy()
        self.target_freqs_y = self.dominant_freqs_y.copy()
        self.update_freq_lines()

    def reset_freqs(self, event, update=True):
        self.dominant_freqs_x = [0, self.N]
        self.dominant_freqs_y = [440, 440]
        self.target_freqs_x = [0, self.N]
        self.target_freqs_y = [440, 440]
        if update:
            self.update_freq_lines()

    def snap_freqs(self, event):
        self.target_freqs_x = np.arange(0, self.N + 1, 1)
        self.target_freqs_y = self.target_freqs_line.revert_graph()
        target_freqs_y_new = []
        previous_time = 0
        prev_freq = None
        prev_closest_freq = None
        for i, freq in enumerate(self.target_freqs_y):
            if freq != prev_freq:
                closest_freq = AudioHandler.closest_note_freq(freq, self.scale)
            else:
                closest_freq = prev_closest_freq
            target_freqs_y_new.append(closest_freq)
            prev_freq = freq
            prev_closest_freq = closest_freq
            if time.time() - previous_time >= 0.5:
                self.status_text.set_text(f"SNAPPING TARGET FREQS: "
                                          f"{round(i / len(self.target_freqs_y) * 100, 2)}% DONE...")
                self.fig.canvas.draw()
                previous_time = time.time()

        self.status_text.set_text("SNAPPING TARGET FREQS: 100% DONE...")
        self.fig.canvas.draw()
        self.target_freqs_x, self.target_freqs_y = self.simplify_freq_list(self.target_freqs_x, target_freqs_y_new)
        self.status_text.set_text("")
        self.fig.canvas.draw()

        self.update_freq_lines()

    def update_indication_status(self, event):
        self.indication_status = event

    def update_editing_status(self, event):
        try:
            self.editing_status = event
            self.update_freq_lines()
        except AttributeError:
            pass

    def update_freq_lines(self):
        self.dom_freqs_line.xs = self.dominant_freqs_x
        self.dom_freqs_line.ys = self.dominant_freqs_y
        self.target_freqs_line.xs = self.target_freqs_x
        self.target_freqs_line.ys = self.target_freqs_y
        self.dom_freqs_line.draw_callback(None)
        self.target_freqs_line.draw_callback(None)

    def get_zoom_level(self):
        xlim = self.ax_spectrogram.get_xlim()
        ylim = self.ax_spectrogram.get_ylim()
        range_x = xlim[1] - xlim[0]
        range_y = ylim[1] - ylim[0]

        return range_x / self.N, range_y / self.frequency_diff

    def load_spectrogram(self, event):
        file_path = tkinter.filedialog.askopenfilename(initialdir=".", filetypes=[("Wave", ".wav")])
        if file_path:
            self.load_file(filename=file_path)

    def record_spectrogram(self, event):
        self.SAMPLE_RATE = 44100
        self.status_text.set_text('STARTED RECORDING...')
        self.fig.canvas.draw()
        data = self.record(self.SAMPLE_RATE, self.record_duration)
        self.status_text.set_text('CALCULATING FREQS...')
        self.fig.canvas.draw()
        self.N = len(data)
        self.load_file(data=data)
        self.status_text.set_text('')
        self.fig.canvas.draw()

    def update_duration(self, text):
        try:
            self.record_duration = int(text)
        except ValueError:
            pass

    def play_spectrogram(self, event):
        self.ax_play.images[0].set_data(self.icon_play2)
        self.status_text.set_text('REVERTING SEQUENCE...')
        self.fig.canvas.draw()
        new_data = AudioHandler.revert_sequence(self.xf, self.yf_array, self.SAMPLE_RATE, self.N,
                                                dominant_freqs=self.dom_freqs_line.revert_graph(),
                                                target_freqs=self.target_freqs_line.revert_graph())
        self.status_text.set_text('PLAYING PROCESSED AUDIO...')
        AudioHandler.play_audio(new_data, self.SAMPLE_RATE)
        step_size = 5000
        for x in range(0, self.N, step_size):
            start_time = time.time()
            line = Line2D([x, x], self.FREQUENCY_RANGE, color='r', linewidth=3)
            line.set_alpha(0.4)
            self.ax_spectrogram.add_line(line)
            self.ax_spectrogram.draw_artist(line)
            self.canvas.draw()
            self.ax_spectrogram.lines.remove(line)
            time.sleep(max(self.DURATION / self.N * step_size - (time.time() - start_time), 0))
        self.ax_play.images[0].set_data(self.icon_play)
        self.status_text.set_text('')
        self.fig.canvas.draw()
