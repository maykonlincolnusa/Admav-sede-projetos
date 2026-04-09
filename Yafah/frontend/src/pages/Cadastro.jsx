import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GCard as GlassCard, CrownIcon, Field, Input, Btn, Glows, GlobalStyles, StarDivider } from "../components/UI";
import { C } from "../theme/tokens";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Cadastro() {
  const [nome, setNome]     = useState("");
  const [cpf, setCpf]       = useState("");
  const [loading, setLoad]   = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError]   = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!nome || !cpf) { setError("Campos obrigatórios para curadoria."); return; }
    setLoad(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, cpf_cnpj: cpf })
      });

      if (res.ok) {
        setSuccess(true);
      } else {
        const d = await res.json();
        setError(d.detail || "Erro ao processar solicitação.");
      }
    } catch (err) {
      setError("Erro de conexão com o sistema Yafa.");
    } finally {
      setLoad(false);
    }
  };

  if (success) {
    return (
      <div style={{minHeight:"100vh", background:C.bg, display:"flex", alignItems:"center", justifyContent:"center", padding:"24px"}}>
        <GlobalStyles />
        <GlassCard style={{maxWidth:"440px", padding:"60px", textAlign:"center", border:`1.5px solid ${C.border}`}}>
          <div style={{fontSize:"60px", marginBottom:"32px"}}>✦</div>
          <h2 style={{margin:"0 0 16px", fontSize:"32px", color:C.brown, fontFamily:C.serif, fontStyle:"italic"}}>Solicitação Enviada</h2>
          <p style={{margin:0, fontSize:"15px", color:C.brown_l, lineHeight:1.8}}>Sua marca entrou em nossa fila de curadoria. Notificaremos você assim que o Conselho Yafa validar seu acesso exclusivo.</p>
          <div style={{marginTop:"48px"}}>
            <Btn onClick={()=>navigate("/login")} full variant="outline" style={{borderColor:C.brown, color:C.brown}}>VOLTAR AO INÍCIO ✦</Btn>
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div style={{minHeight:"100vh", background:C.bg, display:"flex", alignItems:"center", justifyContent:"center", padding:"24px", position:"relative", overflow:"hidden"}}>
      <GlobalStyles />
      <Glows />
      
      <div style={{width:"100%", maxWidth:"440px", position:"relative", zIndex:1, textAlign:"center"}}>
        
        {/* Branding Editorial */}
        <div style={{marginBottom:"48px", animation:"fadeUp 1s ease"}}>
          <div style={{display:"flex", justifyContent:"center", marginBottom:"24px"}}>
             <CrownIcon />
          </div>
          <h1 style={{margin:"0 0 12px", fontSize:"44px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400}}>Yafa ✦</h1>
          <p style={{margin:0, fontSize:"12px", color:C.brown_l, fontFamily:C.sans, letterSpacing:"4px", textTransform:"uppercase", fontWeight:600}}>Solicitar Convite VIP</p>
        </div>

        {/* Cadastro Form */}
        <GlassCard style={{padding:"48px", animation:"fadeUp 1.3s ease", border:`1.5px solid ${C.border}`}}>
          <form onSubmit={handleRegister} style={{display:"flex", flexDirection:"column", gap:"32px"}}>
            <Field label="Nome da Empreendedora" hint="Identidade Titular">
              <Input 
                value={nome} 
                onChange={e=>setNome(e.target.value)} 
                placeholder="Ex: Amanda Rebouças" 
                hasError={!!error}
              />
            </Field>

            <Field label="Documento Identificador" hint="CPF ou CNPJ">
              <Input 
                value={cpf} 
                onChange={e=>setCpf(e.target.value)} 
                placeholder="000.000.000-00" 
                type="text"
                hasError={!!error}
              />
            </Field>

            {error && (
              <p style={{margin:0, fontSize:"13px", color:C.danger, fontStyle:"italic", textAlign:"left"}}>
                ✦ {error}
              </p>
            )}

            <div style={{marginTop:"12px"}}>
              <Btn type="submit" disabled={loading} full style={{height:"60px", fontSize:"11px"}}>
                {loading ? "ENVIANDO PARA CURADORIA..." : "SOLICITAR ACESSO EXCLUSIVO ✦"}
              </Btn>
            </div>
            
            <StarDivider text="Seletividade" />
            <p style={{margin:0, fontSize:"11px", color:C.brown_l, fontFamily:C.sans, lineHeight:1.7}}>
              A Yafa é uma plataforma fechada para negócios de alto nível. Seu cadastro passará por análise manual.
            </p>
          </form>
        </GlassCard>

        {/* Footer Link */}
        <div style={{marginTop:"32px"}}>
          <button 
             onClick={()=>navigate("/login")}
             style={{background:"none", border:"none", color:C.brown_l, fontFamily:C.sans, fontSize:"11px", letterSpacing:"1.5px", fontWeight:600, cursor:"pointer", opacity:0.8}}
          >
            POSSUI CONVITE ATIVO? ACESSAR PORTAL
          </button>
        </div>

      </div>
    </div>
  );
}
