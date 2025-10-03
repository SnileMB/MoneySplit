# MoneySplit Frontend

Modern React TypeScript frontend for the MoneySplit commission splitting application.

## Features

- 📊 **Dashboard**: Real-time statistics and recent projects overview
- 📁 **New Project**: Create projects with tax calculations and team splits
- 📈 **Reports**: Interactive visualizations, forecasts, and PDF exports
- 🎨 **Modern UI**: Clean, responsive design with smooth animations
- 🔄 **Real-time Data**: Live updates from FastAPI backend

## Tech Stack

- **React 18** with TypeScript
- **Axios** for API requests
- **Recharts** for data visualization
- **CSS3** for styling

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── api/
│   └── client.ts          # API client and TypeScript types
├── pages/
│   ├── Dashboard.tsx      # Dashboard page
│   ├── Projects.tsx       # Project creation form
│   └── Reports.tsx        # Analytics and reports
├── App.tsx                # Main app component
├── App.css                # Global styles
└── index.tsx              # Entry point
```

## API Configuration

The frontend connects to the backend API. To change the API URL, set the environment variable:

```bash
REACT_APP_API_URL=http://your-api-url:8000/api npm start
```

Default: `http://localhost:8000/api`

## Pages

### Dashboard
- **Statistics Cards**: Total revenue, projects, tax paid, net income
- **Recent Projects Table**: Latest 5 projects
- **Metrics**: Average tax rate, unique people, profit margin

### New Project
- **Form Fields**: Number of people, revenue, costs, country, tax type
- **Team Input**: Dynamic person forms with work share distribution
- **Validation**: Client-side validation with error messages
- **Success**: Shows created record ID on success

### Reports
- **Visualizations**: One-click access to interactive charts
  - Revenue Summary
  - Monthly Trends
  - Work Distribution
  - Tax Comparison
  - Project Profitability
- **Forecasting**: ML-powered revenue predictions
  - 3-month forecast
  - Confidence levels
  - Trend analysis
- **PDF Exports**: Download professional reports
  - Summary Report
  - Forecast Report

## Troubleshooting

### API Connection Issues
- Ensure backend is running: `cd .. && python3 -m uvicorn api.main:app --reload`
- Check CORS is enabled in backend
- Verify API_URL matches backend address

### Build Issues
- Clear node_modules: `rm -rf node_modules package-lock.json && npm install`
- Check Node version: `node --version` (should be 16+)
