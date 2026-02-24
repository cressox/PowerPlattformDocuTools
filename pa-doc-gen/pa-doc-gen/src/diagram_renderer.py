"""
diagram_renderer.py – Visuelles Rendern des Flussdiagramms mit QPainter.

Erzeugt ein gerendertes Bild (QPixmap / PNG) des Flow-Diagramms,
anstatt nur Mermaid-Textcode zu generieren.
"""
from __future__ import annotations

import math
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen,
    QPixmap, QImage, QLinearGradient, QBrush,
)
from PySide6.QtWidgets import QApplication

from models import PAProject, FlowAction, FlowTrigger


def _ensure_qapp():
    """Stellt sicher, dass eine QApplication-Instanz existiert (fuer headless Rendering)."""
    if QApplication.instance() is None:
        QApplication([])


# ---------------------------------------------------------------------------
# Farben (abgestimmt auf das Dark-Theme)
# ---------------------------------------------------------------------------

COLORS = {
    "bg":           QColor("#13151E"),
    "trigger":      QColor("#5B8DEF"),
    "action":       QColor("#2A3045"),
    "action_border":QColor("#5B8DEF"),
    "connector":    QColor("#1A3A5C"),
    "condition":    QColor("#E0A526"),
    "loop":         QColor("#9C27B0"),
    "scope":        QColor("#2E3B4E"),
    "branch_true":  QColor("#4CAF50"),
    "branch_false": QColor("#EF5B5B"),
    "variable":     QColor("#00897B"),
    "data":         QColor("#546E7A"),
    "http":         QColor("#FF7043"),
    "terminate":    QColor("#EF5B5B"),
    "text":         QColor("#EAEAEA"),
    "text_dark":    QColor("#FFFFFF"),
    "edge":         QColor("#5B8DEF"),
    "edge_yes":     QColor("#4CAF50"),
    "edge_no":      QColor("#EF5B5B"),
    "label_bg":     QColor("#1A1D28"),
}

# Aktionstyp -> Farb-Key
TYPE_COLOR_MAP = {
    "If": "condition", "Condition": "condition", "Switch": "condition",
    "Foreach": "loop", "Until": "loop",
    "Scope": "scope",
    "Branch_True": "branch_true", "Branch_False": "branch_false",
    "Switch_Case": "branch_true", "Switch_Default": "branch_false",
    "InitializeVariable": "variable", "SetVariable": "variable",
    "IncrementVariable": "variable", "DecrementVariable": "variable",
    "AppendToArrayVariable": "variable", "AppendToStringVariable": "variable",
    "Compose": "data", "ParseJson": "data",
    "Http": "http", "HttpWebhook": "http",
    "Terminate": "terminate", "Response": "terminate",
}

# ---------------------------------------------------------------------------
# Layout-Knoten
# ---------------------------------------------------------------------------

NODE_W = 220
NODE_H = 48
NODE_PAD_X = 30
NODE_PAD_Y = 50
FONT_SIZE = 10
ARROW_SIZE = 8


@dataclass
class LayoutNode:
    """Ein positionierter Knoten im Diagramm."""
    label: str
    sub_label: str = ""
    x: float = 0.0
    y: float = 0.0
    w: float = NODE_W
    h: float = NODE_H
    color_key: str = "action"
    shape: str = "rect"  # rect, diamond, rounded, stadium, circle
    children: list["LayoutNode"] = field(default_factory=list)
    edge_label: str = ""  # Label auf der eingehenden Kante

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def top(self) -> QPointF:
        return QPointF(self.cx, self.y)

    @property
    def bottom(self) -> QPointF:
        return QPointF(self.cx, self.y + self.h)


# ---------------------------------------------------------------------------
# Layout-Algorithmus
# ---------------------------------------------------------------------------

def _shape_for_type(action_type: str) -> str:
    if action_type in ("If", "Condition", "Switch"):
        return "diamond"
    if action_type in ("Foreach", "Until"):
        return "rounded"
    if action_type in ("Scope", "Branch_True", "Branch_False", "Switch_Case", "Switch_Default"):
        return "stadium"
    if action_type in ("Terminate", "Response"):
        return "circle"
    return "rect"


def _color_for_type(action_type: str) -> str:
    return TYPE_COLOR_MAP.get(action_type, "action")


