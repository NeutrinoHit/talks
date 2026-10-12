"""Regression checks for stable native sliders; no browser or render."""
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import tomllib
import unittest

HERE=Path(__file__).resolve().parent


class Elements(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ranges={};self.labels={};self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='input' and a.get('type')=='range':self.ranges[a['data-control']]=a
        if 'data-control-label' in a:self.labels[a['data-control-label']]=a


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.elements=Elements((HERE/'interactive.html').read_text())
        with (HERE/'ui.toml').open('rb') as f:self.ui=tomllib.load(f)

    def test_range_size_inherits_the_control_font_and_cannot_flex_shrink(self):
        self.assertEqual(set(self.elements.ranges),{'theta','phi','budget','sigma','group'})
        for node in self.elements.ranges.values():
            style=node['style'];layout=self.ui['layout']
            self.assertIn('font:inherit;',style)
            self.assertIn('flex:none;',style)
            self.assertIn(f'width:{layout["slider_width_em"]}em;',style)
            self.assertIn(f'height:{layout["slider_height_em"]}em;',style)

    def test_math_labels_reserve_fixed_width_and_height(self):
        self.assertEqual(set(self.elements.labels),set(self.elements.ranges))
        for key,node in self.elements.labels.items():
            width=self.ui['layout']['slider_label_width_em'][key]
            self.assertIn(f'flex:0 0 {width}em;',node['style'])
            self.assertIn(f'width:{width}em;',node['style'])
            self.assertIn('white-space:nowrap;',node['style'])
            self.assertIn('min-height:',node['style'])

    def test_math_requests_do_not_erase_visible_artwork_during_input(self):
        # Exercise the production enqueue function in isolation. The visible
        # node throws on any markup write: a frequent input must only queue
        # off-screen typesetting and retain the last completed artwork.
        source=(HERE/'interactive.js').read_text()
        start=source.index('    const applyMath=(node,tex)=>{')
        end=source.index('    let typesetting=false;',start)
        body=source[start:end]
        script="const pendingMath=new Map();"+body+"""
        const node={dataset:{formula:'old-rendered'}};
        Object.defineProperty(node,'textContent',{set(){throw Error('Visible TeX write');}});
        node.replaceChildren=()=>{throw Error('Visible markup erased');};
        for(let i=0;i<100;i++)applyMath(node,'S='+i);
        console.log(JSON.stringify({pending:pendingMath.size,latest:pendingMath.get(node),visible:node.dataset.formula}));
        """
        result=subprocess.run(['node','-e',script],text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(result.stdout),{'pending':1,'latest':'S=99','visible':'old-rendered'})


if __name__=='__main__':unittest.main()
