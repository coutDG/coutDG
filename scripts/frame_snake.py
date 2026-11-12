"""Add the nautical background without changing the generated snake animation."""
from pathlib import Path
import xml.etree.ElementTree as ET

path = Path(__file__).resolve().parents[1] / 'assets/contribution-snake.svg'
ET.parse(path)  # Validate before modifying; preserve original CSS and namespaces.
svg = path.read_text()
start = svg.index('<svg')
end = svg.index('>', start) + 1
svg = svg[:end] + '<rect width="100%" height="100%" rx="8" fill="#0b1719"/>' + svg[end:]
ET.fromstring(svg)
path.write_text(svg)
