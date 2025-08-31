import React, { useEffect, useState } from 'react';
import apiClient from '../api/apiClient';

const QualityReportsPage = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchReports = async () => {
            try {
                // Assuming an API endpoint for quality reports
                const response = await apiClient.get('/quality/reports');
                setReports(response.data);
                setLoading(false);
            } catch (err) {
                setError(err);
                setLoading(false);
            }
        };

        fetchReports();
    }, []);

    if (loading) return <div>Loading quality reports...</div>;
    if (error) return <div>Error loading reports: {error.message}</div>;

    return (
        <div className="quality-reports-page">
            <h1>تقارير الجودة</h1>
            {reports.length === 0 ? (
                <p>لا توجد تقارير جودة متاحة حاليًا.</p>
            ) : (
                <ul>
                    {reports.map(report => (
                        <li key={report.id}>
                            <h3>{report.title}</h3>
                            <p>{report.description}</p>
                            <p>تاريخ الإنشاء: {new Date(report.created_at).toLocaleDateString()}</p>
                            {/* Add more report details as needed */}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default QualityReportsPage;


