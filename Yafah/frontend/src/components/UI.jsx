import { useState } from "react";
import { C } from "../theme/tokens";

export function Glows() {
  return (
    <>
      <div style={{position:"fixed",top:"-200px",left:"40%",width:"900px",height:"900px",borderRadius:"50%",background:`radial-gradient(circle, rgba(212, 175, 55, 0.05) 0%, transparent 70%)`,pointerEvents:"none",zIndex:0}}/>
      <div style={{position:"fixed",bottom:"-150px",right:"-50px",width:"600px",height:"600px",borderRadius:"50%",background:`radial-gradient(circle, rgba(75, 54, 33, 0.03) 0%, transparent 70%)`,pointerEvents:"none",zIndex:0}}/>
    </>
  );
}

export function CrownIcon() {
  return (
    <svg width="48" height="48" viewBox="0 0 64 64">
      <path d="M8 44 L8 28 L20 38 L32 14 L44 38 L56 28 L56 44 Z" fill="none" stroke={C.brown} strokeWidth="1.2" strokeLinejoin="round"/>
      <path d="M6 48 L58 48" stroke={C.brown} strokeWidth="1.2" strokeLinecap="round"/>
      <circle cx="32" cy="14" r="2.5" fill={C.gold}/>
    </svg>
  );
}

export function CrownSm() {
  return (
    <svg width="24" height="24" viewBox="0 0 64 64">
      <path d="M8 44 L8 28 L20 38 L32 14 L44 38 L56 28 L56 44 Z" fill="none" stroke={C.brown} strokeWidth="2" strokeLinejoin="round"/>
      <path d="M6 48 L58 48" stroke={C.brown} strokeWidth="2.5" strokeLinecap="round"/>
      <circle cx="32" cy="14" r="3" fill={C.gold}/>
    </svg>
  );
}

export function StarDivider({ text="" }) {
  return (
    <div style={{display:"flex",alignItems:"center",gap:"12px",margin:"32px 0"}}>
      <div style={{flex:1,height:"0.5px",background:`linear-gradient(to right, transparent, ${C.border})`}}/>
      {text
        ? <span style={{fontSize:"10px",color:C.brown_l,letterSpacing:"5px",fontFamily:C.sans,textTransform:"uppercase",fontWeight:600}}>{text}</span>
        : <div style={{width:4,height:4,borderRadius:"50%",background:C.gold}}/>
      }
      <div style={{flex:1,height:"0.5px",background:`linear-gradient(to left, transparent, ${C.border})`}}/>
    </div>
  );
}

export function GCard({ children, style={}, onClick, onMouseEnter, onMouseLeave }) {
  return (
    <div onClick={onClick} onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave} style={{
      background:C.surface,
      border:`1px solid ${C.border}`,
      borderRadius:C.radius,
      boxShadow:C.shadow,
      transition:"all 0.5s cubic-bezier(0.16, 1, 0.3, 1)",
      overflow:"hidden",
      ...style
    }}>{children}</div>
  );
}

// Retro-compatibility with existing code
export const GlassCard = GCard;

export function Badge({ status }) {
  const m = {
    ativo:    { bg:"rgba(77,103,77,0.05)",  brd:C.border, c:C.success, l:"Ativa" },
    pendente: { bg:`rgba(212,175,55,0.05)`, brd:C.border, c:C.gold,    l:"Pendente" },
    bloqueado:{ bg:"rgba(139,77,77,0.05)",  brd:C.border, c:C.danger,  l:"Bloqueada" },
  };
  const s = m[status]||m.pendente;
  return <span style={{padding:"6px 16px",borderRadius:"2px",background:s.bg,border:`1px solid ${s.brd}`,color:s.c,fontSize:"10px",fontFamily:C.sans,fontWeight:700,letterSpacing:"1.5px",textTransform:"uppercase"}}>{s.l}</span>;
}

export function Btn({ children, onClick, variant="primary", disabled, full, style={} }) {
  const base = { 
    display:"flex",alignItems:"center",justifyContent:"center",gap:"12px",
    padding:"16px 32px",borderRadius:"0px", // Minimalist rectangular with extreme subtle round if needed
    border:"1px solid transparent",cursor:disabled?"not-allowed":"pointer",
    fontFamily:C.sans,fontSize:"11px",fontWeight:600,letterSpacing:"2.5px",
    textTransform:"uppercase",transition:"all 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
    width:full?"100%":"auto",...style 
  };
  
  const v = {
    primary: { background:disabled?"#f4f4f4":C.brown, color:disabled?C.brown_l:"#fff", border:`1px solid ${C.brown}` },
    ghost:   { background:"transparent", border:`1px solid ${C.border}`, color:C.brown },
    gold:    { background:C.gold, color:"#fff", border:`1px solid ${C.gold}` },
    outline: { background:"transparent", border:`2px solid ${C.brown}`, color:C.brown, fontWeight:700 }
  };
  
  return (
    <button onClick={onClick} disabled={disabled} style={{...base,...v[variant]}}>
      {children}
    </button>
  );
}

