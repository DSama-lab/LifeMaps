# AGENTS.md — MAPA VETORIAL VIAJENS / MENTAL MAPS

> Diretrizes para o opencode (e qualquer agente) trabalhar **nesta pasta**.
> Regra-mãe: ver `AGENTS.md` raiz do projeto ("AAA digital PROJECT").

---

## O QUE É ISSO

App standalone mobile-life-planning grafo:
- **3D (modo PADRÃO)**: THREE.js + 3d-force-graph → **globo-múndi** texturizado; nós com `loc` posicionados por latitudes/longitudes (`GEO`), sem local no anel orbital; pontos pinados sem física; clique = menu radial; hover = tooltip.
- **2D (opcional)**: Cytoscape.js (motor condicional, arrastar, editar, persistência localStorage).
- **Sub-plano por nó**: grafo em árvore (`GLOBAL`), drill-down `enterWorld`/`backWorld` com crumbs.
- **IA**: chave do usuário (Groq/OpenRouter) guardada SÓ no navegador (localStorage).

Arquivo principal: `index.html` (HTML+CSS+JS single-file).
Motor condicional: dentro do `index.html` (`propagate()`, `parseCond()`, `condHolds()`).

---

## REGRAS OBRIGATÓRIAS

1. **NUNCA reconstruir do zero.** Evoluir o arquivo existente.
2. **NUNCA quebrar o motor condicional.** Antes/Depois de qualquer mudança relevante rode:
   ```bash
   node test-motor.js        # 13/13 obrigatório
   ```
3. **NUNCA remover funcionalidade validada** (2D, import/export, IA, tooltips, menu radial, globo, sub-plano).
4. **Fonte única de verdade = `cy` (Cytoscape).** O 3D lê do `cy`; se mudar algo no grafo, chamar `sync3D()`.
5. **Anti-credencial**: nenhuma API key em arquivos/MDs. Só `.env.example` com variáveis de exemplo.
6. Ao finalizar tarefa, atualizar: `TAREFAS-ROADMAP.md`, MD do projeto em `MDs Projects/`, `_INDEX_MASTER.md`.

## ARQUIVOS

| Arquivo | Papel |
|---------|-------|
| `index.private.html` | **App pessoal com seed REAL** (NUNCA versionado — gitignore). Abra este p/ uso do dia a dia. |
| `index.html` | App com seed DEMO pública (regenerado por `build-demo.js`). É o que vai pro GitHub. |
| `build-demo.js` | Regenera `index.html` (demo) a partir de `index.private.html` + sanitiza textos pessoais de UI. Rode após editar o app: `node build-demo.js`. |
| `README.md` | Portfólio/README oficial (inglês formal). |
| `index-2D-v1.backup.html` | Snapshot do estado 2D pré-3D. |
| `test-motor.js` | Harness do motor condicional (13/13). |
| `test-3d.html` | Harness 3D automatizado (15/15) via `window.__fg` + iframe same-origin. |
| `test-3d-globo.png` | Screenshot do globo 3D registrado pela rodada do harness. |
| `test-map.html` | Harness do Mapa Premium (17/17): pins sem duplicação + `project()`, card compacto→full + anel `.sel`, touch-guard, troca de estilo (glyphs CORS-safe, `traj-line` converge), diagonalização do touchpad, busca, criação/limpeza de item. Contagem de pins é **dinâmica** (`pinCount` do boot). |
| `FaseE-mapa-premium.png` | Screenshot do Mapa Premium (pins + card) — rodada de 2026-09-12. |
| `TAREFAS-ROADMAP.md` | Lista de tarefas persistente (Fases A–E; C.0/C.1 concluídas). |
| `RELATORIO-EVOLUCAO.md` | Relatório (Fase A + A.2 + C.0/C.1). |
| `# MASTER SPEC - MENTALMAP — MAPA VETORIAL.md` | Visão do produto. |
| `Plano_Mestre_Mobilidade_Internacional.pdf` | Fonte do seed do grafo. |

## PADRÕES DE CÓDIGO (dentro do index.html)

