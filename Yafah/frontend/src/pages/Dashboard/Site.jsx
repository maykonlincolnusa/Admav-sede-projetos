import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { GCard as GlassCard, Lbl, Btn, StarDivider, Pill } from "../../components/UI";
import { C } from "../../theme/tokens";

export default function Site() {
  const { user } = useOutletContext();
  const [copy,  setCopy] = useState("");
  const [load,  setLoad] = useState(false);

  const gen = async () => {
    setLoad(true);
    // Simulação de chamada para manter o fluxo UI
    setTimeout(() => {
      setCopy(`✦ BRANDING ESTRATÉGICO: WEBSITE\n\n[HERO SECTION]\nTítulo: A Excelência que seu Estilo merece.\nSubtítulo: Explore o universo de luxo e cuidado personalizado em ${user?.cidade || "Brasil"}.\nCTA: Reserve sua Experiência ✦\n\n[ABOUT SECTION]\n"Na ${user?.nome_negocio || "nossa boutique"}, não criamos apenas beleza; cultivamos confiança. Cada toque, cada detalhe, é uma ode à mulher contemporânea que valoriza o tempo e a sofisticação."\n\n[SERVICES SECTION]\n- Consultoria de Imagem Exclusive\n- Protocolos Beauty de Alta Performance\n- Experiência sensorial completa\n\n[FOOTER]\n${user?.nome_negocio || "Luxury Boutique"} — Onde a tradição encontra a inovação.`);
      setLoad(false);
    }, 3000);
  };

  return (
    <div style={{display:"flex",flexDirection:"column",gap:"24px",animation:"fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1)"}}>
      <GlassCard style={{padding:"40px",background:C.bg,border:`1.5px solid ${C.border}`}}>
        <div style={{textAlign:"center",marginBottom:"40px"}}>
          <Lbl>Arquitetura de Branding</Lbl>
          <h2 style={{margin:"12px 0",fontSize:"32px",color:C.brown,fontFamily:C.serif,fontWeight:400,fontStyle:"italic"}}>Copywriting para Website ✦</h2>
          <p style={{margin:0,color:C.brown_l,fontSize:"14px",fontFamily:C.sans,letterSpacing:"0.5px"}}>Gere uma narrativa persuasiva e sofisticada para o seu domínio digital.</p>
        </div>
        
        <StarDivider/>
        
        <div style={{display:"flex",justifyContent:"center",margin:"40px 0"}}>
          <Btn onClick={gen} disabled={load} variant="primary">
            {load ? "PROCESSANDO..." : "✦ GERAR NARRATIVA DE LUXO"}
          </Btn>
        </div>

        {load && (
          <div style={{display:"flex",flexDirection:"column",alignItems:"center",gap:"16px",padding:"40px 0"}}>
             <p style={{margin:0,color:C.brown_l,fontSize:"10px",letterSpacing:"2px",textTransform:"uppercase",fontFamily:C.sans,fontWeight:700}}>Curando sua narrativa...</p>
          </div>
        )}

        {copy && (
          <div style={{animation:"fadeUp 0.6s ease",maxWidth:"800px",margin:"0 auto"}}>
            <div style={{background:"#fff", border:`1.5px solid ${C.border}`, borderRadius:0, padding:"40px", position:"relative"}}>
               <div style={{position:"absolute",top:"20px",right:"20px"}}><Pill color={C.brown}>EDITORIAL FINAL</Pill></div>
               <p style={{margin:0,color:C.brown,fontSize:"15px",lineHeight:2,fontFamily:C.sans,whiteSpace:"pre-wrap",marginTop:"24px"}}>{copy}</p>
            </div>
            <div style={{display:"flex",justifyContent:"flex-end",marginTop:"24px"}}>
               <Btn onClick={()=>navigator.clipboard.writeText(copy)} variant="outline" style={{borderColor:C.brown,color:C.brown}}>COPIAR NARRATIVA</Btn>
            </div>
          </div>
        )}
      </GlassCard>
    </div>
  );
}

