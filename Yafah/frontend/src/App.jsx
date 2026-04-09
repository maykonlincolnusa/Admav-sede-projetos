import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Cadastro from './pages/Cadastro';
import Admin from './pages/Admin';
import DashboardLayout from './components/Layout/DashboardLayout';
import Home from './pages/Dashboard/Home';
import Chat from './pages/Dashboard/Chat';
import Instagram from './pages/Dashboard/Instagram';
import TikTok from './pages/Dashboard/TikTok';
import Site from './pages/Dashboard/Site';
import Knowledge from './pages/Dashboard/Knowledge';
import Finance from './pages/Dashboard/Finance';

function PrivateRoute({ children }) {
  // Chamada de Desenvolvimento — Auto login localmente
  const user = JSON.parse(localStorage.getItem('yafa_user') || 'null');
  const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  
  if (!user && isDev) {
    localStorage.setItem('yafa_user', JSON.stringify({ nome: 'Empreendedora VIP', id: 'dev_mode', status: 'ativo' }));
    return children;
  }
  
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/cadastro" element={<Cadastro />} />
        <Route path="/admin" element={<Admin />} />
        
        <Route path="/dashboard" element={<PrivateRoute><DashboardLayout /></PrivateRoute>}>
          <Route index element={<Home />} />
          <Route path="chat" element={<Chat />} />
          <Route path="instagram" element={<Instagram />} />
          <Route path="tiktok" element={<TikTok />} />
          <Route path="site" element={<Site />} />
<Route path="knowledge" element={<Knowledge />} />
<Route path="finance" element={<Finance />} />
        </Route>
        
        {/* Redirect unknown routes */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
