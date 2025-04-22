import React, { useEffect, useState } from 'react';
import axios from 'axios';

const CandidateReport = ({ interviewId }) => {
    const [scores, setScores] = useState([]);
    const [transcript, setTranscript] = useState([]);
    const [showTranscript, setShowTranscript] = useState(false);

    useEffect(() => {
        // axios.get(`/api/scores/${interviewId}`)
        axios.get(`/api/transcripts/?interview_id=${interviewId}`)
            .then(res => setScores(res.data))
            .catch(err => console.error('Error fetching scores:', err));

        axios.get(`/api/transcripts/?interview_id=${interviewId}`)
            .then(res => setTranscript(res.data))
            .catch(err => console.error('Error fetching transcript:', err));
    }, [interviewId]);

    return (
        <div>
            <h2>Candidate Report for Interview ID: {interviewId}</h2>

            <h3>Scores:</h3>
            <ul>
                {scores.map((item, idx) => (
                    <li key={idx}>
                        <strong>{item.category}</strong>: {item.score} <br />
                        <em>Reason:</em> {item.reason}
                    </li>
                ))}
            </ul>

            <button onClick={() => setShowTranscript(!showTranscript)}>
                {showTranscript ? 'Hide Transcript' : 'View Transcript'}
            </button>

            {showTranscript && (
                <div>
                    {transcript.map((t, idx) => (
                        <div key={idx}>
                            <strong>Q:</strong> {t.question} <br />
                            <strong>A:</strong> {t.answer} <br />
                            <strong>Category:</strong> {t.category}
                            <hr />
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default CandidateReport;