def _build_layout_nodes(actions: list[FlowAction]) -> list[LayoutNode]:
    """Wandelt FlowActions in LayoutNodes um (ohne Positionierung)."""
    nodes = []
    for action in actions:
        shape = _shape_for_type(action.action_type)
        color_key = _color_for_type(action.action_type)

        w = NODE_W
        h = NODE_H
        if shape == "diamond":
            w = NODE_W + 40
            h = NODE_H + 16

        sub = action.connector if action.connector else ""
        node = LayoutNode(
            label=action.name[:35] + ("…" if len(action.name) > 35 else ""),
            sub_label=sub[:30] + ("…" if len(sub) > 30 else "") if sub else "",
            w=w, h=h,
            color_key=color_key,
            shape=shape,
        )

        # Kinder verarbeiten
        if action.children:
            if action.action_type in ("If", "Condition"):
                true_branch = [c for c in action.children if c.action_type == "Branch_True"]
                false_branch = [c for c in action.children if c.action_type == "Branch_False"]

                if true_branch:
                    tb = true_branch[0]
                    tb_node = LayoutNode(
                        label="Ja", w=NODE_W - 20, h=36,
                        color_key="branch_true", shape="stadium", edge_label="Ja",
                    )
                    if tb.children:
                        tb_node.children = _build_layout_nodes(tb.children)
                    node.children.append(tb_node)
                if false_branch:
                    fb = false_branch[0]
                    fb_node = LayoutNode(
                        label="Nein", w=NODE_W - 20, h=36,
                        color_key="branch_false", shape="stadium", edge_label="Nein",
                    )
                    if fb.children:
                        fb_node.children = _build_layout_nodes(fb.children)
                    node.children.append(fb_node)
            elif action.action_type == "Switch":
                for child in action.children:
                    case_label = child.name.split("Case: ")[-1] if "Case: " in child.name else child.name
                    c_node = LayoutNode(
                        label=case_label[:25], w=NODE_W - 20, h=36,
                        color_key="branch_true" if child.action_type != "Switch_Default" else "branch_false",
                        shape="stadium",
                        edge_label=case_label[:15],
                    )
                    if child.children:
                        c_node.children = _build_layout_nodes(child.children)
                    node.children.append(c_node)
            else:
                # Scope, Foreach, Until – Kinder sequentiell
                node.children = _build_layout_nodes(action.children)

        nodes.append(node)
    return nodes


def _subtree_width(node: LayoutNode) -> float:
    """Berechnet die Gesamtbreite eines Teilbaums."""
    if not node.children:
        return node.w + NODE_PAD_X

    # Fuer Branches: Summe aller Kinder-Breiten
    parent_shape = node.shape
    if parent_shape == "diamond":
        # Branches nebeneinander
        total = 0
        for child in node.children:
            total += _branch_width(child)
        return max(total, node.w + NODE_PAD_X)
    else:
        # Sequentielle Kinder: breitestes Kind
        max_w = node.w + NODE_PAD_X
        for child in node.children:
            max_w = max(max_w, _subtree_width(child))
        return max_w


def _branch_width(node: LayoutNode) -> float:
    """Breite eines Branch-Knotens inkl. seiner Kinder."""
    w = node.w + NODE_PAD_X
    if node.children:
        # Kinder sind sequentiell unter diesem Branch
        for child in node.children:
            w = max(w, _subtree_width(child))
    return w


def _branch_height(node: LayoutNode) -> float:
    """Hoehe eines Branch-Zweigs."""
    h = node.h + NODE_PAD_Y
    if node.children:
        for child in node.children:
            h += child.h + NODE_PAD_Y
            if child.shape == "diamond":
                h += _max_branch_height(child)
    return h


def _max_branch_height(node: LayoutNode) -> float:
    """Maximale Hoehe aller Branches eines Diamond-Knotens."""
    if not node.children:
        return 0
    max_h = 0
    for child in node.children:
        bh = _branch_height(child)
        max_h = max(max_h, bh)
    return max_h


