import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';



const HomeView = () => {
    const [interviews, setInterviews] = useState([]);
    const [selectedInterviewId, setSelectedInterviewId] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        axios.get('/api/interviews/')
            .then(response => {
                setInterviews(response.data);
            })
            .catch(error => {
                console.error('Error fetching interviews:', error);
            });
    }, []);

    const handleSelect = (e) => {
        const id = e.target.value;
        setSelectedInterviewId(id);
        if (id) {
            navigate(`/report/${id}`);
        }
    };

    return (
        <div>
            <h1>Home Page</h1>
            <p>Select an Interview to View Report:</p>
    
            {interviews.length === 0 ? (
                <p>Loading or no interviews found...</p>
            ) : (
                <select value={selectedInterviewId} onChange={handleSelect}>
                    <option value="">-- Select Interview --</option>
                    {interviews.map((interview) => (
                        <option key={interview.id} value={interview.id}>
                            {interview.candidate_name} - {interview.job_title}
                        </option>
                    ))}
                </select>
            )}
        </div>
    );
};

export default HomeView;
