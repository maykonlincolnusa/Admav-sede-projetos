import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { GCard as GlassCard, Lbl, StarDivider, Pill, Btn, Field, Input, Modal } from "../../components/UI";
import { C } from "../../theme/tokens";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Finance() {
  const { user } = useOutletContext();
  const [summary, setSummary] = useState({ total_receita: 0, total_despesa: 0, lucro: 0 });
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modal, setModal]     = useState(false);
  const [form, setForm]       = useState({ valor: "", tipo: "receita", categoria: "Serviços", descricao: "" });

  const fetchData = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const uId = user.id === 'dev_mode' ? 'dev_mode' : user.id;
      const headers = { "x-user-id": uId };
      const [resSum, resHist] = await Promise.all([
        fetch(`${API_URL}/api/finance/summary`, { headers }),
        fetch(`${API_URL}/api/finance/history`, { headers })
      ]);
      
      if (resSum.ok) setSummary(await resSum.json());
      if (resHist.ok) setHistory(await resHist.ok ? await resHist.json() : []);
    } catch (err) {
      console.error("Erro financeiro:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

  const handleAdd = async () => {
    if (!form.valor) return;
    setLoading(true);
    try {
      const uId = user.id === 'dev_mode' ? 'dev_mode' : user.id;
      const res = await fetch(`${API_URL}/api/finance/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "x-user-id": uId },
        body: JSON.stringify({ ...form, valor: parseFloat(form.valor), usuario_id: uId })
      });
      if (res.ok) {
        setModal(false);
        setForm({ valor: "", tipo: "receita", categoria: "Serviços", descricao: "" });
        fetchData();
      }
    } catch (err) {
      alert("Erro ao salvar registro");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if(!window.confirm("Deseja excluir este lançamento estratégico?")) return;
    try {
      const uId = user.id === 'dev_mode' ? 'dev_mode' : user.id;
      await fetch(`${API_URL}/api/finance/${id}`, {
        method: "DELETE",
        headers: { "x-user-id": uId }
      });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{display:"flex",flexDirection:"column",gap:"40px",animation:"fadeUp 1.2s cubic-bezier(0.16, 1, 0.3, 1)"}}>
      
      {/* ✦ Financial Intelligence Header */}
      <section>
         <Lbl>Gestão de Lucro & Escala</Lbl>
         <h2 style={{margin:"8px 0 12px", fontSize:"36px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400}}>Saúde Financeira ✦</h2>
         <p style={{margin:0, fontSize:"14px", color:C.brown_l, fontFamily:C.sans, lineHeight:1.7, maxWidth:"600px"}}>
            Visualize o fluxo de caixa do seu império com clareza editorial. O lucro é o primeiro passo para o reinvestimento estratégico.
         </p>
      </section>

      {/* ✦ Summary Grid Cards */}
      <div style={{display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(240px, 1fr))", gap:"24px"}}>
        <CardStat title="Receita Bruta" val={summary.total_receita} color={C.brown} icon="📈" />
        <CardStat title="Despesas Totais" val={summary.total_despesa} color={C.brown_l} icon="📉" />
        <CardStat title="Lucro Líquido" val={summary.lucro} color={C.gold} icon="💎" highlight />
        <CardStat title="Previsão ML (30d)" val={summary.forecast_next_month || 0} color={C.gold} icon="🔮" bg={C.success} />
      </div>

      <div style={{display:"grid", gridTemplateColumns:"1.6fr 1fr", gap:"48px", alignItems:"start"}}>
        
        {/* ✦ Transaction List Editorial */}
        <GlassCard style={{padding:"40px", border:`1.5px solid ${C.border}`}}>
          <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"32px"}}>
             <Lbl>Histórico Premium</Lbl>
             <Btn onClick={()=>setModal(true)} variant="primary" style={{padding:"12px 24px", fontSize:"10px"}}>+ NOVO LANÇAMENTO</Btn>
          </div>
          
          <div style={{display:"flex", flexDirection:"column", gap:"16px"}}>
            {history.length === 0 ? (
              <p style={{textAlign:"center", color:C.brown_l, padding:"60px", fontStyle:"italic", fontSize:"14px"}}>Seu livro de caixa está limpo e pronto para o primeiro registro.</p>
            ) : (
              history.map(h => (
                <div key={h.id} style={{display:"flex", alignItems:"center", gap:"24px", padding:"20px", borderBottom:`1.5px solid ${C.border}`, transition:"0.3s"}}>
                  <div style={{width:"44px", height:"44px", borderRadius:"50%", background:h.tipo==="receita"?`${C.success}08`:`${C.danger}08`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:"18px", border:`1px solid ${C.border}`}}>
                    {h.tipo==="receita" ? "✦" : "○"}
                  </div>
                  <div style={{flex:1}}>
                    <p style={{margin:0, color:C.brown, fontSize:"15px", fontWeight:600}}>{h.descricao || h.categoria}</p>
                    <p style={{margin:"2px 0 0", color:C.brown_l, fontSize:"11px", letterSpacing:"1px", textTransform:"uppercase"}}>{h.categoria} · {new Date(h.data).toLocaleDateString()}</p>
                  </div>
                  <div style={{textAlign:"right", marginRight:"24px"}}>
                    <p style={{margin:0, color:h.tipo==="receita"?C.brown:C.danger, fontSize:"18px", fontWeight:700, fontFamily:C.serif}}>
                      {h.tipo==="receita" ? "+" : "-"} R$ {h.valor.toLocaleString()}
                    </p>
                  </div>
                  <button onClick={()=>handleDelete(h.id)} style={{background:"none", border:"none", cursor:"pointer", color:C.brown_l, fontSize:"18px", opacity:0.4}}>×</button>
                </div>
              ))
            )}
          </div>
        </GlassCard>

        {/* ✦ Yafa Intelligence Advice */}
        <GlassCard style={{padding:"40px", background:C.bg, border:`2.5px solid ${C.border}`, position:"relative", overflow:"hidden"}}>
           <div style={{position:"absolute", top:"-20px", right:"-20px", opacity:0.05}}><CrownSm size={120} /></div>
           <div style={{display:"flex", alignItems:"center", gap:"16px", marginBottom:"24px"}}>
              <span style={{fontSize:"32px"}}>👸</span>
              <Lbl>Yafa Strategist</Lbl>
           </div>
           
           <div style={{display:"flex", flexDirection:"column", gap:"24px"}}>
              <p style={{margin:0, fontSize:"16px", color:C.brown, fontStyle:"italic", lineHeight:1.8, fontFamily:C.serif}}>
                "{summary.lucro > 0 
                  ? `Impressionante. Seu lucro consolidado de R$ ${summary.lucro.toLocaleString()} (Margem: ${summary.margem_lucro || 0}%) abre portas para novos horizontes. Nossa IA de Time Series prevê uma receita de R$ ${(summary.forecast_next_month || 0).toLocaleString()} no próximo ciclo. Recomendo um aporte de 12% em Branding para suportar este crescimento.`
                  : "Uma pausa estratégica é necessária. Vamos analisar seus custos operacionais via Isolation Forest para garantir que sua margem de contribuição seja protegida imediatamente."
                }"
              </p>
              
              <StarDivider text="Plano Sugerido" />

              <div style={{display:"flex", flexDirection:"column", gap:"14px"}}>
                {[
                  {l:"Marketing de Luxo", p:"15%"},
                  {l:"Otimização de Operação", p:"10%"},
                  {l:"Reserva Estratégica", p:"5%"}
                ].map(p=>(
                  <div key={p.l} style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
                    <span style={{fontSize:"12px", color:C.brown_l, fontWeight:600}}>{p.l}</span>
                    <span style={{fontSize:"13px", color:C.brown, fontWeight:700}}>{p.p}</span>
                  </div>
                ))}
              </div>

              <Btn variant="outline" full style={{borderColor:C.brown, color:C.brown, fontSize:"10px", marginTop:"16px"}}>SOLICITAR ANÁLISE COMPLETA ✦</Btn>
           </div>
        </GlassCard>
      </div>

      {/* ✦ Minimalist Premium Modal */}
      <Modal isOpen={modal} onClose={()=>setModal(false)} title="Treinar Financeiro Yafa">
         <div style={{display:"flex", flexDirection:"column", gap:"28px"}}>
           <div style={{display:"flex", gap:"1px", background:C.border, padding:"1px", borderRadius:"0px"}}>
              {[{id:"receita",l:"RECEITA"},{id:"despesa",l:"DESPESA"}].map(t=>(
                <button key={t.id} onClick={()=>setForm({...form, tipo:t.id})} style={{flex:1, padding:"14px", border:"none", background:form.tipo===t.id?"#fff":C.bg, color:form.tipo===t.id?C.brown:C.brown_l, fontSize:"10px", fontWeight:700, cursor:"pointer", letterSpacing:"1.5px"}}>{t.l}</button>
              ))}
           </div>

           <Field label="Valor Investido ou Recebido">
              <Input type="number" value={form.valor} onChange={e=>setForm({...form, valor:e.target.value})} placeholder="0.00" />
           </Field>
           
           <Field label="Categoria Estratégica">
              <Input value={form.categoria} onChange={e=>setForm({...form, categoria:e.target.value})} placeholder="Ex: Venda Premium, Marketing, Aluguel" />
           </Field>
           
           <Field label="Descrição Curta (Opcional)">
              <Input value={form.descricao} onChange={e=>setForm({...form, descricao:e.target.value})} placeholder="Detalhes do movimento financeiro" />
           </Field>

           <Btn onClick={handleAdd} disabled={loading} full variant="primary" style={{marginTop:"10px", height:"60px"}}>
              {loading ? "PROCESSANDO..." : "CONFIRMAR REGISTRO ✦"}
           </Btn>
         </div>
      </Modal>

    </div>
  );
}

function CardStat({ title, val, color, icon, highlight }) {
  return (
    <GlassCard style={{padding:"32px", display:"flex", alignItems:"center", gap:"24px", border:highlight?`2px solid ${C.gold}`:`1.5px solid ${C.border}`, background:highlight?`${C.gold}03`:"#fff"}}>
      <div style={{width:"60px", height:"60px", borderRadius:"0px", background:highlight?`${C.gold}15`:`${C.border}44`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:"28px"}}>{icon}</div>
      <div>
        <p style={{margin:"0 0 6px", fontSize:"10px", color:C.brown_l, fontWeight:700, letterSpacing:"2px", textTransform:"uppercase"}}>{title}</p>
        <h3 style={{margin:0, fontSize:"32px", color:C.brown, fontWeight:400, fontFamily:C.serif}}>R$ {val.toLocaleString()}</h3>
      </div>
    </GlassCard>
  );
}
