# Project Name

An Integration app

## Prerequisites

- Node.js (v14 or higher) - Required for running the React.js frontend application and managing JavaScript dependencies
- npm or yarn - Node.js package managers used to install and manage frontend dependencies
- Python 3.8 or higher - Required for running the backend server
- pip (Python package manager) - Used to install Python dependencies
- Redis - Required for storing integration credentials and state information

## Project Structure

```
integrations_technical_assessment/
├── frontend/          # React frontend application
└── backend/           # Python FastAPI backend
    ├── integrations/  # Integration modules
    └── redis_client.py # Redis client configuration
```

## Setup Instructions

### Redis Setup

1. Install Redis on your system:
   - Windows: Download and install from https://github.com/microsoftarchive/redis/releases
   - MacOS: `brew install redis`
   - Linux: `sudo apt-get install redis-server`

2. Start Redis server:
   - Windows: Start Redis service
   - MacOS/Linux: `redis-server`

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd integrations_technical_assessment/backend
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the backend directory with the following variables:
   ```
   HUBSPOT_CLIENT_ID=your_client_id
   HUBSPOT_CLIENT_SECRET=your_client_secret
   HUBSPOT_REDIRECT_URI=http://localhost:8000/integrations/hubspot/callback
   REDIS_HOST=localhost
   ```

5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

The backend server will start running on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd integrations_technical_assessment/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or if using yarn
   yarn install
   ```

3. Start the development server:
   ```bash
   npm start
   # or if using yarn
   yarn start
   ```

The frontend application will start running on `http://localhost:3000`

## Running the Application

1. Make sure Redis server is running
2. Start the backend server
3. Start the frontend development server
4. Open your browser and navigate to `http://localhost:3000`
5. The application should now be fully functional

## Available Integrations

The application supports integration with the following services:

1. **HubSpot**
   - OAuth2 authentication
   - Access to contacts and deals
   - Real-time data synchronization

2. **Airtable**
   - OAuth2 authentication
   - Database/spreadsheet integration
   - Data loading capabilities

3. **Notion**
   - OAuth2 authentication
   - Workspace integration
   - Data synchronization

## API Documentation

- Backend API documentation is available at `http://localhost:8000/docs` when the server is running
- The API follows RESTful principles and uses FastAPI for automatic documentation

## License

This project is MIT Licensed
