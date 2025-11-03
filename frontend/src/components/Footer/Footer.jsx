import { useNavigate } from 'react-router-dom';
import './Footer.css';

export default function Footer() {
  const navigate = useNavigate();

  return (
    <footer className="footer">
      <div className="footer-content">
        <p className="footer-text">© 2025 A–Z Försäkringsassistent</p>
        <a 
          className="footer-link" 
          onClick={() => navigate('/about')}
        >
          Om oss
        </a>
      </div>
    </footer>
  );
}
