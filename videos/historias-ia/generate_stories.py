#!/usr/bin/env python3
"""
Gerador de histórias para o projeto my-prompt-to-video.
Cria histórias sobre erros no uso da IA baseadas no livro "A Resposta Não Basta".
Gera imagens com PIL e áudio silencioso com ffmpeg.
"""

import json
import os
import subprocess
import textwrap
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ──────────────────────────────────────────────────────────
# Configurações
# ──────────────────────────────────────────────────────────
PROJECT_DIR = Path("/home/user/my-prompt-to-video")
CONTENT_DIR = PROJECT_DIR / "public" / "content"
BOLD_FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SEMIBOLD_FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
REGULAR_FONT = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"

VIDEO_W = 1024
VIDEO_H = 1792
# Duração por segmento em ms
SEG_DURATION_MS = 7000


# ──────────────────────────────────────────────────────────
# Paleta de cores por história
# ──────────────────────────────────────────────────────────
THEMES = {
    "aceitacao-automatica": {
        "bg": (10, 10, 20),
        "accent": (255, 60, 80),
        "text": (255, 255, 255),
        "sub": (180, 180, 200),
    },
    "fluencia-nao-e-verdade": {
        "bg": (8, 18, 35),
        "accent": (255, 165, 0),
        "text": (255, 255, 255),
        "sub": (180, 200, 230),
    },
    "gerar-nao-e-aprovar": {
        "bg": (10, 25, 15),
        "accent": (50, 205, 100),
        "text": (255, 255, 255),
        "sub": (180, 220, 190),
    },
    "calibre-sua-confianca": {
        "bg": (20, 10, 35),
        "accent": (140, 80, 255),
        "text": (255, 255, 255),
        "sub": (200, 180, 240),
    },
    "vies-confirmacao": {
        "bg": (30, 15, 5),
        "accent": (255, 120, 30),
        "text": (255, 255, 255),
        "sub": (230, 200, 180),
    },
}


def wrap_text(text: str, max_chars: int) -> list[str]:
    return textwrap.wrap(text, width=max_chars)


def draw_centered_text_block(draw, lines: list[str], center_y: int,
                              font: ImageFont.FreeTypeFont, color: tuple,
                              img_w: int, line_spacing: int = 20) -> None:
    """Desenha bloco de texto centralizado verticalmente a partir de center_y."""
    sizes = [font.getbbox(line)[2:4] for line in lines]
    total_h = sum(h for _, h in sizes) + line_spacing * (len(lines) - 1)
    y = center_y - total_h // 2
    for i, line in enumerate(lines):
        w, h = sizes[i]
        x = (img_w - w) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += h + line_spacing


