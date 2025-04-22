import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';


const cardStyle = {
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 24px rgba(77, 7, 239, 0.1)',
    padding: '16px',
    marginBottom: '20px',
    maxWidth: '800px',
};


const scoreStyle = {
    fontWeight: 'bold',
    color: '#007BFF',
};

const reasonStyle = {
    fontStyle: 'italic',
    marginBottom: '10px',
};

const transcriptStyle = {
    marginTop: '20px',
    padding: '16px',
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 24px rgba(77, 7, 239, 0.1)',
    maxWidth: '1000px',
};

const pageStyle = {
    backgroundColor: '#f5f5f5',
    fontFamily: 'Arial, sans-serif',
    padding: '20px',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',  
};

const buttonStyle = {
    backgroundColor: '#6007ef',  
    color: '#fff',              
    fontSize: '16px',           
    padding: '10px 20px',       
    border: 'none',              
    borderRadius: '0',           
    cursor: 'pointer',           
    marginTop: '20px',          
};

// different score colors based on score
const getScoreColor = (score) => {
    if (score < 5) return '#FF4136';     // Red
    if (score < 8.0) return '#FF851B';   // Orange
    return '#2ECC40';                     // Green
};

const CandidateReport = () => {
    const { interviewId } = useParams();
    const [scores, setScores] = useState([]);
    const [transcript, setTranscript] = useState([]);
    const [showTranscript, setShowTranscript] = useState(false);

    useEffect(() => {
        axios.get(`/api/scores/${interviewId}`)
            .then(res => setScores(res.data))
            .catch(err => console.error('Error fetching scores:', err));

        axios.get(`/api/transcripts/?interview_id=${interviewId}`)
            .then(res => setTranscript(res.data))
            .catch(err => console.error('Error fetching transcript:', err));
    }, [interviewId]);

    return (
        <div>
            <img 
                src="/static/logo.png" 
                alt="Company Logo" 
                style={{ width: '300px', margin: '20px 0 20px 20px', float: 'left' }}
            />
    
            <div style={pageStyle}>
                <h2>Candidate Report for Interview ID: {interviewId}</h2>
    
                {scores.map((item, idx) => (
                    <div style={cardStyle} key={idx}>
                        <h3>{item.category}</h3>
                        <p style={{ ...scoreStyle, color: getScoreColor(item.score) }}>
                            Score: {item.score}/10 </p>
                        <p style={reasonStyle}>Reason: {item.reason}</p>
                    </div>
                ))}
    
                <button 
                  onClick={() => setShowTranscript(!showTranscript)}
                  style={buttonStyle}  
                  >
                  {showTranscript ? 'Hide Transcript' : 'View Transcript'}
                </button>

    
                {showTranscript && (
                    <div style={transcriptStyle}>
                        <h3>Full Transcript</h3>
                        {transcript.map((t, i) => (
                            <div key={i}>
                                <strong>Q:</strong> {t.question} <br />
                                <strong>A:</strong> {t.answer} <br /><br /> 
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );

};

export default CandidateReport;