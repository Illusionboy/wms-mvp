var pmTrack = {};
var pmTrackUUIDKey = "pmTrackUUID";
// 访问时间
pmTrack.visitTime = (new Date()).getTime();
// 当前url
pmTrack.currentUrl = window.location.href;
pmTrack.setTrackingURL = "//qinsilk-log.cn-hangzhou.log.aliyuncs.com/logstores/log_store_view_time/track";
//获取当前浏览器类型
pmTrack.getBrowserVersion = function (){
    	var browser = {};
    	var userAgent = navigator.userAgent.toLowerCase();
    	var s;
    	(s = userAgent.match(/msie ([\d.]+)/)) ? browser.ie = s[1] : (s = userAgent.match(/firefox\/([\d.]+)/)) ? browser.firefox = s[1] 
    	: (s = userAgent.match(/chrome\/([\d.]+)/)) ? browser.chrome = s[1] : (s = userAgent.match(/opera.([\d.]+)/)) ? browser.opera = s[1] 
    	: (s = userAgent .match(/version\/([\d.]+).*safari/)) ? browser.safari = s[1] : 0;
    	   var version = "";
    	   if (browser.ie) {
    	        version = 'msie ' 
    	        	/*+ browser.ie*/;
    	   } else if (browser.firefox) {
    	        version = 'firefox ' 
    	        	/*+ browser.firefox*/;
    	   } else if (browser.chrome) {
    	        version = 'chrome ' 
    	        	/*+ browser.chrome*/;
    	    } else if (browser.opera) {
    	        version = 'opera ' 
    	        	/*+ browser.opera*/;
    	    } else if (browser.safari) {
    	        version = 'safari ' 
    	        	/*+ browser.safari*/;
    	    } else {
    	        version = '未知的浏览器类型';
    	    }
    	    return version;
};
//获取uuid

pmTrack._UUID = function (len, radix) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
    var uuid = [], i;
    radix = radix || chars.length;
    if (len) {
      for (i = 0; i < len; i++) uuid[i] = chars[0 | Math.random()*radix];
    } else {
      var r;
      uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
      uuid[14] = '4';
      for (i = 0; i < 36; i++) {
        if (!uuid[i]) {
          r = 0 | Math.random()*16;
          uuid[i] = chars[(i == 19) ? (r & 0x3) | 0x8 : r];
        }
      }
    }
    return uuid.join('');
}

pmTrack.getUUID = function() {
	var uuid = null;
	if(window.sessionStorage) {
		uuid = window.sessionStorage.getItem(pmTrackUUIDKey);
		if(uuid || uuid == '') {
			uuid = pmTrack._UUID(16, 16);
			window.sessionStorage.setItem(pmTrackUUIDKey, uuid);
		}
	}
	else {
		uuid = pmTrack._UUID(16, 16);
	}
	return uuid;
}

//格式化参数
pmTrack.formatParams = function (data) {
  var arr = [];
  for (var name in data) {
      arr.push(encodeURIComponent(name) + "=" + encodeURIComponent(data[name]));
   }
     arr.push(("v=" + Math.random()).replace(".",""));
   return arr.join("&");
};
pmTrack.logType = {
    pmViewLogType: 'view', // 曝光记录类型
	pmDefaultLogType: 'click' // 默认记录类型
};
//根据js中data取值
pmTrack.getDataValue = function(name){
	var r = document.getElementById('pmClickLogTrackingScript').getAttribute("data-"+name);
	if(typeof r==='undefined' || r == null){
		return '';
	}
	return r;
};

pmTrack._topic = pmTrack.getDataValue('topic');
pmTrack._sys = pmTrack.getDataValue('sys');
pmTrack._agent = pmTrack.getBrowserVersion();
pmTrack.initEventDom = document.querySelectorAll('[data-pm-track-click]');
//监听点击事件到日志跟踪
pmTrack.setTrackingLog = function (){
		var setParam = {
				  APIVersion:'0.6.0',
				  agent:pmTrack._agent,
				  topic:pmTrack._topic,
				  sys:pmTrack._sys || "pc",
				  userid:pmTrack.getCookie('qs_uid') || 0,
				  cid:pmTrack.getCookie('qs_cid') || 0,
				  visitTime:pmTrack.visitTime,
				  leaveTime:(new Date()).getTime(),
				  currentUrl:pmTrack.currentUrl,
				  log:pmTrack._content,
				  skipUrl:pmTrack._skipUrl || '',
			      logType: pmTrack.logType.pmViewLogType,
				  uuid:pmTrack.getUUID()
				  };
		  pmTrack.ajax({
              url:pmTrack.setTrackingURL ,//请求地址
              type: "GET",//请求方式
              data: setParam,//请求参数
              dataType: "json",
              success: function (response, xml) {}
          });
};
		
