"""
flowchart_renderer.py – QPainter-basierter Flussdiagramm-Renderer.

Erzeugt visuelle Darstellungen von Power Automate Flows als Bilder.
Verwendet QPainter fuer plattformunabhaengiges Rendering ohne
externe Abhaengigkeiten.
"""
from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QImage, QPainter, QColor, QPen, QBrush, QFont, QFontMetrics,
    QPainterPath, QPolygonF, QLinearGradient, QPixmap,
)
from PySide6.QtWidgets import QWidget, QScrollArea, QLabel, QVBoxLayout

from models import PAProject, FlowAction, FlowTrigger


# ---------------------------------------------------------------------------
# Layout-Konstanten
# ---------------------------------------------------------------------------
NODE_MIN_W = 180
NODE_MAX_W = 280
NODE_H = 44
V_GAP = 40
H_GAP = 50
PADDING = 50
ARROW_SZ = 8
FONT_SIZE = 10
FONT_FAMILY = "Segoe UI"

# ---------------------------------------------------------------------------
# Farb-Definitionen
# ---------------------------------------------------------------------------
COLORS = {
    "trigger":      ("#3A6FD8", "#5B8DEF"),
    "action":       ("#1E2A42", "#5B8DEF"),
    "connector":    ("#1A3A5C", "#5B8DEF"),
    "condition":    ("#C48F20", "#E0A526"),
    "loop":         ("#7B1FA2", "#9C27B0"),
    "scope":        ("#2E3B4E", "#5B8DEF"),
    "branch_true":  ("#2E7D32", "#4CAF50"),
    "branch_false": ("#C62828", "#EF5B5B"),
    "variable":     ("#00695C", "#00897B"),
    "data":         ("#37474F", "#546E7A"),
    "http":         ("#E64A19", "#FF7043"),
    "terminate":    ("#C62828", "#EF5B5B"),
    "end":          ("#424242", "#757575"),
}

BG_COLOR = "#0F1117"
TEXT_COLOR = "#FFFFFF"
ARROW_COLOR = "#5B8DEF"
LABEL_COLOR = "#B0B4C8"


# ---------------------------------------------------------------------------
# Layout-Knoten
# ---------------------------------------------------------------------------
@dataclass
class LayoutNode:
    """Ein Knoten mit berechneter Position."""
    x: float = 0.0
    y: float = 0.0
    width: float = NODE_MIN_W
    height: float = NODE_H
    text: str = ""
    sub_text: str = ""
    node_type: str = "action"
    shape: str = "rect"   # rect, diamond, stadium, hexagon, rounded

    @property
    def cx(self) -> float:
        return self.x + self.width / 2

    @property
    def cy(self) -> float:
        return self.y + self.height / 2

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height


@dataclass
class Edge:
    """Eine Kante zwischen zwei Knoten."""
    src: LayoutNode
    dst: LayoutNode
    label: str = ""


# ---------------------------------------------------------------------------
# Typ-Erkennung
# ---------------------------------------------------------------------------
def _get_node_type(action: FlowAction) -> str:
    at = (action.action_type or "").lower()
    if at in ("if", "condition", "switch"):
        return "condition"
    if at in ("foreach", "until"):
        return "loop"
    if at == "scope":
        return "scope"
    if at == "branch_true":
        return "branch_true"
    if at in ("branch_false", "switch_default"):
        return "branch_false"
    if at == "switch_case":
        return "branch_true"
    if at in ("terminate", "response"):
        return "terminate"
    if at in ("initializevariable", "setvariable", "incrementvariable",
              "decrementvariable", "appendtoarrayvariable", "appendtostringvariable"):
        return "variable"
    if at in ("compose", "parsejson", "select", "filter", "query"):
        return "data"
    if at in ("http", "httpwebhook"):
        return "http"
    if action.connector:
        return "connector"
    return "action"


_SHAPE_MAP = {
    "trigger": "stadium", "condition": "diamond", "loop": "hexagon",
    "scope": "rounded", "branch_true": "stadium", "branch_false": "stadium",
    "terminate": "stadium", "end": "stadium",
}


def _get_shape(ntype: str) -> str:
    return _SHAPE_MAP.get(ntype, "rect")


