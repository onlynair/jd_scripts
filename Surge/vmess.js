
async function operator(proxies = []) {
    const _ = lodash
    return proxies.map((p = {}) => {
        _.set(p, 'ws-opts.headers.Host', 'api.cloud.189.cn') // 改混淆
        return p
    })
}
