# MENTAL MAPS — LISTA DE TAREFAS (ROADMAP)

> Nome do projeto: **Mental Maps** (ex-"Mapa Vetorial Viajens").
> Essa lista é persistida aqui para NENHUMA tarefa se perder entre sessões.
> Última atualização: 2026-09-14 (rodada: **Sync com a nuvem — Fase 2B frontend**)
- **09-12 · Fase E bugfixs (Playwright)**: pins do mapa NUNCA mais duplicam (camada `#mapPins` reusa por `data-id`; 5× syncMap + 6 trocas de estilo = 9 pins fixos); fontes dos mapas `escuro`/`vias` (Carto) passam a carregar via `fonts.openmaptiles.org` (CORS) — 0 erros de console; anel `.sel` do card no mapa finalmente aplica (erro de precedência `CSS.escape?` sem parênteses). Motor 13/13 verde. Screenshot: `FaseE-mapa-premium.png`.

---

## VISÃO

Grafo de planejamento de vida (objetivos → etapas → dependências → IA) com **visualização 3D orbitável**.
Fonte: `MAPA VETORIAL VIAJENS/# MASTER SPEC - MENTALMAP — MAPA VETORIAL.md`.

Regras:
- NÃO reconstruir do zero. NÃO remover funcionalidades validadas.
- Preservar o **motor condicional** e `test-motor.js` (13/13) — são o coração do projeto.
- Trabalhar sem domínios por enquanto.
- Atualizar MDs ao final de cada entrega.

---

## ✔ FASES A–E (resumo do plano)

| Fase | Escopo | Status |
|------|--------|--------|
| A | 3D real orbitável (3d-force-graph + THREE) · toggle 2D/3D · sync com cy | ✅ **CONCLUÍDA** |
| A.2 | Interatividade (elevar + menu radial) · nós maiores · **3D default** · **globo-múndi por locais** · **sub-plano por nó** | ✅ **CONCLUÍDA (2026-09-06)** |
| B | Robustez (persistência, erros, testes mais profundos, import/export validado) | ⬜ |
| C | Mapa-múndi 3D (globo com nós geolocalizados por país) | ✅ **NÚCLEO ENTREGUE na A.2** (refinar depois) |
| D | Segurança / finanças (área de orçamentos, chave IA só no navegador) | ⬜ |
| E | Relatório final + AGENTS.md + MDs atualizados | 🔄 em curso |

---

## ✅ FASE A — 3D ORBITÁVEL (concluída 2026-09-06)

### Entregue
- `index.html` ganhou **Modo 3D** (botão no header).
  - Librerías via CDN: `three.js r128` + `3d-force-graph 1.70.7`.
  - Renderização WebGL com **câmera orbitável** (arrastar = orbitar, scroll = zoom, assumido OrbitControls).
  - Nós 3D = esfera (cor da categoria) + **anel de status** (cor = status) + **label sprite** sempre visível.
  - Bloqueado/inativo com opacidade reduzida (≈0.45 / 0.25).
  - Arestas: pré-requisito cinza, **condicional vermelha curva**.
  - Contexto 3D espelhando o `cy` (fonte única de verdade = Cytoscape).
  - **Clique no nó 3D abre o painel de edição** (drag para orbitar, click para selecionar).
  - Hover mostra tooltip (título + status + descrição).
  - Toggle 2D ↔ 3D preserva ambos os modos, sem conflito com parallax/“tilt” automaticamente desligado ao entrar em 3D.
  - Sincronização em: mudança de status, criação/remoção de nós/arestas, import, reset, runLayout, commitCat/Name.
- `test-motor.js` continua **13/13** (executado após integração).
- Backup do estado 2D: `index-2D-v1.backup.html`.
- Screenshot: `mental-maps-3d.png` (raiz da pasta de trabalho).

### Como validar
```bash
# dentro da pasta do projeto
python -m http.server 8794
# abrir http://127.0.0.1:8794/index.html → clicar "Modo 3D"
node test-motor.js   # 13/13
```

### Pendências/observações da Fase A
- O nome do container WebGL é `#cy3d`; o 3D nasce escondido (`display:none`) e só é instanciado ao ativar.
- Se o usuário arrastar um nó no 3D, o `cy` (2D) reflete via motor; posições manuais no 3D não são persistidas (visão é decorativa/exploratória).

---

## ✅ FASE A.2 — INTERATIVIDADE + GLOBO + SUB-PLANO (concluída 2026-09-06)

