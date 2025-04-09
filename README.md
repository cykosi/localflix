# LocalFlix Web Dashboard

## Overview

LocalFlix is a web dashboard designed to provide a seamless and visually appealing way to browse and play video files (.mp4 and .mkv) stored on a local Raspberry Pi server. Accessible via a local network address (e.g., `http://192.168.0.68:PORT`), the dashboard aims to offer a user-friendly experience reminiscent of popular streaming platforms, but tailored for local content.

This project consists of two main components:

- **Frontend:** A modern and responsive user interface built with **Next.js**.
- **Backend:** A lightweight API built with **Flask** to serve video file listings and facilitate playback.

The primary goal is to deliver a polished and immersive interface that allows users on the same network to effortlessly discover and enjoy their locally stored video content.

## Design Brief Highlights

The design prioritizes the following key aspects:

- **Stunning, Modern UI:** A visually appealing design with a clean and contemporary aesthetic.
- **Intuitive Layout:** Easy-to-understand organization of content and features.
- **Effortless Navigation:** Simple and straightforward browsing experience for all users.
- **Clear, Responsive Playback Controls:** Smooth and reliable video playback with intuitive controls.
- **Local Network Accessibility:** Designed for access within a local network via a Raspberry Pi server.
- **Support for .mp4 and .mkv:** Compatibility with common video file formats.
- **Polished and Immersive Interface:** A user experience that feels like a dedicated local streaming platform.

## Technologies Used

### Frontend

- **Next.js:** A React framework for building performant and scalable web applications with features like server-side rendering and routing.
- **Yarn:** Package manager used for managing frontend dependencies.
- **Tailwind CSS:**  UI library or framework.
- **HTTP Client (Implicit):** A library like `fetch` or `axios` is used to communicate with the Flask backend.
 
  ```
  yarn -v 1.22.22
  ```
  ```
  node -v v20.19.0
  ```
  ```
  npm -v 11.2.0
  ```


### Backend

- **Flask:** A lightweight and flexible Python web framework used to build the API endpoints.
- **Python:** The programming language used for the backend.
- **Potentially Other Libraries:** Depending on the implementation, the backend might use libraries for file system operations, video metadata extraction (optional), and more.

## Project Structure (Conceptual)

While the exact file structure will depend on the implementation, a typical structure might look like this:

```
localflix/
├── frontend/
│   ├── next.config.js
│   ├── package.json
│   ├── yarn.lock
│   ├── src/
│   │   ├── pages/
│   │   │   ├── _app.js
│   │   │   ├── index.js
│   │   │   └── [videoId].js  # Example for video playback page
│   │   ├── components/
│   │   │   ├── ...
│   │   ├── styles/
│   │   │   ├── ...
│   │   ├── utils/
│   │   │   ├── ...
│   └── README.md         # Frontend-specific README
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── data/             # Potentially for storing video file paths or metadata
│   └── README.md         # Backend-specific README
└── README.md             # This main README
```
