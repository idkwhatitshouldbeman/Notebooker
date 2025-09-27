# Notebooker - Netlify Frontend

This is the frontend React application for Notebooker, deployed on Netlify. The backend API services remain separate and are deployed independently.

## 🚀 Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:5002
```

For production, set the environment variable in Netlify:
- `VITE_API_URL=https://your-backend-api.com`

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
├── pages/              # Page components
├── hooks/              # Custom React hooks
├── services/           # API service functions
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
├── App.tsx             # Main app component
├── main.tsx            # App entry point
├── index.css           # Global styles
└── App.css             # App-specific styles
```

## 🔧 Configuration

### Netlify Configuration

The `netlify.toml` file contains:
- Build settings
- Redirect rules for SPA routing
- Security headers
- API proxy configuration

### Build Process

1. **Development**: Vite dev server with hot reload
2. **Production**: Vite build creates optimized static files
3. **Deployment**: Netlify automatically builds and deploys

## 🔌 API Integration

The frontend communicates with the backend API through:
- **Authentication**: Login/register endpoints
- **Projects**: CRUD operations for projects
- **AI Tasks**: Task management and status tracking
- **Content**: Analysis and planning endpoints

### API Service

The `src/services/api.ts` file contains:
- Axios configuration with interceptors
- Authentication token management
- API endpoint functions
- Error handling

## 🎨 UI Components

### Design System

- **Theme**: Dark theme with Bootstrap 5
- **Colors**: Custom CSS variables for consistency
- **Components**: React Bootstrap components
- **Icons**: Lucide React icons
- **Responsive**: Mobile-first design

### Key Components

- **Navbar**: Navigation with authentication state
- **AuthPage**: Login/register forms
- **Dashboard**: Main dashboard with quick actions
- **Feature Cards**: Reusable action cards

## 🔐 Authentication

### State Management

Uses Zustand for state management:
- User authentication state
- Session token storage
- Persistent storage with localStorage

### Security

- JWT token handling
- Automatic token refresh
- Secure logout functionality
- Protected routes

## 📱 Features

### Current Features

- ✅ User authentication (login/register)
- ✅ Dashboard with quick actions
- ✅ Project management interface
- ✅ AI service status monitoring
- ✅ Responsive design
- ✅ Dark theme

### Planned Features

- 🔄 Section management
- 🔄 Content analysis
- 🔄 Draft creation
- 🔄 Planning sheet
- 🔄 Settings configuration
- 🔄 Backup management

## 🚀 Deployment

### Netlify Deployment

1. **Connect Repository**: Link GitHub repository to Netlify
2. **Build Settings**: 
   - Build command: `npm run build`
   - Publish directory: `dist`
3. **Environment Variables**: Set `VITE_API_URL`
4. **Deploy**: Automatic deployment on push to main branch

### Custom Domain

Configure custom domain in Netlify dashboard:
- Add domain in Site settings
- Configure DNS records
- Enable HTTPS (automatic)

## 🔧 Development

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on configured URL

### Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint errors
npm run type-check   # TypeScript type checking
```

### Code Style

- **ESLint**: Configured for React and TypeScript
- **Prettier**: Code formatting (recommended)
- **TypeScript**: Strict type checking
- **Conventional Commits**: Commit message format

## 🐛 Troubleshooting

### Common Issues

1. **API Connection**: Check `VITE_API_URL` environment variable
2. **Build Errors**: Ensure all dependencies are installed
3. **Authentication**: Verify backend API is running
4. **Styling**: Check Bootstrap CSS is loaded

### Debug Mode

Enable debug logging:
```javascript
localStorage.setItem('debug', 'true')
```

## 📚 Documentation

- **API Documentation**: Backend API endpoints
- **Component Documentation**: React component props and usage
- **Deployment Guide**: Netlify deployment steps
- **Contributing**: Development guidelines

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Note**: This frontend application requires the backend API to be running and accessible at the configured URL. The backend handles all data persistence, AI service integration, and business logic.
