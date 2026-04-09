import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GCard as GlassCard, CrownIcon, Field, Input, Btn, Glows, GlobalStyles, StarDivider } from "../components/UI";
import { C } from "../theme/tokens";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Login() {
  const [nome, setNome]     = useState("");
  const [cpf, setCpf]       = useState("");
  const [loading, setLoad]   = useState(false);
  const [error, setError]   = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!nome || !cpf) { setError("Por favor, preencha todos os campos."); return; }
    setLoad(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, cpf_cnpj: cpf })
      });

      if (res.ok) {
        const user = await res.json();
        localStorage.setItem("yafa_user", JSON.stringify(user));
        navigate("/dashboard");
      } else {
        const d = await res.json();
        setError(d.detail || "Usuário não encontrado ou pendente.");
      }
    } catch (err) {
      setError("Erro de conexão com o servidor Yafa.");
    } finally {
      setLoad(false);
    }
  };

  return (
    <div style={{minHeight:"100vh", background:C.bg, display:"flex", alignItems:"center", justifyContent:"center", padding:"24px", position:"relative", overflow:"hidden"}}>
      <GlobalStyles />
      <Glows />
      
      <div style={{width:"100%", maxWidth:"440px", position:"relative", zIndex:1, textAlign:"center"}}>
        
        {/* Branding Editorial */}
        <div style={{marginBottom:"48px", animation:"fadeUp 1.2s ease"}}>
          <div style={{display:"flex", justifyContent:"center", marginBottom:"24px"}}>
             <CrownIcon />
          </div>
          <h1 style={{margin:"0 0 12px", fontSize:"48px", color:C.brown, fontFamily:C.serif, fontStyle:"italic", fontWeight:400, letterSpacing:"-1px"}}>Yafa ✦</h1>
          <p style={{margin:0, fontSize:"12px", color:C.brown_l, fontFamily:C.sans, letterSpacing:"4px", textTransform:"uppercase", fontWeight:600}}>Inteligência para o Luxo</p>
        </div>

        {/* Login Form */}
        <GlassCard style={{padding:"48px", animation:"fadeUp 1.5s ease", border:`1.5px solid ${C.border}`}}>
          <form onSubmit={handleLogin} style={{display:"flex", flexDirection:"column", gap:"32px"}}>
            <Field label="Identificação do Negócio" hint="Nome da Titular">
              <Input 
                value={nome} 
                onChange={e=>setNome(e.target.value)} 
                placeholder="Ex: Mariana Vasconcelos" 
                hasError={!!error}
              />
            </Field>

            <Field label="Chave de Acesso Principal" hint="CPF ou CNPJ">
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
              <Btn type="submit" disabled={loading} full style={{height:"60px", fontSize:"12px"}}>
                {loading ? "VALIDANDO ACESSO..." : "AUTENTICAR EM YAFA ✦"}
              </Btn>
            </div>
            
            <StarDivider text="Exclusividade" />
            <p style={{margin:0, fontSize:"11px", color:C.brown_l, fontFamily:C.sans, lineHeight:1.6}}>
              Plataforma restrita a parceiras e marcas de beleza de alto impacto.
            </p>
          </form>
        </GlassCard>

        {/* Footer Link */}
        <div style={{marginTop:"32px", animation:"fadeIn 2s ease"}}>
          <button 
             onClick={()=>navigate("/cadastro")}
             style={{background:"none", border:"none", color:C.brown, fontFamily:C.sans, fontSize:"12px", letterSpacing:"1px", fontWeight:600, cursor:"pointer", textDecoration:"underline", opacity:0.8}}
          >
            SOLICITAR CONVITE PARA A PLATAFORMA
          </button>
        </div>

      </div>
    </div>
  );
}
