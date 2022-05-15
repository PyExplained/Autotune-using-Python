# Autotune using Python

Using the GUI, you can easily load or record audio samples and modify the pitch.
If you'd like to know how the calculations behind this program work, you can watch this video: [https://youtu.be/HvKpBbHj5cY](https://youtu.be/HvKpBbHj5cY). <br>
The most important information given in the video will be listed below.
If you have questions, suggestions or if you encounter a bug, be sure to let me know 
(eg. by creating an 'issue' on GitHub).

## Table of Contents
1. [Required modules](#Required_modules)
2. [GUI Explanation](#GUI_Explanation)
    1. [Buttons](#Buttons)
    2. [Selecting a scale](#Selecting_a_scale)
    3. [Modifying frequency lines](#Modifying_frequency_lines)
3. [Moving around and zooming in](#Navigate_spectrogram)

## Required modules <a name="Required_modules"></a>
- matplotlib
- sounddevice
- scipy
- cv2 (OpenCV)
- numpy

The rest of the modules should be built-ins, 
but definitely let me know if you encounter any problems with
the installation.

## GUI Explanation <a name="GUI_Explanation"></a>
When you first open the application, you'll see the **spectrogram** of a piano note (A4).
A spectrogram is a way of representing an audio signal where the X-axis represents time
and the Y-axis represents the frequencies. The color of the pixels represents
the volume or amplitude of that particular frequency.

You'll also see two lines, called the **dominant frequency line** and the **target frequency line**
(also sometimes called the frequency graphs).
These lines can be modified using the buttons displayed on the right or by manually adding and
dragging around points. More info on their purpose or how to modify them can be found 
in the section about [Modifying frequency lines](#Modifying_frequency_lines).

If you want an audio file to test something, you can load in one of the WAV files in "audio_samples".
Some of these samples come from freesound.org, hereby the needed credits: <br>
voice A4 -> "Solfege - La.wav" by digifishmusic (https://freesound.org/people/digifishmusic/sounds/44932/) licensed under CCBY 3.0 <br>
opera vocals -> "ABIDE WITH ME - Opera vocals.wav" by Ramston (https://freesound.org/people/Ramston/sounds/262274/) licensed under CCBYNC 4.0 <br>
someone talking -> "Request #12 - novaawesomesauce (26.5.18) » Voice Request #36 - What's the point.wav" by InspectorJ  <br>(https://freesound.org/people/InspectorJ/sounds/431167/) licensed under CCBYNC 4.0 <br>

 ### Buttons <a name="Buttons"></a>
- **Play button:** Plays the audio sample (Note: it may take some time to calculate the modified audio)
- **Load Sample:** Loads in an audio file (only .WAV files allowed)
- **Record Sample:** Records an audio sample using your microphone
                     (Note that you can change the duration of the audio recording using the 'Duration' entry)
- **Calc. Freqs:** Calculates the dominant frequencies
                   (Note that this calculation won't always result in the correct frequencies, in which case
                   it's recommended to change the graph manually)
- **Copy Freqs:** Sets the target frequencies equal to the dominant frequencies
- **Reset Freqs:** Sets the frequencies equel to 440 Hz
- **Snap Freqs:** Snaps the target frequencies to the closest notes in the scale 
                  (eg. 438 Hz would be rounded to approx. 440 Hz)
- **Select Scale:** Opens up a second window that you can use to select select the notes that are part of the scale
                    (see [Selecting a scale](#Selecting_a_scale))
- **Indication Shown:** By default, when dragging around points or line segments, the frequency will be displayed
                        above them. You can use these radio buttons to configure it to display the note names 
                        or to not display anything. Note names of frequencies that lie in between two notes will get
                        a number with a ¢-symbol, which is one hundredth of a semitone
           
### Selecting a scale <a name="Selecting_a_scale"></a>
Using the **Select Scale** button, you can open up a second window, which allows you to select the notes
that are part of the scale. This scale determines which notes points will get rounded or snapped to when
holding CTRL or clicking the **Snap Freqs** button. You can also choose from a list of presets, which includes
the chromatic scale and all basic major and minor scales (if you want blues scales, pentatonic scales or 
anything else, use the checkboxes to select the notes that are part of that scale).

### Modifying frequency lines <a name="Modifying_frequency_lines"></a>
Frequency lines or graphs refers to the **dominant frequency line** and the **target frequency line**.

The dominant frequency lines indicates the 'tone' or dominant frequency of the original audio at that
moment in time (not to be confused with the so called overtones that are often present in these audio samples).

The target frequencies are what the dominant frequencies will become after the transformation.
Eg. an audio sample of a piano note could have a dominant frequency of 440 Hz throughout the whole sample, but
we want it to be 880 Hz (i.e. one octave higher), so you would set the target frequency graph to 880 Hz.

With the right frequency line selected, you can modify the graph as described below:
- **Add point:** double click where you want to insert the point
- **Delete point:** right click the point you want to delete
- **Move point:** drag around a point using LMB
- **Change height of line segment:** drag a line segment up or down using LMB
- **Snap point or line segment to closest note:** hold CTRL while dragging around the point or line segment
                                                  (only notes of the selected scale will be considered,
                                                  see [Selecting a scale](#Selecting_a_scale);
                                                  in the case of a line segment, only the endpoints will get
                                                  snapped to the closest note)

### Moving around and zooming in <a name="Navigate_spectrogram"></a>
One question you might still have is: how can I zoom in and/or move around?

This can be done using the default Matplotlib buttons, which are located in the bottom left corner of the window.
Most probably, you're going to want to use the button with the move icon (panning around with LMB and zooming in
by dragging with RMB pressed).


_If there are any other topics I should cover in the documentation or if you have any unanswered question,
don't hesitate to let me know._ 