### Entregue
- **Hover eleva card** (classe `nlift`) + dim dos demais; clique seleciona (`nsel`).
- **Menu radial** `#radialMenu` (status + mais opções ▸ → sub-plano/editar/dependência/focar/apagar). Funciona em 2D e 3D (segue o nó por projeção).
- **Nós maiores** (2D 150×74, 3D esfera 1.8 / torus 2.45) com fit e layout `nodeRepulsion:16000, idealEdgeLength:230`.
- **3D é o MODO PADRÃO** (`set3DMode(true)` no boot); 2D opcional via botão.
- **Globo-múndi 3D por geolocalização**: dicionário `GEO` (países/cidades → lat·lng), nós com local na esfera, sem local no anel orbital, pontos pinados (sem física), câmera orbitável.
- **Campo Local por nó**: auto-sugestão + datalist + confirmação (`normLoc`/`getLocLL`/`autoSuggestLoc`/`commitLoc`).
- **Sub-plano por nó (drill-down)**: grafo vira árvore `GLOBAL`, `enterWorld`/`backWorld`, crumbs "Mapa-raiz ▸ ...", persistência/export/import em árvore, autosave 45s + beforeunload.
- `setStatus('bloqueado')` → vira `inativo` com aviso (bloqueado é derivado do motor; não vira no-op silencioso).
- `node test-motor.js` → **13/13**; browser **0 erros de console**; Playwright validou globo, menu, drill-down e persistência.

### Artefatos
- Screenshots: `globo-3d.png`, `globo-3d-view.png`.
- MDs desta pasta atualizados p/ futura importação no app: `RELATORIO-EVOLUCAO.md`, `TAREFAS-ROADMAP.md`, `AGENTS.md`.

### Como validar (após reload no navegador)
```bash
python -m http.server 8794   # abrir http://127.0.0.1:8794/index.html
node test-motor.js           # 13/13
# 1) abre JÁ no 3D (globo). 2) embaçou para 2D? botão alterna.
# 3) hover eleva, clique = menu radial. 4) num card → "mais opções ▸ sub-plano".
# 5) campo Local no painel preenche sozinho quando o nó tem local no seed.
```

---

## ⚙️ FASE B — ROBUSTEZ (🔄 2026-09-07 — itens seguros entregues)

Feito nesta rodada (sem depender das 4 decisões pendentes do dono):
- [x] **Fallback WebGL limpo**: `webglOk()` + try/catch no `init3D()`; se o WebGL não existir/fallhar, volta automaticamente para o **2D com aviso** (`fallbackTo2D`) — sem tela preta.
- [x] **Botão "⟳ Recarregar 3D"** (`reload3D()`): recalcula posições/posiciona a câmera sem trocar de modo (só aparece no modo 3D).
- [x] **Mostrar/esconder rótulos no 3D** (`labels3D` + botão "🏷️ Rótulos"): esconde os sprites de título em nós densos; persistido em `localStorage.mv_labels3d`.
- [x] **Validar re-import/export ida-e-volta**: teste real `freezeGraph() → normalizeGraph() → loadWorld() → propagate()` resultou **idêntico** (70 nós / 30 arestas / 1 sub-plano / statuses / 11 locais) — árvore/sub-planos preservados.
- [x] Bugfix menor: texto cruzado do botão 3D agora usa i18n (`btn.mode2d`/`btn.mode3d`) e `syncMode3DBtn()` corrige após troca de idioma (antes o botão mostrava o texto errado ao mudar idioma com o 3D ativo).
- [x] **Harness 3D automatizado** (2026-09-11): `test-3d.html` (novo) — iframe same-origin + `window.__fg` (exposição global já setada pelo app) + `cy` via `app.contentWindow.eval`; **15/15 asserts**: boot do grafo, coerência de visibilidade cy/cy3d/cymap, `__fg===fg3d` (com `graphData`/`camera`/`scene`), saída do Modo Mapa → entrada no globo, paridade nós/links cy↔3D (85/43 no seed), ids únicos, paridade título/cat/status total, posições finitas, nós com local no globo (banda r 55–90), anel orbital sem local (banda r 80–105), `sync3D()` íntegro, toggle 3D→2D→3D preserva grafo, `fallbackTo2D` limpo (**`window.__fg=null`** — bugfix: antes ficava ponteiro órfão p/ fg3d destruído) + re-sobe, `build3DData()` coerente; rodar com `python -m http.server 8794` → `http://127.0.0.1:8794/test-3d.html`; `?suite=0` bloqueia autorun; `window.__runSuite3D` re-executa. Screenshot `test-3d-globo.png`.

