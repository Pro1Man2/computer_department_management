import React, { useEffect, useState } from 'react';
import apiClient from '../api/apiClient';

const DashboardPage = () => {
    const [kpis, setKpis] = useState({});
    const [statistics, setStatistics] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const kpisResponse = await apiClient.get('/dashboard/kpis');
                setKpis(kpisResponse.data);

                const statsResponse = await apiClient.get('/dashboard/statistics');
                setStatistics(statsResponse.data);

                setLoading(false);
            } catch (err) {
                setError(err);
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div>Loading dashboard data...</div>;
    if (error) return <div>Error loading dashboard: {error.message}</div>;

    return (
        <div className="dashboard-page">
            <h1>لوحة التحكم الرئيسية</h1>
            <section className="kpis-section">
                <h2>مؤشرات الأداء الرئيسية (KPIs)</h2>
                <p>نسبة التخرج: {kpis.graduation_rate}</p>
                <p>نسبة النجاح في المقررات الحرجة: {kpis.success_rate_critical_courses}</p>
                <p>رضا المدربين: {kpis.trainer_satisfaction}</p>
                <p>رضا المتدربين: {kpis.trainee_satisfaction}</p>
                <p>حوادث السلوك شهريًا: {kpis.behavior_incidents_per_month}</p>
            </section>

            <section className="statistics-section">
                <h2>إحصائيات عامة</h2>
                <p>إجمالي عدد المتدربين: {statistics.total_trainees}</p>
                <p>إجمالي عدد المدربين: {statistics.total_trainers}</p>
                <h3>المتدربون حسب التخصص:</h3>
                <ul>
                    {Object.entries(statistics.trainees_by_specialization || {}).map(([specialization, count]) => (
                        <li key={specialization}>{specialization}: {count}</li>
                    ))}
                </ul>
                <h3>التحاق المقررات الحرجة:</h3>
                <ul>
                    {Object.entries(statistics.critical_courses_enrollment || {}).map(([course, count]) => (
                        <li key={course}>{course}: {count}</li>
                    ))}
                </ul>
            </section>
        </div>
    );
};

export default DashboardPage;


