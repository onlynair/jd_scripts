function filter(proxies) {

  return proxies.map(p => [80, 46794].includes(Number(p.port)))

}
