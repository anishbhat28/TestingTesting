export default function SOSButton() {
    function sos() {
      if (navigator.vibrate) navigator.vibrate(200);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords;
          window.location.href = `sms:?&body=Help needed. Location: https://maps.google.com/?q=${latitude},${longitude}`;
        },
        () => {
          window.location.href = `sms:?&body=Help needed.`;
        }
      );
    }
    return (
        <button className="sos" onClick={sos}>SOS</button>
      );
    }