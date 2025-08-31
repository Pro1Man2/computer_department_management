import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { Toaster } from '@/components/ui/toaster'
import './App.css'

// استيراد المكونات
import LoginPage from './components/auth/LoginPage'
import DashboardPage from './pages/DashboardPage'
import QualityReportsPage from './pages/QualityReportsPage'
import InitiativesPage from './pages/InitiativesPage'
import BehaviorManagementPage from './pages/BehaviorManagementPage'
import SurveysPage from './pages/SurveysPage'
import Layout from './components/layout/Layout'
import { AuthProvider, useAuth } from './contexts/AuthContext'

// مكون حماية المسارات
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

// مكون التطبيق الرئيسي
function AppContent() {
  const { user } = useAuth()
  
  return (
    <Router>
      <div className="min-h-screen bg-gray-50" dir="rtl">
        <Routes>
          <Route 
            path="/login" 
            element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />} 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/quality-reports" 
            element={
              <ProtectedRoute>
                <Layout>
                  <QualityReportsPage />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/initiatives" 
            element={
              <ProtectedRoute>
                <Layout>
                  <InitiativesPage />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/behavior-management" 
            element={
              <ProtectedRoute>
                <Layout>
                  <BehaviorManagementPage />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/surveys" 
            element={
              <ProtectedRoute>
                <Layout>
                  <SurveysPage />
                </Layout>
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/" 
            element={<Navigate to="/dashboard" replace />} 
          />
        </Routes>
        <Toaster />
      </div>
    </Router>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App


