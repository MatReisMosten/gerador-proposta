---
name: mosten-design-system
description: >-
  Aplica a identidade visual e o design system Mosten (tokens, tipografia,
  componentes, voz e guardrails) em HTML, CSS, React, Streamlit, slides ou
  qualquer UI sem depender de pacotes. Use when building or restyling Mosten UI,
  landing pages, apps, docs, or when the user mentions Mosten, brandbook, ODS,
  ou design system Mosten.
---

# Mosten Design System (portátil)

Skill autossuficiente. Aplique estes tokens e regras em qualquer stack (HTML/CSS, React, Vue, Streamlit, PPT, PDF). Não invente hex, pesos, radii ou variantes fora deste documento.

---

## Identidade (não negociável)

| Atributo | Valor |
|----------|-------|
| Personalidade | Moderna, leve, otimista, profissional |
| Densidade | Generosa — muito espaço em branco/gelo |
| Tagline | *Negócios e tecnologia caminham juntos.* |
| Fonte UI | **Inter Tight** (única família sans) |
| Mono | IBM Plex Mono (código / dados densos) |
| Ícones | Lucide outline, stroke 1.5–2px |
| Marca | Roxo `#612CB5` — destaque pontual, nunca fundo dominante |

Ritmo de seções: `#FFFFFF` ↔ `#F7F4FC`. Status = **token + ícone + texto** (nunca só cor). Status não usa cor de marca.

---

## Tokens CSS (fonte de verdade)

**Proibido** hex cru em componentes — só `var(--token)`.

```css
:root {
  /* Brand */
  --brand: #612CB5;
  --brand-hover: #803DE0;
  --brand-soft: #CB6BF3;
  --accent-warm: #FE7040; /* nunca como texto */

  /* Alias âncora */
  --color-ink: #23231E;
  --color-mist: #F7F4FC;
  --color-white: #FFFFFF;
  --color-primary: var(--brand);

  /* Superfícies */
  --bg-canvas: #FFFFFF;
  --bg-subtle: #F7F4FC;
  --bg-muted: #EEEAF6;
  --bg-inverse: #23231E;

  /* Texto */
  --text-primary: #23231E;
  --text-secondary: #4A4A45;
  --text-muted: #6E6E66;
  --text-on-brand: #FFFFFF;
  --text-link: #612CB5;

  /* Borda / foco */
  --border-subtle: #E8E4F2;
  --border-default: #D4CFE3;
  --border-strong: #23231E;
  --focus-ring: #612CB5;
  --scrim: rgba(35, 35, 30, 0.5);

  /* Status (AA) — texto / fundo */
  --status-critical: #B42318;
  --status-critical-bg: #FEF3F2;
  --status-high: #B54708;
  --status-high-bg: #FFF6ED;
  --status-attention: #92600A;
  --status-attention-bg: #FFFAEB;
  --status-pending: #175CD3;
  --status-pending-bg: #EFF4FF;
  --status-success: #166534;
  --status-success-bg: #ECFDF3;
  --status-blocked: #6927DA;
  --status-blocked-bg: #F4F0FF;
  --status-info: #0E7090;
  --status-info-bg: #ECFEFF;
  --status-neutral: #475467;
  --status-neutral-bg: #F2F4F7;

  /* Gradientes */
  --gradient-brand: linear-gradient(135deg, #612CB5, #803DE0);
  --gradient-brand-vivid: linear-gradient(120deg, #612CB5, #803DE0 42%, #CB6BF3);
  --gradient-text: linear-gradient(120deg, #612CB5, #803DE0 55%, #9B4DEC); /* só display */
  --gradient-soft: linear-gradient(135deg, #F7F4FC, #FFFFFF);

  /* Tipografia */
  --font-sans: "Inter Tight", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;

  --fs-display-xl: 72px;
  --fs-display-lg: 56px;
  --fs-display-mb: 36px;
  --fs-h1: 44px;
  --fs-h2: 32px;
  --fs-h3: 24px;
  --fs-h4: 20px;
  --fs-body-lg: 18px;
  --fs-body: 16px;
  --fs-body-sm: 14px;
  --fs-label: 12px;

  /* Espaço (base 4px) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;
  --space-30: 120px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-pill: 999px;

  /* Sombra */
  --shadow-1: 0 1px 2px rgba(35, 35, 30, 0.06);
  --shadow-2: 0 4px 12px rgba(35, 35, 30, 0.08);
  --shadow-3: 0 12px 32px rgba(35, 35, 30, 0.10);
  --shadow-4: 0 24px 64px rgba(97, 44, 181, 0.18);
  --shadow-glow: 0 8px 28px rgba(97, 44, 181, 0.28);

  /* Glass (usar com parcimônia) */
  --surface-glass: rgba(255, 255, 255, 0.72);
  --surface-glass-strong: rgba(255, 255, 255, 0.86);
  --border-glass: rgba(97, 44, 181, 0.14);
  --blur-glass: 16px;

  /* Layout */
  --container-max: 1200px;
  --container-wide: 1280px;
  --container-text: 720px;

  /* Motion */
  --ease-mosten: cubic-bezier(0.2, 0.8, 0.2, 1);
  --dur-micro: 120ms;
  --dur-fast: 150ms;
  --dur-base: 200ms;
  --dur-panel: 220ms;
  --dur-page: 280ms;
  --dur-slow: 400ms;
}

[data-theme="dark"] {
  --bg-canvas: #23231E;
  --bg-subtle: #2D2D27;
  --bg-muted: #3A3A33;
  --text-primary: #F7F4FC;
  --text-secondary: #C3C3B7;
  --text-muted: #9A9A8E;
  --text-link: #CB6BF3;
  --brand: #803DE0;
  --brand-hover: #CB6BF3;
  --border-subtle: #3A3A33;
  --border-default: #4A4A45;
  --surface-glass: rgba(45, 45, 39, 0.62);
}
```

