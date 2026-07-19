(function ($) {
    // 用户配置 - 是否默认展开
    var autoShow = (function () {
        var rightDocExpanded = null;
        if (localStorage) {
            rightDocExpanded = localStorage.getItem('rightDocExpanded');
        } else {
            rightDocExpanded = getCookie('rightDocExpanded');
        }
        if (rightDocExpanded == 'true') {
            return true;
        }
        return false;
    })();

    function setCookie(c_name, value, expiredays) {
        var exdate = new Date()
        exdate.setDate(exdate.getDate() + expiredays)
        document.cookie = c_name + "=" + escape(value) +
            ((expiredays == null) ? "" : "; expires=" + exdate.toGMTString())
    }
    //获取cookie
    var getCookie = function (name) {
        var arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
        if (arr = document.cookie.match(reg)) {
            return (arr[2]);
        } else {
            return null;
        }
    };
    var updateAutoShow = function (autoShow) {
        if (localStorage) {
            localStorage.setItem('rightDocExpanded', autoShow);
        } else {
            setCookie('rightDocExpanded', autoShow);
        }
    }
    //获取当前浏览器类型
    var logGetBrowserVersion = function () {
        var browser = {};
        var userAgent = navigator.userAgent.toLowerCase();
        var s;
        (s = userAgent.match(/msie ([\d.]+)/)) ? browser.ie = s[1] : (s = userAgent.match(/firefox\/([\d.]+)/)) ? browser.firefox = s[1]
            : (s = userAgent.match(/chrome\/([\d.]+)/)) ? browser.chrome = s[1] : (s = userAgent.match(/opera.([\d.]+)/)) ? browser.opera = s[1]
                : (s = userAgent.match(/version\/([\d.]+).*safari/)) ? browser.safari = s[1] : 0;
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
    //格式化参数
    var logFormatParams = function (data) {
        var arr = [];
        for (var name in data) {
            arr.push(encodeURIComponent(name) + "=" + encodeURIComponent(data[name]));
        }
        arr.push(("v=" + Math.random()).replace(".", ""));
        return arr.join("&");
    };
    //请求数据（公共）
    var logAjax = function (options) {
        options = options || {};
        options.type = (options.type || "GET").toUpperCase();
        options.dataType = options.dataType || "json";
        var params = logFormatParams(options.data);
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
    var setTrackingURL = "//qinsilk-log.cn-hangzhou.log.aliyuncs.com/logstores/log_store_tracking/track";
    var saveLog = function (log) {
        if (log) {
            var setParam = {
                APIVersion: '0.6.0',
                topic: "helpDocument",
                agent: logGetBrowserVersion(),
                client: "gispc",
                userid: getCookie("qs_uid") || 0,
                cid: getCookie("qs_cid") || 0,
                log: log,
                qsr: window.location.href
            };

            if (setParam.topic != null && setParam.log != null && setParam.client != null && setParam.agent != null) {
                logAjax({
                    url: setTrackingURL,//请求地址
                    type: "GET",//请求方式
                    data: setParam,//请求参数
                    dataType: "json",
                    success: function (response, xml) {
                        // 此处放成功后执行的代码
                    },
                    fail: function (status) {
                        // 此处放失败后执行的代码
                        console.log(status);
                    }
                });
            }
        }
    }

    var autoShowMinWidth = 1800;
    var customerServiceImg = "//cdn.qinsilk.com/img/college/help/helpTips/qinsilkCustomerService.png";
    var wechatCustomerServiceImgEven = "//cdn.qinsilk.com/img/information/gisCompanyWechatQrcode.jpg";
    var wechatCustomerServiceImgOdd = "//cdn.qinsilk.com/img/information/gisCompanyWechatQrcode.jpg";
    var gisNewQrcode = "//cdn.qinsilk.com/img/information/gisNewQrcode.png";
    // 随机选择需要展示的微信二维码
    var wechatCustomerServiceImg = (function () {
        if (userLoginInfoJSON != undefined && userLoginInfoJSON != null
            && userLoginInfoJSON.userVO != undefined && userLoginInfoJSON.userVO != null) {
            var cid = userLoginInfoJSON.userVO.cid;
            // 以2021年11月26日9点为分界线 以前为老用户 以后为新用户 转化为时间戳
            var timeFlag = new Date("2021-11-26 9:00:00").getTime();
            var clientCreateTime = new Date(userLoginInfoJSON.userVO.createTime).getTime()
            if (clientCreateTime < timeFlag) {
                return cid % 2 == 0 ? wechatCustomerServiceImgEven : wechatCustomerServiceImgOdd;
            } else {
                return gisNewQrcode;
            }
        }
        return gisNewQrcode
    })();
    var customServiceUrl_cid = 0;
    var customServiceUrl_uid = 0
    if (userLoginInfoJSON != undefined && userLoginInfoJSON != null
        && userLoginInfoJSON.userVO != undefined && userLoginInfoJSON.userVO != null) {
        customServiceUrl_cid = userLoginInfoJSON.userVO.cid;
        customServiceUrl_uid = userLoginInfoJSON.userVO.id;
    }
    var customServiceUrl = 'https://web.qinsilk.com/customerService/index.html?source=2&kfid=wk3XtzBwAArYB7HO4YZNUEhv6u69Nagg&cid=' + customServiceUrl_cid + '&sys=0&uid=' + customServiceUrl_uid;
    var searchHelpUrl = 'https://www.qinsilk.com/mms/front/help/gis/searchCollegeList.html?searchAppIds=qinsilk_gis_help&clientType=0&page=1&keyword=';
    var helpQuestionDetailUrl = 'https://www.qinsilk.com/mms/front/help/gis/question-id';
    var rightDocDiv = $('<div id="right-help-doc">'
        + '<div class="doc-index"><div class="doc-index-title">帮助中心</div><div class="doc-index-smmary">1000<small>+</small>帮助教程</div><div class="go-doc-index-logo"> &gt; </div>'
        + '</div>'
        + '<div class="doc-title"  style="position: relative;">'
        + '<span class="doc-title-main" style="line-height: 20px;">帮助中心</span>'
        + '<a style="bottom: 4px;right: 5px;position: absolute;" target="_blank" href="#">进入></a>'
        + '</div>'
        + '<div class="input-group" style="margin-top: 20px;margin-left: 15px;">'
        + '<input style="height:20px;outline: none;border: 0;border-bottom: 1px solid #ccc;" type="text" placeholder="有问题？马上搜索答案"/>'
        + '<span class="input-group-btn">'
        + '<button class="btn glyphicon glyphicon-search search-btn" style="background-color: #00aafa;color: white;height: 20px;margin-top: -1px;font-size: 5px;padding: 1px 10px;" type="button"></button>'
        + '</span>'
        + '</div>'
        + '<div class="dataList" style="padding:15px 15px 0 15px;"></div>'
        + '<hr />'
        + '<div class="doc-title">'
        + '<span>秦丝专属客户顾问</span>'
        + '</div>'
        + '<div style="position:relative;margin:15px;padding:30px 20px 30px 70px;background-color: #f8f8f8;border-radius: 2px;color: #666;"><a class="right-help-online-service" id="consulting_help_a" data-display="block">'
        + '<div style="position: absolute;top: 16px;left: 14px;border-radius: 50%;display: inline-block;background-position: 50%;background-size: 100%;width:44px;height:44px;'
        + 'background: url(' + customerServiceImg + ');"></div>'
        + '<span style="">在线咨询</span>'
        + '</a></div>'
        + '<div class="online-link" style="padding:0 15px 15px 15px;">'
        + '<div style="font-weight: bold;margin-top:10px;">企业微信群</div>'
        + '<div style="width:120px;height:120px;background: url(' + wechatCustomerServiceImg + '); background-size:cover;margin-left: 15px;"></div>'
        + '</div>'
        + '<hr style="margin-bottom:2px;" />'
        + '<div style="color:#999;margin-left: 10px;">'
        + '<input id="autoExpended" class="input_check" type="checkbox" ' + (!autoShow ? 'checked' : '') + '/>'
        + '<label for="autoExpended">不再自动展示帮助侧栏</label>'
        + '</div>'
        + '</div>');

    // 设置列表函数
    var setRightDocData = function (data) {
        if (data != null) {
            for (var i = 0; i < data.length; i++) {
                var item = $('<div><a style="color: #07d;text-decoration: none;" target="_blank" href="' + helpQuestionDetailUrl + data[i].id + '.html?qsr=right-help-doc">' + data[i].title + '</a><div>');
                rightDocDiv.find('.dataList').append(item);
            }
        }
    }

    var resizePageNav = function (hideDocOnSmallWidth) {
        var winWidth = $(window).width();
        var winHeight = $(window).height();
        var isShow = rightDocDiv.css('display') != 'none';
        var mainDivWidth = $('#bodyloadinglayer + div').outerWidth();
        // 更新窗口高度
        rightDocDiv.css({
            'height': winHeight - 96
        });
        // 更新导航宽度
        $('.page_navbar').css({
            'width': winWidth > mainDivWidth ? winWidth : mainDivWidth
        });
        if (autoShow) {
            if ((hideDocOnSmallWidth && winWidth < autoShowMinWidth && isShow) || (winWidth >= autoShowMinWidth && !isShow)) {
                toggleRightDoc();
            }
        } else if (isShow && winWidth >= autoShowMinWidth) {
            $('#bodyloadinglayer + div').animate({ 'margin-right': 200 }, 200, function () {
              $(window).resize();
              if (window.fixedFooterFloat && typeof window.fixedFooterFloat === 'function') {
                window.fixedFooterFloat();
              }

            });
        } else if (isShow && winWidth < autoShowMinWidth) {
            $('#bodyloadinglayer + div').animate({ 'margin-right': 0 }, 200, function () {
              $(window).resize();
              if (window.fixedFooterFloat && typeof window.fixedFooterFloat === 'function') {
                window.fixedFooterFloat();
              }
            });
        }
    }

    // 切换主面板显示/隐藏
    var toggleRightDoc = function () {
        var winWidth = $(window).width();
        var isShow = rightDocDiv.css('display') == 'none';
        rightDocDiv.toggle('slide', { direction: 'right' }, 200, function () {
            if (rightDocDiv.css('display') == 'none') {
                $('#bodyloadinglayer + div').animate({ 'margin-right': 0 }, 200, function () {
                  $(window).resize();
                  if (window.fixedFooterFloat && typeof window.fixedFooterFloat === 'function') {
                    window.fixedFooterFloat();
                  }
                });
            } else if (winWidth >= autoShowMinWidth) {
                $('#bodyloadinglayer + div').animate({ 'margin-right': 200 }, 200, function () {
                  $(window).resize();
                  if (window.fixedFooterFloat && typeof window.fixedFooterFloat === 'function') {
                    window.fixedFooterFloat();
                  }
                });
            }
        });
        //$('.right-help-doc-icon').css({'right':!isShow ? 20 : 72});
        $('.page_navbar .icon-help > a').attr('data-content', !isShow ? '+' : '×');
        $('.right-help-doc-icon').attr('title', !isShow ? '展开帮助栏' : '隐藏帮助栏');
    }

    //阻止原帮助文档跳转链接
    $('.page_navbar .icon-help a').on('click', function (e) {
        e.preventDefault();
    });
    //触发右侧帮助文档面板显示/隐藏
    $('.page_navbar .icon-help').on('click', function () {
        autoShow = false;
        toggleRightDoc();
        saveLog("icon-help-click");
    });

    //面板关闭按钮
    rightDocDiv.delegate('.close', 'click', function () {
        autoShow = false;
        toggleRightDoc();
    });
    // 搜索按钮
    rightDocDiv.delegate('.search-btn', 'click', function (e) {
        var text = $('#right-help-doc input').val();
        if (text != '') {
            saveLog("right-help-search-" + text);
            window.open(searchHelpUrl + text);
        }
    });

    // 绑定回车搜索
    rightDocDiv.delegate('input', 'keypress', function (e) {
        if (e.keyCode == 13) {
            window.open(searchHelpUrl + $(this).val());
        }
    });
    rightDocDiv.delegate('#autoExpended', 'change', function (e) {
        var notShow = $(this)[0].checked;
        if (notShow) {
            autoShow = false;
            toggleRightDoc();
        }
        updateAutoShow(!notShow);
    });
    // 监听窗口变动
    $(window).resize(function () {
        resizePageNav(true);
    });

    // 用户信息[区分是否公海]
    var userGroupInfo = null

    // 在线咨询处理公海
    function handleServiceConcat(event) {
        // 默认跳转点击事件
        var defaultClickEvent = function (url) {
            window.open(url, "_balnk")
        }
        // 公海点击事件
        var newClickEvent = function () {
            // 获取对应dom
            var newServiceConcatMask = $("#mareLiberum-service-mask")
            var newServiceConcatModal = $("#mareLiberum-service-modal")
            var closeBtn = $("#mareLiberum-service-modal > .close")
            // 点击遮罩关闭
            newServiceConcatMask.on("click", closeOrShowModal)
            closeBtn.on("click", closeOrShowModal)
            // 防止冒泡
            newServiceConcatModal.on("click", function (e) {
                e.stopPropagation()
            })
            // 打开二维码弹窗
            closeOrShowModal(event)
            function closeOrShowModal(e) {
                e.preventDefault()
                var value = e.currentTarget.dataset.display
                newServiceConcatMask.css("display", value)
            }
        }
        // 请求过不再请求
        if (userGroupInfo) {
            if (userGroupInfo.counselorId == null && userGroupInfo.groupId == null) {
                newClickEvent()
            } else {
                defaultClickEvent(customServiceUrl)
            }
            return
        }
        var cloudServer = location && (location.hostname.indexOf('dev') > -1 || location.hostname.indexOf('local') > -1) ? "https://devcloud.qinsilk.com" : "https://cloud.qinsilk.com"
        $.post(cloudServer + "/console/gis/getUserCounselorAndGroup.ac").success(function (res) {
            if (res.statusCode == 1) {
                if (res.object) {
                    userGroupInfo = {
                        counselorId: res.object.counselorId,
                        groupId: res.object.groupId
                    }
                    // counselorId groupId 同时为null的时候属于公海
                    if (res.object.counselorId == null && res.object.groupId == null) {
                        // 新增遮罩弹窗
                        var newServiceConcatDiv = "<div id='mareLiberum-service-mask' data-display='none'>" +
                            "<div id='mareLiberum-service-modal'>" +
                            "<div class='close' data-display='none'>x</div>"
                            + "<img src='https://cdn.qinsilk.com/img/information/mare_liberum_service_qrcode.jpg'>"
                            + "</div>"
                            + "</div>"
                        // 弹窗里的样式
                        var cssText = "#mareLiberum-service-mask{width:100%;height:100%;position:fixed;left:0;top:0;display:none;background-color: rgba(0, 0, 0, 0.5);z-index:9999;}"
                            + "#mareLiberum-service-modal{position:absolute;left:50%;top:50%;min-width:330px;width:22vw;height:70vh;transform: translate(-50%,-50%)}"
                            + "#mareLiberum-service-modal > .close{position:absolute;right:10px;top:5px;}"
                            + "#mareLiberum-service-modal > img{width:100%;height:100%}"
                        // 加载css
                        loadStyleString(cssText)
                        // 追加弹窗
                        $('body').append($(newServiceConcatDiv))
                        newClickEvent()
                        return
                    }
                }
            }
            defaultClickEvent(customServiceUrl)
        }).fail(function () {
            defaultClickEvent(customServiceUrl)
        })
    }

    // 动态加载css脚本
    function loadStyleString(cssText) {
        var style = document.createElement("style");
        style.type = "text/css";
        try {
            style.appendChild(document.createTextNode(cssText));
        } catch (ex) {
            style.styleSheet.cssText = cssText;
        }
        document.getElementsByTagName("head")[0].appendChild(style);
    }

    var cssText = "#bodyloadinglayer + div {margin-right: 0;}#right-help-doc{padding: 20px 10px 20px 10px;font-size: 12px;}"
        + "#right-help-doc .doc-title{color: #333;border-left: 2px solid #3283FA;padding-left: 8px;padding-right: 10px;line-height: 12px;margin: 10px 0;}"
        + ".page_navbar .icon-help > a::AFTER{content: attr(data-content);margin-left: 10px;color: #ccc;font-size: 20px;}"
        + "#right-help-doc a{color: #38f;text-decoration: none;}#right-help-doc hr{margin: 20px 10px;border: 0;border-top: 1px solid #eee;border-bottom: 1px solid #fff;}"
        + "#right-help-doc .online-link a{font-family: Arial;font-weight: bold;color: #e66d15;}"
        + "#right-help-doc label {font-weight:100}"
        + "#right-help-doc .input_check {position: absolute;visibility: hidden;}"
        + "#right-help-doc .input_check+label {position: relative;}"
        + "#right-help-doc .input_check+label:before {content: '';display: inline-block;width: 11px;height: 11px;border: 1px solid #fd8845;}"
        + "#right-help-doc .input_check:checked+label:after {content: '';position: absolute;left: 2px;top:4px;width: 9px;height: 4px;border: 2px solid #fd8845;border-top-color: transparent;"
        + "border-right-color: transparent;-ms-transform: rotate(-60deg); -moz-transform: rotate(-60deg); -webkit-transform: rotate(-60deg); transform: rotate(-45deg);}"
        + (autoShow ? "@media only screen and (min-width: " + autoShowMinWidth + "px){#bodyloadinglayer + div {margin-right: 200px;}}" : "")
        + ".dataList > div {margin-bottom: 10px; line-height: 16px;}"
        + ".dataList > div:hover {background-color: rgba(0,0,0,0.1); border-radius: 2px;}"
        + ".right-help-doc-icon{ cursor: pointer;position: fixed;right: 20px;top: 62px;width: 50px;background: url(https://cdn.qinsilk.com/img/college/help/common/right_help_icon.png);z-index: 1000;height: 50px;background-repeat: no-repeat;background-size: contain;}"
        + "#right-help-doc{min-height: 780px;}"
        + "#right-help-doc .doc-index{ position: relative;width: auto;background: url(https://cdn.qinsilk.com/img/college/help/common/right_help_back_img@2x.png);height: 80px;background-repeat: no-repeat; background-size: contain;color: #fff;padding: 20px;cursor: pointer;}"
        + "#right-help-doc .doc-index .doc-index-title{padding-bottom: 5px;font-size: 16px;}"
        + "#right-help-doc .doc-index .go-doc-index-logo{position: absolute;top: 50%;right: 20px;font-size: 20px;margin-top: -11.5px;}"
        + "#right-help-doc .doc-index .doc-index-smmary{font-size: 12px;opacity: 0.8;}";

    //
    // 加载css
    loadStyleString(cssText);

    $(document).ready(function () {
        // 延时执行，等待新的用户配置信息加载完成
        setTimeout(function () {
            var helpUrl = $('.page_navbar .icon-help > a').attr('href');

            //如果当前功能介绍无帮助文档链接则跳去帮助文档首页
            if (!helpUrl) {
                helpUrl = "https://www.qinsilk.com/mms/front/help/gis/help-id0.html?pageId=3";
            }
            var removeTargetAttr = false;
            if (helpUrl.indexOf('//') == 0) {
                helpUrl = 'https:' + helpUrl;
            } else if (helpUrl.indexOf('http:') == 0) {
                helpUrl = helpUrl.replace('http:', 'https:');
            } else if (helpUrl.indexOf('javascript:') == 0) {
                removeTargetAttr = true;
            } else if (helpUrl.indexOf('https:') == 0) {
            } else {
                helpUrl = 'https://' + helpUrl;
            }
            var isShow = rightDocDiv.css('display') == 'none';
            var winHeight = $(window).height();
            var winWidth = $(window).width();
            rightDocDiv.css({
                'display': 'none',
                'position': 'absolute',
                'right': 0,
                'top': 96,
                'width': 199,
                'background-color': '#fff',
                'border': '1px solid #cfcfcf',
                'border-right': '0',
                'z-index': 999
            });
            if (autoShow) {
                $('.page_navbar .icon-help > a').attr('data-content', winWidth > autoShowMinWidth ? '×' : '+');
            } else {
                $('.page_navbar .icon-help > a').attr('data-content', '+');
                $('#bodyloadinglayer + div').animate({ 'margin-right': 0 }, 0, function () {
                  $(window).resize();
                  if (window.fixedFooterFloat && typeof window.fixedFooterFloat === 'function') {
                    window.fixedFooterFloat();
                  }
                });
            }

            $('body').append(rightDocDiv);
            var rightHelpDocBtn = $('<div class="right-help-doc-icon" title="展开帮助栏"></div>');
            $('body').append(rightHelpDocBtn);
            //$('.right-help-doc-icon').css({'right':!isShow ? 20 : 72});
            $('#right-help-doc .doc-title-main').text($('.breadcrumb .active').text() + '介绍');
            $('#right-help-doc .doc-title-main + a').attr('href', helpUrl);
            if (removeTargetAttr) {
                $('#right-help-doc .doc-title-main + a').removeAttr('target');
            }
            //右边侧边栏点击在线客服添加埋点日志
            $('.right-help-online-service').on('click', function () {
                saveLog("right-help-go-online-service");
            });
            //右边侧边栏点击帮助文档
            $('.right-help-doc-icon').on('click', function () {
                autoShow = false;
                toggleRightDoc();
                saveLog("icon-help-click");
            });
            $('.icon-help').hide();
            $('.right-help-doc-icon').attr('title', !isShow ? '展开帮助栏' : '隐藏帮助栏');
            //跳转帮助文档首页
            $('.doc-index').on('click', function () {
                window.open("https://www.qinsilk.com/mms/front/help/gis/help-id0.html?qsr=right-help-doc", "_blank");
            });
            resizePageNav(true);
            //获取问题列表
            var key = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1, window.location.pathname.length - 3);
            $.get('//www.qinsilk.com/mms/front/help/gis/getHelpListByPage.ac?pageId=' + key).success(function (data) {
                setRightDocData(data);
            });
            $.getScript("//cdn.qinsilk.com/res/business/commonConfig/qinsilkInfo.js?" + Math.random(), function () { });
            // 在线咨询按钮
            $("#consulting_help_a").on("click", handleServiceConcat)
        }, 100);
    });

})(jQuery);
/**
 * 打开帮助页面
 */
function toHelp(hid, name) {
    window.open("https://www.qinsilk.com/mms/front/help/gis/help-id" + hid + ".html?qsr=right-help-doc#" + (name ? name : ""), "_blank");
}