- Variáveis globais comuns: `cy`, `selected`, `fg3d`, `mode3d`, `GLOBAL` (árvore), `pathArr` (caminho atual), `menuNode`/`menuOpen`/`MENU_R` (menu radial), `hoverNode2D`/`hoverNode3D`.
- Funções 3D/globo: `init3D()`, `build3DData()`, `sync3D()`, `set3DMode(on)`, `toggle3D()`, `resize3D()`, `addGlobeMesh()`, `makeGraticule()`, `ll2v()`, `geoPos3D()`, `makeNode3D()`, `makeLabelSprite()`, `startPin3D()`, `handle3DClick()`, `handle3DHover()`, `syncLift3D()`.
- Fase B (2026-09-07): `webglOk()`, `fallbackTo2D(reason)` (WebGL indisponível → 2D limpo + toast), `reload3D()` (botão "⟳ Recarregar 3D", só no modo 3D), `toggleLabels3D()` (rótulos 3D opcionais, `labels3D` + `localStorage.mv_labels3d`), `syncMode3DBtn()` (texto cruzado do botão 3D correto após idioma).
- Interatividade: `openRadialMenu(n,anchor)`, `closeRadialMenu()`, `renderMenuLayer(1|2)`, `menuStatus/menuMore/menuBack/menuSub/menuEdit/menuDep/menuFocus/menuDelete`.
- Tema (Fase C.0/C.1, 2026-09-07): `toggleTheme()`, `applyTheme()`, `isDark()`, `globeBg()`, `labelColor(st)`; imagem: `commitImg()`, `removeImg()`, `fillImgField()`, `readImgAsDataURL()`.
- Sub-plano: `captureWorld()`, `loadWorld(p)`, `enterWorld(n)`, `backWorld()`, `updateCrumb()`, `treeAt(p)`, `setTreeAt(p,g)`, `normalizeGraph(data)`, `freezeGraph()` (retorna árvore), `seedGraph()`.
- Geo: `GEO` (local → [lat,lng]), `normLoc()`, `getLocLL()`, `buildLocList()`, `autoSuggestLoc()`, `fillLocField()`, `commitLoc()`.
- Imagem no nó: `data('img')` (dataURL leve, ≤~300KB) → `fillImgField()`, `commitImg()` (upload), `removeImg()`; persistida em `normalizeGraph`/`captureWorld`/`loadWorld`/`build3DData`; 2D = `background-image:cover`, 3D = sprite circular (escala 3.3).
- Tema: `:root` claro (Google light, default) + `body.dark` (preset escuro); variáveis `--glass/--glass2/--dot/--modal-bg/--oncolor/--scroll`; `localStorage.mv_theme`; funções `isDark()`, `globeBg()`, `labelColor(st)`, `applyTheme()`, `toggleTheme()`; globo usa `globeBg()` no `init3D`.
- **Status**: `ativo`/`inativo` = manuais (motor nunca sobrescreve); `planejado`/`pendente`/`bloqueado` = derivados. `setStatus` mapeia `bloqueado` → `inativo` (com aviso).
- Harness 3D: o app expõe `window.__fg` (a instância ForceGraph3D) em `init3D()`; `fallbackTo2D()` zera `window.__fg`. `test-3d.html` acessa app por `iframe.contentWindow.eval(...)` (nunca via `window.fg3d` — `fg3d`/`cy`/`mode3d` são top-level `let`, sem propriedade em `window`). O boot abre no **Modo Mapa (maplibre)** quando o mundo tem lugares; o globo 3D entra via `#mode3DBtn`/`set3DMode(true)`.
- Orçamento/nó (D.1): `n.data('custo')={quan,moeda,tipo}`; funções `custoOf`, `hasCusto`, `prereqIdsOf`, `prereqCustoBRL`, `totalCustoDoNo`, `fmtBudget`, `budgetResumo`; resumo em `updateSummary`. Bloco `#costField` no painel; `commitCost(skipFill)` grava/limpa; persistido em `captureWorld`/`normalizeGraph`/`loadWorld`.
- **Mapa Premium (Fase E) — pins NÃO usam `maplibregl.Marker`** (era a fonte da duplicação): camada própria `#mapPins` (div absoluta `inset:0;z-index:1;pointer-events:none` dentro de `#cymap`; `.maplibregl-canvas-container{z-index:2}`). `syncMap()` reconcilia por `data-id` (`mapPinEls`): reusa o mesmo elemento, remove órfãos, `mmPositionPins()` posiciona via `mapObj.project(ll)` em `left/top` inline (CSS `#mapPins .mm-pin` centraliza c/ `translate(-50%,-50%)` e compõe hover/sel). Ocultar ≠ remover container. `satelite` retorna objeto (`esriSatelliteStyle()`), demais são URLs.
- **Diagonalização do touchpad (axis-lock workaround, 2026-09-13)**: `mmDiagDelta(dx,dy)` é função pura — se um eixo domina (`>3×` o outro) e `mag>0`, converte p/ diagonal 45° biaxial: horizontal → (`right→NE`, `left→SW`), vertical → (`down→SE`, `up→NW`); já-diagonal passa direto. `mmTrackpadPan` chama `mmDiagDelta` antes do `panBy`. Motivo: o axis-lock do OS/driver zera o eixo menor em gestos puros horizontais/verticais (travando o pan); diagonal força os 2 eixos sempre ativos. Testado no harness 17/17. Habilitação: `mapGest2F`.
- **CORS fontes Carto**: `setMapStyle()` é `async` — faz `fetch(style.json)`, aplica `styleWithFonts(spec)` (glyphs cartocdn → `https://fonts.openmaptiles.org/{fontstack}/{range}.pbf`) e chama `mapObj.setStyle(objeto)`. **NUNCA** trocar sprite cartocdn por demotiles (404 no `@2x`).
- **Troca de estilo e camadas custom**: `setStyle` remove fontes/camadas custom — o rebuild de `traj-line`/países acontece em `mapRestyleReady()` (converge por **style spec aplicado** — `getStyle()` com layers — e NENHUM gatilho de tile/`loaded()`/`isStyleLoaded()`, pois tiles podem falhar/atrasar). `loadPoliticalLayer()`/`syncMap()`/`drawTrajectory()` rodam em `run()` com retry (~20s) até o `traj-line` existir. `drawTrajectory()` tb usa só o style spec (não `isStyleLoaded`), com guarda `_trajKey` (coords+cor) — pular se a camada já existe com as mesmas coords.
- **Harness `test-map.html`**: sempre **cache-bust o iframe** antes de validar — `f.src='index.html?cv='+Date.now()` — senão o HTTP cache serve o `index.html` antigo e o teste falha em `traj-line` (falso negativo). Poll de `traj-line` pós-estilo = 45s (CDN pode atrasar). Seed demo foi desenhada para o harness passar **limpo** (nó `canada` + exatamente 9 pins + 2 nós de fase com loc).
- **`mmKey`/Escape**: fecha card + overlay de item + cancela pick + fecha busca.
- `T(k,a)` suporta placeholders: `T('chave', v0)` substitui `{0}` no texto (ex.: `summ.budgetCount`).
- Cores: `CAT_STYLE` (categoria) e `STATUS_COLOR` (status) são fonte única de cor.
- Ao adicionar mutação do grafo, lembre de chamar `sync3D()` se a mudança deve aparecer no 3D.

