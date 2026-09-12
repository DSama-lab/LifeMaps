// Regenerates index.html (public demo) from index.private.html (real seed, never versioned).
// Usage: node build-demo.js
'use strict';
const fs = require('fs');
const SRC = 'index.private.html';
const OUT = 'index.html';

const seedNodes = `function seedNodes(){
  const N=[];
  const add=(id,title,cat,status,desc,phase,loc)=>N.push({data:{id,title,cat,status,desc,phase:phase||null,loc:loc||null}});
  // --- Raiz ---
  add('raiz','Objetivo: Vida Portátil + Renda Internacional','raiz','planejado',
    'Construir renda remota + experiência internacional até conquistar residência em um país com boa qualidade de vida. Seed pública de demonstração — dados fictícios.');
  // --- Fases ---
  add('f1','Fase 1 · Base (país atual)','fase','ativo',
    'Reunir capital inicial, aprender habilidades remotas e criar projetos que gerem renda. REGRA: se a viagem não acontecer, o dinheiro permanece.',1,'brasil');
  add('f2','Fase 2 · Trabalhar no Exterior','fase','planejado',
    'Gerar renda + experiência. Referência US$1.500/mês. Meta inicial ~R$15.000 em 4 meses.',2,'nova zelandia');
  add('f3','Fase 3 · Ampliar Renda','fase','planejado',
    'Enquanto trabalha: estudar novas habilidades, idiomas e operações digitais.',3);
  add('f4','Fase 4 · Capital de Mobilidade','fase','pendente',
    'Lucros extras financiam passagem + seguro + estadia + reserva.',4);
  // --- Planos A/B/C/D + saídas ---
  add('pa','Plano A · Austrália','plano','planejado',
    'Projeto + experiência + lucro vira argumento. Trabalhar legalmente, acumular capital.','','australia');
  add('pb','Plano B · Canadá','plano','pendente',
    'SE a Austrália não acontecer: continuar acumulando e mirar o Canadá. Emprego nunca é garantido.','','canada');
  add('pc','Plano C · Chile','plano','pendente',
    'SE Austrália e Canadá não vingarem. Entrada facilitada, custo de vida menor, trabalho remoto possível.','','chile');
  add('pd','Plano D · Outro país','plano','pendente',
    'Avaliado por custo de entrada, salário líquido, moradia, legalidade e rota de residência.','','argentina');
  add('saida','Saídas Alternativas','plano','pendente',
    'Se os projetos começarem a lucrar, o orçamento pode ir direto a outra oportunidade adequada, sem esperar por rota específica.');
  // --- Regras / princípios ---
  add('r7k','Regra do Fundo Sagrado','regra','ativo',
    '40% da renda líquida fica reservada. O restante cobre despesas/operação; todo o sobra vai para a reserva.');
  add('princ','Princípio Final','regra','ativo',
    'DINHEIRO → EXPERIÊNCIA → QUALIFICAÇÃO → MOBILIDADE → RESIDÊNCIA. Nenhuma decisão importante por causa de um vídeo; verificar tudo antes.');
  add('contig','Regra de Contingência','regra','ativo',
    'Plano A → B → C → D. Se uma rota cair, patrimônio e habilidades permanecem.');
  // --- Financeiro ---
  add('reserva','Reserva Financeira','financeiro','ativo',
    'META: reserva de emergência no país-base. Depois, fundo de mobilidade para a próxima etapa.');
  add('numeros','Números-base (demo)','financeiro','ativo',
    'US$1≈R$5 · Meta mensal US$1.500 · Reserva R$12.000 · Fundo mobilidade R$15k+.');
  // --- Pessoal ---
  add('familia','Família e Vínculos','pessoal','ativo',
    'Mobilidade nunca pode significar perder vínculos. Contato periódico organizado e presença à distância.');
  add('projeto_vida','O Projeto de Vida é a Razão','pessoal','ativo',
    'Não é fugir. É correr atrás do que faz bem: conhecer o mundo, aprender e construir uma vida ampla.');
  add('sonho','O Objetivo: Vida Internacional','pessoal','ativo',
    'Conhecer e viver em lugares distantes (Nova Zelândia, Canadá, Japão). Não forçar entrada sem recursos.');
  add('plot','O Plot Twist','pessoal','planejado',
    'A próxima grande mudança será intencional: sair quando estiver preparado. Privacidade operacional para quem precisa saber.');
  // --- Info / países ---
  add('aus','Nova Zelândia · Destino de Referência','info','planejado',
    'Porta para estilo de vida remoto. Visto de trabalho exige oferta ou escola. Naturalização sob condições.','','nova zelandia');
  add('ir','Irlanda / União Europeia','info','planejado',
    'Estudo separado. Regras de trabalho e residência variam por país membro.');
  add('kit','Kit de Sobrevivência Internacional','info','planejado',
    'Transformar a vida em algo portátil: notebook, documentos, cartão internacional, eSIM, cloud/backup.');
  add('passagens','Reservas de Passagens','financeiro','pendente',
    'Reservar com antecedência; preços reais recalculados quando houver data.');
  add('curiosidade','Residência ≠ Cidadania','info','ativo',
    'Residência permanente é diferente de cidadania. Entender a diferença antes de planejar prazos e custos.','','estados unidos');
  add('seguranca','Nota de Segurança e Realidade','regra','ativo',
    'Plano ambicioso, mas legal e verificável. Não contar com promessas sem documentação oficial. Não apostar tudo em uma narrativa.');
  add('seed','SEED · Plano Vetorial (demo)','info','ativo',
    'Este documento é a SEED demonstrativa do sistema. Cada fase vira plano vetorial: objetivos, dependências, orçamento, critérios de sucesso.');
  add('canada','Canadá · Referência Internacional','info','planejado',
    'Exemplo de destino de longo prazo — entrada via estudo, oferta de emprego ou Express Entry. Dados fictícios.','','canada');
  add('demo','Demo · Seed Pública','info','planejado',
    'Este projeto é uma demonstração com dados fictícios. Não representa o plano pessoal do autor.');
  return N;
}`;

