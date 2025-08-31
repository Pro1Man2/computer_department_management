import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Layout = ({ children }) => {
    const { logout } = useAuth();

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-gray-800 text-white flex flex-col">
                <div className="p-4 text-xl font-bold border-b border-gray-700">
                    إدارة القسم
                </div>
                <nav className="flex-1 px-2 py-4 space-y-2">
                    <Link to="/dashboard" className="block px-4 py-2 rounded hover:bg-gray-700">
                        لوحة التحكم
                    </Link>
                    <Link to="/quality-reports" className="block px-4 py-2 rounded hover:bg-gray-700">
                        تقارير الجودة
                    </Link>
                    <Link to="/initiatives" className="block px-4 py-2 rounded hover:bg-gray-700">
                        المبادرات
                    </Link>
                    <Link to="/behavior-management" className="block px-4 py-2 rounded hover:bg-gray-700">
                        إدارة السلوكيات
                    </Link>
                    <Link to="/surveys" className="block px-4 py-2 rounded hover:bg-gray-700">
                        الاستبيانات
                    </Link>
                </nav>
                <div className="p-4 border-t border-gray-700">
                    <button
                        onClick={logout}
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                    >
                        تسجيل الخروج
                    </button>
                </div>
            </aside>

            {/* Main content */}
            <main className="flex-1 overflow-y-auto p-6">
                {children}
            </main>
        </div>
    );
};

export default Layout;


