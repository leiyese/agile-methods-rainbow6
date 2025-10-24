export default function Logo({ onClick, width=120, height=120 }) {
  return (
    <img
      src={"https://res.cloudinary.com/dh4nepzch/image/upload/w_"+ width +",h_"+ height +",c_fill,ar_1:1,f_webp,b_transparent/az_logo_xlvbtl.png"}
      alt="A-Z Logo"
      className="logo"
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    />
  );
}
