"""Add the nautical background without changing the generated snake animation."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def frame(svg):
    root = ET.fromstring(svg)
    x, y, width, height = map(float, root.attrib['viewBox'].split())
    # Replace our existing frame on repeat runs; preserve the generated animation.
    svg = re.sub(r'<!-- PIRATE-FRAME:START -->.*?<!-- PIRATE-FRAME:END -->', '', svg, flags=re.S)
    svg = svg.replace('<rect width="100%" height="100%" rx="8" fill="#0b1719"/>', '')
    waves = ''
    for offset in (18, 30):
        baseline = y + height - offset
        path = f'M{x:g} {baseline:g}'
        for i in range(8):
            mid = x + (i + .5) * width / 8
            right = x + (i + 1) * width / 8
            path += f'Q{mid:g} {baseline-14:g} {right:g} {baseline:g}'
        waves += f'<path d="{path}"/>'
    decoration = f'''<!-- PIRATE-FRAME:START -->
<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" rx="10" fill="#0b1719"/>
<g fill="none" stroke="#c7a15a" opacity=".14">{waves}</g>
<rect x="{x+1.5:g}" y="{y+1.5:g}" width="{width-3:g}" height="{height-3:g}" rx="10" fill="none" stroke="#c7a15a" stroke-width="2"/>
<!-- PIRATE-FRAME:END -->'''
    end = svg.index('>', svg.index('<svg')) + 1
    svg = svg[:end] + decoration + svg[end:]
    ET.fromstring(svg)
    return svg


if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'assets/contribution-snake.svg'
    path.write_text(frame(path.read_text()))
