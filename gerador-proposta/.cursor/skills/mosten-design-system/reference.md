# Mosten DS — Referência de tokens e componentes

Complemento de [SKILL.md](SKILL.md). Valores do brandbook / AduanaOS. Em apps com `@mosten/orla`, preferir tokens `--ods-*` gerados; estes HEX servem para validação visual e projetos sem o pacote.

---

## Paleta

### Principais

| Token | HEX | Uso |
|-------|-----|-----|
| `--color-ink` | `#23231E` | Texto, ícones, dark base |
| `--color-mist` | `#F7F4FC` | Fundo claro, cards neutros |
| `--color-white` | `#FFFFFF` | Canvas limpo |
| `--color-primary` / `--brand` | `#612CB5` | Marca, CTAs, links |
| `--brand-hover` / purple-10 | `#803DE0` | Hover, gradientes |
| `--brand-soft` / purple-20 | `#CB6BF3` | Tags, highlights |
| `--accent-warm` | `#FE7040` | Acento (nunca texto) |
| mist-10 | `#EEEAF6` | Fundos alternados |
| mist-20 | `#D4CFE3` | Bordas, disabled |

### Superfícies / texto / bordas

| Token | Light |
|-------|-------|
| `--bg-canvas` | `#FFFFFF` |
| `--bg-subtle` | `#F7F4FC` |
| `--bg-muted` | `#EEEAF6` |
| `--bg-inverse` | `#23231E` |
| `--text-primary` | `#23231E` |
| `--text-secondary` | `#4A4A45` |
| `--text-muted` | `#6E6E66` |
| `--text-on-brand` | `#FFFFFF` |
| `--text-link` | `#612CB5` |
| `--border-subtle` | `#E8E4F2` |
| `--border-default` | `#D4CFE3` |
| `--border-strong` | `#23231E` |
| `--focus-ring` | `#612CB5` |
| `--scrim` | `rgba(35,35,30,0.5)` |

### Status (AA)

| Papel | Texto | Fundo |
|-------|-------|-------|
| critical | `#B42318` | `#FEF3F2` |
| high | `#B54708` | `#FFF6ED` |
| attention | `#92600A` | `#FFFAEB` |
| pending | `#175CD3` | `#EFF4FF` |
| success | `#166534` | `#ECFDF3` |
| blocked | `#6927DA` | `#F4F0FF` |
| info | `#0E7090` | `#ECFEFF` |
| neutral | `#475467` | `#F2F4F7` |

### Gradientes

| Token | Valor |
|-------|-------|
| `--gradient-brand` | `linear-gradient(135deg, #612CB5, #803DE0)` |
| `--gradient-brand-vivid` | `linear-gradient(120deg, #612CB5, #803DE0 42%, #CB6BF3)` |
| `--gradient-text` | `linear-gradient(120deg, #612CB5, #803DE0 55%, #9B4DEC)` — só display |
| `--gradient-soft` | `linear-gradient(135deg, #F7F4FC, #FFFFFF)` |

### Contraste

- Ink sobre white/mist/muted → AAA  
- White sobre brand/ink → AA/AAA  
- Nunca: roxo sobre laranja; roxo sobre roxo claro; laranja como texto (~2.76:1)

---

## Tipografia

```css
--font-sans: "Inter Tight", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
--font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, Consolas, monospace;
```

| Token | Size | LH | Weight | Tracking |
|-------|------|----|--------|----------|
| `--fs-display-xl` | 72px | 0.95 | 700 | -2% |
| `--fs-display-lg` | 56px | 1.0 | 700 | -1.5% |
| `--fs-display-mb` | 36px | 1.0 | 700 | -1% |
| `--fs-h1` | 44px | 1.05 | 700 | -1% |
| `--fs-h2` | 32px | 1.15 | 600 | -1% |
| `--fs-h3` | 24px | 1.25 | 600 | -0.5% |
| `--fs-h4` | 20px | 1.3 | 600 | 0 |
| `--fs-body-lg` | 18px | 1.55 | 400 | 0 |
| `--fs-body` | 16px | 1.6 | 400 | 0 |
| `--fs-body-sm` | 14px | 1.55 | 400 | 0 |
| `--fs-label` | 12px | 1.4 | 500 | +4% |

Pesos: 300 / 400 / 500 / 600 / 700 / 800 (800 raro).

---

## Espaço, radius, sombra, layout

Escala de espaço: 4px → `--space-1`…`--space-30` (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 120…).

| Radius | Valor | Uso |
|--------|-------|-----|
| sm | 4px | tags, inputs pequenos |
| md | 8px | botões, cards padrão |
| lg | 16px | cards destaque, modais |
| xl | 24px | containers especiais |
| pill | 999px | badges |

| Shadow | Uso |
|--------|-----|
| `--shadow-1` `0 1px 2px rgba(35,35,30,0.06)` | inputs |
| `--shadow-2` `0 4px 12px rgba(35,35,30,0.08)` | cards |
| `--shadow-3` `0 12px 32px rgba(35,35,30,0.10)` | hover/dropdown |
| `--shadow-4` `0 24px 64px rgba(97,44,181,0.18)` | modal |
| `--shadow-glow` / `-strong` | CTA / tile impacto |
| `--ring-glow` | halo foco |

