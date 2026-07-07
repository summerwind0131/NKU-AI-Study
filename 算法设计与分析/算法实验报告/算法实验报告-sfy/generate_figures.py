from __future__ import annotations

from math import hypot
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FIGURE_DIR = ROOT / "figures"
FIGURE_DIR.mkdir(exist_ok=True)

FONT_REGULAR = Path("C:/Windows/Fonts/msyh.ttc")
FONT_BOLD = Path("C:/Windows/Fonts/msyhbd.ttc")

INK = "#243447"
BLUE = "#2F6FAD"
BLUE_DARK = "#315E8A"
BLUE_LIGHT = "#EAF2F8"
GREEN = "#27835B"
GREEN_LIGHT = "#DDF1E6"
ORANGE = "#E58A17"
RED = "#CE493D"
GRAY = "#667786"
EDGE_GRAY = "#B8C4CF"
PANEL = "#FAFBFC"
BORDER = "#C5D2DE"
WHITE = "#FFFFFF"

EDGES = [
    (1, 2, 4),
    (1, 3, 3),
    (1, 4, 1),
    (2, 4, 5),
    (2, 5, 7),
    (3, 4, 2),
    (3, 6, 3),
    (4, 5, 5),
    (4, 6, 4),
    (5, 6, 6),
]

MST = [(1, 4, 1), (3, 4, 2), (3, 6, 3), (1, 2, 4), (4, 5, 5)]

KRUSKAL_EVENTS = [
    ((1, 4, 1), True, "权值最小，接受"),
    ((3, 4, 2), True, "连接两个分量，接受"),
    ((1, 3, 3), False, "V1-V4-V3 已连通，舍弃"),
    ((3, 6, 3), True, "连接新顶点 V6，接受"),
    ((1, 2, 4), True, "连接新顶点 V2，接受"),
    ((4, 6, 4), False, "V4-V3-V6 已连通，舍弃"),
    ((2, 4, 5), False, "V2-V1-V4 已连通，舍弃"),
    ((4, 5, 5), True, "连接 V5，生成树完成"),
]

PRIM_EVENTS = [
    ((1, 4, 1), {1}, "从 V1 出发，选择最小跨边"),
    ((4, 3, 2), {1, 4}, "当前树到 V3 的最小跨边"),
    ((3, 6, 3), {1, 3, 4}, "扩展到新顶点 V6"),
    ((1, 2, 4), {1, 3, 4, 6}, "跳过失效边，选择 V1-V2"),
    ((4, 5, 5), {1, 2, 3, 4, 6}, "连接最后一个顶点 V5"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size)


def edge_key(u: int, v: int) -> tuple[int, int]:
    return min(u, v), max(u, v)


def centered_text(
    draw: ImageDraw.ImageDraw,
    point: tuple[float, float],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
) -> None:
    box = draw.textbbox((0, 0), text, font=text_font)
    width = box[2] - box[0]
    height = box[3] - box[1]
    draw.text(
        (point[0] - width / 2, point[1] - height / 2 - 2),
        text,
        font=text_font,
        fill=fill,
    )


def dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    fill: str,
    width: int,
    dash: int = 14,
    gap: int = 10,
) -> None:
    x1, y1 = start
    x2, y2 = end
    length = hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    dx = (x2 - x1) / length
    dy = (y2 - y1) / length
    position = 0.0
    while position < length:
        stop = min(position + dash, length)
        draw.line(
            (
                x1 + dx * position,
                y1 + dy * position,
                x1 + dx * stop,
                y1 + dy * stop,
            ),
            fill=fill,
            width=width,
        )
        position += dash + gap


def graph_positions(
    box: tuple[int, int, int, int],
) -> dict[int, tuple[float, float]]:
    left, top, right, bottom = box
    width = right - left
    height = bottom - top
    relative = {
        1: (0.48, 0.08),
        2: (0.10, 0.38),
        3: (0.88, 0.27),
        4: (0.50, 0.52),
        5: (0.12, 0.88),
        6: (0.88, 0.86),
    }
    return {
        vertex: (left + x * width, top + y * height)
        for vertex, (x, y) in relative.items()
    }


