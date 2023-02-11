
async function operator(proxies = []) {
    const _ = lodash
    return proxies.map((p = {}) => {
        _.set(p, 'ws-opts.headers.Host', 'cloud189-shzh-person.oos-gdsz.ctyunapi.cn') // 改混淆
        return p
    })
}
