#!/usr/bin/env python3

import argparse
import re
import sys
import unittest

import bs4

def main():
    parser = argparse.ArgumentParser(
            description="Convert a macOS Kindle export of Notes and Highlights into something pasteable into Notion.")
    parser.add_argument("kindle_html_file", type=argparse.FileType('r'))
    parser.add_argument("notion_html_file", type=argparse.FileType('w'))
    args = parser.parse_args()


    html = args.kindle_html_file.read()
    html = clean_html(html)
    soup = bs4.BeautifulSoup(html, 'html5lib')
    clean_soup(soup)
    args.notion_html_file.write(str(soup))
    

_LOCATION_RE = re.compile(r'(Location \d+)</div>')

def clean_html(html):
    return _LOCATION_RE.sub(r'\1', html)


def clean_soup(soup):
    # Remove shitting styling that makes everything bold.
    soup.style.decompose()
    

    # Move noteText's out of their parents, distinguishing between quotes and notes.
    for note in soup.find_all(class_='noteText'):
        parent = note.parent
        is_quote = parent.get_text().startswith('Highlight')

        if is_quote:
            note.name = 'blockquote'

        parent.replace_with(note)
    

if __name__ == '__main__':
    sys.exit(main())



class HTMLTest(unittest.TestCase):
    def test_clean_html(self):
        html = """Page 59 &middot; Location 1284</div><div class='noteText'>When you feel like you"""
        expected = """Page 59 &middot; Location 1284<div class='noteText'>When you feel like you"""
        self.assertEqual(clean_html(html), expected)

    def test_clean_soup(self):
        html = """<h3 class="noteHeading">Highlight (<span class="highlight_pink">pink</span>) - Practical Advice for Delegating Effectively &gt; Page 59 · Location 1289<div class="noteText">When you are managing a team that doesn’t have a clear plan, use the details you’d want to monitor to help them create one. </div></h3>"""
        soup = bs4.BeautifulSoup(html, 'html5lib')
        text = soup.get_text()
        self.assertTrue(text.startswith("Highlight"))
        self.assertTrue(text.endswith("one. "))

        clean_soup(soup)
        text = soup.get_text()
        self.assertTrue(text.startswith("When you are"))
        self.assertTrue(text.endswith("one. "))

        self.assertIsNotNone(soup.blockquote)