def draw_graph(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    selected: set[tuple[int, int]] | None = None,
    current: tuple[int, int] | None = None,
    rejected: set[tuple[int, int]] | None = None,
    candidates: set[tuple[int, int]] | None = None,
    visited: set[int] | None = None,
    order_labels: dict[tuple[int, int], int] | None = None,
    compact: bool = False,
) -> None:
    selected = selected or set()
    rejected = rejected or set()
    candidates = candidates or set()
    visited = visited or set()
    order_labels = order_labels or {}

    positions = graph_positions(box)
    edge_font = font(20 if compact else 29, bold=True)
    node_font = font(21 if compact else 31, bold=True)
    order_font = font(17 if compact else 21, bold=True)
    node_radius = 27 if compact else 39
    offsets = {
        (1, 2): (-8, -14),
        (1, 3): (0, -18),
        (1, 4): (20, 0),
        (2, 4): (0, -18),
        (2, 5): (-19, 0),
        (3, 4): (0, -18),
        (3, 6): (21, 0),
        (4, 5): (-4, 18),
        (4, 6): (4, -18),
        (5, 6): (0, 19),
    }

    for u, v, weight in EDGES:
        key = edge_key(u, v)
        start = positions[u]
        end = positions[v]
        color = EDGE_GRAY
        line_width = 3 if compact else 4
        use_dashes = False

        if key in candidates:
            color = ORANGE
            line_width = 5 if compact else 7
        if key in selected:
            color = GREEN
            line_width = 7 if compact else 9
        if key in rejected:
            color = RED
            line_width = 6 if compact else 8
            use_dashes = True
        if current == key:
            color = RED if key in rejected else BLUE
            line_width = 9 if compact else 12

        if use_dashes:
            dashed_line(draw, start, end, color, line_width)
        else:
            draw.line((*start, *end), fill=color, width=line_width)

        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        offset_x, offset_y = offsets[key]
        label_x = mid_x + offset_x
        label_y = mid_y + offset_y
        text_box = draw.textbbox((0, 0), str(weight), font=edge_font)
        text_width = text_box[2] - text_box[0]
        text_height = text_box[3] - text_box[1]
        draw.rounded_rectangle(
            (
                label_x - text_width / 2 - 7,
                label_y - text_height / 2 - 4,
                label_x + text_width / 2 + 7,
                label_y + text_height / 2 + 4,
            ),
            radius=6,
            fill=WHITE,
        )
        centered_text(draw, (label_x, label_y), str(weight), edge_font, INK)

        if key in order_labels:
            badge_x = mid_x + 25
            badge_y = mid_y - 29
            draw.ellipse(
                (badge_x - 15, badge_y - 15, badge_x + 15, badge_y + 15),
                fill=BLUE,
            )
            centered_text(
                draw,
                (badge_x, badge_y),
                str(order_labels[key]),
                order_font,
                WHITE,
            )

    for vertex, (x, y) in positions.items():
        if vertex in visited:
            node_fill = GREEN_LIGHT
            outline = GREEN
        else:
            node_fill = "#E7EEF5"
            outline = BLUE_DARK
        draw.ellipse(
            (x - node_radius, y - node_radius, x + node_radius, y + node_radius),
            fill=node_fill,
            outline=outline,
            width=4,
        )
        centered_text(draw, (x, y), f"V{vertex}", node_font, INK)


def crossing_edges(visited: set[int]) -> set[tuple[int, int]]:
    return {
        edge_key(u, v)
        for u, v, _ in EDGES
        if (u in visited) != (v in visited)
    }


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, format="PNG", dpi=(300, 300), optimize=True)
    print(path.relative_to(ROOT))


