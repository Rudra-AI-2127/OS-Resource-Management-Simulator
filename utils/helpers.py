"""
Presentation formatting and calculation helper utilities.
Provides clean ASCII table formatting and textual Gantt chart rendering.
"""

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class TimelineSegment:
    """Represents a continuous execution interval on the CPU timeline."""
    pid: str
    start_time: int
    end_time: int

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time


def format_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """
    Renders an aligned ASCII table with borders.
    """
    if not headers:
        return ""

    str_headers = [str(h) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]

    col_widths = [len(h) for h in str_headers]
    for row in str_rows:
        for idx, cell in enumerate(row):
            if idx < len(col_widths):
                col_widths[idx] = max(col_widths[idx], len(cell))
            else:
                col_widths.append(len(cell))

    # Pad headers if row has more columns
    while len(str_headers) < len(col_widths):
        str_headers.append("")
        col_widths[len(str_headers) - 1] = max(col_widths[len(str_headers) - 1], 5)

    sep_border = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_line = "| " + " | ".join(h.center(col_widths[i]) for i, h in enumerate(str_headers)) + " |"

    body_lines = []
    for row in str_rows:
        cells = []
        for i, w in enumerate(col_widths):
            val = row[i] if i < len(row) else ""
            cells.append(val.ljust(w))
        body_lines.append("| " + " | ".join(cells) + " |")

    table_lines = [sep_border, header_line, sep_border]
    table_lines.extend(body_lines)
    table_lines.append(sep_border)

    return "\n".join(table_lines)


def render_gantt_ascii(segments: Sequence[TimelineSegment]) -> str:
    """
    Renders an ASCII text-based Gantt chart from execution timeline segments.
    Example:
    +-------+-----+---------------+
    |  P1   | P2  |      P3       |
    +-------+-----+---------------+
    0       5     8              16
    """
    if not segments:
        return "No execution segments recorded."

    boxes = []
    time_points = [str(segments[0].start_time)]

    for seg in segments:
        label = seg.pid
        box_width = max(len(label) + 2, max(4, int(seg.duration * 2)))
        boxes.append((label, box_width, seg.end_time))

    top_border = "+" + "+".join("-" * w for _, w, _ in boxes) + "+"
    middle_row = "|" + "|".join(label.center(w) for label, w, _ in boxes) + "|"
    bot_border = top_border

    time_row = str(segments[0].start_time)
    for _, w, end_t in boxes:
        time_str = str(end_t)
        spacing = w + 1 - len(time_str)
        if spacing > 0:
            time_row += " " * spacing + time_str
        else:
            time_row += " " + time_str

    return f"{top_border}\n{middle_row}\n{bot_border}\n{time_row}"
