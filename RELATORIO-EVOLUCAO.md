# RELATÓRIO DE EVOLUÇÃO — FASE A (3D Orbitável)

> Projeto: **Mental Maps** (ex-Mapa Vetorial Viajens) — data: 2026-09-06

---

## Contexto

O dono pediu **3D real orbitável** (comparou com Obsidian) e aprovou a engine
**3d-force-graph** (THREE.js/WebGL) via CDN, rodando só no navegador.
Regra: não reconstruir, não remover features validadas, manter o motor condicional 13/13.

## O que mudou em `index.html`

1. **Scripts** — carregados via CDN:
   - `three.js r128` (cdnjs) — base 3D + objetos custom.
   - `3d-force-graph 1.70.7` (unpkg) — grafo 3D orbitável.
2. **Botão no header** — `Modo 3D` / `Modo 2D` (toggle).
3. **Container** — `<div id="cy3d">` ao lado do `#cy`, escondido por padrão.
4. **Motor 3D** — novo bloco de código:
   - `init3D()` — instância (`ForceGraph3D`), fundo `#07080f`, nós custom, arestas condicionais em vermelho curvas.
   - `build3DData()` — converte `cy` → `{nodes, links}` (27 nós / 27 links).
   - `sync3D()` — re-sincroniza o 3D a cada mutação (status, add/remove, import, layout).
   - `toggle3D()` — alterna modos; desliga parallax 2.5D (tilt/spin) para não conflitar.
   - `resize3D()` — fixa o tamanho do canvas e dá fit (fim do "canvas 1280×537").
   - `makeNode3D()` — esfera (cor categoria) + anel de status (cor status) + label sprite.
   - `showTip3D()` — tooltip de hover no nó 3D.
5. **Sincronização ampla** — `sync3D()` chamado em `propagate()`, `commitCat/Name`, `deleteNode`, `runLayout`, `buildFromData`, `addNode`, `addEdge`, `resetDemo`, `applyExtract`.

## Bugs encontrados e corrigidos durante a Fase A

- `forceGraph3D` config: `({controlType:'orbit'})` deve vir **antes** do elemento.
- `coolDownTicks` → correto é `cooldownTicks` (case) e `warmupTicks`.
- Chamada inválida `linkDirUpdateLength` removida.
- `fg3d.pause()` inexistente → `pauseAnimation()` / `resumeAnimation()`.
- `zoomToFit` disparado antes do layout assentar → câmera colapsava (camZ=7) ou ficava longe (camZ=1000).
  Solução: fit único atrasado 1.4s após entrada no 3D (`resize3D()`), com nós já espalhados.
- Canvas do WebGL nascia com tamanho do viewport (1280×537) em vez do container (540×481):
  `resize3D()` força `fg3d.width(w).height(h)` ao entrar e no window.resize.

## Resultados validados (navegador Playwright)

- Página carrega **0 erros de console**.
- Modo 3D: **27 nós** (esfera + anel + label) e **27 arestas**.
- Fit OK: 27/27 nós na tela (câmera ~860).
- **Clique físico num nó 3D abre o painel de edição** (ex: raiz selecionada).
- Hover mostra tooltip (título + status + descrição).
- **Mudar status no painel reflete no 3D**: Plano A `planejado`(anel azul) → `inativo`(anel cinza, opacidade 0.225),
  e a cascata condicional ativou o Plano B (motor intacto).
- Reverter `planejado` → Plano B volta a `pendente`.
- Volta ao 2D funciona (painel, pill e nós intactos).
- `node test-motor.js` → **13 pass, 0 fail**.

## Artefatos

- `index.html` (v2 — 2D + 3D)
- `index-2D-v1.backup.html` (estado 2D original antes do 3D)
- `mental-maps-3d.png` (screenshot do modo 3D)
- `TAREFAS-ROADMAP.md` (roadmap persistente Fases A–E)

## Próximos passos sugeridos

- Fase B (robustez): fallback WebGL, re-import/export validado, toggle de labels.
- Revisar nome "Mental Maps" x concorrência antes de escolher domínio.

---

# RELATÓRIO DE EVOLUÇÃO — FASE A.2 (Interatividade + Globo-múndi + Sub-plano)

> 2026-09-06 — sessão 2 do dia.

## Pedidos do dono (nesta sessão)

1. Ao passar o ponteiro, o card deve **elevar** (não só piscar) e ficar elevado.
2. **Zoom nos nós** (pontos onde as linhas conectam) — estavam pequenos demais.
3. Clicar num card deve abrir **menu radial** para trocar status/ações (2D e 3D).
4. **Sub-plano por card**: entrar num card e criar um plano mais detalhado dentro (drill-down).
5. **3D deve ser o modo padrão** (2D opcional).
6. **Mapa em 3D baseado em locais**: a forma física deve seguir geografia real (lat/lng), não simulação aleatória. Sempre haverá locais.
7. Auto-sugestão de local: o app busca, pede pra confirmar e já preenche.
8. Ao final de tudo: atualizar todos os MDs (e salvar nesta pasta também).

