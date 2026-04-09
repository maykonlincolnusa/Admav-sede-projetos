import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { GCard as GlassCard, Lbl, Pill, Btn, Select, Input, StarDivider } from "../../components/UI";
import { C } from "../../theme/tokens";

const IG_POSTS = [
  { id:1, tipo:"Editorial", emoji:"✨", likes:1240, coments:87,  alcance:"12.4K", data:"Hoje",   legenda:"A arte de transformar o cotidiano em luxo. ✨" },
  { id:2, tipo:"Portfolio", emoji:"💎", likes:890,  coments:43,  alcance:"8.9K",  data:"Ontem",  legenda:"Elegância em cada detalhe. 💍" },
  { id:3, tipo:"Lifestyle", emoji:"🌸", likes:2100, coments:156, alcance:"21K",   data:"3 dias", legenda:"Sinta a suavidade da nossa nova linha. 🌊" },
];

export default function Instagram() {
  const { user } = useOutletContext();
  const [tab,      setTab]  = useState("feed");
  const [servico,  setServ] = useState("");
  const [objetivo, setObj]  = useState("Atrair clientes VIP");
  const [estilo,   setEst]  = useState("Sofisticado");
  const [caption,  setCap]  = useState("");
  const [load,     setLoad] = useState(false);

  const gen = async () => {
    setLoad(true);
    // Simulação de chamada para manter o fluxo UI
    setTimeout(() => {
      setCap(`✦ ELEVANDO O PADRÃO\n\nEm ${user?.cidade || "nossa boutique"}, acreditamos que a beleza é uma expressão de propósito. O serviço de ${servico || "Beleza Premium"} foi desenhado para mulheres que não aceitam nada menos que a excelência.\n\n✨ Sinta o toque da sofisticação.\n💎 Exclusividade em cada detalhe.\n\nReserve seu momento via Direct.\n\n#LuxuryBeauty #BoutiqueExperience #${user?.cidade?.replace(/\s/g,'')||'Estetica'} #BrandingDeLuxo`);
      setLoad(false);
    }, 2000);
  };

  const tabs = [{id:"feed",l:"📸 Galeria"},{id:"metricas",l:"📊 Performance"},{id:"gerador",l:"✦ Editorial IA"}];

  return (
    <div style={{display:"flex",flexDirection:"column",gap:"24px",animation:"fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1)"}}>
      {/* IG Header Editorial */}
      <GlassCard style={{padding:"40px",background:C.bg,border:`1.5px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"space-between",flexWrap:"wrap",gap:"24px"}}>
        <div style={{display:"flex",alignItems:"center",gap:"24px"}}>
          <div style={{width:"80px",height:"80px",borderRadius:"50%",background:"#fff",border:`1.5px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:"32px",boxShadow:C.shadow}}>🖤</div>
          <div>
            <p style={{margin:0,color:C.brown,fontSize:"22px",fontWeight:400,fontFamily:C.serif,fontStyle:"italic"}}>{user?.instagram || "@suamarca.luxury"}</p>
            <p style={{margin:"4px 0 0",color:C.brown_l,fontSize:"12px",fontFamily:C.sans,letterSpacing:"1px",textTransform:"uppercase"}}>Conta Business · Verificada ✦</p>
          </div>
        </div>
        <div style={{display:"flex",gap:"40px"}}>
          {[["Publicações","47"],["Seguidores","3.2K"],["Engajamento","8.4%"]].map(([l,v])=>(
            <div key={l} style={{textAlign:"center"}}>
              <p style={{margin:0,fontSize:"28px",color:C.brown,fontFamily:C.serif,fontWeight:400}}>{v}</p>
              <p style={{margin:0,fontSize:"10px",color:C.brown_l,fontFamily:C.sans,textTransform:"uppercase",letterSpacing:"1.5px",fontWeight:700}}>{l}</p>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Tabs */}
      <div style={{display:"flex",gap:"16px",borderBottom:`1.5px solid ${C.border}`,paddingBottom:"12px"}}>
        {tabs.map(t=>(
          <button key={t.id} onClick={()=>setTab(t.id)} style={{padding:"8px 16px",border:"none",background:"transparent",cursor:"pointer",fontFamily:C.sans,fontSize:"11px",fontWeight:700,color:tab===t.id?C.brown:C.brown_l,letterSpacing:"2px",textTransform:"uppercase",transition:"all 0.3s",borderBottom:tab===t.id?`2px solid ${C.brown}`:"2px solid transparent"}}>{t.l}</button>
        ))}
      </div>

      {/* Content */}
      {tab==="feed" && (
        <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill, minmax(280px, 1fr))",gap:"24px"}}>
          {IG_POSTS.map(p=>(
            <GlassCard key={p.id} style={{padding:"24px",border:`1.5px solid ${C.border}`}}>
              <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"20px"}}>
                <Pill color={C.brown}>{p.tipo}</Pill>
                <span style={{fontSize:"10px",color:C.brown_l,fontFamily:C.sans,letterSpacing:"1.5px",fontWeight:700,textTransform:"uppercase"}}>{p.data}</span>
              </div>
              <div style={{height:"220px",borderRadius:0,background:`${C.border}33`,border:`1px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:"48px",marginBottom:"20px",opacity:0.8}}>{p.emoji}</div>
              <p style={{margin:"0 0 20px",fontSize:"14px",color:C.brown_l,fontFamily:C.sans,lineHeight:1.6,display:"-webkit-box",WebkitLineClamp:2,WebkitBoxOrient:"vertical",overflow:"hidden",fontStyle:"italic"}}>{p.legenda}</p>
              <div style={{display:"flex",justifyContent:"space-between",borderTop:`1px solid ${C.border}`,paddingTop:"16px"}}>
                {[["❤️",p.likes],["💬",p.coments],["👁️",p.alcance]].map(([ic,v])=>(
                  <div key={ic} style={{display:"flex",alignItems:"center",gap:"8px"}}>
                    <span style={{fontSize:"14px"}}>{ic}</span>
                    <span style={{fontSize:"12px",color:C.brown,fontFamily:C.sans,fontWeight:700}}>{v}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      {tab==="gerador" && (
        <div style={{display:"grid",gridTemplateColumns:"1fr 1.2fr",gap:"32px"}}>
          <GlassCard style={{padding:"40px",border:`1.5px solid ${C.border}`}}>
            <Lbl>Configuração Editorial</Lbl>
            <StarDivider/>
            <div style={{display:"flex",flexDirection:"column",gap:"24px"}}>
              <div>
                <Lbl>Serviço de Luxo</Lbl>
                <Input value={servico} onChange={e=>setServ(e.target.value)} placeholder="Ex: Nail Design VIP / Harmonização Facial"/>
              </div>
              <div>
                <Lbl>Objetivo de Campanha</Lbl>
                <Select value={objetivo} onChange={e=>setObj(e.target.value)} options={["Atrair clientes VIP","Lançamento de Coleção","Fidelização Exclusive","Branding de Autoridade"]}/>
              </div>
              <div>
                <Lbl>Tom de Voz</Lbl>
                <Select value={estilo} onChange={e=>setEst(e.target.value)} options={["Sofisticado","Minimalista","Poderoso","Inspiracional"]}/>
              </div>
              <Btn onClick={gen} disabled={load} variant="primary" style={{marginTop:"12px"}}>
                {load ? "PROCESSANDO..." : "✦ GERAR EDITORIAL IA"}
              </Btn>
            </div>
          </GlassCard>

          <GlassCard style={{padding:"40px",minHeight:"400px",display:"flex",flexDirection:"column",border:`1.5px solid ${C.border}`}}>
            <Lbl>Preview do Editorial</Lbl>
            <StarDivider/>
            {!caption && !load && (
              <div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center",flexDirection:"column",gap:"16px",opacity:0.6}}>
                <span style={{fontSize:"48px"}}>📸</span>
                <p style={{margin:0,color:C.brown_l,fontSize:"14px",fontStyle:"italic",fontFamily:C.serif}}>Defina os parâmetros para gerar seu conteúdo de luxo.</p>
              </div>
            )}
            {load && <div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center"}}><Btn disabled variant="ghost" style={{border:"none"}}>GERANDO NARRATIVA DE ALTO VALOR...</Btn></div>}
            {caption && (
              <div style={{animation:"fadeUp 0.5s ease",display:"flex",flexDirection:"column",height:"100%"}}>
                <div style={{flex:1,background:"#fff",padding:"32px",border:`1.5px solid ${C.border}`,marginBottom:"24px",borderRadius:0}}>
                  <p style={{margin:0,color:C.brown,fontSize:"15px",lineHeight:1.8,fontFamily:C.sans,whiteSpace:"pre-wrap"}}>{caption}</p>
                </div>
                <Btn onClick={()=>navigator.clipboard.writeText(caption)} variant="outline" full style={{borderColor:C.brown,color:C.brown}}>📋 COPIAR EDITORIAL</Btn>
              </div>
            )}
          </GlassCard>
        </div>
      )}
    </div>
  );
}
