import { useEffect } from 'react';
import MapView from './map/MapView';
import VoiceBar from './comp/VoiceBar';
import SOSButton from './comp/SOSButton';
export default function App() {
    useEffect(() => {
      document.title = "ComfortZone";
    }, []);
    return (
      <div className="wrap">
        <header className="cz-header">
          <div className="cz-logo-wrap">
            <img
              src="/logo-comfortzone.png"
              alt="ComfortZone logo"
              className="cz-logo"
            />
          </div>
          <div className="cz-title-block">
            <h1>ComfortZone</h1>
            <p>Navigation and Shelter with Dignity</p>
          </div>
        </header>
        <VoiceBar />
        <MapView />
        <SOSButton />
        <footer>
          <small>Demo for SD Big Data Hackathon on 11/15</small>
        </footer>
      </div>
    );
  }