## O que mudou em `index.html`

### Interatividade (2D + 3D)
- Hover eleva o nó (classe `nlift`) com dim dos demais; clique seleciona (`nsel`).
- **Menu radial** `#radialMenu` (overlay): 5 status (Ativo/Planejado/Pendente/Bloqueado/Inativo) + "mais opções ▸" → segunda camada com status ◂, **sub-plano**, **editar**, **dependência**, **focar**, **apagar**.
  - Posicionado por âncoras `--dx/--dy`; em 3D segue o nó por projeção (`project3DNode` + RAF `startMenuFollow`); fecha com Esc/clique fora/re-clique.
- Nós 2D maiores: `width:150,height:74` (era 92×46). Nós 3D maiores: esfera `1.8`, torus `2.45/0.11`, labels `12×2.6`.
- **3D é o modo padrão**: no boot roda `set3DMode(true)` (`#cy3d` visível, `#cy` oculto). Botão continua alternando.

### Globo-múndi 3D por geolocalização
- Dicionário `GEO` (normalizado → `[lat,lng]`): Brasil, SP, Brasília, Malásia/KL, Filipinas/Manila, Montenegro/Podgorica, Espanha/Madrid, Portugal/Lisboa, Canadá(Vancouver/Toronto), Ásia/Europa/UE, EUA, Austrália, NZ, Alemanha, França, Itália, Reino Unido/Inglaterra.
- Helpers: `normLoc()`, `getLocLL()`, `capWords()`, `buildLocList()`, `autoSuggestLoc()`, `fillLocField()`, `commitLoc()` (não aceita local fora da lista).
- Campo **Local** no painel do nó (`#edLoc` + datalist `#locList` + `#locHint`): auto-preenche a sugestão e o usuário confirma.
- `addGlobeMesh()`: esfera texturizada (`earth-blue-marble.jpg` via THREE.TextureLoader) com fallback escuro + `makeGraticule()`; `GLOBE_R=60`.
- Nós com local → posição geográfica na esfera (`ll2v`/`geoPos3D`, raio `GLOBE_R*1.06`); nós sem local → anel orbital (`GLOBE_R+32`).
- Pontos **pinados** (sem simulação): `enableNodeDrag(false)`, `cooldownTicks(0)`, `wolframTicks(0)`, `startPin3D()`; `sync3D()` re-pina após re-build.
- Eventos 3D roteados: `handle3DClick` → menu radial, `handle3DHover` → tooltip + `syncLift3D`; `set3DMode(on)` mostra/esconde contêineres.
- `resize3D()` usa `fg3d.zoomToFit(600,110)`.
- Seed: `f1`=Brasil, `f2`/`pa`=Malásia, `pb`=Filipinas, `pc`/`mont`=Montenegro, `por_esp`=Portugal, `canada`=Canadá.

### Sub-plano por nó (drill-down)
- Cada nó pode ter `data('sub') = {nodes, edges}` (plano detalhado dentro do card).
- O grafo todo vira uma **árvore** (`GLOBAL`): `captureWorld()` grava o nível atual no caminho; `treeAt(path)/setTreeAt(path,g)` navegam; `freezeGraph()` agora retorna a árvore.
- `enterWorld(n)` entra no sub-plano do nó; `backWorld()` volta um nível; barra de **crumbs** `#crumbBar` mostra "Mapa-raiz ▸ …" e o botão "← Voltar".
- Persistência/export/import agora operam na **árvore** (`seedGraph()`, `GLOBAL=normalizeGraph(...)`, `loadWorld`).
- Autosave a cada 45s + `beforeunload`.

### Bugs corrigidos nesta sessão
- Nó com `cat` fora de `CAT_STYLE` quebrava o style do Cytoscape → fallback `CAT_STYLE.info`.
- `menuStatus('bloqueado')` era no-op (bloqueado é **derivado** do motor; só `ativo`/`inativo` são manuais) → `setStatus` mapeia `bloqueado`→`inativo` com aviso, mantendo o motor 13/13.
- Crumb: `onclick="drillUp()"` quebrado → `id="crumbBack"` + `backWorld()`; barra passa a exibir quando há caminho.

