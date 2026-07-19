var BASE_URL = {}
var GLOBAL_ENV = {
    IS_DEV: true,
    IS_PROD: false,
    IS_EX: false
};

if (location.hostname && location.hostname.indexOf('localhost') > -1) {
    BASE_URL = {
        webServer: "https://dev.qinsilk.com/gis",
        cloudServer: "https://devcloud.qinsilk.com",
        mgrWebServer: "https://dev.qinsilk.com/gmc",
        gmcWebServer: "https://syt.dev.qinsilk.com/gmc",
        cdnServer: "https://cdn.qinsilk.com",
        esService: "https://dev.qinsilk.com/ges",
        gsmServer: "https://dev.qinsilk.com/gsm",
        picUrl: "https://syt.qinsilk.com"
    }

	// 	BASE_URL = {
	// 		webServer: "https://web.syt.qinsilk.com/gis",
	// 		cloudServer: "https://cloud.qinsilk.com",
	// 		mgrWebServer: "https://syt.qinsilk.com/gmc",
	// 		gmcWebServer: "https://syt.qinsilk.com/gmc",
	// 		cdnServer: "https://cdn.qinsilk.com",
	// 		esService: "https://web.syt.qinsilk.com/ges",
	// 		gsmServer: "https://syt.qinsilk.com/gsm",
	// 		picUrl: "https://syt.qinsilk.com"
	// }
} else {
    var _xhr = (function() {
        if (window.ActiveXObject) {
            return new ActiveXObject("Microsoft.XMLHTTP");
        }
        return new XMLHttpRequest();
    })();

    _xhr.onreadystatechange = function(){
        if(_xhr.readyState == 4 && _xhr.status == 200){
            var data = eval('(' + _xhr.responseText + ')');
            if(data.statusCode == 1 && data.object){
                var host = eval('(' + data.object + ')');
                BASE_URL.webServer = host.baseUrl + '/gis';
                BASE_URL.cloudServer = host.cloudUrl
                BASE_URL.mgrWebServer = host.baseUrl + '/gmc';
                BASE_URL.gmcWebServer = (host.baseUrl.includes('dev.qinsilk.com') ? 'https://syt.dev.qinsilk.com' : host.baseUrl) + '/gmc';
                BASE_URL.cdnServer = host.cdnUrl
                BASE_URL.esService = host.baseUrl + '/ges';
                BASE_URL.gsmServer = host.gsmUrl + '/gsm';
                BASE_URL.picUrl = host.picUrl;
                GLOBAL_ENV = host.env || {};
            } else {
                alert('服务器开了个小差，刷新再试试吧');
            }
        }
    };
    _xhr.open("GET",'/gis/front/system/getHostConfig.ac',false);
    _xhr.send(null);
}
