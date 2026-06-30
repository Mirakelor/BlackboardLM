from dataclasses import dataclass

@dataclass
class Theme:
    name: str
    display_name: str
    background: str
    surface: str
    surface_alt: str
    primary: str
    accent: str
    text_primary: str
    text_secondary: str
    text_muted: str
    border: str
    shadow: str
    radius: str
    font_heading: str
    font_body: str
    font_mono: str
    google_fonts_url: str
    star_chart_bg: str
    star_chart_node: str
    star_chart_edge: str
    star_chart_highlight: str
    message_user_bg: str
    message_user_color: str
    message_ai_bg: str
    message_ai_color: str
    message_ai_border: str
    message_ai_shadow: str
    doc_card_bg: str
    doc_card_border: str
    doc_card_hover_shadow: str
    input_bg: str
    input_border: str
    description: str = ""
    star_chart_title: str = ""
    star_chart_empty: str = ""
    star_chart_processing: str = ""
    loading_text: str = ""
    placeholder: str = ""
    upload_text: str = ""
    upload_hint: str = ""
    doc_add_text: str = ""
    doc_loading_text: str = ""
    css_extra: str = ""

_hogwarts = Theme(
    name="hogwarts",
    display_name="🏰 Flourish & Blotts",
    description="Where old ink meets new parchment—every spine holds a secret waiting to be whispered",
    background="#1b150e",
    surface="#2c2216",
    surface_alt="#342818",
    primary="#d4a843",
    accent="#9b2d2d",
    text_primary="#efe0c4",
    text_secondary="#c8b078",
    text_muted="#a89570",
    border="1px solid rgba(212,168,67,0.35)",
    shadow="0 0 20px rgba(212,168,67,0.18), 0 2px 8px rgba(0,0,0,0.4)",
    radius="6px",
    font_heading="'Cinzel Decorative', 'Cinzel', serif",
    font_body="'IM Fell English', 'Georgia', serif",
    font_mono="'JetBrains Mono', monospace",
    google_fonts_url="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=IM+Fell+English:ital@0;1&display=swap",
    star_chart_bg="#0d1225",
    star_chart_node="#d4a843",
    star_chart_edge="rgba(212,168,67,0.35)",
    star_chart_highlight="#ffd700",
    message_user_bg="linear-gradient(135deg, #f0ddb8, #d4a843)",
    message_user_color="#1b150e",
    message_ai_bg="linear-gradient(180deg, #2c2216, #1b150e)",
    message_ai_color="#efe0c4",
    message_ai_border="2px solid #b8942e",
    message_ai_shadow="inset 0 0 30px rgba(0,0,0,0.1), 0 0 20px rgba(212,168,67,0.15)",
    doc_card_bg="linear-gradient(180deg, #2c2216, #1b150e)",
    doc_card_border="1px solid rgba(212,168,67,0.45)",
    doc_card_hover_shadow="0 0 25px rgba(212,168,67,0.45), 0 4px 12px rgba(0,0,0,0.5)",
    input_bg="rgba(44,34,22,0.85)",
    input_border="1px solid rgba(212,168,67,0.5)",
    star_chart_title="📜 活点地图 · 知识星座",
    star_chart_empty="✦  上传文档后，知识星座将在此显现……  ✦",
    star_chart_processing="🕯️  正在解读羊皮纸，绘制知识星座……",
    loading_text="猫头鹰正在送信中……",
    placeholder="用羽毛笔写下你的疑问……",
    upload_text="拖放或点击上传文档",
    upload_hint="PDF · DOCX · PPTX · TXT · MD",
    doc_add_text="添加文献",
    doc_loading_text="Unfurling the parchment…",
    css_extra="""
@keyframes candle-flicker {
    0%, 100% { opacity: 0.12; }
    30% { opacity: 0.35; }
    60% { opacity: 0.10; }
    85% { opacity: 0.28; }
}
@keyframes star-twinkle {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 1; transform: scale(2); }
}
@keyframes float-up {
    0% { transform: translateY(0) scale(1); opacity: 1; }
    100% { transform: translateY(-30px) scale(1.3); opacity: 0; }
}
@keyframes message-enter {
    0% { transform: translateY(6px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}
@keyframes expand-enter {
    0% { max-height: 0; opacity: 0; }
    100% { max-height: 500px; opacity: 1; }
}
.hogwarts-bg {
    background: radial-gradient(ellipse at 50% 0%, #2c2216 0%, #1b150e 60%);
}
.hogwarts-bg::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(circle at 50% 50%, rgba(212,168,67,0.12) 0%, transparent 70%);
    animation: candle-flicker 4s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}
.hogwarts-stars {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 1;
}
.parchment-texture {
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(139,105,20,0.08) 2px, rgba(139,105,20,0.08) 4px);
}
""",
)

