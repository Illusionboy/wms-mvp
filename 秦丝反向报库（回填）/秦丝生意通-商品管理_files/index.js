
/**
 * 初始化Sentry配置
 * 依赖 https://sentry.app.qinsilk.com/js-sdk-loader/0cc49dc89479145de9d4a0217afaf26f.min.js脚本加载注入的 window.Sentry
 * 对应sentry后台地址 https://sentry.app.qinsilk.com/organizations/sentry/projects/gis-vue/?project=16
 * 帮助文档参考 https://docs.sentry.io/
 */
const productionHost = 'https://web.syt.qinsilk.com';
const isProduction = window.location.href.includes(productionHost);
const isLocal = window.location.href.includes('localhost');
const environment = productionHost ? 'production' : 'development';
window.Sentry && window.Sentry.init({
	dsn: 'https://0cc49dc89479145de9d4a0217afaf26f@sentry.app.qinsilk.com/16',
	enabled: !isLocal,
	debug: !isProduction,
	environment: environment
});
