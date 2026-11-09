#!/usr/bin/env python3
"""Build the editable, self-contained profile QR banner as lossless SVG."""
import argparse
from base64 import b64encode
from html import escape
from itertools import groupby
import json
from pathlib import Path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
import qrcode

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', required=True,
                        help='Fusion Pixel 12px proportional Simplified Chinese TTF; glyphs are outlined in SVG')
    parser.add_argument('--font-index', type=int, default=0)
    args = parser.parse_args()
    config = json.loads((ROOT / 'assets/accounts/banner.json').read_text())
    font = TTFont(args.font, fontNumber=args.font_index)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    units = font['head'].unitsPerEm
    colors = config['colors']
    accounts = config['accounts']
    if len(accounts) != 4:
        raise ValueError('This banner layout requires four accounts')

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="725" viewBox="0 0 1600 725" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(config["slogan"])}</title>',
        '<desc id="desc">从左到右：小红书、视频号（二维码待补充）、微信号、即刻。李贝拉Bela的账号二维码。</desc>',
        """<defs>
          <linearGradient id="paper" x2=".9" y2="1" gradientUnits="objectBoundingBox">
            <stop stop-color="#fbe9f4"/><stop offset=".56" stop-color="#f7d9e9"/><stop offset="1" stop-color="#fff2ed"/>
          </linearGradient>
          <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M0 32V0H32" fill="none" stroke="#a44576" stroke-opacity=".16"/>
          </pattern>
        </defs>""",
        '<rect width="1600" height="725" rx="24" fill="url(#paper)"/>',
        '<rect width="1600" height="725" rx="24" fill="url(#grid)"/>',
        '<rect x="61" y="29" width="256" height="30" rx="5" fill="#fff6f9"/>',
        '<rect x="1290" y="29" width="249" height="30" rx="5" fill="#fff6f9"/>',
        '<rect x="1310" y="39" width="9" height="9" rx="1" fill="#5dbbce"/>',
    ]
    for filename, x, y, size, angle in (
        ("disk.png", 157, 79, 113, -13),
        ("disc.png", 1343, 79, 112, 12),
    ):
        sticker = b64encode((ROOT / "assets/y2k" / filename).read_bytes()).decode("ascii")
        center_x, center_y = x + size / 2, y + size / 2
        svg.append(
            f'<image x="{x}" y="{y}" width="{size}" height="{size}" '
            f'transform="rotate({angle} {center_x} {center_y})" href="data:image/png;base64,{sticker}"/>'
        )

    def text(value, center, baseline, size, color, tracking=0, weight=0):
        scale = size / units
        names = []
        for ch in value:
            if ord(ch) not in cmap:
                raise ValueError(f'Font is missing character: {ch}')
            names.append(cmap[ord(ch)])
        width = sum(glyphs[name].width for name in names) * scale + tracking * (len(names) - 1)
        x = center - width / 2
        stroke = f' stroke="{color}" stroke-width="{weight / scale:.3f}"' if weight else ""
        svg.append(f'<g aria-label="{escape(value)}"{stroke}>')
        for name in names:
            pen = SVGPathPen(glyphs)
            glyphs[name].draw(pen)
            path = pen.getCommands()
            if path:
                svg.append(f'<path fill="{color}" transform="translate({x:.4f} {baseline}) scale({scale:.6f} {-scale:.6f})" d="{path}"/>')
            x += glyphs[name].width * scale + tracking
        svg.append('</g>')

    text("BELA.ZINE / CONTACT", 189, 50, 20, "#a32962")
    text("SCAN MODE / ON", 1422, 50, 20, "#a32962")
    text(config["slogan"], 800, 157, 72, "#35142a", tracking=5, weight=2.4)
    for index, account in enumerate(accounts):
        center = 260 + index * 360
        left, top, side = center - 150, 280, 300
        text(account['platform'], center, 260, 36, colors['text'])
        svg.append(f'<rect x="{left + 4}" y="{top + 6}" width="{side}" height="{side}" rx="12" fill="#b65b8e" opacity=".19"/>')
        svg.append(f'<rect x="{left}" y="{top}" width="{side}" height="{side}" rx="12" fill="white" stroke="{colors["border"]}" stroke-opacity="0.75" stroke-width="2"/>')
        payload = account['qr_payload']
        if payload:
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
            qr.add_data(payload)
            qr.make(fit=True)
            matrix = qr.get_matrix()
            size = len(matrix)
            # Keep an integer module grid, then apply a single vector scale.
            cells = []
            for row, values in enumerate(matrix):
                col = 0
                for dark, run in groupby(values):
                    length = sum(1 for _ in run)
                    if dark:
                        cells.append(f'M{col} {row}h{length}v1h-{length}z')
                    col += length
            scale = 280 / size
            svg.append(f'<path fill="{colors["qr"]}" shape-rendering="crispEdges" transform="translate({left+10} {top+10}) scale({scale:.8f})" d="{"".join(cells)}"/>')
        else:
            svg.append(f'<rect x="{left+26}" y="{top+26}" width="248" height="248" rx="8" fill="{colors["background"]}" stroke="{colors["border"]}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="8 8"/>')
            text('二维码待补充', center, top + 161, 27, colors['muted'])
        text(account['name'], center, 630, 29, colors['text'])
        text(account['caption'], center, 672, 24, colors['muted'])
    svg.append('</svg>')
    output = ROOT / 'assets/follow-y2k-v3.svg'
    output.write_text('\n'.join(svg) + '\n')
    print(output)


if __name__ == '__main__':
    main()
