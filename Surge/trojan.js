
async function operator(proxies = []) {
    const _ = lodash
    return proxies.map((p = {}) => {
        _.set(p, 'skip-cert-verify', true)  // 改跳过证书验证
        _.set(p, 'sni', 'cloud189-shzh-person.oos-gdsz.ctyunapi.cn') // 改混淆
        return p
    })
}