Pendentes (decisões do dono travam alguns): itens C.2/C.3 (dependem das decisões).

## 🌍 FASE C — MAPA-MÚNDI 3D (núcleo entregue na A.2, refinar depois)

- [x] **Globo 3D com nós sobre coordenadas reais de países** (esfera texturizada + graticule, `ll2v`/`geoPos3D`, nós com local na esfera, sem local no anel orbital, pontos pinados sem física).
- [x] **Campo Local por nó** com auto-sugestão + confirmação (datalist `#locList`, dict `GEO`, `commitLoc`).
- [x] **Modo 3D padrão** no boot.
- [x] **C.0 · Tema "Google light"** (2026-09-07): fundo `#eef1f6` suave, painéis claros, cores Google (`#4285F4`/`#34A853`/`#EA4335`/`#FBBC05`), `--glass` var, toggle ☀️/🌙 (botão header, `localStorage.mv_theme`, default claro), **fundo do globo agora temático e suave** (`#eef2f8`, escuro `#07080f`), labels 3D legíveis nos dois temas, edge-labels legíveis.
- [x] **C.1 · Imagens/avatars nos nós** (2026-09-07): campo "Imagem (avatar)" no painel do nó (upload p/ arquivo, preview redondo 56px, remover ✕, limite ~300 KB c/ aviso); 2D = fundo `cover` + texto com outline; 3D = sprite circular billboard (escala 3.3) sobre a esfera; persistido em `data('img')` ↔ árvore `GLOBAL` ↔ export/import/localStorage.
- [ ] Arcos entre locais / highlight de países (azer mais rico — opcional).
- [ ] Transitores "modo grafo 3D" ↔ "modo globo" sem perder dados (hoje o 3D já é o globo).

### Fase C — próximo (aguarda decisões do dono)
- [x] **C.4 · Status "Concluído"** (2026-09-07) — adiantado nesta rodada.
- C.2 Calibração `ll2v` (Greenwich central, Norte em cima) + texturas (Satélite/Noturno/Mapa) + modo Mapa com bordas de países.
- C.3 Arrastar nós no globo com offset persistido · arcos sobre a superfície (verde = concluída) · zoom → vista de mapa.
- C.5 Leque de sub-planos + herança de geolocalização.

**4 decisões pendentes do dono** (destravam C.2–C.3): zoom auto ou botão Satélite/Mapa? arrastar nós sempre ou "modo editar mapa"? bordas TopoJSON ou textura com fronteiras? (status "Concluído" já foi entregue nesta rodada)

## ✅ RODADA 2026-09-07 — CONCLUÍDO + HISTÓRICO/DIÁRIO + i18n PT/EN + TONS BEBÊ

### Entregue
- **Status `concluido`** protegido pelo motor (padrão `STATUS_COLOR`/`STATUS_LBL`/`MAP`), chip dourado `#e8b64c`, anel 3D, marcador de mapa, legenda, relatório e pill; nunca sobrescrito pelo `propagate`.
- **Importar histórico/diário (aba IA → seção 4)**: diário colado → IA propõe itens "Concluído" (viagens/moradias/trabalhos/pessoas/conquistas) com `local` resolvido via `GEO` (Tailândia, Chiang Mai, Phuket, Manila, Indonésia, Japão, Coreia do Sul, Índia, Vietnã, Camboja, Singapura, México, Argentina, Chile, Peru, Colômbia e mais) e `ligacoes` para etapas existentes (checkboxes de revisão antes de inserir).
- **i18n PT/EN**: seletor no header (`localStorage.mv_lang`, default PT); `I18N`/`T()`/`setLang()`/`applyLang()`; todos os textos da UI traduzíveis (`data-i18n*`).
- **Tons bebê dos países do mapa-múndi**: `hsl(matiz, 44%, 90%)` (lock 34%/93%); mesmas cores por país, mais claras.
- **Bugfix**: `highlightRegion` (ordem camada/source) → 0 erros de console.

### Validações
- `node test-motor.js` **13/13**; `node --check` OK.
- Playwright: PT→EN aplica (abas "Step", botões "Save", "Completed", pill "Active 12 · Planned 51 · Completed 0 · Blocked 0 · Inactive 1 🌍 6/197"), legenda "Completed", help EN ok; histórico insere 3 etapas "Concluído" com local/ptype (Chiang Mai→trabalho, Manila→morar, Tailândia→outro) e permanece após `propagate`; **0 erros de console**.

