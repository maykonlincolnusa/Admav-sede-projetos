import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { GCard as GlassCard, Lbl, StarDivider, Pill, Btn, Field, Input, TextArea, Modal } from "../../components/UI";
import { C } from "../../theme/tokens";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Knowledge() {
  const { user } = useOutletContext();
  const [knowledge, setKnow] = useState([]);
  const [loading, setLoad]     = useState(false);
  const [kModal, setKModal]   = useState(false);
  const [kType, setKType]     = useState("text"); // text, url, pdf, instagram, tiktok
  const [kForm, setKForm]     = useState({ texto:"", fonte:"", categoria:"Geral", url:"", handle:"", arquivo:null });

  const fetchKnowledge = async () => {
    if (!user?.id) return;
    setLoad(true);
    try {
      const uId = user.id === 'dev_mode' ? 'dev_mode' : user.id;
      const res = await fetch(`${API_URL}/api/knowledge/list`, {
        headers: { "x-user-id": uId }
      });
      if (res.ok) {
        const data = await res.json();
        setKnow(data);
      }
    } catch (err) {
      console.error("Erro ao carregar conhecimento:", err);
    } finally {
      setLoad(false);
    }
  };

  useEffect(() => {
    fetchKnowledge();
  }, [user]);

  const handleKSubmit = async () => {
    if (!user?.id) return;
    setLoad(true);
    try {
      let res;
      const uId = user.id === 'dev_mode' ? 'dev_mode' : user.id;
      const commonHeaders = { "x-user-id": uId };
      
      if (kType === "text") {
        res = await fetch(`${API_URL}/api/knowledge/add-text`, {
          method: "POST",
          headers: { ...commonHeaders, "Content-Type": "application/json" },
          body: JSON.stringify({ texto: kForm.texto, fonte: kForm.fonte, categoria: kForm.categoria })
        });
      } else if (kType === "url") {
        res = await fetch(`${API_URL}/api/knowledge/add-url`, {
          method: "POST",
          headers: { ...commonHeaders, "Content-Type": "application/json" },
          body: JSON.stringify({ url: kForm.url, categoria: kForm.categoria })
        });
      } else if (kType === "pdf") {
        const fd = new FormData();
        fd.append("arquivo", kForm.arquivo);
        fd.append("categoria", kForm.categoria);
        res = await fetch(`${API_URL}/api/knowledge/add-pdf?categoria=${kForm.categoria}`, {
          method: "POST",
          headers: commonHeaders,
          body: fd
        });
      } else if (kType === "instagram" || kType === "tiktok") {
        res = await fetch(`${API_URL}/api/knowledge/add-social`, {
          method: "POST",
          headers: { ...commonHeaders, "Content-Type": "application/json" },
          body: JSON.stringify({ handle: kForm.handle, rede: kType, categoria: "Marketing" })
        });
      }

      if (res && res.ok) {
        setKModal(false);
        setKForm({ texto:"", fonte:"", categoria:"Geral", url:"", handle:"", arquivo:null });
        fetchKnowledge();
      } else {
        const d = await res.json();
        alert(d.detail || "Erro ao processar informação estratégica.");
      }
    } catch (err) {
      alert("Erro de conexão com a inteligência Yafa.");
    } finally {
      setLoad(false);
    }
  };

  const deleteKnowledge = async (id) => {
    if(!window.confirm("Deseja remover esta fonte de inteligência?")) return;
    try {
      const uId = user.id === 'dev_mode' ? 'dev_mode' : user.id;
      const res = await fetch(`${API_URL}/api/knowledge/${id}`, {
        method: "DELETE",
        headers: { "x-user-id": uId }
      });
      if (res.ok) fetchKnowledge();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{display:"flex",flexDirection:"column",gap:"40px",animation:"fadeUp 1.2s cubic-bezier(0.16, 1, 0.3, 1)"}}>
      
      {/* ✦ Knowledge Hub Header Editorial */}
      <GlassCard style={{padding:"48px", background:C.bg, border:`2.5px solid ${C.border}`, display:"flex", justifyContent:"space-between", alignItems:"center", flexWrap:"wrap", gap:"32px"}}>
        <div>
           <Lbl>Centro de Inteligência Yafa</Lbl>
           <h2 style={{margin:"8px 0 12px", fontSize:"36px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400}}>Conectores de Saber ✦</h2>
           <p style={{margin:0, fontSize:"14px", color:C.brown_l, fontFamily:C.sans, lineHeight:1.7}}>
              Alimente a Yafa com os manuais de sua marca, sites estratégicos e redes sociais. 
              <br/>Toda informação processada refina a precisão da sua consultoria financeira e de marketing.
           </p>
        </div>
        <Btn onClick={()=>setKModal(true)} variant="primary" style={{padding:"18px 36px", height:"60px"}}>✦ NOVO CONECTOR</Btn>
      </GlassCard>

      {/* ✦ Intelligence Sources Grid */}
      {loading && !knowledge.length ? (
        <div style={{textAlign:"center", padding:"100px"}}>
          <div style={{width:"48px",height:"48px",margin:"0 auto",border:`1.5px solid ${C.border}`,borderTopColor:C.gold,borderRadius:"50%",animation:"spin 2s linear infinite"}}/>
          <p style={{marginTop:"32px", fontSize:"11px", color:C.brown_l, letterSpacing:"2px", fontWeight:700}}>SINCROMIZANDO SINAPSES...</p>
        </div>
      ) : (
        <div style={{display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(360px, 1fr))", gap:"32px"}}>
          {knowledge.length === 0 ? (
            <GlassCard style={{gridColumn:"1/-1", textAlign:"center", padding:"100px 48px", border:`1.5px solid ${C.border}`, borderStyle:"dashed"}}>
               <p style={{fontSize:"24px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", margin:"0 0 12px"}}>Sua IA ainda é uma tela em branco.</p>
               <p style={{fontSize:"14px", color:C.brown_l, fontFamily:C.sans, marginBottom:"40px"}}>Conecte seu site, suba PDFs da empresa ou sincronize suas redes sociais para começar.</p>
               <Btn onClick={()=>setKModal(true)} variant="outline" style={{borderColor:C.brown, color:C.brown, padding:"16px 32px"}}>COMEÇAR AGORA ✦</Btn>
            </GlassCard>
          ) : (
            knowledge.map(k => (
              <GlassCard key={k.id} style={{padding:"40px", display:"flex", flexDirection:"column", gap:"24px", border:`1.5px solid ${C.border}`}}>
                <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
                   <div style={{display:"flex", alignItems:"center", gap:"10px"}}>
                      <span style={{fontSize:"20px"}}>{k.tipo === "instagram" ? "📸" : k.tipo === "tiktok" ? "🎬" : "◈"}</span>
                      <Pill color={C.brown} style={{fontSize:"9px", letterSpacing:"1px"}}>{k.categoria.toUpperCase()}</Pill>
                   </div>
                   <button onClick={()=>deleteKnowledge(k.id)} style={{background:"none", border:"none", cursor:"pointer", color:C.brown_l, fontSize:"20px", opacity:0.4}}>×</button>
                </div>
                <div style={{flex:1}}>
                  <p style={{margin:"0 0 12px", fontSize:"10px", color:C.gold, letterSpacing:"2.5px", fontWeight:700, textTransform:"uppercase"}}>DNA Extraído & Auditado</p>
                  <p style={{margin:0, fontSize:"15px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", lineHeight:1.7, overflow:"hidden", display:"-webkit-box", WebkitLineClamp:4, WebkitBoxOrient:"vertical"}}>"{k.texto_preview}"</p>
                </div>
                
                <StarDivider />

                <div style={{display:"flex", justifyContent:"space-between", alignItems:"baseline"}}>
                   <div>
                      <p style={{margin:"0 0 4px", fontSize:"8px", color:C.brown_l, letterSpacing:"1.5px", textTransform:"uppercase", fontWeight:700}}>Fonte de Inteligência</p>
                      <p style={{margin:0, fontSize:"13px", color:C.brown, fontFamily:C.sans, fontWeight:600, overflow:"hidden", textOverflow:"ellipsis", maxWidth:"180px"}}>{k.fonte}</p>
                   </div>
                   <div style={{textAlign:"right"}}>
                      <p style={{margin:"0 0 4px", fontSize:"8px", color:C.brown_l, letterSpacing:"1.5px", textTransform:"uppercase", fontWeight:700}}>Índice de Acerto</p>
                      <p style={{margin:0, fontSize:"18px", color:C.gold, fontFamily:C.serif, fontWeight:700}}>{(k.qualidade_score * 100).toFixed(0)}%</p>
                   </div>
                </div>
              </GlassCard>
            ))
          )}
        </div>
      )}

      {/* ✦ Modular Premium Ingestion Modal */}
      <Modal isOpen={kModal} onClose={()=>setKModal(false)} title="Treinar Inteligência Yafa">
        <div style={{display:"flex", flexDirection:"column", gap:"28px"}}>
           <div style={{display:"flex", gap:"1px", background:C.border, padding:"1px", borderRadius:"0px", overflowX:"auto"}}>
              {[
                {id:"text",l:"TEXTO"},{id:"url",l:"SITE"},{id:"pdf",l:"PDF"},
                {id:"instagram",l:"INSTA"},{id:"tiktok",l:"TIKTOK"}
              ].map(m=>(
                <button key={m.id} onClick={()=>setKType(m.id)} style={{flexShrink:0, padding:"14px 18px", background:kType===m.id?"#fff":C.bg, border:"none", color:kType===m.id?C.brown:C.brown_l, fontSize:"10px", fontWeight:700, letterSpacing:"1.5px", cursor:"pointer", transition:"0.3s"}}>{m.l}</button>
              ))}
           </div>

           {(kType === "text" || kType === "url" || kType === "pdf") && (
             <Field label="Natureza do Conhecimento" hint="Ex: Catálogo, FAQ, Regras">
                <Input value={kForm.categoria} onChange={e=>setKForm({...kForm, categoria:e.target.value})} placeholder="Classificação da informação" />
             </Field>
           )}

           {kType === "text" && (
             <>
               <Field label="Identificação da Fonte"><Input value={kForm.fonte} onChange={e=>setKForm({...kForm, fonte:e.target.value})} placeholder="Ex: Manual de Branding" /></Field>
               <Field label="Conteúdo Base para IA"><TextArea value={kForm.texto} onChange={e=>setKForm({...kForm, texto:e.target.value})} placeholder="Insira aqui as diretrizes que a Yafa deve processar..." rows={6} /></Field>
             </>
           )}

           {kType === "url" && (
             <Field label="Atalho Digital (URL)"><Input value={kForm.url} onChange={e=>setKForm({...kForm, url:e.target.value})} placeholder="https://seu-site.com.br/sobre" type="url" /></Field>
           )}

           {kType === "pdf" && (
             <Field label="Documento Estruturado (PDF)">
               <input type="file" accept=".pdf" onChange={e=>setKForm({...kForm, arquivo:e.target.files[0]})} style={{width:"100%", color:C.brown, fontFamily:C.sans, fontSize:"12px", background:`${C.border}22`, padding:"18px", border:`1px solid ${C.border}`}} />
             </Field>
           )}

           {(kType === "instagram" || kType === "tiktok") && (
             <Field label={`Identificador @${kType.capitalize()}`} hint="Indexação automática de bio e estilo.">
               <Input value={kForm.handle} onChange={e=>setKForm({...kForm, handle:e.target.value})} placeholder="@seu_perfil_exclusivo" />
             </Field>
           )}

           <Btn onClick={handleKSubmit} disabled={loading} full variant="primary" style={{marginTop:"12px", height:"60px"}}>
              {loading ? "PROCESSANDO..." : `VINCULAR AO SISTEMA YAFA ✦`}
           </Btn>
        </div>
      </Modal>
    </div>
  );
}