_sakura = Theme(
    name="sakura",
    display_name="🌸 栞",
    description="ページの間に挟まれた道しるべ——知識の森を、迷わず歩くために",
    background="#f5efe0",
    surface="#fffaf2",
    surface_alt="#ede4d3",
    primary="#d4838f",
    accent="#7b9e6e",
    text_primary="#5c4a3a",
    text_secondary="#8a7a6a",
    text_muted="#b5a898",
    border="1px solid rgba(212,131,143,0.2)",
    shadow="0 2px 15px rgba(180,160,140,0.12), 0 1px 4px rgba(0,0,0,0.04)",
    radius="16px",
    font_heading="'Zen Kaku Gothic New', sans-serif",
    font_body="'Zen Kaku Gothic New', sans-serif",
    font_mono="'JetBrains Mono', monospace",
    google_fonts_url="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap",
    star_chart_bg="rgba(255,250,242,0.9)",
    star_chart_node="#d4838f",
    star_chart_edge="rgba(123,158,110,0.3)",
    star_chart_highlight="#e898a8",
    message_user_bg="linear-gradient(135deg, #f0e8d8, #e8d8c0)",
    message_user_color="#5c4a3a",
    message_ai_bg="#fffaf2",
    message_ai_color="#5c4a3a",
    message_ai_border="1px solid #e8d8c8",
    message_ai_shadow="0 0 10px rgba(0,0,0,0.04)",
    doc_card_bg="rgba(255,250,242,0.85)",
    doc_card_border="1px solid rgba(212,131,143,0.25)",
    doc_card_hover_shadow="0 4px 20px rgba(212,131,143,0.18), 0 2px 6px rgba(0,0,0,0.04)",
    input_bg="rgba(255,250,242,0.9)",
    input_border="1px solid rgba(212,131,143,0.3)",
    star_chart_title="🌸 知识的花枝",
    star_chart_empty="上传文档后，知识的花枝将悄然伸展……",
    star_chart_processing="正在分析文档，梳理知识枝条……",
    loading_text="正在思考中……",
    placeholder="有什么想问的吗？",
    upload_text="拖放或点击上传文档",
    upload_hint="PDF · DOCX · PPTX · TXT · MD",
    doc_add_text="添加文献",
    doc_loading_text="文書を読み込み中……",
    css_extra="""
@keyframes sakura-fall {
    0% { transform: translateY(-5vh) rotate(0deg) scale(1); opacity: 0.7; }
    100% { transform: translateY(105vh) rotate(540deg) scale(0.4); opacity: 0; }
}
@keyframes sakura-sway {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(20px); }
    75% { transform: translateX(-15px); }
}
@keyframes message-enter {
    0% { transform: translateY(6px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
}
@keyframes expand-enter {
    0% { max-height: 0; opacity: 0; }
    100% { max-height: 500px; opacity: 1; }
}
.sakura-bg {
    background: #f5efe0;
}
.sakura-petals {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 1;
    overflow: hidden;
}
""",
)

THEMES: dict[str, Theme] = {
    "hogwarts": _hogwarts,
    "sakura": _sakura,
}

THEME_HOGWARTS = "hogwarts"
THEME_SAKURA = "sakura"
