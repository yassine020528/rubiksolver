# Rubik Solver

A desktop Rubik's Cube solver built with Python, PyQt6, OpenGL, and the Kociemba two-phase solver.

The app lets you enter the sticker colors of a real 3x3 Rubik's Cube, validates the cube state, finds a solution, and plays the solution step by step with animated 3D face turns.

## Features

- Interactive 3D Rubik's Cube rendered with OpenGL.
- Mouse controls for rotating the camera around the cube.
- 2D sticker editor for entering the colors of each cube face.
- Live 3D preview while editing sticker colors.
- Face orientation labels on the 3D cube: `F`, `B`, `L`, `R`, `U`, and `D`.
- Cube-state validation before solving.
- Kociemba-based solution generation.
- Step-by-step solution guide.
- Animated move playback.
- `Next Move`, `Back`, and `Auto Play` controls.

## Requirements

- Python 3.10 or newer
- PyQt6
- PyOpenGL
- PyOpenGL_accelerate
- kociemba
- numpy

The Python dependencies are listed in [requirements.txt](requirements.txt).

## Installation

From the project folder, install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

If you prefer using a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running The App

Start the desktop app with:

```powershell
python main.py
```

## How To Use

1. Rotate the 3D cube with the mouse to inspect the current state.
2. In the `Cube Colors` panel, choose a face from the dropdown.
3. Pick a color from the palette.
4. Click the 3x3 sticker grid to paint that face.
5. Repeat until the app matches your real cube.
6. Click `Solve`.
7. Use `Next Move` to play one solution step at a time.
8. Use `Back` to undo the last played solution step.
9. Use `Auto Play` to animate the full solution automatically.

## Controls

- Left mouse drag: rotate the 3D view.
- Mouse wheel: zoom in or out.
- Arrow keys: rotate the 3D view in small increments.
- `Solve`: validate the cube and generate a solution.
- `Next Move`: animate the next move in the solution.
- `Back`: animate the inverse of the last applied solution move.
- `Auto Play`: play or pause the remaining solution moves.
- `Reset Solved`: restore the cube to the default solved color layout.

## Face Labels And Orientation

The 3D cube has letter labels on the center stickers:

- `F`: Front
- `B`: Back
- `L`: Left
- `R`: Right
- `U`: Up
- `D`: Down

These labels are not only names. Their rotation shows the face orientation compared to the 2D sticker editor. If a label appears upside-down or rotated in the 3D view, that tells you how the visible face is oriented relative to the editor grid.

## Move Notation

The solution uses standard Rubik's Cube notation:

- `R`: turn the right face clockwise.
- `R'`: turn the right face counter-clockwise.
- `R2`: turn the right face 180 degrees.

The same pattern applies to all six faces:

- `U`: Up
- `D`: Down
- `L`: Left
- `R`: Right
- `F`: Front
- `B`: Back

Clockwise and counter-clockwise are interpreted as if you are looking directly at the face being turned.

## Project Structure

```text
rubiksolver/
|-- cube.py           # Editable cube state and move application
|-- cube_config.py    # Face names, color values, and solved layout
|-- cube_geometry.py  # Cubie positions, facelet mapping, and vector rotation
|-- cube_moves.py     # Move definitions and move parsing helpers
|-- cube_types.py     # Shared dataclasses and type aliases
|-- face_editor.py    # 2D color-entry panel
|-- gl_widget.py      # OpenGL view, camera controls, and animation flow
|-- main.py           # Application entry point
|-- main_window.py    # Main PyQt window layout and signal wiring
|-- render_data.py    # OpenGL mesh, sticker, edge, and label drawing data
|-- solver.py         # Validation, Kociemba conversion, solving, and move helpers
|-- solve_panel.py    # Solver UI, guide, next/back/auto-play controls
`-- requirements.txt  # Python dependencies
```

## How It Works

The app stores the cube as six editable 3x3 face grids in `RubiksCube`. Shared cube constants, geometry mapping, move definitions, and rendering data live in separate modules so the model, solver, UI, and OpenGL view stay independent.

The main responsibilities are:

- `cube.py` owns the current sticker state and applies moves.
- `cube_geometry.py` converts between face-grid coordinates and 3D cubie positions.
- `cube_moves.py` describes face turns and normalizes move details for the model and animation.
- `solver.py` validates the cube and converts it into Kociemba's `URFDLB` facelet order.
- `gl_widget.py` reads sticker colors from the model and renders/animates the 3D cube using data from `render_data.py`.

When you click `Solve`, the app:

1. Checks that every color appears exactly 9 times.
2. Checks that the six center stickers are all different.
3. Converts the cube into Kociemba's expected `URFDLB` facelet string.
4. Calls the Kociemba solver.
5. Displays the move list with plain-language instructions.
6. Animates each move and commits the move back into the cube model.

## Current Limitations

- This project currently targets standard 3x3 Rubik's Cubes only.
- The app assumes the entered sticker state is physically possible. Kociemba will reject impossible cube states.
- There is no camera-based color scanner yet.
- There is no save/load feature for cube states yet.

## Development Notes

Run a quick syntax check with:

```powershell
python -m py_compile main.py main_window.py gl_widget.py cube.py face_editor.py solve_panel.py solver.py cube_config.py cube_geometry.py cube_moves.py cube_types.py render_data.py
```

The solver can be tested by scrambling the model in code, solving it, applying the returned moves, and confirming the cube returns to solved state.

## Roadmap Ideas

- Add save/load for entered cube states.
- Add a scramble button for testing.
- Add manual cube moves outside the solver flow.
- Add speed controls for animations.
- Add camera or image-based sticker detection.
- Add clearer validation messages for impossible cube states.
