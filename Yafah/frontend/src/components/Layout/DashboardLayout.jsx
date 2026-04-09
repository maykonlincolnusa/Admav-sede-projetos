import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation, Outlet } from "react-router-dom";
import { Glows, CrownSm, Pill, GlobalStyles, Avatar } from "../../components/UI";
import { C } from "../../theme/tokens";

const NAV = [
  {id:"",          icon:"◉", label:"Início"},
  {id:"chat",    icon:"✦", label:"IA Consultora"},
  {id:"finance", icon:"$ ", label:"Financeiro"},
  {id:"knowledge",icon:"⚙", label:"Inteligência"},
  {id:"instagram",icon:"◈", label:"Marketing"},
];

const TITLES = { 
  "": "Visão Geral", 
  "chat": "Suíte de Inteligência — IA Yafa", 
  "finance": "Hub de Inteligência Financeira",
  "knowledge": "Gestão de Conhecimento",
  "instagram": "Estratégia de Marketing", 
};

export default function DashboardLayout() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const loc = useLocation();
  const path = loc.pathname.split("/")[2] || "";

  useEffect(() => {
    const s = localStorage.getItem("yafa_user");
    if (!s) { navigate("/login"); return; }
    setUser(JSON.parse(s));
  }, [navigate]);

  if (!user) return null;

  return (
    <div style={{minHeight:"100vh", background:C.bg, display:"flex", position:"relative", overflowX:"hidden"}}>
      <GlobalStyles />
      <Glows />

      {/* ✦ Thin Editorial Sidebar */}
      <nav style={{
        width:"260px", height:"100vh", background:C.surface, 
        borderRight:`1px solid ${C.border}`, position:"sticky", top:0,
        display:"flex", flexDirection:"column", padding:"48px 24px", zIndex:100,
        transition:"all 0.5s ease"
      }}>
        
        {/* Branding Sidebar */}
        <div style={{marginBottom:"60px", padding:"0 12px", display:"flex", alignItems:"center", gap:"14px"}}>
           <CrownSm />
           <h2 style={{margin:0, fontSize:"24px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400}}>Yafa ✦</h2>
        </div>

        {/* Links */}
        <div style={{display:"flex", flexDirection:"column", gap:"8px", flex:1}}>
          {NAV.map(n => {
            const active = path === n.id;
            return (
              <Link key={n.id} to={`/dashboard/${n.id}`} style={{
                display:"flex", alignItems:"center", gap:"16px", padding:"14px 16px",
                borderRadius:C.radius, transition:"0.4s",
                background: active ? `${C.brown}05` : "transparent",
                color: active ? C.brown : C.brown_l,
                fontSize:"12px", letterSpacing:"1.5px", fontWeight:active?700:500,
                textTransform:"uppercase", border:active?`1px solid ${C.border}`:"1px solid transparent"
              }}>
                <span style={{fontSize:"16px", color:active?C.gold:C.brown_l, opacity:0.8}}>{n.icon}</span>
                {n.label}
              </Link>
            );
          })}
        </div>

        {/* Profile Card Sidebar */}
        <div style={{marginTop:"auto", padding:"24px 12px", borderTop:`1px solid ${C.border}`, display:"flex", alignItems:"center", gap:"14px"}}>
           <Avatar letter={user.nome?.[0] || "?"} size={40} glow />
           <div style={{overflow:"hidden"}}>
              <p style={{margin:0, fontSize:"12px", color:C.brown, fontWeight:700, whiteSpace:"nowrap", textOverflow:"ellipsis"}}>{user.nome}</p>
              <button 
                onClick={()=>{localStorage.clear(); navigate("/login");}}
                style={{background:"none", border:"none", cursor:"pointer", color:C.gold, fontSize:"10px", padding:0, fontWeight:700}}
              >X SAIR</button>
           </div>
        </div>
      </nav>

      {/* ✦ Main Body Layout */}
      <main style={{flex:1, minHeight:"100vh", position:"relative", display:"flex", flexDirection:"column"}}>
        
        {/* Floating Header Glass */}
        <header style={{
          height:"100px", padding:"0 60px", display:"flex", alignItems:"center", justifyContent:"space-between",
          background:"rgba(253, 251, 247, 0.8)", borderBottom:`1px solid ${C.border}`,
          backdropFilter:"blur(12px)", position:"sticky", top:0, zIndex:90
        }}>
           <div>
              <p style={{margin:"0 0 4px", fontSize:"9px", color:C.brown_l, letterSpacing:"4px", textTransform:"uppercase", fontWeight:700}}>Seu Império / {loc.pathname.split("/")[2] || "Início"}</p>
              <h1 style={{margin:0, fontSize:"28px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400}}>{TITLES[path]}</h1>
           </div>
           
           <div style={{display:"flex", alignItems:"center", gap:"24px"}}>
              <Pill color={C.brown}>STATUS: {user.status?.toUpperCase() || "VIP"}</Pill>
              <div style={{width:"1px", height:"24px", background:C.border}}/>
              <div style={{width:"10px", height:"10px", background:C.success, borderRadius:"50%", animation:"pulse 2s infinite"}}/>
           </div>
        </header>

        {/* Content Area Rendering */}
        <div style={{flex:1, padding:"60px", position:"relative", zIndex:1, maxWidth:"1400px", margin:"0 auto", width:"100%"}}>
           <Outlet context={{ user }} />
        </div>

        {/* Elite Footer */}
        <footer style={{padding:"40px 60px", borderTop:`1px solid ${C.border}`, display:"flex", justifyContent:"space-between", alignItems:"center"}}>
           <p style={{margin:0, fontSize:"10px", color:C.brown_l, letterSpacing:"1.5px", textTransform:"uppercase"}}>© 2026 Yafa Intelligence — Privado & Exclusivo</p>
           <p style={{margin:0, fontSize:"10px", color:C.brown_l, letterSpacing:"1.5px", textTransform:"uppercase"}}>Sua Segurança em Primeiro Lugar</p>
        </footer>
      </main>

    </div>
  );
}
