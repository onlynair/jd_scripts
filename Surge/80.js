function filter(proxies) {
  return proxies.map(p => [80].includes(Number(p.port)))
}
