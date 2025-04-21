import React, { useEffect, useState } from 'react';
import axios from 'axios';

const HomeView = () => {
    const [transcripts, setTranscripts] = useState([]);

    useEffect(() => {
        axios.get('/api/transcripts/')
            .then(response => {
                console.log('Fetched transcripts:', response.data);
                setTranscripts(response.data);
            })
            .catch(error => {
                console.error('Error fetching transcripts:', error);
            });
    }, []);

    return (
        <div>
            <h1>Home Page</h1>
            <h2>Interview Transcripts</h2>
            {transcripts.length === 0 ? (
                <p>No transcripts available.</p>
            ) : (
                <ul>
                    {transcripts.map((transcript, index) => (
                        <li key={index}>
                            <strong>Candidate:</strong> {transcript.interview.candidate} <br />
                            <strong>Job Title:</strong> {transcript.interview.job_title} <br />
                            <strong>Question:</strong> {transcript.question} <br />
                            <strong>Answer:</strong> {transcript.answer} <br />
                            <strong>Category:</strong> {transcript.category}
                            <hr />
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default HomeView;
