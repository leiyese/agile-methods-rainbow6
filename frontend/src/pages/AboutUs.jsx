import { useNavigate } from 'react-router-dom';
import Logo from '../components/Chat/Logo';
import Footer from '../components/Footer/Footer';
import Button from '../components/ui/Button';
import '../components/LandingPage/LandingPage.css';
import './AboutUs.css';

const TEAM_MEMBERS = [
  {
    name: 'Alex Doe',
    role: 'AI Developer-student',
    email: 'alex@example.com',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/v1730200000/team-member-1.png',
  },
  {
    name: 'Blake Kim',
    role: 'AI Developer-student',
    email: 'blake@example.com',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/v1730200000/team-member-2.png',
  },
  {
    name: 'Casey Lee',
    role: 'AI Developer-student',
    email: 'casey@example.com',
    imageUrl: 'https://res.cloudinary.com/dh4nepzch/image/upload/v1730200000/team-member-3.png',
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
          Denna sida är skapad av en grupp engagerade studenter från AI Developer-programmet vid Jensen Yrkeshögskola. Det du ser här är resultatet av vårt gemensamma grupparbete i kursen Agilmetodik.
        </p>
        <p>
          Under kursens gång har vi fått möjlighet att praktisera Agilmetodik i verkligheten — genom att planera, samarbeta, anpassa oss och utvecklas tillsammans. Vårt mål har varit att skapa en funktionell och användarvänlig lösning, men också att lära oss hur samarbete, kommunikation och kreativ problemlösning kan driva ett projekt framåt.
        </p>
        <p>
          Det här projektet är mer än bara kod och design. Det är ett resultat av kamratskap, brainstorming, feedback och lärande i lag. Vi hoppas att du tycker om att utforska sidan lika mycket som vi har tyckt om att skapa den.
        </p>
        <p className="about-highlight">
          Vill du komma i kontakt med någon av oss? Klicka på våra bilder längst ned på sidan.
        </p>
      </section>

      <section className="team-section">
        <h2>Teamet bakom projektet</h2>
        <div className="team-grid">
          {TEAM_MEMBERS.map((member) => (
            <a
              key={member.email}
              className="team-card"
              href={`mailto:${member.email}`}
              aria-label={`Kontakta ${member.name}`}
            >
              <div className="team-image-wrapper">
                <img src={member.imageUrl} alt={member.name} loading="lazy" />
              </div>
              <div className="team-info">
                <p className="team-name">{member.name}</p>
                <p className="team-role">{member.role}</p>
                <span className="team-contact">Klicka för kontakt</span>
              </div>
            </a>
          ))}
        </div>
      </section>

      <div className="back-button-section">
        <Button onClick={() => navigate('/')}>
          Tillbaka
        </Button>
      </div>

      <Footer />
    </div>
  );
}