## Validação (Playwright + node)
- `node test-motor.js` → **13 pass, 0 fail**.
- Parse JS (`node --check` no script inline): OK.
- Página carrega **0 erros de console**.
- Boot: **modo 3D por padrão** (`mode3d=true`, `#cy` oculto), 27 nós no 2D e no 3D.
- Globo: nós com local posicionados por lat/lng (Brasil, Malásia, Filipinas, Montenegro, Portugal, Canadá em coordenadas distintas); 19 sem local no anel orbital.
- Clique real 3D (`handle3DClick`) abre o menu radial (cabeçalho = título do nó, 6 ações); segundo clique fecha (toggle).
- `menuStatus('bloqueado')` → `inativo` + toast + cascata (Plano B ativa), motor intacto.
- Sub-plano: entrar em `f1` mostra crumbs "Mapa-raiz ▸ Fase 1 · Brasil" e vazio; criar nó dentro persiste na árvore `GLOBAL`; `backWorld()` recarrega os 27 nós da raiz.
- `updateCrumb` mostra "Mapa-raiz 🌍" quando há nós com local.

## Artefatos
- `index.html` (v3 — 2D + 3D default + globo + sub-plano)
- `index-2D-v1.backup.html` (snapshot 2D pré-3D)
- `globo-3d.png` / `globo-3d-view.png` (screenshots)
- MDs atualizados nesta pasta: `TAREFAS-ROADMAP.md`, `AGENTS.md`, este relatório — prontos p/ futura importação no app.

## Pendente
- Teste real do dono no navegador (globo, menu radial, sub-plano, campo Local).
- Imagens/geodados mais ricos (arcos, países OFF) se quiser; locais personalizados.
- Fase B robustez (fallback WebGL, re-import/export ida-e-volta 2D↔3D).

---

# Fase C.0 + C.1 — Tema Google light + Imagens nos nós (2026-09-07)

## Escopo
Tema visual "Google light" (fundo semi-claro e suave, painéis claros, cores da Google) + avatares/imagens leves nos nós (2D e 3D), mantendo o tema escuro como preset alternativo e o motor condicional intacto.

## Tema (C.0)
- `:root` agora é o **tema claro** (default): `--bg:#eef1f6`, `--bg2:#e6ebf3`, `--panel:#ffffff`, `--panel2:#f4f6fa`, `--line:#dfe4ec`, `--text:#202124`, `--muted:#5f6368`, `--accent:#4285f4`, `--accent2:#34a853`, `--green:#34a853`, `--red:#ea4335`, `--amber:#fbbc05`, `--blue:#4285f4`, `--cyan:#00acc1`.
- Novo bloco `body.dark` restaura integralmente a paleta escura anterior (preset alternativo).
- Variáveis novas: `--glass`, `--glass2`, `--dot`, `--modal-bg`, `--oncolor`, `--scroll` — substituem os `rgba(12,14,26,...)` hardcoded em header, tabs, sceneBar, legend, crumbBar, rm-head, modal, scrollbar, dots do fundo.
- Fundo do `body`/`main` com glows suaves azul/verde (Google) em ambos os temas.
- **Botão de tema no header** (`#themeBtn`, ☀️/🌙) → `toggleTheme()`; preferência em `localStorage.mv_theme`; aplicado no boot antes do `set3DMode(true)`.

## Globo (fundo mais claro e suave, pedido do dono)
- `init3D()` usa `globeBg()` (claro `#eef2f8`, escuro `#07080f`) em vez de fundo fixo escuro.
- `applyTheme()` re-aplica fundo do globo + reconstrói labels ao alternar tema (sem reset de seleção).
- Labels 3D por tema: `labelColor(st)` — claro: texto `#3c4043`, inativo `#9aa0a6`, bloqueado `#c5221f`; escuro: mantém tons claros.
- Edge-labels 2D legíveis (cond `#e04a55`; normal `#6b748c`).

## Imagens / avatares nos nós (C.1)
- Campo **"Imagem (avatar — leve, opcional)"** no painel do nó: upload de arquivo, preview redondo 56px, botão remover ✕, limite ~300 KB com aviso (`readImgAsDataURL`).
- **2D**: `background-image` + `background-fit:cover` no nó; texto com `text-outline` escuro quando há imagem; `background-image-opacity` condicional (`none` quando sem img).
- **3D**: sprite circular billboard (THREE.Sprite, escala 3.3) sobre a esfera, textura carregada assíncrona do dataURL.
- Persistência ponta-a-ponta: `data('img')` → `normalizeGraph()`/`captureWorld()`/`loadWorld()`/`build3DData()` → árvore `GLOBAL` → export/import/localStorage → recarrega no reload.

## Validação (2026-09-07)
- `node test-motor.js` → **13 pass, 0 fail**.
- `node --check` (script inline extraído UTF-8): OK.
- Playwright: 0 erros de console; tema claro ativo por padrão (`body` `rgb(238,241,246)`); toggle ☀️↔🌙 altera `body.dark` + `localStorage.mv_theme` + ícone; painel direito `#e6ebf3`; imagem 2D aplica `background-image`, preview redondo aparece, `removeImg()` limpa 2D+3D; sprite 3D (escala 3.3) presente após `sync3D`; imagem persiste após reload real (navegação) no 2D e 3D.
- Screenshot: `mm-tema-claro.jpg` (raiz da pasta de trabalho).

