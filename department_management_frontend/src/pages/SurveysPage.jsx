import React, { useEffect, useState } from 'react';
import apiClient from '../api/apiClient';

const SurveysPage = () => {
    const [surveys, setSurveys] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchSurveys = async () => {
            try {
                const response = await apiClient.get('/surveys');
                setSurveys(response.data);
                setLoading(false);
            } catch (err) {
                setError(err);
                setLoading(false);
            }
        };

        fetchSurveys();
    }, []);

    if (loading) return <div>Loading surveys...</div>;
    if (error) return <div>Error loading surveys: {error.message}</div>;

    return (
        <div className="surveys-page">
            <h1>إدارة الاستبيانات</h1>
            {surveys.length === 0 ? (
                <p>لا توجد استبيانات متاحة حاليًا.</p>
            ) : (
                <ul>
                    {surveys.map(survey => (
                        <li key={survey.id}>
                            <h3>{survey.title}</h3>
                            <p>{survey.description}</p>
                            <p>تاريخ الإنشاء: {new Date(survey.created_at).toLocaleDateString()}</p>
                            <p>نشط: {survey.is_active ? 'نعم' : 'لا'}</p>
                            {/* Add link to view/respond to survey */}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default SurveysPage;


