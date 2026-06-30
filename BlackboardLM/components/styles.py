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
            
            #loading {{
                --loader-bg: {AppState.theme["background"]};
                position: fixed;
                left: 0;
                right: 0;
                top: 0;
                bottom: 0;
                z-index: 9999;
                background-color: var(--loader-bg, #f5efe0);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: opacity 0.5s ease;
            }}
            #loading.cat-done {{
                opacity: 0;
                pointer-events: none;
            }}
            .cat {{
                position: relative;
                display: block;
                width: 15em;
                height: 100%;
                font-size: 10px;
                margin: auto;
                animation: 2.74s linear infinite loading-cat;
            }}
            .cat * {{ box-sizing: content-box; }}
            .cat .head,
            .cat .foot,
            .cat .body,
            .cat .paw {{
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                left: 0;
                margin: auto;
                border-radius: 50%;
                width: 15em;
                height: 15em;
            }}
            .cat .body {{
                background-image: radial-gradient(
                    transparent 0%, transparent 35%,
                    rgb(56,60,75) 35%, rgb(56,60,75) 39%,
                    rgb(237,166,93) 39%, rgb(237,166,93) 46%,
                    rgb(242,192,137) 46%, rgb(242,192,137) 60%,
                    rgb(237,166,93) 60%, rgb(237,166,93) 67%,
                    rgb(56,60,75) 67%, rgb(56,60,75) 100%
                );
                animation: 2.74s linear infinite body;
            }}
            .cat .head:before,
            .cat .foot:before {{
                background-image: radial-gradient(
                    transparent 0%, transparent 35%,
                    rgb(56,60,75) 35%, rgb(56,60,75) 39%,
                    rgb(237,166,93) 39%, rgb(237,166,93) 67%,
                    rgb(56,60,75) 67%, rgb(56,60,75) 100%
                );
            }}
            .cat .head:before {{
                content: '';
                width: 100%;
                height: 100%;
                position: absolute;
                border-radius: 50%;
                clip-path: polygon(100% 20%, 50% 50%, 70% -10%);
                -webkit-clip-path: polygon(100% 20%, 50% 50%, 70% -10%);
            }}
            .cat .head:after {{
                content: '';
                width: 4.125em;
                height: 2.5em;
                position: absolute;
                top: 0.8125em;
                right: 3.9375em;
                background-image:
                    linear-gradient(var(--loader-bg, #f5efe0) 65%, transparent 65%),
                    radial-gradient(var(--loader-bg, #f5efe0) 51%, rgb(56,60,75) 55%, rgb(56,60,75) 68%, transparent 70%);
                transform: rotate(-66deg);
            }}
            .cat .head .face {{
                width: 5em;
                height: 3.75em;
                left: 9.0625em;
                top: 1.8125em;
                position: absolute;
                transform: rotate(-47deg);
                background:
                    radial-gradient(circle, rgb(242,192,137) 0%, rgb(242,192,137) 23%, transparent 23%) -0.1875em 1.0625em no-repeat,
                    radial-gradient(circle, rgb(56,60,75) 0%, rgb(56,60,75) 6%, transparent 6%) 0.75em -0.75em no-repeat,
                    radial-gradient(circle, rgb(56,60,75) 0%, rgb(56,60,75) 6%, transparent 6%) -0.75em -0.75em no-repeat,
                    radial-gradient(rgb(237,166,93) 0%, rgb(237,166,93) 15%, transparent 15%) 0 -0.6875em no-repeat,
                    radial-gradient(circle, transparent 5%, rgb(56,60,75) 5%, rgb(56,60,75) 10%, transparent 10%) -0.1875em -0.3125em no-repeat,
                    radial-gradient(circle, transparent 5%, rgb(56,60,75) 5%, rgb(56,60,75) 10%, transparent 10%) 0.1875em -0.3125em no-repeat,
                    radial-gradient(circle, rgb(237,166,93) 45%, transparent 45%) 0 -0.1875em,
                    linear-gradient(transparent 35%, rgb(56,60,75) 35%, rgb(56,60,75) 41%, transparent 41%, transparent 44%, rgb(56,60,75) 44%, rgb(56,60,75) 50%, transparent 50%, transparent 53%, rgb(56,60,75) 53%, rgb(56,60,75) 59%, transparent 59%);
            }}
            .cat .foot {{
                animation: 2.74s linear infinite foot;
            }}
            .cat .foot:before,
            .cat .foot:after {{
                content: '';
                width: 100%;
                height: 100%;
                position: absolute;
            }}
            .cat .foot:before {{
                border-radius: 50%;
                clip-path: polygon(50% 50%, 0% 50%, 0% 25%);
                -webkit-clip-path: polygon(50% 50%, 0% 50%, 0% 25%);
            }}
            .cat .foot .tummy-end {{
                width: 1.5em;
                height: 1.5em;
                position: absolute;
                border-radius: 50%;
                background-color: rgb(242,192,137);
                left: 1.1875em;
                top: 6.5625em;
            }}
            .cat .foot .bottom {{
                width: 2.1875em;
                height: 0.9375em;
                position: absolute;
                top: 4.875em;
                left: 0.75em;
                border: 0.375em solid rgb(56,60,75);
                border-bottom: 0;
                border-radius: 50%;
                transform: rotate(21deg);
                background: rgb(237,166,93);
            }}
            .cat .hands,
            .cat .legs,
            .cat .foot:after {{
                width: 0.625em;
                height: 1.5625em;
                position: absolute;
                border: 0.375em solid rgb(56,60,75);
                background-color: rgb(237,166,93);
            }}
            .cat .hands {{
                border-top: 0;
                border-radius: 0 0 0.75em 0.75em;
            }}
            .cat .hands.left {{
                top: 4.3em;
                left: 13.1875em;
                transform: rotate(-20deg);
            }}
            .cat .hands.right {{
                top: 5.125em;
                left: 10.975em;
                transform: rotate(-25deg);
            }}
            .cat .legs {{
                border-bottom: 0;
                border-radius: 0.75em 0.75em 0 0;
            }}
            .cat .legs.left {{
                top: 4.0625em;
                left: 3.125em;
                transform: rotate(25deg);
            }}
            .cat .legs.right {{
                top: 3.3125em;
                left: 0.75em;
                transform: rotate(22deg);
            }}
            .cat .foot:after {{
                width: 0.9em;
                height: 2.5em;
                top: 2.625em;
                left: 2.5em;
                z-index: -1;
                transform: rotate(25deg);
                background-color: rgb(198,130,59);
                border-bottom: 0;
                border-radius: 0.75em 0.75em 0 0;
            }}
            .cat:hover {{
                animation-play-state: paused;
            }}
            .cat:hover .body,
            .cat:hover .foot {{
                animation-play-state: paused;
            }}
            .cat:active {{
                animation-play-state: running;
            }}
            .cat:active .body,
            .cat:active .foot {{
                animation-play-state: running;
            }}
            @keyframes loading-cat {{
                0% {{ transform: rotate(0deg); }}
                10% {{ transform: rotate(-80deg); }}
                20% {{ transform: rotate(-180deg); }}
                40% {{ transform: rotate(-245deg); }}
                50% {{ transform: rotate(-250deg); }}
                68% {{ transform: rotate(-300deg); }}
                90% {{ transform: rotate(-560deg); }}
                100% {{ transform: rotate(-720deg); }}
            }}
            @keyframes body {{
                0% {{ clip-path: polygon(50% 50%, 0% 50%, 0% 100%, 100% 100%, 100% 20%); }}
                10% {{ clip-path: polygon(50% 50%, 30% 120%, 50% 100%, 100% 100%, 100% 20%); }}
                20% {{ clip-path: polygon(50% 50%, 100% 90%, 120% 90%, 100% 100%, 100% 20%); }}
                40% {{ clip-path: polygon(50% 50%, 100% 45%, 120% 45%, 120% 50%, 100% 20%); }}
                50% {{ clip-path: polygon(50% 50%, 100% 45%, 120% 45%, 120% 50%, 100% 20%); }}
                65% {{ clip-path: polygon(50% 50%, 100% 65%, 120% 65%, 120% 50%, 100% 20%); }}
                80% {{ clip-path: polygon(50% 50%, 75% 130%, 120% 65%, 120% 50%, 100% 20%); }}
                90% {{ clip-path: polygon(50% 50%, -20% 110%, 50% 120%, 100% 100%, 100% 20%); }}
                100% {{ clip-path: polygon(50% 50%, 0% 50%, 0% 100%, 100% 100%, 100% 20%); }}
            }}
            @keyframes foot {{
                0% {{ transform: rotate(-10deg); }}
                10% {{ transform: rotate(-100deg); }}
                20% {{ transform: rotate(-145deg); }}
                35% {{ transform: rotate(-190deg); }}
                50% {{ transform: rotate(-195deg); }}
                70% {{ transform: rotate(-165deg); }}
                100% {{ transform: rotate(-10deg); }}
            }}
            
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
        rx.script("""
        (function initCatLoader() {
            var _loader = document.getElementById('loading');
            if (!_loader) { setTimeout(initCatLoader, 200); return; }
            var _done = false;
            function _hide() {
                if (_done) return;
                _done = true;
                _loader.classList.add('cat-done');
            }
            _loader.addEventListener('click', _hide);
            setTimeout(_hide, 15000);
            function _watchGraph() {
                var _dataEl = document.getElementById('graph-data');
                if (!_dataEl) { setTimeout(_watchGraph, 200); return; }
                if ((_dataEl.textContent || '').length > 4) { _hide(); return; }
                new MutationObserver(function() {
                    var _t = _dataEl.textContent || '';
                    if (_t.length > 4) _hide();
                }).observe(_dataEl, {characterData: true, childList: true, subtree: true});
            }
            _watchGraph();
        })();
        """),
    )
