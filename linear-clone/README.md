# Linear Clone

A modern issue tracking and project management application inspired by Linear, built with Next.js, TypeScript, and Tailwind CSS.

## Features

### ✨ Core Functionality
- **Issue Management**: Create, update, and delete issues with rich metadata
- **Multiple Views**: Switch between List, Board (Kanban), and Calendar views
- **Drag & Drop**: Intuitive drag-and-drop functionality in board view
- **Real-time Filtering**: Search and filter issues by status, priority, and text
- **Project Organization**: Organize issues across multiple projects
- **Labels & Tags**: Categorize issues with colored labels

### 🎨 UI/UX Features
- **Modern Design**: Clean, minimalist interface inspired by Linear
- **Responsive Layout**: Works seamlessly on desktop and tablet devices
- **Keyboard Shortcuts**: Quick actions with keyboard shortcuts (⌘K for search)
- **Smooth Animations**: Polished interactions with Framer Motion
- **Dark Mode Ready**: Structure prepared for dark mode implementation

### 📊 Issue Properties
- **Status**: Backlog, To Do, In Progress, Done, Cancelled
- **Priority**: Urgent, High, Medium, Low, None
- **Assignees**: Assign issues to team members
- **Due Dates**: Track deadlines
- **Story Points**: Estimate effort with story points
- **Labels**: Custom labels with colors

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **UI Components**: Radix UI
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Drag & Drop**: @dnd-kit
- **Date Handling**: date-fns

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd linear-clone
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
linear-clone/
├── app/                  # Next.js app router pages
│   ├── layout.tsx       # Root layout with sidebar
│   ├── page.tsx         # Home page (redirects to my-issues)
│   ├── my-issues/       # Main issues view
│   ├── inbox/           # Inbox page
│   └── views/           # Custom views page
├── components/          # React components
│   ├── sidebar.tsx      # Navigation sidebar
│   ├── header.tsx       # Page header with filters
│   ├── issue-list.tsx   # List view component
│   ├── issue-board.tsx  # Kanban board view
│   └── issue-card.tsx   # Issue card for board view
├── lib/                 # Utilities and store
│   ├── store.ts         # Zustand state management
│   └── utils.ts         # Helper functions
└── public/              # Static assets
```

## Usage

### Creating Issues
1. Click the "New Issue" button in the header
2. Fill in issue details (title, description, priority, etc.)
3. Assign to team members and add labels
4. Set due dates and story points

### Managing Issues
- **Change Status**: Click on the status icon to update
- **Set Priority**: Click on the priority indicator
- **Quick Actions**: Use the three-dot menu for more options
- **Bulk Operations**: Select multiple issues for batch updates

### Views
- **List View**: Traditional list with expandable details
- **Board View**: Kanban-style board with drag-and-drop
- **Calendar View**: Timeline view (coming soon)

### Filtering
- Use the search bar to find issues by title or ID
- Apply filters for status and priority
- Combine multiple filters for precise results

## Development

### Available Scripts

```bash
# Development
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npm run type-check
```

### Adding New Features

1. **New Issue Properties**: Update the `Issue` interface in `lib/store.ts`
2. **New Views**: Create components in `components/` and add routes in `app/`
3. **New Filters**: Extend the filter logic in `lib/store.ts` and `components/header.tsx`

## Sample Data

The application comes with pre-populated sample data including:
- 3 Projects (Web Platform, Mobile App, API Development)
- 8 Sample issues with various statuses and priorities
- 5 Labels (Bug, Feature, Enhancement, Documentation, Performance)
- Sample user profile

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Real-time collaboration with WebSockets
- [ ] Calendar view implementation
- [ ] Issue comments and activity feed
- [ ] File attachments
- [ ] Time tracking
- [ ] Advanced reporting and analytics
- [ ] Mobile responsive design
- [ ] Dark mode support
- [ ] Keyboard navigation
- [ ] Issue templates
- [ ] Webhooks and integrations
- [ ] Export functionality (CSV, JSON)
- [ ] Bulk operations
- [ ] Custom fields

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes and is not affiliated with Linear.

## Acknowledgments

- Design inspiration from [Linear](https://linear.app)
- Icons from [Lucide](https://lucide.dev)
- UI components from [Radix UI](https://radix-ui.com)