def _position_nodes(
    nodes: list[LayoutNode],
    start_x: float,
    start_y: float,
    available_width: float,
) -> float:
    """
    Positioniert eine lineare Kette von Knoten.
    Gibt die Y-Position nach dem letzten Knoten zurueck.
    """
    y = start_y
    center_x = start_x + available_width / 2

    for node in nodes:
        node.x = center_x - node.w / 2
        node.y = y
        y += node.h + NODE_PAD_Y

        if node.shape == "diamond" and node.children:
            # Branches nebeneinander layouten
            num_branches = len(node.children)
            if num_branches == 0:
                continue

            branch_widths = [_branch_width(ch) for ch in node.children]
            total_branch_w = sum(branch_widths)

            # Branches zentrieren unter dem Diamond
            bx = center_x - total_branch_w / 2
            max_branch_y = y

            for i, child in enumerate(node.children):
                bw = branch_widths[i]
                child.x = bx + bw / 2 - child.w / 2
                child.y = y

                # Kinder des Branches sequentiell
                if child.children:
                    child_end_y = _position_nodes(
                        child.children, bx, y + child.h + NODE_PAD_Y, bw
                    )
                    max_branch_y = max(max_branch_y, child_end_y)
                else:
                    max_branch_y = max(max_branch_y, y + child.h + NODE_PAD_Y)

                bx += bw

            y = max_branch_y + NODE_PAD_Y

        elif node.children and node.shape != "diamond":
            # Sequentielle Kinder (Scope, Loop)
            y = _position_nodes(node.children, start_x, y, available_width)

    return y


# ---------------------------------------------------------------------------
# Zeichnen
# ---------------------------------------------------------------------------

def _draw_rounded_rect(painter: QPainter, rect: QRectF, radius: float, fill: QColor, border: QColor):
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    painter.fillPath(path, QBrush(fill))
    painter.setPen(QPen(border, 1.5))
    painter.drawPath(path)


