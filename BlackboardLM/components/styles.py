import reflex as rx
from BlackboardLM.state import AppState
import BlackboardLM.theme as _theme

def global_styles() -> rx.Component:
    return rx.fragment(
        rx.script("""
        (function(){var _s=document.createElement('script');_s.src='https://unpkg.com/cytoscape@3.30.4/dist/cytoscape.min.js';_s.async=true;document.head.appendChild(_s);})();
        """),
        rx.html(f"""
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="{AppState.theme["google_fonts_url"]}" rel="stylesheet">
        <style>
            *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
            html, body {{
                font-family: {AppState.theme["font_body"]};
                background: {AppState.theme["background"]};
                color: {AppState.theme["text_primary"]};
                overflow: hidden;
                height: 100dvh;
                -webkit-overflow-scrolling: touch;
            }}
            {AppState.theme["css_extra"]}
            
            div[role="button"] {{
                border: none !important;
                background: transparent !important;
                border-radius: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
                width: fit-content !important;
                display: flex !important;
            }}
            
            .rx-Upload {{ padding: 0px !important; border: none !important; }}
            .rx-Upload > div {{ padding: 0px 16px !important; }}
            ::-webkit-scrollbar {{ width: 6px; height: 3px; }}
            ::-webkit-scrollbar-track {{ background: transparent; }}
            ::-webkit-scrollbar-thumb {{
                background: {AppState.theme["text_muted"]};
                border-radius: 3px;
            }}
            
            @media (max-width: 640px) {{
                .header-subtitle {{ display: none; }}
                .header-heading {{ font-size: 18px !important; }}
                .star-chart-box {{ height: 80px !important; }}
                .header-bar {{ padding: 10px 14px !important; }}
                .doc-shelf-scroll > div {{ gap: 8px !important; }}
                .doc-card {{ min-width: 150px !important; max-width: 150px !important; }}
                .message-row {{ padding: 2px 8px !important; }}
                .input-container {{ margin: 8px 12px !important; }}
            }}
            
            ::placeholder {{ color: {AppState.theme["text_secondary"]}; opacity: 0.8; }}
            ::selection {{ background: {AppState.theme["primary"]}; color: {AppState.theme["background"]}; }}
            textarea::selection {{ background: {AppState.theme["primary"]}; color: {AppState.theme["background"]}; }}
        </style>
        """),
        rx.script("""
        (function initScroll() {
            var vp = document.querySelector('[data-radix-scroll-area-viewport]');
            if (!vp) { setTimeout(initScroll, 200); return; }
            var _auto = false;
            vp.addEventListener('wheel', function(e) { if (e.deltaY < 0) _auto = false; });
            vp.addEventListener('touchmove', function() { _auto = false; });
            new MutationObserver(function(muts) {
                for (var i = 0; i < muts.length; i++) {
                    var added = muts[i].addedNodes;
                    for (var j = 0; j < added.length; j++) {
                        if (added[j].nodeType === 1 && added[j].querySelector && added[j].querySelector('[data-radix-scroll-area-viewport] .rt-Spinner, .rt-Spinner')) {
                            _auto = true;
                        }
                    }
                }
            }).observe(vp, {childList: true, subtree: true});
            setInterval(function() {
                if (_auto) vp.scrollTop = vp.scrollHeight;
            }, 80);
        })();
        """),
        rx.script("""
        document.addEventListener('keydown', function(e) {
            if (e.target.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                var form = e.target.closest('form');
                if (form) form.requestSubmit();
            }
        });
        
        document.addEventListener('input', function(e) {
            if (e.target.tagName === 'TEXTAREA') {
                e.target.style.height = 'auto';
                var lineH = 24;
                var pad = 16;
                var maxH = lineH * 5 + pad;
                var newH = Math.min(e.target.scrollHeight, maxH);
                e.target.style.height = newH + 'px';
                e.target.style.overflowY = e.target.scrollHeight > maxH ? 'auto' : 'hidden';
            }
        });
        document.addEventListener('click', function(e) {
            var btn = e.target.closest('.doc-scroll-left') || e.target.closest('.doc-scroll-right');
            if (!btn) return;
            var shelf = document.querySelector('.doc-shelf-scroll');
            if (!shelf) return;
            var dir = btn.classList.contains('doc-scroll-left') ? -200 : 200;
            shelf.scrollBy({left: dir, behavior: 'smooth'});
        });
        """),
        rx.script("""
        (function initCyGraph() {
            if (typeof cytoscape === 'undefined') {
                setTimeout(initCyGraph, 200);
                return;
            }
            var _cy = null;
            var _lastHash = '';
            var _typeColors = {
                person: '#e07050', organization: '#5090d0', location: '#50b870',
                event: '#c080e0', concept: '#e0b840', work: '#60c0c0',
                geo: '#50b870', time: '#c080e0', other: '#909090'
            };
            function _nodeColor(d) {
                var t = (d.entity_type || '').toLowerCase();
                if (_typeColors[t]) return _typeColors[t];
                for (var k in _typeColors) {
                    if (t.indexOf(k) !== -1 || k.indexOf(t) !== -1) return _typeColors[k];
                }
                var h = 0;
                for (var i = 0; i < t.length; i++) { h = t.charCodeAt(i) + ((h << 5) - h); }
                return 'hsl(' + (Math.abs(h) % 360) + ', 50%, 55%)';
            }
            function _labelColor() {
                var el = document.getElementById('cy-star-chart');
                if (!el) return '#efe0c4';
                return getComputedStyle(el).getPropertyValue('--cy-label-color') || '#efe0c4';
            }
            function _edgeLineColor() {
                var el = document.getElementById('cy-star-chart');
                if (!el) return 'rgba(212,168,67,0.3)';
                return (getComputedStyle(el).getPropertyValue('--cy-edge-color') || 'rgba(212,168,67,0.3)').trim();
            }
            function _outlineColor() {
                var el = document.getElementById('cy-star-chart');
                if (!el) return 'rgba(0,0,0,0.5)';
                return (getComputedStyle(el).getPropertyValue('--cy-outline-color') || 'rgba(0,0,0,0.5)').trim();
            }
            function _build() {
                var dataEl = document.getElementById('graph-data');
                var container = document.getElementById('cy-star-chart');
                if (!dataEl || !container) return;
                var data;
                try { data = JSON.parse(dataEl.textContent); } catch(e) { return; }
                if (!data || !data.nodes || !data.nodes.length) {
                    if (_cy) { _cy.destroy(); _cy = null; }
                    return;
                }
                var tip = document.getElementById('cy-tooltip');
                if (!tip) {
                    tip = document.createElement('div');
                    tip.id = 'cy-tooltip';
                    tip.style.cssText = 'position:absolute;display:none;background:rgba(20,18,16,0.92);color:#efe0c4;padding:4px 10px;border-radius:6px;font-size:12px;pointer-events:none;z-index:9999;max-width:320px;word-break:break-all;white-space:normal;';
                    container.appendChild(tip);
                }
                var elements = [];
                for (var i = 0; i < data.nodes.length; i++) {
                    var n = data.nodes[i];
                    elements.push({ data: { id: n.id, label: n.id, entity_type: n.entity_type || '', degree: n.degree || 0, description: n.description || '' }});
                }
                for (var i = 0; i < data.edges.length; i++) {
                    var e = data.edges[i];
                    elements.push({ data: { id: e.source + '__' + e.target + '__' + i, source: e.source, target: e.target, weight: e.weight || 1, keywords: e.keywords || '' }});
                }
                if (_cy) {
                    _cy.elements().remove();
                    _cy.add(elements);
                } else {
                    _cy = cytoscape({
                        container: container,
                        elements: elements,
                        style: [
                            { selector: 'node', style: { 'background-color': function(ele) { return _nodeColor(ele.data()); }, 'label': 'data(label)', 'font-size': '8px', 'color': _labelColor(), 'text-outline-color': _outlineColor(), 'text-outline-width': 1.5, 'text-valign': 'center', 'text-halign': 'center', 'text-wrap': 'ellipsis', 'text-max-width': '70px', 'width': function(ele) { return 8 + Math.min(ele.data('degree'), 20) * 0.7; }, 'height': function(ele) { return 8 + Math.min(ele.data('degree'), 20) * 0.7; } }},
                            { selector: 'edge', style: { 'width': function(ele) { return 0.5 + Math.min(ele.data('weight') || 1, 5) * 0.6; }, 'line-color': _edgeLineColor(), 'curve-style': 'bezier', 'opacity': 0.4 }}
                        ],
                        layout: { name: 'concentric', animate: false, concentric: function(node) { return node.degree(true); }, minNodeSpacing: 15 },
                        minZoom: 0.3,
                        maxZoom: 3,
                        userZoomingEnabled: true,
                        userPanningEnabled: true,
                        autoungrabify: true,
                        autounselectify: true,
                        boxSelectionEnabled: false,
                    });
                    var _tip = tip;
                    _cy.on('mouseover', 'node', function(evt) {
                        var node = evt.target;
                        var hood = node.closedNeighborhood();
                        _cy.elements().not(hood).style('opacity', 0.2);
                        hood.style('opacity', 1);
                        var label = node.data('label') || '';
                        var desc = node.data('description') || '';
                        var html = '<b>' + label + '</b>';
                        if (desc) html += '<br><span style="font-size:10px;opacity:0.7">' + desc + '</span>';
                        _tip.innerHTML = html;
                        _tip.style.display = 'block';
                    });
                    _cy.on('mousemove', 'node', function(evt) {
                        var rect = container.getBoundingClientRect();
                        _tip.style.left = (evt.originalEvent.clientX - rect.left + 14) + 'px';
                        _tip.style.top = (evt.originalEvent.clientY - rect.top - 10) + 'px';
                    });
                    _cy.on('mouseout', 'node', function() {
                        _cy.elements().style('opacity', '');
                        _tip.style.display = 'none';
                    });
                    _cy.on('dblclick', function(evt) {
                        if (evt.target === _cy) { _cy.fit(undefined, 15); }
                    });
                }
                _cy.fit(undefined, 15);
                var layout = _cy.layout({ name: 'concentric', animate: false, concentric: function(node) { return node.degree(true); }, minNodeSpacing: 15 });
                layout.run();
            }
            setInterval(function() {
                var el = document.getElementById('graph-data');
                if (!el) return;
                var h = el.textContent;
                if (h !== _lastHash) { _lastHash = h; _build(); }
            }, 400);
            _build();
        })();
        """),
    )