def create_original_graph() -> None:
    image = Image.new("RGB", (1600, 1180), WHITE)
    draw = ImageDraw.Draw(image)
    draw.text((80, 52), "实验图：无向带权连通图", font=font(48, True), fill=INK)
    draw.text(
        (82, 122),
        "顶点数 |V| = 6，边数 |E| = 10",
        font=font(28),
        fill=GRAY,
    )
    draw_graph(draw, (125, 205, 1475, 1040))

    legend_y = 1090
    draw.line((410, legend_y, 485, legend_y), fill=EDGE_GRAY, width=6)
    draw.text((500, legend_y - 20), "原始边", font=font(25), fill=INK)
    draw.ellipse(
        (710, legend_y - 25, 760, legend_y + 25),
        fill="#E7EEF5",
        outline=BLUE_DARK,
        width=3,
    )
    draw.text((775, legend_y - 20), "顶点", font=font(25), fill=INK)
    save_png(image, FIGURE_DIR / "original_graph.png")


def create_kruskal_process() -> None:
    image = Image.new("RGB", (1900, 2300), WHITE)
    draw = ImageDraw.Draw(image)
    draw.text((75, 48), "Kruskal 算法逐边检查过程", font=font(48, True), fill=INK)
    draw.text(
        (78, 116),
        "排序规则：权值 → 较小端点 → 较大端点",
        font=font(27),
        fill=GRAY,
    )

    legend = [
        (GREEN, "此前已接受"),
        (BLUE, "当前接受"),
        (RED, "当前舍弃（成环）"),
        (EDGE_GRAY, "尚未处理"),
    ]
    x = 90
    for color, label in legend:
        draw.line((x, 183, x + 58, 183), fill=color, width=9)
        draw.text((x + 70, 165), label, font=font(22), fill=INK)
        x += 420

    selected: set[tuple[int, int]] = set()
    rejected: set[tuple[int, int]] = set()
    panel_width = 860
    panel_height = 485
    x_positions = [70, 970]
    y_positions = [235, 745, 1255, 1765]

    for index, (edge, accepted, reason) in enumerate(KRUSKAL_EVENTS):
        left = x_positions[index % 2]
        top = y_positions[index // 2]
        right = left + panel_width
        bottom = top + panel_height
        draw.rounded_rectangle(
            (left, top, right, bottom),
            radius=20,
            fill=PANEL,
            outline=BORDER,
            width=3,
        )

        u, v, weight = edge
        key = edge_key(u, v)
        status = "接受" if accepted else "舍弃"
        status_color = GREEN if accepted else RED
        draw.text(
            (left + 25, top + 20),
            f"检查 {index + 1}：V{u}-V{v}({weight})",
            font=font(28, True),
            fill=INK,
        )
        draw.rounded_rectangle(
            (right - 140, top + 18, right - 25, top + 62),
            radius=11,
            fill=status_color,
        )
        centered_text(
            draw,
            (right - 82, top + 40),
            status,
            font(22, True),
            WHITE,
        )

        rejected_now = rejected | ({key} if not accepted else set())
        draw_graph(
            draw,
            (left + 28, top + 75, right - 28, bottom - 70),
            selected=selected,
            current=key,
            rejected=rejected_now,
            compact=True,
        )
        draw.text(
            (left + 27, bottom - 53),
            reason,
            font=font(22),
            fill=status_color,
        )

        if accepted:
            selected.add(key)
        else:
            rejected.add(key)

    save_png(image, FIGURE_DIR / "kruskal_process.png")


def create_prim_process() -> None:
    image = Image.new("RGB", (1900, 1800), WHITE)
    draw = ImageDraw.Draw(image)
    draw.text((75, 48), "Prim 算法从 V1 出发的扩展过程", font=font(48, True), fill=INK)
    draw.text(
        (78, 116),
        "橙色为当前割上的候选边，蓝色为本轮选择，绿色为已加入生成树",
        font=font(27),
        fill=GRAY,
    )

    selected: set[tuple[int, int]] = set()
    stale: set[tuple[int, int]] = set()
    panel_width = 860
    panel_height = 475
    x_positions = [70, 970]
    y_positions = [190, 690, 1190]

    for index, (edge, visited_before, reason) in enumerate(PRIM_EVENTS):
        left = x_positions[index % 2]
        top = y_positions[index // 2]
        right = left + panel_width
        bottom = top + panel_height
        draw.rounded_rectangle(
            (left, top, right, bottom),
            radius=20,
            fill=PANEL,
            outline=BORDER,
            width=3,
        )

        u, v, weight = edge
        key = edge_key(u, v)
        if index == 3:
            stale = {edge_key(1, 3), edge_key(4, 6)}
        draw.text(
            (left + 25, top + 20),
            f"步骤 {index + 1}：选择 V{u}-V{v}({weight})",
            font=font(28, True),
            fill=INK,
        )
        draw_graph(
            draw,
            (left + 28, top + 74, right - 28, bottom - 70),
            selected=selected,
            current=key,
            rejected=stale,
            candidates=crossing_edges(visited_before),
            visited=visited_before,
            compact=True,
        )
        draw.text(
            (left + 27, bottom - 53),
            reason,
            font=font(22),
            fill=BLUE_DARK,
        )
        selected.add(key)

    left = x_positions[1]
    top = y_positions[2]
    right = left + panel_width
    bottom = top + panel_height
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=20,
        fill=BLUE_LIGHT,
        outline="#8FB1CF",
        width=3,
    )
    draw.text(
        (left + 35, top + 34),
        "Prim 的关键判断",
        font=font(32, True),
        fill=BLUE_DARK,
    )
    notes = [
        "1. 始终只比较从已访问集合到外部的跨边。",
        "2. 候选边两端均已访问时，该边已经失效。",
        "3. 每轮加入一个新顶点，因此不会形成环。",
        "4. 加入 5 条边后覆盖 6 个顶点，算法结束。",
    ]
    y = top + 112
    for note in notes:
        draw.text((left + 42, y), note, font=font(24), fill=INK)
        y += 65
    draw.rounded_rectangle(
        (left + 42, bottom - 105, right - 42, bottom - 38),
        radius=14,
        fill=GREEN,
    )
    centered_text(
        draw,
        ((left + right) / 2, bottom - 71),
        "最终边数 = 5，总权值 = 15",
        font(28, True),
        WHITE,
    )
    save_png(image, FIGURE_DIR / "prim_process.png")


def create_mst_comparison() -> None:
    image = Image.new("RGB", (1900, 1120), WHITE)
    draw = ImageDraw.Draw(image)
    draw.text((75, 48), "两种算法的最终结果与选边顺序", font=font(48, True), fill=INK)
    draw.text(
        (78, 116),
        "圆形编号表示选边顺序；无向边 V4-V3 与 V3-V4 表示同一条边",
        font=font(27),
        fill=GRAY,
    )

    panels = [
        (70, 190, 920, 940, "Kruskal", [(1, 4), (3, 4), (3, 6), (1, 2), (4, 5)]),
        (
            980,
            190,
            1830,
            940,
            "Prim（从 V1 出发）",
            [(1, 4), (3, 4), (3, 6), (1, 2), (4, 5)],
        ),
    ]
    selected = {edge_key(u, v) for u, v, _ in MST}

    for left, top, right, bottom, title, order in panels:
        draw.rounded_rectangle(
            (left, top, right, bottom),
            radius=22,
            fill=PANEL,
            outline=BORDER,
            width=3,
        )
        draw.text(
            (left + 28, top + 20),
            title,
            font=font(32, True),
            fill=BLUE_DARK,
        )
        order_map = {
            edge_key(u, v): index + 1 for index, (u, v) in enumerate(order)
        }
        draw_graph(
            draw,
            (left + 30, top + 80, right - 30, bottom - 30),
            selected=selected,
            visited=set(range(1, 7)),
            order_labels=order_map,
            compact=True,
        )

    draw.rounded_rectangle((275, 980, 1625, 1070), radius=18, fill=GREEN_LIGHT)
    centered_text(
        draw,
        (950, 1024),
        "共同结果：5 条边，覆盖 6 个顶点，无环，总权值 1+2+3+4+5 = 15",
        font(28, True),
        "#246A4B",
    )
    save_png(image, FIGURE_DIR / "mst_comparison.png")


def main() -> None:
    create_original_graph()
    create_kruskal_process()
    create_prim_process()
    create_mst_comparison()


if __name__ == "__main__":
    main()
