from __future__ import annotations

import os
import subprocess
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


DOCS_DIR = Path(__file__).resolve().parent
REPO = DOCS_DIR.parent
FINAL_DIR = DOCS_DIR / "final"
DIAGRAM_DIR = DOCS_DIR / "diagrams"
SCREENSHOT_DIR = DOCS_DIR / "screenshots"


TITLE_FONT = "微软雅黑"
BODY_FONT = "宋体"
TODAY = date.today().strftime("%Y年%m月%d日")


def ensure_dirs() -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def text_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    text: str,
    fill: str = "#ffffff",
    outline: str = "#334155",
    width: int = 2,
    radius: int = 12,
    text_fill: str = "#111827",
    font_size: int = 26,
    bold: bool = False,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    f = font(font_size, bold)
    lines = text.split("\n")
    line_heights = [draw.textbbox((0, 0), line, font=f)[3] for line in lines]
    total_h = sum(line_heights) + (len(lines) - 1) * 8
    y = xy[1] + ((xy[3] - xy[1]) - total_h) / 2
    for line, lh in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=f)
        x = xy[0] + ((xy[2] - xy[0]) - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=f, fill=text_fill)
        y += lh + 8


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, max_width: int, f: ImageFont.FreeTypeFont) -> list[str]:
    result: list[str] = []
    for raw_line in text.split("\n"):
        line = ""
        for char in raw_line:
            test = line + char
            if draw.textbbox((0, 0), test, font=f)[2] <= max_width:
                line = test
            else:
                if line:
                    result.append(line)
                line = char
        if line:
            result.append(line)
    return result or [""]


def wrapped_text_box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    text: str,
    fill: str = "#ffffff",
    outline: str = "#334155",
    width: int = 2,
    radius: int = 10,
    text_fill: str = "#111827",
    font_size: int = 22,
    bold: bool = False,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    box_width = xy[2] - xy[0] - 28
    box_height = xy[3] - xy[1] - 18
    size = font_size
    while size >= 14:
        f = font(size, bold)
        lines = wrap_lines(draw, text, box_width, f)
        line_h = max(18, draw.textbbox((0, 0), "国", font=f)[3] + 4)
        if line_h * len(lines) <= box_height:
            break
        size -= 1
    f = font(size, bold)
    lines = wrap_lines(draw, text, box_width, f)
    line_h = max(18, draw.textbbox((0, 0), "国", font=f)[3] + 4)
    y = xy[1] + ((xy[3] - xy[1]) - line_h * len(lines)) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        x = xy[0] + ((xy[2] - xy[0]) - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=f, fill=text_fill)
        y += line_h


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], fill: str = "#475569", width: int = 3) -> None:
    draw.line([start, end], fill=fill, width=width)
    sx, sy = start
    ex, ey = end
    if abs(ex - sx) >= abs(ey - sy):
        direction = 1 if ex > sx else -1
        points = [(ex, ey), (ex - 14 * direction, ey - 8), (ex - 14 * direction, ey + 8)]
    else:
        direction = 1 if ey > sy else -1
        points = [(ex, ey), (ex - 8, ey - 14 * direction), (ex + 8, ey - 14 * direction)]
    draw.polygon(points, fill=fill)


def save_canvas(name: str, size: tuple[int, int] = (1800, 1100)) -> tuple[Image.Image, ImageDraw.ImageDraw, Path]:
    img = Image.new("RGB", size, "#f8fafc")
    draw = ImageDraw.Draw(img)
    path = DIAGRAM_DIR / name
    return img, draw, path


def label(draw: ImageDraw.ImageDraw, pos: tuple[int, int], text: str, size: int = 30, bold: bool = True) -> None:
    draw.text(pos, text, font=font(size, bold), fill="#0f172a")