export function Field({ label, hint, error, children }) {
  return (
    <div style={{display:"flex",flexDirection:"column",gap:"12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
        <label style={{fontSize:"10px",letterSpacing:"3px",textTransform:"uppercase",color:C.brown_l,fontFamily:C.sans,fontWeight:700}}>{label}</label>
        {hint && <span style={{fontSize:"10px",color:C.gold,fontFamily:C.serif,fontStyle:"italic"}}>{hint}</span>}
      </div>
      {children}
      {error && <span style={{fontSize:"11px",color:C.danger,fontFamily:C.sans,letterSpacing:"0.5px"}}>✦ {error}</span>}
    </div>
  );
}

export function Input({ value, onChange, placeholder, type="text", onKeyDown, hasError }) {
  const [f, setF] = useState(false);
  return (
    <input type={type} value={value} onChange={onChange} placeholder={placeholder} onKeyDown={onKeyDown}
      onFocus={()=>setF(true)} onBlur={()=>setF(false)}
      style={{
        padding:"18px", borderRadius:0, fontSize:"15px", fontFamily:C.sans,
        border:`1px solid ${hasError?C.danger:f?C.gold:C.border}`,
        borderBottom:`1.5px solid ${f?C.gold:C.border}`,
        background: f ? "#fff" : "transparent",
        color: C.txt, outline:"none", transition:"all 0.4s ease",
        width:"100%",boxSizing:"border-box"
      }}
    />
  );
}

export function TextArea({ value, onChange, placeholder, rows=4 }) {
  const [f,setF] = useState(false);
  return (
    <textarea value={value} onChange={onChange} placeholder={placeholder} rows={rows}
      onFocus={()=>setF(true)} onBlur={()=>setF(false)}
      style={{width:"100%",padding:"18px",border:`1px solid ${f?C.gold:C.border}`,
        borderRadius:0,fontSize:"14px",fontFamily:C.sans,
        background:f?"#fff":"transparent",
        color:C.txt,outline:"none",boxSizing:"border-box",
        transition:"all 0.3s",resize:"none",lineHeight:1.7}}/>
  );
}

export function Select({ value, onChange, options, placeholder }) {
  return (
    <div style={{position:"relative",width:"100%"}}>
      <select value={value} onChange={onChange}
        style={{
          padding:"18px 40px 18px 16px", borderRadius:0, fontSize:"15px", fontFamily:C.sans,
          border:`1px solid ${C.border}`, background:"transparent", color: value ? C.txt : C.txtSub,
          outline:"none", cursor:"pointer", appearance:"none", width:"100%"
        }}
      >
        <option value="" disabled>{placeholder}</option>
        {options.map(o => <option key={o} value={o} style={{background:C.bg, color:C.txt}}>{o}</option>)}
      </select>
      <div style={{position:"absolute",right:"16px",top:"50%",transform:"translateY(-50%)",pointerEvents:"none"}}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={C.brown} strokeWidth="1.5"><path d="M6 9l6 6 6-6"/></svg>
      </div>
    </div>
  );
}

export function Avatar({ letter, size=36, glow=false }) {
  return (
    <div style={{
      width:size, height:size, borderRadius:"50%", flexShrink:0,
      display:"flex", alignItems:"center", justifyContent:"center",
      background:"#fff",
      border:`1px solid ${C.border}`,
      boxShadow: glow ? C.shadow : "none",
      fontSize:size*0.4, color:C.brown, fontFamily:C.serif, fontWeight:700,
    }}>{letter}</div>
  );
}

export function Lbl({ children }) {
  return <p style={{margin:"0 0 10px",fontSize:"10px",letterSpacing:"5px",textTransform:"uppercase",color:C.brown_l,fontFamily:C.sans,fontWeight:700}}>{children}</p>;
}

export function Pill({ children, color=C.brown }) {
  return <span style={{padding:"6px 18px",borderRadius:"100px",background:C.bg,border:`1px solid ${C.border}`,color,fontSize:"9px",fontFamily:C.sans,fontWeight:700,textTransform:"uppercase",letterSpacing:"2px"}}>{children}</span>;
}

export function Modal({ isOpen, onClose, title, children }) {
  if(!isOpen) return null;
  return (
    <div style={{position:"fixed",inset:0,zIndex:1000,display:"flex",alignItems:"center",justifyContent:"center",padding:"24px"}}>
      <div onClick={onClose} style={{position:"absolute",inset:0,background:"rgba(44, 30, 17, 0.4)",backdropFilter:"blur(12px)"}}/>
      <GCard style={{width:"100%",maxWidth:"500px",position:"relative",zIndex:1,padding:"48px",animation:"fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1)"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"baseline",marginBottom:"40px"}}>
          <h3 style={{margin:0,fontSize:"24px",color:C.brown,fontFamily:C.serif}}>{title}</h3>
          <button onClick={onClose} style={{background:"none",border:"none",color:C.brown_l,cursor:"pointer",fontSize:"24px",fontFamily:C.serif}}>×</button>
        </div>
        {children}
      </GCard>
    </div>
  );
}

export function GlobalStyles() {
  return <style>{`
    * { box-sizing:border-box; }
    body { background: ${C.bg}; margin: 0; color: ${C.txt}; font-family: ${C.sans}; }
    ::-webkit-scrollbar { width:4px; }
    ::-webkit-scrollbar-track { background:transparent; }
    ::-webkit-scrollbar-thumb { background:${C.border}; }
    ::-webkit-scrollbar-thumb:hover { background:${C.gold}; }
    input::placeholder, textarea::placeholder { color:${C.brown_l}; font-size:13px; letter-spacing:1px; }
  `}</style>;
}
