import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext';
import { Layout } from './components/Layout';
import { PrivateRoute } from './components/PrivateRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { HomePage } from './pages/HomePage';
import { ArticlesPage } from './pages/ArticlesPage';
import { ArticleDetailPage } from './pages/ArticleDetailPage';
import { ArticleEditPage } from './pages/ArticleEditPage';
import { PapersPage } from './pages/PapersPage';
import { PaperDetailPage } from './pages/PaperDetailPage';
import { PaperEditPage } from './pages/PaperEditPage';
import { PaperCreatePage } from './pages/PaperCreatePage';
import { ProfilePage } from './pages/ProfilePage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected routes */}
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Layout />
                </PrivateRoute>
              }
            >
              <Route index element={<HomePage />} />
              <Route path="articles" element={<ArticlesPage />} />
              <Route path="articles/:id" element={<ArticleDetailPage />} />
              <Route path="articles/new" element={<ArticleEditPage />} />
              <Route path="articles/:id/edit" element={<ArticleEditPage />} />
              <Route path="papers" element={<PapersPage />} />
              <Route path="papers/:id" element={<PaperDetailPage />} />
              <Route path="papers/new" element={<PaperCreatePage />} />
              <Route path="papers/:id/edit" element={<PaperEditPage />} />
              <Route path="profile" element={<ProfilePage />} />
            </Route>

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </AuthProvider>
    </Router>
  );
}

export default App;
