import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { GCard as GlassCard, Lbl, Btn, Select, Input, StarDivider, Pill } from "../../components/UI";
import { C } from "../../theme/tokens";

const TT_VIDEOS = [
  { id:1, titulo:"Editorial de Outono", emoji:"🍂", views:"42.1K", dur:"15s", perf:"Alta" },
  { id:2, titulo:"Behind the Scenes: Luxury", emoji:"🎥", views:"12.8K", dur:"30s", perf:"Estável" },
  { id:3, titulo:"Tutorial: Elegância Diária", emoji:"💄", views:"89.4K", dur:"60s", perf:"Viral" },
];

export default function TikTok() {
  const { user } = useOutletContext();
  const [tab,    setTab]   = useState("videos");
  const [tema,   setTema]  = useState("");
  const [dur,    setDur]   = useState("30 segundos");
  const [fmt,    setFmt]   = useState("Cinematic Editorial");
  const [script, setScript]= useState("");
  const [load,   setLoad]  = useState(false);

  const gen = async () => {
    if(!tema.trim()) return;
    setLoad(true);
    // Simulação de chamada para manter o fluxo UI
    setTimeout(() => {
      setScript(`✦ ROTEIRO CINEMATIC: ${tema.toUpperCase()}\n\n[00-05s] GANCHO: Close em detalhe de produto com iluminação quente. Texto na tela: "A essência da sofisticação".\n\n[05-15s] CORPO: Transições suaves entre ${tema} e o ambiente da boutique. Voz em off: "Na ${user?.nome_negocio || "nossa boutique"}, cada detalhe é um convite à excelência."\n\n[15-25s] VALOR: Demonstração do serviço de ${tema} com trilha sonora minimalista e elegante.\n\n[25-30s] CTA: Logo da marca centralizado. "Agende sua experiência exclusiva. Link na bio."\n\n#LuxuryLifestyle #${user?.cidade?.replace(/\s/g,'')}Business #EditorialBeauty`);
      setLoad(false);
    }, 2500);
  };

  const tabs = [{id:"videos",l:"🎥 Galeria Editorial"},{id:"roteiro",l:"✦ Scripting IA"}];

  return (
    <div style={{display:"flex",flexDirection:"column",gap:"24px",animation:"fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1)"}}>
      {/* TT Header */}
      <GlassCard style={{padding:"40px",background:C.bg,border:`1.5px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"space-between",flexWrap:"wrap",gap:"24px"}}>
        <div style={{display:"flex",alignItems:"center",gap:"24px"}}>
          <div style={{width:"80px",height:"80px",borderRadius:"50%",background:"#fff",border:`1.5px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:"32px",boxShadow:C.shadow}}>🎥</div>
          <div>
            <p style={{margin:0,color:C.brown,fontSize:"22px",fontWeight:400,fontFamily:C.serif,fontStyle:"italic"}}>{user?.tiktok || "@suamarca.exclusive"}</p>
            <p style={{margin:"4px 0 0",color:C.brown_l,fontSize:"12px",fontFamily:C.sans,letterSpacing:"1px",textTransform:"uppercase"}}>TikTok Creator Portfolio · Premium ✦</p>
          </div>
        </div>
        <div style={{display:"flex",gap:"40px"}}>
          {[["Visualizações","1.2M"],["Vídeos","124"],["Conversão","12%"]].map(([l,v])=>(
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
      {tab==="videos" && (
        <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill, minmax(320px, 1fr))",gap:"16px"}}>
          {TT_VIDEOS.map(v=>(
            <GlassCard key={v.id} style={{padding:"24px",display:"flex",alignItems:"center",gap:"20px",transition:"all 0.3s ease",border:`1.5px solid ${C.border}`}}>
              <div style={{width:"64px",height:"64px",borderRadius:"0px",background:`${C.border}33`,border:`1px solid ${C.border}`,display:"flex",alignItems:"center",justifyContent:"center",fontSize:"32px",flexShrink:0,opacity:0.8}}>{v.emoji}</div>
              <div style={{flex:1}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:"6px"}}>
                  <p style={{margin:0,color:C.brown,fontSize:"15px",fontFamily:C.sans,fontWeight:600}}>{v.titulo}</p>
                  <Pill color={C.brown}>{v.perf}</Pill>
                </div>
                <p style={{margin:0,color:C.brown_l,fontSize:"11px",fontFamily:C.sans,letterSpacing:"1px",textTransform:"uppercase"}}>{v.dur} · {v.views} views</p>
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      {tab==="roteiro" && (
        <div style={{display:"grid",gridTemplateColumns:"1fr 1.2fr",gap:"32px"}}>
          <GlassCard style={{padding:"40px",border:`1.5px solid ${C.border}`}}>
            <Lbl>Direção de Arte IA</Lbl>
            <StarDivider/>
            <div style={{display:"flex",flexDirection:"column",gap:"24px"}}>
              <div>
                <Lbl>Tema do Conteúdo</Lbl>
                <Input value={tema} onChange={e=>setTema(e.target.value)} placeholder="Ex: Demonstração de Luxo / Dia de Spa"/>
              </div>
              <div>
                <Lbl>Duração de Vídeo</Lbl>
                <Select value={dur} onChange={e=>setDur(e.target.value)} options={["15 segundos","30 segundos","60 segundos","90 segundos"]}/>
              </div>
              <div>
                <Lbl>Formato Sugerido</Lbl>
                <Select value={fmt} onChange={e=>setFmt(e.target.value)} options={["Cinematic Editorial","Lifestlye Minimalista","Processo Criativo","Voz da Autoridade"]}/>
              </div>
              <Btn onClick={gen} disabled={load} variant="primary" style={{marginTop:"12px"}}>
                {load ? "PROCESSANDO..." : "✦ GERAR ROTEIRO PREMIUM"}
              </Btn>
            </div>
          </GlassCard>
          <GlassCard style={{padding:"40px",minHeight:"450px",display:"flex",flexDirection:"column",border:`1.5px solid ${C.border}`}}>
            <Lbl>Editorial Script</Lbl>
            <StarDivider/>
            {!script && !load && (
              <div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center",flexDirection:"column",gap:"16px",opacity:0.6}}>
                <span style={{fontSize:"48px"}}>🎬</span>
                <p style={{margin:0,color:C.brown_l,fontSize:"14px",fontStyle:"italic",fontFamily:C.serif}}>O roteiro perfeito para sua marca de luxo será exibido aqui.</p>
              </div>
            )}
            {load && <div style={{flex:1,display:"flex",alignItems:"center",justifyContent:"center"}}><Btn disabled variant="ghost" style={{border:"none"}}>GERANDO DIRETRIZES DE ALTO VALOR...</Btn></div>}
            {script && (
              <div style={{animation:"fadeUp 0.5s ease",display:"flex",flexDirection:"column",height:"100%"}}>
                <div style={{flex:1,background:"#fff",padding:"32px",borderRadius:0,border:`1.5px solid ${C.border}`,marginBottom:"24px",overflowY:"auto"}}>
                  <p style={{margin:0,color:C.brown,fontSize:"15px",lineHeight:1.8,fontFamily:C.sans,whiteSpace:"pre-wrap"}}>{script}</p>
                </div>
                <Btn onClick={()=>navigator.clipboard.writeText(script)} variant="outline" full style={{borderColor:C.brown,color:C.brown}}>📋 COPIAR ROTEIRO</Btn>
              </div>
            )}
          </GlassCard>
        </div>
      )}
    </div>
  );
}
