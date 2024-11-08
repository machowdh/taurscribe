# Taurscribe | Realtime Translation with a Desktop App

## Overview
This is a Tauri application that leverages Next.js for the frontend and a Python sidecar using FastAPI for backend services. The application listens to the user's desktop audio using PyAudio and WASAPI. As such, the application currently **only works on Windows.** The captured audio is fed into a HuggingFace pipeline using Whisper-Tiny to automatically transcribe incoming audio to English. Audio transcriptions are sent through a WebSocket used to communicate between the FastAPI server and the frontend.

## Inspiration

I wanted to design a one-stop shop application for all audio translation and transcription needs, or at least a proof of such a concept. For example, sometimes you may want to listen to foreign music and watch foreign media, or interchange between the two. The Taurscribe app would provide an opportunity to do so without needing to have a specific application tailored for each need.

## Features
- **Real-time audio capture** using PyAudio and WASAPI
- **Transcription and translation** FastAPI backend that connects to the frontend with a Websocket endpoint
- **Frontend** built with Next.js and using shadcn/ui
- **Desktop integration** with Tauri

![image](https://github.com/user-attachments/assets/f9faaa66-b1fa-421f-a943-49f1d10d252b)

## Prerequisites
- A discrete GPU, this project was built and tested on an RTX 2080
- Windows 10

## Installation
- For local testing and use a requirements.txt is provided for virtual environments.
- [TODO] The executable can be downloaded from the release page and run as an .exe

## Additional Features/Points of Improvement
- The UI currently only provides a textarea and a few buttons to demonstrate the project use case
- User-set parameters:
    - Context window, or how many seconds of audio should be saved in the buffer for consecutive transcriptions
    - Transcription to the language of choice
- The model replicates standard Whisper performance on the most popular subset of languages. As such, fine-tuning or modifications to the buffering process
  could help produce better transcriptions.
