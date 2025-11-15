
export default function VoiceBar() {
    function onVoice() {
      const SpRec =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;
      if (!SpRec) {
        alert("Speech recognition is not supported by this browser.");
        return;
      }
      const r = new SpRec();
      r.lang = "en-US";
      r.onresult = (e: any) => {
        const text = e.results[0][0].transcript.toLowerCase();
        if (text.includes("sos") || text.includes("pineapple")) {
          triggerSOS();
        } else {
          alert(`Heard: "${text}". (Hook to routing intent later.)`);
        }
      };
      r.start();
    }
    function triggerSOS() {
      if (navigator.vibrate) navigator.vibrate(200);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords;
          window.location.href = `sms:?&body=Help needed. Location: https://maps.google.com/?q=${latitude},${longitude}`;
        },
        () => {
          window.location.href = `sms:?&body=Help needed.`;});
    }
    return (
      <div className="voicebar">
        <button onClick={onVoice}>Speak</button>
        <span>Try saying “SOS”.</span>
      </div>);
}