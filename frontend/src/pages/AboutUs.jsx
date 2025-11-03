import { useNavigate } from 'react-router-dom';
import Logo from '../components/Chat/Logo';
import Footer from '../components/Footer/Footer';
import Button from '../components/ui/Button';
import '../components/LandingPage/LandingPage.css';
import './AboutUs.css';

const TEAM_MEMBERS = [
  {
    name: 'Alice Rydén',
    linkedinUrl: 'https://www.linkedin.com/in/alice-ryd%C3%A9n-ba745b228/',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/w_1000,ar_1:1,c_fill,g_auto,e_art:hokusai/v1761738498/alice_rrnidt.png',
  },
  {
    name: 'Daniel Salin',
    linkedinUrl: 'https://www.linkedin.com/in/daniel-salin-57084535/',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/w_1000,ar_1:1,c_fill,g_auto,e_art:hokusai/v1761738498/daniel_dixakb.png',
  },
  {
    name: 'Lei Ye',
    linkedinUrl: 'https://www.linkedin.com/in/leiye1989/',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/w_1000,ar_1:1,c_fill,g_auto,e_art:hokusai/v1761738879/lei_v2_eyf7fl.png',
  },
  {
    name: 'Piroz Kianersi',
    linkedinUrl: 'https://www.linkedin.com/in/piroz-kianersi/',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/w_1000,ar_1:1,c_fill,g_auto,e_art:hokusai/v1761738498/piroz_awtgcn.png',
  },
  {
    name: 'Sabrina Rybak',
    linkedinUrl: 'https://www.linkedin.com/in/sabrinarybak/',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/w_1000,ar_1:1,c_fill,g_auto,e_art:hokusai/v1761738879/sabrina_v2_h6v0fu.png',
  },
  {
    name: 'Xiaohua Zhu',
    linkedinUrl: 'https://www.linkedin.com/in/xiaohua-zhu-561906230/',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/w_1000,ar_1:1,c_fill,g_auto,e_art:hokusai/v1761738880/xiahua_v2_weatjn.png',
  },
];

export default function AboutUs() {
  const navigate = useNavigate();

  return (
    <div className="landing-container about-page">
      <div className="hero-section">
        <Logo onClick={() => navigate('/app')} width={256} height={256} />
        <h1 className="about-title">Om Oss</h1>
      </div>

      <section className="about-content">
        <p>
          Denna sida är skapad av en grupp engagerade studenter från AI Developer-programmet vid Jensen Yrkeshögskola. Det du ser här är resultatet av vårt gemensamma grupparbete i kursen Agil utveckling.
        </p>
        <p>
          Under kursens gång har vi fått möjlighet att praktisera agil metodik i verkligheten genom att planera, samarbeta, anpassa oss och utvecklas tillsammans. Vårt mål har varit att skapa en funktionell och användarvänlig lösning, men också att lära oss hur samarbete, kommunikation och kreativ problemlösning kan driva ett projekt framåt.
        </p>
        <p>
          Det här projektet är mer än bara kod och design. Det är ett resultat av kamratskap, brainstorming, feedback och lärande i lag. Vi hoppas att du tycker om att utforska sidan lika mycket som vi har tyckt om att skapa den.
        </p>
        <p className="about-highlight">
          Vill du komma i kontakt med någon av oss? Klicka på våra bilder längst ned på sidan för att besöka våra LinkedIn profiler.
        </p>
      </section>

      <section className="team-section">
        <h2>Teamet bakom projektet</h2>
        <div className="team-grid">
          {TEAM_MEMBERS.map((member) => (
            <a
              key={member.linkedinUrl}
              className="team-card"
              href={member.linkedinUrl}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`LinkedIn profil för ${member.name} - öppnas i nytt fönster`}
            >
              <div className="team-image-wrapper">
                <img 
                  src={member.imageUrl} 
                  alt={`Profilbild av ${member.name}, AI Developer-student`} 
                  loading="lazy" 
                />
              </div>
              <div className="team-info">
                <p className="team-name">{member.name}</p>
              </div>
            </a>
          ))}
        </div>
      </section>

      <div className="back-button-section">
        <Button onClick={() => navigate('/')}>
          Tillbaka
        </Button>
        <Button onClick={() => navigate('/app')}>
          Till Chatbotten
        </Button>
      </div>

      <Footer />
    </div>
  );
}
