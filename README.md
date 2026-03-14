# NeuroNav
> 🏆 **1st Place Winner - TR1 2026 AI Hackathon** (Option 2: Smart Cities Under Pressure) 🏆
>
> **The Healthiest & Calmest Path Through the City.**

## The Core Problem: The Invisible Urban Crisis
Modern navigation applications optimise routes primarily based on speed and distance, assuming efficiency is the main priority for all users. However, for individuals with Autism Spectrum Disorder (ASD) and the caregivers who support them, environments such as crowded spaces, loud traffic areas, and complex transit hubs can lead to sensory overload and significant distress. Because current routing systems do not consider sensory sensitivities, caregivers and autistic individuals are often forced to navigate routes that are technically efficient but emotionally and psychologically overwhelming.

## Our Solution
**NeuroNav** is a real-time, AI-powered routing engine that shifts the paradigm of urban navigation. Instead of minimizing time, NeuroNav minimizes a dynamic **"Sensory Cost Function"** to calculate the calmest, most accessible path using live urban data. 

### Key Features
* **Sensory Weighting Algorithm:** Highly customizable user profiles. Users input their specific triggers (e.g., high sensitivity to noise, moderate sensitivity to crowds) to generate personalized route weights.
* **Live Urban Data Integration:** * **OneMap API:** Pulls real-time crowd density data at transit hubs and shopping districts.
    * **LTA DataMall API:** Ingests live traffic volume data serving as a proxy for street-level noise pollution.
* **Predictive AI Forecasting:** Leverages time-series modeling to predict crowd surges before they happen, recommending optimal departure times to avoid sensory bottlenecks.

## System Architecture
NeuroNav is built for speed, scalability, and real-time processing. 



| Component | Technology Stack | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React.js, Tailwind CSS, Vite | A single-page, highly accessible interactive prototype. |
| **Backend** | Python, FastAPI | High-performance routing logic and API management. |
| **AI / ML** | Python, scikit-learn, Prophet | Time-series forecasting for predictive crowd modeling. |
| **Data Sources**| OneMap API, LTA DataMall | Real-time Singapore urban metrics. |

## Business Viability & Scalability
NeuroNav is designed with a sustainable, dual-stream revenue model:

1.  **Freemium B2C Model:** * *Free Tier:* Basic sensory routing and real-time navigation.
    * *Premium Tier:* Advanced predictive scheduling, calendar integration, and custom waypoint saving.
2.  **B2G (Business-to-Government) Licensing:** * Aggregated, anonymized accessibility data is licensed to urban planners (e.g., URA). This provides unprecedented insights into how citizens navigate sensory bottlenecks, directly aiding in the design of more inclusive "Smart Cities."

## Local Setup & Installation

### Prerequisites
* Python (3.10+)
* A modern web browser

### 1. Frontend Setup
The frontend is built with pure HTML, CSS, and JS. No build step is required!
Simply open `frontend/index.html` in your web browser.