| Layout | Valor |
|--------|-------|
| `--container-max` | 1200px |
| `--container-wide` | 1280px |
| `--container-text` | 720px |
| grid | 12 col, gutter 24px |
| bp | 640 / 768 / 1024 / 1280 / 1536 |
| z | dropdown 10 → sticky 20 → drawer 40 → modal 50 → toast 60 → tooltip 70 |

### Glass

`--surface-glass: rgba(255,255,255,0.72)`; `--surface-glass-strong: 0.86`; `--border-glass: rgba(97,44,181,0.14)`; `--blur-glass: 16px`.

---

## Motion

| Token | Valor |
|-------|-------|
| `--ease-mosten` | `cubic-bezier(0.2, 0.8, 0.2, 1)` |
| `--dur-micro` | 120ms |
| `--dur-fast` | 150ms |
| `--dur-base` | 200ms |
| `--dur-panel` | 220ms |
| `--dur-page` | 280ms |
| `--dur-slow` | 400ms |

Keyframes: `mosten-fade-up`, `mosten-fade-in`, `mosten-aurora` (~18–20s), `mosten-sheen`.  
Utils: `.u-reveal`, `.u-stagger` (`--i` 0-based).  
Hover card: `translateY(-2px)` + shadow-2→3. Só `transform`/`opacity`.

---

## Componentes (contrato brand)

### Button

- Variants: Primary / Secondary / Ghost  
- Sizes: 36 / 44 (default) / 52  
- States: default, hover, focus-visible, active, disabled  
- Primary: bg brand, text on-brand, padding 12×20, radius md, fw 600  
- Secondary: border 1.5 brand, hover fill brand  
- Ghost: transparent, hover text brand  
- CTA alto impacto: gradient-brand-vivid + shadow-glow; **1 por tela**

### Input

Altura 44px; border 1.5 default → 2px brand no foco; erro visual `#FE7040` + texto abaixo.

### Card

bg canvas/subtle; **borda ou sombra**; padding 24/32; radius lg; hover translateY(-2px)+shadow-3.  
Destaque: gradient brand + texto branco. Glass: surface-glass + border-glass.

### Badge

Pill; padding 4×10; 12px / 500 / +4%. Default: subtle+primary text. Brand: soft 20% + texto brand.

### Header / Sidebar / Modal / Table

- Header sticky 72px; ativo = brand + underline 2px  
- Sidebar ativo: barra gradient-brand-vivid + tint 10% brand  
- Modal: shadow-4, radius lg, scrim, z-50  
- DataTable rows: 32 / 40 / 48; cell pad-x 12

---

## Dark mode (`data-theme="dark"`)

| Token | Dark |
|-------|------|
| `--bg-canvas` | `#23231E` |
| `--bg-subtle` | `#2D2D27` |
| `--bg-muted` | `#3A3A33` |
| `--text-primary` | `#F7F4FC` |
| `--text-secondary` | `#C3C3B7` |
| `--text-muted` | `#9A9A8E` |
| `--text-link` | `#CB6BF3` |
| `--brand` | `#803DE0` |
| `--brand-hover` | `#CB6BF3` |
| `--border-subtle` | `#3A3A33` |
| `--border-default` | `#4A4A45` |
| `--surface-glass` | `rgba(45,45,39,0.62)` |

---

## Camadas de theming (skin de cliente)

**Camada 1 — estrutural (nunca sobrescrever):** space, radius, shadow base, motion, layout, escala tipográfica, Inter Tight (troca só com decisão explícita), status, superfícies/texto neutros.

**Camada 2 — marca (override permitido):** `--brand`, `--brand-hover`, `--brand-soft`, `--text-link`, `--text-on-brand`, `--focus-ring`, `--gradient-brand`, logo. Manter `--accent-warm` Mosten. Gerar par dark da brand com contraste AA.

---

## Orla — mapeamento mental

| Brand mental model | Orla |
|--------------------|------|
| CSS var `--brand` | tokens semantic `component.brand.*` / utils `*-ods-*` |
| Button Primary | `Button variant="fill" tone="brand"` |
| Button Secondary | `variant="outline"` |
| Button Ghost | `variant="ghost"` |
| Alert / Toast | `Alert` / `Snackbar` |
| Sidebar / Header | `Sidebar` / padrões docs |
| Tokens no layout | `gap-ods-*`, `p-ods-*`, `bg-ods-*`, `text-ods-*` |

Figma: Design Tokens v1.2, Padrões v1.2, Componentes v1.2 (boards no `llms.txt` do monorepo).

---

## Fotografia & gráfico

**Foto:** equipes em ação, dispositivos, expressões positivas, roxo na cena, luz clara.  
**Não:** escuro, duotone, pessoa isolada, caricatura.  
**Gráfico:** 1 elemento forte/viewport; ângulos 8°/12°/18°; opacidade 100% (foco) ou 8–15% (textura).
