export default function Logo({ onClick }) {
  return (
    <img
      src="https://res.cloudinary.com/dh4nepzch/image/upload/w_128,h_128,c_fill,ar_1:1,f_webp,b_transparent/az_logo_xlvbtl.png"
      alt="A-Z Logo"
      className="logo"
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    />
  );
}
