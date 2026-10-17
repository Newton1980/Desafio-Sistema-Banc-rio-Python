# Histórias sobre Erros no Uso da IA

Vídeos curtos baseados no livro **"A Resposta Não Basta"** — Newton Nascimento.
Criados com o framework **Remotion** (prompt-to-video format).

## Histórias incluídas

| Slug | Título | Tema |
|------|--------|------|
| `aceitacao-automatica` | Aceitação Automática | Pergunta → Resposta → Cópia: o padrão mais perigoso |
| `fluencia-nao-e-evidencia` | Fluência Não É Verdade | Confabulação: a IA inventa com confiança |
| `gerar-nao-e-aprovar` | Gerar Não É Aprovar | Delegar sem compreender — responsabilidade não se transfere |
| `calibre-sua-confianca` | Calibre sua Confiança | Supervisão proporcional à consequência do erro |
| `vies-de-confirmacao` | IA Como Espelho | A IA como máquina de validação do que já acreditamos |

## Estrutura de cada história

```
<slug>/
├── descriptor.json   # Texto + descrições de imagem para cada cena
└── timeline.json     # Timing de imagens, legendas e áudio
```

## Como gerar os assets (imagens + áudio)

As imagens e o áudio são gerados localmente e não estão no repositório.

### Pré-requisitos

```bash
pip install Pillow
# ffmpeg (para o áudio silencioso)
```

### Gerar com imagens PIL (sem APIs externas)

```bash
cd /home/user/my-prompt-to-video
python3 generate_stories.py
```

Isso cria:
- `public/content/<slug>/images/*.png` — imagens 1024×1792 com texto do livro
- `public/content/<slug>/audio/*.mp3` — áudio silencioso (substitua por TTS depois)

### Gerar com IA (OpenAI + ElevenLabs)

Para gerar imagens DALL-E e voz neural:

```bash
cd /home/user/my-prompt-to-video
OPENAI_API_KEY=sk-... ELEVENLABS_API_KEY=el_... bun cli/cli.ts generate \
  --title "Aceitação Automática" \
  --topic "O padrão de copiar respostas da IA sem verificar, baseado no livro A Resposta Não Basta"
```

## Renderizar os vídeos

```bash
cd /home/user/my-prompt-to-video

# Renderizar uma história
npx remotion render aceitacao-automatica output/aceitacao-automatica.mp4

# Renderizar todas
for story in aceitacao-automatica fluencia-nao-e-evidencia gerar-nao-e-aprovar calibre-sua-confianca vies-de-confirmacao; do
  npx remotion render $story output/$story.mp4
done
```

## Referência do livro

> **"A Resposta Não Basta: Como usar inteligência artificial no serviço público com autonomia, critério e responsabilidade"**
> Autor: Newton Nascimento
