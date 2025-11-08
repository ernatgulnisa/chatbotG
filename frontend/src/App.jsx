import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'

// Layouts
import AuthLayout from './layouts/AuthLayout'
import DashboardLayout from './layouts/DashboardLayout'

// Auth Pages
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'

// Dashboard Pages
import Dashboard from './pages/dashboard/Dashboard'
import Bots from './pages/bots/Bots'
import BotBuilder from './pages/BotBuilder'
import Customers from './pages/customers/Customers'
import Conversations from './pages/conversations/Conversations'
import Deals from './pages/deals/Deals'
import Broadcasts from './pages/broadcasts/Broadcasts'
import Settings from './pages/settings/Settings'
import WhatsAppSettings from './pages/WhatsAppSettings'
import WhatsAppSetupWizard from './pages/WhatsAppSetupWizard'
import LiveChat from './pages/LiveChat'

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" />} />
        <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} />
      </Route>

      {/* Dashboard Routes */}
      <Route element={isAuthenticated ? <DashboardLayout /> : <Navigate to="/login" />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/bots" element={<Bots />} />
        <Route path="/bots/:id/builder" element={<BotBuilder />} />
        <Route path="/customers" element={<Customers />} />
        <Route path="/conversations" element={<Conversations />} />
        <Route path="/live-chat" element={<LiveChat />} />
        <Route path="/deals" element={<Deals />} />
        <Route path="/broadcasts" element={<Broadcasts />} />
        <Route path="/whatsapp" element={<WhatsAppSettings />} />
        <Route path="/whatsapp/setup" element={<WhatsAppSetupWizard />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      {/* Redirect root to dashboard */}
      <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
      
      {/* 404 */}
      <Route path="*" element={<div className="flex items-center justify-center h-screen"><h1 className="text-2xl">404 - Page Not Found</h1></div>} />
    </Routes>
  )
}

export default App