def diagram_use_case() -> Path:
    img, draw, path = save_canvas("01-use-case.png")
    label(draw, (60, 40), "UML 用例图：XShop AI 电商系统")
    actors = {
        "普通用户": (80, 220, 300, 310),
        "运营管理员": (80, 500, 300, 590),
        "系统管理员": (80, 780, 300, 870),
    }
    for actor, xy in actors.items():
        text_box(draw, xy, actor, fill="#e0f2fe", outline="#0284c7", font_size=28, bold=True)
    system = (390, 140, 1700, 950)
    draw.rounded_rectangle(system, radius=18, outline="#64748b", width=3, fill="#ffffff")
    draw.text((420, 165), "系统边界", font=font(24, True), fill="#475569")
    cases = [
        ("注册/登录", 460, 230),
        ("浏览/搜索商品", 760, 230),
        ("管理购物车", 1060, 230),
        ("下单/支付/收货", 1360, 230),
        ("AI 智能导购", 760, 410),
        ("商品与分类管理", 460, 590),
        ("订单处理", 760, 590),
        ("促销活动管理", 1060, 590),
        ("AI 运营助手", 1360, 590),
        ("用户与角色管理", 760, 770),
        ("后台权限鉴权", 1110, 770),
    ]
    centers: dict[str, tuple[int, int]] = {}
    for text, x, y in cases:
        xy = (x, y, x + 230, y + 92)
        text_box(draw, xy, text, fill="#fefce8", outline="#ca8a04", radius=46, font_size=24)
        centers[text] = (x + 115, y + 46)
    actor_centers = {k: (v[2], (v[1] + v[3]) // 2) for k, v in actors.items()}
    for case in ["注册/登录", "浏览/搜索商品", "管理购物车", "下单/支付/收货", "AI 智能导购"]:
        arrow(draw, actor_centers["普通用户"], centers[case])
    for case in ["注册/登录", "商品与分类管理", "订单处理", "促销活动管理", "AI 运营助手", "后台权限鉴权"]:
        arrow(draw, actor_centers["运营管理员"], centers[case])
    for case in ["用户与角色管理", "后台权限鉴权", "商品与分类管理", "订单处理"]:
        arrow(draw, actor_centers["系统管理员"], centers[case])
    img.save(path)
    return path


def diagram_class() -> Path:
    img, draw, path = save_canvas("02-domain-class.png", (1900, 1200))
    label(draw, (60, 40), "领域类图：核心业务对象及关系")
    classes = {
        "SysUser\nid, username, password\nnickname, status": (70, 150, 390, 270),
        "SysRole\nid, code, name": (500, 150, 790, 270),
        "ProductCategory\nid, parentId, name\nsort, status": (70, 430, 420, 560),
        "Product\nid, categoryId, name\nprice, stock, status": (520, 430, 870, 560),
        "CartItem\nid, userId, productId\nquantity, selected": (1010, 260, 1360, 390),
        "OrderMain\nid, orderNo, userId\ntotalAmount, status": (1010, 560, 1360, 700),
        "OrderItem\nid, orderId, productId\nprice, quantity": (1480, 560, 1820, 700),
        "PaymentRecord\nid, orderId, amount\nstatus, paidAt": (1010, 850, 1360, 980),
        "InventoryRecord\nproductId, beforeStock\nafterStock, businessType": (520, 760, 900, 900),
        "PromotionActivity\nid, name, startTime\nendTime, status": (70, 760, 430, 900),
        "PromotionProduct\nactivityId, productId\npromotionStock, limit": (70, 990, 430, 1120),
        "AiChatRecord\nuserId, scene, prompt\nresponse, model": (1480, 150, 1820, 290),
    }
    centers = {}
    for name, xy in classes.items():
        text_box(draw, xy, name, fill="#ffffff", outline="#334155", radius=8, font_size=22)
        centers[name.split("\n")[0]] = ((xy[0] + xy[2]) // 2, (xy[1] + xy[3]) // 2)
    relations = [
        ("SysUser", "SysRole", "多对多"),
        ("ProductCategory", "Product", "1 对多"),
        ("SysUser", "CartItem", "1 对多"),
        ("Product", "CartItem", "1 对多"),
        ("SysUser", "OrderMain", "1 对多"),
        ("OrderMain", "OrderItem", "1 对多"),
        ("Product", "OrderItem", "1 对多"),
        ("OrderMain", "PaymentRecord", "1 对 1"),
        ("Product", "InventoryRecord", "1 对多"),
        ("PromotionActivity", "PromotionProduct", "1 对多"),
        ("Product", "PromotionProduct", "1 对多"),
        ("SysUser", "AiChatRecord", "1 对多"),
    ]
    for a, b, note in relations:
        arrow(draw, centers[a], centers[b], width=2)
        mx = (centers[a][0] + centers[b][0]) // 2
        my = (centers[a][1] + centers[b][1]) // 2
        draw.text((mx + 8, my + 4), note, font=font(18), fill="#475569")
    img.save(path)
    return path


def diagram_package() -> Path:
    img, draw, path = save_canvas("03-package.png")
    label(draw, (60, 40), "包图：模块化单体结构")
    text_box(draw, (90, 180, 410, 300), "frontend\nVue3 / Pinia / Router", fill="#dcfce7", outline="#16a34a", font_size=24, bold=True)
    text_box(draw, (620, 120, 1510, 940), "backend\nSpring Boot 模块化单体", fill="#ffffff", outline="#475569", font_size=26, bold=True)
    modules = [
        ("auth\n登录注册/JWT", 690, 250),
        ("user\n用户角色", 980, 250),
        ("product\n商品分类", 1270, 250),
        ("cart\n购物车", 690, 430),
        ("order\n订单流程", 980, 430),
        ("inventory\n库存流水", 1270, 430),
        ("promotion\n限时抢购", 690, 610),
        ("ai\n导购/运营", 980, 610),
        ("upload\nOSS 上传", 1270, 610),
        ("common\n响应/异常/分页", 980, 790),
    ]
    for text, x, y in modules:
        text_box(draw, (x, y, x + 210, y + 100), text, fill="#f1f5f9", outline="#64748b", font_size=21)
    text_box(draw, (90, 540, 410, 660), "MySQL\n业务数据", fill="#dbeafe", outline="#2563eb", font_size=24, bold=True)
    text_box(draw, (90, 740, 410, 860), "Redis\n抢购库存", fill="#fee2e2", outline="#dc2626", font_size=24, bold=True)
    text_box(draw, (90, 940, 410, 1040), "OpenAI Compatible API\nAI 能力", fill="#fae8ff", outline="#a21caf", font_size=22, bold=True)
    arrow(draw, (410, 240), (620, 470))
    arrow(draw, (980, 940), (410, 600))
    arrow(draw, (760, 660), (410, 800))
    arrow(draw, (1080, 660), (410, 990))
    img.save(path)
    return path


def diagram_activity() -> Path:
    img, draw, path = save_canvas("04-order-activity.png", (1400, 1300))
    label(draw, (60, 40), "活动图：购物车下单流程")
    steps = [
        ("开始", 600, 120, "#e0f2fe"),
        ("选择购物车商品", 520, 250, "#ffffff"),
        ("校验登录状态", 520, 380, "#ffffff"),
        ("检查商品状态与库存", 520, 510, "#ffffff"),
        ("创建订单与订单项", 520, 640, "#ffffff"),
        ("扣减库存并记录流水", 520, 770, "#ffffff"),
        ("模拟支付", 520, 900, "#ffffff"),
        ("订单状态变为已支付", 520, 1030, "#ffffff"),
        ("结束", 600, 1160, "#e0f2fe"),
    ]
    last_center = None
    centers = []
    for text, x, y, fill in steps:
        xy = (x, y, x + 360, y + 80)
        text_box(draw, xy, text, fill=fill, outline="#334155", radius=38 if text in ("开始", "结束") else 10, font_size=25)
        center = (x + 180, y + 80)
        if last_center:
            arrow(draw, last_center, (x + 180, y))
        centers.append((x + 180, y + 40))
        last_center = center
    text_box(draw, (1010, 420, 1280, 520), "失败提示\n未登录/库存不足", fill="#fee2e2", outline="#dc2626", font_size=22)
    arrow(draw, centers[2], (1010, 470), fill="#dc2626")
    arrow(draw, centers[3], (1010, 470), fill="#dc2626")
    img.save(path)
    return path


def diagram_sequence() -> Path:
    img, draw, path = save_canvas("05-ai-sequence.png", (1900, 1100))
    label(draw, (60, 40), "顺序图：AI 智能导购协作")
    parts = [
        ("用户", 130),
        ("Vue3 前端", 420),
        ("AI Controller", 720),
        ("Product Service", 1040),
        ("MySQL", 1340),
        ("LLM Client", 1630),
    ]
    for name, x in parts:
        text_box(draw, (x - 95, 130, x + 95, 210), name, fill="#e0f2fe", outline="#0284c7", font_size=22, bold=True)
        draw.line([(x, 210), (x, 990)], fill="#94a3b8", width=2)
    messages = [
        (130, 420, 280, "输入购物需求"),
        (420, 720, 390, "POST /api/ai/shopping-guide"),
        (720, 1040, 500, "查询候选商品"),
        (1040, 1340, 610, "读取商品数据"),
        (1340, 1040, 720, "返回商品列表"),
        (1040, 720, 790, "返回候选商品"),
        (720, 1630, 850, "组装 Prompt 并调用模型"),
        (1630, 720, 920, "返回推荐理由"),
        (720, 420, 990, "返回 AI 建议"),
    ]
    for x1, x2, y, text in messages:
        arrow(draw, (x1, y), (x2, y), width=2)
        draw.text((min(x1, x2) + 20, y - 32), text, font=font(19), fill="#334155")
    img.save(path)
    return path


def diagram_state() -> Path:
    img, draw, path = save_canvas("06-order-state.png", (1500, 900))
    label(draw, (60, 40), "状态机图：订单状态流转")
    states = {
        "CREATED\n已创建": (120, 250, 340, 350),
        "PAID\n已支付": (520, 250, 740, 350),
        "SHIPPED\n已发货": (920, 250, 1140, 350),
        "RECEIVED\n已收货": (1220, 250, 1440, 350),
        "CANCELLED\n已取消": (520, 560, 760, 660),
    }
    for text, xy in states.items():
        text_box(draw, xy, text, fill="#ffffff", outline="#334155", font_size=24, bold=True)
    text_box(draw, (120, 560, 260, 660), "开始", fill="#e0f2fe", outline="#0284c7", radius=50, font_size=24)
    text_box(draw, (1220, 560, 1360, 660), "结束", fill="#e0f2fe", outline="#0284c7", radius=50, font_size=24)
    arrow(draw, (260, 610), (520, 300))
    arrow(draw, (340, 300), (520, 300))
    draw.text((395, 260), "支付成功", font=font(18), fill="#475569")
    arrow(draw, (740, 300), (920, 300))
    draw.text((805, 260), "后台发货", font=font(18), fill="#475569")
    arrow(draw, (1140, 300), (1220, 300))
    draw.text((1160, 260), "确认收货", font=font(18), fill="#475569")
    arrow(draw, (230, 350), (520, 610), fill="#dc2626")
    draw.text((320, 505), "用户取消", font=font(18), fill="#dc2626")
    arrow(draw, (630, 350), (630, 560), fill="#dc2626")
    draw.text((650, 455), "后台取消", font=font(18), fill="#dc2626")
    arrow(draw, (760, 610), (1220, 610))
    arrow(draw, (1330, 350), (1290, 560))
    img.save(path)
    return path


def diagram_deployment() -> Path:
    img, draw, path = save_canvas("07-component-deployment.png", (1800, 1000))
    label(draw, (60, 40), "组件/部署图：本地演示环境")
    text_box(draw, (90, 180, 420, 320), "浏览器\nVue3 SPA\nlocalhost:5173", fill="#dcfce7", outline="#16a34a", font_size=24, bold=True)
    text_box(draw, (680, 160, 1120, 340), "应用服务器\nSpring Boot\nlocalhost:8080", fill="#e0f2fe", outline="#0284c7", font_size=26, bold=True)
    text_box(draw, (1370, 100, 1690, 230), "MySQL 8\n业务数据", fill="#dbeafe", outline="#2563eb", font_size=24, bold=True)
    text_box(draw, (1370, 330, 1690, 460), "Redis\n促销库存", fill="#fee2e2", outline="#dc2626", font_size=24, bold=True)
    text_box(draw, (1370, 560, 1690, 690), "阿里云 OSS\n商品图片", fill="#fef3c7", outline="#d97706", font_size=24, bold=True)
    text_box(draw, (1370, 780, 1690, 910), "OpenAI 兼容 API\nAI 服务", fill="#fae8ff", outline="#a21caf", font_size=24, bold=True)
    arrow(draw, (420, 250), (680, 250))
    draw.text((485, 215), "HTTP / REST / JWT", font=font(21), fill="#475569")
    for y in [165, 395, 625, 845]:
        arrow(draw, (1120, 250), (1370, y))
    img.save(path)
    return path


def generate_diagrams() -> list[Path]:
    return [
        diagram_use_case(),
        diagram_class(),
        diagram_package(),
        diagram_activity(),
        diagram_sequence(),
        diagram_state(),
        diagram_deployment(),
    ]


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_doc_style(doc: Document) -> None:
    styles = doc.styles
    styles["Normal"].font.name = BODY_FONT
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    styles["Normal"].font.size = Pt(11)
    for style_name in ["Title", "Heading 1", "Heading 2", "Heading 3"]:
        style = styles[style_name]
        style.font.name = TITLE_FONT
        style._element.rPr.rFonts.set(qn("w:eastAsia"), TITLE_FONT)


def add_title_page(doc: Document, title: str, subtitle: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("\n\n\n")
    run = p.add_run(title)
    run.font.name = TITLE_FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), TITLE_FONT)
    run.font.size = Pt(26)
    run.bold = True
    p.add_run("\n")
    sub = p.add_run(subtitle)
    sub.font.name = TITLE_FONT
    sub._element.rPr.rFonts.set(qn("w:eastAsia"), TITLE_FONT)
    sub.font.size = Pt(16)
    sub.font.color.rgb = RGBColor(71, 85, 105)
    p.add_run("\n\n\n\n")
    info = [
        "课程名称：《面向对象技术与方法》",
        "项目名称：XShop B2C AI 电商系统",
        "姓名：________________",
        "学号：________________",
        "班级：________________",
        f"日期：{TODAY}",
    ]
    for item in info:
        row = doc.add_paragraph()
        row.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = row.add_run(item)
        r.font.name = BODY_FONT
        r._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
        r.font.size = Pt(14)
    doc.add_page_break()


def add_toc_note(doc: Document) -> None:
    p = doc.add_paragraph()
    r = p.add_run("目录提示：在 Word/WPS 中可通过“引用 - 目录”基于标题样式自动生成目录。")
    r.italic = True
    r.font.color.rgb = RGBColor(100, 116, 139)


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr[i].text = header
        set_cell_shading(hdr[i], "E2E8F0")
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = val
    doc.add_paragraph()


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_numbered(doc: Document, items: list[str]) -> None:
    for item in items:
        doc.add_paragraph(item, style="List Number")


def add_image(doc: Document, path: Path, caption: str, width: float = 6.4) -> None:
    if not path.exists():
        doc.add_paragraph(f"[缺少图片：{path.name}] {caption}")
        return
    doc.add_picture(str(path), width=Inches(width))
    p = doc.add_paragraph(caption)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(71, 85, 105)


def paragraph(doc: Document, text: str) -> None:
    doc.add_paragraph(text)


def heading(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def save_doc(doc: Document, filename: str) -> Path:
    target = FINAL_DIR / filename
    try:
        doc.save(target)
        return target
    except PermissionError:
        fallback = target.with_name(f"{target.stem}.updated{target.suffix}")
        doc.save(fallback)
        print(f"{target} is locked; wrote {fallback} instead")
        return fallback


def run_git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True, encoding="utf-8", errors="replace").strip()
    except Exception:
        return ""


def count_lines() -> tuple[list[list[str]], int]:
    exts = {".java", ".vue", ".ts", ".css", ".sql", ".xml", ".yml", ".json", ".html", ".mjs", ".md", ".py"}
    parts: dict[str, tuple[int, int]] = {}
    total = 0
    for base in ["backend", "frontend", "docs"]:
        for path in (REPO / base).rglob("*"):
            if not path.is_file() or path.suffix not in exts:
                continue
            rel = path.relative_to(REPO)
            if "node_modules" in rel.parts or "dist" in rel.parts or "target" in rel.parts:
                continue
            if path.name == "package-lock.json":
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").count("\n") + 1
            files, old = parts.get(base, (0, 0))
            parts[base] = (files + 1, old + lines)
            total += lines
    readme = REPO / "README.md"
    if readme.exists():
        lines = readme.read_text(encoding="utf-8", errors="ignore").count("\n") + 1
        parts["README"] = (1, lines)
        total += lines
    rows = [[part, str(files), str(lines)] for part, (files, lines) in sorted(parts.items())]
    return rows, total


def create_requirements_doc(diagrams: dict[str, Path]) -> None:
    doc = Document()
    set_doc_style(doc)
    add_title_page(doc, "系统需求文档", "XShop B2C AI 电商系统")
    add_toc_note(doc)

    heading(doc, "一、项目可行性分析与领域描述")
    heading(doc, "1.1 领域边界", 2)
    paragraph(doc, "XShop 属于 B2C 在线零售领域，覆盖消费者从商品浏览、搜索、加入购物车、下单、模拟支付到订单跟踪的核心购物流程，同时覆盖运营人员对商品、分类、订单、促销、库存和 AI 运营内容的管理流程。系统不覆盖真实第三方支付、真实物流、多商户结算、供应链采购和财务结算。")
    heading(doc, "1.2 目标用户与需求", 2)
    add_table(doc, ["用户类型", "核心需求", "系统响应"], [
        ["普通用户", "快速找到商品并完成稳定购买流程", "商品首页、搜索筛选、详情页、购物车、订单中心、AI 导购"],
        ["运营管理员", "维护商品和促销，处理订单并获得运营建议", "后台商品/订单/促销管理、AI 商品文案和运营分析"],
        ["系统管理员", "控制后台权限和用户状态", "用户管理、角色调整、接口鉴权"],
    ])
    heading(doc, "1.3 竞品分析", 2)
    add_table(doc, ["对比对象", "成熟平台能力", "本系统定位"], [
        ["京东/淘宝/拼多多", "完整支付、物流、供应链、推荐、客服和商家体系", "聚焦课程项目可验证的核心交易链路和 AI 服务集成"],
        ["传统电商管理后台", "侧重商品、订单、库存管理", "在后台增加 AI 文案生成与运营分析能力"],
        ["AI 导购应用", "侧重自然语言问答", "与真实商品库、订单流程和后台管理协同"],
    ])

    heading(doc, "二、系统功能分析、原型设计与开发计划")
    heading(doc, "2.1 功能分解", 2)
    paragraph(doc, "系统功能按业务重要性和依赖关系划分如下。订单中心、商品中心和 AI 服务是本项目的核心能力，认证权限、购物车和后台管理为核心链路提供支撑。")
    add_table(doc, ["一级功能", "二级功能", "权重", "依赖关系"], [
        ["认证与权限", "注册登录、JWT 鉴权、角色权限", "10", "独立基础功能"],
        ["商品中心", "分类管理、商品管理、搜索、详情", "15", "依赖认证用于后台管理"],
        ["购物车", "加入、修改数量、删除、选择结算", "10", "依赖商品与登录态"],
        ["订单中心", "创建订单、库存扣减、支付、取消、收货", "20", "依赖用户、商品、购物车、库存"],
        ["促销秒杀", "活动配置、活动库存、抢购下单", "10", "依赖商品、订单、Redis"],
        ["AI 服务", "智能导购、商品问答、文案生成、运营分析", "15", "依赖商品数据和外部模型服务"],
        ["后台管理", "商品运营、订单处理、用户管理", "10", "依赖角色权限"],
        ["数据看板", "销售额、订单趋势、库存预警", "10", "依赖订单和商品数据"],
    ])
    heading(doc, "2.2 用户权限与用例图", 2)
    add_image(doc, diagrams["use_case"], "图 1 UML 用例图：用户类型、后台权限和主要业务用例。")
    heading(doc, "2.3 客户端与服务端职责", 2)
    add_table(doc, ["组成部分", "职责"], [
        ["Client 端 Vue3 应用", "负责页面展示、路由跳转、表单校验、登录态保存、购物交互和后台管理界面，通过 Axios 调用后端 API。"],
        ["Server 端 Spring Boot 应用", "负责认证鉴权、业务规则、事务一致性、数据持久化、Redis 抢购库存、OSS 上传和 AI 服务调用。"],
        ["MySQL/Redis/OSS/LLM", "分别承担业务数据持久化、促销库存缓存、商品图片存储和 AI 能力输出。"],
    ])
    heading(doc, "2.4 原型与运行截图", 2)
    screenshots = [
        ("store-home.png", "图 2 商城首页：展示品牌首页、商品搜索、分类筛选、限时抢购和 AI 导购入口。"),
        ("product-detail.png", "图 3 商品详情：展示商品图片、价格、库存、详情、加入购物车和商品问答入口。"),
        ("cart.png", "图 4 购物车：支持商品数量修改、删除、勾选结算和订单创建。"),
        ("orders.png", "图 5 我的订单：展示订单状态、商品明细、支付、取消和确认收货操作。"),
        ("admin-products.png", "图 6 后台商品管理：支持商品查询、新增、编辑、上下架和图片上传。"),
        ("admin-orders.png", "图 7 后台订单管理：支持订单筛选、详情查看、发货和取消。"),
        ("admin-promotions.png", "图 8 后台促销管理：支持限时抢购活动配置和启停。"),
        ("admin-ai-operation.png", "图 9 AI 运营助手：支持商品文案生成和运营分析。"),
    ]
    for filename, caption in screenshots:
        add_image(doc, SCREENSHOT_DIR / filename, caption, width=6.2)
    heading(doc, "2.5 开发计划", 2)
    add_table(doc, ["时间", "开发活动", "产出"], [
        ["2026-06-04 至 2026-06-05", "完成需求、数据库、接口、UML 草稿，初始化前后端项目", "项目骨架、README、初始文档"],
        ["2026-06-06 至 2026-06-09", "完成认证、权限、用户、商品分类和商品管理", "登录注册、商品列表、后台商品管理"],
        ["2026-06-10 至 2026-06-13", "完成购物车、订单、支付、库存扣减和订单管理", "完整购物链路和库存流水"],
        ["2026-06-14 至 2026-06-16", "完成限时抢购、Redis 库存、AI 导购和 AI 运营功能", "促销链路、AI 接口和页面"],
        ["2026-06-17 至 2026-06-20", "完成测试、截图、文档和打包检查", "测试报告、截图、三份结课文档"],
    ])

    heading(doc, "三、领域模型")
    heading(doc, "3.1 领域类图", 2)
    add_image(doc, diagrams["class"], "图 10 领域类图：展示用户、角色、商品、订单、支付、促销、库存和 AI 记录之间的关系。")
    heading(doc, "3.2 包图", 2)
    add_image(doc, diagrams["package"], "图 11 包图：展示前端、后端业务包和外部基础设施的协作边界。")
    heading(doc, "3.3 动态行为图", 2)
    add_image(doc, diagrams["activity"], "图 12 下单活动图：购物车订单创建、库存校验和支付流程。")
    add_image(doc, diagrams["sequence"], "图 13 AI 导购顺序图：前端、AI 控制器、商品服务、数据库和模型服务协作。")
    add_image(doc, diagrams["state"], "图 14 订单状态机图：订单从创建到支付、发货、收货或取消的状态流转。")

    save_doc(doc, "系统需求文档.docx")


def create_design_doc(diagrams: dict[str, Path]) -> None:
    doc = Document()
    set_doc_style(doc)
    add_title_page(doc, "系统设计文档", "XShop B2C AI 电商系统")
    add_toc_note(doc)

    heading(doc, "一、技术选型")
    add_table(doc, ["层次", "选型", "理由"], [
        ["后端", "Java 8、Spring Boot 2.7.18", "本地 JDK 为 1.8，Spring Boot 2.7 对 Java 8 兼容稳定，适合快速构建 REST 服务。"],
        ["数据访问", "MyBatis-Plus、MySQL 8", "简化 CRUD 与分页查询，MySQL 适合课程项目的关系型交易数据。"],
        ["安全", "Spring Security、JWT", "支持前后端分离认证和后台角色鉴权。"],
        ["缓存", "Redis", "用于限时抢购活动库存，降低短时访问对数据库的压力。"],
        ["前端", "Vue3、TypeScript、Vite、Pinia、Vue Router、Element Plus", "开发效率高，组件生态成熟，适合管理后台和商城前台。"],
        ["AI", "OpenAI 兼容 API", "便于接入 OpenAI、DeepSeek、通义千问等兼容模型，支持演示环境替换。"],
        ["存储", "阿里云 OSS", "用于商品主图上传和公网访问。"],
    ])

    heading(doc, "二、系统架构设计")
    paragraph(doc, "系统采用前后端分离的模块化单体架构。后端不是拆分为多个独立部署微服务，而是在单个 Spring Boot 应用内按业务边界拆分为认证、用户、商品、购物车、订单、库存、促销、AI、上传和公共模块。该方式适合个人课程项目，降低部署和调试复杂度，同时保留清晰的服务边界。")
    add_image(doc, diagrams["deployment"], "图 1 组件/部署图：本地演示环境中的客户端、服务端、数据库、Redis、OSS 和 AI 服务。")
    add_image(doc, diagrams["package"], "图 2 后端包图：模块边界和外部基础设施依赖。")
    heading(doc, "2.1 子系统边界", 2)
    add_table(doc, ["子系统", "边界", "交换信息"], [
        ["商城前台", "商品浏览、购物车、订单、AI 导购", "通过 REST API 传递商品、购物车、订单和 AI 请求数据"],
        ["后台运营端", "商品、分类、订单、促销、用户和 AI 运营管理", "通过 JWT 保护的后台 API 传递管理数据"],
        ["后端服务", "统一承载业务规则、事务和外部服务调用", "读写 MySQL/Redis，调用 OSS 和 AI API"],
        ["外部 AI 服务", "生成导购建议、问答、商品文案、运营分析", "接收 Prompt 与商品上下文，返回自然语言结果"],
    ])
    heading(doc, "2.2 数据存储设计", 2)
    add_table(doc, ["数据表", "说明"], [
        ["sys_user / sys_role / sys_user_role", "用户、角色及用户角色关联"],
        ["product_category / product / product_image", "商品分类、商品主数据和图片"],
        ["cart_item", "用户购物车项"],
        ["order_main / order_item / payment_record", "订单主表、明细和模拟支付记录"],
        ["inventory_record", "库存变更流水，用于追踪扣减和回滚"],
        ["promotion_activity / promotion_product", "限时抢购活动和活动商品"],
        ["ai_chat_record", "AI 调用场景、输入、响应和模型记录"],
        ["operation_log", "预留后台操作日志表"],
    ])

    heading(doc, "三、关键技术方案")
    heading(doc, "3.1 认证与鉴权", 2)
    paragraph(doc, "用户登录成功后由后端签发 JWT，前端存储 token 并在 Axios 请求中携带 Authorization 头。Spring Security 过滤器解析 token 后写入当前用户上下文，后台接口按 USER、OPERATOR、ADMIN 等角色进行访问控制。普通用户不能访问后台管理页面和后台 API。")
    heading(doc, "3.2 订单事务一致性", 2)
    paragraph(doc, "普通订单创建与库存扣减放在同一个数据库事务中执行：先校验购物车、商品状态和库存，再创建 order_main 和 order_item，随后扣减 product.stock 并写入 inventory_record。取消未完成订单时恢复库存，支付和订单状态变更保持一致。")
    add_image(doc, diagrams["activity"], "图 3 订单创建活动图。")
    add_image(doc, diagrams["state"], "图 4 订单状态机图。")
    heading(doc, "3.3 限时抢购与高并发处理", 2)
    paragraph(doc, "促销活动使用 Redis 保存活动库存，抢购请求优先扣减 Redis 库存，降低对 MySQL 的瞬时压力。订单创建失败时回滚 Redis 库存；数据库仍保存活动商品和订单明细，便于最终一致性核对。课程项目未引入消息队列，后续可扩展为 Redis Lua 脚本加异步下单队列。")
    heading(doc, "3.4 AI 服务集成", 2)
    paragraph(doc, "AI 模块提供智能导购、商品问答、商品文案和运营分析接口。后端根据业务场景拼接商品上下文与用户问题，调用 OpenAI 兼容 API，并将 prompt、response、scene、model 保存到 ai_chat_record。若未配置 API Key 或模型调用失败，服务返回模板化降级结果，保证课堂演示稳定。")
    add_image(doc, diagrams["sequence"], "图 5 AI 导购顺序图。")
    heading(doc, "3.5 商品图片上传", 2)
    paragraph(doc, "后台商品管理支持本地图片选择，前端通过 multipart/form-data 上传到后端，后端使用阿里云 OSS SDK 上传对象并返回可访问 URL，数据库只保存最终图片地址。")
    heading(doc, "3.6 日志、故障定位与监控", 2)
    paragraph(doc, "开发和演示阶段主要使用 Spring Boot 控制台日志、统一异常处理和 HTTP 状态码定位问题。典型排查路径为：检查浏览器 Network 请求、确认后端接口日志、核对数据库记录和 Redis 库存。生产化演进可接入 Actuator、集中日志和告警系统。")

    heading(doc, "四、接口设计概要")
    add_table(doc, ["模块", "接口"], [
        ["认证", "POST /api/auth/register；POST /api/auth/login；GET /api/auth/profile"],
        ["商品", "GET /api/categories；GET /api/products；GET /api/products/{id}"],
        ["购物车", "GET/POST /api/cart/items；PUT/DELETE /api/cart/items/{id}"],
        ["订单", "POST /api/orders；GET /api/orders；POST /api/orders/{id}/pay|cancel|receive"],
        ["促销", "GET /api/promotions/active；GET /api/promotions/{id}；POST /api/promotions/{id}/orders"],
        ["AI", "POST /api/ai/shopping-guide；/product-qa；/product-copywriting；/operation-analysis"],
        ["后台", "/api/admin/products；/orders；/promotions；/users；/uploads/product-images"],
    ])

    heading(doc, "五、运行、部署与环境说明")
    add_table(doc, ["项目", "说明"], [
        ["后端环境", "JDK 1.8、Maven 3.8+、Spring Boot 2.7.18"],
        ["前端环境", "Node.js 20、npm、Vite 6、Vue3"],
        ["基础设施", "MySQL 8、Redis、可选阿里云 OSS、可选 OpenAI 兼容模型 API"],
        ["后端启动", "cd backend && mvn spring-boot:run，默认 http://localhost:8080"],
        ["前端启动", "cd frontend && npm run dev，默认 http://localhost:5173"],
        ["数据库初始化", "先执行 schema.sql 创建表，再执行 data.sql 导入演示账号与商品数据"],
        ["卸载方法", "停止前后端进程，删除 ai_commerce 数据库和前端 node_modules 即可清理本地部署"],
    ])
    heading(doc, "六、系统规模", 2)
    rows, total = count_lines()
    add_table(doc, ["范围", "文件数", "代码/文档行数"], rows + [["合计", "-", str(total)]])
    paragraph(doc, "统计口径为工程交付宽口径，包含 backend、frontend、docs、README 中的 Java、Vue、TypeScript、CSS、SQL、XML、YAML、JSON、HTML、脚本、Markdown 和文档生成脚本，不包含 node_modules、dist、target、package-lock.json 等依赖或构建产物。")

    save_doc(doc, "系统设计文档.docx")


def create_management_doc() -> None:
    doc = Document()
    set_doc_style(doc)
    add_title_page(doc, "项目管理文档", "XShop B2C AI 电商系统")
    add_toc_note(doc)

    heading(doc, "一、项目组成员及分工")
    add_table(doc, ["成员", "学号", "承担工作", "贡献占比"], [
        ["________________", "________________", "个人独立完成需求分析、架构设计、数据库设计、后端开发、前端开发、AI 服务集成、测试、截图和文档整理。", "100%"],
    ])
    paragraph(doc, "本项目按个人结课设计组织，使用 Git 管理代码版本，结合 AI 工具辅助需求梳理、代码生成、问题排查、测试设计和文档整理。")

    heading(doc, "二、AI 应用情况报告")
    add_table(doc, ["阶段", "AI 使用方式", "人工确认与修改"], [
        ["需求分析", "辅助拆分 B2C 电商系统功能、梳理用户角色和用例。", "根据课程要求和实际开发规模确定功能边界。"],
        ["后端开发", "辅助生成 Spring Boot 控制器、Service、DTO、实体、MyBatis-Plus Mapper 和异常处理代码。", "人工检查事务边界、权限控制、库存扣减和降级逻辑。"],
        ["前端开发", "辅助生成 Vue3 页面结构、Element Plus 表格表单、Axios API 封装和 Pinia 登录态管理。", "人工调整页面风格、交互流程和路由权限。"],
        ["AI 功能", "辅助设计 Prompt、导购问答、商品文案和运营分析的接口形态。", "人工添加商品上下文、调用记录保存和失败降级。"],
        ["测试与排错", "辅助设计权限、订单流程和库存一致性测试，定位构建或接口问题。", "人工运行测试并修复具体错误。"],
        ["文档整理", "辅助将草稿整理为课程要求的三份正式文档，并生成图表说明。", "人工核对项目事实、截图和统计口径。"],
    ])
    paragraph(doc, "AI 的作用是提高开发效率和帮助形成初稿，关键业务规则、运行结果、截图和最终提交内容均以本项目实际代码和本地验证结果为准。")

    heading(doc, "三、实际开发记录")
    add_table(doc, ["日期", "开发活动", "相关产出"], [
        ["2026-06-04", "创建项目仓库，搭建 Spring Boot 后端和 Vue3 前端骨架。", "初始项目结构、README、基础页面"],
        ["2026-06-05", "完成需求、数据库、接口和 UML 初稿。", "requirements-draft、database-design、api-design、uml-draft"],
        ["2026-06-06 至 2026-06-09", "实现注册登录、JWT、角色权限、商品分类和商品管理。", "auth/user/product 模块与前端页面"],
        ["2026-06-10 至 2026-06-13", "实现购物车、订单、模拟支付、库存流水和后台订单处理。", "cart/order/inventory/payment 模块"],
        ["2026-06-14 至 2026-06-16", "实现限时抢购、AI 导购、商品问答、AI 文案和运营分析。", "promotion/ai 模块与对应页面"],
        ["2026-06-16", "统一前台哥特风界面、后台页面、截图脚本和运行截图。", "docs/screenshots、前端样式优化"],
        ["2026-06-17 至 2026-06-20", "整理结课设计文档，补充设计图、截图、代码量统计和验证记录。", "三份 Word 文档、diagrams、final 目录"],
    ])
    heading(doc, "四、Git Commit 记录")
    log = run_git(["log", "--oneline", "--decorate", "--max-count=20"])
    if log:
        for line in log.splitlines():
            doc.add_paragraph(line, style="List Bullet")
    else:
        paragraph(doc, "未能读取 Git 记录。")

    heading(doc, "五、关键产出清单")
    add_bullets(doc, [
        "后端 Spring Boot 项目：认证、商品、购物车、订单、库存、促销、AI、上传和后台管理模块。",
        "前端 Vue3 项目：商城首页、商品详情、购物车、订单中心、后台商品/订单/促销/用户/AI 页面。",
        "数据库脚本：schema.sql 和 data.sql，可初始化演示数据和默认账号。",
        "测试用例：权限、订单流程和库存一致性集成测试。",
        "自动截图脚本：frontend/scripts/capture-screenshots.mjs。",
        "结课文档：系统需求文档、系统设计文档、项目管理文档。",
    ])

    heading(doc, "六、项目总结")
    paragraph(doc, "项目完成了一个前后端分离的 B2C AI 电商系统，核心购物链路、后台运营链路、限时抢购库存控制和 AI 服务均可本地演示。由于项目为个人课程设计，系统采用模块化单体而非多服务拆分，降低了部署成本；后续若继续完善，可补充真实支付、物流、消息队列、监控告警和更完整的数据看板。")

    rows, total = count_lines()
    heading(doc, "七、代码量统计")
    add_table(doc, ["范围", "文件数", "代码/文档行数"], rows + [["合计", "-", str(total)]])
    paragraph(doc, "统计口径与系统设计文档一致，为工程交付宽口径。")

    save_doc(doc, "项目管理文档.docx")


def route(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: str = "#475569", width: int = 3) -> None:
    if len(points) < 2:
        return
    draw.line(points, fill=fill, width=width, joint="curve")
    arrow(draw, points[-2], points[-1], fill=fill, width=width)


def diagram_use_case_clean() -> Path:
    img, draw, path = save_canvas("01-use-case.png", (2100, 1250))
    label(draw, (70, 45), "UML 用例图：XShop AI 电商系统")
    actors = [
        ("普通用户", (90, 220, 320, 310), "#e0f2fe", "#0284c7"),
        ("运营管理员", (90, 520, 320, 610), "#dcfce7", "#16a34a"),
        ("系统管理员", (90, 820, 320, 910), "#fae8ff", "#a21caf"),
    ]
    for name, xy, fill, outline in actors:
        text_box(draw, xy, name, fill=fill, outline=outline, font_size=28, bold=True)

    system = (430, 130, 1990, 1080)
    draw.rounded_rectangle(system, radius=18, outline="#64748b", width=3, fill="#ffffff")
    draw.text((470, 165), "系统边界", font=font(24, True), fill="#475569")

    columns = [
        ("前台购物", ["注册/登录", "浏览/搜索商品", "AI 智能导购", "管理购物车", "下单/支付/收货"], 520),
        ("运营后台", ["商品与分类管理", "订单处理", "促销活动管理", "AI 运营助手", "销售看板"], 1010),
        ("系统管理", ["用户与角色管理", "后台权限鉴权", "运行数据维护"], 1500),
    ]
    centers: dict[str, tuple[int, int]] = {}
    for title, cases, x in columns:
        draw.rounded_rectangle((x - 35, 220, x + 345, 980), radius=14, fill="#f8fafc", outline="#cbd5e1", width=2)
        draw.text((x + 88, 240), title, font=font(25, True), fill="#0f172a")
        for idx, case in enumerate(cases):
            y = 315 + idx * 125
            xy = (x, y, x + 280, y + 78)
            text_box(draw, xy, case, fill="#fefce8", outline="#ca8a04", radius=36, font_size=23)
            centers[case] = (x + 140, y + 39)

    # Keep actor links on dedicated horizontal lanes to avoid crossing use-case nodes.
    lanes = {
        "普通用户": (320, 265, ["注册/登录", "浏览/搜索商品", "AI 智能导购", "管理购物车", "下单/支付/收货"]),
        "运营管理员": (320, 565, ["注册/登录", "商品与分类管理", "订单处理", "促销活动管理", "AI 运营助手", "销售看板", "后台权限鉴权"]),
        "系统管理员": (320, 865, ["用户与角色管理", "后台权限鉴权", "运行数据维护"]),
    }
    lane_x = {"普通用户": 370, "运营管理员": 390, "系统管理员": 410}
    for actor, (start_x, y, cases) in lanes.items():
        spine_x = lane_x[actor]
        draw.line([(start_x, y), (spine_x, y)], fill="#64748b", width=3)
        for case in cases:
            cx, cy = centers[case]
            mid_x = cx - 165
            route(draw, [(spine_x, y), (mid_x, y), (mid_x, cy), (cx - 140, cy)], width=2)
    img.save(path)
    return path


def diagram_class_clean() -> Path:
    img, draw, path = save_canvas("02-domain-class.png", (2200, 1450))
    label(draw, (70, 45), "领域类图：核心业务对象及关系")
    groups = [
        ("用户与权限", (70, 140, 590, 440), [
            ("SysUser\nid, username, password\nnickname, phone, status", (110, 210, 350, 330)),
            ("SysRole\nid, code, name", (390, 210, 550, 330)),
        ]),
        ("商品与促销", (70, 520, 790, 1230), [
            ("ProductCategory\nid, parentId, name\nsort, status", (110, 610, 390, 740)),
            ("Product\nid, categoryId, name\nprice, stock, status", (470, 610, 750, 740)),
            ("PromotionActivity\nid, name, startTime\nendTime, status", (110, 880, 390, 1010)),
            ("PromotionProduct\nactivityId, productId\npromotionPrice, stock, limit", (470, 880, 750, 1030)),
            ("InventoryRecord\nproductId, changeQuantity\nbeforeStock, afterStock", (470, 1090, 750, 1210)),
        ]),
        ("交易链路", (900, 140, 1500, 1230), [
            ("CartItem\nid, userId, productId\nquantity, selected", (980, 260, 1260, 390)),
            ("OrderMain\nid, orderNo, userId\ntotalAmount, status", (980, 560, 1260, 700)),
            ("OrderItem\nid, orderId, productId\nprice, quantity", (980, 840, 1260, 970)),
            ("PaymentRecord\nid, orderId, paymentNo\namount, status", (980, 1100, 1260, 1230)),
        ]),
        ("AI 记录", (1620, 140, 2090, 440), [
            ("AiChatRecord\nid, userId, scene\nprompt, response, model", (1710, 230, 2000, 360)),
        ]),
    ]
    boxes: dict[str, tuple[int, int, int, int]] = {}
    for title, frame, items in groups:
        draw.rounded_rectangle(frame, radius=18, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 25, frame[1] + 22), title, font=font(25, True), fill="#0f172a")
        for text, xy in items:
            text_box(draw, xy, text, fill="#f8fafc", outline="#334155", radius=8, font_size=20)
            boxes[text.split("\n")[0]] = xy

    def right(name: str) -> tuple[int, int]:
        x1, y1, x2, y2 = boxes[name]
        return x2, (y1 + y2) // 2

    def left(name: str) -> tuple[int, int]:
        x1, y1, x2, y2 = boxes[name]
        return x1, (y1 + y2) // 2

    def bottom(name: str) -> tuple[int, int]:
        x1, y1, x2, y2 = boxes[name]
        return (x1 + x2) // 2, y2

    def top(name: str) -> tuple[int, int]:
        x1, y1, x2, y2 = boxes[name]
        return (x1 + x2) // 2, y1

    relations = [
        (right("SysUser"), left("SysRole"), "多对多"),
        (right("SysUser"), left("CartItem"), "1 对多"),
        (right("SysUser"), left("OrderMain"), "1 对多"),
        (right("SysUser"), left("AiChatRecord"), "1 对多"),
        (right("ProductCategory"), left("Product"), "1 对多"),
        (right("Product"), left("CartItem"), "1 对多"),
        (right("Product"), left("OrderItem"), "1 对多"),
        (bottom("Product"), top("InventoryRecord"), "1 对多"),
        (bottom("PromotionActivity"), top("PromotionProduct"), "1 对多"),
        (right("Product"), left("PromotionProduct"), "1 对多"),
        (bottom("OrderMain"), top("OrderItem"), "1 对多"),
        (bottom("OrderItem"), top("PaymentRecord"), "订单支付"),
    ]
    for start, end, note in relations:
        sx, sy = start
        ex, ey = end
        if abs(sx - ex) > 120:
            mid = (sx + ex) // 2
            pts = [(sx, sy), (mid, sy), (mid, ey), (ex, ey)]
        else:
            pts = [(sx, sy), (sx, (sy + ey) // 2), (ex, (sy + ey) // 2), (ex, ey)]
        route(draw, pts, width=2)
        draw.text(((sx + ex) // 2 + 8, (sy + ey) // 2 - 18), note, font=font(17), fill="#475569")
    img.save(path)
    return path


def diagram_package_clean() -> Path:
    img, draw, path = save_canvas("03-package.png", (2200, 1250))
    label(draw, (70, 45), "包图：模块化单体结构")
    text_box(draw, (80, 230, 380, 350), "Client\nVue3 SPA", fill="#dcfce7", outline="#16a34a", font_size=28, bold=True)
    draw.rounded_rectangle((560, 130, 1620, 1040), radius=18, fill="#ffffff", outline="#64748b", width=3)
    draw.text((600, 165), "Server：Spring Boot 模块化单体", font=font(28, True), fill="#0f172a")
    modules = [
        ("auth\n认证", 630, 260), ("user\n用户角色", 880, 260), ("common\n公共能力", 1130, 260),
        ("product\n商品分类", 630, 460), ("cart\n购物车", 880, 460), ("order\n订单", 1130, 460),
        ("inventory\n库存", 630, 660), ("promotion\n促销", 880, 660), ("ai\nAI 服务", 1130, 660),
        ("upload\nOSS 上传", 880, 860),
    ]
    for text, x, y in modules:
        text_box(draw, (x, y, x + 190, y + 100), text, fill="#f8fafc", outline="#334155", font_size=22)
    infra = [
        ("MySQL\n业务数据", (1800, 180, 2080, 300), "#dbeafe", "#2563eb"),
        ("Redis\n抢购库存", (1800, 420, 2080, 540), "#fee2e2", "#dc2626"),
        ("阿里云 OSS\n商品图片", (1800, 660, 2080, 780), "#fef3c7", "#d97706"),
        ("OpenAI 兼容 API\nAI 能力", (1800, 900, 2080, 1020), "#fae8ff", "#a21caf"),
    ]
    for text, xy, fill, outline in infra:
        text_box(draw, xy, text, fill=fill, outline=outline, font_size=23, bold=True)
    route(draw, [(380, 290), (560, 290)], width=3)
    # Server-to-infrastructure links leave from the right edge and travel in separate lanes.
    lanes = [(1620, 240, 1800, 240), (1620, 480, 1800, 480), (1620, 720, 1800, 720), (1620, 960, 1800, 960)]
    for pts in lanes:
        route(draw, [pts[:2], pts[2:]], width=3)
    img.save(path)
    return path


def diagram_activity_clean() -> Path:
    img, draw, path = save_canvas("04-order-activity.png", (1700, 1300))
    label(draw, (70, 45), "活动图：购物车下单流程")
    lanes = [("用户", 70, 430), ("前端", 430, 790), ("后端服务", 790, 1210), ("数据库", 1210, 1630)]
    for title, x1, x2 in lanes:
        draw.rounded_rectangle((x1, 130, x2, 1180), radius=12, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((x1 + 25, 155), title, font=font(24, True), fill="#0f172a")
    nodes = [
        ("选择商品并结算", (120, 270, 360, 350)),
        ("填写收货信息", (480, 270, 720, 350)),
        ("提交创建订单", (480, 440, 720, 520)),
        ("校验登录/购物车", (870, 440, 1130, 520)),
        ("检查上架与库存", (870, 610, 1130, 690)),
        ("写入订单主表/明细", (1280, 610, 1560, 690)),
        ("扣减库存/写流水", (1280, 780, 1560, 860)),
        ("返回订单详情", (870, 950, 1130, 1030)),
        ("跳转订单详情", (480, 950, 720, 1030)),
    ]
    centers = []
    for text, xy in nodes:
        text_box(draw, xy, text, fill="#f8fafc", outline="#334155", font_size=21)
        centers.append(((xy[0] + xy[2]) // 2, (xy[1] + xy[3]) // 2))
    for a, b in zip(centers, centers[1:]):
        route(draw, [a, ((a[0] + b[0]) // 2, a[1]), ((a[0] + b[0]) // 2, b[1]), b], width=2)
    text_box(draw, (870, 780, 1130, 860), "失败返回提示", fill="#fee2e2", outline="#dc2626", font_size=21)
    route(draw, [centers[4], (1000, 740), (1000, 780)], fill="#dc2626", width=2)
    img.save(path)
    return path


def diagram_sequence_clean() -> Path:
    img, draw, path = save_canvas("05-ai-sequence.png", (2100, 1150))
    label(draw, (70, 45), "顺序图：AI 智能导购协作")
    parts = [("用户", 160), ("Vue3 前端", 470), ("AI Controller", 810), ("Product Service", 1160), ("MySQL", 1500), ("LLM Client", 1810)]
    for name, x in parts:
        text_box(draw, (x - 120, 140, x + 120, 220), name, fill="#e0f2fe", outline="#0284c7", font_size=22, bold=True)
        draw.line([(x, 220), (x, 1020)], fill="#cbd5e1", width=2)
    messages = [
        (160, 470, 300, "输入预算/场景/偏好"),
        (470, 810, 390, "POST /api/ai/shopping-guide"),
        (810, 1160, 480, "查询候选商品"),
        (1160, 1500, 570, "读取商品列表"),
        (1500, 1160, 660, "返回商品数据"),
        (1160, 810, 750, "返回候选商品"),
        (810, 1810, 840, "组装 Prompt 调用模型"),
        (1810, 810, 930, "返回推荐内容"),
        (810, 470, 1010, "保存记录并返回结果"),
    ]
    for x1, x2, y, text in messages:
        route(draw, [(x1, y), (x2, y)], width=2)
        draw.text((min(x1, x2) + 16, y - 30), text, font=font(19), fill="#334155")
    img.save(path)
    return path


def diagram_state_clean() -> Path:
    img, draw, path = save_canvas("06-order-state.png", (1700, 900))
    label(draw, (70, 45), "状态机图：订单状态流转")
    states = {
        "CREATED\n待支付": (210, 230, 430, 330),
        "PAID\n已支付": (600, 230, 820, 330),
        "SHIPPED\n已发货": (990, 230, 1210, 330),
        "RECEIVED\n已收货": (1380, 230, 1600, 330),
        "CANCELLED\n已取消": (600, 570, 820, 670),
    }
    for text, xy in states.items():
        text_box(draw, xy, text, fill="#ffffff", outline="#334155", font_size=24, bold=True)
    text_box(draw, (70, 230, 160, 330), "开始", fill="#e0f2fe", outline="#0284c7", radius=45, font_size=20)
    text_box(draw, (1380, 570, 1530, 670), "结束", fill="#e0f2fe", outline="#0284c7", radius=45, font_size=20)
    route(draw, [(160, 280), (210, 280)])
    route(draw, [(430, 280), (600, 280)])
    draw.text((480, 245), "模拟支付", font=font(18), fill="#475569")
    route(draw, [(820, 280), (990, 280)])
    draw.text((870, 245), "后台发货", font=font(18), fill="#475569")
    route(draw, [(1210, 280), (1380, 280)])
    draw.text((1250, 245), "确认收货", font=font(18), fill="#475569")
    route(draw, [(320, 330), (320, 620), (600, 620)], fill="#dc2626")
    draw.text((345, 505), "用户取消", font=font(18), fill="#dc2626")
    route(draw, [(710, 330), (710, 570)], fill="#dc2626")
    draw.text((730, 450), "后台取消", font=font(18), fill="#dc2626")
    route(draw, [(820, 620), (1380, 620)])
    route(draw, [(1490, 330), (1490, 570)])
    img.save(path)
    return path


def diagram_deployment_clean() -> Path:
    img, draw, path = save_canvas("07-component-deployment.png", (2100, 1120))
    label(draw, (70, 45), "组件/部署图：本地演示环境")
    tiers = [
        ("客户端层", (70, 160, 470, 940), [("浏览器\nVue3 SPA\nlocalhost:5173", (130, 390, 410, 530))]),
        ("服务层", (650, 160, 1120, 940), [("Spring Boot\nREST API\nlocalhost:8080", (735, 360, 1035, 540)), ("静态/脚本\n截图与文档生成", (735, 650, 1035, 790))]),
        ("基础设施层", (1300, 160, 2030, 940), [
            ("MySQL 8\n业务数据", (1370, 240, 1630, 360)),
            ("Redis\n促销库存", (1690, 240, 1950, 360)),
            ("阿里云 OSS\n商品图片", (1370, 600, 1630, 720)),
            ("OpenAI 兼容 API\nAI 服务", (1690, 600, 1950, 720)),
        ]),
    ]
    for title, frame, nodes in tiers:
        draw.rounded_rectangle(frame, radius=16, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 25, frame[1] + 25), title, font=font(26, True), fill="#0f172a")
        for text, xy in nodes:
            text_box(draw, xy, text, fill="#f8fafc", outline="#334155", font_size=22, bold=True)
    route(draw, [(410, 460), (735, 460)])
    draw.text((505, 420), "HTTP / REST / JWT", font=font(20), fill="#475569")
    routes = [
        [(1035, 410), (1210, 410), (1210, 300), (1370, 300)],
        [(1035, 460), (1235, 460), (1235, 300), (1690, 300)],
        [(1035, 510), (1210, 510), (1210, 660), (1370, 660)],
        [(1035, 560), (1235, 560), (1235, 660), (1690, 660)],
    ]
    for pts in routes:
        route(draw, pts, width=2)
    img.save(path)
    return path


def diagram_er() -> Path:
    img, draw, path = save_canvas("08-er.png", (2100, 1250))
    label(draw, (70, 45), "数据库 ER 图：核心表关系")
    tables = {
        "sys_user": (90, 180, 350, 290),
        "sys_role": (90, 430, 350, 540),
        "product_category": (620, 180, 920, 290),
        "product": (620, 430, 920, 540),
        "cart_item": (1110, 300, 1390, 410),
        "order_main": (1110, 560, 1390, 670),
        "order_item": (1600, 560, 1880, 670),
        "payment_record": (1110, 820, 1390, 930),
        "promotion_activity": (620, 740, 920, 850),
        "promotion_product": (620, 980, 920, 1090),
        "inventory_record": (1110, 1040, 1390, 1150),
        "ai_chat_record": (1600, 180, 1880, 290),
    }
    for name, xy in tables.items():
        text_box(draw, xy, name, fill="#ffffff", outline="#334155", font_size=22, bold=True)
    def c(name): 
        x1,y1,x2,y2=tables[name]; return ((x1+x2)//2,(y1+y2)//2)
    pairs = [
        ("sys_user","sys_role"), ("product_category","product"), ("sys_user","cart_item"),
        ("product","cart_item"), ("sys_user","order_main"), ("order_main","order_item"),
        ("product","order_item"), ("order_main","payment_record"), ("promotion_activity","promotion_product"),
        ("product","promotion_product"), ("product","inventory_record"), ("sys_user","ai_chat_record")
    ]
    for a,b in pairs:
        ax, ay = c(a); bx, by = c(b)
        route(draw, [(ax, ay), ((ax+bx)//2, ay), ((ax+bx)//2, by), (bx, by)], width=2)
    img.save(path)
    return path


def diagram_api_layers() -> Path:
    img, draw, path = save_canvas("09-api-layers.png", (1900, 1050))
    label(draw, (70, 45), "接口分层图：前端 API 到后端业务模块")
    layers = [
        ("Vue 页面层", ["首页/详情", "购物车/订单", "后台管理", "AI 页面"], 150),
        ("API 封装层", ["auth.ts", "products.ts", "cart.ts/orders.ts", "admin.ts/ai.ts"], 430),
        ("Controller 层", ["AuthController", "ProductController", "OrderController", "Admin*/AiController"], 710),
        ("Service 层", ["AuthService", "ProductService", "OrderService", "Promotion/Ai Service"], 990),
        ("持久化/外部服务", ["Mapper/MySQL", "Redis", "OSS", "LLM API"], 1270),
    ]
    for title, items, y in layers:
        draw.rounded_rectangle((130, y, 1770, y + 150), radius=16, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((165, y + 22), title, font=font(24, True), fill="#0f172a")
        for i, item in enumerate(items):
            x = 430 + i * 315
            text_box(draw, (x, y + 45, x + 250, y + 120), item, fill="#f8fafc", outline="#334155", font_size=19)
    for y in [300, 580, 860, 1140]:
        pass
    for y1, y2 in [(300, 430), (580, 710), (860, 990), (1140, 1270)]:
        route(draw, [(950, y1), (950, y2)], width=3)
    img.save(path)
    return path


def diagram_auth_flow() -> Path:
    img, draw, path = save_canvas("10-auth-flow.png", (1700, 1000))
    label(draw, (70, 45), "权限鉴权流程图：JWT 与角色控制")
    steps = [
        ("用户提交账号密码", (120, 210, 400, 300)),
        ("AuthController 校验", (540, 210, 820, 300)),
        ("签发 JWT", (960, 210, 1240, 300)),
        ("前端保存 token", (1380, 210, 1600, 300)),
        ("请求携带 Authorization", (120, 560, 400, 650)),
        ("JwtAuthenticationFilter 解析", (540, 560, 860, 650)),
        ("SecurityConfig 匹配权限", (1000, 560, 1300, 650)),
        ("允许访问或返回 401/403", (1420, 560, 1620, 650)),
    ]
    for text, xy in steps:
        text_box(draw, xy, text, fill="#f8fafc", outline="#334155", font_size=21)
    for i in range(3):
        route(draw, [((steps[i][1][2]), 255), ((steps[i+1][1][0]), 255)], width=2)
    for i in range(4, 7):
        route(draw, [((steps[i][1][2]), 605), ((steps[i+1][1][0]), 605)], width=2)
    route(draw, [(1490, 300), (1490, 420), (260, 420), (260, 560)], width=2)
    img.save(path)
    return path


def diagram_promotion_flow() -> Path:
    img, draw, path = save_canvas("11-promotion-flow.png", (1800, 1050))
    label(draw, (70, 45), "抢购库存流程图：Redis 预扣与数据库落单")
    lanes = [("用户/前端", 80, 420), ("后端服务", 520, 960), ("Redis", 1060, 1320), ("MySQL", 1420, 1720)]
    for title, x1, x2 in lanes:
        draw.rounded_rectangle((x1, 150, x2, 900), radius=14, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((x1 + 20, 175), title, font=font(24, True), fill="#0f172a")
    nodes = [
        ("点击立即抢购", (135, 300, 365, 380)),
        ("提交收货信息", (135, 520, 365, 600)),
        ("校验活动/限购", (620, 300, 860, 380)),
        ("Redis 扣减库存", (1100, 300, 1280, 380)),
        ("创建订单/明细", (1470, 300, 1670, 380)),
        ("失败回滚 Redis", (620, 650, 860, 730)),
        ("返回订单详情", (620, 520, 860, 600)),
    ]
    centers = {}
    for text, xy in nodes:
        fill = "#fee2e2" if "失败" in text else "#f8fafc"
        outline = "#dc2626" if "失败" in text else "#334155"
        text_box(draw, xy, text, fill=fill, outline=outline, font_size=20)
        centers[text] = ((xy[0]+xy[2])//2, (xy[1]+xy[3])//2)
    for a,b in [("点击立即抢购","校验活动/限购"),("校验活动/限购","Redis 扣减库存"),("Redis 扣减库存","创建订单/明细"),("创建订单/明细","返回订单详情"),("返回订单详情","提交收货信息")]:
        ax,ay=centers[a]; bx,by=centers[b]
        route(draw, [(ax,ay),((ax+bx)//2,ay),((ax+bx)//2,by),(bx,by)], width=2)
    route(draw, [centers["Redis 扣减库存"], (1190, 690), centers["失败回滚 Redis"]], fill="#dc2626", width=2)
    img.save(path)
    return path


def generate_diagrams() -> list[Path]:
    return [
        diagram_use_case_clean(),
        diagram_class_clean(),
        diagram_package_clean(),
        diagram_activity_clean(),
        diagram_sequence_clean(),
        diagram_state_clean(),
        diagram_deployment_clean(),
        diagram_er(),
        diagram_api_layers(),
        diagram_auth_flow(),
        diagram_promotion_flow(),
    ]


SCREENSHOT_ITEMS = [
    ("login.png", "登录页：展示默认账号提示和用户名、密码输入。"),
    ("register.png", "注册页：展示普通用户注册所需字段。"),
    ("store-home-guest.png", "游客首页：展示未登录状态、商品首页、分类与 AI 导购入口。"),
    ("store-home-user.png", "登录用户首页：展示当前用户、角色和购物入口。"),
    ("store-search-filter.png", "商品筛选：展示搜索关键词、分类、库存和视图切换后的结果。"),
    ("promotion-expanded.png", "限时抢购展开：展示活动商品、活动价、库存和限购信息。"),
    ("promotion-checkout-dialog.png", "抢购确认弹窗：展示活动商品、购买数量与收货信息表单。"),
    ("ai-guide-dialog.png", "AI 导购弹窗：展示用户需求输入和 AI 建议区域。"),
    ("product-detail.png", "商品详情：展示商品图片、价格、库存、详情和购物按钮。"),
    ("product-qa.png", "商品 AI 问答：展示商品问答输入区域和 AI 回答区域。"),
    ("cart.png", "购物车：展示购物车商品、数量调整、选择结算和金额汇总。"),
    ("checkout-dialog.png", "购物车结算弹窗：展示收货人、电话、地址和订单提交。"),
    ("orders.png", "订单列表：展示订单状态筛选、订单摘要和操作按钮。"),
    ("order-detail.png", "订单详情：展示订单号、状态、收货信息、金额和明细。"),
    ("admin-dashboard.png", "后台销售看板：展示核心指标和库存预警表。"),
    ("admin-products.png", "后台商品管理：展示商品查询、商品表格和上下架操作。"),
    ("admin-product-dialog.png", "商品编辑弹窗：展示商品基础信息、图片上传和详情字段。"),
    ("admin-category-dialog.png", "分类新增弹窗：展示分类名称、排序和状态字段。"),
    ("admin-orders.png", "后台订单管理：展示订单筛选、状态和处理操作。"),
    ("admin-order-drawer.png", "订单详情抽屉：展示后台订单明细、收货信息和商品行。"),
    ("admin-promotions.png", "后台促销管理：展示活动列表、状态和编辑入口。"),
    ("admin-promotion-dialog.png", "促销活动弹窗：展示活动时间、状态和活动商品配置。"),
    ("admin-ai-operation.png", "AI 运营助手：展示商品文案生成和运营分析表单。"),
    ("admin-users.png", "用户管理：展示用户、角色多选、状态开关和分页。"),
]


def diagram_class_clean() -> Path:
    img, draw, path = save_canvas("02-domain-class.png", (2200, 1500))
    label(draw, (70, 45), "领域类图：核心业务对象及关系")
    groups = [
        ("用户与权限", (80, 140, 610, 470), [
            ("SysUser\n- id\n- username\n- password\n- nickname\n- status", (120, 220, 350, 390)),
            ("SysRole\n- id\n- code\n- name", (390, 220, 570, 390)),
        ]),
        ("商品与促销", (690, 140, 1470, 470), [
            ("ProductCategory\n- id\n- parentId\n- name\n- sort", (730, 220, 960, 390)),
            ("Product\n- id\n- categoryId\n- name\n- price\n- stock", (1000, 220, 1230, 390)),
            ("PromotionProduct\n- activityId\n- productId\n- promotionStock", (1270, 220, 1430, 390)),
        ]),
        ("交易链路", (80, 540, 1060, 880), [
            ("CartItem\n- userId\n- productId\n- quantity", (120, 625, 330, 795)),
            ("OrderMain\n- orderNo\n- userId\n- totalAmount\n- status", (380, 625, 610, 795)),
            ("OrderItem\n- orderId\n- productId\n- price\n- quantity", (660, 625, 880, 795)),
        ]),
        ("支付、库存与 AI", (1140, 540, 2100, 880), [
            ("PaymentRecord\n- orderId\n- amount\n- status", (1180, 625, 1410, 795)),
            ("InventoryRecord\n- productId\n- changeQuantity\n- businessType", (1460, 625, 1700, 795)),
            ("AiChatRecord\n- userId\n- scene\n- prompt\n- response", (1750, 625, 2060, 795)),
        ]),
    ]
    for title, frame, items in groups:
        draw.rounded_rectangle(frame, radius=18, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 24, frame[1] + 22), title, font=font(26, True), fill="#0f172a")
        for text, xy in items:
            wrapped_text_box(draw, xy, text, fill="#f8fafc", outline="#334155", font_size=20, bold=False)

    # Superseded below by the edge-anchor class diagram implementation.
    img.save(path)
    return path


def diagram_activity_clean() -> Path:
    img, draw, path = save_canvas("04-order-activity.png", (1850, 1400))
    label(draw, (70, 45), "活动图：购物车下单流程")
    lane_defs = [("用户", 80, 430), ("前端", 430, 780), ("后端服务", 780, 1230), ("数据库", 1230, 1770)]
    for title, x1, x2 in lane_defs:
        draw.rounded_rectangle((x1, 130, x2, 1160), radius=12, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((x1 + 20, 155), title, font=font(24, True), fill="#0f172a")

    nodes = [
        ("选择商品\n点击结算", (145, 260, 365, 350)),
        ("填写收货信息", (500, 260, 710, 350)),
        ("提交订单请求", (500, 430, 710, 520)),
        ("校验登录态\n购物车项", (890, 430, 1120, 520)),
        ("校验商品状态\n与库存", (890, 600, 1120, 690)),
        ("写入订单主表\n与订单明细", (1380, 600, 1630, 690)),
        ("扣减库存\n写入流水", (1380, 790, 1630, 880)),
        ("返回订单 ID", (890, 970, 1120, 1060)),
        ("跳转订单详情", (500, 970, 710, 1060)),
    ]
    centers = []
    for text, xy in nodes:
        wrapped_text_box(draw, xy, text, fill="#f8fafc", outline="#334155", font_size=20)
        centers.append(((xy[0] + xy[2]) // 2, (xy[1] + xy[3]) // 2))
    flow_pairs = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
    for a_idx, b_idx in flow_pairs:
        a, b = centers[a_idx], centers[b_idx]
        if a[1] == b[1]:
            route(draw, [a, b], width=2)
        else:
            route(draw, [a, (a[0], b[1]), b], width=2)

    draw.rounded_rectangle((80, 1210, 1770, 1340), radius=12, fill="#fff1f2", outline="#dc2626", width=2)
    draw.text((110, 1230), "异常分支（独立区域，不回穿主流程）：未登录、购物车为空、商品下架、库存不足、数据库写入失败时返回错误提示；若已扣减库存则执行补偿回滚。", font=font(22), fill="#991b1b")
    img.save(path)
    return path


def diagram_deployment_clean() -> Path:
    img, draw, path = save_canvas("07-component-deployment.png", (2200, 1180))
    label(draw, (70, 45), "组件/部署图：本地演示环境")
    frames = [
        ("客户端层", (90, 180, 540, 940)),
        ("服务端层", (700, 180, 1250, 940)),
        ("基础设施层", (1460, 180, 2110, 940)),
    ]
    for title, frame in frames:
        draw.rounded_rectangle(frame, radius=16, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 24, frame[1] + 24), title, font=font(27, True), fill="#0f172a")
    wrapped_text_box(draw, (160, 420, 470, 570), "浏览器\nVue3 SPA\nlocalhost:5173", fill="#dcfce7", outline="#16a34a", font_size=23, bold=True)
    wrapped_text_box(draw, (790, 320, 1160, 500), "Spring Boot\nREST API\nlocalhost:8080", fill="#e0f2fe", outline="#0284c7", font_size=24, bold=True)
    wrapped_text_box(draw, (790, 640, 1160, 790), "文档/截图脚本\nPython + Playwright", fill="#f8fafc", outline="#334155", font_size=22)
    infra_nodes = [
        ("MySQL 8\n业务数据", (1530, 260, 1760, 380)),
        ("Redis\n促销库存", (1830, 260, 2040, 380)),
        ("阿里云 OSS\n商品图片", (1530, 650, 1760, 770)),
        ("OpenAI 兼容 API\nAI 服务", (1830, 650, 2040, 770)),
    ]
    for text, xy in infra_nodes:
        wrapped_text_box(draw, xy, text, fill="#f8fafc", outline="#334155", font_size=21, bold=True)

    # External buses: no line crosses through component rectangles.
    client_bus = [(470, 495), (610, 495), (610, 1040), (1370, 1040), (1370, 410), (790, 410)]
    route(draw, client_bus, width=3)
    draw.text((570, 1000), "HTTP / REST / JWT", font=font(20), fill="#475569")
    infra_bus_x = 1370
    draw.line([(1250, 410), (infra_bus_x, 410), (infra_bus_x, 980)], fill="#475569", width=3)
    for y in [320, 710]:
        route(draw, [(infra_bus_x, y), (1530, y)], width=2)
        route(draw, [(infra_bus_x, y), (1830, y)], width=2)
    draw.text((1290, 945), "JDBC / Redis / OSS SDK / HTTPS", font=font(20), fill="#475569")
    img.save(path)
    return path


def diagram_er() -> Path:
    img, draw, path = save_canvas("08-er.png", (2200, 1450))
    label(draw, (70, 45), "数据库 ER 图：核心表分组与外键关系")
    groups = [
        ("用户权限", (80, 150, 520, 440), ["sys_user", "sys_role", "sys_user_role"]),
        ("商品", (580, 150, 1020, 440), ["product_category", "product", "product_image"]),
        ("交易", (80, 520, 720, 860), ["cart_item", "order_main", "order_item", "payment_record"]),
        ("促销与库存", (780, 520, 1320, 860), ["promotion_activity", "promotion_product", "inventory_record"]),
        ("AI 与日志", (1380, 520, 1800, 860), ["ai_chat_record", "operation_log"]),
    ]
    for title, frame, tables in groups:
        draw.rounded_rectangle(frame, radius=16, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 22, frame[1] + 20), title, font=font(24, True), fill="#0f172a")
        y = frame[1] + 75
        for table_name in tables:
            wrapped_text_box(draw, (frame[0] + 35, y, frame[2] - 35, y + 62), table_name, fill="#f8fafc", outline="#334155", font_size=20, bold=True)
            y += 78
    # Superseded below by the edge-anchor ER diagram implementation.
    img.save(path)
    return path


def diagram_api_layers() -> Path:
    img, draw, path = save_canvas("09-api-layers.png", (2000, 1500))
    label(draw, (70, 45), "接口分层图：前端 API 到后端业务模块")
    layers = [
        ("Vue 页面层", ["首页/详情", "购物车/订单", "后台管理", "AI 页面"], 150),
        ("API 封装层", ["auth.ts", "products.ts", "cart.ts / orders.ts", "admin.ts / ai.ts"], 390),
        ("Controller 层", ["AuthController", "ProductController", "OrderController", "Admin* / AiController"], 630),
        ("Service 层", ["AuthService", "ProductService", "OrderService", "PromotionService / AiService"], 870),
        ("持久化/外部服务", ["Mapper / MySQL", "Redis", "OSS", "LLM API"], 1110),
    ]
    for title, items, y in layers:
        draw.rounded_rectangle((120, y, 1880, y + 170), radius=16, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((155, y + 24), title, font=font(24, True), fill="#0f172a")
        for i, item in enumerate(items):
            x = 420 + i * 350
            wrapped_text_box(draw, (x, y + 55, x + 280, y + 132), item, fill="#f8fafc", outline="#334155", font_size=18)
    for y1, y2 in [(320, 390), (560, 630), (800, 870), (1040, 1110)]:
        route(draw, [(1000, y1), (1000, y2)], width=3)
    draw.rounded_rectangle((120, 1320, 1880, 1420), radius=12, fill="#f8fafc", outline="#cbd5e1", width=2)
    draw.text((155, 1350), "说明：页面层只处理交互；API 封装层统一 Axios 调用；Controller 负责 HTTP 入参；Service 承载业务规则；Mapper/外部服务负责数据与第三方能力。", font=font(21), fill="#334155")
    img.save(path)
    return path


def diagram_auth_flow() -> Path:
    img, draw, path = save_canvas("10-auth-flow.png", (1900, 1050))
    label(draw, (70, 45), "权限鉴权流程图：JWT 与角色控制")
    rows = [
        [("用户提交\n账号密码", (110, 220, 370, 330)), ("AuthController\n校验账号密码", (510, 220, 810, 330)), ("签发 JWT\n返回用户角色", (950, 220, 1240, 330)), ("前端保存\nToken", (1380, 220, 1660, 330))],
        [("请求携带\nAuthorization", (110, 620, 370, 730)), ("JwtAuthentication\nFilter 解析", (510, 620, 810, 730)), ("SecurityConfig\n匹配权限", (950, 620, 1240, 730)), ("允许访问\n或 401/403", (1380, 620, 1660, 730))],
    ]
    for row in rows:
        for text, xy in row:
            wrapped_text_box(draw, xy, text, fill="#f8fafc", outline="#334155", font_size=21, bold=True)
        for i in range(len(row) - 1):
            route(draw, [((row[i][1][2]), (row[i][1][1] + row[i][1][3]) // 2), (row[i + 1][1][0], (row[i + 1][1][1] + row[i + 1][1][3]) // 2)], width=2)
    route(draw, [(1520, 330), (1520, 470), (240, 470), (240, 620)], width=2)
    draw.rounded_rectangle((110, 820, 1660, 940), radius=12, fill="#f8fafc", outline="#cbd5e1", width=2)
    draw.text((145, 855), "角色规则：前台订单与购物车要求登录；后台商品、订单、促销、AI 运营要求 OPERATOR 或 ADMIN；用户角色管理仅 ADMIN 可操作。", font=font(22), fill="#334155")
    img.save(path)
    return path


def diagram_promotion_flow() -> Path:
    img, draw, path = save_canvas("11-promotion-flow.png", (1900, 1250))
    label(draw, (70, 45), "抢购库存流程图：Redis 预扣与数据库落单")
    lanes = [("用户/前端", 90, 430), ("后端服务", 430, 850), ("Redis", 850, 1210), ("MySQL", 1210, 1770)]
    for title, x1, x2 in lanes:
        draw.rounded_rectangle((x1, 140, x2, 960), radius=14, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((x1 + 20, 165), title, font=font(24, True), fill="#0f172a")
    nodes = [
        ("点击立即抢购", (145, 280, 375, 360)),
        ("提交数量\n与收货信息", (145, 520, 375, 610)),
        ("校验活动\n时间/限购", (525, 280, 755, 370)),
        ("预扣活动库存", (925, 280, 1135, 370)),
        ("创建订单\n和订单明细", (1320, 280, 1600, 370)),
        ("返回订单详情", (525, 520, 755, 610)),
        ("失败补偿\n回滚 Redis", (925, 780, 1135, 870)),
    ]
    centers = {}
    for text, xy in nodes:
        fill = "#fff1f2" if "失败" in text else "#f8fafc"
        outline = "#dc2626" if "失败" in text else "#334155"
        wrapped_text_box(draw, xy, text, fill=fill, outline=outline, font_size=20, bold=True)
        centers[text] = ((xy[0] + xy[2]) // 2, (xy[1] + xy[3]) // 2)
    main = ["点击立即抢购", "校验活动\n时间/限购", "预扣活动库存", "创建订单\n和订单明细", "返回订单详情", "提交数量\n与收货信息"]
    for a, b in zip(main, main[1:]):
        ax, ay = centers[a]
        bx, by = centers[b]
        if ay == by:
            route(draw, [(ax, ay), (bx, by)], width=2)
        else:
            route(draw, [(ax, ay), (ax, by), (bx, by)], width=2)
    # Failure lane uses bottom channel only.
    route(draw, [centers["创建订单\n和订单明细"], (1460, 1030), (1030, 1030), centers["失败补偿\n回滚 Redis"]], fill="#dc2626", width=2)
    draw.text((1140, 1000), "数据库落单失败/校验失败", font=font(18), fill="#dc2626")
    img.save(path)
    return path


def create_requirements_doc(diagrams: dict[str, Path]) -> None:
    doc = Document()
    set_doc_style(doc)
    add_title_page(doc, "系统需求文档", "XShop B2C AI 电商系统")
    add_toc_note(doc)

    heading(doc, "一、项目可行性分析与领域描述")
    heading(doc, "1.1 领域边界", 2)
    paragraph(doc, "XShop 面向 B2C 在线零售场景，覆盖商品展示、搜索筛选、购物车、下单、模拟支付、订单状态跟踪、后台商品运营、订单处理、促销活动和 AI 辅助服务。系统边界限定在课程项目可本地演示的交易闭环与运营后台，不包含真实支付清算、真实物流履约、多商户分账、供应链采购和财务结算。")
    heading(doc, "1.2 用户画像与业务痛点", 2)
    add_table(doc, ["用户", "典型场景", "痛点", "系统能力"], [
        ["普通用户", "浏览商品、按场景选择商品、加入购物车并下单", "商品信息筛选成本高，购买链路需要清晰稳定", "搜索筛选、详情页、购物车、订单中心、AI 导购"],
        ["运营管理员", "维护商品、设置促销、处理订单、生成文案", "重复录入多，促销库存和订单状态需要统一管理", "后台商品/订单/促销管理、AI 文案和运营分析"],
        ["系统管理员", "管理后台账号权限", "需要限制普通用户访问后台并控制角色能力", "用户管理、角色调整、JWT 鉴权和路由拦截"],
    ])
    heading(doc, "1.3 竞品分析", 2)
    add_table(doc, ["系统", "优势", "不足", "本项目取舍"], [
        ["京东/淘宝/拼多多", "支付、物流、商家、推荐和客服体系完整", "系统复杂度远超课程项目", "保留核心交易链路，去掉真实商业履约"],
        ["传统电商后台", "商品、库存和订单管理成熟", "AI 辅助能力通常弱或需单独采购", "加入 AI 导购、AI 问答、AI 文案和运营分析"],
        ["AI 导购工具", "自然语言交互友好", "与真实商品库存和订单协同不足", "把 AI 服务接入商品库和后台运营流程"],
    ])

    heading(doc, "二、系统功能分析")
    heading(doc, "2.1 完整功能树与优先级", 2)
    add_table(doc, ["一级功能", "二级功能", "权重", "优先级", "依赖"], [
        ["认证与权限", "注册、登录、JWT、角色鉴权、前端路由守卫", "10", "高", "独立基础能力"],
        ["商品中心", "分类、商品列表、搜索、详情、上下架、图片上传", "15", "高", "后台依赖权限"],
        ["购物车", "加入、数量修改、删除、勾选、结算", "10", "高", "依赖登录和商品"],
        ["订单中心", "创建订单、支付、取消、收货、订单详情", "20", "最高", "依赖购物车、商品、库存"],
        ["促销秒杀", "活动配置、活动商品、限购、Redis 库存预扣", "10", "中高", "依赖商品、订单、Redis"],
        ["AI 服务", "导购、商品问答、商品文案、运营分析、记录保存", "15", "高", "依赖商品数据和模型接口"],
        ["后台管理", "商品、分类、订单、促销、用户、角色", "10", "高", "依赖鉴权"],
        ["数据看板", "销售额、订单数、支付订单、低库存预警", "10", "中", "依赖订单和商品数据"],
    ])
    heading(doc, "2.2 用例与权限", 2)
    add_image(doc, diagrams["use_case"], "图 1 UML 用例图：采用分区式布局展示三类用户和系统用例，连线按角色专用通道进入功能分区。")
    add_table(doc, ["功能", "游客", "普通用户", "运营管理员", "系统管理员"], [
        ["浏览商品/搜索/详情", "允许", "允许", "允许", "允许"],
        ["购物车/下单/支付/收货", "禁止", "允许", "允许", "允许"],
        ["AI 导购/商品问答", "部分允许", "允许", "允许", "允许"],
        ["后台商品/订单/促销/AI 运营", "禁止", "禁止", "允许", "允许"],
        ["用户角色管理", "禁止", "禁止", "禁止", "允许"],
    ])
    heading(doc, "2.3 客户端与服务端职责矩阵", 2)
    add_table(doc, ["模块", "Client 端职责", "Server 端职责", "数据/外部依赖"], [
        ["认证", "登录注册表单、token 保存、路由守卫", "密码校验、JWT 签发、当前用户解析", "sys_user、sys_role"],
        ["商品", "首页、筛选、详情、后台表单", "商品查询、分类管理、上下架、图片 URL 保存", "product、product_category、OSS"],
        ["购物车/订单", "购物车交互、收货信息、订单状态操作", "事务创建订单、库存扣减、支付和状态流转", "cart_item、order_main、inventory_record"],
        ["促销", "活动展示、抢购弹窗", "活动校验、Redis 库存预扣、抢购订单创建", "promotion_*、Redis"],
        ["AI", "导购/问答/运营表单和结果展示", "Prompt 组装、模型调用、失败降级、记录保存", "ai_chat_record、LLM API"],
    ])
    heading(doc, "2.4 非功能需求", 2)
    add_table(doc, ["类别", "需求"], [
        ["可运行性", "前后端可本地启动，数据库脚本可初始化演示数据，默认账号可登录。"],
        ["安全性", "后台接口必须登录且具备角色权限，普通用户不能访问管理端。"],
        ["一致性", "订单创建、库存扣减和库存流水应保持事务一致；取消订单应回滚库存。"],
        ["可演示性", "AI 服务在缺少 API Key 或调用失败时提供降级结果，保证课堂演示不中断。"],
        ["可维护性", "按业务包划分后端模块，前端 API 封装与页面视图分离。"],
    ])
    heading(doc, "2.5 原型与运行截图", 2)
    for filename, caption in SCREENSHOT_ITEMS:
        add_image(doc, SCREENSHOT_DIR / filename, caption, width=6.2)
    heading(doc, "2.6 开发计划与验收标准", 2)
    add_table(doc, ["阶段", "工作", "验收产物"], [
        ["需求与设计", "梳理领域边界、功能树、UML、数据库和接口", "需求文档、设计文档、图表"],
        ["核心开发", "实现认证、商品、购物车、订单、库存和后台管理", "可运行前后端和数据库脚本"],
        ["智能化扩展", "实现 AI 导购、问答、文案和运营分析", "AI 接口、页面和记录表"],
        ["促销与测试", "实现限时抢购、Redis 库存和集成测试", "抢购流程、测试报告"],
        ["文档与提交", "生成截图、设计图和三份 Word 文档", "final 文档目录"],
    ])

    heading(doc, "三、领域模型与动态特性")
    add_image(doc, diagrams["class"], "图 2 领域类图：按业务分区展示用户权限、商品促销、交易链路和 AI 记录。")
    add_image(doc, diagrams["package"], "图 3 包图：展示前端、后端模块和外部基础设施边界。")
    add_image(doc, diagrams["er"], "图 4 数据库 ER 图：展示核心表关系和主要业务外键关系。")
    add_image(doc, diagrams["activity"], "图 5 下单活动图：泳道展示用户、前端、后端和数据库协作。")
    add_image(doc, diagrams["sequence"], "图 6 AI 导购顺序图：展示商品上下文查询、模型调用和结果返回。")
    add_image(doc, diagrams["state"], "图 7 订单状态机图：展示创建、支付、发货、收货和取消状态。")
    add_image(doc, diagrams["promotion"], "图 8 抢购库存流程图：展示 Redis 预扣、数据库落单和失败回滚。")

    save_doc(doc, "系统需求文档.docx")


def create_design_doc(diagrams: dict[str, Path]) -> None:
    doc = Document()
    set_doc_style(doc)
    add_title_page(doc, "系统设计文档", "XShop B2C AI 电商系统")
    add_toc_note(doc)

    heading(doc, "一、技术选型与对比")
    add_table(doc, ["层次", "可选方案", "最终选型", "选择理由"], [
        ["后端框架", "Spring Boot / Node.js / .NET", "Spring Boot 2.7.18", "Java 8 环境兼容，生态成熟，适合 REST 和事务型业务。"],
        ["前端框架", "Vue / React / Angular", "Vue3 + TypeScript + Vite", "开发效率高，组合式 API 适合中小型前后端分离项目。"],
        ["数据库", "MySQL / PostgreSQL / MongoDB", "MySQL 8", "订单、商品、用户关系清晰，适合关系型建模和事务。"],
        ["缓存", "Redis / 本地缓存", "Redis", "适合抢购库存预扣和短时高并发库存保护。"],
        ["安全", "Session / JWT", "JWT + Spring Security", "前后端分离，便于无状态接口鉴权和角色控制。"],
        ["AI", "固定供应商 / OpenAI 兼容协议", "OpenAI 兼容 API", "便于切换 DeepSeek、通义千问、OpenAI 等兼容模型。"],
    ])

    heading(doc, "二、系统架构设计")
    paragraph(doc, "系统采用前后端分离架构。客户端由 Vue3 单页应用承载商城前台和后台管理端；服务端为 Spring Boot 模块化单体，按业务边界拆分包；MySQL 保存业务数据，Redis 支撑促销库存，OSS 保存商品图片，OpenAI 兼容 API 提供智能服务。")
    add_image(doc, diagrams["deployment"], "图 1 组件/部署图：分层展示客户端、服务端和基础设施，连线按层间通道绘制。")
    add_image(doc, diagrams["package"], "图 2 包图：后端模块化单体结构。")
    add_image(doc, diagrams["api"], "图 3 接口分层图：从 Vue 页面、API 封装、Controller、Service 到持久化/外部服务。")
    heading(doc, "2.1 后端模块职责", 2)
    add_table(doc, ["模块", "职责", "主要接口/对象"], [
        ["auth", "注册、登录、JWT 签发、当前用户资料", "AuthController、AuthService"],
        ["user", "用户分页、状态启停、角色调整", "AdminUserController、SysUser、SysRole"],
        ["product", "分类、商品、上下架、商品查询", "ProductController、AdminProductController"],
        ["cart", "购物车增删改查", "CartController、CartService"],
        ["order", "订单创建、支付、取消、收货、后台发货", "OrderController、AdminOrderController"],
        ["inventory", "库存扣减、库存回滚、库存流水", "InventoryRecord"],
        ["promotion", "限时活动、活动商品、抢购下单", "PromotionController、AdminPromotionController"],
        ["ai", "AI 导购、商品问答、文案、运营分析", "AiController、AiService、AiChatRecord"],
        ["upload", "商品主图上传到 OSS", "AdminUploadController、OssUploadService"],
        ["common/security/config", "统一响应、异常、分页、安全和 MyBatis 配置", "ApiResponse、SecurityConfig、JwtAuthenticationFilter"],
    ])
    heading(doc, "2.2 数据库设计概要", 2)
    add_image(doc, diagrams["er"], "图 4 ER 图：核心表关系。")
    add_table(doc, ["表", "关键字段", "说明"], [
        ["sys_user", "id、username、password、nickname、status", "用户账号和状态"],
        ["sys_role / sys_user_role", "code、name、user_id、role_id", "角色和多对多关联"],
        ["product_category / product", "category_id、name、price、stock、status", "商品分类和商品主数据"],
        ["cart_item", "user_id、product_id、quantity、selected", "用户购物车"],
        ["order_main / order_item", "order_no、status、total_amount、product_id、quantity", "订单主表和明细"],
        ["payment_record", "payment_no、amount、status、paid_at", "模拟支付记录"],
        ["inventory_record", "change_quantity、before_stock、after_stock、business_type", "库存流水"],
        ["promotion_activity / promotion_product", "start_time、end_time、promotion_price、promotion_stock", "限时抢购活动"],
        ["ai_chat_record", "scene、prompt、response、model", "AI 交互记录"],
    ])

    heading(doc, "三、接口与数据格式")
    paragraph(doc, "后端接口统一返回 ApiResponse，成功时 code 为 0，message 为 success，data 为业务数据；分页数据使用 PageResult，包含 records、total、page、size。")
    add_table(doc, ["模块", "核心接口"], [
        ["认证", "POST /api/auth/register；POST /api/auth/login；GET /api/auth/profile"],
        ["商品/分类", "GET /api/categories；GET /api/products；GET /api/products/{id}；/api/admin/products；/api/admin/categories"],
        ["购物车", "GET/POST /api/cart/items；PUT/DELETE /api/cart/items/{id}"],
        ["订单", "POST /api/orders；GET /api/orders；GET /api/orders/{id}；POST /pay|cancel|receive"],
        ["后台订单", "GET /api/admin/orders；GET /api/admin/orders/{id}；PUT /ship；PUT /cancel"],
        ["促销", "GET /api/promotions/active；GET /api/promotions/{id}；POST /api/promotions/{id}/orders；/api/admin/promotions"],
        ["AI", "POST /api/ai/shopping-guide；/product-qa；/product-copywriting；/operation-analysis"],
        ["上传", "POST /api/admin/uploads/product-images"],
        ["用户管理", "GET /api/admin/users；PUT /api/admin/users/{id}/status；PUT /api/admin/users/{id}/roles"],
    ])

    heading(doc, "四、关键技术解决方案")
    heading(doc, "4.1 JWT 鉴权与角色控制", 2)
    paragraph(doc, "登录成功后后端签发 JWT，前端保存 token 并在每次请求中通过 Authorization 头传递。JwtAuthenticationFilter 解析 token 后注入当前用户，SecurityConfig 根据接口路径和角色限制访问。前端路由守卫同步判断登录态和后台角色，避免普通用户进入管理页面。")
    add_image(doc, diagrams["auth"], "图 5 权限鉴权流程图：展示登录签发、请求携带、过滤器解析和角色判断。")
    heading(doc, "4.2 订单事务一致性", 2)
    paragraph(doc, "订单创建过程在数据库事务内完成：读取购物车、校验商品状态和库存、创建订单主表和明细、扣减库存、写入库存流水、删除或更新购物车。取消订单时按订单项恢复库存并追加库存流水，避免账面库存与订单状态不一致。")
    add_image(doc, diagrams["activity"], "图 6 订单事务活动图。")
    add_image(doc, diagrams["state"], "图 7 订单状态机图。")
    heading(doc, "4.3 Redis 抢购库存", 2)
    paragraph(doc, "限时抢购先在 Redis 中扣减活动库存，成功后再进入数据库订单创建流程。若数据库创建失败或校验失败，后端回滚 Redis 库存。该方案减少短时抢购请求直接冲击 MySQL 的概率，并保留数据库活动表作为最终业务记录。")
    add_image(doc, diagrams["promotion"], "图 8 Redis 抢购库存流程图。")
    heading(doc, "4.4 AI 服务与降级策略", 2)
    paragraph(doc, "AI 模块按场景构造 Prompt：导购会加入用户预算、偏好和候选商品；商品问答会加入商品名称、详情和库存；文案生成会加入商品卖点和目标用户；运营分析会加入时间范围和关注点。若 API Key 缺失、网络失败或模型返回异常，服务返回模板化结果，保证功能可演示。所有 AI 调用写入 ai_chat_record 便于追踪。")
    add_image(doc, diagrams["sequence"], "图 9 AI 导购顺序图。")
    heading(doc, "4.5 OSS 上传与图片访问", 2)
    paragraph(doc, "后台商品表单通过 Element Plus Upload 选择图片，前端使用 multipart/form-data 上传到后端。后端校验文件后调用阿里云 OSS SDK 保存对象，返回公网 URL，商品表只保存 URL，不保存二进制图片。")
    heading(doc, "4.6 日志定位、部署与演进", 2)
    add_table(doc, ["主题", "设计说明"], [
        ["日志定位", "浏览器 Network 定位请求，后端控制台查看异常，数据库/Redis 校验状态，统一异常处理返回错误信息。"],
        ["部署方式", "课程演示采用本地人工部署：MySQL、Redis、Spring Boot、Vite。后续可改为 Nginx + JAR + Docker Compose。"],
        ["环境变量", "DB_URL、DB_USERNAME、DB_PASSWORD、REDIS_HOST、AI_API_KEY、ALIYUN_OSS_* 等敏感项通过环境变量或本地 dev 配置提供。"],
        ["升级演进", "后续可引入消息队列异步抢购、Actuator 监控、集中日志、真实支付和物流模块。"],
    ])

    heading(doc, "五、运行与安装说明")
    add_numbered(doc, [
        "安装 JDK 1.8、Maven 3.8+、Node.js 20、MySQL 8、Redis。",
        "执行 backend/src/main/resources/schema.sql 创建数据库表。",
        "执行 backend/src/main/resources/data.sql 导入默认账号、商品和促销数据。",
        "在 backend 下执行 mvn spring-boot:run 启动后端，默认端口 8080。",
        "在 frontend 下执行 npm install 和 npm run dev 启动前端，默认端口 5173。",
        "访问 http://localhost:5173，使用 admin/admin123、operator/operator123、user/user123 演示不同角色。",
        "卸载时停止服务，删除 ai_commerce 数据库、frontend/node_modules 和构建产物即可。",
    ])
    heading(doc, "六、系统规模", 2)
    rows, total = count_lines()
    add_table(doc, ["范围", "文件数", "代码/文档行数"], rows + [["合计", "-", str(total)]])
    paragraph(doc, "统计口径为工程交付宽口径，包含 backend、frontend、docs、README 中的源码、配置、SQL、脚本、Markdown 和文档生成脚本，不包含 node_modules、dist、target、package-lock.json 等依赖或构建产物。")

    save_doc(doc, "系统设计文档.docx")


def create_management_doc() -> None:
    doc = Document()
    set_doc_style(doc)
    add_title_page(doc, "项目管理文档", "XShop B2C AI 电商系统")
    add_toc_note(doc)

    heading(doc, "一、项目组成员及分工")
    add_table(doc, ["成员", "学号", "承担工作", "贡献占比"], [
        ["________________", "________________", "个人独立完成需求分析、架构设计、数据库设计、后端开发、前端开发、AI 服务集成、截图、测试和文档整理。", "100%"],
    ])
    heading(doc, "二、AI 应用情况报告")
    add_table(doc, ["阶段", "AI 使用方式", "人工确认与修改"], [
        ["需求分析", "辅助拆分功能树、用户角色、用例和非功能需求。", "按课程要求和实际代码修正范围。"],
        ["后端开发", "辅助生成 Spring Boot 分层代码、DTO、Mapper 和测试思路。", "人工确认事务、权限、库存和降级逻辑。"],
        ["前端开发", "辅助生成 Vue 页面、API 封装、表格表单和截图自动化脚本。", "人工调整界面、路由和交互状态。"],
        ["AI 功能", "辅助设计导购、问答、文案和运营分析 Prompt。", "人工加入商品上下文、记录保存和异常降级。"],
        ["文档与图表", "辅助整理三份文档、UML/ER/流程图和截图说明。", "人工核对项目事实、截图覆盖和代码量口径。"],
    ])
    heading(doc, "三、实际开发记录")
    add_table(doc, ["日期", "活动", "产出"], [
        ["2026-06-04", "初始化前后端项目和仓库。", "Spring Boot、Vue3、README"],
        ["2026-06-05", "完成需求、数据库、接口和 UML 草稿。", "docs 初稿"],
        ["2026-06-06 至 2026-06-09", "实现认证、权限、商品和用户管理。", "auth/user/product 模块"],
        ["2026-06-10 至 2026-06-13", "实现购物车、订单、支付和库存流水。", "cart/order/inventory 模块"],
        ["2026-06-14 至 2026-06-16", "实现促销抢购、AI 导购、AI 问答和运营助手。", "promotion/ai 模块"],
        ["2026-06-17 至 2026-06-18", "补全截图、重绘图表、扩充需求与设计文档。", "docs/screenshots、docs/diagrams、docs/final"],
    ])
    heading(doc, "四、Git Commit 记录")
    log = run_git(["log", "--oneline", "--decorate", "--max-count=20"])
    for line in log.splitlines() if log else ["未能读取 Git 记录。"]:
        doc.add_paragraph(line, style="List Bullet")
    heading(doc, "五、关键产出清单")
    add_bullets(doc, [
        "后端：认证、用户、商品、购物车、订单、库存、促销、AI、上传和后台管理模块。",
        "前端：登录、注册、首页、商品详情、购物车、订单、后台看板、商品、订单、促销、AI、用户管理页面。",
        f"运行截图：{len(SCREENSHOT_ITEMS)} 张，覆盖页面、弹窗、抽屉和关键交互状态。",
        "设计图：用例图、类图、包图、ER 图、接口分层图、鉴权流程图、下单活动图、AI 顺序图、订单状态机图、抢购库存流程图和部署图。",
        "验证：后端集成测试、前端构建、截图脚本和 Word 文档可读性校验。",
    ])
    heading(doc, "六、项目总结")
    paragraph(doc, "项目完成了 B2C AI 电商系统的核心购物闭环、后台运营闭环、限时抢购库存控制和 AI 智能服务。当前系统适合课程演示和本地部署，后续可继续扩展真实支付、物流、消息队列、集中监控和更完整的数据看板。")
    heading(doc, "七、代码量统计")
    rows, total = count_lines()
    add_table(doc, ["范围", "文件数", "代码/文档行数"], rows + [["合计", "-", str(total)]])

    save_doc(doc, "项目管理文档.docx")


def edge_point(box: tuple[int, int, int, int], side: str, offset: int = 0) -> tuple[int, int]:
    x1, y1, x2, y2 = box
    if side == "left":
        return x1, (y1 + y2) // 2 + offset
    if side == "right":
        return x2, (y1 + y2) // 2 + offset
    if side == "top":
        return (x1 + x2) // 2 + offset, y1
    if side == "bottom":
        return (x1 + x2) // 2 + offset, y2
    raise ValueError(f"unknown side: {side}")


def draw_edge_arrow(
    draw: ImageDraw.ImageDraw,
    source_box: tuple[int, int, int, int],
    source_side: str,
    target_box: tuple[int, int, int, int],
    target_side: str,
    waypoints: list[tuple[int, int]] | None = None,
    fill: str = "#475569",
    width: int = 2,
    source_offset: int = 0,
    target_offset: int = 0,
) -> None:
    route(
        draw,
        [edge_point(source_box, source_side, source_offset), *(waypoints or []), edge_point(target_box, target_side, target_offset)],
        fill=fill,
        width=width,
    )


def diagram_class_clean() -> Path:
    img, draw, path = save_canvas("02-domain-class.png", (2300, 1450))
    label(draw, (70, 45), "领域类图：核心业务对象及关系")
    group_frames = [
        ("用户与权限", (70, 135, 430, 650)),
        ("商品与促销", (570, 135, 990, 1280)),
        ("交易链路", (1130, 135, 1530, 1340)),
        ("库存与 AI", (1660, 135, 2090, 1060)),
    ]
    for title, frame in group_frames:
        draw.rounded_rectangle(frame, radius=16, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 22, frame[1] + 20), title, font=font(24, True), fill="#0f172a")
    boxes = {
        "SysUser": (110, 190, 390, 330),
        "SysRole": (110, 470, 390, 590),
        "ProductCategory": (620, 190, 940, 330),
        "Product": (620, 470, 940, 620),
        "PromotionActivity": (620, 790, 940, 930),
        "PromotionProduct": (620, 1080, 940, 1230),
        "CartItem": (1180, 240, 1480, 380),
        "OrderMain": (1180, 560, 1480, 710),
        "OrderItem": (1180, 890, 1480, 1040),
        "PaymentRecord": (1180, 1160, 1480, 1300),
        "InventoryRecord": (1710, 470, 2040, 620),
        "AiChatRecord": (1710, 850, 2040, 1000),
    }
    texts = {
        "SysUser": "SysUser\nid: Long\nusername: String\npassword: String\nnickname: String\nstatus: Integer",
        "SysRole": "SysRole\nid: Long\ncode: String\nname: String",
        "ProductCategory": "ProductCategory\nid: Long\nparentId: Long\nname: String\nsort: Integer",
        "Product": "Product\nid: Long\ncategoryId: Long\nname: String\nprice: BigDecimal\nstock: Integer",
        "PromotionActivity": "PromotionActivity\nid: Long\nname: String\nstartTime: Date\nendTime: Date",
        "PromotionProduct": "PromotionProduct\nactivityId: Long\nproductId: Long\npromotionPrice: BigDecimal\npromotionStock: Integer",
        "CartItem": "CartItem\nuserId: Long\nproductId: Long\nquantity: Integer",
        "OrderMain": "OrderMain\norderNo: String\nuserId: Long\ntotalAmount: BigDecimal\nstatus: String",
        "OrderItem": "OrderItem\norderId: Long\nproductId: Long\nprice: BigDecimal\nquantity: Integer",
        "PaymentRecord": "PaymentRecord\norderId: Long\namount: BigDecimal\nstatus: String",
        "InventoryRecord": "InventoryRecord\nproductId: Long\nchangeQuantity: Integer\nbusinessType: String",
        "AiChatRecord": "AiChatRecord\nuserId: Long\nscene: String\nprompt: Text\nresponse: Text",
    }
    for name, box in boxes.items():
        wrapped_text_box(draw, box, texts[name], fill="#f8fafc", outline="#334155", font_size=18)
    draw_edge_arrow(draw, boxes["SysUser"], "bottom", boxes["SysRole"], "top", source_offset=-60, target_offset=-60)
    draw_edge_arrow(draw, boxes["ProductCategory"], "bottom", boxes["Product"], "top", source_offset=-80, target_offset=-80)
    draw_edge_arrow(draw, boxes["Product"], "bottom", boxes["PromotionActivity"], "top", waypoints=[(700, 700), (700, 760)], source_offset=-85, target_offset=-85)
    draw_edge_arrow(draw, boxes["PromotionActivity"], "bottom", boxes["PromotionProduct"], "top", source_offset=-80, target_offset=-80)
    draw_edge_arrow(draw, boxes["OrderMain"], "bottom", boxes["OrderItem"], "top", source_offset=-75, target_offset=-75)
    draw_edge_arrow(draw, boxes["OrderItem"], "bottom", boxes["PaymentRecord"], "top", source_offset=-75, target_offset=-75)
    draw_edge_arrow(draw, boxes["SysUser"], "right", boxes["CartItem"], "left", waypoints=[(500, 260), (500, 310), (1180, 310)], source_offset=-35, target_offset=-20)
    draw_edge_arrow(draw, boxes["SysUser"], "right", boxes["OrderMain"], "left", waypoints=[(520, 300), (520, 635), (1180, 635)], source_offset=25, target_offset=-15)
    draw_edge_arrow(draw, boxes["Product"], "right", boxes["CartItem"], "left", waypoints=[(1035, 520), (1035, 350), (1180, 350)], source_offset=-25, target_offset=25)
    draw_edge_arrow(draw, boxes["Product"], "right", boxes["OrderItem"], "left", waypoints=[(1065, 570), (1065, 955), (1180, 955)], source_offset=25, target_offset=-15)
    draw_edge_arrow(draw, boxes["Product"], "right", boxes["InventoryRecord"], "left", waypoints=[(1600, 545)], source_offset=55)
    draw_edge_arrow(draw, boxes["Product"], "bottom", boxes["PromotionProduct"], "top", waypoints=[(780, 720), (780, 1040)], target_offset=70)
    draw_edge_arrow(draw, boxes["SysUser"], "right", boxes["AiChatRecord"], "left", waypoints=[(2140, 300), (2140, 925), (2040, 925)], source_offset=55)
    img.save(path)
    return path


def diagram_activity_clean() -> Path:
    img, draw, path = save_canvas("04-order-activity.png", (1900, 1450))
    label(draw, (70, 45), "活动图：购物车下单流程")
    lanes = [("用户", 80, 430), ("前端", 430, 780), ("后端服务", 780, 1240), ("数据库", 1240, 1800)]
    for title, x1, x2 in lanes:
        draw.rounded_rectangle((x1, 135, x2, 1190), radius=12, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((x1 + 22, 160), title, font=font(24, True), fill="#0f172a")
    boxes = {
        "select": (145, 270, 365, 355),
        "form": (505, 270, 720, 355),
        "submit": (505, 455, 720, 540),
        "auth": (890, 455, 1140, 540),
        "stock": (890, 650, 1140, 735),
        "write": (1380, 650, 1650, 735),
        "inventory": (1380, 850, 1650, 935),
        "return": (890, 1025, 1140, 1110),
        "detail": (505, 1025, 720, 1110),
        "fail": (780, 1260, 1240, 1360),
    }
    labels = {
        "select": "选择商品\n点击结算",
        "form": "填写收货信息",
        "submit": "提交订单请求",
        "auth": "校验登录态\n购物车项",
        "stock": "校验商品状态\n与库存",
        "write": "写入订单主表\n与订单明细",
        "inventory": "扣减库存\n写入流水",
        "return": "返回订单 ID",
        "detail": "跳转订单详情",
        "fail": "异常返回：未登录 / 库存不足 / 写入失败",
    }
    for key, box in boxes.items():
        fill = "#fff1f2" if key == "fail" else "#f8fafc"
        outline = "#dc2626" if key == "fail" else "#334155"
        wrapped_text_box(draw, box, labels[key], fill=fill, outline=outline, font_size=20)
    for a, side_a, b, side_b in [
        ("select", "right", "form", "left"),
        ("form", "bottom", "submit", "top"),
        ("submit", "right", "auth", "left"),
        ("auth", "bottom", "stock", "top"),
        ("stock", "right", "write", "left"),
        ("write", "bottom", "inventory", "top"),
        ("return", "left", "detail", "right"),
    ]:
        draw_edge_arrow(draw, boxes[a], side_a, boxes[b], side_b)
    draw_edge_arrow(draw, boxes["inventory"], "left", boxes["return"], "right", waypoints=[(1300, 980), (1140, 1068)])
    draw_edge_arrow(draw, boxes["auth"], "bottom", boxes["fail"], "top", waypoints=[(1015, 1215)], fill="#dc2626")
    draw_edge_arrow(draw, boxes["stock"], "bottom", boxes["fail"], "top", waypoints=[(1090, 1215)], fill="#dc2626", source_offset=70, target_offset=80)
    img.save(path)
    return path


def diagram_deployment_clean() -> Path:
    img, draw, path = save_canvas("07-component-deployment.png", (2200, 1180))
    label(draw, (70, 45), "组件/部署图：本地演示环境")
    for title, frame in [("客户端层", (90, 180, 540, 940)), ("服务端层", (700, 180, 1250, 940)), ("基础设施层", (1460, 180, 2110, 940))]:
        draw.rounded_rectangle(frame, radius=16, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 24, frame[1] + 24), title, font=font(27, True), fill="#0f172a")
    boxes = {
        "browser": (160, 420, 470, 570),
        "api": (790, 320, 1160, 500),
        "script": (790, 640, 1160, 790),
        "mysql": (1530, 260, 1760, 380),
        "redis": (1830, 260, 2040, 380),
        "oss": (1530, 650, 1760, 770),
        "llm": (1830, 650, 2040, 770),
    }
    labels = {
        "browser": "浏览器\nVue3 SPA\nlocalhost:5173",
        "api": "Spring Boot\nREST API\nlocalhost:8080",
        "script": "文档/截图脚本\nPython + Playwright",
        "mysql": "MySQL 8\n业务数据",
        "redis": "Redis\n促销库存",
        "oss": "阿里云 OSS\n商品图片",
        "llm": "OpenAI 兼容 API\nAI 服务",
    }
    for key, box in boxes.items():
        wrapped_text_box(draw, box, labels[key], fill="#f8fafc", outline="#334155", font_size=22, bold=True)
    draw_edge_arrow(draw, boxes["browser"], "right", boxes["api"], "left", waypoints=[(620, 495), (620, 410)], width=3)
    bus_x = 1360
    draw.line([(1250, 410), (bus_x, 410), (bus_x, 845)], fill="#475569", width=3)
    for key in ["mysql", "redis", "oss", "llm"]:
        route(draw, [(bus_x, edge_point(boxes[key], "left")[1]), edge_point(boxes[key], "left")], width=2)
    img.save(path)
    return path


def diagram_er() -> Path:
    img, draw, path = save_canvas("08-er.png", (2300, 1450))
    label(draw, (70, 45), "数据库 ER 图：核心表关系")
    boxes = {
        "sys_user": (100, 190, 360, 290),
        "sys_role": (100, 450, 360, 550),
        "sys_user_role": (100, 720, 360, 820),
        "product_category": (620, 190, 920, 290),
        "product": (620, 470, 920, 570),
        "product_image": (620, 750, 920, 850),
        "promotion_activity": (620, 1030, 920, 1130),
        "promotion_product": (620, 1250, 920, 1350),
        "cart_item": (1180, 260, 1460, 360),
        "order_main": (1180, 560, 1460, 660),
        "order_item": (1180, 850, 1460, 950),
        "payment_record": (1180, 1120, 1460, 1220),
        "inventory_record": (1720, 560, 2040, 660),
        "ai_chat_record": (1720, 850, 2040, 950),
    }
    for title, frame in [("用户权限", (70, 135, 410, 880)), ("商品促销", (570, 135, 970, 1390)), ("交易", (1130, 135, 1510, 1270)), ("记录", (1670, 135, 2090, 1020))]:
        draw.rounded_rectangle(frame, radius=16, fill="#ffffff", outline="#cbd5e1", width=3)
        draw.text((frame[0] + 24, frame[1] + 22), title, font=font(24, True), fill="#0f172a")
    for name, box in boxes.items():
        wrapped_text_box(draw, box, name, fill="#f8fafc", outline="#334155", font_size=20, bold=True)
    draw_edge_arrow(draw, boxes["sys_user_role"], "top", boxes["sys_user"], "bottom", source_offset=-65, target_offset=-65)
    draw_edge_arrow(draw, boxes["sys_user_role"], "top", boxes["sys_role"], "bottom", source_offset=65, target_offset=65)
    draw_edge_arrow(draw, boxes["product"], "top", boxes["product_category"], "bottom")
    draw_edge_arrow(draw, boxes["product"], "bottom", boxes["product_image"], "top", source_offset=-70, target_offset=-70)
    draw_edge_arrow(draw, boxes["promotion_product"], "top", boxes["promotion_activity"], "bottom", source_offset=-70, target_offset=-70)
    draw_edge_arrow(draw, boxes["promotion_product"], "top", boxes["product"], "bottom", source_offset=70, target_offset=70)
    draw_edge_arrow(draw, boxes["sys_user"], "right", boxes["cart_item"], "left", waypoints=[(500, 240), (500, 310), (1180, 310)])
    draw_edge_arrow(draw, boxes["product"], "right", boxes["cart_item"], "left", waypoints=[(1040, 520), (1040, 335), (1180, 335)], target_offset=25)
    draw_edge_arrow(draw, boxes["sys_user"], "right", boxes["order_main"], "left", waypoints=[(520, 250), (520, 610), (1180, 610)], source_offset=35)
    draw_edge_arrow(draw, boxes["order_main"], "bottom", boxes["order_item"], "top")
    draw_edge_arrow(draw, boxes["product"], "right", boxes["order_item"], "left", waypoints=[(1065, 520), (1065, 900), (1180, 900)], source_offset=25)
    draw_edge_arrow(draw, boxes["order_item"], "bottom", boxes["payment_record"], "top", source_offset=-70, target_offset=-70)
    draw_edge_arrow(draw, boxes["product"], "right", boxes["inventory_record"], "left", waypoints=[(1580, 520), (1580, 610), (1720, 610)], source_offset=50)
    draw_edge_arrow(draw, boxes["sys_user"], "right", boxes["ai_chat_record"], "left", waypoints=[(2140, 250), (2140, 900), (2040, 900)], source_offset=65)
    img.save(path)
    return path


def diagram_api_layers() -> Path:
    img, draw, path = save_canvas("09-api-layers.png", (2000, 1500))
    label(draw, (70, 45), "接口分层图：前端 API 到后端业务模块")
    layer_boxes = []
    layers = [
        ("Vue 页面层", ["首页/详情", "购物车/订单", "后台管理", "AI 页面"], 150),
        ("API 封装层", ["auth.ts", "products.ts", "cart.ts / orders.ts", "admin.ts / ai.ts"], 390),
        ("Controller 层", ["AuthController", "ProductController", "OrderController", "Admin* / AiController"], 630),
        ("Service 层", ["AuthService", "ProductService", "OrderService", "PromotionService / AiService"], 870),
        ("持久化/外部服务", ["Mapper / MySQL", "Redis", "OSS", "LLM API"], 1110),
    ]
    for title, items, y in layers:
        frame = (120, y, 1880, y + 170)
        layer_boxes.append(frame)
        draw.rounded_rectangle(frame, radius=16, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((155, y + 24), title, font=font(24, True), fill="#0f172a")
        for i, item in enumerate(items):
            x = 420 + i * 350
            wrapped_text_box(draw, (x, y + 55, x + 280, y + 132), item, fill="#f8fafc", outline="#334155", font_size=18)
    for upper, lower in zip(layer_boxes, layer_boxes[1:]):
        draw_edge_arrow(draw, upper, "bottom", lower, "top", width=3)
    wrapped_text_box(draw, (120, 1320, 1880, 1420), "说明：页面层处理交互；API 封装层统一 Axios 调用；Controller 负责 HTTP 入参；Service 承载业务规则；Mapper/外部服务负责数据与第三方能力。", fill="#f8fafc", outline="#cbd5e1", font_size=21)
    img.save(path)
    return path


def diagram_auth_flow() -> Path:
    img, draw, path = save_canvas("10-auth-flow.png", (1900, 1050))
    label(draw, (70, 45), "权限鉴权流程图：JWT 与角色控制")
    boxes = {
        "login": (110, 220, 390, 340),
        "auth": (520, 220, 850, 340),
        "jwt": (980, 220, 1290, 340),
        "store": (1420, 220, 1710, 340),
        "request": (110, 620, 390, 740),
        "filter": (520, 620, 850, 740),
        "security": (980, 620, 1290, 740),
        "result": (1420, 620, 1710, 740),
    }
    labels = {
        "login": "用户提交\n账号密码",
        "auth": "AuthController\n校验账号密码",
        "jwt": "签发 JWT\n返回用户角色",
        "store": "前端保存\nToken",
        "request": "请求携带\nAuthorization",
        "filter": "JwtAuthentication\nFilter 解析",
        "security": "SecurityConfig\n匹配权限",
        "result": "允许访问\n或 401 / 403",
    }
    for key, box in boxes.items():
        wrapped_text_box(draw, box, labels[key], fill="#f8fafc", outline="#334155", font_size=21, bold=True)
    for a, b in [("login", "auth"), ("auth", "jwt"), ("jwt", "store"), ("request", "filter"), ("filter", "security"), ("security", "result")]:
        draw_edge_arrow(draw, boxes[a], "right", boxes[b], "left")
    draw_edge_arrow(draw, boxes["store"], "bottom", boxes["request"], "top", waypoints=[(1565, 470), (250, 470)])
    wrapped_text_box(draw, (110, 840, 1710, 950), "角色规则：前台订单与购物车要求登录；后台商品、订单、促销、AI 运营要求 OPERATOR 或 ADMIN；用户角色管理仅 ADMIN 可操作。", fill="#f8fafc", outline="#cbd5e1", font_size=22)
    img.save(path)
    return path


def diagram_promotion_flow() -> Path:
    img, draw, path = save_canvas("11-promotion-flow.png", (1900, 1250))
    label(draw, (70, 45), "抢购库存流程图：Redis 预扣与数据库落单")
    lanes = [("用户/前端", 90, 430), ("后端服务", 430, 850), ("Redis", 850, 1210), ("MySQL", 1210, 1770)]
    for title, x1, x2 in lanes:
        draw.rounded_rectangle((x1, 140, x2, 980), radius=14, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((x1 + 20, 165), title, font=font(24, True), fill="#0f172a")
    boxes = {
        "click": (145, 280, 375, 370),
        "form": (145, 560, 375, 650),
        "validate": (525, 280, 755, 380),
        "redis": (925, 280, 1135, 380),
        "mysql": (1320, 280, 1600, 380),
        "return": (525, 560, 755, 650),
        "rollback": (925, 820, 1135, 920),
    }
    labels = {
        "click": "点击立即抢购",
        "form": "提交数量\n与收货信息",
        "validate": "校验活动\n时间 / 限购",
        "redis": "预扣活动库存",
        "mysql": "创建订单\n和订单明细",
        "return": "返回订单详情",
        "rollback": "失败补偿\n回滚 Redis",
    }
    for key, box in boxes.items():
        fill = "#fff1f2" if key == "rollback" else "#f8fafc"
        outline = "#dc2626" if key == "rollback" else "#334155"
        wrapped_text_box(draw, box, labels[key], fill=fill, outline=outline, font_size=20, bold=True)
    for a, b in [("click", "validate"), ("validate", "redis"), ("redis", "mysql")]:
        draw_edge_arrow(draw, boxes[a], "right", boxes[b], "left")
    draw_edge_arrow(draw, boxes["mysql"], "bottom", boxes["return"], "right", waypoints=[(1460, 735), (755, 735)])
    draw_edge_arrow(draw, boxes["return"], "left", boxes["form"], "right")
    draw_edge_arrow(draw, boxes["mysql"], "bottom", boxes["rollback"], "top", waypoints=[(1460, 1060), (1030, 1060)], fill="#dc2626")
    draw.text((1160, 1030), "落单失败或校验失败", font=font(18), fill="#dc2626")
    img.save(path)
    return path


DIAGRAMS = {
    "use_case": DIAGRAM_DIR / "用例图.png",
    "class": DIAGRAM_DIR / "领域类图.png",
    "package": DIAGRAM_DIR / "包图.png",
    "activity": DIAGRAM_DIR / "下单活动图.png",
    "sequence": DIAGRAM_DIR / "AI导购顺序图.png",
    "state": DIAGRAM_DIR / "订单状态机图.png",
    "deployment": DIAGRAM_DIR / "组件部署图.png",
    "er": DIAGRAM_DIR / "ER图.png",
    "api": DIAGRAM_DIR / "接口分层图.png",
    "auth": DIAGRAM_DIR / "权限鉴权流程图.png",
    "promotion": DIAGRAM_DIR / "抢购库存流程图.png",
}


def generate_diagrams() -> list[Path]:
    missing = [path for path in DIAGRAMS.values() if not path.exists()]
    if missing:
        joined = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing externally rendered diagram PNG files:\n{joined}")
    return list(DIAGRAMS.values())


def main() -> None:
    ensure_dirs()
    generated = generate_diagrams()
    create_requirements_doc(DIAGRAMS)
    create_design_doc(DIAGRAMS)
    create_management_doc()
    print(f"Using {len(generated)} external diagrams in {DIAGRAM_DIR}")
    print(f"Generated final documents in {FINAL_DIR}")


if __name__ == "__main__":
    main()
