function filter(proxies) {
  return proxies.map(p => [80, 443 ].includes(Number(p.port)))
}