def _draw_diamond(painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
    path = QPainterPath()
    cx, cy = rect.center().x(), rect.center().y()
    hw, hh = rect.width() / 2, rect.height() / 2
    path.moveTo(cx, rect.top())
    path.lineTo(rect.right(), cy)
    path.lineTo(cx, rect.bottom())
    path.lineTo(rect.left(), cy)
    path.closeSubpath()
    painter.fillPath(path, QBrush(fill))
    painter.setPen(QPen(border, 2.0))
    painter.drawPath(path)


def _draw_stadium(painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
    radius = rect.height() / 2
    _draw_rounded_rect(painter, rect, radius, fill, border)


def _draw_circle(painter: QPainter, rect: QRectF, fill: QColor, border: QColor):
    painter.setBrush(QBrush(fill))
    painter.setPen(QPen(border, 2.0))
    size = min(rect.width(), rect.height())
    cr = QRectF(rect.center().x() - size / 2, rect.center().y() - size / 2, size, size)
    painter.drawEllipse(cr)


def _draw_arrow(painter: QPainter, start: QPointF, end: QPointF, color: QColor, label: str = ""):
    """Zeichnet einen Pfeil mit optionalem Label."""
    painter.setPen(QPen(color, 1.5))
    painter.drawLine(start, end)

    # Pfeilspitze
    angle = math.atan2(end.y() - start.y(), end.x() - start.x())
    p1 = QPointF(
        end.x() - ARROW_SIZE * math.cos(angle - math.pi / 6),
        end.y() - ARROW_SIZE * math.sin(angle - math.pi / 6),
    )
    p2 = QPointF(
        end.x() - ARROW_SIZE * math.cos(angle + math.pi / 6),
        end.y() - ARROW_SIZE * math.sin(angle + math.pi / 6),
    )
    path = QPainterPath()
    path.moveTo(end)
    path.lineTo(p1)
    path.lineTo(p2)
    path.closeSubpath()
    painter.fillPath(path, QBrush(color))

    # Label
    if label:
        mid = QPointF((start.x() + end.x()) / 2, (start.y() + end.y()) / 2)
        font = QFont("Segoe UI", 8)
        painter.setFont(font)
        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance(label)
        th = fm.height()
        lr = QRectF(mid.x() - tw / 2 - 4, mid.y() - th / 2 - 2, tw + 8, th + 4)
        painter.fillRect(lr, QBrush(COLORS["label_bg"]))
        painter.setPen(QPen(COLORS["text"], 1))
        painter.drawText(lr, Qt.AlignCenter, label)


def _draw_node(painter: QPainter, node: LayoutNode):
    """Zeichnet einen einzelnen Knoten."""
    rect = QRectF(node.x, node.y, node.w, node.h)
    fill = COLORS.get(node.color_key, COLORS["action"])
    border = fill.lighter(130)

    if node.shape == "diamond":
        _draw_diamond(painter, rect, fill, border)
    elif node.shape == "stadium":
        _draw_stadium(painter, rect, fill, border)
    elif node.shape == "circle":
        _draw_circle(painter, rect, fill, border)
    else:
        _draw_rounded_rect(painter, rect, 8, fill, border)

    # Text
    painter.setPen(QPen(COLORS["text_dark"], 1))
    font = QFont("Segoe UI", FONT_SIZE, QFont.Bold)
    painter.setFont(font)

    if node.sub_label:
        # Zwei Zeilen
        top_rect = QRectF(rect.x() + 8, rect.y() + 4, rect.width() - 16, rect.height() / 2)
        bot_rect = QRectF(rect.x() + 8, rect.center().y(), rect.width() - 16, rect.height() / 2 - 4)
        painter.drawText(top_rect, Qt.AlignCenter | Qt.TextSingleLine, node.label)
        font2 = QFont("Segoe UI", FONT_SIZE - 2)
        painter.setFont(font2)
        painter.setPen(QPen(COLORS["text"].darker(120), 1))
        painter.drawText(bot_rect, Qt.AlignCenter | Qt.TextSingleLine, node.sub_label)
    else:
        text_rect = QRectF(rect.x() + 8, rect.y(), rect.width() - 16, rect.height())
        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextSingleLine, node.label)


def _draw_edges(painter: QPainter, nodes: list[LayoutNode], parent_bottom: QPointF | None = None):
    """Zeichnet Kanten zwischen Knoten."""
    prev_bottom: QPointF | None = parent_bottom

    for node in nodes:
        # Kante vom Vorgaenger
        if prev_bottom is not None:
            edge_color = COLORS["edge"]
            if node.edge_label == "Ja":
                edge_color = COLORS["edge_yes"]
            elif node.edge_label == "Nein":
                edge_color = COLORS["edge_no"]

            _draw_arrow(painter, prev_bottom, node.top, edge_color, node.edge_label)

        if node.shape == "diamond" and node.children:
            # Kanten zu Branches
            for child in node.children:
                edge_color = COLORS["edge"]
                label = child.edge_label or ""
                if label in ("Ja",):
                    edge_color = COLORS["edge_yes"]
                elif label in ("Nein",):
                    edge_color = COLORS["edge_no"]

                _draw_arrow(painter, node.bottom, child.top, edge_color, label)

                # Kinder des Branches
                if child.children:
                    _draw_edges(painter, child.children, child.bottom)

            prev_bottom = None  # Branches konvergieren implizit
        elif node.children and node.shape != "diamond":
            # Sequentielle Kinder
            _draw_edges(painter, node.children, node.bottom)
            # Letztes Kind wird Vorgaenger
            last = node.children[-1]
            while last.children:
                if last.shape == "diamond":
                    break
                last = last.children[-1]
            prev_bottom = last.bottom if last.shape != "diamond" else None
        else:
            prev_bottom = node.bottom


def _draw_all_nodes(painter: QPainter, nodes: list[LayoutNode]):
    """Zeichnet alle Knoten rekursiv."""
    for node in nodes:
        _draw_node(painter, node)
        if node.shape == "diamond" and node.children:
            for child in node.children:
                _draw_node(painter, child)
                if child.children:
                    _draw_all_nodes(painter, child.children)
        elif node.children:
            _draw_all_nodes(painter, node.children)


# ---------------------------------------------------------------------------
# Legende
# ---------------------------------------------------------------------------

def _draw_legend(painter: QPainter, x: float, y: float):
    """Zeichnet eine Farb-Legende."""
    items = [
        ("Trigger", "trigger"),
        ("Aktion", "action"),
        ("Bedingung", "condition"),
        ("Schleife", "loop"),
        ("Ja-Zweig", "branch_true"),
        ("Nein-Zweig", "branch_false"),
        ("Variable", "variable"),
        ("HTTP", "http"),
        ("Connector", "connector"),
        ("Ende", "terminate"),
    ]

    font = QFont("Segoe UI", 9)
    painter.setFont(font)
    fm = QFontMetrics(font)

    lx = x
    ly = y + 4

    # Titel
    title_font = QFont("Segoe UI", 10, QFont.Bold)
    painter.setFont(title_font)
    painter.setPen(QPen(COLORS["text"], 1))
    painter.drawText(QPointF(lx, ly + 12), "Legende")
    ly += 28
    painter.setFont(font)

    for label, color_key in items:
        color = COLORS.get(color_key, COLORS["action"])
        rect = QRectF(lx, ly, 16, 16)
        _draw_rounded_rect(painter, rect, 3, color, color.lighter(130))
        painter.setPen(QPen(COLORS["text"], 1))
        painter.drawText(QPointF(lx + 24, ly + 12), label)
        ly += 22


# ---------------------------------------------------------------------------
# Oeffentliche API
# ---------------------------------------------------------------------------

def render_flowchart(project: PAProject, scale: float = 1.0) -> QPixmap:
    """
    Rendert das Flussdiagramm eines Projekts als QPixmap.

    Args:
        project: Das PA-Projekt mit Trigger und Aktionen.
        scale: Skalierungsfaktor (1.0 = 100%).

    Returns:
        QPixmap mit dem gerenderten Diagramm.
    """
    _ensure_qapp()

    # Trigger-Node erstellen
    all_nodes: list[LayoutNode] = []
    trigger = project.trigger

    if trigger.name:
        trig_label = f"⚡ {trigger.name}"
        trig_sub = ""
        if trigger.connector:
            trig_sub = trigger.connector
        elif trigger.trigger_type:
            trig_sub = trigger.trigger_type
        trig_node = LayoutNode(
            label=trig_label[:35],
            sub_label=trig_sub[:30],
            w=NODE_W, h=NODE_H,
            color_key="trigger",
            shape="stadium",
        )
        all_nodes.append(trig_node)

    # Aktions-Knoten
    action_nodes = _build_layout_nodes(project.actions)
    all_nodes.extend(action_nodes)

    # Ende-Node
    if project.actions:
        end_node = LayoutNode(
            label="Ende", w=80, h=40,
            color_key="terminate", shape="circle",
        )
        all_nodes.append(end_node)

    if not all_nodes:
        # Leeres Diagramm
        pixmap = QPixmap(400, 200)
        pixmap.fill(COLORS["bg"])
        p = QPainter(pixmap)
        p.setPen(QPen(COLORS["text"], 1))
        p.setFont(QFont("Segoe UI", 12))
        p.drawText(QRectF(0, 0, 400, 200), Qt.AlignCenter,
                    "Keine Aktionen vorhanden.\nImportieren Sie einen Flow.")
        p.end()
        return pixmap

    # Gesamtbreite berechnen
    total_width = 0
    for node in all_nodes:
        w = _subtree_width(node)
        total_width = max(total_width, w)
    total_width = max(total_width, 400)

    # Layout berechnen
    y = _position_nodes(all_nodes, 0, 30, total_width)
    total_height = y + 40

    # Legende rechts
    legend_w = 180
    diagram_w = total_width + 40
    img_w = int((diagram_w + legend_w) * scale)
    img_h = int(max(total_height, 300) * scale)

    # QPixmap erstellen
    pixmap = QPixmap(img_w, img_h)
    pixmap.fill(COLORS["bg"])

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)

    if scale != 1.0:
        painter.scale(scale, scale)

    # Offset fuer Zentrierung
    offset_x = 20
    painter.translate(offset_x, 0)

    # Kanten zeichnen (hinter den Knoten)
    _draw_edges(painter, all_nodes)

    # Knoten zeichnen
    _draw_all_nodes(painter, all_nodes)

    # Legende
    _draw_legend(painter, total_width - 10, 20)

    painter.end()
    return pixmap


def render_flowchart_to_png(project: PAProject, output_path: Path | str, scale: float = 2.0) -> Path:
    """
    Rendert das Flussdiagramm und speichert es als PNG-Datei.

    Args:
        project: Das PA-Projekt.
        output_path: Zielpfad fuer die PNG-Datei.
        scale: Skalierungsfaktor (2.0 fuer hohe Qualitaet).

    Returns:
        Path zur PNG-Datei.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pixmap = render_flowchart(project, scale=scale)
    pixmap.save(str(output_path), "PNG")
    return output_path


def render_flowchart_to_temp_png(project: PAProject, scale: float = 2.0) -> str:
    """
    Rendert das Flussdiagramm in eine temporaere PNG-Datei.

    Returns:
        Pfad zur temporaeren PNG-Datei.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="flowchart_")
    tmp.close()
    render_flowchart_to_png(project, tmp.name, scale=scale)
    return tmp.name