### Contraste

- Ink sobre white/mist/muted → AAA
- White sobre brand/ink → AA/AAA
- **Nunca:** roxo sobre laranja; roxo sobre roxo claro; laranja como texto

### Tipografia (uso)

| Token | Size | LH | Weight | Tracking |
|-------|------|----|--------|----------|
| display-xl | 72px | 0.95 | 700 | -2% |
| display-lg | 56px | 1.0 | 700 | -1.5% |
| display-mb | 36px | 1.0 | 700 | -1% |
| h1 | 44px | 1.05 | 700 | -1% |
| h2 | 32px | 1.15 | 600 | -1% |
| h3 | 24px | 1.25 | 600 | -0.5% |
| h4 | 20px | 1.3 | 600 | 0 |
| body-lg | 18px | 1.55 | 400 | 0 |
| body | 16px | 1.6 | 400 | 0 |
| body-sm | 14px | 1.55 | 400 | 0 |
| label | 12px | 1.4 | 500 | +4% |

Pesos: 300 / 400 / 500 / 600 / 700 / 800 (800 raro).

Carregar fontes (web):

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter+Tight:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
```

### Layout

| Item | Valor |
|------|-------|
| Grid | 12 colunas, gutter 24px |
| Breakpoints | 640 / 768 / 1024 / 1280 / 1536 |
| z-index | dropdown 10 → sticky 20 → drawer 40 → modal 50 → toast 60 → tooltip 70 |

---

## Motion

```css
@keyframes mosten-fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes mosten-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.u-reveal {
  animation: mosten-fade-up var(--dur-page) var(--ease-mosten) both;
}
.u-stagger { animation-delay: calc(var(--i, 0) * 60ms); }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

Regras: máx. **2 animações/viewport**; só `transform`/`opacity`; hover de card = `translateY(-2px)` + shadow-2→3.

---

## Componentes (contrato)

### Button

| Variant | Estilo |
|---------|--------|
| Primary | bg `var(--brand)`, text `var(--text-on-brand)`, padding 12×20, radius md, fw 600 |
| Secondary | border 1.5 `var(--brand)`, hover fill brand |
| Ghost | transparent, hover text brand |
| CTA impacto | `var(--gradient-brand-vivid)` + `var(--shadow-glow)` — **1 por tela** |

Alturas: 36 / **44** (default) / 52. Estados: default, hover, focus-visible, active, disabled.

### Input

Altura 44px; border 1.5 `var(--border-default)` → 2px brand no foco; erro = acento visual + texto abaixo (nunca só cor).

