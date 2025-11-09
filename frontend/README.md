# TraqCheck Frontend

React-based frontend for TraqCheck candidate management system.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure `.env` file with API base URL

3. Run development server:
```bash
npm run dev
```

## Build for Production

```bash
npm run build
```

Output will be in `dist/` directory

## Project Structure

```
src/
├── components/
│   ├── layout/          # Header, Layout
│   ├── upload/          # Resume upload components
│   ├── dashboard/       # Candidate table
│   ├── profile/         # Profile view, document section
│   └── shared/          # Reusable UI components
├── pages/               # Page components
├── services/            # API integration
└── App.jsx             # Main app with routing
```

## Features

### Upload Page
- Drag-and-drop resume upload
- Progress indicator
- File validation
- Success/error handling

### Dashboard
- Candidate table with pagination
- Status filtering
- Search functionality
- Click to view profile

### Candidate Profile
- Extracted data with confidence scores
- Document request generation
- Document upload
- Request history

## Components

### Shared Components
- Button: Reusable button with variants
- Card: Container component
- Badge: Status badges
- Spinner: Loading indicator
- ConfidenceScore: Confidence visualization

## Styling

Built with Tailwind CSS for responsive, modern UI design.

## API Integration

All API calls are centralized in `services/candidateService.js`
