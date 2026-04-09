import { useState, useEffect } from "react";
import { GCard as GlassCard, CrownIcon, Btn, Field, Input, StarDivider, Badge, Lbl } from "../components/UI";
import { C } from "../theme/tokens";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Admin() {
  const [auth, setAuth] = useState(false);
  const [pass, setPass] = useState("");
  const [users, setUsers] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkPass = (e) => {
    e.preventDefault();
    if(pass === "yafa2026") { setAuth(true); setPass(""); }
    else { alert("Acesso não autorizado ao núcleo Yafa."); }
  };

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const hdrs = { "x-admin-secret": "yafah_admin_2024" };
      const [resUsers, resMetrics] = await Promise.all([
        fetch(`${API_URL}/api/auth/users`),
        fetch(`${API_URL}/api/admin/metrics`, { headers: hdrs })
      ]);
      if (resUsers.ok) setUsers(await resUsers.json());
      if (resMetrics.ok) setMetrics(await resMetrics.json());
    } catch(err) {
      console.error(err);
    } finally { 
      setLoading(false); 
    }
  };

  useEffect(() => { if (auth) fetchAdminData(); }, [auth]);

  const updateStatus = async (uid, status) => {
    try {
      await fetch(`${API_URL}/api/auth/update-status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario_id: uid, status })
      });
      fetchAdminData();
    } catch (err) { console.error(err); }
  };

  if (!auth) {
    return (
      <div style={{minHeight:"100vh", background:C.bg, display:"flex", alignItems:"center", justifyContent:"center", padding:"24px"}}>
        <GlassCard style={{width:"100%", maxWidth:"400px", padding:"48px", textAlign:"center", border:`1.5px solid ${C.border}`}}>
          <div style={{display:"flex", justifyContent:"center", marginBottom:"24px"}}><CrownIcon /></div>
          <h1 style={{margin:"0 0 12px", fontSize:"36px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400}}>Yafa Curator ✦</h1>
          <p style={{marginBottom:"32px", fontSize:"12px", color:C.brown_l, letterSpacing:"2px", textTransform:"uppercase", fontWeight:700}}>Acesso Restrito ao Conselho</p>
          
          <form onSubmit={checkPass} style={{display:"flex", flexDirection:"column", gap:"24px"}}>
            <Field label="Chave do Núcleo">
               <Input type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="••••••••" />
            </Field>
            <Btn type="submit" full>SINCROMIZAR ACESSO ✦</Btn>
          </form>
          
          <p style={{marginTop:"32px", color:C.brown_l, fontSize:"10px", fontFamily:C.sans, letterSpacing:"1.5px"}}>CURADORIA SUPREMA & AUDITORIA</p>
        </GlassCard>
      </div>
    );
  }

  return (
    <div style={{minHeight:"100vh", background:C.bg, padding:"60px"}}>
      <nav style={{padding:"0 0 48px", borderBottom:`1.5px solid ${C.border}`, marginBottom:"60px", display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <div style={{display:"flex", alignItems:"center", gap:"16px"}}>
           <CrownIcon />
           <h1 style={{margin:0, fontSize:"28px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400}}>Yafa Curator Hub ✦</h1>
        </div>
        <Btn variant="ghost" onClick={()=>setAuth(false)}>ENCERRAR SESSÃO CURADORIA</Btn>
      </nav>

      <section style={{maxWidth:"1200px", margin:"0 auto"}}>
        <div style={{display:"flex", justifyContent:"space-between", alignItems:"baseline", marginBottom:"40px"}}>
           <div>
              <Lbl>Gestão de Convites & Membros</Lbl>
              <h2 style={{margin:0, fontSize:"32px", color:C.brown, fontFamily:C.serif, fontWeight:400}}>Curadoria de Empreendedoras</h2>
           </div>
           <Badge status="ativo" label={`TOTAL: ${users.length} MEMBROS`} />
        </div>

        {metrics && (
          <div style={{display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(250px, 1fr))", gap:"24px", marginBottom:"60px"}}>
             <GlassCard style={{padding:"24px", border:`1.5px solid ${C.border}`}}>
               <Lbl>INTELIGÊNCIA ARTIFICIAL (RAG)</Lbl>
               <h3 style={{fontSize:"24px", margin:"12px 0 4px", color:C.brown, fontFamily:C.sans}}>{metrics.rag.total_sessions} Consultas</h3>
               <p style={{margin:0, fontSize:"12px", color:C.brown_l}}>Latência: {metrics.rag.avg_latency_ms}ms | Precisão: {(metrics.rag.vector_precision*100).toFixed(0)}%</p>
             </GlassCard>
             
             <GlassCard style={{padding:"24px", border:`1.5px solid ${C.border}`}}>
               <Lbl>MÁQUINAS PREDITIVAS (MLOPS)</Lbl>
               <h3 style={{fontSize:"24px", margin:"12px 0 4px", color:C.brown, fontFamily:C.sans}}>{metrics.ml.forecasting_mape_percent.toFixed(1)}% Erro (MAPE)</h3>
               <p style={{margin:0, fontSize:"12px", color:C.brown_l}}>F1 Anomalias: {metrics.ml.anomaly_f1_score}</p>
             </GlassCard>
             
             <GlassCard style={{padding:"24px", border:`1.5px solid ${C.border}`}}>
               <Lbl>AQUISIÇÃO E PRODUTO</Lbl>
               <h3 style={{fontSize:"24px", margin:"12px 0 4px", color:C.gold, fontFamily:C.serif}}>R$ {metrics.product.capital_gerenciado_total.toLocaleString()}</h3>
               <p style={{margin:0, fontSize:"12px", color:C.brown_l}}>Capital Gerenciado na Yafa Plataforma</p>
             </GlassCard>
          </div>
        )}

        <GlassCard style={{overflow:"hidden", border:`1.5px solid ${C.border}`}}>
          <table style={{width:"100%", borderCollapse:"collapse", textAlign:"left"}}>
            <thead>
              <tr style={{background:C.surface, borderBottom:`1.5px solid ${C.border}`}}>
                <th style={THS}>NOME / ENTIDADE</th>
                <th style={THS}>CPF / CNPJ</th>
                <th style={THS}>CADASTRO</th>
                <th style={THS}>STATUS</th>
                <th style={THS}>CURADORIA</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} style={{borderBottom:`1px solid ${C.border}`, transition:"0.3s"}}>
                  <td style={TDS}>
                    <div style={{display:"flex", alignItems:"center", gap:"12px"}}>
                       <div style={{width:"32px", height:"32px", borderRadius:"50%", background:C.bg, display:"flex", alignItems:"center", justifyContent:"center", color:C.brown, fontWeight:700, fontSize:"11px", border:`1px solid ${C.border}`}}>{u.nome?.[0]}</div>
                       <span style={{color:C.brown, fontWeight:600}}>{u.nome}</span>
                    </div>
                  </td>
                  <td style={TDS}><span style={{fontSize:"12px", color:C.brown_l}}>{u.cpf_cnpj}</span></td>
                  <td style={TDS}><span style={{fontSize:"11px", color:C.brown_l}}>{new Date().toLocaleDateString()}</span></td>
                  <td style={TDS}><Badge status={u.status} /></td>
                  <td style={TDS}>
                    <div style={{display:"flex", gap:"8px"}}>
                      {u.status === "pendente" && (
                        <Btn onClick={()=>updateStatus(u.id, "ativo")} style={{padding:"8px 16px", fontSize:"9px", background:C.success, border:"none"}}>ATIVAR</Btn>
                      )}
                      {u.status !== "bloqueado" && (
                        <Btn variant="outline" onClick={()=>updateStatus(u.id, "bloqueado")} style={{padding:"8px 16px", fontSize:"9px", borderColor:C.danger, color:C.danger}}>BLOQUEAR</Btn>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {loading && <div style={{padding:"60px", textAlign:"center", color:C.brown_l, fontStyle:"italic"}}>PROCESSANDO DADOS SUPREMOS...</div>}
        </GlassCard>
      </section>

      <footer style={{marginTop:"80px", textAlign:"center"}}>
         <StarDivider text="Segurança de Dados Auditoria Yafa" />
      </footer>
    </div>
  );
}

const THS = { padding:"24px", fontSize:"10px", color:C.brown_l, letterSpacing:"2px", fontWeight:700, textTransform:"uppercase" };
const TDS = { padding:"24px", fontSize:"14px" };
