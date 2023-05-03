# LIS - Life Improvement System

This project is my take on a small Smart Home hub. I´m a huge Smart Home and Smart City enthusiast, which is why I decided on this type of project.

The goal is to have a working REST backend and a separate frontend that both run on a 
raspberry pi with an attached touchscreen to act as a control panel I can mount next to
my bed to make a lot of my "everyday-actions" easier for me.

**"But you could just use Home Assistant or OpenHAB?!?"**

That´s absolutely correct and there are many good solutions out there! This project is more of a personal pet project as well as a way to see how far I have improved my skills over the last years. It is also kind of a "playground" for me to test different technologies and ideas I have.

While one of my main goals was to design a complete system from the ground up and focus on a modular architecture where all modules are cleanly seperated from each other and only communicate via common structures located in the "core" of the system, I also gave myself three challenges when I started this project to work with some technologies I have never (or barely) used before and learn a lot more along the way.

The three challenges were:
* Use **Vue.js** to create a simple but beautiful frontend that works and fits onto a raspberry pi 7" touchscreen.
* Work with **TailwindCSS** to see if it´s a good fit for me and how it feels to use it.
* Create the backend in Python, but instead of using flask (like I´m used to) use a different framework (I landed on **tornado**) and write the whole backend as an **async** application completely avoiding threading where possible, to better my understanding of async task scheduling.

## Features

When it comes to features I´m pretty open-minded and will probably add more features as the project progresses.
I tried to design the system in a way that makes adding feature modules later on easy and uncomplicated by basing all communication between modules on a central event distributing system.

The "big" features I want to implement at the very least and the topics I want to play around with are:

* [x] Philipps Hue Integration 
* [x] Spotify Integration
* [X] Clock (to provide Server-Time offset to the client)
* [X] Weather
* [ ] Calendar
* [ ] CI/CD + Containerization


The features currently implemented are:
* REST Server setup using tornado. The actual request handling is however handled by a custom implementation to enable dynamic module-level api endpoint registration.
* Config / Data Storage using .toml files.
* Event System to distribute events between feature implementations and the core system to better encapsulate the logic. Also allows for dynamic short-term use response event receivers.
* Simple Philipps Hue integration using the REST Api of the local hue bridge.
* Simple Spotify integration using the spotify web api allowing for play, pause, next and prev commands and currently playing track. (Active device discovery and playback transferring may be implemented later on)
* Logging
* Support for server-sent events to communicate events like light state changes via an external source to the frontend. Also supports connecting to SSE-Streams itself (like the Hue-Bridge eventstream)
* Scheduling system to schedule event for later execution (~accurate to the minute) with support for persistent events that survive a system reboot as well as a grace period system that enables critical persistent events to be executed even if their scheduled execution time has long passed after a system-outage. It also supports automatic re-scheduling based on a repetition policy (e.g. hourly or daily).
* Weather data based on the provided longitude and latitude based on the Open-Weathermap API (updates every full hour)