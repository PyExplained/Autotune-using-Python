from autotune import *


class AdjustableLine:
    def __init__(self, at, name, xs, ys, fig, ax, color):
        self.at = at
        self.xs = xs
        self.ys = ys
        self.color = color
        self.max_distance = 200

        self.fig, self.ax = fig, ax
        self.canvas = self.ax.figure.canvas

        self.name = name
        self.line = None
        self.mouse_point = None
        self.surrounding_x = [None, None]
        self.start_points_y = None
        self.start_mouse_y = None
        self.ctrl_pressed = False
        self.text_indication = None
        self.canvas.mpl_connect('draw_event', self.draw_callback)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_callback)
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)
        self.canvas.mpl_connect('key_release_event', self.key_release_callback)

    def draw_callback(self, event):
        if self.line is not None:
            self.ax.lines.remove(self.line)
        self.line = Line2D(self.xs, self.ys, color=self.color, linewidth=1,
                           marker='o', markerfacecolor=self.color, markersize=3)
        alpha = 1 if self.at.editing_status == self.name else 0.2
        self.line.set_alpha(alpha)
        self.ax.add_line(self.line)
        self.ax.draw_artist(self.line)

        if event is None:
            self.canvas.draw()

    def button_press_callback(self, event):
        if self.at.editing_status == self.name and event.inaxes == self.at.ax_spectrogram:
            zoom_x, zoom_y = self.at.get_zoom_level()
            zoom_vector = np.array([zoom_x, zoom_y])

            # (Re)move point
            for i, (x, y) in enumerate(zip(self.xs, self.ys)):
                distance = np.linalg.norm((np.array([event.xdata, event.ydata]) - np.array([x, y])) / zoom_vector)
                if distance <= self.max_distance:
                    if event.button == 1:
                        self.mouse_point = i
                        if i not in [0, len(self.xs) - 1]:
                            self.surrounding_x = [self.xs[i - 1], self.xs[i + 1]]
                        self.motion_callback(event)
                    elif event.button == 3 and x not in [0, self.at.N]:
                        del self.xs[i], self.ys[i]
                        self.draw_callback(None)
                    return

            # Add point or move line segment
            if event.button == 1:
                xp, yp = event.xdata, event.ydata
                dist_min, x_min, y_min, i_min = np.inf, None, None, None
                for i in range(len(self.xs) - 1):
                    x1, y1, x2, y2 = self.xs[i], self.ys[i], self.xs[i + 1], self.ys[i + 1]
                    m1 = (y2 - y1) / (x2 - x1)
                    q1 = -m1 * x1 + y1
                    if m1 != 0:
                        m2 = -1 / m1
                        q2 = -m2 * xp + yp

                        x = (q2 - q1) / (m1 - m2)
                        y = m2 * x + q2
                    else:
                        x, y = xp, y1

                    if x1 < x < x2 or x2 < x < x1:
                        dist = np.sqrt((((xp - x) / zoom_x) ** 2 + ((yp - y) / zoom_y) ** 2))
                        if dist < dist_min and dist < self.max_distance:
                            dist_min, x_min, y_min, i_min = dist, x, y, i

                if i_min is not None:
                    if event.dblclick:
                        self.xs.insert(i_min + 1, x_min)
                        self.ys.insert(i_min + 1, y_min)
                        self.draw_callback(None)
                    else:
                        self.mouse_point = [i_min, i_min + 1]
                        self.start_points_y = self.ys[i_min], self.ys[i_min + 1]
                        self.start_mouse_y = yp

    def button_release_callback(self, event):
        self.mouse_point = None
        if self.text_indication is not None:
            self.text_indication.remove()
            self.text_indication = None
            self.draw_callback(None)

    def motion_callback(self, event):
        if self.mouse_point is not None and event.inaxes == self.at.ax_spectrogram:
            yp = max(event.ydata, 1)
            if type(self.mouse_point) == list:
                for i, j in enumerate(self.mouse_point):
                    self.ys[j] = max(self.start_points_y[i] + yp - self.start_mouse_y, 1)
                x = sum([self.xs[self.mouse_point[i]] for i in range(2)]) / 2
                y = sum([self.ys[self.mouse_point[i]] for i in range(2)]) / 2
            else:
                if self.xs[self.mouse_point] not in [0, self.at.N] and \
                        self.surrounding_x[0] < event.xdata < self.surrounding_x[1]:
                    self.xs[self.mouse_point] = event.xdata
                self.ys[self.mouse_point] = yp
                x = event.xdata
                y = yp

            if self.ctrl_pressed:
                if type(self.mouse_point) == list:
                    note_names = []
                    for i in self.mouse_point:
                        note_name, self.ys[i] = AudioHandler.calculate_note_name(self.ys[i],
                                                                                 return_closest_note_freq=True,
                                                                                 scale=self.at.scale)
                        if self.at.indication_status == "Freq indication":
                            note_name = str(round(self.ys[i], 2)) + "Hz"
                        note_names.append(note_name)
                    note_name = "-".join(note_names) if note_names[0] != note_names[1] else note_names[0]
                else:
                    note_name, y = AudioHandler.calculate_note_name(y, return_closest_note_freq=True,
                                                                    scale=self.at.scale)
                    self.ys[self.mouse_point] = y
                    if self.at.indication_status == "Freq indication":
                        note_name = str(round(y, 2)) + "Hz"
            else:
                if type(self.mouse_point) == list:
                    note_names = []
                    for i in self.mouse_point:
                        if self.at.indication_status == "Note indication":
                            note_name = AudioHandler.calculate_note_name(self.ys[i])
                            note_names.append(note_name)
                        else:
                            note_names.append(str(round(self.ys[i], 2)) + "Hz")
                    note_name = "-".join(note_names) if note_names[0] != note_names[1] else note_names[0]
                else:
                    if self.at.indication_status == "Note indication":
                        note_name = AudioHandler.calculate_note_name(y)
                    else:
                        note_name = str(round(y, 2)) + "Hz"

            if self.text_indication is not None:
                self.text_indication.remove()

            if self.at.indication_status != "None":
                dist = 80 * self.at.get_zoom_level()[1]
                self.text_indication = self.at.ax_spectrogram.text(x, y + dist, note_name,
                                                                   ha="center", fontsize=10, backgroundcolor="white")

            self.draw_callback(None)

    def key_press_callback(self, event):
        if event.key == "control":
            self.ctrl_pressed = True

    def key_release_callback(self, event):
        if event.key == "control":
            self.ctrl_pressed = False

    def revert_graph(self):
        new_y_data = []
        for i in range(len(self.xs) - 1):
            x1, x2 = self.xs[i], self.xs[i + 1]
            y1, y2 = self.ys[i], self.ys[i + 1]
            range_ = x2 - x1
            for n, j in enumerate(range(int(x1), int(x2))):
                new_y_data.append(y1 + (y2 - y1) * n / range_)

        return new_y_data + [self.ys[-1]]
