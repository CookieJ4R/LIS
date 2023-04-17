# LIS - Life Improvement System

This project is my take on a small Smart Home hub. 
The goal is to have a working REST backend and a separate frontend that both run on a 
raspberry pi with an attached touchscreen to act as a control panel I can mount next to
my bed to make a lot of my "everyday-actions" easier for me.

**"But you could just use Home Assistant or OpenHAB?!?"**

That´s absolutely correct and there are many good solutions out there! This project is more of a personal pet project as well as a way to see how far I have improved my skills over the last years. It is also kind of a "playground" for me to test different technologies and ideas I have.
When I started this project I also gave myself three challenges to work with some technologies I have never (or barely) used before.

The three challenges are:
* Use **Vue.js** to create a simple but beautiful project
* Work with **TailwindCSS** to see if it´s a good fit for me and how it feels to use it.
* Create the backend in Python, but instead of using flask (like I´m used to) use a different framework (I landed on **tornado**) and write the whole backend as an **async** application completely avoiding threading where possible, to better my understanding of async task scheduling.

## Features

When it comes to features I´m pretty flexible and will probably add more features as the project progresses.
I tried to design the system in a way that makes adding feature modules later on easy and uncomplicated by basing all communication between modules on a central event distributing system.

The "big" features I want to implement at the very least and the topics I want to play around with are:

* Philipps Hue Integration
* Spotify Integration
* Calendar
* Clock/Alarm
* Weather
* Logging
* CI/CD + Containerization


The features currently implemented are:
* REST Server setup using tornado. The actual request handling is however handled by a custom implementation.
* Config / Data Storage using .toml files.
* Event System to distribute events between feature implementations and the core system to better encapsulate the logic.
* Simple Philipps Hue integration using the REST Api of the local hue bridge.