"""Obsidian trade journal writer."""

import os
from datetime import date
from pathlib import Path

VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "/mnt/e/workspace/obsidian-vault")
TRADE_DIR = "Fleeting Notes/trades"


def write_trade_journal(
    ticker: str,
    direction: str,
    entry_date: date,
    entry_price: float,
    entry_reason: str,
    target_price: float | None = None,
    stop_loss: float | None = None,
    indicators: dict | None = None,
    tags: list[str] | None = None,
) -> str:
    """Write a trade journal entry to Obsidian vault.

    Returns the file path of the created note.
    """
    trade_dir = Path(VAULT_PATH) / TRADE_DIR
    trade_dir.mkdir(parents=True, exist_ok=True)

    filename = f"trade-{entry_date.isoformat()}-{ticker.replace('.', '_')}.md"
    filepath = trade_dir / filename

    all_tags = ["trade", direction]
    if tags:
        all_tags.extend(tags)
    tags_str = ", ".join(f'"{t}"' for t in all_tags)

    lines = [
        "---",
        f'id: "trade-{entry_date.isoformat()}-{ticker}"',
        "type: trade-journal",
        f'ticker: "{ticker}"',
        f"direction: {direction}",
        f"entry_date: {entry_date.isoformat()}",
        f"entry_price: {entry_price}",
    ]

    if target_price is not None:
        lines.append(f"target_price: {target_price}")
    if stop_loss is not None:
        lines.append(f"stop_loss: {stop_loss}")

    lines.extend([
        "status: open",
        f"tags: [{tags_str}]",
        "---",
        "",
        f"# {ticker} {direction.upper()} @{entry_price}",
        "",
        "## エントリー根拠",
        entry_reason or "(未記入)",
        "",
    ])

    if indicators:
        lines.extend([
            "## テクニカル状況（エントリー時点）",
        ])
        for key, value in indicators.items():
            if key != "date":
                lines.append(f"- {key}: {value}")
        lines.append("")

    lines.extend([
        "## 振り返り（クローズ後に追記）",
        "- P/L: ",
        "- 学び: ",
        "",
    ])

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return str(filepath)


def update_trade_close(
    ticker: str,
    entry_date: date,
    exit_date: date,
    exit_price: float,
    exit_reason: str,
    pnl: float,
    pnl_pct: float,
) -> str | None:
    """Update an existing trade journal with close information."""
    trade_dir = Path(VAULT_PATH) / TRADE_DIR
    filename = f"trade-{entry_date.isoformat()}-{ticker.replace('.', '_')}.md"
    filepath = trade_dir / filename

    if not filepath.exists():
        return None

    content = filepath.read_text(encoding="utf-8")

    # Update frontmatter status
    content = content.replace("status: open", f"status: closed")

    # Update retrospective section
    old_retro = "- P/L: \n- 学び: "
    pnl_sign = "+" if pnl >= 0 else ""
    new_retro = (
        f"- P/L: {pnl_sign}{pnl:.0f}円 ({pnl_sign}{pnl_pct:.1f}%)\n"
        f"- 決済日: {exit_date.isoformat()} @{exit_price}\n"
        f"- 決済理由: {exit_reason}\n"
        f"- 学び: "
    )
    content = content.replace(old_retro, new_retro)

    filepath.write_text(content, encoding="utf-8")
    return str(filepath)
