# CICC Gericinó — Dashboard Operacional SEPPEN-RJ

Dashboard operacional do **Centro Integrado de Comando e Controle (CICC)** do Complexo Penitenciário de Gericinó, desenvolvido para a **Secretaria de Estado de Administração Penitenciária do Rio de Janeiro (SEPPEN-RJ)**.

🌐 **[cicc-gericino.vercel.app](https://cicc-gericino.vercel.app)**

---

## Visão Geral

O sistema provê visualização geoespacial e monitoramento operacional em tempo real do Complexo de Gericinó, incluindo:

- **Mapa interativo** com geometrias KML oficiais das unidades prisionais
- **Modo imersivo** com pilha de overlays sobre o mapa (KPI → Radar → Navegação)
- **Radar meteorológico** via API REDEMET/DECEA (MaxCAPPI) com proxy serverless
- **Painel de KPIs** com indicadores operacionais (efetivo, movimentação, segurança)
- **Navegação modular** entre visões: Infraestrutura, Segurança, Relatórios e Administração

---

## Arquitetura

```
/
├── index.html          # SPA — dashboard completo (Leaflet + Tailwind + KML embutido)
├── api/
│   └── radar.js        # Serverless function — proxy REDEMET (chave fora do bundle)
├── vercel.json         # Headers de segurança + cache-control
└── .gitignore
```

**Stack:**
- **Frontend:** HTML5 + [Tailwind CSS](https://tailwindcss.com) + [Leaflet.js 1.9.4](https://leafletjs.com) + [Lucide Icons](https://lucide.dev)
- **Backend:** Node.js Serverless Function (Vercel Runtime)
- **Infraestrutura:** [Vercel](https://vercel.com) — sem build step, framework "Other"
- **Fonte de dados:** KML oficial SEPPEN-RJ (embutido) + API REDEMET/DECEA (radar)

---

## Interface

### Modo Normal
Exibe o mapa em tela parcial com painéis laterais e barra de navegação inferior visível.

### Modo Imersivo
Mapa em tela cheia com pilha de overlays transparentes que revelam ao hover:

```
┌─────────────────────────────────────────┐  ←  topo da viewport
│                                         │
│           MAPA (Leaflet)                │
│                                         │
│                        [zoom ↑ bottom:210px]
│                                         │
├─────────────────────────────────────────┤  ←  bottom: 86px  z:552  #kpiBar
│  KPI BAR  (hover → opaco)               │
├─────────────────────────────────────────┤  ←  bottom: 34px  z:551  #radarStrip
│  RADAR STRIP  (hover → opaco)           │
├─────────────────────────────────────────┤  ←  bottom: 0     z:550  #mapNavBar
│  NAV BAR  (hover → opaco)               │
└─────────────────────────────────────────┘
```

Todos os overlays usam `position:fixed`, `opacity:0.12` em repouso e `opacity:1` no hover, com `backdrop-filter:blur(10px)`.

---

## Proxy Serverless — Radar REDEMET

A função `api/radar.js` isola a chave de API do DECEA do bundle client-side:

```
Cliente → GET /api/radar → Vercel Function → api-redemet.decea.mil.br → resposta JSON
```

A chave nunca aparece no HTML entregue ao navegador.

---

## Deploy

### Pré-requisitos
- Conta [Vercel](https://vercel.com)
- Chave de API REDEMET/DECEA (`REDEMET_API_KEY`)

### Passos

1. **Clone o repositório**
   ```bash
   git clone https://github.com/Newton1980/Desafio-Sistema-Banc-rio-Python.git
   cd Desafio-Sistema-Banc-rio-Python
   ```

2. **Importe no Vercel**
   - Acesse [vercel.com/new](https://vercel.com/new)
   - Selecione o repositório
   - Framework Preset: **Other**
   - Sem comandos de build necessários

3. **Configure a variável de ambiente**

   | Nome | Valor | Ambientes |
   |------|-------|-----------|
   | `REDEMET_API_KEY` | `<sua-chave>` | Production, Preview |

4. **Deploy**
   Clique em **Deploy**. O Vercel detecta automaticamente a serverless function em `api/radar.js`.

### Redeploy automático
Qualquer push para a branch `master` dispara um novo deploy via integração GitHub → Vercel.

---

## Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `REDEMET_API_KEY` | Sim | Chave de acesso à API REDEMET/DECEA para dados de radar meteorológico |

> Solicite a chave em [redemet.decea.mil.br](https://redemet.decea.mil.br).

---

## Headers de Segurança

Configurados via `vercel.json` em todas as rotas:

| Header | Valor |
|--------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `SAMEORIGIN` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `geolocation=(), camera=(), microphone=()` |

---

## Estrutura de Dados Geoespaciais

O mapa consome **dados KML oficiais** da SEPPEN-RJ embutidos diretamente no `index.html`, sem dependência de serviço externo. Isso garante disponibilidade offline e elimina latência de rede para os polígonos.

As geometrias cobrem:
- Perímetros das unidades prisionais do Complexo de Gericinó
- Áreas funcionais internas
- Pontos de controle e infraestrutura

---

## Desenvolvimento Local

Como o projeto não possui build step, basta servir os arquivos estáticos:

```bash
# Com Python
python3 -m http.server 8080

# Com Node.js
npx serve .
```

> Para testar a rota `/api/radar` localmente instale a [Vercel CLI](https://vercel.com/docs/cli):
> ```bash
> npm i -g vercel
> vercel dev
> ```
> A CLI lê o arquivo `.env.local` automaticamente:
> ```
> REDEMET_API_KEY=sua-chave-aqui
> ```

---

## Licença

Uso restrito — SEPPEN-RJ / Governo do Estado do Rio de Janeiro.
