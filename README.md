# NeuroNav
The Problem: The Invisible Urban Crisis

Modern navigation apps (like Google Maps) optimize purely for speed and distance. However, for the 15-20% of the population who are neurodivergent (Autism, ADHD) or suffer from anxiety, the fastest route is often the most inaccessible due to severe sensory overload (dense crowds, heavy traffic noise).

Our Solution

Neuro-Nav is a real-time, AI-powered routing engine that calculates the "Healthiest & Calmest Path".
Instead of minimizing time, our algorithm minimizes a Sensory Cost Function using live urban data.

Core Features

Sensory Weighting Algorithm: Users input their specific triggers (e.g., highly sensitive to noise, moderately sensitive to crowds).

Live Urban APIs Integration:

OneMap API: Real-time crowd density data at transit hubs and malls.

LTA DataMall: Real-time traffic volume (used as a proxy for street-level noise pollution).

Predictive AI Forecasting: Uses time-series modeling to predict crowd surges before they happen, advising users on optimal departure times.

System Architecture

Frontend Prototype: React.js + Tailwind CSS (Single Page Application dashboard for demo).

Proposed Backend: Python (FastAPI) handling pathfinding logic.

AI/ML: Python scikit-learn / Prophet for predictive crowd modeling.

How to Run the Prototype

For the hackathon demonstration, the frontend prototype has been consolidated into a single interactive React component.

Clone this repository.

Ensure you have Node.js installed.

Install dependencies using npm install (assuming standard Vite/React setup).

Run the development server using npm run dev.

The core UI logic is contained within App.jsx.

Hackathon Rubric Focus

Clear Problem Definition: Targets a highly specific, underserved demographic with a real urban problem.

Scalability: The sensory cost algorithm can be applied to any city globally with open data APIs.

Business Viability: Freemium B2C model + B2G (Business-to-Government) data licensing to urban planners (e.g., URA) to design more accessible public spaces.
