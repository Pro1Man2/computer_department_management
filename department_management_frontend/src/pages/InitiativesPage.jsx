import React, { useEffect, useState } from 'react';
import apiClient from '../api/apiClient';

const InitiativesPage = () => {
    const [initiatives, setInitiatives] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchInitiatives = async () => {
            try {
                const response = await apiClient.get('/initiatives');
                setInitiatives(response.data);
                setLoading(false);
            } catch (err) {
                setError(err);
                setLoading(false);
            }
        };

        fetchInitiatives();
    }, []);

    if (loading) return <div>Loading initiatives...</div>;
    if (error) return <div>Error loading initiatives: {error.message}</div>;

    return (
        <div className="initiatives-page">
            <h1>إدارة المبادرات</h1>
            {initiatives.length === 0 ? (
                <p>لا توجد مبادرات متاحة حاليًا.</p>
            ) : (
                <ul>
                    {initiatives.map(initiative => (
                        <li key={initiative.id}>
                            <h3>{initiative.title}</h3>
                            <p>{initiative.description}</p>
                            <p>الحالة: {initiative.status}</p>
                            {/* Add more initiative details as needed */}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default InitiativesPage;