### Card

bg canvas ou subtle; **borda ou sombra** (nunca ambos); padding 24/32; radius lg. Destaque: gradient brand + texto branco.

### Badge

Pill; padding 4×10; 12px / 500 / tracking +4%. Default: fundo subtle + texto brand. Brand: soft 20% + texto brand.

### Header / Sidebar / Modal / Table

- Header sticky 72px; ativo = brand + underline 2px
- Sidebar ativo: barra `var(--gradient-brand-vivid)` + tint 10% brand
- Modal: shadow-4, radius lg, scrim, z-50
- DataTable rows: 32 / 40 / 48; cell pad-x 12

### Form

Label + campo + helper/erro em texto. Erro nunca só por cor.

---

## Logo

| Arquivo típico | Uso |
|----------------|-----|
| mosten-logo.svg | Padrão web |
| mosten-logo-bco.svg | Fundo escuro/roxo |
| mosten-icone.svg | Favicon / redução |
| mosten-icone-bco.svg | Sobre escuro |

Proteção ≥ 1 “M”; logo mín. 120px; símbolo mín. 16px. Proibido: inclinar, distorcer, sombra, cores fora da paleta.

---

## Voz & tom

- 1ª pessoa do plural (“Nós, da Mosten…”)
- Verbos: transformar, impulsionar, unir, integrar, otimizar, antecipar, conectar
- Narrativa: desafio → oportunidade → solução → futuro
- Evitar jargão sem tradução, tom de “problema”, autoelogio vazio

Âncoras: *Negócios e tecnologia caminham juntos.* · *Transformamos seus desafios em oportunidades.* · *Inovação como meio, não como fim.*

---

## Fotografia & gráfico

**Foto:** equipes em ação, dispositivos, expressões positivas, roxo na cena, luz clara.  
**Não:** escuro, duotone, pessoa isolada, caricatura.  
**Gráfico:** 1 elemento forte/viewport; ângulos 8° / 12° / 18°; opacidade 100% (foco) ou 8–15% (textura).

---

## Theming (skin de cliente)

**Camada 1 — estrutural (nunca sobrescrever):** space, radius, shadow, motion, layout, escala tipográfica, Inter Tight, status, superfícies/texto neutros.

**Camada 2 — marca (override ok):** `--brand`, `--brand-hover`, `--brand-soft`, `--text-link`, `--text-on-brand`, `--focus-ring`, `--gradient-brand`, logo. Manter `--accent-warm`. Gerar par dark da brand com contraste AA.

---

## Como aplicar por stack

1. Definir `:root` (bloco acima) ou equivalente em tema (Streamlit `st.markdown` + CSS, Tailwind `@theme`, etc.).
2. Tipografia Inter Tight; mono só para código/dados.
3. Compor UI com tokens semânticos; Lucide outline.
4. Um CTA primário forte por tela; roxo pontual.
5. Validar contraste AA e reduced-motion.

Streamlit: injetar o CSS de `:root` + classes utilitárias; evitar widgets nativos sem skin.  
Slides/PPT: usar HEX da tabela âncora; Inter Tight se disponível; ritmo white/mist; 1 acento brand por slide.

---

## Guardrails

### Faça

- Roxo como destaque pontual
- Contraste AA em todo texto
- Status = token + ícone + texto
- 1 elemento gráfico inclinado forte por viewport
- Um CTA primário de alto impacto por tela
- Tokens via `var(--*)`, sem hex solto em componentes

### Não faça

- Inter / Roboto / Plus Jakarta / Arial como fonte de marca
- Laranja como texto; texto roxo sobre laranja ou roxo claro
- Foto escura, duotone, pessoa isolada
- Glassmorphism excessivo, neon, >2 animações por viewport
- Inventar tokens ou variantes fora deste skill

---

## Checklist (antes de entregar)

- [ ] Inter Tight (+ IBM Plex Mono se houver código)
- [ ] Cores só via tokens
- [ ] Contraste AA; laranja só decorativo
- [ ] Lucide outline; status com texto
- [ ] Logo com proteção e variante correta no fundo
- [ ] Motion limitada + `prefers-reduced-motion`
- [ ] Densidade generosa; ritmo white ↔ mist
