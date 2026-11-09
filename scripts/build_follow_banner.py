#!/usr/bin/env python3
"""Build the editable, self-contained profile QR banner as lossless SVG."""
import argparse
from base64 import b64encode
from html import escape
import json
from pathlib import Path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
import qrcode

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', default='/System/Library/Fonts/Hiragino Sans GB.ttc',
                        help='Chinese TTF/OTF/TTC font; glyphs are outlined in SVG')
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
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="680" viewBox="0 0 1600 680" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(config["slogan"])}</title>',
        '<desc id="desc">从左到右：小红书、视频号（二维码待补充）、微信号、即刻。李贝拉Bela的账号二维码。</desc>',
        """<defs>
          <linearGradient id="paper" x2=".9" y2="1" gradientUnits="objectBoundingBox">
            <stop stop-color="#fbe9f4"/><stop offset=".56" stop-color="#f7d9e9"/><stop offset="1" stop-color="#e9e7fa"/>
          </linearGradient>
          <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M0 32V0H32" fill="none" stroke="#a44576" stroke-opacity=".16"/>
          </pattern>
          <pattern id="scan" width="8" height="8" patternUnits="userSpaceOnUse">
            <path d="M0 7.5H8" stroke="#f8bbde" stroke-opacity=".20"/>
          </pattern>
          <linearGradient id="lcd" x2="0" y2="1" gradientUnits="objectBoundingBox">
            <stop stop-color="#fff3f9"/><stop offset=".48" stop-color="#ffc3e6"/>
            <stop offset=".53" stop-color="#f585c8"/><stop offset="1" stop-color="#ffacd9"/>
          </linearGradient>
        </defs>""",
        '<rect width="1600" height="680" rx="24" fill="url(#paper)"/>',
        '<rect width="1600" height="680" rx="24" fill="url(#grid)"/>',
        f'<rect x="15" y="15" width="1570" height="650" rx="24" fill="none" stroke="{colors["border"]}" stroke-width="2"/>',
        '<path d="M28 58V29h34m1476 0h34v29M28 622v29h34m1476 0h34v-29" fill="none" stroke="#652c55" stroke-width="2"/>',
        '<rect x="61" y="29" width="256" height="30" rx="3" fill="#3d1735"/>',
        '<rect x="1290" y="29" width="249" height="30" rx="3" fill="#3d1735"/>',
        '<rect x="1310" y="39" width="9" height="9" rx="1" fill="#88eaff"/>',
        '<path d="M347 67h906l23 23v64l-23 23H347l-23-23V90Z" fill="#ca74a3" opacity=".55" transform="translate(0 5)"/>',
        '<path d="M347 67h906l23 23v64l-23 23H347l-23-23V90Z" fill="#34132e" stroke="#9f487f" stroke-width="3"/>',
        '<path d="M347 67h906l23 23v64l-23 23H347l-23-23V90Z" fill="url(#scan)"/>',
        '<path d="M355 93h34m-34 0v31m890-31h-34m34 0v31" fill="none" stroke="#ffc8e9" stroke-opacity=".65" stroke-width="2"/>',
    ]
    for filename, x, y, size, angle in (
        ("disk.png", 157, 64, 113, -13),
        ("disc.png", 1343, 64, 112, 12),
    ):
        sticker = b64encode((ROOT / "assets/y2k" / filename).read_bytes()).decode("ascii")
        center_x, center_y = x + size / 2, y + size / 2
        svg.append(
            f'<image x="{x}" y="{y}" width="{size}" height="{size}" '
            f'transform="rotate({angle} {center_x} {center_y})" href="data:image/png;base64,{sticker}"/>'
        )

    def text(value, center, baseline, size, color):
        scale = size / units
        names = []
        for ch in value:
            if ord(ch) not in cmap:
                raise ValueError(f'Font is missing character: {ch}')
            names.append(cmap[ord(ch)])
        width = sum(glyphs[name].width for name in names) * scale
        x = center - width / 2
        svg.append(f'<g aria-label="{escape(value)}">')
        for name in names:
            pen = SVGPathPen(glyphs)
            glyphs[name].draw(pen)
            path = pen.getCommands()
            if path:
                svg.append(f'<path fill="{color}" transform="translate({x:.4f} {baseline}) scale({scale:.6f} {-scale:.6f})" d="{path}"/>')
            x += glyphs[name].width * scale
        svg.append('</g>')

    text("BELA.ZINE / CONTACT", 189, 50, 17, "#ffe6f5")
    text("SCAN MODE / ON", 1422, 50, 17, "#ffe6f5")
    text(config["slogan"], 802, 144, 66, "#ac4281")
    text(config["slogan"], 800, 140, 66, "url(#lcd)")
    for index, account in enumerate(accounts):
        center = 260 + index * 360
        left, top, side = center - 150, 235, 300
        text(account['platform'], center, 217, 36, colors['text'])
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
                for col, dark in enumerate(values):
                    if dark:
                        cells.append(f'M{col} {row}h1v1h-1z')
            scale = 280 / size
            svg.append(f'<path fill="{colors["qr"]}" shape-rendering="crispEdges" transform="translate({left+10} {top+10}) scale({scale:.8f})" d="{" ".join(cells)}"/>')
        else:
            svg.append(f'<rect x="{left+26}" y="{top+26}" width="248" height="248" rx="8" fill="{colors["background"]}" stroke="{colors["border"]}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="8 8"/>')
            text('二维码待补充', center, top + 161, 27, colors['muted'])
        text(account['name'], center, 585, 29, colors['text'])
        text(account['caption'], center, 627, 21, colors['muted'])
    svg.append('</svg>')
    output = ROOT / 'assets/follow-y2k.svg'
    output.write_text('\n'.join(svg) + '\n')
    print(output)


if __name__ == '__main__':
    main()
