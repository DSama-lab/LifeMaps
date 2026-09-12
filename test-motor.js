// Teste do motor condicional (lógica pura) — espelha o propagar do index.html
// Status: ativo(invariável) · planejado · pendente(aguarda gatilho/pré-req) · bloqueado(rota caiu) · inativo(arquivado manual)

function nodesSeed(){
  return {
    raiz:{status:'planejado'}, f1:{status:'ativo'}, f2:{status:'planejado'}, f3:{status:'planejado'},
    f4:{status:'pendente'}, pa:{status:'planejado'}, pb:{status:'pendente'}, pc:{status:'pendente'},
    pd:{status:'pendente'}, saida:{status:'pendente'}, nz:{status:'planejado'}, eu:{status:'planejado'},
    curiosidade:{status:'ativo'}, passagens:{status:'pendente'}, reserva:{status:'ativo'}, r7k:{status:'ativo'},
    fam:{status:'ativo'}, sonho:{status:'ativo'}, princ:{status:'ativo'}, contig:{status:'ativo'},
    ca:{status:'planejado'}, kit:{status:'planejado'}, seed:{status:'ativo'}, seguranca:{status:'ativo'},
    numeros:{status:'ativo'}, projeto_vida:{status:'ativo'}, plot:{status:'planejado'},
  };
}
function edgesSeed(){
  const E=[];
  const add=(s,t,c)=>E.push({s,t,c:c||null});
  add('raiz','f1'); add('f1','f2'); add('f1','f3'); add('f2','f4'); add('f3','f4');
  add('f2','pa');
  add('pa','pb','if pa.ativo==false → ativar b'); add('pb','pc','if pb.ativo==false → ativar c'); add('pc','pd','if pc.ativo==false → ativar d');
  add('saida','pc');
  add('f2','nz'); add('nz','curiosidade'); add('pc','nz'); add('f2','eu'); add('eu','curiosidade');
  add('f1','reserva'); add('reserva','r7k'); add('f4','passagens'); add('reserva','f4');
  add('princ','raiz'); add('contig','f4'); add('sonho','raiz'); add('fam','raiz');
  add('f2','kit'); add('seguranca','curiosidade'); add('seed','raiz'); add('f1','passagens');
  return E;
}

function parseCond(c){
  const sm=String(c||'').match(/if\s+(\w+)\.(\w+)\s*==\s*(true|false)/);
  return {src:sm?sm[1]:null, triggerFalse:sm&&sm[3]==='false', triggerTrue:sm&&sm[3]==='true'};
}
function condHolds(e,n){
  const p=parseCond(e.c); if(!p.src) return true;
  const st=n[p.src].status;
  if(p.triggerFalse) return st==='bloqueado'||st==='inativo';
  if(p.triggerTrue) return st==='ativo';
  return true;
}
function propagate(nodes,edges){
  let changed=true,guard=0;
  while(changed&&guard<80){ changed=false;guard++;
    for(const id of Object.keys(nodes)){
      const st=nodes[id].status;
      if(st==='ativo'||st==='inativo') continue;
      const prereqs=edges.filter(e=>e.t===id&&!e.c).map(e=>e.s);
      const conds=edges.filter(e=>e.t===id&&e.c);
      let want=null;
      if(conds.length>0){
        want = conds.every(e=>condHolds(e,nodes)) ? 'planejado':'pendente';
      } else if(prereqs.length>0){
        let blocked=false,waiting=false;
        for(const s of prereqs){
          const v=nodes[s].status;
          if(v==='bloqueado'||v==='inativo') blocked=true;
          if(v==='pendente') waiting=true;
        }
        want = blocked?'bloqueado' : waiting?'pendente' : 'planejado';
      }
      if(want&&want!==st){ nodes[id].status=want; changed=true; }
    }
  }
}

let pass=0,fail=0;
function check(name,got,want){ if(JSON.stringify(got)===JSON.stringify(want)){pass++;console.log('  ✓ '+name);} else {fail++;console.log('  ✗ '+name+'\n      got  '+JSON.stringify(got)+'\n      want '+JSON.stringify(want));} }

console.log('CENÁRIO 1 · estado inicial (nada descartado)');
let n=nodesSeed(); propagate(n,edgesSeed());
check('Plano A = planejado', n.pa.status,'planejado');
check('Plano B = pendente (A não descartado)', n.pb.status,'pendente');
check('Plano C = pendente', n.pc.status,'pendente');
check('Plano D = pendente', n.pd.status,'pendente');
check('Fase 4 = planejado (pre-reqs ok)', n.f4.status,'planejado');
check('NZ = pendente (plano C em aberto)', n.nz.status,'pendente');
console.log('  DEBUG: passagens='+n.passagens.status+' f4='+n.f4.status);

console.log('CENÁRIO 2 · descartar Plano A');
n=nodesSeed(); n.pa.status='inativo'; propagate(n,edgesSeed());
check('Plano B ATIVA quando A descartado', n.pb.status,'planejado');
check('Plano C continua pendente', n.pc.status,'pendente');

console.log('CENÁRIO 3 · Plano A acontece');
n=nodesSeed(); n.pa.status='ativo'; propagate(n,edgesSeed());
check('Plano B não ativa (pendente)', n.pb.status,'pendente');

console.log('CENÁRIO 4 · cascata A→B descartados');
n=nodesSeed(); n.pa.status='inativo'; n.pb.status='inativo'; propagate(n,edgesSeed());
check('Plano B preservado inativo (manual)', n.pb.status,'inativo');
check('Plano C ATIVA (Plano B descartado)', n.pc.status,'planejado');

console.log('CENÁRIO 5 · reverter: reativar Plano A');
n=nodesSeed(); n.pa.status='inativo'; propagate(n,edgesSeed());
n.pa.status='ativo'; propagate(n,edgesSeed());
check('Plano B reverte p/ pendente', n.pb.status,'pendente');
check('Plano C permanece pendente', n.pc.status,'pendente');

console.log('\nRESULTADO: '+pass+' pass, '+fail+' fail');
process.exit(fail?1:0);