def generate_image(uid: str, segment: dict, theme: dict, story_slug: str,
                   img_dir: Path) -> None:
    """Gera uma imagem 1024x1792 (retrato) para um segmento da historia."""
    bg = theme["bg"]
    accent = theme["accent"]
    text_color = theme["text"]
    sub_color = theme["sub"]

    img = Image.new("RGB", (VIDEO_W, VIDEO_H), bg)
    draw = ImageDraw.Draw(img)

    # Gradiente radial suave centrado no 1/3 superior
    cx, cy = VIDEO_W // 2, VIDEO_H // 3
    for r in range(800, 0, -20):
        alpha = int(40 * (800 - r) / 800)
        color = (
            min(bg[0] + accent[0] * alpha // 255, 255),
            min(bg[1] + accent[1] * alpha // 255, 255),
            min(bg[2] + accent[2] * alpha // 255, 255),
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # Linha decorativa de acento no topo
    draw.rectangle([80, 100, 80 + 60, 100 + 8], fill=accent)

    # Titulo da historia
    try:
        label_font = ImageFont.truetype(SEMIBOLD_FONT, 38)
    except Exception:
        label_font = ImageFont.load_default()
    draw.text((80, 122), segment.get("story_label", "").upper(),
              font=label_font, fill=accent)

    # Numero do segmento
    try:
        small_font = ImageFont.truetype(REGULAR_FONT, 30)
    except Exception:
        small_font = ImageFont.load_default()
    draw.text((80, 172), f"{segment.get('num', '')} de {segment.get('total', '')}",
              font=small_font, fill=(120, 120, 140))

    # Texto principal (grande, centralizado)
    main_text = segment["text"]
    wrapped = wrap_text(main_text, 28)

    if len(wrapped) <= 2:
        font_size = 88
    elif len(wrapped) <= 4:
        font_size = 74
    else:
        font_size = 62

    try:
        main_font = ImageFont.truetype(BOLD_FONT, font_size)
    except Exception:
        main_font = ImageFont.load_default()

    draw_centered_text_block(draw, wrapped, VIDEO_H // 2, main_font, text_color,
                             VIDEO_W, line_spacing=18)

    # Nota (acima do rodape)
    if segment.get("note"):
        note_lines = wrap_text(segment["note"], 40)
        try:
            note_font = ImageFont.truetype(REGULAR_FONT, 36)
        except Exception:
            note_font = ImageFont.load_default()
        y = VIDEO_H - 220
        for line in note_lines[-2:]:
            w = note_font.getbbox(line)[2]
            x = (VIDEO_W - w) // 2
            draw.text((x, y), line, font=note_font, fill=sub_color)
            y += 46

    # Rodape com marca do livro
    try:
        footer_font = ImageFont.truetype(REGULAR_FONT, 26)
    except Exception:
        footer_font = ImageFont.load_default()
    footer = "A RESPOSTA NAO BASTA - Newton Nascimento"
    fw = footer_font.getbbox(footer)[2]
    draw.text(((VIDEO_W - fw) // 2, VIDEO_H - 70), footer,
              font=footer_font, fill=(80, 80, 100))

    img.save(str(img_dir / f"{uid}.png"))
    print(f"  [img] {uid}.png gerado")


def generate_silent_audio(uid: str, duration_ms: int, audio_dir: Path) -> None:
    """Gera arquivo MP3 silencioso via ffmpeg."""
    duration_s = duration_ms / 1000.0
    out = str(audio_dir / f"{uid}.mp3")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=mono",
        "-t", str(duration_s),
        "-q:a", "9",
        "-acodec", "libmp3lame",
        out
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  [aud] {uid}.mp3 gerado ({duration_ms}ms silencioso)")


def build_timeline(content_items: list[dict], seg_duration_ms: int) -> dict:
    """Constrói timeline.json a partir dos itens de conteúdo."""
    elements = []
    text_entries = []
    audio_entries = []

    current_ms = 0
    animations = [
        [{"type": "scale", "from": 1.05, "to": 1.0, "startMs": 0, "endMs": seg_duration_ms}],
        [{"type": "scale", "from": 1.0, "to": 1.05, "startMs": 0, "endMs": seg_duration_ms}],
    ]

    for i, item in enumerate(content_items):
        uid = item["uid"]
        end_ms = current_ms + seg_duration_ms

        # Background image element
        elements.append({
            "startMs": current_ms,
            "endMs": end_ms,
            "imageUrl": uid,
            "enterTransition": "blur",
            "exitTransition": "blur",
            "animations": animations[i % 2],
        })

        # Text caption
        text_entries.append({
            "startMs": current_ms,
            "endMs": end_ms,
            "text": item["text"],
        })

        # Audio (silent)
        audio_entries.append({
            "startMs": current_ms,
            "endMs": end_ms,
            "audioUrl": uid,
        })

        current_ms = end_ms

    return {
        "shortTitle": content_items[0].get("short_title", ""),
        "elements": elements,
        "text": text_entries,
        "audio": audio_entries,
    }


def build_descriptor(short_title: str, content_items: list[dict]) -> dict:
    """Constrói descriptor.json."""
    content = []
    for item in content_items:
        content.append({
            "text": item["text"],
            "imageDescription": item["image_description"],
            "uid": item["uid"],
            "audioTimestamps": {
                "characters": list(item["text"]),
                "characterStartTimesSeconds": [
                    i * (SEG_DURATION_MS / 1000.0) / len(item["text"])
                    for i in range(len(item["text"]))
                ],
                "characterEndTimesSeconds": [
                    (i + 1) * (SEG_DURATION_MS / 1000.0) / len(item["text"])
                    for i in range(len(item["text"]))
                ],
            },
        })
    return {"shortTitle": short_title, "content": content}


def create_story(slug: str, short_title: str, story_label: str,
                 segments: list[dict], theme_key: str) -> None:
    """Cria todos os arquivos de uma história."""
    print(f"\n{'='*60}")
    print(f"Criando história: {short_title}")
    print(f"{'='*60}")

    story_dir = CONTENT_DIR / slug
    img_dir = story_dir / "images"
    audio_dir = story_dir / "audio"
    story_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(exist_ok=True)
    audio_dir.mkdir(exist_ok=True)

    theme = THEMES[theme_key]
    content_items = []

    for i, seg in enumerate(segments):
        uid = str(uuid.uuid4())
        seg_with_meta = {
            **seg,
            "uid": uid,
            "num": i + 1,
            "total": len(segments),
            "story_label": story_label,
            "short_title": short_title,
        }
        content_items.append(seg_with_meta)

        generate_image(uid, seg_with_meta, theme, slug, img_dir)
        generate_silent_audio(uid, SEG_DURATION_MS, audio_dir)

    # Salva descriptor.json
    descriptor = build_descriptor(short_title, content_items)
    with open(story_dir / "descriptor.json", "w", encoding="utf-8") as f:
        json.dump(descriptor, f, ensure_ascii=False, indent=2)
    print(f"  [json] descriptor.json salvo")

    # Salva timeline.json
    timeline = build_timeline(content_items, SEG_DURATION_MS)
    with open(story_dir / "timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)
    print(f"  [json] timeline.json salvo")

    print(f"  ✓ História '{short_title}' criada em {story_dir}")


# ══════════════════════════════════════════════════════════
# HISTÓRIAS
# ══════════════════════════════════════════════════════════

STORIES = [

    # ──────────────────────────────────────────────────────
    # HISTÓRIA 1: Aceitação Automática
    # ──────────────────────────────────────────────────────
    {
        "slug": "aceitacao-automatica",
        "short_title": "Aceitação Automática",
        "story_label": "Erro no uso da IA",
        "theme_key": "aceitacao-automatica",
        "segments": [
            {
                "text": "Pergunta. Resposta. Cópia.",
                "image_description": "Dark dramatic scene showing a hand typing on a glowing keyboard, with a chat interface displaying an AI response, blue light illuminating the face of a focused professional",
                "note": "O padrão mais comum — e mais arriscado — no uso da IA.",
            },
            {
                "text": "O servidor recebeu a tarefa. Abriu a IA. Digitou a pergunta.",
                "image_description": "Close-up of a government employee at a modern desk, opening an AI chat interface on their computer, looking focused and slightly rushed",
                "note": None,
            },
            {
                "text": "A resposta chegou em segundos. Bem escrita. Fluente. Profissional.",
                "image_description": "Computer screen showing a well-formatted AI response with professional text, the screen glowing in a dark office environment, creating a sense of false confidence",
                "note": "Parecia tão certo...",
            },
            {
                "text": "Ele copiou. Colou no documento. Assinou. Enviou.",
                "image_description": "Hand moving from copy-paste keyboard shortcut to signing a document, quick succession showing rushed workflow without verification",
                "note": None,
            },
            {
                "text": "Ninguém verificou. Ninguém precisou entender.",
                "image_description": "Empty desk with a sent document on screen, the person gone, a red warning symbol subtly appearing in the corner of the screen",
                "note": "A responsabilidade ainda era do servidor.",
            },
            {
                "text": "Gerar não é aprovar. Seu trabalho ainda não terminou.",
                "image_description": "Split image: left side showing AI completing a task automatically, right side showing a human professional reviewing and questioning the output with critical eyes",
                "note": "— A Resposta Não Basta, Cap. 2",
            },
        ],
    },

    # ──────────────────────────────────────────────────────
    # HISTÓRIA 2: Fluência Não É Evidência
    # ──────────────────────────────────────────────────────
    {
        "slug": "fluencia-nao-e-evidencia",
        "short_title": "Fluência Não É Verdade",
        "story_label": "Erro no uso da IA",
        "theme_key": "fluencia-nao-e-verdade",
        "segments": [
            {
                "text": "A resposta parecia perfeita. Gramática impecável. Tom profissional.",
                "image_description": "A beautifully formatted AI response on a screen, text appearing polished and professional, with subtle warning signs barely visible",
                "note": "Mas aparência não é evidência.",
            },
            {
                "text": "\"Conforme o Art. 17 da Lei nº...\" A frase parecia precisa.",
                "image_description": "Close-up of a legal citation in a document, the citation looking authoritative and official, but with a subtle distortion suggesting something is wrong",
                "note": "A IA pode inventar artigos que soam reais.",
            },
            {
                "text": "O artigo existia. Só que tratava de outro assunto completamente.",
                "image_description": "A law book open to a page, showing text that contradicts what was cited, with a highlighting pen marking the discrepancy, sense of discovery and alarm",
                "note": None,
            },
            {
                "text": "Isso é confabulação. A IA apresenta conteúdo falso com confiança.",
                "image_description": "Abstract visualization of AI generating text, words forming confidently but some floating away as mirages, representing the concept of hallucination in AI",
                "note": "O NIST chama de 'confabulação'. O cotidiano chama de 'alucinação'.",
            },
            {
                "text": "Fluência não é evidência de verdade.",
                "image_description": "Beautiful golden text on dark background that slowly cracks and crumbles to reveal the words 'CHECK YOUR SOURCES' underneath, dramatic lighting",
                "note": None,
            },
            {
                "text": "Verifique. Especialmente: números, leis, datas, citações e referências.",
                "image_description": "Checklist on a screen with items being verified one by one with green checkmarks: numbers, laws, dates, citations, references, each lighting up as verified",
                "note": "— A Resposta Não Basta, Cap. 5",
            },
        ],
    },

    # ──────────────────────────────────────────────────────
    # HISTÓRIA 3: Gerar Não É Aprovar
    # ──────────────────────────────────────────────────────
    {
        "slug": "gerar-nao-e-aprovar",
        "short_title": "Gerar Não É Aprovar",
        "story_label": "Erro no uso da IA",
        "theme_key": "gerar-nao-e-aprovar",
        "segments": [
            {
                "text": "\"Se alguém me questionar, eu consigo explicar essa conclusão?\"",
                "image_description": "Professional in a meeting being questioned by colleagues about a document, looking uncertain as they realize they cannot explain the reasoning behind it",
                "note": "Essa é a pergunta que separa o uso maduro do uso irresponsável.",
            },
            {
                "text": "A IA pode organizar, resumir, sugerir e produzir uma primeira versão.",
                "image_description": "AI assistant shown as a helpful collaborator, organizing documents and creating drafts, depicted in a positive collaborative light",
                "note": None,
            },
            {
                "text": "Mas o uso profissional do resultado continua exigindo sua compreensão.",
                "image_description": "Same document from AI now being reviewed critically by a human expert, annotating and questioning sections, ownership and responsibility depicted",
                "note": None,
            },
            {
                "text": "Você não pode assinar aquilo que não compreende.",
                "image_description": "Close-up of a signature being added to a document, hand hesitating, with the document content visible but blurry - symbolizing signing without understanding",
                "note": "A responsabilidade não se delega junto com a tarefa.",
            },
            {
                "text": "A IA terminou a resposta. Seu trabalho ainda não.",
                "image_description": "Split screen: left side AI completing a task with a checkmark, right side a human just beginning their review process, the real work starting",
                "note": "— A Resposta Não Basta, Cap. 2",
            },
        ],
    },

    # ──────────────────────────────────────────────────────
    # HISTÓRIA 4: Calibre sua Confiança
    # ──────────────────────────────────────────────────────
    {
        "slug": "calibre-sua-confianca",
        "short_title": "Calibre sua Confiança",
        "story_label": "Método LÚCIDO",
        "theme_key": "calibre-sua-confianca",
        "segments": [
            {
                "text": "\"Não dá para confiar na IA.\" — \"Confio em tudo que ela diz.\"",
                "image_description": "Two contrasting figures: one completely rejecting a tablet showing AI, another blindly following AI instructions off a cliff, extremes depicted",
                "note": "Os dois extremos são igualmente perigosos.",
            },
            {
                "text": "Confiança profissional raramente é absoluta. Ela é calibrada.",
                "image_description": "A professional gauge or dial being carefully adjusted, representing calibration, with different settings for different risk levels",
                "note": None,
            },
            {
                "text": "Sugerir títulos: tolerância alta. Fundamentar uma decisão: outro padrão.",
                "image_description": "Two parallel workflows: casual brainstorming with AI on left (relaxed, creative), critical legal/administrative document preparation on right (careful, systematic)",
                "note": "A intensidade da inspeção deve acompanhar a consequência do erro.",
            },
            {
                "text": "Quanto maior a consequência do erro, maior deve ser sua supervisão.",
                "image_description": "Scale of risk visualization: from low-consequence creative tasks at the bottom to high-consequence administrative decisions at the top, supervision increasing proportionally",
                "note": None,
            },
            {
                "text": "Isso não é medo. É critério.",
                "image_description": "Calm, confident professional at a desk, carefully reviewing an AI-generated document with a methodical approach, competence and control depicted",
                "note": "— A Resposta Não Basta, Epílogo",
            },
        ],
    },

    # ──────────────────────────────────────────────────────
    # HISTÓRIA 5: Viés de Confirmação
    # ──────────────────────────────────────────────────────
    {
        "slug": "vies-de-confirmacao",
        "short_title": "IA Como Espelho",
        "story_label": "Erro no uso da IA",
        "theme_key": "vies-confirmacao",
        "segments": [
            {
                "text": "\"Essa proposta é boa?\" — A IA encontrou razões para concordar.",
                "image_description": "Person asking AI a leading question, AI responding with enthusiastic agreement, the person looking satisfied but the mirror effect showing they're just seeing their own reflection",
                "note": "Quando a pergunta já carrega a conclusão.",
            },
            {
                "text": "Você acrescenta detalhes. Ela continua validando. Sempre.",
                "image_description": "Echo chamber visualization: person speaking, AI amplifying and returning the same ideas, circular pattern showing no new information being added",
                "note": "A ferramenta confirma. Mas não investiga.",
            },
            {
                "text": "O problema não está só na IA. Está em como você formulou a pergunta.",
                "image_description": "Two versions of the same question appearing on screen: one leading question in red that directs the answer, one open question in green that invites real analysis",
                "note": None,
            },
            {
                "text": "\"Demonstre por que este projeto é bom\" ≠ \"Avalie se existem evidências suficientes\"",
                "image_description": "Side-by-side comparison: biased AI response on left with pre-determined conclusion, critical analysis on right with pros, cons, and uncertainties listed",
                "note": None,
            },
            {
                "text": "Peça à IA o melhor argumento contrário à sua conclusão.",
                "image_description": "Person actively asking AI to challenge their ideas, the AI presenting counterarguments, the person looking thoughtful and engaged in genuine critical thinking",
                "note": "— A Resposta Não Basta, Cap. 5",
            },
        ],
    },
]


# ══════════════════════════════════════════════════════════
# Execução principal
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Gerando histórias sobre erros no uso da IA")
    print("Livro: A Resposta Não Basta — Newton Nascimento")
    print()

    for story in STORIES:
        create_story(
            slug=story["slug"],
            short_title=story["short_title"],
            story_label=story["story_label"],
            segments=story["segments"],
            theme_key=story["theme_key"],
        )

    print("\n✅ Todas as histórias geradas com sucesso!")
    print(f"Local: {CONTENT_DIR}")
