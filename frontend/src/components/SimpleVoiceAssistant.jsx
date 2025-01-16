import { useVoiceAssistant} from "@livekit/components-react";

const SimpleVoiceAssistant = () => {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();

  // TODO - add particpant audio transcription and waveform

  return (
    <div className="h-80">
      <p className="text-center">{state}</p>
      <div className="conversation">
        {agentTranscriptions && (
          <div className="agent-transcriptions">
            {agentTranscriptions.map((transcription, index) => (
              <p key={index}>{transcription.text}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SimpleVoiceAssistant;
