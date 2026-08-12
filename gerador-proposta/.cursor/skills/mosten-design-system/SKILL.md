---
name: mosten-design-system
description: >-
  Aplica o Design System Mosten (Orla/ODS + brandbook): tokens, tipografia,
  componentes @mosten/orla, guardrails visuais e voz da marca. Use when building
  or restyling Mosten UI, Streamlit/React apps, landing pages, or when the user
  mentions Mosten, Orla, ODS, @mosten/orla, brandbook, ou design system Mosten.
---

# Mosten Design System

Fonte de verdade em ordem de precedência:

1. **Figma ODS** (aparência / tokens / estados)
2. **`@mosten/orla`** (API React executável)
3. **`@mosten/ds-catalog` / MCP `@mosten/orla-mcp`** (descoberta por IA)
4. **Brandbook / tokens de marca** (identidade quando o pacote Orla não está no projeto)
5. Docs textuais — nunca inventar hex, px, pesos, props ou variantes

Repo canônico: `mosten-design-system` (Azure DevOps Mosten Core). Feed npm: `orla-ds`.

Detalhes de tokens e componentes → [reference.md](reference.md).

---

## Quando usar qual caminho

| Contexto | Caminho |
|----------|---------|
| App React Mosten com acesso ao feed | Consumir **`@mosten/orla`** (+ MCP se disponível) |
| Evoluir o monorepo do DS | Seguir `AGENTS.md` do repo Orla (ritual Figma → tokens → scaffold) |
| Streamlit, PPT, HTML estático, scaffold sem Orla | Aplicar **brand tokens** + tipografia Inter Tight + guardrails abaixo |
| Skin de cliente sobre Mosten | Só sobrescrever Camada 2 (marca); manter estrutura/status/motion |

---

## Identidade (não negociável)

| Atributo | Valor |
|----------|-------|
| Personalidade | Moderna, leve, otimista, profissional |
| Densidade | Generosa — muito espaço em branco/gelo |
| Tagline | *Negócios e tecnologia caminham juntos.* |
| Fonte UI | **Inter Tight** (única família sans) |
| Mono | IBM Plex Mono (código / dados densos) |
| Ícones | **Lucide** outline, stroke 1.5–2px |
| Marca | Roxo `#612CB5` — destaque pontual, não fundo dominante |

### Cores âncora

| Papel | HEX | Token típico |
|-------|-----|--------------|
| Brand | `#612CB5` | `--brand` / ODS brand |
| Brand hover | `#803DE0` | `--brand-hover` |
| Brand soft | `#CB6BF3` | `--brand-soft` |
| Ink | `#23231E` | `--text-primary` / `--color-ink` |
| Mist | `#F7F4FC` | `--bg-subtle` / `--color-mist` |
| White | `#FFFFFF` | `--bg-canvas` |
| Accent warm | `#FE7040` | `--accent-warm` — **nunca como texto** |

Ritmo de seções: `#FFFFFF` ↔ `#F7F4FC`. Status sempre **token + ícone + texto** (nunca só cor). Status não usa cor de marca.

---

## Consumo React (`@mosten/orla`)

### Setup mínimo

```ts
import "@mosten/orla/styles.css";
import "@fontsource/inter-tight/400.css";
import "@fontsource/inter-tight/500.css";
import "@fontsource/inter-tight/600.css";
import "@fontsource/ibm-plex-mono/400.css";
```

```tsx
import { SnackbarProvider, TooltipProvider, Button, Card, Typography } from "@mosten/orla";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <TooltipProvider>
      <SnackbarProvider>{children}</SnackbarProvider>
    </TooltipProvider>
  );
}
```

`.npmrc` (feed privado):

```ini
@mosten:registry=https://pkgs.dev.azure.com/mosten-core/Mosten%20Core/_packaging/orla-ds/npm/registry/
always-auth=true
```

### Algoritmo obrigatório (MCP Orla)

1. `get-setup` — registry, CSS, fontes, providers  
2. Decompor a tela em regiões/interações  
3. `list-components` / `search-capabilities` — descobrir candidatos  
4. `get-component` — props/variants/examples reais **antes** de codar  
5. Compor layout com tokens semânticos (`gap-ods-*`, `p-ods-*`, `bg-ods-*`, `text-ods-*`)  
6. Não inventar variantes; se faltar, documentar a lacuna  

### Composição

