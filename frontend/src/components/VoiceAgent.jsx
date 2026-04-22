import React, { useState, useEffect, useRef } from 'react';

export default function VoiceAgent({ onMetricsUpdate }) {
  const [callState, setCallState] = useState('offline'); // offline, active
  const [status, setStatus] = useState('idle'); // idle, listening, processing, speaking
  const [logs, setLogs] = useState([]);
  
  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);
  const streamRef = useRef(null);
  
  const pcmDataRef = useRef([]);
  const isSpeakingRef = useRef(false);
  const silenceStartRef = useRef(0);
  const consecutiveSpeechFramesRef = useRef(0);
  const currentAudioOutRef = useRef(null); 
  const SILENCE_THRESHOLD = 2500; 
  const ENERGY_THRESHOLD = 0.05; 
  const MIN_FRAMES_TO_SEND = 10; 

  const [sessionId] = useState(() => `session_${Math.random().toString(36).substring(7)}`);
  
  const addLog = (msg, type = "system") => {
    setLogs(prev => [...prev, { text: msg, type }]);
  };

  const startCall = async () => {
    if (callState === 'active') return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 48000 });
      audioContextRef.current = audioCtx;
      
      const host = window.location.hostname === "localhost" ? "127.0.0.1:8000" : window.location.host;
      wsRef.current = new WebSocket(`ws://${host}/ws/voice/${sessionId}`);

      wsRef.current.onopen = () => {
        addLog("Telecall Established.", "success");
        setCallState('active');
        setStatus('listening');
        startContinuousRecording(stream, audioCtx);
      };
      
      wsRef.current.onmessage = async (event) => {
        if (typeof event.data === "string") {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "metrics" && onMetricsUpdate) {
              onMetricsUpdate(data);
            }
          } catch(e) {}
        } else {
          // Audio Blob received
          setStatus('speaking');
          addLog("Agent speaking...", "system");
          try {
            const audioBlob = new Blob([event.data], { type: 'audio/mp3' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            currentAudioOutRef.current = audio;
            
            audio.onended = () => {
               setStatus('listening');
               currentAudioOutRef.current = null;
            };
            audio.play();
          } catch (err) {
            addLog("Audio Playback Error: " + err.message, "error");
            setStatus('listening');
          }
        }
      };

      wsRef.current.onclose = () => {
        addLog("Telecall Disconnected.", "error");
        endCall();
      };

    } catch (e) {
      addLog("Microphone Error: " + e.message, "error");
    }
  };

  const endCall = () => {
    if (wsRef.current) wsRef.current.close();
    if (processorRef.current) processorRef.current.disconnect();
    if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
    if (audioContextRef.current) audioContextRef.current.close();
    if (currentAudioOutRef.current) {
        currentAudioOutRef.current.pause();
        currentAudioOutRef.current = null;
    }
    setCallState('offline');
    setStatus('idle');
  };

  const startContinuousRecording = (stream, audioCtx) => {
    const inputSource = audioCtx.createMediaStreamSource(stream);
    processorRef.current = audioCtx.createScriptProcessor(4096, 1, 1);
    
    pcmDataRef.current = [];
    isSpeakingRef.current = false;
    consecutiveSpeechFramesRef.current = 0;
    silenceStartRef.current = Date.now();

    processorRef.current.onaudioprocess = (e) => {
      const inputData = e.inputBuffer.getChannelData(0);
      let sumSquares = 0;
      
      const int16Array = new Int16Array(inputData.length);
      for (let i = 0; i < inputData.length; i++) {
        let s = Math.max(-1, Math.min(1, inputData[i]));
        int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        sumSquares += inputData[i] * inputData[i];
      }
      
      const rms = Math.sqrt(sumSquares / inputData.length);
      
      // Barge-in Check with Debounce
      if (rms > ENERGY_THRESHOLD) {
         consecutiveSpeechFramesRef.current++;
         if (consecutiveSpeechFramesRef.current > 3) {
             isSpeakingRef.current = true;
             silenceStartRef.current = Date.now();
             
             if (currentAudioOutRef.current && !currentAudioOutRef.current.paused) {
                 currentAudioOutRef.current.pause();
                 addLog("Barge-in: Interrupting agent playback", "error");
                 setStatus('listening');
             }
         }
      } else {
         consecutiveSpeechFramesRef.current = 0;
      }

      // Collect audio if speaking happened
      if (isSpeakingRef.current) {
         pcmDataRef.current.push(int16Array);
      }

      // Silence detection
      if (isSpeakingRef.current && rms < ENERGY_THRESHOLD) {
         if (Date.now() - silenceStartRef.current > SILENCE_THRESHOLD) {
             const collected = pcmDataRef.current;
             if (collected.length > MIN_FRAMES_TO_SEND) { 
                dispatchAudioChunk(collected);
             } else {
                addLog("Discarded noise fragment.", "system");
                setStatus('listening');
             }
             pcmDataRef.current = [];
             isSpeakingRef.current = false;
         }
      }
    };

    inputSource.connect(processorRef.current);
    processorRef.current.connect(audioCtx.destination);
  };

  const dispatchAudioChunk = (pcmFrames) => {
    setStatus('processing');
    addLog("Sending frame to agent...", "system");
    const totalLength = pcmFrames.reduce((acc, val) => acc + val.length, 0);
    const outArray = new Int16Array(totalLength);
    let offset = 0;
    for (let i = 0; i < pcmFrames.length; i++) {
        outArray.set(pcmFrames[i], offset);
        offset += pcmFrames[i].length;
    }
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(outArray.buffer);
    }
  };

  return (
    <div className="agent-container w-full">
      <div className="control-deck">
        <button 
          className={`telecall-btn ${callState === 'active' ? 'danger' : 'success'}`}
          onClick={callState === 'active' ? endCall : startCall}
        >
          <svg className="btn-icon" viewBox="0 0 24 24" fill="currentColor">
            {callState === 'active' ? (
              <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM15.53 14.47L14.47 15.53L12 13.06L9.53 15.53L8.47 14.47L10.94 12L8.47 9.53L9.53 8.47L12 10.94L14.47 8.47L15.53 9.53L13.06 12L15.53 14.47Z"/>
            ) : (
              <path d="M17 10.5V7C17 6.45 16.55 6 16 6H4C3.45 6 3 6.45 3 7V17C3 17.55 3.45 18 4 18H16C16.55 18 17 17.55 17 17V13.5L21 17.5V6.5L17 10.5Z"/>
            )}
          </svg>
          {callState === 'active' ? 'End Telecall' : 'Start Telecall'}
        </button>
      </div>
      
      <div className="call-visualizer">
        <div className={`orb-avatar agent ${status === 'speaking' ? 'glowing' : ''}`}>
           <span className="avatar-label">Agent</span>
           <div className="waves"></div>
        </div>
        <div className="call-status">
           <span className={`pill ${status}`}>{status.toUpperCase()}</span>
        </div>
        <div className={`orb-avatar patient ${status === 'listening' ? 'glowing' : ''}`}>
           <span className="avatar-label">You</span>
        </div>
      </div>

      <div className="log-container">
        <div className="log-window">
          {logs.slice(-6).map((log, i) => (
            <div key={i} className={`log-entry ${log.type}`}>
               {log.text}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
