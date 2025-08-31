# Simple Counter App

This is a simple full stack application that allows users to increment a count variable by pressing a button. The application consists of a backend built with Express and a frontend built with React.

## Project Structure

```
simple-counter-app
├── backend
│   ├── server.js
│   └── package.json
├── frontend
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
└── README.md
```

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm (Node Package Manager)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install the dependencies:
   ```
   npm install
   ```

3. Start the backend server:
   ```
   npm start
   ```

   The server will run on `http://localhost:5000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the dependencies:
   ```
   npm install
   ```

3. Start the frontend application:
   ```
   npm start
   ```

   The application will run on `http://localhost:3000`.

### Usage

- Open your browser and go to `http://localhost:3000`.
- You will see a button in the middle of the screen. Each time you press the button, the count will increment by 1.

## License

This project is licensed under the MIT License.