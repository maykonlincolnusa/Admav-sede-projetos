export const MOCK_DB = [
  { id:"1", nome:"Maria Silva",   documento:"111.222.333-44",    email:"maria@email.com", telefone:"(21)99999-1111", tipo_negocio:"Manicure / Pedicure",  cidade:"Rio de Janeiro-RJ", status:"ativo",    instagram:"@marianails", criado_em:"2025-01-10", como_ajudar:"Quero organizar financeiro e atrair mais clientes" },
  { id:"2", nome:"Ana Costa",     documento:"98.765.432/0001-10",email:"ana@email.com",   telefone:"(11)98888-2222", tipo_negocio:"Cabeleireira",          cidade:"São Paulo-SP",      status:"ativo",    instagram:"@anacabelos", criado_em:"2025-01-15", como_ajudar:"Preciso de ajuda com marketing" },
  { id:"3", nome:"Juliana Souza", documento:"333.444.555-66",    email:"ju@email.com",    telefone:"(21)97777-3333", tipo_negocio:"Esteticista",           cidade:"Niterói-RJ",        status:"pendente", instagram:"@juestetic",  criado_em:"2025-02-01", como_ajudar:"Quero crescer nas redes sociais" },
  { id:"4", nome:"Fernanda Lima", documento:"444.555.666-77",    email:"fe@email.com",    telefone:"(31)96666-4444", tipo_negocio:"Maquiadora",            cidade:"BH-MG",             status:"pendente", instagram:"@femakeup",   criado_em:"2025-02-03", como_ajudar:"Preciso montar pacotes de serviços" },
  { id:"5", nome:"Camila Reis",   documento:"555.666.777-88",    email:"ca@email.com",    telefone:"(85)95555-5555", tipo_negocio:"Lash Designer",         cidade:"Fortaleza-CE",      status:"bloqueado",instagram:"@camilash",   criado_em:"2025-01-20", como_ajudar:"Quero abrir meu salão" },
];

export const TIPOS = ["Manicure / Pedicure","Cabeleireira","Esteticista","Maquiadora","Designer de Sobrancelhas","Micropigmentadora","Lash Designer","Salão completo","Outro"];

export const MOCK_CONV = [
  { id:"c1", uid:"1", resumo:"Precificação de esmaltação em gel", data:"2025-02-10", stars:5 },
  { id:"c2", uid:"1", resumo:"Estratégia no Instagram para atrair noivas", data:"2025-02-08", stars:4 },
  { id:"c3", uid:"2", resumo:"Como montar pacote de coloração", data:"2025-02-09", stars:5 },
];

export const IG_POSTS = [
  { id:1, tipo:"Reels", emoji:"💅", likes:1240, coments:87,  alcance:"12.4K", data:"Hoje",   legenda:"Nail art borboleta 🦋 Transformação completa! Quer o mesmo? Link na bio ✨ #nailart #manicurerj" },
  { id:2, tipo:"Foto",  emoji:"✨", likes:890,  coments:43,  alcance:"8.9K",  data:"Ontem",  legenda:"Francesinha elegante para a noiva especial 💍 #naildesigner #noivarj" },
  { id:3, tipo:"Reels", emoji:"🌸", likes:2100, coments:156, alcance:"21K",   data:"3 dias", legenda:"Unhas para o verão 🌊 Qual você escolheria? Comenta aí! #nailrj #verao" },
  { id:4, tipo:"Story", emoji:"💎", likes:0,    coments:0,   alcance:"3.2K",  data:"4 dias", legenda:"Bastidores do atendimento 🌹 Amor no que faço!" },
];

export const TT_VIDEOS = [
  { id:1, emoji:"💅", titulo:"Nail art borboleta em 60s",    views:"48.2K", likes:"3.1K", coments:"241", shares:"892",  dur:"0:58" },
  { id:2, emoji:"✨", titulo:"Gel antes e depois — incrível", views:"31.5K", likes:"2.4K", coments:"189", shares:"456",  dur:"0:45" },
  { id:3, emoji:"🌸", titulo:"5 unhas que toda noiva precisa",views:"89.1K", likes:"7.8K", coments:"612", shares:"2.1K", dur:"1:12" },
];

export const AGENDA = [
  { hora:"09:00", nome:"Ana Lima",    serv:"Gel completo",       valor:"R$150" },
  { hora:"11:00", nome:"Carol Matos", serv:"Nail art + Spa",     valor:"R$180" },
  { hora:"14:00", nome:"Bia Ferreira",serv:"Nail art exclusivo", valor:"R$200" },
  { hora:"16:30", nome:"Luiza Santos",serv:"Manutenção gel",     valor:"R$90"  },
];

export const CHAT_SUGG = [
  "Como aumentar meu ticket médio para R$ 200?",
  "Estratégia para conseguir mais clientes noivas no RJ",
  "Como precificar nail art exclusivo?",
  "Script de reativação de clientes inativos",
];

export const USER_CONTEXT = {
  id: "1",
  nome: "Maria Silva",
  tipo_negocio: "Manicure / Nail Designer",
  cidade: "Rio de Janeiro - RJ",
  instagram: "@marianails",
  tiktok: "@marianails",
  site: "marianails.com.br",
  avatar: "M",
  como_ajudar: "Quero organizar financeiro, atrair mais clientes pelo Instagram e criar pacotes premium.",
  nicho: "Especialista em nail art e gel de longa duração",
  publico: "Mulheres executivas e noivas do Rio de Janeiro",
  diferenciais: "Atendimento VIP, ambiente sofisticado, produtos importados, nail art exclusivo",
  tempo_negocio: "3 anos",
  ticket_medio: "R$ 132",
};
