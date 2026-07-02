const _DB_NAME = 'blackboardlm_rag';
const _DB_VERSION = 1;
const _STORE_NAME = 'rag_state';

function _open() {
  return new Promise((_resolve, _reject) => {
    const _req = indexedDB.open(_DB_NAME, _DB_VERSION);
    _req.onupgradeneeded = (_e) => {
      const _db = _e.target.result;
      if (!_db.objectStoreNames.contains(_STORE_NAME)) {
        _db.createObjectStore(_STORE_NAME);
      }
    };
    _req.onsuccess = (_e) => _resolve(_e.target.result);
    _req.onerror = (_e) => _reject(_e.target.error);
  });
}

async function _save(key, data) {
  const _db = await _open();
  return new Promise((_resolve, _reject) => {
    const _tx = _db.transaction(_STORE_NAME, 'readwrite');
    const _store = _tx.objectStore(_STORE_NAME);
    _store.put(data, key);
    _tx.oncomplete = () => _resolve();
    _tx.onerror = (_e) => _reject(_e.target.error);
  });
}

async function _load(key) {
  const _db = await _open();
  return new Promise((_resolve, _reject) => {
    const _tx = _db.transaction(_STORE_NAME, 'readonly');
    const _store = _tx.objectStore(_STORE_NAME);
    const _req = _store.get(key);
    _req.onsuccess = (_e) => _resolve(_e.target.result);
    _req.onerror = (_e) => _reject(_e.target.error);
  });
}

async function _clear() {
  const _db = await _open();
  return new Promise((_resolve, _reject) => {
    const _tx = _db.transaction(_STORE_NAME, 'readwrite');
    const _store = _tx.objectStore(_STORE_NAME);
    _store.clear();
    _tx.oncomplete = () => _resolve();
    _tx.onerror = (_e) => _reject(_e.target.error);
  });
}

const Storage = {
  save: (key, data) => _save(key, data),
  load: (key) => _load(key),
  clear: () => _clear(),
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { Storage };
}
