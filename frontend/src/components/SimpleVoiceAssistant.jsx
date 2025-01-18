import { useVoiceAssistant, BarVisualizer, VoiceAssistantControlBar, useTrackTranscription, useLocalParticipant } from "@livekit/components-react";
import { Track } from 'livekit-client';
import { useEffect, useState } from 'react';

const Message = ({ type, text }) => (
  <div style={{ marginBottom: '10px' }}>
    <strong style={{ color: type === 'agent' ? '#4a90e2' : '#2ecc71' }}>
      {type === 'agent' ? 'Agent: ' : 'You: '}
    </strong>
    <span>{text}</span>
  </div>
);

const SimpleVoiceAssistant = () => {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const localParticipant = useLocalParticipant();
  const { segments: userTranscriptions } = useTrackTranscription({
    publication: localParticipant.microphoneTrack,
    source: Track.Source.Microphone,
    participant: localParticipant.localParticipant,
  });

  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const allMessages = [
      ...(agentTranscriptions?.map(t => ({ ...t, type: 'agent' })) ?? []),
      ...(userTranscriptions?.map(t => ({ ...t, type: 'user' })) ?? [])
    ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
    
    setMessages(allMessages);
  }, [agentTranscriptions, userTranscriptions]);

  return (
    <>
      <BarVisualizer
        state={state}
        barCount={7}
        trackRef={audioTrack}
        style={{ width: '75vw', height: '300px' }}
      />
      <div className="h-80">
        <VoiceAssistantControlBar />
        <div className="conversation" style={{ padding: '20px', maxHeight: '300px', overflowY: 'auto' }}>
          {messages.map((msg, index) => (
            <Message 
              key={msg.id || index}
              type={msg.type}
              text={msg.text}
            />
          ))}
        </div>
      </div>
    </>
  );
};

export default SimpleVoiceAssistant;