const seedEdges = `function seedEdges(){
  const E=[];
  const add=(s,t,cond)=>E.push({data:{id:'e'+E.length,source:s,target:t,cond:cond||null}});
  // fluxo principal
  add('raiz','f1');
  add('f1','f2');
  add('f1','f3');
  add('f2','f4');
  add('f3','f4');
  // planos
  add('f2','pa');
  add('pa','pb','if pa.ativo==false → ativar b (Plano B quando Austrália não acontecer)');
  add('pb','pc','if pb.ativo==false → ativar c (Plano C quando Canadá não vingar)');
  add('pc','pd','if pc.ativo==false → ativar d (Plano D quando Chile não vingar)');
  add('saida','pc');
  // países / info
  add('f2','aus');
  add('aus','curiosidade');
  add('pc','aus');
  add('f2','ir');
  add('ir','curiosidade');
  // financeiro
  add('f1','reserva');
  add('reserva','r7k');
  add('f4','passagens');
  add('reserva','f4');
  // princípios
  add('princ','raiz');
  add('contig','f4');
  add('sonho','raiz');
  add('familia','raiz');
  // infos complementares
  add('f2','kit');
  add('seguranca','curiosidade');
  add('seed','raiz');
  add('f1','passagens');
  add('demo','raiz');
  return E;
}`;

const FUNCS = [
  ['seedNodes', seedNodes],
  ['seedEdges', seedEdges]
];

let src;
try {
  src = fs.readFileSync(SRC, 'utf8');
} catch (e) {
  console.error('[build-demo] missing ' + SRC + ' — first run: Copy-Item index.html index.private.html');
  process.exit(1);
}

for (const [name, body] of FUNCS) {
  const pattern = new RegExp('function ' + name + '\\(\\)\\s*\\{[\\s\\S]*?return [NE];\\s*\\}');
  if (!pattern.test(src)) {
    console.error('[build-demo] function ' + name + ' not found in ' + SRC);
    process.exit(1);
  }
  src = src.replace(pattern, body);
}

// Neutralize UI copy that references the author's real routes/personal facts.
const SANITIZE = [
  ['Malásia, Filipinas, Montenegro', 'Nova Zelândia, Canadá, Irlanda'],
  ['e se eu descartar a Malásia e ir só para o Canadá?', 'e se eu descartar o Plano B e focar no Canadá?'],
  ['quero adicionar um custo extra de R$3k na vinda', 'quero adicionar um custo extra na próxima etapa'],
  ['quero adicionar um custo extra na vinda', 'quero adicionar um custo extra na próxima etapa'],
  ['Malásia 1ª vez, depois Tailândia e Filipinas onde já trabalhou', 'morou em Lisboa 2 anos, trabalhou em Auckland e já visitou o Chile'],
  ['Malaysia first time, then Thailand and the Philippines where you already worked', 'lived in Lisbon for 2 years, worked in Auckland and visited Chile'],
  ['I met João in Manila.', 'I visited Chile in 2019.'],
  ['Plano B (Filipinas) só ativa SE Malásia NÃO acontecer', 'Plano B (Canadá) só ativa SE Austrália não acontecer'],
  ['ex: Malásia)', 'ex: Nova Zelândia)'],
  ['e.g.: Malaysia, Philippines, Montenegro', 'e.g.: New Zealand, Canada, Ireland'],
  ['Plan B (Philippines) only activates IF Malaysia does NOT happen', 'Plan B (Canada) only activates IF Australia does NOT happen'],
  ['(vaga Breslávia/ID LOGISTIC)', 'cidades úteis'],
  ['Morei em São Paulo 2 anos. Trabalhei em Chiang Mai em 2019. Conheci o João em Manila.', 'Morei em São Paulo 2 anos e trabalhei em Auckland em 2015.'],
  ['I worked in Chiang Mai in 2019. I visited Chile in 2019.', 'I worked in Auckland in 2015. I visited Chile in 2019.'],
];
for (const [from, to] of SANITIZE) {
  src = src.split(from).join(to);
}

// Regex-based sanitization (exact match, tolerant to accents/escaping in the AI prompt).
src = src.replace(/"Tail[^"]*", "Chiang Mai", "Manila", "Assun[^"]*"/, '"Berlim", "Cidade do México", "Lima"');

fs.writeFileSync(OUT, src, 'utf8');
console.log('[build-demo] ' + OUT + ' regenerated from ' + SRC + ' — public demo seed applied.');