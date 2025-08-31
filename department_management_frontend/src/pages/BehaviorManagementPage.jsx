import React, { useEffect, useState } from 'react';
import apiClient from '../api/apiClient';

const BehaviorManagementPage = () => {
    const [behaviorRecords, setBehaviorRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchBehaviorRecords = async () => {
            try {
                const response = await apiClient.get('/behavior_records');
                setBehaviorRecords(response.data);
                setLoading(false);
            } catch (err) {
                setError(err);
                setLoading(false);
            }
        };

        fetchBehaviorRecords();
    }, []);

    if (loading) return <div>Loading behavior records...</div>;
    if (error) return <div>Error loading records: {error.message}</div>;

    return (
        <div className="behavior-management-page">
            <h1>إدارة السلوكيات</h1>
            {behaviorRecords.length === 0 ? (
                <p>لا توجد سجلات سلوك متاحة حاليًا.</p>
            ) : (
                <ul>
                    {behaviorRecords.map(record => (
                        <li key={record.id}>
                            <p>المتدرب ID: {record.trainee_id}</p>
                            <p>نوع السلوك: {record.behavior_type}</p>
                            <p>الوصف: {record.description}</p>
                            <p>تاريخ التسجيل: {new Date(record.date_recorded).toLocaleDateString()}</p>
                            <p>سجل بواسطة المدرب ID: {record.recorded_by_trainer_id}</p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default BehaviorManagementPage;