//监听具体操作
pmTrack.doMonitorForDataQinsi = function (target) {
        pmTrack._content = target.getAttribute("data-pm-track-click");
        pmTrack._skipUrl = target.getAttribute("data-pm-track-skip");
        if ( pmTrack._content != '' && pmTrack._content != null) {
        	pmTrack.setTrackingLog();
        }
};

pmTrack._logEvent = function(event) {
	var event = event ? event : window.event;
	var target = event.srcElement ? event.srcElement : event.target;
	if (target.getAttribute('data-pm-track-click')){
		pmTrack.doMonitorForDataQinsi(target);
	} else if (target.parentNode.getAttribute('data-pm-track-click')) {
		pmTrack.doMonitorForDataQinsi(target.parentNode);
	}else if(target.children.getAttribute('data-pm-track-click')){
		pmTrack.doMonitorForDataQinsi(target.children);
	}

}

//添加监听事件
pmTrack.initEvent = function(){
	pmTrack.initEventDom = document.querySelectorAll('[data-pm-track-click]');
	for(var _trackDocument = 0;_trackDocument< pmTrack.initEventDom.length;_trackDocument++){
		pmTrack.addEvent(pmTrack.initEventDom[_trackDocument], "click");
	}
};
    

//定义ajax请求方法
pmTrack.ajax =function(options) {
        options = options || {};
        options.type = (options.type || "GET").toUpperCase();
        options.dataType = options.dataType || "json";
        var params = pmTrack.formatParams(options.data);
        //创建 - 非IE6 - 第一步
        if (window.XMLHttpRequest) {
            var xhr = new XMLHttpRequest();
        } else { //IE6及其以下版本浏览器
            var xhr = new ActiveXObject('Microsoft.XMLHTTP');
        }
        //接收 - 第三步
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                var status = xhr.status;
                if (status >= 200 && status < 300) {
                    options.success && options.success(xhr.responseText, xhr.responseXML);
                } else {
                    options.fail && options.fail(status);
                }
            }
        };
        //连接 和 发送 - 第二步
        if (options.type == "GET") {
            xhr.open("GET", options.url + "?" + params, true);
            xhr.send(null);
        } else if (options.type == "POST") {
            xhr.open("POST", options.url, true);
            //设置表单提交时的内容类型
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xhr.send(params);
        }
};
//添加监听事件
pmTrack.addEvent = function(obj, type){
	if (obj.attachEvent) {
		obj.detachEvent('on' + type, obj[type + pmTrack._logEvent]);
		obj['e' + type + pmTrack._logEvent] = pmTrack._logEvent;
		obj[type+pmTrack._logEvent] = function(){obj['e'+type+pmTrack._logEvent]( window.event );};
		obj.attachEvent('on' + type, obj[type + pmTrack._logEvent]);
	} else{
		obj.removeEventListener(type, pmTrack._logEvent);
		obj.addEventListener(type, pmTrack._logEvent, false);
	}
};
//获取当前url地址参数值
pmTrack.getQueryString = function(name) { 
	var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i"); 
	var r = window.location.search.substr(1).match(reg); 
	if (r != null) return unescape(r[2]); return null; 
}; 

//获取cookie
pmTrack.getCookie = function(name) { 
	var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
	if (arr = document.cookie.match(reg)) {
		return (arr[2]);
	} else {
		return null;
	}
};
		
//初始化绑定click事件
pmTrack.initEvent();

pmTrack._content = pmTrack.getDataValue('init');
if(pmTrack._content != '' && pmTrack._content != null){
	pmTrack.setTrackingLog();
}