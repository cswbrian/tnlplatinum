# 試當真白金像獎 (Trial and Error Platinum Awards) - Voting Platform

A React-based voting platform for the "試當真白金像獎" (Trial and Error Platinum Awards), featuring over 1000 videos from 5 years of content. Users can browse, search, and vote for their favorite films, songs, advertisements, variety shows, audition films, and supporting actors.

## 🎬 About This Project

This is a comprehensive voting platform that allows users to:
- Browse through 6 different award categories
- Search through thousands of entries with real-time filtering
- Mark items as watched/unwatched with local storage persistence
- Search for videos on YouTube directly from the platform
- Experience smooth performance with virtual scrolling and lazy loading

### Award Categories
- **最佳電影** (Best Film) - Feature films and short films
- **最佳原創電影歌曲** (Best Original Film Song) - Original songs from films
- **最佳廣告片** (Best Advertisement) - Commercial and promotional videos
- **最佳試音片** (Best Audition Film) - Casting and audition videos
- **最佳綜藝** (Best Variety Show) - Entertainment and variety content
- **最佳搭膊頭** (Best Supporting Actor) - Supporting actor performances

## 🚀 Getting Started

### Prerequisites
- Node.js (version 18 or higher)
- npm or yarn package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tnlplatinum
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 📦 Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build the project for production
- `npm run preview` - Preview the production build locally
- `npm run lint` - Run ESLint to check code quality
- `npm run deploy` - Build and deploy to GitHub Pages

## 🏗️ Building for Production

To create a production build:

```bash
npm run build
```

This will:
1. Compile TypeScript code
2. Bundle and optimize assets
3. Generate static files in the `dist/` directory

## 🚀 Deployment

### GitHub Pages (Recommended)

The project is configured for easy deployment to GitHub Pages:

```bash
npm run deploy
```

This command will:
1. Build the project for production
2. Deploy the `dist/` folder to the `gh-pages` branch
3. Make the site available at `https://<username>.github.io/<repository-name>/`

### Manual Deployment

For other hosting platforms:

1. Build the project:
```bash
npm run build
```

2. Upload the contents of the `dist/` directory to your web server

### Environment Variables

No environment variables are required for this project as it uses static data files.

## 🛠️ Technology Stack

- **Frontend Framework**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: CSS with responsive design
- **Data Management**: Static JSON files
- **Performance**: Virtual scrolling, lazy loading, debounced search
- **Deployment**: GitHub Pages

## 📁 Project Structure

```
tnlplatinum/
├── src/
│   ├── App.tsx          # Main application component
│   ├── App.css          # Application styles
│   ├── assets/          # Images and static assets
│   ├── data/            # Award category data (JSON files)
│   └── main.tsx         # Application entry point
├── public/              # Public assets
├── dist/                # Production build output
└── package.json         # Dependencies and scripts
```

## 🎯 Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Search**: Instant filtering across all categories
- **Progress Tracking**: Mark items as watched with local storage
- **YouTube Integration**: Direct search links to YouTube
- **Performance Optimized**: Virtual scrolling for large datasets
- **Accessibility**: Keyboard navigation and screen reader support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is private and proprietary to 試當真 (Trial and Error).

---

**五年時間 過千影片 由你選出心中最佳**  
*Five years, over a thousand videos - you choose the best*