### Deploy avaliado (2026-09-07)
- **Pronto para subir como estático** (single-file, localStorage, chave IA só no navegador). Sem banco por enquanto.
- VPS Hostinger `148.230.78.83` (KVM 2 · 8 GB RAM · 8 TB/mês) → nginx/Caddy + HTTPS.
- Fase 2 (login/compartilhamento): FastAPI/Node + Postgres (Docker) no mesmo VPS; MinIO só p/ mídia grande.
- Pré-publicação: domínio, HTTPS, CORS dos CDNs/estilos, favicon/meta, decidir self-host dos CDNs.

## 🔐 FASE D — SEGURANÇA / FINANÇAS (pendente)

- [x] **D.0 · Itens Inteligentes — extração curada de transcrições/vídeos** (2026-09-11): aba IA seção 5 com schema por tipo de item, avaliação colorida, impacto, fato/inferência, requisitos (visto/passagem/recurso_minimo/curso/documento/idioma/contato/outro), contatos, câmbio real sem chave (`open.er-api.com`, cache 6h), markup de venda (15% default), Google Flights link, seleção um-a-um, painel do nó com campos completos (incluindo "Moeda local" no campo Local), chips clicáveis; **+ Polônia (GEO: polonia/breslavia/wroclaw) e moeda PLN** (09-11, vaga ID LOGISTIC 061); motor 13/13; Playwright 0 erros; screenshots `itens-proposal.png` + `node-meta-panel.png`.
- [ ] Teste real do dono: colar transcrições dos 2 vídeos do Japão; gravar "Fontes analisadas" no MD com link + resumo curado (sem transcrição bruta).
- [x] **D.1 · Orçamento por nó** (2026-09-11): campo `custo {quan,moeda,tipo(único|mensal|estimado)}` no painel do nó; cascata de pré-requisitos (`totalCustoDoNo`, ex. Passaporte R$500 + vaga R$3.000 → R$3.500); resumo "💶 Orçamento estimado do plano" no Resumo (contagem + total BRL/USD + por-planos); persistência em save/load/export/import; `T()` com placeholders `{0}`; bugfix boot (`budgetResumo` sem `cy`); motor 13/13; Playwright 0 erros; round-trip pós-reload ok; i18n EN ok.
- [ ] Painel de orçamento por nó consolidado (valores `R$/US$/€` + prazos) — export financeiro consolidado.
- [ ] Registrar que a API key NUNCA sai do navegador (já é assim hoje).
- [ ] Exports anonimizados (sem chave).

## 📦 FASE E — FECHAMENTO (em curso)