# ---------------------------------------------------------------------------
# Layout-Engine
# ---------------------------------------------------------------------------
class FlowchartLayoutEngine:
    """Berechnet Positionen aller Knoten im Flussdiagramm."""

    def __init__(self):
        self._font = QFont(FONT_FAMILY, FONT_SIZE)
        self._fm = QFontMetrics(self._font)
        self.nodes: list[LayoutNode] = []
        self.edges: list[Edge] = []

    def layout(self, project: PAProject) -> tuple[list[LayoutNode], list[Edge], int, int]:
        """Berechnet das Layout und gibt (nodes, edges, breite, hoehe) zurueck."""
        self.nodes.clear()
        self.edges.clear()

        y = PADDING

        # Trigger
        trigger_node = None
        if project.trigger and project.trigger.name:
            t = project.trigger
            sub = t.connector or t.trigger_type or ""
            w = self._text_width(t.name)
            trigger_node = LayoutNode(
                text=f"⚡ {t.name}", sub_text=sub,
                node_type="trigger", shape="stadium",
                width=w, height=NODE_H,
            )
            self.nodes.append(trigger_node)
            y += NODE_H + V_GAP

        # Aktionen
        prev = [trigger_node] if trigger_node else []
        end_nodes = self._layout_actions(project.actions, prev, y, 0.0)

        # Ende-Knoten
        end_node = LayoutNode(
            text="Ende", node_type="end", shape="stadium",
            width=100, height=36,
        )
        self.nodes.append(end_node)
        for en in end_nodes:
            self.edges.append(Edge(en, end_node))

        # Bounds berechnen & zentrieren
        if not self.nodes:
            return [], [], 400, 200

        min_x = min(n.x for n in self.nodes)
        offset_x = PADDING - min_x
        for n in self.nodes:
            n.x += offset_x

        # Ende-Knoten positionieren
        others = [n for n in self.nodes if n is not end_node]
        max_y = max(n.bottom for n in others)
        end_node.y = max_y + V_GAP
        if end_nodes:
            avg_cx = sum(n.cx for n in end_nodes) / len(end_nodes)
            end_node.x = avg_cx + offset_x - end_node.width / 2
        else:
            end_node.x = PADDING

        total_w = int(max(n.x + n.width for n in self.nodes) + PADDING)
        total_h = int(end_node.bottom + PADDING)

        return self.nodes, self.edges, max(total_w, 400), max(total_h, 200)

    # ---------------------------------------------------------------
    def _text_width(self, text: str) -> float:
        w = self._fm.horizontalAdvance(text) + 28
        return max(NODE_MIN_W, min(NODE_MAX_W, w))

    def _measure_width(self, actions: list[FlowAction]) -> float:
        """Schaetzt die benoetigte Breite eines Aktions-Subtrees."""
        if not actions:
            return NODE_MIN_W
        max_w = NODE_MIN_W
        for a in actions:
            if self._is_branching(a):
                branches = self._get_branches(a)
                branch_w = sum(self._measure_width(b_children) for b_children in branches.values())
                branch_w += H_GAP * max(0, len(branches) - 1)
                max_w = max(max_w, branch_w)
            elif a.children:
                max_w = max(max_w, self._measure_width(a.children))
            else:
                max_w = max(max_w, self._text_width(a.name))
        return max_w

    def _is_branching(self, action: FlowAction) -> bool:
        at = (action.action_type or "").lower()
        if at in ("if", "condition", "switch"):
            return True
        return any(
            c.action_type in ("Branch_True", "Branch_False", "Switch_Case", "Switch_Default")
            for c in action.children
        )

    def _get_branches(self, action: FlowAction) -> dict[str, list[FlowAction]]:
        """Gibt Branching-Kinder gruppiert zurueck."""
        branches: dict[str, list[FlowAction]] = {}
        other: list[FlowAction] = []
        for c in action.children:
            if c.action_type == "Branch_True":
                branches.setdefault("Ja", []).append(c)
            elif c.action_type == "Branch_False":
                branches.setdefault("Nein", []).append(c)
            elif c.action_type == "Switch_Case":
                label = c.name.split("Case: ")[-1] if "Case: " in c.name else c.name
                branches.setdefault(label, []).append(c)
            elif c.action_type == "Switch_Default":
                branches.setdefault("Default", []).append(c)
            else:
                other.append(c)
        if not branches and other:
            branches[""] = other
        return branches

    def _layout_actions(
        self,
        actions: list[FlowAction],
        prev: list[LayoutNode],
        start_y: float,
        center_x: float,
    ) -> list[LayoutNode]:
        """Layout-Berechnung (rekursiv). Gibt die letzten Knoten zurueck."""
        cur_prev = list(prev)
        cur_y = start_y

        for action in actions:
            ntype = _get_node_type(action)
            shape = _get_shape(ntype)
            text = action.name
            sub = action.connector or ""
            w = self._text_width(text)

            if self._is_branching(action):
                # ---- Bedingung / Switch ----
                h = NODE_H + 10 if shape == "diamond" else NODE_H
                cond = LayoutNode(
                    x=center_x - w / 2, y=cur_y,
                    width=w, height=h,
                    text=text, sub_text=sub,
                    node_type=ntype, shape=shape,
                )
                self.nodes.append(cond)
                for pn in cur_prev:
                    self.edges.append(Edge(pn, cond))

                cur_y += h + V_GAP

                branches = self._get_branches(action)
                n_branches = len(branches)

                # Breiten der Zweige berechnen
                branch_widths: dict[str, float] = {}
                for label, b_group in branches.items():
                    all_children = []
                    for bg in b_group:
                        all_children.extend(bg.children)
                    branch_widths[label] = max(NODE_MIN_W, self._measure_width(all_children))

                total_w = sum(branch_widths.values()) + H_GAP * max(0, n_branches - 1)

                # Zweige nebeneinander platzieren
                branch_end_nodes: list[LayoutNode] = []
                x_cursor = center_x - total_w / 2

                for label, b_group in branches.items():
                    bw = branch_widths[label]
                    branch_cx = x_cursor + bw / 2

                    for bg in b_group:
                        # Branch-Header
                        is_true = bg.action_type in ("Branch_True", "Switch_Case")
                        b_ntype = "branch_true" if is_true else "branch_false"
                        if bg.action_type == "Switch_Default":
                            b_ntype = "branch_false"

                        display_label = label or bg.name
                        bh_w = self._text_width(display_label)
                        bh_w = max(80, min(160, bh_w))
                        bh = LayoutNode(
                            x=branch_cx - bh_w / 2, y=cur_y,
                            width=bh_w, height=32,
                            text=display_label,
                            node_type=b_ntype, shape="stadium",
                        )
                        self.nodes.append(bh)
                        self.edges.append(Edge(cond, bh, label))

                        if bg.children:
                            child_ends = self._layout_actions(
                                bg.children, [bh],
                                cur_y + 32 + V_GAP, branch_cx,
                            )
                            branch_end_nodes.extend(child_ends)
                        else:
                            branch_end_nodes.append(bh)

                    x_cursor += bw + H_GAP

                if branch_end_nodes:
                    cur_y = max(n.bottom for n in branch_end_nodes) + V_GAP
                    cur_prev = branch_end_nodes
                else:
                    cur_prev = [cond]
                    cur_y += V_GAP

            elif ntype in ("loop", "scope") and action.children:
                # ---- Schleife / Scope mit Kindern ----
                node = LayoutNode(
                    x=center_x - w / 2, y=cur_y,
                    width=w, height=NODE_H,
                    text=text, sub_text=sub,
                    node_type=ntype, shape=shape,
                )
                self.nodes.append(node)
                for pn in cur_prev:
                    self.edges.append(Edge(pn, node))
                cur_y += NODE_H + V_GAP

                child_ends = self._layout_actions(
                    action.children, [node], cur_y, center_x,
                )
                if child_ends:
                    cur_y = max(n.bottom for n in child_ends) + V_GAP
                    cur_prev = child_ends
                else:
                    cur_prev = [node]

            else:
                # ---- Einfache Aktion ----
                node = LayoutNode(
                    x=center_x - w / 2, y=cur_y,
                    width=w, height=NODE_H,
                    text=text, sub_text=sub,
                    node_type=ntype, shape=shape,
                )
                self.nodes.append(node)
                for pn in cur_prev:
                    self.edges.append(Edge(pn, node))
                cur_prev = [node]
                cur_y += NODE_H + V_GAP

        return cur_prev


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------
class FlowchartRenderer:
    """Rendert ein Flussdiagramm als QImage."""

    def render(self, project: PAProject, scale: float = 1.0) -> QImage:
        engine = FlowchartLayoutEngine()
        nodes, edges, w, h = engine.layout(project)

        img_w = max(int(w * scale), 400)
        img_h = max(int(h * scale), 200)

        image = QImage(img_w, img_h, QImage.Format.Format_ARGB32)
        image.fill(QColor(BG_COLOR))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        if scale != 1.0:
            painter.scale(scale, scale)

        # Kanten zuerst (hinter den Knoten)
        for edge in edges:
            self._draw_edge(painter, edge)

        # Knoten
        for node in nodes:
            self._draw_node(painter, node)

        painter.end()
        return image

    def save_png(self, project: PAProject, path: str | Path, scale: float = 1.5) -> Path:
        """Speichert das Flussdiagramm als PNG."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        image = self.render(project, scale)
        image.save(str(path), "PNG")
        return path

    def render_pixmap(self, project: PAProject, scale: float = 1.0) -> QPixmap:
        """Rendert als QPixmap (fuer Anzeige in QLabel)."""
        return QPixmap.fromImage(self.render(project, scale))

    # ---- Kanten zeichnen ----
    def _draw_edge(self, p: QPainter, edge: Edge):
        pen = QPen(QColor(ARROW_COLOR))
        pen.setWidth(2)
        p.setPen(pen)

        x1, y1 = edge.src.cx, edge.src.bottom
        x2, y2 = edge.dst.cx, edge.dst.top

        if abs(x1 - x2) < 3:
            # Gerade Linie
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        else:
            # L-foermiger Verbinder
            mid_y = (y1 + y2) / 2
            p.drawLine(QPointF(x1, y1), QPointF(x1, mid_y))
            p.drawLine(QPointF(x1, mid_y), QPointF(x2, mid_y))
            p.drawLine(QPointF(x2, mid_y), QPointF(x2, y2))

        # Pfeilspitze
        self._draw_arrowhead(p, x2, y2)

        # Kanten-Label
        if edge.label:
            lbl_font = QFont(FONT_FAMILY, 8)
            lbl_font.setBold(True)
            p.setFont(lbl_font)
            p.setPen(QColor(LABEL_COLOR))
            lx = (x1 + x2) / 2
            ly = y1 + 14
            fm = QFontMetrics(lbl_font)
            tw = fm.horizontalAdvance(edge.label)
            p.drawText(QPointF(lx - tw / 2, ly), edge.label)

    def _draw_arrowhead(self, p: QPainter, x: float, y: float):
        p.setBrush(QBrush(QColor(ARROW_COLOR)))
        p.setPen(Qt.PenStyle.NoPen)
        poly = QPolygonF([
            QPointF(x, y),
            QPointF(x - ARROW_SZ / 2, y - ARROW_SZ),
            QPointF(x + ARROW_SZ / 2, y - ARROW_SZ),
        ])
        p.drawPolygon(poly)

    # ---- Knoten zeichnen ----
    def _draw_node(self, p: QPainter, node: LayoutNode):
        fill, border = COLORS.get(node.node_type, COLORS["action"])
        fill_c = QColor(fill)
        border_c = QColor(border)

        rect = QRectF(node.x, node.y, node.width, node.height)

        pen = QPen(border_c, 2)
        p.setPen(pen)

        # Gradient-Fill
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, fill_c.lighter(115))
        grad.setColorAt(1, fill_c)
        p.setBrush(QBrush(grad))

        if node.shape == "diamond":
            self._draw_diamond(p, rect)
        elif node.shape == "stadium":
            p.drawRoundedRect(rect, node.height / 2, node.height / 2)
        elif node.shape == "hexagon":
            self._draw_hexagon(p, rect)
        elif node.shape == "rounded":
            pen.setStyle(Qt.PenStyle.DashLine)
            p.setPen(pen)
            p.drawRoundedRect(rect, 10, 10)
        else:
            p.drawRoundedRect(rect, 6, 6)

        # Text
        self._draw_text(p, node, rect)

    def _draw_text(self, p: QPainter, node: LayoutNode, rect: QRectF):
        p.setPen(QColor(TEXT_COLOR))
        font = QFont(FONT_FAMILY, FONT_SIZE)
        font.setBold(True)
        p.setFont(font)

        fm = QFontMetrics(font)
        avail = node.width - 16

        if node.sub_text:
            # Zwei Zeilen
            main = fm.elidedText(node.text, Qt.TextElideMode.ElideRight, int(avail))
            r1 = QRectF(rect.x() + 8, rect.y() + 3, avail, rect.height() / 2)
            p.drawText(r1, Qt.AlignmentFlag.AlignCenter, main)

            sub_font = QFont(FONT_FAMILY, 7)
            p.setFont(sub_font)
            p.setPen(QColor("#A0A4B8"))
            sfm = QFontMetrics(sub_font)
            sub = sfm.elidedText(f"[{node.sub_text}]", Qt.TextElideMode.ElideRight, int(avail))
            r2 = QRectF(rect.x() + 8, rect.y() + rect.height() / 2 - 2, avail, rect.height() / 2)
            p.drawText(r2, Qt.AlignmentFlag.AlignCenter, sub)
        else:
            main = fm.elidedText(node.text, Qt.TextElideMode.ElideRight, int(avail))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, main)

    def _draw_diamond(self, p: QPainter, rect: QRectF):
        cx, cy = rect.center().x(), rect.center().y()
        poly = QPolygonF([
            QPointF(cx, rect.top()),
            QPointF(rect.right(), cy),
            QPointF(cx, rect.bottom()),
            QPointF(rect.left(), cy),
        ])
        p.drawPolygon(poly)

    def _draw_hexagon(self, p: QPainter, rect: QRectF):
        inset = 14
        poly = QPolygonF([
            QPointF(rect.left() + inset, rect.top()),
            QPointF(rect.right() - inset, rect.top()),
            QPointF(rect.right(), rect.center().y()),
            QPointF(rect.right() - inset, rect.bottom()),
            QPointF(rect.left() + inset, rect.bottom()),
            QPointF(rect.left(), rect.center().y()),
        ])
        p.drawPolygon(poly)


# ---------------------------------------------------------------------------
# Preview-Widget
# ---------------------------------------------------------------------------
class FlowchartWidget(QScrollArea):
    """Widget mit scrollbarer Flussdiagramm-Vorschau."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("background-color: #0F1117; border: none;")
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background-color: #0F1117;")
        self.setWidget(self._label)
        self._renderer = FlowchartRenderer()

    def update_flowchart(self, project: PAProject, scale: float = 1.0):
        """Aktualisiert die Anzeige mit dem aktuellen Projekt."""
        if not project.actions and not (project.trigger and project.trigger.name):
            self._label.setText("Kein Flow geladen – importieren Sie einen Flow, um das Diagramm zu sehen.")
            self._label.setStyleSheet(
                "background-color: #0F1117; color: #6B6F82; font-size: 14px; padding: 40px;"
            )
            return

        pixmap = self._renderer.render_pixmap(project, scale)
        self._label.setPixmap(pixmap)
        self._label.adjustSize()


# ---------------------------------------------------------------------------
# Convenience-Funktionen
# ---------------------------------------------------------------------------
def render_flowchart_image(project: PAProject, scale: float = 1.5) -> QImage:
    """Rendert ein Flussdiagramm als QImage."""
    return FlowchartRenderer().render(project, scale)


def save_flowchart_png(project: PAProject, path: str | Path, scale: float = 1.5) -> Path:
    """Speichert ein Flussdiagramm als PNG-Datei."""
    return FlowchartRenderer().save_png(project, path, scale)


def get_flowchart_temp_png(project: PAProject, scale: float = 1.5) -> str:
    """Rendert in eine temporaere PNG-Datei und gibt den Pfad zurueck."""
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.close()
    save_flowchart_png(project, tmp.name, scale)
    return tmp.name
