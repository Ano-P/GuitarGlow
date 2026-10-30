# GuitarGlow

#### Video Demo: (https://youtu.be/nH8rkn1L-pc)

#### Description:

GuitarGlow is a Python audio visualizer that turns live microphone input into an on-screen effect. When sound is detected, a glow starts at the centre of the display and spreads across a grid, while colourful particles move outward and leave fading trails. The current version responds to overall sound intensity rather than identifying musical notes or chords.

I started GuitarGlow to explore a visual idea inspired by playing guitar, and I hope to develop it beyond the CS50P final project. It brings audio input, numerical processing, graphics, and object-oriented programming together in a project I can continue experimenting with myself.

#### Installation

You need Python, a working microphone, and the packages listed in `requirements.txt`. GuitarGlow uses your computer's default microphone, so check that the correct input device is selected.

From the project directory, create and activate a virtual environment on Windows PowerShell, then install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

#### Usage

With the environment activated and the dependencies installed, run:

```bash
python project.py
```

GuitarGlow opens a full-screen Pygame display and reacts to sound picked up by the default microphone. Allow microphone access and play sound near the selected input device. Close the application window to exit.

#### How It Works and Design Decisions

Audio recording runs on a separate thread so the main loop can draw the visualisation without waiting for a recording to finish. The recording function calculates the root mean square (RMS) of each short audio chunk and places the measurement in a queue. The main loop retrieves measurements from the queue, which acts as a handoff point between audio recording and graphics rendering.

Each RMS value is normalised to a range between 0 and 1 using lower and upper thresholds. The program smooths that value with the previous smoothed measurement to reduce abrupt changes, then scales it through energy mapping. Energy transfer adds the result to the centre cell of a two-dimensional NumPy grid. Starting in the centre was a deliberate choice to make the visual effect expand outward from one point.

The diffusion function updates each interior cell using the average of its four neighbours, moving the cell's value towards that average. Repeating the calculation makes the energy pattern spread across the grid. A separate fading step gradually reduces the grid's energy. The grid is converted into pixel brightness values for a Pygame surface, with the same brightness assigned to red, green, and blue to create a grayscale glow. The coloured particles provide the colour in the visualisation.

The particle system adds movement and colour. The `Particle` class groups each particle's position, velocity, colour, and lifetime with the methods that update and draw it. Particles are created when the smoothed audio value passes a threshold. Random starting velocities and a colour palette give them variation. They are drawn onto a separate trail surface, which fades over time. Dividing these operations into separate functions also makes the program easier to follow and test.

#### Files and Functionality

- `project.py` contains the main application, `Particle` class, audio recording, and visualisation functions.
- `test_project.py` contains automated tests for functions in `project.py`.
- `requirements.txt` lists the external packages needed to run the application.
- `README.md` documents the project and explains how to set it up.

#### Tests

Run the tests from the project directory with:

```bash
pytest
```

If `pytest` is not installed, install it with `python -m pip install pytest` first.

#### Future Enhancements

I would like GuitarGlow to recognise more than overall sound intensity. For guitar, a future version could identify individual notes and chords so a single note, a chord, or a solo could trigger different visual effects. This would require analysing the audio in more detail.

I would also like to add an interface where users choose their sound source and visual preferences. Guitar could produce particle effects, singing could create landscape-like scenes, and different sound layers could control separate visual elements. These are plans, not features of the current version.