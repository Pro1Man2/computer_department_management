import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Eye, EyeOff, LogIn, Monitor } from 'lucide-react'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (!username || !password) {
      setError('يرجى إدخال اسم المستخدم وكلمة المرور')
      setLoading(false)
      return
    }

    const result = await login(username, password)
    
    if (!result.success) {
      setError(result.message)
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md">
        {/* شعار المؤسسة */}
        <div className="text-center mb-8">
          <div className="mx-auto w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <Monitor className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            منصة إدارة قسم تقنية الحاسب
          </h1>
          <p className="text-gray-600">
            المؤسسة العامة للتدريب التقني والمهني
          </p>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">تسجيل الدخول</CardTitle>
            <CardDescription>
              أدخل بياناتك للوصول إلى المنصة
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="username">اسم المستخدم</Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="أدخل اسم المستخدم"
                  disabled={loading}
                  className="text-right"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">كلمة المرور</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="أدخل كلمة المرور"
                    disabled={loading}
                    className="text-right pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    disabled={loading}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
              
              <Button 
                type="submit" 
                className="w-full" 
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    جاري تسجيل الدخول...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <LogIn className="w-4 h-4" />
                    تسجيل الدخول
                  </div>
                )}
              </Button>
            </form>
            
            <div className="mt-6 text-center text-sm text-gray-600">
              <p>هل تواجه مشكلة في تسجيل الدخول؟</p>
              <p className="mt-1">تواصل مع مدير النظام</p>
            </div>
          </CardContent>
        </Card>
        
        <div className="mt-8 text-center text-xs text-gray-500">
          <p>© 2024 المؤسسة العامة للتدريب التقني والمهني</p>
          <p>جميع الحقوق محفوظة</p>
        </div>
      </div>
    </div>
  )
}

