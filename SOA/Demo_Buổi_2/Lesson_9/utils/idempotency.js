const store = new Map();

function processIdempotent(key, handler) {
  if (store.has(key)) {
    return store.get(key); // trả kết quả cũ
  }
  const result = handler();
  store.set(key, result);
  return result;
}

module.exports = processIdempotent;
