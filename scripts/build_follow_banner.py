#!/usr/bin/env python3
"""Build the editable, self-contained profile QR banner as lossless SVG."""
import argparse
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

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="680" viewBox="0 0 1600 680" role="img" aria-labelledby="title desc">',
           f'<title id="title">{escape(config["slogan"])}</title>',
           '<desc id="desc">从左到右：小红书、视频号（二维码待补充）、微信号、即刻。李贝拉Bela的账号二维码。</desc>',
           f'<rect width="1600" height="680" rx="24" fill="{colors["background"]}"/>',
           f'<rect x="15" y="15" width="1570" height="650" rx="24" fill="none" stroke="{colors["border"]}" stroke-width="2"/>']

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

    text(config['slogan'], 800, 115, 62, colors['text'])
    svg.append(f'<path d="M538 147 Q800 135 1062 147" fill="none" stroke="{colors["accent"]}" stroke-width="8" stroke-linecap="round"/>')
    for index, account in enumerate(accounts):
        center = 260 + index * 360
        left, top, side = center - 150, 235, 300
        text(account['platform'], center, 217, 36, colors['text'])
        svg.append(f'<rect x="{left}" y="{top}" width="{side}" height="{side}" rx="12" fill="white" stroke="{colors["border"]}" stroke-opacity="0.65" stroke-width="2"/>')
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
    output = ROOT / 'assets/follow.svg'
    output.write_text('\n'.join(svg) + '\n')
    print(output)


if __name__ == '__main__':
    main()
