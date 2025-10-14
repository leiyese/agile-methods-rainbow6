import { useNavigate } from 'react-router-dom';
import { IoChatbubblesOutline } from 'react-icons/io5'; // Natural conversation
import { IoFlashOutline } from 'react-icons/io5'; // Fast answers
import { IoDocumentTextOutline } from 'react-icons/io5'; // Document knowledge
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
        <h1 className="hero-title">A-Z Försäkringsassistent</h1>
        <p className="hero-description">
          En intelligent chatbot som hjälper dig förstå dina försäkringsvillkor.
        </p>
        <p className="hero-description">
          Ställ frågor på svenska och få tydliga svar baserat på dokument.
        </p>
        <p className="hero-subtitle">
          Skapad för att göra försäkringsinformation lättillgänglig och begriplig.
        </p>
      </div>

      {/* Features Section */}
      <div className="features-section">
        {/* First Flip Card - Natural Conversation */}
        <div className="wrapper">
          <div className="flip-container">
            <div className="flip flip-left">
              <div className="front front-left">
                <div className="circle">
                  <IoChatbubblesOutline className="flip-icon" />
                </div>
              </div>
              <div className="back back-left">
                <div className="flip-text flip-text-combined">
                  <h3>Naturlig Konversation</h3>
                  <p>Prata som med en människa. Inga komplicerade kommandon eller tekniska termer behövs.</p>
                </div>
              </div>
            </div>
          </div><div className="flip-container">
            <div className="flip flip-right">
              <div className="front front-right">
                <div className="circle">
                  <IoChatbubblesOutline className="flip-icon" />
                </div>
              </div>
              <div className="back back-right">
                <div className="flip-text flip-text-combined flip-text-right">
                  <h3>Naturlig Konversation</h3>
                  <p>Prata som med en människa. Inga komplicerade kommandon eller tekniska termer behövs.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Second Flip Card - Fast Answers */}
        <div className="wrapper">
          <div className="flip-container">
            <div className="flip flip-left">
              <div className="front front-left">
                <div className="circle">
                  <IoFlashOutline className="flip-icon" />
                </div>
              </div>
              <div className="back back-left">
                <div className="flip-text flip-text-combined">
                  <h3>Snabba Svar</h3>
                  <p>Få svar på sekunder istället för att läsa genom långa dokument. AI:n sammanfattar informationen åt dig.</p>
                </div>
              </div>
            </div>
          </div><div className="flip-container">
            <div className="flip flip-right">
              <div className="front front-right">
                <div className="circle">
                  <IoFlashOutline className="flip-icon" />
                </div>
              </div>
              <div className="back back-right">
                <div className="flip-text flip-text-combined flip-text-right">
                  <h3>Snabba Svar</h3>
                  <p>Få svar på sekunder istället för att läsa genom långa dokument. AI:n sammanfattar informationen åt dig.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Third Flip Card - Document Knowledge */}
        <div className="wrapper">
          <div className="flip-container">
            <div className="flip flip-left">
              <div className="front front-left">
                <div className="circle">
                  <IoDocumentTextOutline className="flip-icon" />
                </div>
              </div>
              <div className="back back-left">
                <div className="flip-text flip-text-combined">
                  <h3>Dokumentkunskap</h3>
                  <p>Alla svar baseras på riktiga försäkringsdokument. AI:n anger alltid källa och avsnitt för transparens.</p>
                </div>
              </div>
            </div>
          </div><div className="flip-container">
            <div className="flip flip-right">
              <div className="front front-right">
                <div className="circle">
                  <IoDocumentTextOutline className="flip-icon" />
                </div>
              </div>
              <div className="back back-right">
                <div className="flip-text flip-text-combined flip-text-right">
                  <h3>Dokumentkunskap</h3>
                  <p>Alla svar baseras på riktiga försäkringsdokument. AI:n anger alltid källa och avsnitt för transparens.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Button */}
      <div className="cta-section">
        <button 
          className="cta-button"
          onClick={() => navigate('/chat')}
        >
          Ta mig till A-Z
        </button>
      </div>
    </div>
  );
}
