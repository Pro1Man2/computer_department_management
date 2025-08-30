import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  // التحقق من صحة التوكن عند تحميل التطبيق
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token')
      if (storedToken) {
        try {
          const response = await fetch('/api/profile', {
            headers: {
              'Authorization': `Bearer ${storedToken}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (response.ok) {
            const data = await response.json()
            setUser(data.user)
            setToken(storedToken)
          } else {
            // التوكن غير صالح
            localStorage.removeItem('token')
            setToken(null)
          }
        } catch (error) {
          console.error('خطأ في التحقق من المصادقة:', error)
          localStorage.removeItem('token')
          setToken(null)
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (username, password) => {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json()

      if (response.ok) {
        setUser(data.user)
        setToken(data.token)
        localStorage.setItem('token', data.token)
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch (error) {
      console.error('خطأ في تسجيل الدخول:', error)
      return { success: false, message: 'خطأ في الاتصال بالخادم' }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
  }

  const updateProfile = async (profileData) => {
    try {
      const response = await fetch('/api/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      })

      const data = await response.json()

      if (response.ok) {
        setUser(data.user)
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch (error) {
      console.error('خطأ في تحديث الملف الشخصي:', error)
      return { success: false, message: 'خطأ في الاتصال بالخادم' }
    }
  }

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await fetch('/api/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      })

      const data = await response.json()

      if (response.ok) {
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch (error) {
      console.error('خطأ في تغيير كلمة المرور:', error)
      return { success: false, message: 'خطأ في الاتصال بالخادم' }
    }
  }

  // دالة مساعدة للتحقق من الصلاحيات
  const hasPermission = (permission) => {
    if (!user || !user.permissions) return false
    return user.permissions.includes(permission)
  }

  // دالة مساعدة للتحقق من الأدوار
  const hasRole = (role) => {
    if (!user || !user.roles) return false
    return user.roles.includes(role)
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    updateProfile,
    changePassword,
    hasPermission,
    hasRole
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

