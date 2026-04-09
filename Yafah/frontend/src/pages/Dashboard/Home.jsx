
import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { StarDivider, GCard as GlassCard, Lbl } from "../../components/UI";
import { C } from "../../theme/tokens";

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Home() {
   const { user } = useOutletContext();
   const [loading, setLoad] = useState(true);
   const [metrics, setMetrics] = useState({ total_receita: 0, lucro: 0, forecast_next_month: 0, margem_lucro: 0 });

   useEffect(() => {
      const fetchHomeData = async () => {
         try {
            const uId = user?.id === 'dev_mode' ? 'dev_mode' : user?.id;
            if (!uId) return;

            const res = await fetch(`${API_URL}/api/finance/summary`, {
               headers: { "x-user-id": uId }
            });
            if (res.ok) setMetrics(await res.json());
         } catch (err) {
            console.error(err);
         } finally {
            setLoad(false);
         }
      };
      fetchHomeData();
   }, [user]);

   return (
      <div style={{ animation: "fadeUp 1.2s cubic-bezier(0.16, 1, 0.3, 1)", display: "flex", flexDirection: "column", gap: "48px" }}>

         {/* ✦ Hero Welcome Header */}
         <section style={{ textAlign: "left" }}>
            <Lbl>Bem-vinda ao seu Império</Lbl>
            <h1 style={{ margin: "8px 0 16px", fontSize: "44px", color: C.brown, fontFamily: C.serif, fontStyle: "italic", fontWeight: 400, lineHeight: 1 }}>
               Olá, {user?.nome?.split(" ")[0]} ✦
            </h1>
            <p style={{ margin: 0, fontSize: "15px", color: C.brown_l, maxWidth: "600px", lineHeight: 1.8 }}>
               Hoje é um dia perfeito para expandir sua influência e refinar seus números. A Yafa já processou as tendências do mercado para o seu negócio de beleza.
            </p>
         </section>

         {/* ✦ Financial Intelligence Quick Stats */}
         <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "32px" }}>
            <Stat label="Receita Mensal" val={`R$ ${metrics.total_receita.toLocaleString()}`} sub="Faturamento bruto consolidado" up="Metrifique o Sucesso" />
            <Stat label="Lucro Líquido" val={`R$ ${metrics.lucro.toLocaleString()}`} sub={`Margem Saudável de ${metrics.margem_lucro}%`} up="Otimização Inteligente" />
            <Stat label="Previsão ML (30d)" val={`R$ ${(metrics.forecast_next_month || 0).toLocaleString()}`} sub="Baseado em Séries Temporais" up="Auditado por Yafa" />
         </div>

         <StarDivider text="Insights Estratégicos" />

         {/* ✦ Secondary Insights Section */}
         <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: "48px", alignItems: "start" }}>

            <div style={{ display: "flex", flexDirection: "column", gap: "32px" }}>
               <GlassCard style={{ padding: "40px", border: `1.5px solid ${C.border}` }}>
                  <Lbl>Próximo Passo Financeiro</Lbl>
                  <p style={{ margin: "12px 0 24px", fontSize: "18px", color: C.brown, fontFamily: C.serif, fontStyle: "italic", lineHeight: 1.6 }}>
                     "{metrics.lucro > 0
                        ? `O fluxo constante de caixa prevê R$ ${(metrics.forecast_next_month).toLocaleString()} para o próximo mês. Ideal direcionar margens para CX e Branding.`
                        : `Mantenha a vigilância. Foque na recuperação de clientes inativos para estabilizar as operações.`
                     }"
                  </p>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", color: C.gold, fontSize: "11px", fontWeight: 700, letterSpacing: "1.5px", textTransform: "uppercase" }}>
                     <span>✦ ANALISADO POR YAFA</span>
                  </div>
               </GlassCard>

               <BibleVerse
                  verse="Onde não há conselho os projetos saem vãos, mas na multidão de conselheiros se confirmam."
                  refText="Provérbios 15:22"
               />
            </div>

            <GlassCard style={{ padding: "40px", border: `1.5px solid ${C.border}` }}>
               <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
                  <Lbl>Tendências do seu Mercado</Lbl>
                  <span style={{ fontSize: "11px", color: C.gold, fontWeight: 700, letterSpacing: "1px" }}>VER TUDO →</span>
               </div>

               <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                  {[
                     { t: "Minimalismo na Estética", d: "Aumento de 40% na busca por protocolos naturais e cleans.", icon: "◌" },
                     { t: "Influência do Quiet Luxury", d: "Consumidoras buscam marcas com comunicação discreta e alta qualidade.", icon: "✧" },
                     { t: "Sustentabilidade Consciente", d: "Valor percebido maior em produtos com embalagens refiláveis.", icon: "◈" }
                  ].map((item, idx) => (
                     <div key={idx} style={{ display: "flex", gap: "20px", borderBottom: idx === 2 ? "none" : `1px solid ${C.border}`, paddingBottom: idx === 2 ? 0 : "24px" }}>
                        <span style={{ fontSize: "20px", color: C.gold }}>{item.icon}</span>
                        <div>
                           <h4 style={{ margin: "0 0 6px", fontSize: "16px", color: C.brown, fontFamily: C.sans, fontWeight: 700 }}>{item.t}</h4>
                           <p style={{ margin: 0, fontSize: "13px", color: C.brown_l, lineHeight: 1.6 }}>{item.d}</p>
                        </div>
                     </div>
                  ))}
               </div>
            </GlassCard>

         </div>

      </div>
   );
}

function Stat({ label, val, sub, up }) {
   return (
      <GlassCard style={{ padding: "32px", border: `1.5px solid ${C.border}` }}>
         <Lbl>{label}</Lbl>
         <p style={{ margin: "12px 0 6px", fontSize: "36px", color: C.brown, fontFamily: C.serif, fontWeight: 400 }}>{val}</p>
         {sub && <p style={{ margin: 0, fontSize: "13px", color: C.brown_l, fontFamily: C.sans, letterSpacing: "0.5px" }}>{sub}</p>}
         {up && <p style={{ margin: "12px 0 0", fontSize: "11px", color: C.gold, fontFamily: C.sans, letterSpacing: "1px", fontWeight: 700 }}>✦ {up}</p>}
      </GlassCard>
   );
}

export function BibleVerse({ verse, refText }) {
   return (
      <div style={{ fontFamily: C.serif, fontStyle: "italic", textAlign: "center", padding: "24px", color: C.brown_l, lineHeight: 1.8 }}>
         <p style={{ margin: "0 0 12px", fontSize: "18px", color: C.brown, fontWeight: 400 }}>"{verse}"</p>
         <span style={{ fontSize: "12px", color: C.gold, fontWeight: 700, textTransform: "uppercase", letterSpacing: "1px" }}>- {refText}</span>
      </div>
   );
}
