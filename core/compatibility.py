"""Read-only official wiki lookup. Web text is advice, never executable instructions."""
import re
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser
from urllib.parse import quote, unquote
from core.game_rules import match_recipe, normalize_title

WIKI = 'https://github.com/optiscaler/OptiScaler/wiki/'
RAW = 'https://raw.githubusercontent.com/wiki/optiscaler/OptiScaler/'


class WikiBody(HTMLParser):
    """Extract only the wiki article, excluding navigation and executable markup."""
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts = []
        self.cell = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.depth:
                self.depth += 1
            elif 'markdown-body' in dict(attrs).get('class', '').split():
                self.depth = 1
        if not self.depth:
            return
        if tag == 'tr':
            self.parts.append('\n| ')
        elif tag in ('td', 'th'):
            self.cell = True
        elif tag in ('p', 'li', 'br'):
            self.parts.append(' ' if self.cell else '\n')

    def handle_endtag(self, tag):
        if not self.depth:
            return
        if tag == 'div':
            self.depth -= 1
        elif tag in ('td', 'th'):
            self.parts.append(' | ')
            self.cell = False
        elif tag == 'tr':
            self.parts.append('\n')

    def handle_data(self, data):
        if self.depth:
            self.parts.append(re.sub(r'\s+', ' ', data))

    def text(self):
        return '\n'.join(re.sub(r'[ \t]+', ' ', line).strip() for line in ''.join(self.parts).splitlines() if line.strip())


class CompatibilityResearch:
    _cache = {}

    @staticmethod
    def normalize(value):
        return normalize_title(value)

    @classmethod
    def fetch(cls, page):
        cached = cls._cache.get(page)
        if cached and time.time() - cached[0] < 3600:
            return cached[1]
        request = urllib.request.Request(RAW + quote(page, safe='') + '.md',
                                         headers={'User-Agent': 'OptiScaler-XeSS-GUI'})
        html = False
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = response.read(2_000_001)
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                raise
            # Many detailed entries use AsciiDoc, not Markdown. GitHub renders both.
            request = urllib.request.Request(WIKI + quote(page, safe=''), headers={'User-Agent': 'OptiScaler-XeSS-GUI'})
            with urllib.request.urlopen(request, timeout=10) as response:
                data = response.read(2_000_001)
            html = True
        if len(data) > 2_000_000:
            raise ValueError('Compatibility page exceeds size limit.')
        text = data.decode('utf-8')
        if html:
            parser = WikiBody()
            parser.feed(text)
            text = parser.text()
            if not text:
                raise ValueError('Wiki article body was unavailable.')
        cls._cache[page] = (time.time(), text)
        return text

    @classmethod
    def lookup(cls, names):
        result = {'status': 'unmatched', 'sources': [WIKI + 'Compatibility-List', WIKI + 'Manual-Installation'],
                  'checked_at': time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()),
                  'notes': 'No exact title match. Confirm the game title; compatibility remains unknown.'}
        try:
            recipe = match_recipe(names)
            if recipe:
                names = [*names, recipe['title']]
            table = cls.fetch('Compatibility-List')
            targets = {cls.normalize(n) for n in names if n}
            matches = []
            for line in table.splitlines():
                cells = line.strip().strip('|').split('|')
                if len(cells) < 3:
                    continue
                title = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', cells[0]).strip(' *')
                if cls.normalize(title) in targets:
                    matches.append((title, line, cells[0]))
            if len(matches) != 1:
                return result
            title, row, first = matches[0]
            result.update(status='matched', title=title, notes=row.strip(), row=row.strip())
            links = re.findall(r'\[[^]]+\]\(([^)]+)\)', first)
            for link in links[:1]:
                if link.startswith(WIKI):
                    page = unquote(link[len(WIKI):])
                elif not any(c in link for c in '/\\:#?') and '..' not in link:
                    page = unquote(link)
                else:
                    continue
                result['sources'].insert(0, WIKI + quote(page, safe=''))
                try:
                    detail = cls.fetch(page)[:14000]
                    result['notes'] += '\n\n' + detail
                    result['detail'] = detail
                    result['detail_status'] = 'available'
                    result['fields'] = parse_fields(detail)
                except Exception as exc:
                    result['detail_status'] = 'unavailable'
                    result['notes'] += '\nDetailed page unavailable: ' + str(exc)
            return result
        except Exception as exc:
            result.update(status='offline', notes='Online lookup unavailable: ' + str(exc) + '\nLocal evidence only; compatibility is unverified.')
            return result


def parse_fields(detail):
    fields = {}
    for line in detail.splitlines():
        cells = line.strip().strip('|').split('|')
        if len(cells) == 2:
            key = cells[0].strip(' *').casefold()
            fields[key] = cells[1].strip(' *` ')
    return fields


def suggested_controls(support, research):
    """Only local input evidence and an unambiguous proxy in the matched row."""
    controls = {'xess_quality': 'User Defined'}
    if support:
        if support['fsr']:
            controls['starting_upscaler'] = 'FSR'
        elif support['dlss']:
            controls['starting_upscaler'] = 'DLSS'
        if support['dlssg']:
            controls['fg_input'] = 'dlssg'
    if research and research.get('status') == 'matched':
        filename = research.get('fields', {}).get('filename', '').strip('` ')
        if re.fullmatch(r'(?:dxgi|version|winmm|nvngx|d3d12|dbghelp|wininet|winhttp)\.dll', filename, re.I):
            controls['hook_method'] = filename.lower()
            return controls
        row = research.get('row', '')
        hooks = set(re.findall(r'\b(?:dxgi|version|winmm|nvngx|d3d12|dbghelp|wininet|winhttp)\.dll\b', row, re.I))
        if re.search(r"\b(?:not|avoid|don't|never|without)\b", row, re.I):
            hooks.clear()
        if len(hooks) == 1:
            controls['hook_method'] = hooks.pop().lower()
    return controls