- [x] **Harness do Mapa Premium** (2026-09-12): `test-map.html` (novo) — padrão do `test-3d.html`, iframe same-origin + `app.contentWindow.eval` + `pollUntil` + `#results`; `?suite=0` bloqueia autorun; `window.__runSuiteMap` re-executa. **16/16 asserts**, 2 rodadas: boot com mapa aberto (28 nós), pins renderizados (9) e posicionados, `mapPinEls` coerente, 3× `syncMap` sem duplicação, posição == `project()`, anel `.sel` aplica/limpa, card compacto→full (popup real), `setMapStyle("escuro")` → glyphs `fonts.openmaptiles.org` (CORS), **`traj-line` presente após troca (convergência)**, touch-guard `hover:none`, pointerenter desktop abre card, busca `mapSearchRun`, criação de item persiste `latll` + pin, limpeza volta a 9 pins.
- [x] **4° bug achado pelo harness — `traj-line` pós-troca de estilo**: `setStyle` remove camadas custom e o rebuild dependia de `idle`/`style.load`/`loaded()` (que espera os TILES — CDN lento/falho → nunca assenta, idle loop a 0,3s). Fix intermediário (pré-limpeza): `mapRestyleReady()` + polling `isStyleLoaded()` + guarda `_trajKey`.
- [x] **5° bug achado em seed limpa (09-12)**: fix 4º não bastava — em seeds limpas `traj-line` só recriava após ~2 min (tiles CDN atrasando), derrubando harness (15/16). Fix definitivo: convergência por **style spec aplicado** (`mapObj.getStyle().layers`) — camadas custom geojson não dependem de tiles. `drawTrajectory()` também usa style spec. **Harness 16/16 em seed limpa** (reset de localStorage).
- [x] **GitHub público criado e reescrito (09-12)**: `github.com/DSama-lab/LifeMaps` — 1º commit (`d5e8c7f`) com seed real; **história reescrita via orphan + force push** (`e527d48` → sem dados pessoais). Agora: `index.html` carrega **seed DEMO** (gerada por `build-demo.js` a partir de `index.private.html` [gitignore]); `[#] MASTER SPEC*` e PDFs exclude by `.gitignore`. Regra: commits/README em EN; nunca versionar seed real/PDF/MASTER SPEC/credenciais.
- [x] Screenshot 3D.
- [x] `RELATORIO-EVOLUCAO.md` na pasta do projeto (Fase A + A.2).
- [x] `AGENTS.md` na pasta do projeto (atualizado p/ A.2).
- [x] Atualizar `MDs Projects/Mapa-Vetorial-VIAJENS.md`.
- [x] Atualizar `MDs Projects/_INDEX_MASTER.md`.
- [x] **Duplo clique do mapa = zoom (Google Maps)** + **config IA compacta (2026-09-14)**: `dblclick` agora faz `mapObj.zoomTo(min(z+1,max),{center:e.lngLat,duration:250})` (antes criava pin vermelho/abria form → marcadores agora passam a ser via prompt IA ou busca; botão manual "➕ Marcar item" mantido); campos API key/Provider/Modelo movidos para `#aiConfigBox` colapsável (botão `#aiConfigToggle` — label "IA usada: Groq · sem chave" / "OpenRouter · sk-…"), preparação p/ servir IA no SaaS. Motor 13/13, zoom verificado no Chrome (1.6→2.6→3.6), 0 erros console.
- [x] **Sync com a nuvem — Fase 2B frontend (2026-09-14)**: login/registro (email+senha + Google pronto no backend) com cookie httpOnly; **um doc por usuário** (`GET/PUT /api/docs/:id`, `base_version` → 409); autosave local→PUT (debounce 1,5s) + pull no boot; **offline-first** — localStorage continua a fonte local e o push é best-effort; resolução de conflito por **assinatura semântica** (id/title/cat/status/loc + edges) — local não-seed → “meu dispositivo vence”; local seed/fresh + nuvem com dados → pull; 409 → recarrega via pull automático; UI discreta: botão **☁️** no header + modal (`buildSyncModal`) + `apiSyncBoot()` no boot; `SYNC_API_BASE` por env `mv_api_base` (default `127.0.0.1:8000` local / `api.lifemaps.pro` produção). **Validado de ponta a ponta com mock Node do contrato da API**: register→doc criado e plano enviado, editar→PUT (v+1), localStorage limpo (novo device)→login→pull restaura, base_version obsoleto→409+pull (conteúdo preservado), logout→/me 401; botão sync volta ao estado off. Backend ganhou `GET /api/docs` (lista) + `DocMetaOut`. Motores: 13/13, mapa 18/18, 3D 15/15; único console error = probe offline do backend (some quando o backend está no ar). Pendente: deploy VPS (docker-compose) + `CORS_ORIGINS` do domínio + opt-in Google (`mv_google_client_id`/`LIFEMAPS_GOOGLE_CLIENT_ID`).
- [x] **Deploy VPS PRONTO (2026-09-14)**: `backend/docker-compose.prod.yml` + `backend/Caddyfile.prod` + `backend/DEPLOY-VPS.md` (runbook auto-contido p/ rodar SEM o opencode com VPN off: DNS, .env, subir, teste, conflito 80/443 com aaPanel, front, Google opt-in, backup cron + restore, troubleshooting). `.env.example` ganhou `DOMAIN`. Front já aponta sozinho no prod (`SYNC_API_BASE`). Próximo: dono executar o runbook na VPS.

---

## 🏷 NOME "MENTAL MAPS" — CONCORRÊNCIA

Busca web (2026-09-06) indicou nomes genéricos de mapas mentais (MapaMental.org, etc.)
e produtos consolidados (MindMeister, Miro, XMind, Coggle, GitMind) — mas **nenhum projeto exatamente chamado "Mental Maps"** com o mesmo nicho (planejamento de vida → mobilidade internacional) foi confirmado ainda.

- [ ] Verificação mais fina quando o deploy for decidido (busca por marca/registro).
- [ ] Decisão de manter nome antes de investir em domínio.

---

## 📌 NOTAS
- Pasta continua `MAPA VETORIAL VIAJENS/` (renomear só quando decidir domínio/identidade final).
- CDNs usados: cdnjs (three r128), unpkg (3d-force-graph 1.70.7).