## Arquivos alterados
- `index.html` — tudo (CSS vars/tema, botão tema, campo imagem, persistência, render 2D/3D).
- `TAREFAS-ROADMAP.md`, `RELATORIO-EVOLUCAO.md`, `AGENTS.md` (pasta), `MDs Projects/Mapa-Vetorial-VIAJENS.md`, `MDs Projects/_INDEX_MASTER.md`.

## Pendente
- Decisões do dono para C.2–C.4 (status "Concluído"? zoom automático ou botão? arrastar nós sempre ou modo editar? bordas TopoJSON ou textura?).
- C.2: calibração `ll2v` (Greenwich central) + texturas + modo Mapa.

---

# RODADA 2026-09-07 (noite) — FASE B: ROBUSTEZ (itens seguros)

## Escopo
Itens da Fase B que não dependem das **4 decisões pendentes do dono**: fallback WebGL, recarregar layout 3D, rótulos 3D opcionais e validação do round-trip import/export com a árvore/sub-planos. Nada foi feito em C.2/C.3 (travados nas decisões).

## Entregue
- **Fallback WebGL** (`webglOk()` + try/catch no `init3D()`): se o contexto WebGL não existir ou o `ForceGraph3D` lançar erro, o app volta limpo para o **2D com toast** (`fallbackTo2D`) — sem tela preta/JS morto. Guarda também no `set3DMode(true)` (`if(!fg3d) return`).
- **Botão "⟳ Recarregar 3D"** (`reload3D()`): reconstroi `build3DData()` + `zoomToFit` sem sair do modo 3D (reposiciona câmera/nós). Só aparece com o 3D ativo (`set3DMode`/`openMap`).
- **Rótulos 3D opcionais** (`labels3D` + botão "🏷️ Rótulos"): esconde/mostra os sprites de título (`spr.visible=labels3D` em `makeLabelSprite`); persistido em `localStorage.mv_labels3d`; estado refletido no boot.
- **i18n novo**: `btn.mode2d`, `btn.reload3d`, `btn.labels3d`, `b.only3d`, `b.webglFail`, `b.reloadDone`, `b.labelsOn`, `b.labelsOff` (PT/EN).
- **Bugfix botão 3D após idioma**: `syncMode3DBtn()` sincroniza o texto cruzado ("Modo 2D" quando em 3D) depois de `applyLang()` — antes o botão mostrava texto errado ao trocar idioma com o 3D ligado.

## Validação (2026-09-07)
- `node test-motor.js` → **13 pass, 0 fail** (depois das mudanças).
- `node --check` (script inline extraído UTF-8): **OK**.
- Playwright (http://127.0.0.1:8794/index.html): **0 erros de console** (so 5 warnings pré-existentes das libs Three/cytoscape).
  - 3D abre: botão cruzado "Modo 2D" visível; "⟳ Recarregar 3D" aparece só no 3D.
  - "🏷️ Rótulos" ON → 70/70 sprites visíveis; OFF → 0/70 visíveis; ON novamente → 70/70. `localStorage.mv_labels3d` persiste.
  - `reload3D()` → toast "Posições 3D recalculadas ✓", 70 nós.
  - Round-trip import/export: `freezeGraph() → normalizeGraph() → loadWorld([]) → propagate()` resultou **idêntico** (70 nós / 30 arestas / 1 sub-plano / statuses 51·12·1·4·2 / 11 locais).
  - 2D ↔ 3D toggle ida e volta sem erro.
- Screenshot: `mental-maps-3d-faseB.png` (raiz da pasta).

## Arquivos alterados
- `index.html` — `webglOk`, `fallbackTo2D`, `reload3D`, `toggleLabels3D`, `syncMode3DBtn`, i18n novos, botões header, `makeLabelSprite` condicional, `set3DMode`/`openMap`/`applyLang`/boot.
- `TAREFAS-ROADMAP.md`, `RELATORIO-EVOLUCAO.md`, `AGENTS.md` (pasta), `MDs Projects/Mapa-Vetorial-VIAJENS.md`, `MDs Projects/_INDEX_MASTER.md`.

## Pendente
- Decisões do dono (4) para destravar C.2/C.3 (zoom/texturas, arrastar nós, border GeoJSON, cores).
- Fase B restante (opcional): harness 3D automatizado com `window.__fg` (27 nós) em Chrome headless.
- Fase D (orçamento/finanças) e Fase 2 (login/compartilhamento no deploy).