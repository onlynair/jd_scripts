async function operator(proxies = []) {
    const _ = lodash
    return proxies.map((p = {}) => {
        _.set(p, 'plugin', 'obfs')  // 改混淆插件
        _.set(p, 'plugin-opts', { "mode": "http", "host": "api.cloud.189.cn" })  // 改混淆

        // _.set(p, 'plugin-opts.mode', 'http')  // 改混淆插件
        // _.set(p, 'plugin-opts.host', 'api.cloud.189.cn')  // 改混淆

        return p
    })
}
