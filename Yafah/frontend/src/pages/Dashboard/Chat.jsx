import { useState, useRef, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { GCard as GlassCard, CrownSm, Btn, Lbl, Input } from "../../components/UI";
import { C } from "../../theme/tokens";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Chat() {
  const { user } = useOutletContext();
  const [messages, setMsgs] = useState([
    { role:"assistant", content: `Olá, ${user?.nome?.split(" ")[0]}. Sou sua Estrategista Yafa. Como posso elevar seu império de beleza hoje?` }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoad] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role:"user", content: input };
    setMsgs(prev => [...prev, userMsg]);
    setInput("");
    setLoad(true);

    try {
      const uId = user.id === 'dev_mode' ? 'dev_mode' : user.id;
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-user-id": uId },
        body: JSON.stringify({ message: input, session_id: "default" })
      });

      if (res.ok) {
        const data = await res.json();
        setMsgs(prev => [...prev, { role:"assistant", content: data.response }]);
      } else {
        setMsgs(prev => [...prev, { role:"assistant", content: "Sinto muito, houve uma interrupção na nossa conexão estratégica. Pode repetir?" }]);
      }
    } catch (err) {
      setMsgs(prev => [...prev, { role:"assistant", content: "Erro de frequência. Verifique sua conexão." }]);
    } finally {
      setLoad(false);
    }
  };

  return (
    <div style={{height:"calc(100vh - 220px)", display:"flex", flexDirection:"column", animation:"fadeUp 1s cubic-bezier(0.16, 1, 0.3, 1)"}}>
      
      {/* ✦ Chat Context Info */}
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"32px", padding:"0 12px"}}>
         <div>
            <Lbl>Sessão de Estratégia Ativa</Lbl>
            <p style={{margin:0, fontSize:"13px", color:C.brown_l, fontStyle:"italic", fontFamily:C.serif}}>Consultoria personalizada com base no seu DNA Financeiro e Social.</p>
         </div>
         <Btn variant="outline" style={{padding:"10px 20px", fontSize:"9px"}} onClick={()=>setMsgs([messages[0]])}>REINICIAR DIÁLOGO ✦</Btn>
      </div>

      {/* ✦ Chat Area Editorial */}
      <div style={{flex:1, overflowY:"auto", padding:"0 12px 100px", display:"flex", flexDirection:"column", gap:"32px"}}>
        {messages.map((m, idx) => (
          <div key={idx} style={{
            display:"flex", 
            justifyContent: m.role === "user" ? "flex-end" : "flex-start",
            animation: "fadeUp 0.5s ease"
          }}>
            <div style={{
              maxWidth: "80%",
              padding: m.role === "assistant" ? "32px" : "24px",
              background: m.role === "assistant" ? "#fff" : C.brown,
              color: m.role === "assistant" ? C.brown : "#fff",
              borderRadius: C.radius,
              border: m.role === "assistant" ? `1.5px solid ${C.border}` : "none",
              boxShadow: m.role === "assistant" ? C.shadow : "none",
              position: "relative"
            }}>
              {m.role === "assistant" && (
                <div style={{display:"flex", alignItems:"center", gap:"10px", marginBottom:"16px"}}>
                   <CrownSm size={18} />
                   <p style={{margin:0, fontSize:"10px", letterSpacing:"1.5px", fontWeight:700, textTransform:"uppercase", color:C.gold}}>Yafa Strategist</p>
                </div>
              )}
              <p style={{
                margin: 0, 
                fontSize: m.role === "assistant" ? "17px" : "15px", 
                lineHeight: 1.8,
                fontFamily: m.role === "assistant" ? C.serif : C.sans,
                fontStyle: m.role === "assistant" ? "italic" : "normal",
                whiteSpace: "pre-wrap"
              }}>
                {m.content}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div style={{display:"flex", justifyContent:"flex-start"}}>
            <div style={{padding:"24px 32px", background:"#fff", border:`1.5px solid ${C.border}`, borderRadius:C.radius}}>
               <TypingDots />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* ✦ Elegant Input Bar */}
      <div style={{
        position:"absolute", bottom:"40px", left:"60px", right:"60px", zIndex:100,
        background:"rgba(255, 255, 255, 0.8)", backdropFilter:"blur(20px)",
        border:`1.5px solid ${C.border}`, borderRadius:"0px", padding:"12px",
        boxShadow: "0 20px 40px rgba(44, 30, 17, 0.08)",
        display:"flex", gap:"16px", alignItems:"center"
      }}>
        <div style={{flex:1}}>
          <input 
            value={input}
            onChange={e=>setInput(e.target.value)}
            onKeyDown={e=>e.key==="Enter" && handleSend()}
            placeholder="Qual o próximo movimento para seu negócio hoje? (Ex: Como otimizar meu lucro?)"
            style={{
              width:"100%", padding:"20px", border:"none", background:"transparent",
              color:C.brown, fontSize:"15px", fontFamily:C.sans, outline:"none"
            }}
            disabled={loading}
          />
        </div>
        <Btn onClick={handleSend} disabled={loading || !input.trim()} style={{height:"54px", minWidth:"150px"}}>
          {loading ? "PROCESSANDO..." : "ENVIAR ✦"}
        </Btn>
      </div>

    </div>
  );
}

function TypingDots() {
  return (
    <div style={{display:"flex", gap:"6px", padding:"8px", alignItems:"center"}}>
      {[0, 1, 2].map(i => (
        <div key={i} style={{
          width:"6px", height:"6px", borderRadius:"50%", background:C.gold,
          animation:`bounce 1.4s infinite ease-in-out both`, animationDelay:`${i * 0.16}s`
        }} />
      ))}
      <style>
        {`@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }`}
      </style>
    </div>
  );
}
