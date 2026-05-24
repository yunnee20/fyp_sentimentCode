# Emotion Test — AI Emotional Assessment Installation

An interactive speculative installation exploring how artificial intelligence systems attempt to measure, classify, and optimise human emotion.

The project combines:

- facial analysis
- voice analysis
- text sentiment analysis
- real-time visualisation
- projection systems
- thermal receipt generation

to simulate an AI-driven emotional assessment environment.

---

# Project Overview

Emotion Test is an immersive installation that places participants inside a fictional emotional evaluation system.

Participants are shown socially complex scenario videos and must respond by selecting answers and optionally verbally justifying their decisions. Throughout the interaction, the system continuously analyses:

- facial expressions
- vocal behaviour
- speech sentiment
- emotional patterns

The installation then generates a speculative emotional score and prints a thermal receipt summarising the participant’s behavioural profile.

The project critiques how AI systems increasingly attempt to interpret emotion through computational data while presenting unstable or speculative interpretations as objective truth.

---

# System Architecture

```text
                        ┌──────────────────┐
                        │ Thermal Printer  │
                        └────────▲─────────┘
                                 │
                                 │
                    ┌────────────┴────────────┐
                    │         Python          │
                    │-------------------------│
                    │ • Face Analysis         │
                    │ • Voice Analysis        │
                    │ • Text Sentiment        │
                    │ • Scene Control         │
                    │ • Score System          │
                    │ • Receipt Generation    │
                    └───────┬─────────┬───────┘
                            │         │
              WebSocket     │         │ OSC
                            │         │
                ┌───────────▼───┐   ┌─▼──────────────┐
                │ JavaScript UI │   │ TouchDesigner  │
                └───────┬───────┘   └──────┬─────────┘
                        │                  │
                        ▼                  ▼
               Data Panel Screen     Projection Screen

```

# Technical Stack
## Python
Python functions as the central controller for the installation.

Responsibilities include:
```text
- scene flow management
- keyboard interaction handling
- face tracking
- voice processing
- speech transcription
- text sentiment analysis
- WebSocket communication
- OSC communication
- score calculation
- receipt printing
```

## Face Analysis
<b>Libraries</b>
- MediaPipe
- OpenCV
- Features
- facial landmark tracking
- face mesh rendering
- blendshape analysis
- emotional dimension calculation
- Emotion Metrics

The system derives speculative emotional dimensions from facial movement:
<b>valence, arousal, thinking, anxiousness</b>

Example Logic
$$ 
valence = smileLeft + smileRight - frownLeft - frownRight
$$

Landmark coordinates are streamed in real-time to the dashboard for visual overlays and reactive graphics.

## Voice Analysis
<b>Libraries</b>
```
SoundDevice
Librosa
```

<b>Features</b>
real-time microphone input
pitch detection
RMS energy analysis
voice activity monitoring

<b>Voice Metrics</b>
pitch
energy
average frequency
vocal stability


Pitch detection uses the YIN algorithm through Librosa.

## Speech-to-Text
Library
- Faster Whisper

The system temporarily transcribes spoken justification responses.

Audio is processed temporarily and deleted afterwards to avoid permanently storing participant voice recordings.

Text Sentiment Analysis
Model
```
j-hartmann/emotion-english-distilroberta-base
```

## Emotion Outputs
```
joy
sadness
anger
fear
disgust
surprise
neutral
```
The resulting emotion probabilities contribute to the speculative emotional assessment score.

## JavaScript Dashboard
The live dashboard interface was built using:
```
HTML
CSS
JavaScript Canvas API
WebSockets
```
<b>Features</b>
```
real-time face overlays
edge-detection camera effect
emotion radar chart
waveform visualisation
terminal logs
text sentiment display
animated UI components
```
Python streams live emotion data into JavaScript using WebSockets.

## TouchDesigner
TouchDesigner handles:
```
projection playback
scenario switching
cinematic transitions
audio triggering
installation visuals
```
Communication between Python and TouchDesigner uses OSC.

## Thermal Receipt System
Libraries
- PIL (Python Imaging Library)

The installation generates a thermal-style receipt containing:
```
emotional scores
behavioural labels
timestamps
facial metrics
authenticity percentage
```
The receipt acts as a physical artifact of the AI assessment process.

# Interaction Flow
```
WELCOME
↓
Scenario Video
↓
Participant chooses A/B/C/D
↓
System records response
↓
Optional spoken justification
↓
AI analysis
↓
Scene result
↓
Next scenario
↓
Final receipt printed
```

Participants may:
```
hold SPACE to speak
press TAB to skip
press ESC to end the experience early
```

## Main Python Structure
```
main2.py
│
├── scene_controller.py
│
├── face.py
│
├── voice_freqpitch.py
│
├── voicetotext.py
│
├── textsentiment.py
│
├── score.py
│
├── receipt.py
│
├── wsServer.py
│
└── audioTrigger.py
```

# Technical Challenges
Some major development challenges included:
```
real-time threading conflicts
camera synchronization
OSC timing issues
WebSocket instability
simultaneous audio/video processing
TouchDesigner switching logic
balancing performance between systems
managing multiple displays simultaneously
```
Many of these instabilities became conceptually relevant to the project itself, reinforcing the critique of unreliable AI emotional interpretation systems.

# Conceptual Focus

The project questions:
```
Can emotion truly be quantified?
Why do numerical systems appear trustworthy?
How easily do people submit to machine judgement?
What happens when emotional behaviour becomes optimised for systems?
```
Emotion Test intentionally presents unstable emotional interpretation through polished technological aesthetics to critique the authority often granted to AI systems.