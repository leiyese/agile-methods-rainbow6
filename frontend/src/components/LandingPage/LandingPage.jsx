import { useNavigate } from 'react-router-dom';
import { IoChatbubblesOutline, IoFlashOutline, IoDocumentTextOutline } from 'react-icons/io5';
import Button from '../ui/Button';
import Footer from '../Footer/Footer';
import Logo from '../Chat/Logo';
import './LandingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <IoChatbubblesOutline />,
      title: "Naturlig Konversation",
      description: "Prata som med en människa. Inga komplicerade kommandon eller tekniska termer behövs."
    },
    {
      icon: <IoFlashOutline />,
      title: "Snabba Svar",
      description: "Få svar på sekunder istället för att läsa genom långa dokument. AI:n sammanfattar informationen åt dig."
    },
    {
      icon: <IoDocumentTextOutline />,
      title: "Dokumentkunskap",
      description: "Alla svar baseras på riktiga försäkringsdokument. AI:n anger alltid källa och avsnitt för transparens."
    }
  ];

  return (
    <div className="landing-container">
      {/* Hero Section */}
      <div className="hero-section">
        <Logo onClick={() => navigate('/app')} width={256} height={256} />
        <p className="hero-description">
          Försäkringsinformation – på ett ögonblick<br />
          Kombinerar din expertis med intelligent AI<br />
          Assistenten hjälper dig med exakta svar baserat<br />
          på interna villkor och policys.
        </p>
      </div>

      {/* CTA Button */}
      <div className="cta-section">
        <Button onClick={() => navigate('/app')}>
          Kom igång nu →
        </Button>
      </div>

      {/* Features Section */}
      <div className="features-section">
      {features.map((feature) => (
        <div key={feature.title} className="feature-card">
          <div className="feature-icon">{feature.icon}</div>
          <h3>{feature.title}</h3>
          <p>{feature.description}</p>
        </div>
      ))}
    </div>
    
    <Footer />
    </div>
  );
}