- Primária: `Button variant="fill" tone="brand"`
- Secundária: `outline` / `ghost` + `tone="neutral"`
- Forms: `FormControl` + `FormLabel` + campo + `FormHelperText` (erro não só por cor)
- `className` só para layout externo (posição, gap, width) — não reestilizar o miolo do componente

Tokens: 3 camadas DTCG (`primitive` → `semantic` → `component`), prefixo `ods`. Em app, preferir **semantic**. Nunca consumir primitive direto.

---

## Sem Orla (CSS Modules / HTML / Streamlit)

Espelhar o brandbook com CSS variables. **Proibido** hex cru em componentes — só `var(--token)`.

```css
:root {
  --brand: #612CB5;
  --brand-hover: #803DE0;
  --brand-soft: #CB6BF3;
  --accent-warm: #FE7040;
  --bg-canvas: #FFFFFF;
  --bg-subtle: #F7F4FC;
  --bg-muted: #EEEAF6;
  --text-primary: #23231E;
  --text-secondary: #4A4A45;
  --text-muted: #6E6E66;
  --text-on-brand: #FFFFFF;
  --text-link: #612CB5;
  --border-subtle: #E8E4F2;
  --border-default: #D4CFE3;
  --focus-ring: #612CB5;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-pill: 999px;
  --font-sans: "Inter Tight", ui-sans-serif, system-ui, sans-serif;
  --ease-mosten: cubic-bezier(0.2, 0.8, 0.2, 1);
  --dur-base: 200ms;
}
```

Padrões de componente (resumo):

| Peça | Regra |
|------|-------|
| Button | Primary / Secondary / Ghost; alturas 36 / 44 / 52; 5 estados |
| Card | borda **ou** sombra (nunca ambos); radius `--radius-lg` |
| Badge | pill, 12px, peso 500, tracking +4% |
| Header | sticky 72px |
| Input | altura 44px; foco 2px brand |
| Motion | `mosten-fade-up` / `mosten-fade-in`; máx. 2 animações/viewport; só `transform`/`opacity`; respeitar `prefers-reduced-motion` |

Arquitetura preferida em apps Vite/React legado: Atomic Design em `presentation/` (atoms → molecules → organisms → templates), CSS Modules, Lucide.

Dark mode: `data-theme="dark"` nos tokens semânticos (ver [reference.md](reference.md)).

---

## Logo

| Arquivo | Uso |
|---------|-----|
| `mosten-logo.svg` | Padrão web |
| `mosten-logo-bco.svg` / `mosten-logo_bco.svg` | Fundo escuro/roxo |
| `mosten-icone.svg` | Favicon / redução |
| `mosten-icone-bco.svg` | Sobre escuro |

Proteção ≥ 1 “M”; logo mín. 120px; símbolo mín. 16px. Proibido: inclinar, distorcer, sombra, cores fora da paleta.

---

## Voz & tom

- 1ª pessoa do plural (“Nós, da Mosten…”)
- Verbos: transformar, impulsionar, unir, integrar, otimizar, antecipar, conectar
- Narrativa: desafio → oportunidade → solução → futuro
- Evitar jargão sem tradução, tom de “problema”, autoelogio vazio

Âncoras: *Negócios e tecnologia caminham juntos.* · *Transformamos seus desafios em oportunidades.* · *Inovação como meio, não como fim.*

---

## Guardrails

### Faça

- Roxo como destaque pontual
- Contraste AA em todo texto
- Status = token + ícone + texto
- 1 elemento gráfico inclinado forte por viewport (ângulos 8° / 12° / 18°)
- Um CTA primário de alto impacto por tela

### Não faça

- Inter / Roboto / Plus Jakarta / Arial como fonte de marca (usar **Inter Tight**)
- Tailwind/shadcn inventados fora do Orla; hex cru em componente
- Laranja como texto; texto roxo sobre laranja ou roxo claro
- Foto escura, duotone, pessoa isolada
- Glassmorphism excessivo, neon, >2 animações por viewport
- Inventar props/variantes “do ODS” — se não está no catálogo/Figma, é lacuna

---

## Checklist rápido (antes de entregar UI)

- [ ] Inter Tight + (se Orla) IBM Plex Mono carregados
- [ ] Cores via tokens (`--brand` / `*-ods-*`), sem hex solto
- [ ] Contraste AA; laranja só decorativo
- [ ] Lucide outline; status com texto
- [ ] Se Orla: MCP/`get-component` consultado; providers montados
- [ ] Logo com área de proteção; variante correta no fundo
- [ ] Motion limitada e com reduced-motion
