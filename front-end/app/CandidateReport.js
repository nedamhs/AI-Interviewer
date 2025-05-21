import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

/* each card */ 
const cardStyle = {
    backgroundColor: '#fff',
    borderRadius: '8px',
    boxShadow: '0 4px 24px rgba(77, 7, 239, 0.1)',
    padding: '16px',
    marginBottom: '20px',
    maxWidth: '800px',
};

/* top banner */
const bannerHeader = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-start',
    backgroundColor: '#FFFFFF',
    color: 'white',
    padding: '8px 24px',            
    width: '100%',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    height: '60px',                
};

/* pairwise logo */ 
const bannerLogo = {
    width: '120px',                
    height: 'auto',
    marginRight: '16px',
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
    /*alignItems: 'center', */ 
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

/* box with scores and progress bars */ 
const progressBarContainer = {
    width: '100%',
    backgroundColor: '#eee',
    borderRadius: '5px',
    height: '10px',
    marginTop: '4px',
    marginBottom: '12px',
};

const getScoreColor = (score) => {
    if (score < 5) return '#FF4136';     // Red
    if (score < 8.0) return '#FF851B';   // Orange
    return '#2ECC40';                    // Green
};

const getProgressBarStyle = (score) => ({
    width: `${score * 10}%`,
    backgroundColor: getScoreColor(score),
    height: '100%',
    borderRadius: '5px',
});


const CandidateReport = () => {
    const { interviewId } = useParams();
    const [scores, setScores] = useState([]);
    const [transcript, setTranscript] = useState([]);
    const [showTranscript, setShowTranscript] = useState(false);
    const [summary, setSummary] = useState('');
    const [finalScore, setFinalScore] = useState(null);
    const [candidateName, setCandidateName] = useState('');
    const [jobTitle, setJobTitle] = useState('');
    const [report, setReport] = useState(null);



    useEffect(() => {
        axios.get(`/api/interview/${interviewId}/details/`)
            .then(res => {setSummary(res.data.summary);
                           setFinalScore(res.data.final_score);
                           setCandidateName(res.data.candidate_name);
                           setJobTitle(res.data.job_title);})
            .catch(err => console.error('Error fetching interview details:', err));

        axios.get(`/api/interviews/${interviewId}/report/`)
            .then(res => setReport(res.data))
            .catch(err => console.error('Error fetching interview report:', err));
    
        axios.get(`/api/scores/${interviewId}`)
            .then(res => setScores(res.data))
            .catch(err => console.error('Error fetching scores:', err));
    
        axios.get(`/api/transcripts/?interview_id=${interviewId}`)
            .then(res => setTranscript(res.data))
            .catch(err => console.error('Error fetching transcript:', err));
    }, [interviewId]);
    

    return (
        <div>
            {/* banner and logo */}
            <div style={bannerHeader}>
                    <img 
                        src="/static/logo.png" 
                        alt="Company Logo" 
                        style={bannerLogo}
                    />
            </div>
    
            {/* page */}
            <div style={pageStyle}>

                {/* candidate - job detail  */}
                <h2>Candidate Report for Interview ID: {interviewId}</h2>
                <p><strong>Candidate:</strong> {candidateName}</p>
                <p><strong>Job Title:</strong> {jobTitle}</p>

                {/* box with scores - progress bars  */}
                <div style={{...cardStyle, backgroundColor: '#f9f9f9', padding: '20px', maxWidth: '500px', width: '90%', margin: '30px 0 30px 40px',  borderRadius: '12px', boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)'}}>
                        <h2 style={{ marginBottom: '20px', textAlign: 'center' }}>📊 Candidate Fit Overview</h2>

                        {/* final score  */}
                        <div style={{ marginBottom: '28px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '6px' }}>Final Score</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <div style={{ ...progressBarContainer, flex: 1 }}>
                                    <div style={getProgressBarStyle(finalScore)} />
                                </div>
                                <span style={{ color: getScoreColor(finalScore), fontWeight: 'bold', minWidth: '50px' }}>
                                    {finalScore !== null ? `${finalScore}/10` : 'N/A'}
                                </span>
                            </div>
                        </div>

                        {/* category score(s) */}
                        <div>
                            <div style={{ fontWeight: 'bold', marginBottom: '10px' }}>Category Scores</div>
                            {scores.map((item, idx) => (
                                <div key={idx} style={{ marginBottom: '16px' }}>
                                    <div style={{ marginBottom: '4px' }}>{item.category}</div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <div style={{ ...progressBarContainer, flex: 1 }}>
                                            <div style={getProgressBarStyle(item.score)} />
                                        </div>
                                        <span style={{ color: getScoreColor(item.score), fontWeight: 'bold', minWidth: '50px' }}>
                                            {item.score}/10
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                </div>


             {report && ( <>
                             {/* resume summary */}
                            <div style={cardStyle}>
                                <h3>📄 Resume Summary</h3>
                                <p>{report.resume_summary}</p>
                            </div>

                            {/* interveiw summary */}
                            <div style={cardStyle}>
                                <h3>🗣️ Interview Summary</h3>
                                <p>{report.interview_summary}</p>
                            </div>

                            {/* rrecommendation part  */}
                            <div style={cardStyle}>
                                <h3>{report.recommendation === "recommended" ? "✅ Recommended" : "❌ Not Recommended"}</h3>
                                <p><strong>Reason:</strong> {report.reason}</p>
                            </div>

                            {/* 5 bulletpoints  */}
                            <div style={cardStyle}>
                                <h3>🔍 Key Insights</h3>
                                <ul>
                                    {report.key_insights.map((insight, idx) => (
                                        <li key={idx}>
                                            <strong>{insight.label === "good" ? "✅" : "❌"} </strong>
                                            {insight.text}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </>
                    )}


                {/* all category scoring & details  */}
                {scores.map((item, idx) => (
                    <div style={cardStyle} key={idx}>
                        <h3>{item.category}</h3>
                        <p style={{ ...scoreStyle, color: getScoreColor(item.score) }}>
                            Score: {item.score}/10 </p>
                        <p style={reasonStyle}>Reason: {item.reason}</p>
                    </div>
                ))}
    
                {/* transcript expanising button  */}
                <button 
                  onClick={() => setShowTranscript(!showTranscript)}
                  style={buttonStyle}  
                  >
                  {showTranscript ? 'Hide Transcript' : 'View Transcript'}
                </button>

    
                {/* transcript Q & A  */}
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