## GIT / GITHUB (obrigatório)

- Repositório: **`https://github.com/DSama-lab/LifeMaps`** (público, `origin`, branch `main`). Este `.git` fica nesta pasta.
- **Commits e README em INGLÊS FORMAL** (portfólio). Mensagens objetivas, sem emojis.
- **O repo carrega a seed DEMO** (`index.html`, via `build-demo.js`). A seed REAL fica só em `index.private.html` (gitignore).
- **NUNCA** versionar: `index.private.html`, `*.pdf` (plano pessoal), `*.backup.html`, demais `*.png`, `[#] MASTER SPEC*`, credenciais — `.gitignore` já cobre; não force adds fora disso.
- Identidade local já configurada (`DSama`); não alterar sem avisar.
- Ao fechar fase/marco: rever o seed (privado) → `node build-demo.js` → `git add -A` (revisar `git status` — deve EXCLUIR private/pdf/MASTER SPEC) → commit → `git push`.

## VALIDAÇÃO DE TESTE

```bash
node test-motor.js          # 13/13
python -m http.server 8794  # abrir http://127.0.0.1:8794/test-3d.html → 15/15 do harness 3D
# Browser (manual):
# 1) abre no Modo Mapa (maplibre) se o mundo tem lugares; botão globo 3D = #mode3DBtn.
# 2) hover eleva; clique = menu radial; "mais opções ▸ sub-plano" entra no drill-down.
# 3) mudar status → anel 3D muda de cor; descartar (inativo) dispara cascata condicional.
# 4) voltar p/ 2D está no botão; retornar ao 3D preserva tudo.
# 5) sem erros no console.
```