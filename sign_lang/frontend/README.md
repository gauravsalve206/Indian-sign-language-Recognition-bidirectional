# Frontend Structure

This directory contains the frontend files for the ISL Translator application.

## Files

- `index.html` - Main landing page with navigation
- `sign-to-text.html` - Real-time sign language recognition page
- `text-to-sign.html` - Text to sign language translation page (placeholder for future implementation)
- `styles.css` - Shared stylesheet for all pages

## Navigation Structure

All pages share a common navigation bar with links to:
- **Home** (`index.html`) - Landing page with feature overview
- **Sign to Text** (`sign-to-text.html`) - Webcam-based sign recognition
- **Text to Sign** (`text-to-sign.html`) - Text input to sign language translation

## Backend Connection

The frontend connects to the backend server running on `http://localhost:8000`:

- WebSocket: `ws://localhost:8000/ws` - Used for real-time sign recognition
- REST API: `http://localhost:8000/text-to-sign` - Used for text-to-sign translation

## Running the Frontend

### Option 1: Via FastAPI Backend (Recommended)

When you start the FastAPI backend server, it will serve the frontend files automatically:

1. Start the backend:
   ```bash
   uvicorn src.server:app --reload --port 8000
   ```

2. Open your browser and navigate to:
   - `http://localhost:8000` - Home page
   - `http://localhost:8000/sign-to-text.html` - Sign to Text page
   - `http://localhost:8000/text-to-sign.html` - Text to Sign page

### Option 2: Using Python HTTP Server

Alternatively, you can serve the frontend separately:

1. Start a separate HTTP server:
   ```bash
   python -m http.server 3000 --directory frontend
   ```

2. Make sure the backend is running on port 8000

3. Open your browser to: `http://localhost:3000`

## Development Notes

- The `text-to-sign.html` page currently uses a placeholder endpoint that returns a "not implemented" message
- When implementing the text-to-sign feature, update the `/text-to-sign` endpoint in `src/server.py`
- All pages use the shared `styles.css` for consistent styling
- Navigation is handled via relative links between HTML pages










