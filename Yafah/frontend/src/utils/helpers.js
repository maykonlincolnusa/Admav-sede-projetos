import { MOCK_DB } from './mockData';

export const fmtDoc = v => {
  const d = v.replace(/\D/g,"").slice(0,14);
  if(d.length<=11) return d.replace(/(\d{3})(\d)/,"$1.$2").replace(/(\d{3})(\d)/,"$1.$2").replace(/(\d{3})(\d{1,2})$/,"$1-$2");
  return d.replace(/(\d{2})(\d)/,"$1.$2").replace(/(\d{3})(\d)/,"$1.$2").replace(/(\d{3})(\d)/,"$1/$2").replace(/(\d{4})(\d{1,2})$/,"$1-$2");
};

export const fmtPhone = v => {
  const d = v.replace(/\D/g,"").slice(0,11);
  return d.replace(/(\d{2})(\d)/,"($1) $2").replace(/(\d{5})(\d{1,4})$/,"$1-$2");
};

export async function mockLogin(nome, doc) {
  await new Promise(r => setTimeout(r, 950));
  const d = doc.replace(/\D/g,""), n = nome.trim().toLowerCase();
  const f = MOCK_DB.find(u => u.documento.replace(/\D/g,"")=== d && u.nome.trim().toLowerCase()===n && u.status==="ativo");
  if(!f) throw new Error("Não autorizado");
  return f;
}
