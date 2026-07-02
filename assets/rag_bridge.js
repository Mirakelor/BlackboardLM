(function () {
  console.log('[rag_bridge] Script loaded');

  let _worker = null;
  let _ready = false;
  let _readyCallbacks = [];
  let _lastDocCounter = '';
  let _lastQueryCounter = '';
  let _lastResetCounter = '';
  let _lastConfigHash = '';
  let _statusBar = null;
  let _statusText = null;
  let _statusSpinner = null;
  let _statusBarFill = null;

  let _themePrimary = '#d4838f';
  let _themeBg = '#fffaf2';
  let _themeText = '#5c4a3a';
  let _themeSurface = '#fffaf2';
  let _themeMuted = '#b5a898';

  function _readThemeColors() {
    const _el = document.getElementById('rag-theme-colors');
    if (!_el) return;
    const _parts = (_el.textContent || '').split('|');
    if (_parts.length >= 5) {
      _themePrimary = _parts[0];
      _themeBg = _parts[1];
      _themeText = _parts[2];
      _themeSurface = _parts[3];
      _themeMuted = _parts[4];
    }
  }

  function _applyTheme() {
    _readThemeColors();
    if (!_statusBar) return;
    _statusBar.style.background = _themeSurface + 'e0';
    _statusBar.style.color = _themeText;
    if (_statusSpinner) {
      _statusSpinner.style.borderTopColor = _themePrimary;
      _statusSpinner.style.borderColor = _themeMuted + '40';
      _statusSpinner.style.borderTopColor = _themePrimary;
    }
    if (_statusBarFill) {
      _statusBarFill.style.background = _themePrimary;
    }
  }

  function _initStatusDom() {
    _statusBar = document.getElementById('rag-status-bar');
    _statusText = document.getElementById('rag-status-text');
    _statusSpinner = document.getElementById('rag-status-spinner');
    _statusBarFill = document.getElementById('rag-status-bar-fill');
    _applyTheme();
    console.log('[rag_bridge] Status DOM elements:', {
      bar: !!_statusBar,
      text: !!_statusText,
      spinner: !!_statusSpinner,
      fill: !!_statusBarFill,
    });
  }

  function _showStatus(msg, progress, isError) {
    console.log('[rag_bridge] _showStatus:', msg, 'progress:', progress, 'isError:', isError);
    if (!_statusBar) _initStatusDom();
    if (!_statusBar) {
      console.error('[rag_bridge] _showStatus FAILED: no #rag-status-bar element');
      return;
    }
    _applyTheme();
    _statusBar.style.display = 'flex';
    if (_statusSpinner) _statusSpinner.style.display = 'inline-block';
    if (_statusText) {
      _statusText.textContent = msg;
      _statusText.style.color = isError ? '#c04040' : '';
    }
    if (_statusBarFill) {
      if (progress !== undefined) {
        _statusBarFill.style.display = 'block';
        _statusBarFill.style.width = progress + '%';
      } else {
        _statusBarFill.style.display = 'none';
      }
    }
    const _closeBtn = document.getElementById('rag-status-close');
    if (_closeBtn) _closeBtn.style.display = isError ? 'inline' : 'none';
  }

  function _hideStatus() {
    console.log('[rag_bridge] _hideStatus');
    if (!_statusBar) _initStatusDom();
    if (!_statusBar) return;
    _statusBar.style.display = 'none';
  }

  function _onReady(_cb) {
    if (_ready) { _cb(); return; }
    _readyCallbacks.push(_cb);
  }

  function _setReady() {
    console.log('[rag_bridge] Worker ready, flushing', _readyCallbacks.length, 'callbacks');
    _ready = true;
    const _cbs = _readyCallbacks;
    _readyCallbacks = [];
    for (let _i = 0; _i < _cbs.length; _i++) _cbs[_i]();
  }

  function _getAddEvents() {
    const _reflex = window.__reflex;
    if (_reflex && _reflex['$/utils/context'] && _reflex['$/utils/context'].addEvents) {
      return _reflex['$/utils/context'].addEvents;
    }
    return null;
  }

  function _getReflexEvent() {
    const _reflex = window.__reflex;
    if (_reflex && _reflex['$/utils/state'] && _reflex['$/utils/state'].ReflexEvent) {
      return _reflex['$/utils/state'].ReflexEvent;
    }
    return null;
  }

  function _event(_name, _payload) {
    const _ReflexEvent = _getReflexEvent();
    if (!_ReflexEvent) return null;
    return _ReflexEvent(_name, _payload || {}, {});
  }

  let _eventCount = 0;
  function _sendEvent(_name, _payload) {
    const _addEvents = _getAddEvents();
    if (!_addEvents) {
      console.warn('[rag_bridge] _sendEvent SKIP (no addEvents):', _name);
      return false;
    }
    const _evt = _event(_name, _payload);
    if (_evt) {
      _eventCount++;
      if (_eventCount <= 5) console.log('[rag_bridge] _sendEvent #' + _eventCount + ':', _name, _payload);
      _addEvents([_evt]);
      return true;
    }
    return false;
  }

  function _initWorker() {
    console.log('[rag_bridge] _initWorker start');
    if (_worker) { console.log('[rag_bridge] Worker already exists'); return; }
    try {
      _worker = new Worker('/rag.worker.js', { type: 'module' });
      console.log('[rag_bridge] Worker created');
    } catch (_e) {
      console.error('[rag_bridge] Worker creation FAILED:', _e.message);
      _showStatus('Failed to start RAG engine: ' + _e.message, undefined, true);
      return;
    }

    _worker.onmessage = (_e) => {
      const { type } = _e.data;
      const _data = _e.data;
      console.log('[rag_bridge] Worker message:', type, _data);

      if (type === 'ready') {
        _setReady();
        _hideStatus();
        _sendEvent('reflex___state____state.blackboard_lm___state____app_state.on_rag_worker_ready', {});
        if (_data.hasData) {
          _worker.postMessage({ type: 'graph' });
        }
        return;
      }
      if (type === 'init_progress') {
        const _pct = _data.total > 0 ? Math.round(_data.loaded * 100 / _data.total) : 0;
        _showStatus('Loading embedding model: ' + _pct + '%', _pct, false);
        return;
      }
      if (type === 'progress') {
        const _pct = _data.total > 0 ? Math.round(_data.ready * 100 / _data.total) : 0;
        _showStatus('Indexing document: chunk ' + _data.ready + '/' + _data.total, _pct, false);
        return;
      }

      if (type === 'insert_done') {
        _hideStatus();
        _sendEvent('reflex___state____state.blackboard_lm___state____app_state.on_rag_insert_done', {
          graph_json: JSON.stringify(_data.graph || { nodes: [], edges: [] })
        });
        return;
      }
      if (type === 'chunk') {
        _sendEvent('reflex___state____state.blackboard_lm___state____app_state.on_chat_chunk', {
          chunk: _data.text
        });
        return;
      }
      if (type === 'done') {
        _sendEvent('reflex___state____state.blackboard_lm___state____app_state.on_chat_done', {});
        return;
      }
      if (type === 'graph') {
        _sendEvent('reflex___state____state.blackboard_lm___state____app_state.on_rag_graph_update', {
          graph_json: JSON.stringify({ nodes: _data.nodes || [], edges: _data.edges || [] })
        });
        return;
      }
      if (type === 'reset_done') return;
      if (type === 'config_set') return;
      if (type === 'error') {
        console.error('[rag_bridge] Worker error:', _data.message);
        _showStatus(_data.message, undefined, true);
        _sendEvent('reflex___state____state.blackboard_lm___state____app_state.on_rag_error', {
          error: _data.message
        });
        return;
      }
    };

    _worker.onerror = (_e) => {
      console.error('[rag_bridge] Worker onerror:', _e.message);
      _showStatus('RAG engine error: ' + _e.message, undefined, true);
    };

    const _configEl = document.getElementById('rag-llm-config');
    console.log('[rag_bridge] Config element found:', !!_configEl);
    if (_configEl) {
      try {
        const _cfg = JSON.parse(_configEl.textContent);
        delete _cfg._configChanged;
        _lastConfigHash = JSON.stringify(_cfg);
        console.log('[rag_bridge] Sending config to worker:', _cfg);
        _worker.postMessage({ type: 'set_config', data: _cfg });
      } catch (_e) {
        console.error('[rag_bridge] Config parse error:', _e.message);
      }
    }

    console.log('[rag_bridge] Sending init to worker');
    _worker.postMessage({ type: 'init' });
  }

  function _waitForDOM(_cb) {
    if (document.getElementById('rag-status-bar') && window.__reflex) {
      _cb();
      return;
    }
    let _tries = 0;
    const _timer = setInterval(function () {
      _tries++;
      if (document.getElementById('rag-status-bar') && window.__reflex) {
        console.log('[rag_bridge] DOM ready after', _tries, 'tries');
        clearInterval(_timer);
        _cb();
        return;
      }
      if (_tries > 200) {
        console.error('[rag_bridge] DOM not ready after 200 tries, starting anyway');
        clearInterval(_timer);
        _cb();
      }
    }, 100);
  }

  function _checkDocSignal() {
    const _counterEl = document.getElementById('rag-doc-counter');
    if (!_counterEl) return;
    const _val = _counterEl.textContent || '';
    if (_val === _lastDocCounter || !_val || _val === '0') return;
    console.log('[rag_bridge] Doc signal changed:', _lastDocCounter, '->', _val);
    _lastDocCounter = _val;
    const _textEl = document.getElementById('rag-doc-text');
    if (!_textEl) return;
    const _text = _textEl.textContent || '';
    if (!_text) return;
    _onReady(function () {
      console.log('[rag_bridge] Sending insert to worker, text length:', _text.length);
      _worker.postMessage({ type: 'insert', data: { text: _text } });
    });
  }

  function _checkQuerySignal() {
    const _counterEl = document.getElementById('rag-query-counter');
    if (!_counterEl) return;
    const _val = _counterEl.textContent || '';
    if (_val === _lastQueryCounter || !_val || _val === '0') return;
    console.log('[rag_bridge] Query signal changed:', _lastQueryCounter, '->', _val);
    _lastQueryCounter = _val;
    const _paramsEl = document.getElementById('rag-query-params');
    if (!_paramsEl) return;
    try {
      const _params = JSON.parse(_paramsEl.textContent || '{}');
      _onReady(function () {
        console.log('[rag_bridge] Sending query to worker:', _params.question?.slice(0, 50));
        _worker.postMessage({ type: 'query', data: _params });
      });
    } catch (_e) {
      console.log('[rag_bridge] Query params parse error:', _e.message);
    }
  }

  function _checkResetSignal() {
    const _counterEl = document.getElementById('rag-reset-counter');
    if (!_counterEl) return;
    const _val = _counterEl.textContent || '';
    if (_val === _lastResetCounter || !_val || _val === '0') return;
    console.log('[rag_bridge] Reset signal changed:', _lastResetCounter, '->', _val);
    _lastResetCounter = _val;
    _onReady(function () {
      _worker.postMessage({ type: 'reset' });
    });
  }

  function _checkConfigSignal() {
    const _configEl = document.getElementById('rag-llm-config');
    if (!_configEl || !_worker) return;
    try {
      const _cfg = JSON.parse(_configEl.textContent);
      delete _cfg._configChanged;
      const _hash = JSON.stringify(_cfg);
      if (_hash !== _lastConfigHash) {
        console.log('[rag_bridge] Config changed');
        _lastConfigHash = _hash;
        _worker.postMessage({ type: 'set_config', data: _cfg });
      }
    } catch (_e) {}
  }

  _initStatusDom();

  _waitForDOM(function () {
    _initWorker();

    setInterval(function () {
      _applyTheme();
      _checkDocSignal();
      _checkQuerySignal();
      _checkResetSignal();
      _checkConfigSignal();
    }, 500);
  });
})();
