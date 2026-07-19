webpackJsonp([114],{

/***/ "/7ae":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "MessageReceiveOptType", function() { return MessageReceiveOptType; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "AllowType", function() { return AllowType; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GroupType", function() { return GroupType; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GroupJoinSource", function() { return GroupJoinSource; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GroupMemberRole", function() { return GroupMemberRole; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GroupVerificationType", function() { return GroupVerificationType; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "MessageStatus", function() { return MessageStatus; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Platform", function() { return Platform; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "LogLevel", function() { return LogLevel; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ApplicationHandleResult", function() { return ApplicationHandleResult; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "MessageType", function() { return MessageType; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "SessionType", function() { return SessionType; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GroupStatus", function() { return GroupStatus; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GroupAtType", function() { return GroupAtType; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "GroupMemberFilter", function() { return GroupMemberFilter; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "Relationship", function() { return Relationship; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "LoginStatus", function() { return LoginStatus; });
var MessageReceiveOptType;
(function (MessageReceiveOptType) {
	MessageReceiveOptType[MessageReceiveOptType["Nomal"] = 0] = "Nomal";
	MessageReceiveOptType[MessageReceiveOptType["NotReceive"] = 1] = "NotReceive";
	MessageReceiveOptType[MessageReceiveOptType["NotNotify"] = 2] = "NotNotify";
})(MessageReceiveOptType || (MessageReceiveOptType = {}));
var AllowType;
(function (AllowType) {
	AllowType[AllowType["Allowed"] = 0] = "Allowed";
	AllowType[AllowType["NotAllowed"] = 1] = "NotAllowed";
})(AllowType || (AllowType = {}));
var GroupType;
(function (GroupType) {
	GroupType[GroupType["WorkingGroup"] = 2] = "WorkingGroup";
})(GroupType || (GroupType = {}));
var GroupJoinSource;
(function (GroupJoinSource) {
	GroupJoinSource[GroupJoinSource["Invitation"] = 2] = "Invitation";
	GroupJoinSource[GroupJoinSource["Search"] = 3] = "Search";
	GroupJoinSource[GroupJoinSource["QrCode"] = 4] = "QrCode";
})(GroupJoinSource || (GroupJoinSource = {}));
var GroupMemberRole;
(function (GroupMemberRole) {
	GroupMemberRole[GroupMemberRole["Nomal"] = 20] = "Nomal";
	GroupMemberRole[GroupMemberRole["Admin"] = 60] = "Admin";
	GroupMemberRole[GroupMemberRole["Owner"] = 100] = "Owner";
})(GroupMemberRole || (GroupMemberRole = {}));
var GroupVerificationType;
(function (GroupVerificationType) {
	GroupVerificationType[GroupVerificationType["ApplyNeedInviteNot"] = 0] = "ApplyNeedInviteNot";
	GroupVerificationType[GroupVerificationType["AllNeed"] = 1] = "AllNeed";
	GroupVerificationType[GroupVerificationType["AllNot"] = 2] = "AllNot";
})(GroupVerificationType || (GroupVerificationType = {}));
var MessageStatus;
(function (MessageStatus) {
	MessageStatus[MessageStatus["Sending"] = 1] = "Sending";
	MessageStatus[MessageStatus["Succeed"] = 2] = "Succeed";
	MessageStatus[MessageStatus["Failed"] = 3] = "Failed";
})(MessageStatus || (MessageStatus = {}));
var Platform;
(function (Platform) {
	Platform[Platform["iOS"] = 1] = "iOS";
	Platform[Platform["Android"] = 2] = "Android";
	Platform[Platform["Windows"] = 3] = "Windows";
	Platform[Platform["MacOSX"] = 4] = "MacOSX";
	Platform[Platform["Web"] = 5] = "Web";
	Platform[Platform["Linux"] = 7] = "Linux";
	Platform[Platform["AndroidPad"] = 8] = "AndroidPad";
	Platform[Platform["iPad"] = 9] = "iPad";
})(Platform || (Platform = {}));
var LogLevel;
(function (LogLevel) {
	LogLevel[LogLevel["Debug"] = 5] = "Debug";
	LogLevel[LogLevel["Info"] = 4] = "Info";
	LogLevel[LogLevel["Warn"] = 3] = "Warn";
	LogLevel[LogLevel["Error"] = 2] = "Error";
	LogLevel[LogLevel["Fatal"] = 1] = "Fatal";
	LogLevel[LogLevel["Panic"] = 0] = "Panic";
})(LogLevel || (LogLevel = {}));
var ApplicationHandleResult;
(function (ApplicationHandleResult) {
	ApplicationHandleResult[ApplicationHandleResult["Unprocessed"] = 0] = "Unprocessed";
	ApplicationHandleResult[ApplicationHandleResult["Agree"] = 1] = "Agree";
	ApplicationHandleResult[ApplicationHandleResult["Reject"] = -1] = "Reject";
})(ApplicationHandleResult || (ApplicationHandleResult = {}));
var MessageType;
(function (MessageType) {
	MessageType[MessageType["TextMessage"] = 101] = "TextMessage";
	MessageType[MessageType["PictureMessage"] = 102] = "PictureMessage";
	MessageType[MessageType["VoiceMessage"] = 103] = "VoiceMessage";
	MessageType[MessageType["VideoMessage"] = 104] = "VideoMessage";
	MessageType[MessageType["FileMessage"] = 105] = "FileMessage";
	MessageType[MessageType["AtTextMessage"] = 106] = "AtTextMessage";
	MessageType[MessageType["MergeMessage"] = 107] = "MergeMessage";
	MessageType[MessageType["CardMessage"] = 108] = "CardMessage";
	MessageType[MessageType["LocationMessage"] = 109] = "LocationMessage";
	MessageType[MessageType["CustomMessage"] = 110] = "CustomMessage";
	MessageType[MessageType["TypingMessage"] = 113] = "TypingMessage";
	MessageType[MessageType["QuoteMessage"] = 114] = "QuoteMessage";
	MessageType[MessageType["FaceMessage"] = 115] = "FaceMessage";
	MessageType[MessageType["FriendAdded"] = 1201] = "FriendAdded";
	MessageType[MessageType["OANotification"] = 1400] = "OANotification";
	MessageType[MessageType["GroupCreated"] = 1501] = "GroupCreated";
	MessageType[MessageType["GroupInfoUpdated"] = 1502] = "GroupInfoUpdated";
	MessageType[MessageType["MemberQuit"] = 1504] = "MemberQuit";
	MessageType[MessageType["GroupOwnerTransferred"] = 1507] = "GroupOwnerTransferred";
	MessageType[MessageType["MemberKicked"] = 1508] = "MemberKicked";
	MessageType[MessageType["MemberInvited"] = 1509] = "MemberInvited";
	MessageType[MessageType["MemberEnter"] = 1510] = "MemberEnter";
	MessageType[MessageType["GroupDismissed"] = 1511] = "GroupDismissed";
	MessageType[MessageType["GroupMemberMuted"] = 1512] = "GroupMemberMuted";
	MessageType[MessageType["GroupMemberCancelMuted"] = 1513] = "GroupMemberCancelMuted";
	MessageType[MessageType["GroupMuted"] = 1514] = "GroupMuted";
	MessageType[MessageType["GroupCancelMuted"] = 1515] = "GroupCancelMuted";
	MessageType[MessageType["GroupMemberInfoUpdated"] = 1516] = "GroupMemberInfoUpdated";
	MessageType[MessageType["GroupMemberToAdmin"] = 1517] = "GroupMemberToAdmin";
	MessageType[MessageType["GroupAdminToNomal"] = 1518] = "GroupAdminToNomal";
	MessageType[MessageType["GroupAnnouncementUpdated"] = 1519] = "GroupAnnouncementUpdated";
	MessageType[MessageType["GroupNameUpdated"] = 1520] = "GroupNameUpdated";
	MessageType[MessageType["BurnMessageChange"] = 1701] = "BurnMessageChange";
	// notification
	MessageType[MessageType["RevokeMessage"] = 2101] = "RevokeMessage";
	MessageType[MessageType["HasReadReceiptMessage"] = 2150] = "HasReadReceiptMessage";
	MessageType[MessageType["GroupHasReadReceipt"] = 2155] = "GroupHasReadReceipt";
})(MessageType || (MessageType = {}));
var SessionType;
(function (SessionType) {
	SessionType[SessionType["Single"] = 1] = "Single";
	SessionType[SessionType["Group"] = 2] = "Group";
	SessionType[SessionType["WorkingGroup"] = 3] = "WorkingGroup";
	SessionType[SessionType["Notification"] = 4] = "Notification";
})(SessionType || (SessionType = {}));
var GroupStatus;
(function (GroupStatus) {
	GroupStatus[GroupStatus["Nomal"] = 0] = "Nomal";
	GroupStatus[GroupStatus["Baned"] = 1] = "Baned";
	GroupStatus[GroupStatus["Dismissed"] = 2] = "Dismissed";
	GroupStatus[GroupStatus["Muted"] = 3] = "Muted";
})(GroupStatus || (GroupStatus = {}));
var GroupAtType;
(function (GroupAtType) {
	GroupAtType[GroupAtType["AtNormal"] = 0] = "AtNormal";
	GroupAtType[GroupAtType["AtMe"] = 1] = "AtMe";
	GroupAtType[GroupAtType["AtAll"] = 2] = "AtAll";
	GroupAtType[GroupAtType["AtAllAtMe"] = 3] = "AtAllAtMe";
	GroupAtType[GroupAtType["AtGroupNotice"] = 4] = "AtGroupNotice";
})(GroupAtType || (GroupAtType = {}));
var GroupMemberFilter;
(function (GroupMemberFilter) {
	GroupMemberFilter[GroupMemberFilter["All"] = 0] = "All";
	GroupMemberFilter[GroupMemberFilter["Owner"] = 1] = "Owner";
	GroupMemberFilter[GroupMemberFilter["Admin"] = 2] = "Admin";
	GroupMemberFilter[GroupMemberFilter["Nomal"] = 3] = "Nomal";
	GroupMemberFilter[GroupMemberFilter["AdminAndNomal"] = 4] = "AdminAndNomal";
	GroupMemberFilter[GroupMemberFilter["AdminAndOwner"] = 5] = "AdminAndOwner";
})(GroupMemberFilter || (GroupMemberFilter = {}));
var Relationship;
(function (Relationship) {
	Relationship[Relationship["isBlack"] = 0] = "isBlack";
	Relationship[Relationship["isFriend"] = 1] = "isFriend";
})(Relationship || (Relationship = {}));
var LoginStatus;
(function (LoginStatus) {
	LoginStatus[LoginStatus["Logout"] = 1] = "Logout";
	LoginStatus[LoginStatus["Logging"] = 2] = "Logging";
	LoginStatus[LoginStatus["Logged"] = 3] = "Logged";
})(LoginStatus || (LoginStatus = {}));

/***/ }),

/***/ 0:
/***/ (function(module, exports) {

/* (ignored) */

/***/ }),

/***/ "0xDb":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (immutable) */ __webpack_exports__["c"] = parseTime;
/* unused harmony export formatTime */
/* harmony export (immutable) */ __webpack_exports__["b"] = md5Password;
/* harmony export (immutable) */ __webpack_exports__["d"] = setAppMainBgColor;
/* harmony export (immutable) */ __webpack_exports__["a"] = handleElTableLoopError;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_helpers_typeof__ = __webpack_require__("pFYg");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_helpers_typeof___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_babel_runtime_helpers_typeof__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_md5__ = __webpack_require__("NC6I");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_js_md5___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_js_md5__);

/**
 * Created by jiachenpan on 16/11/18.
 */


function parseTime(time, cFormat) {
	if (arguments.length === 0) {
		return null;
	}
	var format = cFormat || "{y}-{m}-{d} {h}:{i}:{s}";
	var date = void 0;
	if ((typeof time === "undefined" ? "undefined" : __WEBPACK_IMPORTED_MODULE_0_babel_runtime_helpers_typeof___default()(time)) === "object") {
		date = time;
	} else {
		if (("" + time).length === 10) time = parseInt(time) * 1000;
		date = new Date(time);
	}
	var formatObj = {
		y: date.getFullYear(),
		m: date.getMonth() + 1,
		d: date.getDate(),
		h: date.getHours(),
		i: date.getMinutes(),
		s: date.getSeconds(),
		a: date.getDay()
	};
	var time_str = format.replace(/{(y|m|d|h|i|s|a)+}/g, function (result, key) {
		var value = formatObj[key];
		if (key === "a") {
			return ["一", "二", "三", "四", "五", "六", "日"][value - 1];
		}
		if (result.length > 0 && value < 10) {
			value = "0" + value;
		}
		return value || 0;
	});
	return time_str;
}

function formatTime(time, option) {
	time = +time * 1000;
	var d = new Date(time);
	var now = Date.now();

	var diff = (now - d) / 1000;

	if (diff < 30) {
		return "刚刚";
	} else if (diff < 3600) {
		// less 1 hour
		return Math.ceil(diff / 60) + "分钟前";
	} else if (diff < 3600 * 24) {
		return Math.ceil(diff / 3600) + "小时前";
	} else if (diff < 3600 * 24 * 2) {
		return "1天前";
	}
	if (option) {
		return parseTime(time, option);
	} else {
		return d.getMonth() + 1 + "月" + d.getDate() + "日" + d.getHours() + "时" + d.getMinutes() + "分";
	}
}

function md5Password(password) {
	return __WEBPACK_IMPORTED_MODULE_1_js_md5___default()(password).toUpperCase();
}

// 设置 .app-main的背景颜色
function setAppMainBgColor(color) {
	var app = document.querySelector('.app-main');
	app && (app.style.backgroundColor = color || '');
}

// 解决 ElTable 自动宽度高度导致的「ResizeObserver loop limit exceeded」问题
function handleElTableLoopError(table) {
	var oldResizeListener = table.methods.resizeListener;
	if (window.requestAnimationFrame) {
		table.methods.resizeListener = function () {
			window.requestAnimationFrame(oldResizeListener.bind(this));
		};
	}
}

/***/ }),

/***/ "2K1W":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "7S6e":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (immutable) */ __webpack_exports__["y"] = getUserAccMenu;
/* harmony export (immutable) */ __webpack_exports__["B"] = getUserLoginInfo;
/* harmony export (immutable) */ __webpack_exports__["w"] = getUnreadMsgCount;
/* harmony export (immutable) */ __webpack_exports__["p"] = getPrintTemplateInfo;
/* harmony export (immutable) */ __webpack_exports__["j"] = getCustomPrintTemplateInfo;
/* harmony export (immutable) */ __webpack_exports__["m"] = getOneTscTemplate;
/* harmony export (immutable) */ __webpack_exports__["c"] = getAllAreas;
/* harmony export (immutable) */ __webpack_exports__["i"] = getCompanyConfigJson;
/* unused harmony export getCompanyConfigJsonByKey */
/* harmony export (immutable) */ __webpack_exports__["o"] = getOwnAppIds;
/* harmony export (immutable) */ __webpack_exports__["f"] = getClientPoint;
/* unused harmony export allAreaGet */
/* harmony export (immutable) */ __webpack_exports__["t"] = getQuestionList;
/* harmony export (immutable) */ __webpack_exports__["A"] = getUserConfigs;
/* harmony export (immutable) */ __webpack_exports__["I"] = saveOrUpdateUserConfigNew;
/* unused harmony export categoryListJSON */
/* harmony export (immutable) */ __webpack_exports__["r"] = getPubUserListJSON;
/* harmony export (immutable) */ __webpack_exports__["q"] = getPubSalerList;
/* harmony export (immutable) */ __webpack_exports__["K"] = setCompanyConfig;
/* harmony export (immutable) */ __webpack_exports__["h"] = getCompanyConfigByKey;
/* harmony export (immutable) */ __webpack_exports__["n"] = getOpenNavActivityData;
/* harmony export (immutable) */ __webpack_exports__["x"] = getUpdateOptActivitySiteRead;
/* harmony export (immutable) */ __webpack_exports__["b"] = accountListSelectJSON;
/* harmony export (immutable) */ __webpack_exports__["a"] = accountAllListSelectJSON;
/* harmony export (immutable) */ __webpack_exports__["d"] = getCertificationInfo;
/* harmony export (immutable) */ __webpack_exports__["C"] = getValueAddedServiceURL;
/* harmony export (immutable) */ __webpack_exports__["e"] = getClientCidURL;
/* harmony export (immutable) */ __webpack_exports__["F"] = queryProfessionalEnableTime;
/* unused harmony export getAppInfo */
/* harmony export (immutable) */ __webpack_exports__["H"] = saveLog;
/* harmony export (immutable) */ __webpack_exports__["G"] = saveInterfaceRequestTimeLog;
/* unused harmony export goodsExactSelectForOrder */
/* harmony export (immutable) */ __webpack_exports__["g"] = getCommonConfigs;
/* unused harmony export getGisCustomPrintConfigs */
/* harmony export (immutable) */ __webpack_exports__["l"] = getLocalPrinters;
/* harmony export (immutable) */ __webpack_exports__["J"] = sendCmdContentToPoint;
/* harmony export (immutable) */ __webpack_exports__["D"] = getWechatShopServiceState;
/* harmony export (immutable) */ __webpack_exports__["E"] = isExceedOnSaleCommodityLimit;
/* harmony export (immutable) */ __webpack_exports__["v"] = getTemplateList;
/* harmony export (immutable) */ __webpack_exports__["z"] = getUserAccResource;
/* harmony export (immutable) */ __webpack_exports__["k"] = getIsCompanyRegistrant;
/* harmony export (immutable) */ __webpack_exports__["u"] = getStorageSpace;
/* harmony export (immutable) */ __webpack_exports__["s"] = getPublicKeys;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise__ = __webpack_require__("//Fk");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_babel_runtime_helpers_extends__ = __webpack_require__("Dd8w");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_babel_runtime_helpers_extends___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_babel_runtime_helpers_extends__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_babel_runtime_core_js_json_stringify__ = __webpack_require__("mvHQ");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_babel_runtime_core_js_json_stringify___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_babel_runtime_core_js_json_stringify__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3__service_request__ = __webpack_require__("R/2u");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_qs__ = __webpack_require__("mw3O");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_qs___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_qs__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__utils_common__ = __webpack_require__("X2Oc");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_axios__ = __webpack_require__("mtWM");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_axios___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_6_axios__);








// 请求数据
function getUserAccMenu() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubmenu/userAccMenu.ac",
		method: "post"
	});
}

// 获取用户登录信息
function getUserLoginInfo() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/getUserInfo.ac",
		method: "get"
	});
}

// 获取用户登录信息
function getUnreadMsgCount() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/gis/message/getUnreadMsgCount.ac",
		method: "get"
	});
}

// 获取打印模板信息
function getPrintTemplateInfo(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/system/printTemplate/getPrintTemplateInfo.ac',
		params: params
	});
}

// 获取打印数据
function getCustomPrintTemplateInfo(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/cloudprint/barcode/gis/getPrinterCommand.ac',
		method: 'post',
		data: data
	});
}

// 获取吊牌打印模板详情
function getOneTscTemplate(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/cloudprint/cmd/gis/getOneTscTemplate.ac',
		method: 'post',
		data: data
	});
}

// 获取用户登录信息
function getAllAreas() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cdnServer + "/res/lib/area/allArea.json",
		method: "get",
		withCredentials: false
	});
}

// 获取公司信息
function getCompanyConfigJson() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/getCompanyConfigJson.ac",
		method: "post"
	});
}
// 根据configKey值获取公司信息
function getCompanyConfigJsonByKey(configKey) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/getCompanyConfigByKey.ac?configKey=" + configKey,
		method: "post"
	});
}

// 获取用户是否开通某服务
function getOwnAppIds(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubmenu/getOwnAppIds.ac",
		method: "post",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		data: __WEBPACK_IMPORTED_MODULE_4_qs___default.a.stringify(data)
	});
}

// 获取客户积分规则
function getClientPoint() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/consumerpoint/rule/getPointRules.ac',
		method: 'get'
	});
}

// 后台接口获取全部区域信息
function allAreaGet() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/inner/area/allAreaGet.ac',
		method: 'get'
	});
}

// 获取问题列表
function getQuestionList(keyword) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: 'https://www.qinsilk.com/mms/front/help/gis/getHelpListByPage.ac',
		params: { pageId: keyword }
	});
}

//	获取登录人配置，如查询配置记录；
function getUserConfigs(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/getUserConfigs.ac",
		method: "post",
		headers: {
			"Content-Type": "application/json"
		},
		data: __WEBPACK_IMPORTED_MODULE_2_babel_runtime_core_js_json_stringify___default()(data)
	});
}

//	保存登录人相关配置；
function saveOrUpdateUserConfigNew(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/saveOrUpdateUserConfigNew.ac",
		method: "post",
		headers: {
			"Content-Type": "application/json"
		},
		data: __WEBPACK_IMPORTED_MODULE_2_babel_runtime_core_js_json_stringify___default()(data)
	});
}

//	获取分类信息
function categoryListJSON(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/goods/category/categoryListJSON.ac",
		method: "post",
		headers: {
			"Content-Type": "application/json"
		},
		data: __WEBPACK_IMPORTED_MODULE_2_babel_runtime_core_js_json_stringify___default()(data)
	});
}

// 获取用户信息
function getPubUserListJSON(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/userSelectJSON.ac",
		params: params
	});
}
// 获取销售员
function getPubSalerList(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/userSelectJSONFilterComStore.ac",
		params: params
	});
}

function setCompanyConfig(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/setCompanyConfig.ac",
		params: params
	});
}

function getCompanyConfigByKey(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/getCompanyConfigByKey.ac",
		params: params
	});
}

// 导航活动数据
function getOpenNavActivityData() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/gis/optActivitySite/getOptActivitySite.ac?site=17",
		method: "post"
	});
}

// 千人千面上报已被点击接口
function getUpdateOptActivitySiteRead(site, optId) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/push/gis/optActivitySiteRead/updateOptActivitySiteRead.ac?site=' + site + '&optActivitySiteId=' + optId,
		method: "post"
	});
}

// 获取有权限看到的结算账户（分页）
function accountListSelectJSON(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/finance/account/accountListSelectJSON.ac",
		method: "post",
		headers: {
			"Content-Type": "multipart/form-data"
		},
		params: params
	});
}

// 获取有权限看到的结算账户（全部，用于判断权限）
function accountAllListSelectJSON(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/finance/account/accountAllListSelectJSON.ac",
		method: "post",
		headers: {
			"Content-Type": "multipart/form-data"
		},
		params: params
	});
}

// 公司认证信息
function getCertificationInfo(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/crmf/gis/merchantCertificate/getCertificateJSON.ac",
		method: "post",
		params: params
	});
}

// 获取增值服务跳转链接
function getValueAddedServiceURL() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cdnServer + "/dms/prod/" + (GLOBAL_ENV.IS_DEV ? "0b98455e9a0cb847204d2ea878e8c8e9.json" : "c2363c15b37cd2b1ea5251518dc8f6d1.json"),
		method: "get",
		withCredentials: false
	});
}

// 获取批量导出白名单
function getClientCidURL() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cdnServer + "/dms/prod/" + (GLOBAL_ENV.IS_DEV ? "ab5add4915428f086a8af73dac8d8647.json" : "d944c5f848232d1c0b8301a42f8e2629.json") + "?random=" + new Date().getTime(),
		method: "get",
		withCredentials: false
	});
}

// 获取是否开通 vip
function queryProfessionalEnableTime() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.mgrWebServer + "/comapp/queryProfessionalEnableTime.ac",
		method: "post"
	});
}

// 获取客户是否购买增值服务信息
function getAppInfo(id) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/system/companyConfig/getAppInfo.ac',
		method: 'post',
		params: { appId: id }
	});
}

// operate 必传，操作行为id
function saveLog(operate) {
	var parmas = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

	var hostname = window.location.hostname;
	if (hostname.includes("dev") || hostname.includes("localhost")) return;
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: "//qinsilk-log.cn-hangzhou.log.aliyuncs.com/logstores/log_store_tracking/track",
		method: "get",
		params: __WEBPACK_IMPORTED_MODULE_1_babel_runtime_helpers_extends___default()({
			'APIVersion': '0.6.0',
			'qsr': window.location.href,
			'client': 'gis-pc',
			"topic": operate || '',
			"operate": operate || '',
			'userid': Object(__WEBPACK_IMPORTED_MODULE_5__utils_common__["t" /* getCookie */])("qs_uid") || '',
			'cid': Object(__WEBPACK_IMPORTED_MODULE_5__utils_common__["t" /* getCookie */])("qs_cid") || '',
			'agent': Object(__WEBPACK_IMPORTED_MODULE_5__utils_common__["M" /* getWebBrowser */])()
		}, parmas),
		withCredentials: false
	});
}

// 记录接口的请求日志
// 记录接口的请求日志
function saveInterfaceRequestTimeLog() {
	var params = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

	var hostname = window.location.hostname;
	if (hostname.includes("dev") || hostname.includes("localhost")) return;
	var xhr = new XMLHttpRequest();
	var url = "//qinsilk-log.cn-hangzhou.log.aliyuncs.com/logstores/error_report_log/track";
	var paramString = new URLSearchParams(__WEBPACK_IMPORTED_MODULE_1_babel_runtime_helpers_extends___default()({
		'APIVersion': '0.6.0',
		'app': 'gis_pc',
		'userid': Object(__WEBPACK_IMPORTED_MODULE_5__utils_common__["t" /* getCookie */])("qs_uid") || '',
		'cid': Object(__WEBPACK_IMPORTED_MODULE_5__utils_common__["t" /* getCookie */])("qs_cid") || '',
		'device': Object(__WEBPACK_IMPORTED_MODULE_5__utils_common__["M" /* getWebBrowser */])()
	}, params)).toString();
	xhr.open('GET', url + "?" + paramString, true);
	xhr.withCredentials = false;
	xhr.onload = function () {
		if (xhr.status >= 200 && xhr.status < 300) {
			// 请求成功处理
			console.log('Request successful:', xhr.responseText);
		} else {
			// 请求出错处理
			console.error('Request error:', xhr.statusText);
		}
	};
	xhr.onerror = function () {
		// 网络错误处理
		console.error('Network error');
	};
	xhr.send();
}

// 从es查商品列表
function goodsExactSelectForOrder(data, categoryIdsStr) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/goods/goodsExactSelectForOrder.ac" + categoryIdsStr,
		method: "post",
		data: {},
		params: data
	});
}

// 获取移动端公共配置信息
function getCommonConfigs() {
	var baseUrl = BASE_URL.webServer.replace('ex.', 'syt.dev.').replace('dev.', 'syt.dev.').replace("/gis", "");
	// 如果是开发环境，获取生意通开发环境上的commonConfig.json
	baseUrl =  true ? baseUrl : 'https://syt.dev.qinsilk.com';
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: baseUrl + "/download/data/commonConfig.json?random=" + new Date().getTime(),
		method: "get",
		params: {
			withCredentials: false
		}
	});
}

// 获取驱动配置
function getGisCustomPrintConfigs() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.cdnServer + "/dms/prod/" + (GLOBAL_ENV.IS_DEV ? "26b0d3d61924f8fd84f2a36636cfda37.json" : "71cbd64984ae78a81cdf1929981b9adb.json"),
		method: "get",
		withCredentials: false
	});
}

// 给端口发送数据
var portList = ['8900', '8902', '8903'];
var port = null;
function getLocalPrinters(data) {
	var index = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;

	var url = "http://127.0.0.1:" + portList[index] + "/getLocalPrinters";
	port = portList[index];
	return new __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise___default.a(function (resolve, reject) {
		if (portList && portList[index]) {
			// 设置自定义超时时间
			__WEBPACK_IMPORTED_MODULE_6_axios___default.a.get(url, {
				timeout: 5000 // 设置超时时间为5秒
			}).then(function (response) {
				// 请求到数据 证明端口已经开启
				resolve(response);
			}).catch(function () {
				index++;
				getLocalPrinters(data, index).then(function () {
					// 如果成功的端口不是第一个，则把成功的端口放在第一个，失败的端口放最后，下次请求时直接从成功的端口开始请求，减少请求时间
					if (index > 0) {
						var delPortList = portList.splice(0, index);
						portList = portList.concat(delPortList);
					}
					resolve();
				}, function () {
					reject();
				});
			});
		} else {
			reject();
		}
	});
}

// 通过端口发送打印数据
function sendCmdContentToPoint(data) {
	var url = "http://127.0.0.1:" + port + "/print";
	return new __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise___default.a(function (resolve, reject) {
		// 设置自定义超时时间和其他配置
		data.timeout = 5000; // 设置超时时间为5秒
		__WEBPACK_IMPORTED_MODULE_6_axios___default.a.post(url, data).then(function (response) {
			resolve(response);
		}).catch(function () {
			reject();
		});
	});
}
// 获取用户销货宝的开通状态
function getWechatShopServiceState() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/shop/wechat/memberOrders/getWechatShopServiceState.ac',
		method: 'post'
	});
}
// 检查商品是否超出最大上架商品数
function isExceedOnSaleCommodityLimit(number) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/shop/wechat/v2/commodity/isExceedOnSaleCommodityLimit.ac?number=" + number,
		method: "post"
	});
}
// 获取运费设置模板列表
function getTemplateList(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/shop/wechat/deliveryfeetemplet/deliveryFeeTempletListJSONNew.ac",
		method: "post",
		params: params
	});
}

// 获取权限列表
function getUserAccResource() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubmenu/userAccResource.ac",
		method: "post"
	});
}

// 获取是否为注册人

function getIsCompanyRegistrant() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/isCompanyRegistrant.ac",
		method: "post"
	});
}

// 获取用户存储空间
function getStorageSpace() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/storageQuota/getStorageQuotaInfo.ac",
		method: "post"
	});
}

// 获取公钥
function getPublicKeys() {
	return Object(__WEBPACK_IMPORTED_MODULE_3__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/security/publicKeys.ac",
		method: "get"
	});
}

/***/ }),

/***/ "7xIN":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "7yFX":
/***/ (function(module, exports) {

module.exports = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAJ4SURBVDhPtZRNTBNREMefFxox1pjo0XjQm4kmGlG8EBI86cULMUpEPJAoFOLJk6kaLzV+HEwqqBeNH8RGolCgHrC0lLRaDMJB2tIWS9JtZXfZrW0tbWnHeduuFLrb1hgn+e9m35v9vXnzZh4h/9XarPvJ1ZkGonMdJ73OY1XV9amRdM0eJqfMOzfG1TldTx74rp0wC7PtNp67YGX59gmWk2TjylWcu2hlV1rHBWbPy+gouT7XtA69F7hyyfkLgjmANABkUPQti37LKh3P4ngcZcHHoYHIPNG59yFUX3fgVdj5jc7+gxl8AOT2fCcC++ubh5kFUQXGp3PwIZKBZ4urYGczkFzLK3qaogB1xqBeAjYNRby8gpuLy8DJjyIQEydJgzo7FQN/fK3M+20EYFvf4s0CcDjq4Ta5BJI5OGgRgAzwcH8hBQ4+C7qZJJAXHJz/nIBsfmOkJgaBjxZvqAIHmTTCOOiYTvxZisXt7zCLsHdMBCaFJ1hiJhphJeB3jNDgTcFcbH17T0O4yLsVaHUnILUpl1WBpavTWJ6H06C1iNDo+AlehRz+FXBkOQO7xmPQ4opDECNXsgIwpJ5D+acs5r4ND0MzKoBbLD9d2a/mCOlZ0tzd8qVgVTk4iVkzkDp/EbIwhMWdUClqCVitbOStxBFyeiIG2tccWFn1/pSAxkChsJvNjE9QaT2aw37cbo87DrSU1GwQW2+rMUSBOs2RN+GvS8otWvN18WQJL4e7/l56hW3RPgwY9J48VMh5RXAAM9EywnKkZ+po4U7ssO/e3hd6fGbsR6LbwUO3bbkge1GT+JZFx4rzOhy7PMlDw/uoh9zxn6PB/QaRbtEKEMLb8gAAAABJRU5ErkJggg=="

/***/ }),

/***/ "9x2J":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "BfUi":
/***/ (function(module, exports) {

// ----------------------------------
// 定义全局常量
// ----------------------------------
/**
 * 对Date的扩展，将 Date 转化为指定格式的String
 * 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
 * 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
 * 例子：
 * (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
 * (new Date()).Format("yyyy-M-d h:m:s.S") ==> 2006-7-2 8:9:4.18
 *
 */
window.Date.prototype.Format = function (fmt) {
	// author: meizz
	var o = {
		"M+": this.getMonth() + 1, // 月份
		"d+": this.getDate(), // 日
		"h+": this.getHours(), // 小时
		"m+": this.getMinutes(), // 分
		"s+": this.getSeconds(), // 秒
		"q+": Math.floor((this.getMonth() + 3) / 3), // 季度
		S: this.getMilliseconds()
		// 毫秒
	};
	if (/(y+)/.test(fmt)) {
		fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
	}
	for (var k in o) {
		if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, RegExp.$1.length == 1 ? o[k] : ("00" + o[k]).substr(("" + o[k]).length));
	}
	return fmt;
};

window.GL_CONS = {};

// 增值服务
window.GL_CONS.ADDEDSERVICE_URL = {
	// 销货
	gsmIntroduce: "//syt.qinsilk.com/paymentservice/depositWechatAppShopBase.html",
	// 客户积分
	customerIntegral: "/app/openMyAppPage.ac?id=5",
	// 短信购买
	smsPurchase: "/paymentservice/applyBuySmsPackage.ac",
	// 客户分类管理
	customCateLink: "/static/view#/sale/client/clientClassifyItem?mid=4",
	// 短信服务
	smsService: "/admin/inner/sms/smsMain.ac?mid=4",
	// 客户管理
	customManager: "/admin/inner/client/clientList.ac?mid=4",
	// 改版客户详情
	customDetail: "/static/view#/sale/client/detail?mid=4&clientId="
};

window.GL_CONS.HELP_URL = {
	bindShopMemberHelp: "https://www.qinsilk.com/mms/front/help/gis/question-id1109.html", // 绑定微商城会员
	clientListHelp: "//www.qinsilk.com/mms/front/help/gis/help-id212.html", // 客户管理介绍
	clientItemList: "//www.qinsilk.com/mms/front/help/gis/help-id480.html", // 客户分类
	smsServiceHelp: "//www.qinsilk.com/mms/front/help/gis/help-id872.html", // 短信服务介绍
	clientPointHelp: "//www.qinsilk.com/mms/front/help/gis/help-id360.html", // 客户积分介绍
	memberCardHelp: "//www.qinsilk.com/mms/front/help/gis/help-id1084.html", // 会员卡介绍、充值介绍
	wechatMemberCardHelp: "//www.qinsilk.com/mms/front/help/gis/help-id1085.html", // 微信会员卡介绍
	wechatOrderListHelp: "//www.qinsilk.com/mms/front/help/gis/help-id220.html", // 订单处理介绍
	distributionHelp: "//www.qinsilk.com/mms/front/help/gis/question-id1086.html", // 分销功能介绍
	replaceClientMemberHelp: "//cloud.qinsilk.com/document/front/help/gis/question-id1137.html", // 更换会员
	wechatFrontManagerHelp: "https://www.qinsilk.com/mms/front/help/gis/question-id913.html", // 店面管理介绍
	wechatShopHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id616.html", // 店铺概况介绍
	wechatPaySettingHelp: "http://www.qinsilk.com/mms/m/help/help-detail-405.html", // 支付渠道介绍,
	deliveryfeetempletHelp: "https://www.qinsilk.com/mms/front/help/gis/question-id759.html", // 如何设置运费模板,
	wechatCommodityListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id919.html", // 销货宝上架商品
	shopDecorationHelp: "http://cloud.qinsilk.com/document/m/help/gis/help-detail-1179.html", // 首页自定义帮助文档
	unitListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id190.html#%E5%8D%95%E4%BD%8D%E7%AE%A1%E7%90%86", // 单位管理
	blandListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id190.html#%E5%93%81%E7%89%8C%E7%AE%A1%E7%90%86", // 品牌管理
	categoryListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id190.html#%E5%95%86%E5%93%81%E5%88%86%E7%B1%BB", // 商品分类
	accountItemList: "https://www.qinsilk.com/mms/front/help/gis/help-id216.html#", // 账目类型
	accountList: "https://www.qinsilk.com/mms/front/help/gis/help-id215.html#", // 结算账户
	barcodeConfigPage: "https://www.qinsilk.com/mms/front/help/gis/help-id190.html#%E6%9D%A1%E7%A0%81%E7%AE%A1%E7%90%86", // 条码管理
	operateLogList: "https://www.qinsilk.com/mms/front/help/gis/help-id196.html#", // 系统日志
	resetPage: "https://www.qinsilk.com/mms/front/help/gis/help-id244.html#", // 系统重置
	personalInfo: "https://www.qinsilk.com/mms/front/help/gis/help-id191.html", // 个人信息
	bulletinInnerListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id193.html#", // 公司公告
	comStoreListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id192.html#", // 门店与员工
	roleListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id991.html", // 角色管理
	deliveryCompanyListHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id194.html#", // 物流设置
	companyConfigHelp: "//www.qinsilk.com/mms/front/help/gis/help-id195.html", // 系统参数
	wxappVersion: "//cloud.qinsilk.com/document/front/help/gis/help-id1258.html", // 查看小程序版本号
	clientUserStoreHelp: "http://cloud.qinsilk.com/document/front/help/gis/help-id1261.html", // 客户所属门店 销售员
	clientRemarkSearchHelp: "http://cloud.qinsilk.com/document/front/help/gis/help-id1276.html", // 客户信息备注及搜索功能设置教程
	clientPointUseHelp: "https://www.qinsilk.com/paymentservice/customerIntegral.html", // 客户积分购买页面
	clientPointEditHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id861.html", // 客户积分修改帮助文档
	liveManagementHelp: "http://www.qinsilk.com/mms/front/help/gis/help-id1290.html", // 小程序直播教程
	clientLabelHelp: 'https://cloud.qinsilk.com/document/front/help/gis/help-id1458.html', // 客户标签帮助文档
	shopNoticesHelp: 'https://cloud.qinsilk.com/document/m/help/gis/help-detail-1179.html', // 店铺公告帮助文档
	bindMemberHelp: 'https://cloud.qinsilk.com/document/front/help/gis/help-id1109.html', // 绑定微商城会员
	salePayRecordListHelp: 'https://www.qinsilk.com/mms/front/help/gis/help-id763.html', // 收款流水帮助文档
	goodsList: 'https://www.qinsilk.com/mms/front/help/gis/help-id190.html?qsr=right-help-doc#%E5%95%86%E5%93%81%E7%AE%A1%E7%90%86', // 商品管理帮助文档
	goodsListHelp: 'https://www.qinsilk.com/mms/front/help/gis/help-id1842.html',
	printBarcodeListHelp: 'https://www.qinsilk.com/mms/front/help/gis/help-id235.html?qsr=right-help-doc#', // 条码打印帮助文档
	goodsSnList: 'https://www.qinsilk.com/mms/front/help/gis/help-id0.html?pageId=3',
	purchaseReport: 'https://www.qinsilk.com/mms/front/help/gis/help-id203.html?qsr=right-help-doc#', // 采购报表帮助文档
	clientSaleReport: 'https://www.qinsilk.com/mms/front/help/gis/help-id206.html?qsr=right-help-doc#', // 客户销量
	saleReportByGoods: 'https://www.qinsilk.com/mms/front/help/gis/help-id207.html?qsr=right-help-doc#', // 商品销量
	storeReport: 'https://www.qinsilk.com/mms/front/help/gis/help-id205.html?qsr=right-help-doc#', // 盘点报表
	currentAccmulatedPointHelp: "https://cloud.qinsilk.com/document/front/help/gis/question-id1586.html", // 当前累计积分，当前剩余积分文档
	transfersReport: 'https://www.qinsilk.com/mms/front/help/gis/help-id508.html?qsr=right-help-doc#', // 调拨报表
	inStoreReport: 'https://www.qinsilk.com/mms/front/help/gis/help-id1032.html?qsr=right-help-doc#', // 入库报表
	outStoreReport: 'https://www.qinsilk.com/mms/front/help/gis/help-id1032.html?qsr=right-help-doc#', // 出库报表
	saleReport: 'https://www.qinsilk.com/mms/front/help/gis/help-id204.html?qsr=right-help-doc#', // 销售报表
	accountRecordClientList: "https://www.qinsilk.com/mms/front/help/gis/help-id213.html?qsr=right-help-doc#", // 客户对账及收款文档
	sendMailHelp: "https://www.qinsilk.com/mms/front/help/gis/help-id189.html", // 发送邮件
	accountRecordCompanyList: 'https://www.qinsilk.com/mms/front/help/gis/help-id214.html?qsr=right-help-doc#', // 账户流水及记账
	storehouseList: 'https://www.qinsilk.com/mms/front/help/gis/help-id201.html?qsr=right-help-doc#', // 仓库管理
	goodsStoredRecordList: 'https://www.qinsilk.com/mms/front/help/gis/help-id200.html?qsr=right-help-doc#', // 仓库流水
	clientActiveReportHelp: 'http://cloud.qinsilk.com/document/front/help/gis/question-id1722.html', // 客户活跃分析
	wechatProgramHelp: 'https://www.qinsilk.com/mms/front/help/gis/help-id1478.html', // 专属品牌小程序
	achievementReport: 'http://cloud.qinsilk.com/document/front/help/gis/help-id1780.html', // 门店员工业绩报表
	customerServiceHelp: "https://www.qinsilk.com/mms/front/help/help-id1953.html", // 客服工具
	batchGoodsStoredListHelp: "http://cloud.qinsilk.com/document/front/help/gis/help-id1823.html", // 批次管理
	storageLocationManageListHelp: "http://cloud.qinsilk.com/document/front/help/gis/help-id1235.html", // 库位管理
	customAttributeHelp: "http://cloud.qinsilk.com/document/front/help/gis/help-id1897.html", // 自定义属性管理
	clientOrderDebtDetailsHelp: "http://cloud.qinsilk.com/document/front/help/gis/help-id1813.html", // 单据欠款明细
	specManage: "http://cloud.qinsilk.com/document/front/help/gis/help-id1836.html", // 单据欠款明细
	microMailActivitiesPage: 'https://syt.qinsilk.com/paymentservice/depositWechatAppShopBase.html', // 销货宝微商城购买页面
	quotation: 'http://cloud.qinsilk.com/document/front/help/gis/help-id1896.html' // 报价单帮助文档
};
window.GL_CONS.BANLANCE_BUSINESS_SN_REF = [{ val: 'CG', text: BASE_URL.webServer + "/admin/inner/orders/purchase/purchaseList.ac?mid=2&onLoadOrdersSn=" }, { val: 'CT', text: BASE_URL.webServer + "/admin/inner/orders/purchase/rejectPurchaseList.ac?mid=2&onLoadOrdersSn=" }, { val: 'XS', text: BASE_URL.webServer + "/admin/inner/sale/wholesaleOrdersList.ac?mid=4&onLoadOrdersSn=" }, { val: 'XT', text: BASE_URL.webServer + "/admin/inner/sale/rejectOrdersList.ac?mid=4&onLoadOrdersSn=" }, { val: 'PD', text: BASE_URL.webServer + "/admin/inner/storehouse/storeOrderList.ac?mid=3&onLoadOrdersSn=" }, { val: 'IMPORT', text: BASE_URL.webServer + "/admin/inner/storehouse/storeOrderList.ac?mid=3&onLoadOrdersSn=" }, { val: 'DB', text: BASE_URL.webServer + "/admin/inner/storehouse/storeTransferOrder/storeTransferOrderList.ac?mid=3&onLoadOrdersSn=" }, { val: 'ZZ', text: BASE_URL.webServer + "/admin/inner/goods/assembly/assemblyOrdersList.ac?mid=3&onLoadOrdersSn=" }, { val: 'CX', text: BASE_URL.webServer + "/admin/inner/goods/assembly/assemblyOrdersList.ac?mid=3&onLoadOrdersSn=" }, { val: 'CK', text: BASE_URL.webServer + "/admin/inner/storehouse/wout/storeOutOrdersList.ac?mid=3&onLoadOrdersSn=" }, { val: 'RK', text: BASE_URL.webServer + "/admin/inner/storehouse/win/storeInOrdersList.ac?mid=3&onLoadOrdersSn=" },
/** DR是待入库，DC指待出库，原本应该是DRK和DCK，但是因为截取的时候只用2位，所以用DC和DR*/
{ val: 'DC', text: BASE_URL.webServer + "/admin/inner/storehouse/wout/storeOutOrdersList.ac?mid=3&onLoadOrdersSn=" }, { val: 'DR', text: BASE_URL.webServer + "/admin/inner/storehouse/win/storeInOrdersList.ac?mid=3&onLoadOrdersSn=" }, { val: 'WD', text: BASE_URL.webServer + "/static/view#/onlineStore/gsm/order/orderDetail/" }];
// ----------------------------------
// 定义全局常量 end
// ----------------------------------

/***/ }),

/***/ "DZlS":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "EdkY":
/***/ (function(module, exports) {

module.exports = "data:image/png;base64,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"

/***/ }),

/***/ "GSXG":
/***/ (function(module, exports) {

module.exports = "data:image/png;base64,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"

/***/ }),

/***/ "I+UZ":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "IcnI":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/vue/dist/vue.esm.js
var vue_esm = __webpack_require__("7+uW");

// EXTERNAL MODULE: ./node_modules/vuex/dist/vuex.esm.js
var vuex_esm = __webpack_require__("NYxO");

// EXTERNAL MODULE: ./node_modules/babel-runtime/regenerator/index.js
var regenerator = __webpack_require__("Xxa5");
var regenerator_default = /*#__PURE__*/__webpack_require__.n(regenerator);

// EXTERNAL MODULE: ./node_modules/babel-runtime/helpers/asyncToGenerator.js
var asyncToGenerator = __webpack_require__("exGp");
var asyncToGenerator_default = /*#__PURE__*/__webpack_require__.n(asyncToGenerator);

// EXTERNAL MODULE: ./node_modules/babel-runtime/core-js/json/stringify.js
var stringify = __webpack_require__("mvHQ");
var stringify_default = /*#__PURE__*/__webpack_require__.n(stringify);

// EXTERNAL MODULE: ./node_modules/babel-runtime/core-js/promise.js
var promise = __webpack_require__("//Fk");
var promise_default = /*#__PURE__*/__webpack_require__.n(promise);

// EXTERNAL MODULE: ./node_modules/babel-runtime/helpers/typeof.js
var helpers_typeof = __webpack_require__("pFYg");
var typeof_default = /*#__PURE__*/__webpack_require__.n(helpers_typeof);

// EXTERNAL MODULE: ./src/service/common.js
var common = __webpack_require__("7S6e");

// EXTERNAL MODULE: ./src/service/onlineStore/decoration/edit.js
var edit = __webpack_require__("k8iF");

// CONCATENATED MODULE: ./src/store/modules/user.js









var GetCompanyConfigJsonPromise = null;
var GetPublicKeysConfigPromise = null;
//移除不需要展示的菜单
var removeMenuItem = function removeMenuItem(arr, key) {
	if (Array.isArray(arr) && arr.length > 0) {
		for (var i = 0; i < arr.length; i++) {
			if (arr[i].pTableVO.url) {
				if (arr[i].pTableVO.url.indexOf(key) > -1 && arr[i].pTableVO.url.indexOf(key + '/') == -1) {
					arr.splice(i, 1); // 从原始数组中移除该元素
					break;
				} else {
					removeMenuItem(arr[i].lstSubHierarchyVO, key);
				}
			} else {
				removeMenuItem(arr[i].lstSubHierarchyVO, key);
			}
		}
	}
};
var user_customDeepCopy = function customDeepCopy(obj) {
	var result = Array.isArray(obj) ? [] : {};
	for (var key in obj) {
		if (obj.hasOwnProperty(key)) {
			if (obj[key] === null) {
				result[key] = null;
			} else if (typeof_default()(obj[key]) === "object") {
				// 深拷贝日期类型
				if (obj[key] instanceof Date) {
					result[key] = new Date(obj[key].valueOf());
				} else {
					result[key] = customDeepCopy(obj[key]); // 递归复制
				}
			} else {
				result[key] = obj[key];
			}
		}
	}
	return result;
};
var user_isSyInventoryQuery = function isSyInventoryQuery() {
	return new promise_default.a(function (resolve, reject) {
		var syInventoryQueryMenu = false;
		Object(common["A" /* getUserConfigs */])({ device: 2 }).then(function (userConfigRes) {
			if (userConfigRes && userConfigRes.statusCode == 1) {
				var userCfg = userConfigRes.object ? userConfigRes.object : [];
				var syInventoryQueryMenuObj = userCfg.find(function (item) {
					return item.configKey === "syInventoryQueryMenu";
				});
				if (syInventoryQueryMenuObj && syInventoryQueryMenuObj.configValue) {
					syInventoryQueryMenu = parseInt(syInventoryQueryMenuObj.configValue) == 1;
				} else {
					syInventoryQueryMenu = false;
				}
			}
			resolve(syInventoryQueryMenu);
		}).catch(function () {
			resolve(syInventoryQueryMenu);
		});
	});
};
var user_getUserConfigsByDevice = function getUserConfigsByDevice(device) {
	return new promise_default.a(function (resolve, reject) {
		Object(common["A" /* getUserConfigs */])({ device: device || 2 }).then(function (userConfigRes) {
			var userCfg = [];
			if (userConfigRes && userConfigRes.statusCode == 1) {
				userCfg = userConfigRes.object ? userConfigRes.object : [];
			}
			resolve(userCfg);
		}).catch(function () {
			resolve([]);
		});
	});
};
var user = {
	state: {
		menuList: null,
		userLoginInfo: null,
		companyInfo: null,
		companyConfigList: null,
		certificationInfo: null,
		actionAccessRuleList: null, // 独立增值服务权限列表
		openprofession: null, // 是否开通专业版
		publicKeysConfig: null // 公钥配置
	},

	mutations: {
		SET_MENU: function SET_MENU(state, menuList) {
			state.menuList = menuList;
		},
		SET_USER_LOGIN_INFO: function SET_USER_LOGIN_INFO(state, userLoginInfo) {
			state.userLoginInfo = userLoginInfo;
		},
		SET_COMPANY_CONFIG: function SET_COMPANY_CONFIG(state, company) {
			state.companyInfo = company.company;
			state.actionAccessRuleList = company.actionAccessRuleList;
			state.companyConfigList = company.companyConfigList;
		},
		SET_CERTIFICATION_INFO: function SET_CERTIFICATION_INFO(state, info) {
			state.certificationInfo = info;
		},
		SET_PROFESSION_STATUS: function SET_PROFESSION_STATUS(state, status) {
			state.openprofession = status;
		},
		SET_PUBLIC_KEYS_CONFIG: function SET_PUBLIC_KEYS_CONFIG(state, config) {
			state.publicKeysConfig = config;
		}
	},

	actions: {
		// 获取用户菜单
		GetUserMenuList: function GetUserMenuList(_ref) {
			var commit = _ref.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(common["y" /* getUserAccMenu */])().then(function (response) {
					commit("SET_MENU", response);
					resolve(response);
					// let flag = false;//判断有没有交接班和车次对账白名单
					// let trainAccountingMenu, //判断有没有车次对账菜单白名单
					// 			exceptionReportMenu, //判断有没有异常提报处理菜单白名单
					// 			syInventoryQueryMenu, //判断有没有顺誉库存查询菜单白名单
					// 			employeeScheduleMenu = false; //判断有没有员工排班菜单白名单
					// getCompanyConfigJsonByKey('shiftAndTrainAccounting').then(async (companyRes) => {
					//   if(companyRes.statusCode == 1 && companyRes.object.configValue){
					//     flag = parseInt(companyRes.object.configValue) == 1;
					//   } else {
					//     flag = false;
					// 	}
					// 	const userCfg = await getUserConfigsByDevice();
					// 	if (userCfg && userCfg.length > 0) {
					// 		if (flag) {
					// 			// 如果开启了交接班白名单
					// 			const trainAccountingMenuObj = userCfg.find(item => item.configKey === "trainAccountingMenu");
					// 			const exceptionReportMenuObj = userCfg.find(item => item.configKey === "exceptionReportMenu");
					// 			if (trainAccountingMenuObj && trainAccountingMenuObj.configValue) {
					// 				trainAccountingMenu = parseInt(trainAccountingMenuObj.configValue) == 1;
					// 			} else {
					// 				trainAccountingMenu = false;
					// 			}
					// 			if (exceptionReportMenuObj && exceptionReportMenuObj.configValue) {
					// 				exceptionReportMenu = parseInt(exceptionReportMenuObj.configValue) == 1;
					// 			} else {
					// 				exceptionReportMenu = false;
					// 			}
					// 		}
					// 		const syInventoryQueryMenuObj = userCfg.find(item => item.configKey === "syInventoryQueryMenu");
					// 		const employeeScheduleMenuObj = userCfg.find(item => item.configKey === "rotaEmployeeScheduleMenu");
					// 		if (syInventoryQueryMenuObj && syInventoryQueryMenuObj.configValue) {
					// 			syInventoryQueryMenu = parseInt(syInventoryQueryMenuObj.configValue) == 1;
					// 		} else {
					// 			syInventoryQueryMenu = false;
					// 		}
					// 		if (employeeScheduleMenuObj && employeeScheduleMenuObj.configValue) {
					// 			employeeScheduleMenu = parseInt(employeeScheduleMenuObj.configValue) == 1;
					// 		} else {
					// 			employeeScheduleMenu = false;
					// 		}
					// 		if (exceptionReportMenu && trainAccountingMenu && syInventoryQueryMenu && employeeScheduleMenu) {
					// 			commit("SET_MENU", response);
					// 			resolve(response);
					// 		} else {
					// 			const newRes = customDeepCopy(response);
					// 			if (!trainAccountingMenu) {
					// 				removeMenuItem(newRes, 'trainReconciliation'); //过滤车次对账
					// 			}
					// 			if (!exceptionReportMenu) {
					// 				removeMenuItem(newRes, 'handlingAbnormalReporting'); //过滤异常提报
					// 			}
					// 			if (!syInventoryQueryMenu) {
					// 				removeMenuItem(newRes, 'syInventoryQuery'); //过滤顺誉库存查询
					// 			}
					// 			if (!employeeScheduleMenu) {
					// 				removeMenuItem(newRes, 'employeeScheduling'); //过滤员工排班
					// 			}
					// 			commit("SET_MENU", newRes);
					// 			resolve(newRes);
					// 		}
					// 	} else {
					// 		const newRes = customDeepCopy(response);
					// 		removeMenuItem(newRes, 'trainReconciliation'); //过滤车次对账
					// 		removeMenuItem(newRes, 'handlingAbnormalReporting'); //过滤异常提报
					// 		removeMenuItem(newRes, 'syInventoryQuery'); //过滤顺誉库存查询
					// 		removeMenuItem(newRes, 'employeeScheduling'); //过滤员工排班
					// 		commit("SET_MENU", newRes);
					// 		resolve(newRes);
					// 	}
					// }).catch(async () => {
					//   //没有车次对账白名单则移除车次对账菜单和异常提报菜单
					// 	const newRes = customDeepCopy(response);
					// 	removeMenuItem(newRes, 'trainReconciliation'); //过滤车次对账
					// 	removeMenuItem(newRes, 'handlingAbnormalReporting'); //过滤异常提报
					// 	const userCfg = await getUserConfigsByDevice();
					// 	if (userCfg && userCfg.length > 0) {
					// 		const syInventoryQueryMenuObj = userCfg.find(item => item.configKey === "syInventoryQueryMenu");
					// 		const employeeScheduleMenuObj = userCfg.find(item => item.configKey === "rotaEmployeeScheduleMenu");
					// 		if (syInventoryQueryMenuObj && syInventoryQueryMenuObj.configValue) {
					// 			syInventoryQueryMenu = parseInt(syInventoryQueryMenuObj.configValue) == 1;
					// 		} else {
					// 			syInventoryQueryMenu = false;
					// 		}
					// 		if (employeeScheduleMenuObj && employeeScheduleMenuObj.configValue) {
					// 			employeeScheduleMenu = parseInt(employeeScheduleMenuObj.configValue) == 1;
					// 		} else {
					// 			employeeScheduleMenu = false;
					// 		}
					// 		if (!syInventoryQueryMenu) {
					// 			removeMenuItem(newRes, 'syInventoryQuery'); //过滤顺誉库存查询
					// 		}
					// 		if (!employeeScheduleMenu) {
					// 			removeMenuItem(newRes, 'employeeScheduling'); //过滤员工排班
					// 		}
					// 	} else {
					// 		removeMenuItem(newRes, 'employeeScheduling'); //过滤员工排班
					// 		removeMenuItem(newRes, 'syInventoryQuery'); //过滤顺誉库存查询
					// 	}
					//   commit("SET_MENU", newRes);
					//   resolve(newRes);
					// })
				}).catch(function (error) {
					reject(error);
				});
			});
		},

		// 获取用户登录信息
		GetUserLoginInfo: function GetUserLoginInfo(_ref2) {
			var commit = _ref2.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(common["B" /* getUserLoginInfo */])().then(function (response) {
					if (response && response.statusCode == 1) {
						commit("SET_USER_LOGIN_INFO", response.object);
						resolve(response.object);
					}
				}).catch(function (error) {
					reject(error);
				});
			});
		},

		// 获取公司账号信息
		GetCompanyConfigJson: function GetCompanyConfigJson(_ref3) {
			var state = _ref3.state,
			    commit = _ref3.commit,
			    dispatch = _ref3.dispatch;

			return new promise_default.a(function (resolve, reject) {
				Object(common["i" /* getCompanyConfigJson */])().then(function (response) {
					if (response.statusCode == 1) {
						!state.certificationInfo && dispatch("getCertificationInfo", response.object.company.comName);
						commit("SET_COMPANY_CONFIG", response.object);
						resolve(JSON.parse(stringify_default()(response.object)));
					}
				}).catch(function (error) {
					reject(error);
				});
			});
		},

		// 获取公司账号信息,只获取一次
		GetCompanyConfigJsonOnlyOnce: function GetCompanyConfigJsonOnlyOnce(_ref4) {
			var _this = this;

			var state = _ref4.state,
			    dispatch = _ref4.dispatch,
			    commit = _ref4.commit;

			if (GetCompanyConfigJsonPromise) {
				return GetCompanyConfigJsonPromise;
			} else {
				return GetCompanyConfigJsonPromise = new promise_default.a(function (resolve, reject) {
					Object(common["i" /* getCompanyConfigJson */])().then(function () {
						var _ref5 = asyncToGenerator_default()( /*#__PURE__*/regenerator_default.a.mark(function _callee(response) {
							return regenerator_default.a.wrap(function _callee$(_context) {
								while (1) {
									switch (_context.prev = _context.next) {
										case 0:
											if (response.statusCode == 1) {
												!state.certificationInfo && dispatch("getCertificationInfo", response.object.company.comName);
												commit("SET_COMPANY_CONFIG", response.object);
												resolve(JSON.parse(stringify_default()(response.object)));
											}

										case 1:
										case 'end':
											return _context.stop();
									}
								}
							}, _callee, _this);
						}));

						return function (_x) {
							return _ref5.apply(this, arguments);
						};
					}()).catch(function (error) {
						reject(error);
					});
				});
			}
		},

		// 获取公共密钥
		GetPublicKeysConfig: function GetPublicKeysConfig(_ref6) {
			var state = _ref6.state,
			    dispatch = _ref6.dispatch,
			    commit = _ref6.commit;

			if (GetPublicKeysConfigPromise) {
				return GetPublicKeysConfigPromise;
			} else {
				return GetPublicKeysConfigPromise = new promise_default.a(function (resolve, reject) {
					Object(common["s" /* getPublicKeys */])().then(function (response) {
						if (response.statusCode == 1) {
							commit("SET_PUBLIC_KEYS_CONFIG", response.object);
							resolve(JSON.parse(stringify_default()(response.object)));
						} else {
							resolve({});
						}
					}).catch(function (error) {
						reject(error);
					});
				});
			}
		},

		// 获取公司认证信息
		getCertificationInfo: function getCertificationInfo(_ref7, name) {
			var commit = _ref7.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(common["d" /* getCertificationInfo */])({ companyName: name }).then(function (response) {
					if (response && response.statusCode === 1) {
						commit("SET_CERTIFICATION_INFO", response.object);
					}
					resolve(response);
				}).catch(function (error) {
					reject(error);
				});
			});
		},

		// 获取是否开通专业版
		getProfessionStatus: function getProfessionStatus(_ref8) {
			var state = _ref8.state,
			    commit = _ref8.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(edit["getFunctionsState"])().then(function (res) {
					if (res.statusCode == 1) {
						commit("SET_PROFESSION_STATUS", res.object.ownAppIds.some(function (item) {
							return item == 24;
						}));
					}
					resolve(res);
				}).catch(function (err) {
					reject(err);
				});
			});
		}
	}
};

/* harmony default export */ var modules_user = (user);
// EXTERNAL MODULE: ./src/service/marketing/subMarketing/smsService/sms-service.js
var sms_service = __webpack_require__("mGB5");

// CONCATENATED MODULE: ./src/store/modules/sms.js



var sms_user = {
	state: {
		// 短信分类列表
		smsCateList: [],
		// 客户分类列表
		clientItems: [],
		// 短信账号信息
		smsAccountInfo: {},
		// 短信分类详细信息
		smsCateContentList: [],
		// 活动营销分类信息
		activityCate: {}
	},

	mutations: {
		// 设置客户分类信息
		SET_SMS_CLIENTITEMS: function SET_SMS_CLIENTITEMS(state, list) {
			state.clientItems = list;
		},
		// 设置短信账户信息
		SET_SMS_ACCOUNTINFO: function SET_SMS_ACCOUNTINFO(state, mes) {
			state.smsAccountInfo = mes;
		},
		// 设置某个短信分类详细信息
		SET_SMS_CONTENTLIST: function SET_SMS_CONTENTLIST(state, list) {
			state.smsCateContentList = list;
		},
		// 设置某个短信分类项信息
		SET_SMS_CONTENTLIST_ITEM: function SET_SMS_CONTENTLIST_ITEM(state, obj) {
			if (obj) {
				var ii = state.smsCateContentList.findIndex(function (value, array, index) {
					return value.categoryId === obj.categoryId;
				});
				if (ii > -1) {
					state.smsCateContentList.splice(ii, 1, obj);
				} else {
					state.smsCateContentList.push(obj);
				}
			}
		},
		// 设置全部短信分类信息
		SET_SMS_SMSCATELIST: function SET_SMS_SMSCATELIST(state, list) {
			list.forEach(function (item, index) {
				var mesSubCate = {};
				item.cate.forEach(function (_item, _index) {
					if (item.firstSelect === undefined && _item.isOpen) {
						item.firstSelect = _index;
					}
					mesSubCate[_item.pid] ? mesSubCate[_item.pid]++ : mesSubCate[_item.pid] = 1;
				});
				if (item.isActivity === true) {
					item.firstSelect = 0;
					state.activityCate = item;
					return;
				}
				item.sub.forEach(function (_item, _index) {
					_item.copies = mesSubCate[_item.id];
				});
			});
			state.smsCateList = list;
		}
	},
	actions: {
		// 获取客户分类列表
		GetAllClientItems: function GetAllClientItems(_ref) {
			var commit = _ref.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(sms_service["g" /* getAllClientItems */])().then(function (response) {
					commit("SET_SMS_CLIENTITEMS", response || []);
					resolve(response);
				}).catch(function (error) {
					reject(error);
				});
			});
		},

		// 获取短信账户信息
		GetSmsAccountInfo: function GetSmsAccountInfo(_ref2) {
			var commit = _ref2.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(sms_service["r" /* getSmsAccountInfo */])().then(function (response) {
					commit("SET_SMS_ACCOUNTINFO", response.object || {
						emergencyMobile: "",
						signName: "",
						alertRemainTimes: ""
					});
					resolve(response);
				}).catch(function (error) {
					reject(error);
				});
			});
		},

		// 返回所有短信分类
		UserCategoryListJSON: function UserCategoryListJSON(_ref3) {
			var commit = _ref3.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(sms_service["D" /* userCategoryListJSON */])({}).then(function (response) {
					commit("SET_SMS_CONTENTLIST", response.object || []);
					resolve(response);
				}).catch(function (error) {
					reject(error);
				});
			});
		},

		// 获取短信分类列表
		getCategoryJSON: function getCategoryJSON(_ref4) {
			var commit = _ref4.commit;

			return new promise_default.a(function (resolve, reject) {
				Object(sms_service["i" /* getCategoryJSON */])().then(function (response) {
					commit("SET_SMS_SMSCATELIST", response || []);
					resolve(response);
				}).catch(function (error) {
					reject(error);
				});
			});
		}
	}
};

/* harmony default export */ var sms = (sms_user);
// EXTERNAL MODULE: ./node_modules/babel-runtime/core-js/object/assign.js
var object_assign = __webpack_require__("woOf");
var assign_default = /*#__PURE__*/__webpack_require__.n(object_assign);

// EXTERNAL MODULE: ./src/tim.js
var tim = __webpack_require__("oVfb");

// CONCATENATED MODULE: ./src/store/modules/imuser.js


var imuser = {
  state: {
    currentUserProfile: {},
    isLogin: false,
    isSDKReady: false, // TIM SDK 是否 ready
    shopImUserId: null,
    operationId: null,
    userSig: null
  },
  mutations: {
    updateCurrentUserProfile: function updateCurrentUserProfile(state, userProfile) {
      state.currentUserProfile = userProfile;
    },
    toggleIsLogin: function toggleIsLogin(state, isLogin) {
      state.isLogin = typeof isLogin === 'undefined' ? !state.isLogin : isLogin;
    },
    toggleIsSDKReady: function toggleIsSDKReady(state, isSDKReady) {
      state.isSDKReady = typeof isSDKReady === 'undefined' ? !state.isSDKReady : isSDKReady;
    },
    setShopImUserId: function setShopImUserId(state, data) {
      state.shopImUserId = data.shopImUserId;
      state.operationId = data.operationId;
      state.userSig = data.userSig;
    },
    reset: function reset(state) {
      assign_default()(state, {
        currentUserProfile: {},
        isLogin: false,
        isSDKReady: false // TIM SDK 是否 ready
      });
    }
  },
  actions: {
    login: function login(context, timUser) {
      tim["a" /* default */].login(timUser).then(function () {
        context.commit('toggleIsLogin', true);
      }).catch(function (imError) {
        if (imError.code === 2000) {
          window.$message.error(imError.message + ', 请检查是否正确填写了 SDKAPPID');
        } else {
          window.$message.error(imError.message);
        }
      });
    },
    logout: function logout(context) {
      // 若有当前会话，在退出登录时已读上报
      if (context.rootState.conversation.currentConversation.conversationID) {
        tim["a" /* default */].setMessageRead({ conversationID: context.rootState.conversation.currentConversation.conversationID });
      }
      tim["a" /* default */].logout().then(function () {
        context.commit('toggleIsLogin');
        context.commit('stopComputeCurrent');
        context.commit('reset');
      });
    },
    loginOpenIm: function loginOpenIm(context, shopImUserId) {
      var userID = shopImUserId.userID,
          userSig = shopImUserId.userSig;

      var config = {
        userID: userID, // 用户ID
        token: userSig, // 用户token
        url: "wss://im.app.qinsilk.com", // jssdk server ws地址
        platformID: 5 // 平台号
      };
      return window.openIM.login(config).then(function (res) {
        console.log("login suc...", res);
        if (res && res.errCode === 0) {
          var operationId = res.operationID;
          context.commit('toggleIsLogin', true);
          context.commit('setShopImUserId', { shopImUserId: userID, operationId: operationId, userSig: userSig });
        } else {
          console.error('login failed', res);
        }
      }).catch(function (err) {
        throw new Error(err.message);
      });
    }
  }
};

/* harmony default export */ var modules_imuser = (imuser);
// EXTERNAL MODULE: ./node_modules/babel-runtime/helpers/toConsumableArray.js
var toConsumableArray = __webpack_require__("Gu7T");
var toConsumableArray_default = /*#__PURE__*/__webpack_require__.n(toConsumableArray);

// EXTERNAL MODULE: ./node_modules/tim-js-sdk/tim-js.js
var tim_js = __webpack_require__("B5T/");
var tim_js_default = /*#__PURE__*/__webpack_require__.n(tim_js);

// EXTERNAL MODULE: ./src/service/client/client.js
var client = __webpack_require__("wjXq");

// EXTERNAL MODULE: ./src/utils/common.js
var utils_common = __webpack_require__("X2Oc");

// EXTERNAL MODULE: ./src/lib/open-im-sdk-wasm/types/enum.js
var types_enum = __webpack_require__("/7ae");

// CONCATENATED MODULE: ./src/store/modules/conversation.js









var MESSAGE_SHOW_INTERVAL = 60 * 2;
var conversationModules = {
  state: {
    currentConversation: {},
    currentMessageList: [],
    currentMember: {},
    consultation: {
      goods: {},
      order: {}
    },
    consultations: null,
    startClientMsgID: '',
    nextReqMessageID: '',
    isCompleted: false, // 当前会话消息列表是否已经拉完了所有消息
    conversationList: []
  },
  getters: {
    toAccount: function toAccount(state) {
      if (!state.currentConversation || !state.currentConversation.conversationID) {
        return '';
      }
      switch (state.currentConversation.type) {
        case 'C2C':
          return state.currentConversation.conversationID.replace('C2C', '');
        case 'GROUP':
          return state.currentConversation.conversationID.replace('GROUP', '');
        default:
          return state.currentConversation.conversationID;
      }
    },
    currentConversationType: function currentConversationType(state) {
      if (!state.currentConversation || !state.currentConversation.type) {
        return '';
      }
      return state.currentConversation.type;
    },
    totalUnreadCount: function totalUnreadCount(state) {
      return state.conversationList.reduce(function (count, conversation) {
        return count + conversation.unreadCount;
      }, 0);
    },
    // 用于当前会话的图片预览
    imgUrlList: function imgUrlList(state) {
      return state.currentMessageList.filter(function (message) {
        return message.contentType === types_enum["MessageType"].PictureMessage;
      }).map(function (message) {
        return message.pictureElem.sourcePicture.url;
      });
    }
  },
  mutations: {
    /**
     * 更新当前会话
     * 调用时机: 切换会话时
     * @param {Object} state
     * @param {Conversation} conversation
     */
    updateCurrentConversation: function updateCurrentConversation(state, conversation) {
      state.currentConversation = conversation;
      state.currentMessageList = [];
      state.startClientMsgID = '';
      state.isCompleted = false;
    },
    updateCurrentMember: function updateCurrentMember(state, memberInfo) {
      state.currentMember = memberInfo;
    },

    /**
     * 更新会话列表
     * 调用时机：触发会话列表更新事件时。CONVERSATION_LIST_UPDATED
     * @param {Object} state
     * @param {Conversation[]} conversationList
     */
    updateConversationList: function updateConversationList(state, conversationList) {
      return openIM.getAllConversationList().then(function (_ref) {
        var data = _ref.data;

        state.conversationList = JSON.parse(data);
      }).catch(function (err) {
        throw new Error(err);
      });
    },

    /**
     * 重置当前会话
     * 调用时机：需要重置当前会话时，例如：当前会话是一个群组，正好被踢出群时（被踢群事件触发），重置当前会话
     * @param {Object} state
     */
    resetCurrentConversation: function resetCurrentConversation(state) {
      state.currentConversation = {};
    },
    reset: function reset(state) {
      assign_default()(state, {
        currentConversation: {},
        currentMessageList: [],
        startClientMsgID: '',
        isCompleted: false, // 当前会话消息列表是否已经拉完了所有消息
        conversationList: []
      });
    }
  },
  actions: {
    handleGoodsAndOrderMessage: function handleGoodsAndOrderMessage(context, data) {
      var currentMember = {};
      for (var i = data.messageList.length - 1; i >= 0; i--) {
        var msg = data.messageList[i];
        // 消息类型是商品
        if (msg.contentType == types_enum["MessageType"].CustomMessage) {
          var content = JSON.parse(msg.content);
          switch (content.extension) {
            case "commodityDetail":
              currentMember.goods = JSON.parse(content.data);
              currentMember.order = {};
              break;
            case "orderDetail":
              currentMember.goods = {};
              currentMember.order = JSON.parse(content.data);
              break;
            default:
              break;
          }
          break;
        }
      }
      // 防止goods, order缺失报错
      !currentMember.goods && (currentMember.goods = {});
      !currentMember.order && (currentMember.order = {});
      context.state.consultation = currentMember;
    },

    /**
    * 获取消息列表
    * 调用时机：打开某一会话时或下拉获取历史消息时
    * @param {Object} context
    * @param {String} userID
    */
    getMessageList: function getMessageList(context, userID) {
      if (context.state.isCompleted) {
        window.$message('已经没有更多的历史消息了哦');
        return;
      }
      var _context$state = context.state,
          startClientMsgID = _context$state.startClientMsgID,
          currentMessageList = _context$state.currentMessageList;

      var options = {
        groupID: "",
        startClientMsgID: startClientMsgID,
        count: 30,
        userID: userID
      };
      return openIM.getHistoryMessageList(options).then(function (res) {
        // 调用成功
        var messageList = JSON.parse(res.data);
        context.state.isCompleted = messageList.length === 0;
        var lastMesg = messageList[0];
        lastMesg && (context.state.startClientMsgID = lastMesg.clientMsgID);
        // 更新当前消息列表，从头部插入
        var tempList = [].concat(toConsumableArray_default()(messageList), toConsumableArray_default()(currentMessageList));
        tempList.reduce(function (showTimeItem, item) {
          showTimeItem.isShowTime = true;
          if (Math.abs(Object(utils_common["d" /* accSub */])(showTimeItem.createTime, item.createTime)) <= MESSAGE_SHOW_INTERVAL) {
            item.isShowTime = false;
            return showTimeItem;
          } else {
            item.isShowTime = true;
            return item;
          }
        }, tempList[0]);
        // 更新当前消息列表，从头部插入
        context.state.currentMessageList = tempList;
        // 仅判断最近的消息含有goods或商品的消息
        context.dispatch('handleGoodsAndOrderMessage', { messageList: tempList });
        return messageList;
      }).catch(function (err) {
        throw new Error(err);
      });
    },

    /**
     * 切换会话
     * 调用时机：切换会话时
     * @param {Object} context
     * @param {String} conversationID
     */
    checkoutConversation: function checkoutConversation(context, conversation) {
      var _this = this;

      return asyncToGenerator_default()( /*#__PURE__*/regenerator_default.a.mark(function _callee() {
        var conversationID, userID, prefKey, memberId, options, res;
        return regenerator_default.a.wrap(function _callee$(_context) {
          while (1) {
            switch (_context.prev = _context.next) {
              case 0:
                conversationID = conversation.conversationID, userID = conversation.userID;

                context.commit('resetCurrentMemberList');
                prefKey = "custom_gsm";
                memberId = conversationID.substring(conversationID.indexOf(prefKey) + prefKey.length);

                if (!isNaN(memberId)) {
                  // 获取会员信息
                  client["z" /* getMemberWithClientInfo */]({ "id": memberId }).then(function (data) {
                    if (data.object) {
                      context.commit('updateCurrentMember', data.object);
                    } else {
                      context.commit('updateCurrentMember', {});
                    }
                  });
                }

                // 存在未读消息先行上报

                if (!(context.getters.totalUnreadCount > 0)) {
                  _context.next = 16;
                  break;
                }

                _context.prev = 6;

                // 1.切换会话前，将切换前的会话进行已读上报
                options = {
                  userID: userID,
                  msgIDList: [] // 当msgIDList为一个空数组[]时，，即标记单聊会话为已读，置零该会话未读数
                };
                _context.next = 10;
                return openIM.markC2CMessageAsRead(options);

              case 10:
                res = _context.sent;
                _context.next = 16;
                break;

              case 13:
                _context.prev = 13;
                _context.t0 = _context['catch'](6);
                throw new Error(_context.t0);

              case 16:
                // 2 更新当前会话
                context.commit('updateCurrentConversation', conversation);
                // 3 获取消息列表
                context.dispatch('getMessageList', userID);
                // 4 更新会话列表
                context.commit('updateConversationList');

              case 19:
              case 'end':
                return _context.stop();
            }
          }
        }, _callee, _this, [[6, 13]]);
      }))();
    },

    /**
     * 将消息插入当前会话列表
     * 调用时机：收/发消息事件触发时
     * @param {Object} state
     * @param {Message[]|Message} data
     * @returns
     */
    pushCurrentMessageList: function pushCurrentMessageList(context, data) {
      var state = context.state;
      if (Array.isArray(data)) {
        var tempList = [].concat(toConsumableArray_default()(state.currentMessageList), toConsumableArray_default()(data));
        tempList.reduce(function (showTimeItem, item) {
          showTimeItem.isShowTime = true;
          if (Math.abs(Object(utils_common["d" /* accSub */])(showTimeItem.createTime, item.createTime)) <= MESSAGE_SHOW_INTERVAL) {
            item.isShowTime = false;
            return showTimeItem;
          } else {
            item.isShowTime = true;
            return item;
          }
        }, tempList[0]);
        state.currentMessageList = tempList;
        // state.currentMessageList = mergeMessageList(state.currentMessageList, result);
      } else {
        state.currentMessageList = [].concat(toConsumableArray_default()(state.currentMessageList), [data]);
      }
      // 仅判断最近的消息含有goods或商品的消息
      context.dispatch('handleGoodsAndOrderMessage', { messageList: state.currentMessageList });
      // 当前会话的userID与接收到消息的sendID一致时，更新当前会话的消息列表,同时标记为已读
      if (state.currentConversation && state.currentConversation.userID === data.sendID) {
        var options = {
          userID: data.sendID,
          msgIDList: []
        };
        console.log('state.currentMessageList', state);
        // 标记已读
        return openIM.markC2CMessageAsRead(options);
      }
    }
  }
};

/* harmony default export */ var modules_conversation = (conversationModules);
// CONCATENATED MODULE: ./src/store/modules/group.js




var groupModules = {
  state: {
    groupList: [],
    currentMemberList: [],
    createGroupModelVisible: false
  },
  getters: {
    hasGroupList: function hasGroupList(state) {
      return state.groupList.length > 0;
    }
  },
  mutations: {
    updateGroupList: function updateGroupList(state, groupList) {
      state.groupList = groupList;
    },
    updateCreateGroupModelVisible: function updateCreateGroupModelVisible(state, visible) {
      state.createGroupModelVisible = visible;
    },
    updateCurrentMemberList: function updateCurrentMemberList(state, memberList) {
      state.currentMemberList = [].concat(toConsumableArray_default()(state.currentMemberList), toConsumableArray_default()(memberList));
    },
    resetCurrentMemberList: function resetCurrentMemberList(state) {
      state.currentMemberList = [];
    },
    reset: function reset(state) {
      assign_default()(state, {
        groupList: [],
        currentMemberList: [],
        createGroupModelVisible: false
      });
    }
  },
  actions: {
    updateGroupList: function updateGroupList(context, groupList) {
      context.commit('updateGroupList', groupList);
    },
    getGroupMemberList: function getGroupMemberList(context, groupID) {
      return tim["a" /* default */].getGroupMemberList({
        groupID: groupID,
        offset: context.state.currentMemberList.length,
        count: 30
      }).then(function (imResponse) {
        context.commit('updateCurrentMemberList', imResponse.data.memberList);
        return imResponse;
      });
    }
  }
};

/* harmony default export */ var group = (groupModules);
// CONCATENATED MODULE: ./src/store/modules/friend.js

var friendModules = {
  state: {
    friendList: [],
    createGroupModelVisible: false
  },
  mutations: {
    upadteFriendList: function upadteFriendList(state, friendList) {
      state.friendList = friendList;
    },
    reset: function reset(state) {
      assign_default()(state, {
        friendList: [],
        createGroupModelVisible: false
      });
    }
  }
};

/* harmony default export */ var friend = (friendModules);
// CONCATENATED MODULE: ./src/store/modules/selectImageScale.js
var selectImageScale = {
    state: {
        selectImageScaleList: [{ val: "1", text: "100%(不压缩)", compressScaleValue: "100" }, { val: "2", text: "80%", compressScaleValue: "80" }, { val: "3", text: "70%", compressScaleValue: "70" }, { val: "4", text: "50%", compressScaleValue: "50" }, { val: "5", text: "20%", compressScaleValue: "20" }]
    },
    getters: {
        selectImageScaleList: function selectImageScaleList(state) {
            return state.selectImageScaleList;
        }
    }
};

/* harmony default export */ var modules_selectImageScale = (selectImageScale);
// CONCATENATED MODULE: ./src/store/modules/blacklist.js


var blacklistModule = {
  state: {
    blacklist: []
  },
  mutations: {
    updateBlacklist: function updateBlacklist(state, blacklist) {
      state.blacklist = blacklist;
    },
    removeFromBlacklist: function removeFromBlacklist(state, userID) {
      state.blacklist = state.blacklist.filter(function (item) {
        return item.userID !== userID;
      });
    },
    reset: function reset(state) {
      assign_default()(state, {
        blacklist: []
      });
    }
  },
  actions: {
    getBlacklist: function getBlacklist(context) {
      tim["a" /* default */].getBlacklist().then(function (_ref) {
        var data = _ref.data;
        return tim["a" /* default */].getUserProfile({ userIDList: data });
      }).then(function (_ref2) {
        var data = _ref2.data;

        context.commit('updateBlacklist', data);
      });
    }
  }
};

/* harmony default export */ var blacklist = (blacklistModule);
// CONCATENATED MODULE: ./src/store/getters.js
var getters = {
	menuList: function menuList(state) {
		return state.user.menuList;
	},
	userLoginInfo: function userLoginInfo(state) {
		return state.user.userLoginInfo;
	},
	companyInfo: function companyInfo(state) {
		return state.user.companyInfo;
	},
	companyConfigList: function companyConfigList(state) {
		return state.user.companyConfigList;
	},
	actionAccessRuleList: function actionAccessRuleList(state) {
		return state.user.actionAccessRuleList;
	},
	openprofession: function openprofession(state) {
		return state.user.openprofession;
	},
	// sms
	smsCateList: function smsCateList(state) {
		return state.sms.smsCateList;
	},
	clientItems: function clientItems(state) {
		return state.sms.clientItems;
	},
	smsAccountInfo: function smsAccountInfo(state) {
		return state.sms.smsAccountInfo;
	},
	smsCateContentList: function smsCateContentList(state) {
		return state.sms.smsCateContentList;
	},
	activityCate: function activityCate(state) {
		return state.sms.activityCate;
	},
	certificationInfo: function certificationInfo(state) {
		return state.user.certificationInfo;
	},
	cid: function cid(state) {
		return state.user.userLoginInfo.companyVO.id || 0;
	}
};
/* harmony default export */ var store_getters = (getters);
// CONCATENATED MODULE: ./src/store/index.js












vue_esm["default"].use(vuex_esm["a" /* default */]);

var store = new vuex_esm["a" /* default */].Store({
	modules: {
		user: modules_user,
		sms: sms,
		imuser: modules_imuser,
		conversation: modules_conversation,
		group: group,
		friend: friend,
		blacklist: blacklist,
		selectImageScale: modules_selectImageScale
	},
	getters: store_getters
});

/* harmony default export */ var src_store = __webpack_exports__["a"] = (store);

/***/ }),

/***/ "NHnr":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });

// EXTERNAL MODULE: ./node_modules/babel-polyfill/lib/index.js
var lib = __webpack_require__("j1ja");
var lib_default = /*#__PURE__*/__webpack_require__.n(lib);

// EXTERNAL MODULE: ./node_modules/es6-promise/auto.js
var auto = __webpack_require__("MU8w");
var auto_default = /*#__PURE__*/__webpack_require__.n(auto);

// EXTERNAL MODULE: ./node_modules/vue/dist/vue.esm.js
var vue_esm = __webpack_require__("7+uW");

// EXTERNAL MODULE: ./node_modules/normalize.css/normalize.css
var normalize = __webpack_require__("uMhA");
var normalize_default = /*#__PURE__*/__webpack_require__.n(normalize);

// EXTERNAL MODULE: ./node_modules/element-ui/lib/element-ui.common.js
var element_ui_common = __webpack_require__("zL8q");
var element_ui_common_default = /*#__PURE__*/__webpack_require__.n(element_ui_common);

// EXTERNAL MODULE: ./node_modules/element-ui/lib/theme-chalk/index.css
var theme_chalk = __webpack_require__("tvR6");
var theme_chalk_default = /*#__PURE__*/__webpack_require__.n(theme_chalk);

// EXTERNAL MODULE: ./node_modules/element-ui/lib/locale/lang/zh-CN.js
var zh_CN = __webpack_require__("Vi3T");
var zh_CN_default = /*#__PURE__*/__webpack_require__.n(zh_CN);

// EXTERNAL MODULE: ./src/styles/index.scss
var styles = __webpack_require__("yh13");
var styles_default = /*#__PURE__*/__webpack_require__.n(styles);

// CONCATENATED MODULE: ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib/selector.js?type=script&index=0!./src/App.vue
//
//
//
//
//
//
//

/* harmony default export */ var App = ({
	name: "app"
});
// 统一捕获使用promise走reject却没有catch导致sentry捕获报错的问题
window.addEventListener('unhandledrejection', function browserRejectionHandler(event) {
	console.warn("UNHANDLED PROMISE REJECTION: " + event.reason);
	// 阻止sentry捕获
	event && event.preventDefault();
});
// CONCATENATED MODULE: ./node_modules/vue-loader/lib/template-compiler?{"id":"data-v-3f2b7f74","hasScoped":false,"transformToRequire":{"video":["src","poster"],"source":"src","img":"src","image":"xlink:href"},"buble":{"transforms":{}}}!./node_modules/vue-loader/lib/selector.js?type=template&index=0!./src/App.vue
var render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{attrs:{"id":"app"}},[_c('div',{directives:[{name:"custom-title",rawName:"v-custom-title",value:(_vm.$route.meta.title?("秦丝生意通-" + (_vm.$route.meta.title)):'秦丝生意通'),expression:"$route.meta.title?`秦丝生意通-${$route.meta.title}`:'秦丝生意通'"}]}),_vm._v(" "),_c('router-view')],1)}
var staticRenderFns = []
var esExports = { render: render, staticRenderFns: staticRenderFns }
/* harmony default export */ var selectortype_template_index_0_src_App = (esExports);
// CONCATENATED MODULE: ./src/App.vue
var normalizeComponent = __webpack_require__("VU/8")
/* script */

/* template */

/* template functional */
var __vue_template_functional__ = false
/* styles */
var __vue_styles__ = null
/* scopeId */
var __vue_scopeId__ = null
/* moduleIdentifier (server only) */
var __vue_module_identifier__ = null
var Component = normalizeComponent(
  App,
  selectortype_template_index_0_src_App,
  __vue_template_functional__,
  __vue_styles__,
  __vue_scopeId__,
  __vue_module_identifier__
)

/* harmony default export */ var src_App = (Component.exports);

// EXTERNAL MODULE: ./src/store/index.js + 9 modules
var store = __webpack_require__("IcnI");

// EXTERNAL MODULE: ./src/router/index.js + 16 modules
var router = __webpack_require__("YaEn");

// EXTERNAL MODULE: ./node_modules/nprogress/nprogress.js
var nprogress = __webpack_require__("Y81h");
var nprogress_default = /*#__PURE__*/__webpack_require__.n(nprogress);

// EXTERNAL MODULE: ./node_modules/nprogress/nprogress.css
var nprogress_nprogress = __webpack_require__("UVIz");
var nprogress_nprogress_default = /*#__PURE__*/__webpack_require__.n(nprogress_nprogress);

// EXTERNAL MODULE: ./src/utils/common.js
var common = __webpack_require__("X2Oc");

// CONCATENATED MODULE: ./src/permission.js

 // Progress 进度条
 // Progress 进度条样式

// 这个文件可以监控路由变化的操作，后续根据功能需要来编写相应的代码
router["a" /* default */].beforeEach(function (to, from, next) {
	// 获取权限列表
	// 权限判断
	var authority = to.meta.authority;

	if (authority) {
		Object(common["N" /* includeAuthority */])(authority).then(function (res) {
			if (!res) {
				next(false);
				window.location.href = BASE_URL.webServer + "/admin/error/authenticationFailed.ac";
			} else {
				nprogress_default.a.start();
				next();
			}
		});
	} else {
		nprogress_default.a.start();
		next();
	}
});

router["a" /* default */].afterEach(function () {
	nprogress_default.a.done(); // 结束Progress
});
// EXTERNAL MODULE: ./src/utils/global.js
var global = __webpack_require__("BfUi");
var global_default = /*#__PURE__*/__webpack_require__.n(global);

// CONCATENATED MODULE: ./src/utils/filter.js


// 注册全局过滤
// 正整数(大于等于0的整数)
vue_esm["default"].filter("positiveInteger", function (nv, ov) {
	// 返回处理后的值
	var res = parseInt(nv);
	if (isNaN(res)) {
		res = ov || 0;
	}
	res = res > 0 ? res : 0;
	return res;
});

// 保留几位小数，默认两位
vue_esm["default"].filter('toFixed', function (val) {
	var num = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 2;

	return val || val === 0 ? Number(val).toFixed(num) : '';
});

// 添加￥前缀
vue_esm["default"].filter('currency', function (val, symbol) {
	return (symbol || '￥') + " " + (val || 0);
});
// 金钱每3位，分割
vue_esm["default"].filter('precisionFilter', function (value) {
	var pricePrecision = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 2;
	var symbol = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : ',';

	var floatPart = "".padEnd(pricePrecision, '0');
	if (!value) {
		return "0." + floatPart;
	}
	var intPart = Number(value) - Number(value) % 1;
	var sign = '';
	if (value < 0 && intPart == 0) {
		// 处理-0变成0的问题
		sign = '-';
	}
	var intPartFormat = intPart.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1' + symbol);
	var value2Array = value.toString().split(".");
	if (value2Array.length == 2) {
		floatPart = value2Array[1].toString().substring(0, pricePrecision).padEnd(pricePrecision, '0');
		return sign + intPartFormat + "." + floatPart;
	} else {
		return sign + intPartFormat + "." + floatPart;
	}
});
vue_esm["default"].filter('toDate', function (val) {
	return val ? new Date(val).Format('yyyy-MM-dd hh:mm') : '';
});

// 根据长度裁剪字符串（中英文混合，用于html2canvas画图）
vue_esm["default"].filter('cutStr', function (val, maxLen) {
	var len = 0;
	for (var i = 0; i < val.length; i++) {
		if (val.charCodeAt(i) > 127 || val.charCodeAt(i) == 94) {
			len += 2;
		} else {
			len++;
		}
		if (len > maxLen) {
			val = val.slice(0, i) + '...';
			break;
		}
	}
	return val;
});

vue_esm["default"].prototype.$filter = {};
// 将全局过滤注册到全局方法
// 正整数
vue_esm["default"].prototype.$filter.positiveInteger = function (nv, ov) {
	// 返回处理后的值
	nv = nv + "";
	var res = nv.replace(/[^\.0-9]/g, "").replace(".", "");
	res = parseInt(res);
	if (isNaN(res)) {
		res = "";
	}
	return res;
};
// EXTERNAL MODULE: ./node_modules/babel-runtime/helpers/toConsumableArray.js
var toConsumableArray = __webpack_require__("Gu7T");
var toConsumableArray_default = /*#__PURE__*/__webpack_require__.n(toConsumableArray);

// CONCATENATED MODULE: ./src/utils/directives.js




// 注册全局指令
// 输入框自动聚焦 用法： v-focus="{ cls: 'el-input',tag: 'input', foc: Boolean }
vue_esm["default"].directive("focus", {
	inserted: function inserted(el, option) {
		directives_focus(el, option);
	},
	bind: function bind() {},
	update: function update(el, option) {
		// focus(el, option);
	},
	componentUpdated: function componentUpdated(el, option) {
		directives_focus(el, option);
	}
});

function directives_focus(el, option) {
	var defClass = 'el-input';
	var defTag = 'input';
	var value = option.value || true;
	if (typeof value === 'boolean') {
		value = {
			cls: defClass,
			tag: defTag,
			foc: value
		};
	} else {
		value = {
			cls: value.cls || defClass,
			tag: value.tag || defTag,
			foc: value.foc || false
		};
	}

	if (el.classList.contains(value.cls) && value.foc) {
		el.getElementsByTagName(value.tag)[0].focus();
	}
}

// 权限指令-展示与不展示
vue_esm["default"].directive('authority', function (el, binding) {
	var authority = binding.value;
	Object(common["N" /* includeAuthority */])(authority).then(function (res) {
		if (!res) {
			el.classList.add('display-none');
		} else {
			el.classList.remove('display-none');
		}
	});
});

var setWechatTitle = function setWechatTitle(title, img) {
	if (title === undefined || window.document.title === title) {
		return;
	}
	document.title = title;
	var mobile = navigator.userAgent.toLowerCase();
	if (/iphone|ipad|ipod/.test(mobile)) {
		var iframe = document.createElement("iframe");
		iframe.style.display = "none";
		// 替换成站标favicon路径或者任意存在的较小的图片即可
		iframe.setAttribute("src", img || "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7");
		var iframeCallback = function iframeCallback() {
			setTimeout(function () {
				iframe.removeEventListener("load", iframeCallback);
				document.body.removeChild(iframe);
			}, 0);
		};
		iframe.addEventListener("load", iframeCallback);
		document.body.appendChild(iframe);
	}
};

vue_esm["default"].directive("custom-title", function (el, binding) {
	setWechatTitle(binding.value, el.getAttribute("img-set") || null);
});

// el-select多选下拉框设置指定的tags删除图标隐藏指令
vue_esm["default"].directive('undelete-tags', {
	bind: function bind(el, bindings) {
		// doNone 需要隐藏删除图标的数据ID，vModel v-model绑定的数据
		var _bindings$value = bindings.value,
		    doNone = _bindings$value.doNone,
		    vModel = _bindings$value.vModel;

		var dealStyle = function dealStyle(tags) {
			// 因为v-model绑定的值与tags的顺序是一致的，所以可以根据绑定值的下标来判断是否哪个tags需要隐藏
			if (tags.length == vModel.length) {
				for (var i = 0, len = vModel.length; i < len; i++) {
					if (doNone.includes(vModel[i].id)) {
						if (![].concat(toConsumableArray_default()(tags[i].classList)).includes('select-tag-close-none')) {
							tags[i].classList.add("select-tag-close-none");
							var closeIcon = tags[i].querySelector('.el-tag__close');
							closeIcon.style.display = 'none'; // close 图标隐藏掉
						}
					}
				}
			}
		};
		setTimeout(function () {
			var tags = el.querySelectorAll('.el-tag');
			dealStyle(tags);
		});
	}
});

// el-select多选下拉框tags的删除图标绑定mousedown事件
vue_esm["default"].directive('mousedown-tags', function (el, bindings) {
	// mousedown 需要绑定的方法，index 绑定元素对应的数据下标
	var _bindings$value2 = bindings.value,
	    mousedown = _bindings$value2.mousedown,
	    index = _bindings$value2.index;

	var dealStyle = function dealStyle(tags) {
		tags.forEach(function (el) {
			el.onmousedown = function (e) {
				mousedown(index);
			};
		});
	};
	setTimeout(function () {
		var tags = el.querySelectorAll(".el-tag__close");
		dealStyle(tags);
	});
});
// EXTERNAL MODULE: ./node_modules/open-im-sdk/index.esm.js
var index_esm = __webpack_require__("AWpn");

// EXTERNAL MODULE: ./src/lib/open-im-sdk-wasm/types/enum.js
var types_enum = __webpack_require__("/7ae");

// EXTERNAL MODULE: ./src/utils/index.js
var utils = __webpack_require__("0xDb");

// CONCATENATED MODULE: ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib/selector.js?type=script&index=0!./src/components/managerWorkstation/avatar.vue
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//


/* harmony default export */ var avatar = ({
	props: {
		src: String,
		text: {
			type: String,
			default: "U"
		},
		shape: {
			type: String,
			default: "circle"
		},
		width: {
			type: Number,
			default: 30
		},
		height: {
			type: Number,
			default: 30
		}
	},
	components: {
		ElImage: element_ui_common["Image"]
	}
});
// CONCATENATED MODULE: ./node_modules/vue-loader/lib/template-compiler?{"id":"data-v-73d2f668","hasScoped":false,"transformToRequire":{"video":["src","poster"],"source":"src","img":"src","image":"xlink:href"},"buble":{"transforms":{}}}!./node_modules/vue-loader/lib/selector.js?type=template&index=0!./src/components/managerWorkstation/avatar.vue
var avatar_render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[(_vm.src)?_c('img',{staticClass:"avatar",class:_vm.shape,style:({
			width: _vm.width + 'px',
			height: _vm.height + 'px',
			lineHeight: _vm.height + 'px'
		}),attrs:{"src":_vm.src}}):_c('div',{staticClass:"avatar",class:_vm.shape,style:({
			width: _vm.width + 'px',
			height: _vm.height + 'px',
			lineHeight: _vm.height + 'px'
		})},[_vm._v("\n\t\t"+_vm._s(_vm.text ? _vm.text[0] : "E")+"\n\t")])])}
var avatar_staticRenderFns = []
var avatar_esExports = { render: avatar_render, staticRenderFns: avatar_staticRenderFns }
/* harmony default export */ var managerWorkstation_avatar = (avatar_esExports);
// CONCATENATED MODULE: ./src/components/managerWorkstation/avatar.vue
function injectStyle (ssrContext) {
  __webpack_require__("DZlS")
}
var avatar_normalizeComponent = __webpack_require__("VU/8")
/* script */

/* template */

/* template functional */
var avatar___vue_template_functional__ = false
/* styles */
var avatar___vue_styles__ = injectStyle
/* scopeId */
var avatar___vue_scopeId__ = null
/* moduleIdentifier (server only) */
var avatar___vue_module_identifier__ = null
var avatar_Component = avatar_normalizeComponent(
  avatar,
  managerWorkstation_avatar,
  avatar___vue_template_functional__,
  avatar___vue_styles__,
  avatar___vue_scopeId__,
  avatar___vue_module_identifier__
)

/* harmony default export */ var components_managerWorkstation_avatar = (avatar_Component.exports);

// EXTERNAL MODULE: ./src/tim.js
var tim = __webpack_require__("oVfb");

// EXTERNAL MODULE: ./node_modules/tim-js-sdk/tim-js.js
var tim_js = __webpack_require__("B5T/");
var tim_js_default = /*#__PURE__*/__webpack_require__.n(tim_js);

// EXTERNAL MODULE: ./src/assets/icon/iconfont.css
var iconfont = __webpack_require__("7xIN");
var iconfont_default = /*#__PURE__*/__webpack_require__.n(iconfont);

// EXTERNAL MODULE: ./src/assets/qs-icon/iconfont.css
var qs_icon_iconfont = __webpack_require__("2K1W");
var qs_icon_iconfont_default = /*#__PURE__*/__webpack_require__.n(qs_icon_iconfont);

// EXTERNAL MODULE: ./node_modules/babel-runtime/regenerator/index.js
var regenerator = __webpack_require__("Xxa5");
var regenerator_default = /*#__PURE__*/__webpack_require__.n(regenerator);

// EXTERNAL MODULE: ./node_modules/babel-runtime/helpers/asyncToGenerator.js
var asyncToGenerator = __webpack_require__("exGp");
var asyncToGenerator_default = /*#__PURE__*/__webpack_require__.n(asyncToGenerator);

// CONCATENATED MODULE: ./src/utils/vaService.js






/**
 * 独立增值服务鉴权处理
 * 有权限返回true
 * 无权限则弹窗提示，点击确定后跳转对应购买页面
 * @param {String} actionId
 * @param {Object} operate custom:自定义弹窗 ruleName显示规则的名称
 * @returns Boolean
 */
var hasAuthentication = function () {
	var _ref = asyncToGenerator_default()( /*#__PURE__*/regenerator_default.a.mark(function _callee(actionId) {
		var operate = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
		var actionAccessRuleList, action, has, recommandName, recommendPaymentPcUrl, tipsMessage, tempText;
		return regenerator_default.a.wrap(function _callee$(_context) {
			while (1) {
				switch (_context.prev = _context.next) {
					case 0:
						_context.t0 = !store["a" /* default */].state.user.actionAccessRuleList;

						if (!_context.t0) {
							_context.next = 4;
							break;
						}

						_context.next = 4;
						return store["a" /* default */].dispatch("GetCompanyConfigJsonOnlyOnce");

					case 4:
						actionAccessRuleList = store["a" /* default */].state.user.actionAccessRuleList;

						if (actionId) {
							_context.next = 7;
							break;
						}

						return _context.abrupt('return', true);

					case 7:
						if (Array.isArray(actionAccessRuleList)) {
							_context.next = 9;
							break;
						}

						throw new Error('请检查鉴权接口getCompanyConfigJson！！');

					case 9:
						action = actionAccessRuleList.find(function (rule) {
							return rule.actionId === actionId;
						});

						if (action) {
							_context.next = 12;
							break;
						}

						return _context.abrupt('return', false);

					case 12:
						has = action.has, recommandName = action.recommandName, recommendPaymentPcUrl = action.recommendPaymentPcUrl, tipsMessage = action.tipsMessage;
						// 直接返回action

						if (!operate.custom) {
							_context.next = 15;
							break;
						}

						return _context.abrupt('return', action);

					case 15:
						// has代表该项增值服务是否有权限
						if (!has) {
							tempText = tempText = '<div>\u60A8\u8FD8\u672A\u5F00\u901A' + (recommandName || '') + '\u76F8\u5173\u589E\u503C\u670D\u52A1\uFF0C\u65E0\u6CD5\u8FDB\u5165!</div>';

							if (operate.ruleName) {
								tempText = (operate.ruleName || '') + '\u4E3A' + (recommandName || '') + '\u4ED8\u8D39\u529F\u80FD\uFF0C\u5F00\u901A\u540E\u53EF\u4F7F\u7528';
							}
							if (tipsMessage) {
								tempText += '<div style="margin-top:20px;">' + tipsMessage + '</div>';
							}
							// 没有权限的提示购买相应权限，并提供相应跳转
							element_ui_common["MessageBox"].confirm(tempText, '提示', { confirmButtonText: '去开通服务', showCancelButton: operate.showCancelButton || false, dangerouslyUseHTMLString: true }).then(function () {
								// 缺少购买链接需运营提供给后台
								if (!recommendPaymentPcUrl) {
									throw new Error('请配置相应购买页面！');
								}
								// 跳转相应购买页面
								if (recommendPaymentPcUrl.startsWith('http')) {
									window.open(recommendPaymentPcUrl, "_blank");
								} else {
									router["a" /* default */].push({ path: recommendPaymentPcUrl });
								}
							}).catch(function (e) {
								return e;
							});
						}
						return _context.abrupt('return', has);

					case 17:
					case 'end':
						return _context.stop();
				}
			}
		}, _callee, this);
	}));

	return function hasAuthentication(_x) {
		return _ref.apply(this, arguments);
	};
}();
// EXTERNAL MODULE: ./src/assets/images/vip/qsVipPro_left@2x.png
var qsVipPro_left_2x = __webpack_require__("Uiiq");
var qsVipPro_left_2x_default = /*#__PURE__*/__webpack_require__.n(qsVipPro_left_2x);

// EXTERNAL MODULE: ./src/assets/images/vip/qsVipSenior_left@2x.png
var qsVipSenior_left_2x = __webpack_require__("lHsg");
var qsVipSenior_left_2x_default = /*#__PURE__*/__webpack_require__.n(qsVipSenior_left_2x);

// EXTERNAL MODULE: ./src/assets/images/vip/qsVipPro_right@2x.png
var qsVipPro_right_2x = __webpack_require__("EdkY");
var qsVipPro_right_2x_default = /*#__PURE__*/__webpack_require__.n(qsVipPro_right_2x);

// EXTERNAL MODULE: ./src/assets/images/vip/qsVipSenior_right@2x.png
var qsVipSenior_right_2x = __webpack_require__("GSXG");
var qsVipSenior_right_2x_default = /*#__PURE__*/__webpack_require__.n(qsVipSenior_right_2x);

// CONCATENATED MODULE: ./src/utils/vip.js


/**
 * 用于判断路由 功能 是否具有权限
 */









// 菜单路由配置 (id: 路由id, vaServiceRes: 权限id, vipType: 用于区分是专业版(qsVipPro) 还是 高级版(qsVipSenior))
/* 菜单配置 */
var menuAuthorityList = [{
	menuName: "商品分类",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_GOODS_CATEGORY_VIEW"
}, {
	menuName: "条码管理",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_BARCODE_CONFIG_VIEW"
}, {
	menuName: "角色管理",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_ROLE_MAN_VIEW"
}, {
	menuName: "公司公告",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_BULLETIN_VIEW"
}, {
	menuName: "打印模板",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_PRINT_TEMPLATE"
}, {
	menuName: "打印模板(旧)",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_PRINT_TEMPLATE"
}, {
	menuName: "物流设置",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_DELIVERY_VIEW"
}, {
	menuName: "系统重置",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_SYSTEM_RESET"
}, {
	menuName: "客户分类",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_CLIENTITEM"
}, {
	menuName: "客户标签",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_CLIENTTAGVIEW"
}, {
	menuName: "库存调拨单",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_STORETRANSFERORDER"
}, {
	menuName: "组装拆卸",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_ASSEMBLYORDERVIEW"
}, {
	menuName: "出库单",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_STOREOUTORDER"
}, {
	menuName: "入库单",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_STOREINORDER"
}, {
	menuName: "物流服务",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_EXPRESSORDERVIEW"
}, {
	menuName: "采购报表",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_PURCHASEREPORT"
}, {
	menuName: "客户活跃分析",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_CLIENTSALESTATISTICS"
}, {
	menuName: "销售报表",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_SALEREPORTVIEW"
}, {
	isVipMenu: true,
	menuName: "客户销量",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_CLIENTSALEREPORTVIEW"
}, {
	menuName: "商品销量",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_GOODSSALEREPORTVIEW"
}, {
	menuName: "进销对比",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_PURCHASEVSSALEREPORTVIEW"
}, {
	menuName: "盘点报表",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_STOREREPORT"
}, {
	menuName: "调拨报表",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_TRANFERSREPORT"
}, {
	menuName: "出库报表",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_OUTSTOREREPORT"
}, {
	menuName: "入库报表",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_INSTOREREPORT"
}, {
	menuName: "经营汇总",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_TOTALSALEREPORTVIEW"
}, {
	menuName: "进销存汇总",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_GOODSSUMMARY"
}, {
	menuName: "商品概况",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_MAIN_GOODS_GENERAL"
}, {
	menuName: "近7天销售走势",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_MAIN_SALES"
}, {
	menuName: "业绩增长分析",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_ACHIEVEMENTREPORT"
}, {
	menuName: "批次查询",
	vipType: "qsVipPro",
	vaServiceRes: "PC_FUNCTIONS_BATCHQUERY"
}, {
	menuName: "库位管理",
	vipType: "qsVipPro",
	vaServiceRes: "PC_FUNCTIONS_WAREHOUSELOCATION"
}, {
	menuName: "自定义属性管理",
	vipType: "qsVipPro",
	vaServiceRes: "PC_FUNCTIONS_CUSTOMATTRIBUTE"
}, {
	menuName: "规格管理",
	vipType: "qsVipSenior",
	vaServiceRes: "PC_FUNCTIONS_SPECMANAGE"
}, {
	menuName: "报价单",
	vipType: "qsVipPro",
	vaServiceRes: "PC_FUNCTIONS_QUOTATION"
}];

// 功能配置
var functionsAuthority = {
	SALESORDERGOODSREMARK: {
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "SALES_ORDER_GOODS_REMARK",
		name: "SALESORDERGOODSREMARK",
		text: "生意通新增单据商品备注编辑功能"
	},
	// 客户分类价格-高级版
	CUSTOMERCLASSIFICATIONPRICE: {
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "APP_FUNCTIONS_CUSTOMERCLASSIFICATIONPRICE",
		appName: "CUSTOMERCLASSIFICATIONPRICE",
		text: "生意通商品编辑 客户分类价格"
	},
	// 上次价格默认开启 高级版
	LASTDEFAULTPRICE: {
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "PC_LAST_DEFAULT_PRICE",
		appName: "LASTDEFAULTPRICE",
		text: "上次价格默认开启 高级版"
	},
	// 编辑草稿单时业务日期刷新为当前日期 高级版
	AUTOREFRESHDATEDSWITCH: {
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "PC_AUTO_REFRESH_DATED_SWITCH",
		appName: "AUTOREFRESHDATEDSWITCH",
		text: "编辑草稿单时业务日期刷新为当前日期 高级版"
	},
	// 数量小数位数 高级版
	QUANTITYDECIMAL: {
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "PC_QUANTITY_DECIMAL",
		appName: "QUANTITYDECIMAL",
		text: "数量小数位数 高级版"
	},
	// 开启序列号-专业版
	OPENSERIALNUMBER: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "APP_GIS_FUNCTIONS_INDUSTRY_GOODS_ATTR",
		appName: "OPENSERIALNUMBER",
		text: "系统设置-开启序列号 专业版"
	},
	//
	GOODSEDITADVANCE: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "PC_FUNCTIONS_GOODSEDITADVANCE",
		appName: "GOODSEDITADVANCE",
		text: "商品新增编辑弹窗 高级版"
	},
	//
	GOODSEDITPRO: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "PC_FUNCTIONS_GOODSEDITPRO",
		appName: "GOODSEDITPRO",
		text: "商品新增编辑弹窗 专业版"
	},
	//
	GOODCLASSIFICATION: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "APP_GIS_FUNCTIONS_GOODCLASSIFICATION",
		appName: "GOODCLASSIFICATION",
		text: "商品新增编辑 商品分类 高级版"
	},
	//
	SINGLEPRODUCTBARCODE: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "APP_FUNCTIONS_SINGLEPRODUCTBARCODE",
		appName: "SINGLEPRODUCTBARCODE",
		text: "商品新增编辑 商品条码权限 免费版"
	},
	GOODSPHOTOS: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "PC_FUNCTIONS_GOODSPHOTOS",
		appName: "GOODSPHOTOS",
		text: "商品新增编辑 商品相册 专业版"
	},
	PRIMARYANDSECONDUNIT: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "GOODSMULTIUNIT_INDUSTRY_VERSION_EDIT",
		appName: "PRIMARYANDSECONDUNIT",
		text: "商品新增编辑 主辅单位 专业版"
	},
	SERIALNUMBER: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "SERIAL_NUMBER_SETTING_INDUSTRY_VERSION",
		appName: "SERIALNUMBER",
		text: "商品新增编辑 序列号 专业版"
	},
	KEEPQUALITYDATE: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "SHELF_LIFE_INDUSTRY_VERSION",
		appName: "KEEPQUALITYDATE",
		text: "商品新增编辑 保质期 专业版"
	},
	SPACEOFPRODUCTION: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "ORIGIN_ARE_INDUSTRY_VERSION",
		appName: "SPACEOFPRODUCTION",
		text: "商品新增编辑 产地 专业版"
	},
	APPLICABLEAGE: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "ADAPT_AGE_INDUSTRY_VERSION",
		appName: "APPLICABLEAGE",
		text: "商品新增编辑 年龄 专业版"
	},
	// 商品新增 库位
	STORAGELOCATION: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "APP_FUNCTIONS_STORAGELOCATION",
		appName: "STORAGELOCATION",
		text: "商品新增 库位"
	},
	// 商品列表 维度切换
	FUNCTIONSSALEREPORTDIMENSIONSWITCHING: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "FUNCTIONS_SALEREPORT_DIMENSION_SWITCHING",
		appName: "FUNCTIONSSALEREPORTDIMENSIONSWITCHING",
		text: "商品列表 维度切换 高级版"
	},
	// 商品列表 筛选
	FUNCTIONSSALEREPORTFILTER: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "FUNCTIONS_SALEREPORT_FILTER",
		appName: "FUNCTIONSSALEREPORTFILTER",
		text: "商品列表 筛选 高级版"
	},
	// 商品列表 导出
	FUNCTIONSSALEREPORTEXPORT: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "FUNCTIONS_SALEREPORT_EXPORT",
		appName: "FUNCTIONSSALEREPORTEXPORT",
		text: "商品列表 导出 高级版"
	},
	// 新增报价单
	FUNCTIONSCREATEQUOTATION: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "PC_FUNCTIONS_CREATE_QUOTATION",
		appName: "FUNCTIONSCREATEQUOTATION",
		text: "商品管理 新增报价单 专业版"
	},
	// 新增报价单
	CUSTOMLABELMODE: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "CUSTOM_LABEL_MODE",
		appName: "CUSTOMLABELMODE",
		text: "条码打印 打印 自定义标签模板 高级版"
	},
	// 从秦丝商品导入
	QSIMPORTGOODS: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "PC_QS_IMPORT_GOODS",
		appName: "QSIMPORTGOODS",
		text: "商品管理 新增商品 从秦丝海量数据导入"
	},
	// 销售限价规则
	SALELIMITPRICE: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "FUNCTIONS_SALE_LIMIT_PRICE",
		appName: "SALELIMITPRICE",
		text: "销售单 新增销售单 销售限价"
	},
	// 客户欠款额度限制
	CUSTOMERDEBTLIMIT: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "PC_CUSTOMER_DEBT_LIMIT",
		appName: "CUSTOMERDEBTLIMIT",
		text: "客户欠款额度限制"
	},
	// 售价为0时进行提醒
	SALEPRICEZEROTIP: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "SALE_PRICE_ZERO_TIP",
		appName: "SALEPRICEZEROTIP",
		text: "系统配置项 售价为0时进行提醒"
	},
	SALERETAILLISTCONFIGURELIST: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "SALE_RETAIL_LIST_CONFIGURE_LIST",
		appName: "SALERETAILLISTCONFIGURELIST",
		text: "销售单报表 列表配置"
	},
	// 销售商品标记为赠品
	SALEGOODSSETGIFT: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "ORDER_GOODS_SET_GIFT",
		appName: "MULTILINEORDER",
		text: "标记为赠品 高级版"
	},
	// 未来日期开单
	FUTUREDATEORDERS: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipSenior",
		vaServiceRes: "FUTURE_DATE_ORDERS",
		appName: "FUTUREDATEORDERS",
		text: "未来日期开单 高级版"
	},
	//  库存数量单位换算
	UNITCONVERSIONENABLED: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "UNIT_CONVERSIONEN_ABLED",
		appName: "UNITCONVERSIONENABLED",
		text: "库存数量单位换算 专业版"
	},
	// Excel 全部导出(销售报表)
	EXCELALLEXPORT: {
		// 是否需要判断Vip
		isVipMenu: true,
		vipType: "qsVipPro",
		vaServiceRes: "EXCEL_ALL_EXPORT",
		appName: "EXCELALLEXPORT",
		text: "Excel 全部导出"
	}
};

var QS_VIP_CDNICON = {
	QS_VIP_SENIOR_NEWS: "http://cdn.qinsilk.com/img/qinsilk/gis/vip/qsVipSenior-news.png",
	QS_VIP_SENIOR: "http://cdn.qinsilk.com/img/qinsilk/gis/vip/qsVipSenior.png",
	QS_VIP_MAIN_TIPS: "http://cdn.qinsilk.com/img/qinsilk/gis/vip/main-tips.png",
	QS_VIP_PRO: qsVipPro_left_2x_default.a
};

var Vip = {
	leftIcon: function leftIcon(name) {
		var authorityObj = functionsAuthority[name];
		if (authorityObj && authorityObj.vipType) {
			return authorityObj.vipType === "qsVipSenior" ? qsVipSenior_left_2x_default.a : qsVipPro_left_2x_default.a;
		} else {
			return "";
		}
	},
	rightIcon: function rightIcon(name) {
		// 获取功能配置
		var authorityObj = functionsAuthority[name];
		if (authorityObj && authorityObj.vipType) {
			return authorityObj.vipType === "qsVipSenior" ? qsVipSenior_right_2x_default.a : qsVipPro_right_2x_default.a;
		} else {
			return "";
		}
	},
	menuVipIcon: function menuVipIcon(menuName) {
		var menuAuthorityItem = null;
		for (var i = 0; i < menuAuthorityList.length; i++) {
			if (menuName === menuAuthorityList[i].menuName) {
				menuAuthorityItem = menuAuthorityList[i];
				break;
			}
		}
		if (menuAuthorityItem) {
			if (menuAuthorityItem.vipType == "qsVipSenior") {
				// 菜单icon
				return QS_VIP_CDNICON.QS_VIP_SENIOR;
			} else {
				return QS_VIP_CDNICON.QS_VIP_PRO;
			}
		} else {
			return "";
		}
	},

	// 判断页面路由是否有权限
	menuRouterVaServiceResource: function menuRouterVaServiceResource(menuName, toast) {
		// 保证actionAccessRuleList已经存到store中
		var actionAccessRuleList = [];
		if (store["a" /* default */].state && store["a" /* default */].state.user && store["a" /* default */].state.user.actionAccessRuleList) {
			actionAccessRuleList = store["a" /* default */].state.user.actionAccessRuleList;
		}
		if (actionAccessRuleList.length === 0) return;
		// 获取功能配置
		// 这里使用 menuName 作为菜单的唯一标识 不准确
		var menuAuthorityItem = null;
		for (var i = 0; i < menuAuthorityList.length; i++) {
			if (menuName === menuAuthorityList[i].menuName) {
				menuAuthorityItem = menuAuthorityList[i];
				break;
			}
		}
		// 存在 这代表在权限菜单中进行了配置 需要判断权限 没有配置的菜单 默认可以使用
		if (menuAuthorityItem && menuAuthorityItem.vaServiceRes) {
			var rule = null;
			for (var _i = 0; _i < actionAccessRuleList.length; _i++) {
				if (menuAuthorityItem.vaServiceRes === actionAccessRuleList[_i].actionId) {
					rule = actionAccessRuleList[_i];
					break;
				}
			}
			if (rule) {
				if (toast) {
					return rule;
				}
				return rule.has;
			} else {
				return true;
			}
		} else {
			return true;
		}
	},


	// 判断功能是否具有权限
	hasVaServiceResource: function hasVaServiceResource(name, toast) {
		var _this = this;

		return asyncToGenerator_default()( /*#__PURE__*/regenerator_default.a.mark(function _callee() {
			var actionAccessRuleList, authorityObj, vaServiceRes, action, has, tipsMessage;
			return regenerator_default.a.wrap(function _callee$(_context) {
				while (1) {
					switch (_context.prev = _context.next) {
						case 0:
							_context.t0 = !store["a" /* default */].state.user.actionAccessRuleList;

							if (!_context.t0) {
								_context.next = 4;
								break;
							}

							_context.next = 4;
							return store["a" /* default */].dispatch("GetCompanyConfigJsonOnlyOnce");

						case 4:
							actionAccessRuleList = store["a" /* default */].state.user.actionAccessRuleList;

							// 获取功能配置

							authorityObj = functionsAuthority[name];

							if (!(authorityObj && authorityObj.vaServiceRes)) {
								_context.next = 16;
								break;
							}

							vaServiceRes = authorityObj.vaServiceRes;
							action = actionAccessRuleList.find(function (rule) {
								return rule.actionId === vaServiceRes;
							});
							// 如果再权限列表种找不到该字段 代表没有配置权限 默认可用

							if (action) {
								_context.next = 11;
								break;
							}

							return _context.abrupt("return", true);

						case 11:
							has = action.has, tipsMessage = action.tipsMessage;
							// toast 有值弹出 toast

							if (!has && toast) element_ui_common["Message"].warning(tipsMessage);
							return _context.abrupt("return", has);

						case 16:
							return _context.abrupt("return", true);

						case 17:
						case "end":
							return _context.stop();
					}
				}
			}, _callee, _this);
		}))();
	},


	/**
  * @descriptions 判断功能是否临期
  * @param name functionsAuthority key
  * @returns { url: '购买续费链接', tipsMessage: '过期文字，为空时未临期' }
  */
	isNearExpiredVaServiceResource: function isNearExpiredVaServiceResource(name) {
		var _this2 = this;

		return asyncToGenerator_default()( /*#__PURE__*/regenerator_default.a.mark(function _callee2() {
			var actionAccessRuleList, authorityObj, vaServiceRes, action;
			return regenerator_default.a.wrap(function _callee2$(_context2) {
				while (1) {
					switch (_context2.prev = _context2.next) {
						case 0:
							_context2.t0 = !store["a" /* default */].state.user.actionAccessRuleList;

							if (!_context2.t0) {
								_context2.next = 4;
								break;
							}

							_context2.next = 4;
							return store["a" /* default */].dispatch("GetCompanyConfigJsonOnlyOnce");

						case 4:
							actionAccessRuleList = store["a" /* default */].state.user.actionAccessRuleList;

							// 获取功能配置

							authorityObj = functionsAuthority[name];

							if (!(authorityObj && authorityObj.vaServiceRes)) {
								_context2.next = 14;
								break;
							}

							vaServiceRes = authorityObj.vaServiceRes;
							action = actionAccessRuleList.find(function (rule) {
								return rule.actionId === vaServiceRes;
							});
							// 如果再权限列表种找不到该字段 代表没有配置权限 默认未过期

							if (action) {
								_context2.next = 11;
								break;
							}

							return _context2.abrupt("return", {});

						case 11:
							return _context2.abrupt("return", action);

						case 14:
							return _context2.abrupt("return", {});

						case 15:
						case "end":
							return _context2.stop();
					}
				}
			}, _callee2, _this2);
		}))();
	},

	/**
  * 判断是否有权限，没有权限则弹toast，有权限则判断是否临期，临期则弹窗
  * @param name
  * @returns {Promise<boolean|*>}
  */
	vaServiceResourceCheck: function vaServiceResourceCheck(name, toast) {
		// 保证actionAccessRuleList已经存到store中
		!store["a" /* default */].state.user.actionAccessRuleList && store["a" /* default */].dispatch("GetCompanyConfigJsonOnlyOnce");
		var actionAccessRuleList = store["a" /* default */].state.user.actionAccessRuleList || [];

		// 获取功能配置
		var authorityObj = functionsAuthority[name];
		if (authorityObj && authorityObj.vaServiceRes) {
			var vaServiceRes = authorityObj.vaServiceRes;
			var action = actionAccessRuleList.find(function (rule) {
				return rule.actionId === vaServiceRes;
			});
			// 如果再权限列表种找不到该字段 代表没有配置权限 默认可用
			if (!action) return true;
			var has = action.has,
			    tipsMessage = action.tipsMessage;
			// toast 有值弹出 toast

			if (!has && toast) element_ui_common["Message"].warning(tipsMessage);
			return has;
		} else {
			return true;
		}
	}
};

/* harmony default export */ var vip = (Vip);
// CONCATENATED MODULE: ./src/main.js




 // A modern alternative to CSS resets





 // global css





 // permission control

// 全局变量

// 全局过滤器

// 自定义指令

// 客服openIm


// 处理elTable的报错


vue_esm["default"].prototype.openIM = window.openIM;
vue_esm["default"].prototype.$CbEvents = index_esm["a" /* CbEvents */];
vue_esm["default"].prototype.IM_ENUM = types_enum;

vue_esm["default"].prototype.GL_CONS = window.GL_CONS;
vue_esm["default"].prototype.BASE_URL = window.BASE_URL;

Object(utils["a" /* handleElTableLoopError */])(element_ui_common["Table"]);
vue_esm["default"].use(element_ui_common_default.a, {
	locale: zh_CN_default.a,
	size: "mini",
	zIndex: 2000
});

vue_esm["default"].config.productionTip = false;









__webpack_require__("puN1").shim();

window.tim = tim["a" /* default */];
window.TIM = tim_js_default.a;
window.store = store["a" /* default */];
window.$message = element_ui_common["Message"];
vue_esm["default"].prototype.tim = tim["a" /* default */];
vue_esm["default"].prototype.TIM = tim_js_default.a;
vue_esm["default"].prototype.$store = store["a" /* default */];
vue_esm["default"].prototype.$message = element_ui_common["Message"];
vue_esm["default"].prototype.$confirm = element_ui_common["MessageBox"].confirm;
vue_esm["default"].prototype.$hasAuthentication = hasAuthentication;
vue_esm["default"].prototype.$vip = vip;
vue_esm["default"].use(element_ui_common["Button"]);
vue_esm["default"].use(element_ui_common["Row"]);
vue_esm["default"].use(element_ui_common["Col"]);
vue_esm["default"].use(element_ui_common["Input"]);
vue_esm["default"].use(element_ui_common["Loading"]);
vue_esm["default"].use(element_ui_common["Dialog"]);
vue_esm["default"].use(element_ui_common["Popover"]);
vue_esm["default"].component('avatar', components_managerWorkstation_avatar);

// event Bus 用于无关系组件间的通信。
vue_esm["default"].prototype.$bus = new vue_esm["default"]();
new vue_esm["default"]({
	el: "#app",
	store: store["a" /* default */],
	router: router["a" /* default */],
	template: "<App/>",
	components: {
		App: src_App
	}
});

/***/ }),

/***/ "R/2u":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify__ = __webpack_require__("mvHQ");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_babel_runtime_core_js_promise__ = __webpack_require__("//Fk");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_babel_runtime_core_js_promise___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_babel_runtime_core_js_promise__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_classCallCheck__ = __webpack_require__("Zrlr");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_classCallCheck___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_classCallCheck__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_babel_runtime_helpers_createClass__ = __webpack_require__("wxAW");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_babel_runtime_helpers_createClass___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_babel_runtime_helpers_createClass__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_axios__ = __webpack_require__("mtWM");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_axios___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_axios__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_element_ui__ = __webpack_require__("zL8q");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5_element_ui___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_5_element_ui__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6__service_common__ = __webpack_require__("7S6e");








var Http = function () {
	function Http(option) {
		__WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_classCallCheck___default()(this, Http);

		this.option = option || {};
		// 是否拦截
		this.intercept = this.option.intercept || false;
		// 是否静默请求
		this.silence = this.option.silence || false;
		// 注册axios
		this.init();
		return this.connect();
	}

	__WEBPACK_IMPORTED_MODULE_3_babel_runtime_helpers_createClass___default()(Http, [{
		key: "init",
		value: function init() {
			var _this = this;

			// 创建axios实例
			this.service = __WEBPACK_IMPORTED_MODULE_4_axios___default.a.create({
				BASE_URL: "https://web.qinsilk.com/is", // api的base_url
				timeout: 300000, // 请求超时时间
				withCredentials: true, // 允许携带cookie
				headers: {
					"Content-Type": "application/json"
				}
			});

			this.service.interceptors.request.use(function (config) {
				// 记录请求发送时间
				config.startTime = Date.now();
				return config;
			}, function (error) {
				return __WEBPACK_IMPORTED_MODULE_1_babel_runtime_core_js_promise___default.a.reject(error);
			});

			// 拦截请求
			this.service.interceptors.response.use(function (response) {
				if (response && response.config && response.config.startTime) {
					try {
						var startTime = response.config.startTime;
						var endTime = Date.now();
						var time = endTime - startTime;
						var status = response.status;
						var params = {
							source: "gis-vue",
							url: response && response.request && response.request.responseURL || "",
							data: response && response.data ? __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify___default()(response.data) : "",
							status: status,
							responseTime: time,
							isLongRequest: 1
						};
						if (time > 5 * 1000) {
							Object(__WEBPACK_IMPORTED_MODULE_6__service_common__["G" /* saveInterfaceRequestTimeLog */])(params);
						}
					} catch (error) {
						console.log(error);
					}
				}
				_this.stopConnectStatus();
				if (_this.intercept) {
					if (response.data.statusCode === 1) {
						return response.data;
					} else {
						_this.errorHandle(response.data.message || '请求发生错误');
					}
				}
				return response.data;
			}, function (error) {
				if (error && error.config && error.config.startTime) {
					try {
						var startTime = error.config.startTime;
						var endTime = Date.now();
						var time = endTime - startTime;
						var status = error.response.status;
						var params = {
							url: error.response && error.response.request && error.response.request.responseURL || "",
							source: "gis-vue",
							status: status,
							responseTime: time,
							data: error.response && error.response.data ? __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify___default()(error.response.data) : ""
						};
						Object(__WEBPACK_IMPORTED_MODULE_6__service_common__["G" /* saveInterfaceRequestTimeLog */])(params);
					} catch (e) {
						console.log(e);
					}
				}
				_this.stopConnectStatus();
				console.log("err" + error); // for debug
				// 如果接口是静默处理错误信息，则直接将错误信息全部返回出去
				if (error.config.errorSilence) {
					return __WEBPACK_IMPORTED_MODULE_1_babel_runtime_core_js_promise___default.a.reject(error);
				}
				// 如果服务端返回403则认为当前请求资源要求登录，而当前会话未登录，跳至登录页面
				if (error.response && error.response.status === 403) {
					if (error.response.data && error.response.data.statusCode === 1403) {
						// 未登录
						if (location.hostname == "ex.qinsilk.com") {
							window.location.href = BASE_URL.webServer + "/admin/loginOut.ac";
						} else {
							window.location.href = BASE_URL.webServer + "/admin/loginOut.ac";
						}
						return;
					} else if (error.response.data && error.response.data.statusCode === 1401) {
						// 无权限
						window.location.href = BASE_URL.webServer + "/admin/error/authenticationFailed.ac";
						return;
					} else if (error.response.data && error.response.data.content) {
						// 其他情况弹出错误提示
						_this.errorHandle(error.response.data.content);
					}
				} else {
					_this.errorHandle(error.response && error.response.data && error.response.data.content ? error.response.data.content : error.message);
				}
				return __WEBPACK_IMPORTED_MODULE_1_babel_runtime_core_js_promise___default.a.reject(error);
			});
		}

		// 通用错误回调

	}, {
		key: "errorHandle",
		value: function errorHandle(msg) {
			// 非静默请求才提示
			Object(__WEBPACK_IMPORTED_MODULE_5_element_ui__["Message"])({
				message: msg,
				type: "error",
				duration: 2 * 1000
			});
		}

		// 解锁并隐藏loading

	}, {
		key: "stopConnectStatus",
		value: function stopConnectStatus() {
			this.lock = false;
			if (this.intercept && !this.silence) {
				this.loading && this.loading.close();
			}
		}

		// 发送请求获取数据方法

	}, {
		key: "connect",
		value: function connect() {
			var _this2 = this;

			// 锁定请求
			if (this.lock) return;
			this.lock = true;
			if (this.intercept && !this.silence) {
				this.loading = __WEBPACK_IMPORTED_MODULE_5_element_ui__["Loading"].service({
					lock: true,
					text: 'Loading',
					fullscreen: true,
					background: 'rgba(0, 0, 0, 0.7)'
				});
				setTimeout(function () {
					_this2.loading.close();
				}, 2500);
			}
			return this.service(this.option);
		}
	}]);

	return Http;
}();

// 因为项目结构问题，这里需要用函数中转一下，不然在被引入的js文件内可直接return new requst({option})


function requst(option) {
	return new Http(option);
}

/* harmony default export */ __webpack_exports__["a"] = (requst);

/***/ }),

/***/ "UVIz":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "Uiiq":
/***/ (function(module, exports) {

module.exports = "data:image/png;base64,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"

/***/ }),

/***/ "UxW6":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (immutable) */ __webpack_exports__["g"] = getOSSAddress;
/* harmony export (immutable) */ __webpack_exports__["k"] = getUserConfig;
/* harmony export (immutable) */ __webpack_exports__["i"] = getScanPaymentStatus;
/* harmony export (immutable) */ __webpack_exports__["h"] = getQRCodeURL;
/* harmony export (immutable) */ __webpack_exports__["o"] = saveUserConfig;
/* harmony export (immutable) */ __webpack_exports__["a"] = batchSaveUserConfig;
/* harmony export (immutable) */ __webpack_exports__["n"] = saveSystemConfig;
/* harmony export (immutable) */ __webpack_exports__["c"] = getAllAccount;
/* harmony export (immutable) */ __webpack_exports__["d"] = getAllAccountItem;
/* harmony export (immutable) */ __webpack_exports__["e"] = getAllIndustry;
/* harmony export (immutable) */ __webpack_exports__["m"] = saveIndustryInfo;
/* harmony export (immutable) */ __webpack_exports__["f"] = getExistDebtWholesaleOrder;
/* harmony export (immutable) */ __webpack_exports__["l"] = getUserCounselorAndGroup;
/* harmony export (immutable) */ __webpack_exports__["p"] = updateCompany;
/* harmony export (immutable) */ __webpack_exports__["j"] = getStoreSoleQrcodeList;
/* harmony export (immutable) */ __webpack_exports__["b"] = comStoreSelectListJSON;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__service_request__ = __webpack_require__("R/2u");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_qs__ = __webpack_require__("mw3O");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_qs___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_qs__);



function getOSSAddress(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/file/img/getLogoUploadUrl.ac",
		method: "post",
		params: params
	});
}

function getUserConfig(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/getUserConfig.ac",
		method: "post",
		data: data
	});
}

function getScanPaymentStatus() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/getBarpayConfig.ac",
		method: "post"
	});
}

function getQRCodeURL() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/qrcodeReceiptUrlGet.ac",
		method: "post"
	});
}

function saveUserConfig(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/saveOrUpdateUserConfigNew.ac",
		method: "post",
		data: data
	});
}

function batchSaveUserConfig(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/batchSaveUserConfig.ac",
		method: "post",
		data: data
	});
}

function saveSystemConfig(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/saveCompanyConfig.ac",
		method: "post",
		headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
		data: __WEBPACK_IMPORTED_MODULE_1_qs___default.a.stringify(data)
	});
}

function getAllAccount() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/finance/account/allAccount.ac",
		method: "post"
	});
}

function getAllAccountItem() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/finance/accountItem/allAccountItem.ac",
		method: "post"
	});
}

function getAllIndustry() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/crmf/gis/merchantCertificate/getIndustry.ac",
		method: "post"
	});
}

function saveIndustryInfo(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/crmf/gis/merchantCertificate/saveOrUpdateIndustryInfo.ac",
		method: "post",
		data: data
	});
}

function getExistDebtWholesaleOrder() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/sale/existDebtWholesaleOrder.ac",
		method: "post"
	});
}

function getUserCounselorAndGroup() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/console/gis/getUserCounselorAndGroup.ac",
		method: "post"
	});
}

function updateCompany(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/updateCompany.ac",
		method: "post",
		data: data
	});
}

/** 门店独立收款：门店+收款码+账户/类型列表（进销存） */
function getStoreSoleQrcodeList(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/system/companyConfig/getStoreSoleQrcodeList.ac",
		method: "post",
		data: data || {}
	});
}

// 所属门店选择列表
function comStoreSelectListJSON(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/comstore/comStoreSelectListJSON.ac?queryAll=true",
		method: "post",
		params: params
	});
}

/***/ }),

/***/ "X2Oc":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function(jQuery, $) {/* unused harmony export translateGroupSystemNotice */
/* harmony export (immutable) */ __webpack_exports__["M"] = getWebBrowser;
/* unused harmony export getContextPath */
/* unused harmony export transKeyMap */
/* harmony export (immutable) */ __webpack_exports__["c"] = accMul;
/* harmony export (immutable) */ __webpack_exports__["b"] = accDiv;
/* harmony export (immutable) */ __webpack_exports__["a"] = accAdd;
/* harmony export (immutable) */ __webpack_exports__["p"] = decimalAdd;
/* harmony export (immutable) */ __webpack_exports__["d"] = accSub;
/* harmony export (immutable) */ __webpack_exports__["q"] = decimalSub;
/* harmony export (immutable) */ __webpack_exports__["W"] = setQuantityDecimal;
/* harmony export (immutable) */ __webpack_exports__["Z"] = setWranNumberDecimal;
/* unused harmony export countDecimal */
/* harmony export (immutable) */ __webpack_exports__["X"] = setScale;
/* harmony export (immutable) */ __webpack_exports__["Y"] = setScaleToFixed;
/* unused harmony export accAbs */
/* unused harmony export objectArrayToIdString */
/* unused harmony export objectArrayToIdArray */
/* harmony export (immutable) */ __webpack_exports__["f"] = arrayDiff;
/* unused harmony export idStringToObjectArray */
/* unused harmony export keyIndexOfArr */
/* harmony export (immutable) */ __webpack_exports__["D"] = getObject;
/* harmony export (immutable) */ __webpack_exports__["E"] = getObjectByObject;
/* harmony export (immutable) */ __webpack_exports__["F"] = getObjectList;
/* harmony export (immutable) */ __webpack_exports__["i"] = contains;
/* harmony export (immutable) */ __webpack_exports__["j"] = containsValue;
/* unused harmony export add */
/* unused harmony export remove */
/* harmony export (immutable) */ __webpack_exports__["U"] = removeByKey;
/* unused harmony export dateFormat */
/* harmony export (immutable) */ __webpack_exports__["k"] = dateFormatEx;
/* unused harmony export openUrl */
/* harmony export (immutable) */ __webpack_exports__["_2"] = stringToDate;
/* harmony export (immutable) */ __webpack_exports__["v"] = getDayBeginStr;
/* harmony export (immutable) */ __webpack_exports__["_5"] = transferGMTStringtoBJTime;
/* harmony export (immutable) */ __webpack_exports__["u"] = getDayBegin;
/* unused harmony export getDayEndStr */
/* harmony export (immutable) */ __webpack_exports__["w"] = getDayEnd;
/* harmony export (immutable) */ __webpack_exports__["H"] = getOffsetDayBeginStr;
/* harmony export (immutable) */ __webpack_exports__["G"] = getOffsetDayBegin;
/* unused harmony export getOffsetMinuteBeginStr */
/* harmony export (immutable) */ __webpack_exports__["I"] = getOffsetMinuteBegin;
/* harmony export (immutable) */ __webpack_exports__["e"] = addDate;
/* unused harmony export addMonth */
/* unused harmony export addYear */
/* unused harmony export getYesterday */
/* unused harmony export awayFormThePresentDays */
/* unused harmony export getTomorrow */
/* harmony export (immutable) */ __webpack_exports__["y"] = getLastMonthDate;
/* harmony export (immutable) */ __webpack_exports__["B"] = getNextMonthDate;
/* harmony export (immutable) */ __webpack_exports__["z"] = getLastYearDate;
/* harmony export (immutable) */ __webpack_exports__["C"] = getNextYearDate;
/* harmony export (immutable) */ __webpack_exports__["l"] = dateIsEquals;
/* harmony export (immutable) */ __webpack_exports__["m"] = dateIsLessThan;
/* unused harmony export mergeBySn */
/* unused harmony export group */
/* harmony export (immutable) */ __webpack_exports__["_1"] = sortFunction;
/* unused harmony export htmlDecode */
/* unused harmony export htmlEncode */
/* unused harmony export isBlank */
/* unused harmony export trim */
/* unused harmony export ltrim */
/* unused harmony export rtrim */
/* unused harmony export stopEvent */
/* unused harmony export showMessageIfLowLevelBrowser */
/* unused harmony export setConfig */
/* unused harmony export saveConfig */
/* harmony export (immutable) */ __webpack_exports__["t"] = getCookie;
/* unused harmony export getAllConfig */
/* unused harmony export checkQueryParams */
/* unused harmony export getQueryString */
/* unused harmony export getEvtTarget */
/* harmony export (immutable) */ __webpack_exports__["o"] = debounce;
/* harmony export (immutable) */ __webpack_exports__["_3"] = throttle;
/* harmony export (immutable) */ __webpack_exports__["_4"] = throttleForAsync;
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "N", function() { return includeAuthority; });
/* harmony export (immutable) */ __webpack_exports__["r"] = deepCopy;
/* harmony export (immutable) */ __webpack_exports__["s"] = deepCopyPlus;
/* harmony export (immutable) */ __webpack_exports__["V"] = removeListForValue;
/* harmony export (immutable) */ __webpack_exports__["R"] = isNumberType;
/* harmony export (immutable) */ __webpack_exports__["Q"] = isNumber;
/* harmony export (immutable) */ __webpack_exports__["x"] = getImageSizeFromFileData;
/* harmony export (immutable) */ __webpack_exports__["h"] = compareVersion;
/* harmony export (immutable) */ __webpack_exports__["g"] = binarySearch;
/* harmony export (immutable) */ __webpack_exports__["K"] = getUUID;
/* harmony export (immutable) */ __webpack_exports__["A"] = getNetworkType;
/* harmony export (immutable) */ __webpack_exports__["O"] = includeEmoji;
/* harmony export (immutable) */ __webpack_exports__["S"] = isPureNum;
/* harmony export (immutable) */ __webpack_exports__["n"] = dealWithPic;
/* harmony export (immutable) */ __webpack_exports__["J"] = getOrderTypeBySn;
/* harmony export (immutable) */ __webpack_exports__["T"] = number_chinese;
/* harmony export (immutable) */ __webpack_exports__["_0"] = shelfLife;
/* harmony export (immutable) */ __webpack_exports__["L"] = getValidNum;
/* harmony export (immutable) */ __webpack_exports__["P"] = isEanBarcode;
/* harmony export (immutable) */ __webpack_exports__["_6"] = validateGBCode;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise__ = __webpack_require__("//Fk");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_babel_runtime_regenerator__ = __webpack_require__("Xxa5");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_babel_runtime_regenerator___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_babel_runtime_regenerator__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_asyncToGenerator__ = __webpack_require__("exGp");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_asyncToGenerator___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_asyncToGenerator__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify__ = __webpack_require__("mvHQ");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_babel_runtime_helpers_typeof__ = __webpack_require__("pFYg");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_4_babel_runtime_helpers_typeof___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_4_babel_runtime_helpers_typeof__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_5__store__ = __webpack_require__("IcnI");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_decimal_js__ = __webpack_require__("wbDN");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_6_decimal_js___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_6_decimal_js__);








function translateGroupSystemNotice(message) {
	var groupName = message.payload.groupProfile.groupName || message.payload.groupProfile.groupID;
	switch (message.payload.operationType) {
		case 1:
			return message.payload.operatorID + ' \u7533\u8BF7\u52A0\u5165\u7FA4\u7EC4\uFF1A' + groupName;
		case 2:
			return '\u6210\u529F\u52A0\u5165\u7FA4\u7EC4\uFF1A' + groupName;
		case 3:
			return '\u7533\u8BF7\u52A0\u5165\u7FA4\u7EC4\uFF1A' + groupName + '\u88AB\u62D2\u7EDD';
		case 4:
			return '\u88AB\u7BA1\u7406\u5458' + message.payload.operatorID + '\u8E22\u51FA\u7FA4\u7EC4\uFF1A' + groupName;
		case 5:
			return '\u7FA4\uFF1A' + groupName + ' \u5DF2\u88AB' + message.payload.operatorID + '\u89E3\u6563';
		case 6:
			return message.payload.operatorID + '\u521B\u5EFA\u7FA4\uFF1A' + groupName;
		case 7:
			return message.payload.operatorID + '\u9080\u8BF7\u4F60\u52A0\u7FA4\uFF1A' + groupName;
		case 8:
			return '\u4F60\u9000\u51FA\u7FA4\u7EC4\uFF1A' + groupName;
		case 9:
			return '\u4F60\u88AB' + message.payload.operatorID + '\u8BBE\u7F6E\u4E3A\u7FA4\uFF1A' + groupName + '\u7684\u7BA1\u7406\u5458';
		case 10:
			return '\u4F60\u88AB' + message.payload.operatorID + '\u64A4\u9500\u7FA4\uFF1A' + groupName + '\u7684\u7BA1\u7406\u5458\u8EAB\u4EFD';
		case 255:
			return '自定义群系统通知';
	}
}
/**
 * 获取浏览器标识
 */
function getWebBrowser() {
	// 调试代码
	// return "IE8";
	var userAgent = navigator.userAgent; // 取得浏览器的userAgent字符串
	var isOpera = userAgent.indexOf("Opera") > -1; // 判断是否Opera浏览器
	var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera; // 判断是否IE浏览器
	var isFF = userAgent.indexOf("Firefox") > -1; // 判断是否Firefox浏览器
	var isSafari = userAgent.indexOf("Safari") > -1; // 判断是否Safari浏览器
	var isChrome = userAgent.indexOf("Chrome") > -1; // 判断是否Chrome浏览器
	if (isChrome) {
		return "Chrome";
	}
	if (isFF) {
		return "Firefox";
	}
	if (isSafari) {
		return "Safari";
	}
	if (isOpera) {
		return "Opera";
	}
	if (isIE) {
		var IE5 = IE55 = IE6 = IE7 = IE8 = false;
		var reIE = new RegExp("MSIE (\\d+\\.\\d+);");
		reIE.test(userAgent);
		var fIEVersion = parseFloat(RegExp["$1"]);
		IE5 = fIEVersion == 5.0;
		IE55 = fIEVersion == 5.5;
		IE6 = fIEVersion == 6.0;
		IE7 = fIEVersion == 7.0;
		IE8 = fIEVersion == 8.0;
		if (IE5) {
			return "IE5";
		}
		if (IE55) {
			return "IE55";
		}
		if (IE6) {
			return "IE6";
		}
		if (IE7) {
			return "IE7";
		}
		if (IE8) {
			return "IE8";
		} else {
			return "IE9+";
		}
	} else {
		return "unknown";
	}
}

/**
 * 使用js获取当前应用名称
 *
 * @returns
 */
function getContextPath() {
	var contextPath = document.location.pathname;
	var index = contextPath.substr(1).indexOf("/");
	contextPath = contextPath.substr(0, index + 1);
	return contextPath;
}

/**
 * 把json数组对象srcData中的key值改为keyMaps中对应的值 比如 srcData: [{id: 1, name: '姓名1'}, {id:
 * 2, name: '姓名2'}]; keyMaps : {text:"name",val:"id"}; 则会返回 [{val: 1, text:
 * '姓名1'}, {val: 2, text: '姓名2'}];
 *
 * @param srcData
 * @param keyMaps
 */
function transKeyMap(srcData, keyMaps) {
	if (keyMaps === undefined || undefined === "") {
		return srcData;
	}
	for (var i = 0; i < srcData.length; i++) {
		for (var srcObject in srcData[i]) {
			for (var keyMap in keyMaps) {
				if (srcObject === keyMaps[keyMap]) {
					srcData[i][keyMap] = srcData[i][srcObject];
				}
			}
		}
	}
	return srcData;
}

// 乘法
function accMul(arg1, arg2) {
	arg1 = arg1 || 0;
	arg2 = arg2 || 0;
	var m = 0;
	var s1 = arg1.toString();
	var s2 = arg2.toString();
	m += s1.split('.')[1] ? s1.split('.')[1].length : 0;
	m += s2.split('.')[1] ? s2.split('.')[1].length : 0;
	return Number(s1.replace('.', '')) * Number(s2.replace('.', '')) / Math.pow(10, m);
}
// 除法
function accDiv(arg1, arg2) {
	var t1 = 0;
	var t2 = 0;
	var r1, r2;
	t1 = arg1.toString().split('.')[1] ? arg1.toString().split('.')[1].length : 0;
	t2 = arg2.toString().split('.')[1] ? arg2.toString().split('.')[1].length : 0;
	r1 = Number(arg1.toString().replace('.', ''));
	r2 = Number(arg2.toString().replace('.', ''));
	return accMul(r1 / r2, Math.pow(10, t2 - t1));
}
// 加法
function accAdd(arg1, arg2) {
	var r1, r2, m, n;
	try {
		r1 = arg1.toString().split(".")[1].length;
	} catch (e) {
		r1 = 0;
	}
	try {
		r2 = arg2.toString().split(".")[1].length;
	} catch (e) {
		r2 = 0;
	}
	m = Math.pow(10, Math.max(r1, r2));
	n = r1 >= r2 ? r1 : r2;
	return parseFloat(((arg1 * m + arg2 * m) / m).toFixed(n));
}
//基于decimal的加法，decimal小数位
function decimalAdd(arg1, arg2, decimal) {
	if (!__WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a) accAdd(arg1, arg2);
	var a = new __WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a(arg1 || 0);
	var b = new __WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a(arg2 || 0);
	var res = a.add(b);
	// 四舍五入指定小数位
	return decimal || decimal === 0 ? parseFloat(res.toDecimalPlaces(decimal, __WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a.ROUND_HALF_UP).toString()) : parseFloat(res.toString());
}
// 减法
function accSub(arg1, arg2) {
	var r1, r2, m, n;
	try {
		r1 = arg1.toString().split(".")[1].length;
	} catch (e) {
		r1 = 0;
	}
	try {
		r2 = arg2.toString().split(".")[1].length;
	} catch (e) {
		r2 = 0;
	}
	m = Math.pow(10, Math.max(r1, r2));
	n = r1 >= r2 ? r1 : r2;
	return parseFloat(((arg1 * m - arg2 * m) / m).toFixed(n));
}
//基于decimal的减法，decimal小数位
function decimalSub(arg1, arg2, decimal) {
	if (!__WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a) accSub(arg1, arg2);
	var a = new __WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a(arg1 || 0);
	var b = new __WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a(arg2 || 0);
	var res = a.sub(b);
	// 四舍五入指定小数位
	return decimal || decimal === 0 ? parseFloat(res.toDecimalPlaces(decimal, __WEBPACK_IMPORTED_MODULE_6_decimal_js___default.a.ROUND_HALF_UP).toString()) : parseFloat(res.toString());
}

// 截取小数位,返回数值对象
function setQuantityDecimal(a, n) {
	if (!n) {
		return a;
	}
	var value;
	try {
		value = accDiv(parseInt(accMul(a, Math.pow(10, n))), Math.pow(10, n));
	} catch (e) {
		return a;
	}

	return value;
}

// 库存预警上下限的截取
function setWranNumberDecimal(a, n) {
	if (a === undefined || a === '' || isNaN(a) || a === null) {
		return "";
	}
	return setQuantityDecimal(a, n);
}

// 计算有多少个小数位
function countDecimal(value) {
	if (!value) {
		return 0;
	}
	var stringValue = value.toString(); // 将数值转换为字符串
	var parts = stringValue.split('.'); // 以小数点分割字符串
	return parts.length > 1 ? parts[1].length : 0; // 如果有小数部分，返回小数部分的长度
}

// 四舍五入截取小数位,返回数值对象
function setScale(a, n) {
	var value;
	try {
		value = accDiv(Math.round(accMul(a, Math.pow(10, n))), Math.pow(10, n));
	} catch (e) {
		return a;
	}

	return value;
}
// 先四舍五入，然后用toFixed返回
function setScaleToFixed(a, n) {
	var value;
	try {
		value = accDiv(Math.round(accMul(a, Math.pow(10, n))), Math.pow(10, n)).toFixed(n);
	} catch (e) {
		return a;
	}

	return value;
}

// 取绝对值
function accAbs(arg1) {
	var value;
	try {
		value = Math.abs(arg1);
	} catch (e) {
		value = 0;
	}
	return value;
}

/**
 * 从数组中，把对象的ID提出来拼成字符串,如1,2,3
 * @param objArray 对象数组
 * @param keyName 所要提取属性的名称
 * @param splitChar拼接分隔符
 * @returns {string}
 */
function objectArrayToIdString(objArray, keyName, splitChar) {
	var idStr = "";
	for (var i = 0; i < objArray.length; i++) {
		if (i == objArray.length - 1) {
			idStr += objArray[i][keyName];
		} else {
			idStr += objArray[i][keyName] + splitChar;
		}
	}
	return idStr;
}

/**
 * 从数组中，把对象的ID提出来放到新的数组中,如[1,2,3]
 * @param objArray 对象数组
 * @param keyName 所要提取属性的名称
 * @returns {string}
 */
function objectArrayToIdArray(objArray, keyName) {
	var idArray = [];
	for (var i = 0; i < objArray.length; i++) {
		idArray.push(objArray[i][keyName]);
	}
	return idArray;
}

// 取两个数组的差集
function arrayDiff(arr1, arr2) {
	return arr1.filter(function (v) {
		return arr2.indexOf(v) === -1;
	});
}

/**
 * 从数组中，根据对象ID拼成字符串找到对应的对象
 * @param objArrayContainer
 * @param idString
 * @param keyName
 * @param splitChar
 * @returns {Array}
 */
function idStringToObjectArray(objArrayContainer, idString, keyName, splitChar) {
	var resultArray = [];
	if (idString == undefined || idString == "") {
		return resultArray;
	}
	var ids = idString.split(splitChar);
	for (var j = 0; j < objArrayContainer.length; j++) {
		for (var i = 0; i < ids.length; i++) {
			if (ids[i] == objArrayContainer[j][keyName]) {
				resultArray.push(objArrayContainer[j]);
				break;
			}
		}
	}
	return resultArray;
}

/**
 * 从对象数组中，取出key对应的值为obj的位置
 * @param array
 * @param obj
 * @param key
 * @returns {*}
 */
function keyIndexOfArr(obj, array, key) {
	if (array && array.length > 0) {
		for (var i = 0; i < array.length; i++) {
			if (array[i][key] == obj) {
				return i;
			}
		}
		return -1;
	} else {
		return -1;
	}
}

function equals(obj, obj1) {
	if (obj == obj1) return true;
	if (typeof obj1 == "undefined" || obj1 == null || (typeof obj1 === 'undefined' ? 'undefined' : __WEBPACK_IMPORTED_MODULE_4_babel_runtime_helpers_typeof___default()(obj1)) != "object") return false;
	var length = 0;
	var length1 = 0;
	for (var ele in obj) {
		length++;
	}for (var ele in obj1) {
		length1++;
	}if (length != length1) return false;
	if (obj1.constructor == obj.constructor) {
		for (var ele in obj) {
			if (__WEBPACK_IMPORTED_MODULE_4_babel_runtime_helpers_typeof___default()(obj[ele]) == "object") {
				if (!obj[ele].equals(obj1[ele])) return false;
			} else if (typeof obj[ele] == "function") {
				if (!obj[ele].toString().equals(obj1[ele].toString())) return false;
			} else if (obj[ele] != obj1[ele]) return false;
		}
		return true;
	}
	return false;
}

/**
 * 从对象数组中，取出keyName对应的值为value的第一个对象
 * @param arr
 * @param keyName
 * @param value
 * @returns {*}
 */
function getObject(arr, keyName, value) {
	if (Array.isArray(arr)) {
		for (var i = 0; i < arr.length; i++) {
			if (arr[i] && equals(arr[i][keyName], value)) {
				return arr[i];
			}
		}
	}
	return undefined;
}
/**
 * 从对象数组中，取出几个key的值都和paramObject中几个key的值一一对应的对象
 * @param arr
 * @param paramObject 获取对象数据的参数,格式如{goodsSn:'sn001',colorId:201,sizeId:232}
 * @returns {*}
 */
function getObjectByObject(arr, paramObject) {
	var equalFlag;
	if (Array.isArray(arr)) {
		for (var i = 0; i < arr.length; i++) {
			equalFlag = true;

			for (var property in paramObject) {
				if (!equals(arr[i][property], paramObject[property])) {
					equalFlag = false;
					break;
				}
			}

			if (equalFlag) {
				return arr[i];
			}
		}
	}
	return undefined;
}

/**
 * 从对象数组中，取出keyName对应的值为value的对象数组
 * @param arr
 * @param keyName
 * @param value
 * @returns {*}
 */
function getObjectList(arr, keyName, value) {
	var resultArray = [];
	if (Array.isArray(arr)) {
		for (var i = 0; i < arr.length; i++) {
			if (equals(arr[i][keyName], value)) {
				resultArray.push(arr[i]);
			}
		}
	}
	return resultArray;
}

/**
 * 判断数组中是否包含某个对象
 * @param arr 数组
 * @param item 对象
 * @returns {Boolean}
 */
function contains(arr, item) {
	if (Array.isArray(arr)) {
		for (var i = 0; i < arr.length; i++) {
			if (equals(arr[i], item)) {
				return true;
			}
		}
	}
	return false;
}

/**
 * 判断数组中是否包含key对应的值为value的对象
 * @param arr
 * @param key
 * @param value
 * @returns {Boolean}
 */
function containsValue(arr, key, value) {
	if (Array.isArray(arr)) {
		for (var i = 0; i < arr.length; i++) {
			if (equals(arr[i][key], value)) {
				return true;
			}
		}
	}
	return false;
}

// add
function add(arr, item) {
	arr = Array.isArray(arr) ? arr : [];
	for (var i = 0; i < arr.length; i++) {
		if (equals(arr[i], item)) {
			return;
		}
	}
	arr.push(item);
}

// remove
function remove(arr, item) {
	if (Array.isArray(arr)) {
		for (var i = 0; i < arr.length; i++) {
			if (equals(arr[i], item)) {
				arr.splice(i, 1);
				return;
			}
		}
	}
}

/**
 * 从数组中删除key对应的值为value的一条数据
 * @param arr
 * @param key
 * @param value
 */
function removeByKey(arr, key, value) {
	if (Array.isArray(arr)) {
		for (var i = 0; i < arr.length; i++) {
			if (equals(arr[i][key], value)) {
				arr.splice(i, 1);
				return;
			}
		}
	}
}

// 从url中提取菜单id
// (function($) {
// 	/**
// 	 * 获取当前Url参数
// 	 */
// 	$.getUrlParam = function(name) {
// 		var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
// 		var r = window.location.search.substr(1).match(reg);
// 		if (r != null)
// 			return unescape(r[2]);
// 		return null;
// 	};
// 	/**
// 	 * 返回的是当前字符串形式的参数，例如：class_id=3&id=2&
// 	 */
// 	$.getUrlParamStr = function(){
// 		var q=location.search.substr(1);
// 		var qs=q.split('&');
// 		var argStr='';
// 		if(qs){
// 			for(var i=0;i<qs.length;i++){
// 				argStr+=qs[i].substring(0,qs[i].indexOf('='))+'='+qs[i].substring(qs[i].indexOf('=')+1)+'&';
// 			}
// 		}
// 		return argStr;
// 	};

// 	/**
// 	 * 当前URL中的对象形式的参数
// 	 */
// 	$.getCurParamObject= function(){
// 		var args=new Object();
// 		var query=location.search.substring(1);//获取查询串
// 		var pairs=query.split(",");//在逗号处断开
// 		for(var i=0;i<pairs.length;i++){
// 			var pos=pairs[i].indexOf('=');//查找name=value
// 			if(pos==-1){//如果没有找到就跳过
// 				continue;
// 			}
// 			var argname=pairs[i].substring(0,pos);//提取name
// 			var value=pairs[i].substring(pos+1);//提取value
// 			args[argname]=unescape(value);//存为属性
// 		}
// 		return args;//返回对象
// 	};

// 	/**
// 	 * 指定URL中的对象形式的参数
// 	 */
// 	$.getUrlParamObject = function(url) {
// 		var theRequest = new Object();
// 		var pos = url.indexOf("?");
// 		if (pos != -1) {
// 			var str = url.substr(pos + 1);
// 			strs = str.split("&");
// 			for ( var i = 0; i < strs.length; i++) {
// 				theRequest[strs[i].split("=")[0]] = unescape(strs[i].split("=")[1]);
// 			}
// 		}
// 		return theRequest;
// 	};
// 	/**
// 	 * 取出URL路径部分
// 	 *
// 	 * @param url
// 	 * @returns {String}
// 	 */
// 	$.getUrlPagePath = function(url)
// 	{
// 		var pagePath=url;
// 		var pos = url.indexOf("?");
// 		if (pos != -1) {
// 			var pagePath = url.substr(0,pos);
// 		}
// 		return pagePath;
// 	};

// 	$.gotoPage = function(url,mid)
// 	{
// 		var urlParams = $.getUrlParamObject(url);
// 		var urlParamsStr = '';

// 		if(mid==undefined)
// 		{
// 			mid = getActiveMId();
// 		}
// 		urlParams['mid'] = mid;

// 		$.each(urlParams,function(key,value) {
// 			urlParamsStr += (key+"="+value+"&");
// 	    });
// 		var toUrl = $.getUrlPagePath(url) + "?"+ urlParamsStr;
// 		window.location.href = toUrl;
// 	};
// })(jQuery);

// /**
//  * 从url中提取菜单id
//  * @returns
//  */
// function getActiveMId()
// {
// 	var mid = $.getUrlParam("mid");
// 	if(mid == undefined)
// 	{
// 		mid = 1;
// 	}
// 	return mid;
// };

/**
 * 日期格式化（不包含时点）
 * @param val
 * @param opt
 * @param row
 * @returns
 */
function dateFormat(val, opt, row) {
	var date = new Date(val);
	var html_con = date.Format("yyyy-") + "<strong>" + date.Format("MM-dd") + "</strong>";
	return html_con;
}

function dateFormatEx(val) {
	var date = new Date(val);
	var html_con = date.Format("yyyy-MM-dd hh:mm:ss");
	return html_con;
}
/**
 * 打开新窗口
 * @param url
 */
function openUrl(url) {
	var f = document.createElement("form");
	f.setAttribute("action", url);
	f.setAttribute("method", "get");
	f.setAttribute("target", "_black");
	document.body.appendChild(f);
	f.submit();
}

/**
 * 把字符串转换成日期
 */
function stringToDate(str) {
	if (str == null || str == undefined || str == "") {
		return;
	} else {
		var temp = str.toString();

		temp = temp.replace(/-/g, "/");

		var date = new Date(Date.parse(temp));

		return date;
	}
}

/**
 * 获取日期的最开始时间（0点0分0秒）
 * @param date
 * @returns {String}
 */
function getDayBeginStr(date) {
	if (date == null || date == undefined || date == "") {
		return;
	} else {
		return date.Format("yyyy-MM-dd") + " 00:00:00";
	}
}

/**
 * 将时间转化为GMT时间(通过计算偏移量)，再转换为北京时间
 * @param value 字符串格式的时间变量
 * @param format 格式化格式
 * @returns
 */
function transferGMTStringtoBJTime(value, format) {
	if (value == null || value == undefined || value == "") {
		return null;
	}
	var date = stringToDate(value); // 创建一个Date对象
	if (date == "Invalid Date") {
		return null;
	} else {
		var offset = 8; // 北京时间，东8区
		var bjTime = date.getTime() + date.getTimezoneOffset() * 60000 + 3600000 * offset;
		return new Date(bjTime).Format(format || "yyyy-MM-dd hh:mm:ss");
	}
}

/**
 * 获取日期的最开始时间（0点0分0秒）
 * @param date
 * @returns {Date}
 */
function getDayBegin(date) {
	return stringToDate(getDayBeginStr(date));
}

/**
 * 获取日期的最晚时间（23点59分59秒）
 * @param date
 * @returns {String}
 */
function getDayEndStr(date) {
	if (date == null || date == undefined || date == "") {
		return;
	} else {
		return date.Format("yyyy-MM-dd") + " 23:59:59";
	}
}

/**
 * 获取日期的最晚时间（23点59分59秒）
 * @param date
 * @returns {Date}
 */
function getDayEnd(date) {
	return stringToDate(getDayEndStr(date));
}

/**
 * 获取日期N天后的那天的最开始时间（0点0分0秒）
 * @param date
 * @returns {String}
 */
function getOffsetDayBeginStr(date, offsetDay) {
	if (date == null || date == undefined || date == "") {
		return;
	} else {
		var targetDate = new Date(date.getTime());
		targetDate.setDate(targetDate.getDate() + offsetDay);
		return targetDate.Format("yyyy-MM-dd") + " 00:00:00";
	}
}
/**
 * 获取日期N天后的那天的最开始时间（0点0分0秒）
 * @param date
 * @returns {Date}
 */
function getOffsetDayBegin(date, offsetDay) {
	return stringToDate(getOffsetDayBeginStr(date, offsetDay));
}

/**
 * 获取日期N分钟后的最开始时间（0秒）
 * @param date
 * @returns {String}
 */
function getOffsetMinuteBeginStr(date, offsetMinute) {
	if (date == null || date == undefined || date == "") {
		return;
	} else {
		var targetDate = new Date(date.getTime());
		targetDate.setMinutes(targetDate.getMinutes() + offsetMinute);
		return targetDate.Format("yyyy-MM-dd hh:mm") + ":00";
	}
}
/**
 * 获取日期N分钟后的最开始时间（0秒）
 * @param date
 * @returns {Date}
 */
function getOffsetMinuteBegin(date, offsetMinute) {
	return stringToDate(getOffsetMinuteBeginStr(date, offsetMinute));
}

/**
 * 根据指定的日期返回加减天数之后的日期
 *
 * @param date 指定的日期
 * @param days 可为正负整数，代表加减的天数
 * @returns {Date} 加减后的日期
 */
function addDate(date, days) {
	var newDate = new Date(date);
	newDate.setDate(newDate.getDate() + days);
	return newDate;
}

/**
 * 根据指定的日期返回加减月份数之后的日期
 *
 * @param date 指定的日期
 * @param months 可为正负整数，代表加减的月份数
 * @returns {Date} 加减后的日期
 */
function addMonth(date, months) {
	var newDate = new Date(date);
	newDate.setMonth(newDate.getMonth() + months);
	return newDate;
}

/**
 * 根据指定的日期返回加减年数之后的日期
 *
 * @param date 指定的日期
 * @param years 可为正负整数，代表加减的年数
 * @returns {Date} 加减后的日期
 */
function addYear(date, years) {
	var newDate = new Date(date);
	newDate.setYear(newDate.getFullYear() + years);
	return newDate;
}

/**
 * 获取当前日期的前一天（昨天）
 *
 * @param date 指定日期
 * @returns {Date} 当前日期的前一天
 */
function getYesterday(date) {
	return addDate(date, -1);
}

/**
 * 获取距离当前时间的天数
 *
 * @param {number | Date}date 指定日期
 * @returns {number} 天数
 */
function awayFormThePresentDays(date) {
	return Math.ceil((new Date(date).getTime() - new Date().getTime()) / 1000 / 60 / 60 / 24); // 向上取整
}

/**
 * 获取当前日期的后一天（明天）
 *
 * @param date 指定日期
 * @returns {Date} 当前日期的后一天
 */
function getTomorrow(date) {
	return addDate(date, 1);
}

/**
 * 返回指定日期的上个月的日期
 *
 * @param date 指定日期
 * @returns {Date} 指定日期的上个月的日期
 */
function getLastMonthDate(date) {
	var newDate = addMonth(date, -1);
	var vMonth = date.getMonth();
	var vNewMonth = newDate.getMonth();
	// 有可能指定日期的月份和上个月指定日期的月份相同。
	// 比如指定日期为5月31日,求得的newDate为5月1日,此时应该返回4月30日
	if (vMonth == vNewMonth) {
		var firstDate = new Date(date.getFullYear(), date.getMonth(), 1);
		return getYesterday(firstDate);
	} else {
		return newDate;
	}
}

/**
 * 返回指定日期的下个月的日期
 *
 * @param date 指定日期
 * @returns {Date} 指定日期的下个月的日期
 */
function getNextMonthDate(date) {
	return addMonth(date, 1);
}

/**
 * 返回指定日期的去年的日期
 *
 * @param date 指定日期
 * @returns {Date} 指定日期的去年的日期
 */
function getLastYearDate(date) {
	return addYear(date, -1);
}

/**
 * 返回指定日期的明年的日期
 *
 * @param date 指定日期
 * @returns {Date} 指定日期的明年的日期
 */
function getNextYearDate(date) {
	return addYear(date, 1);
}

/**
 * 判断两个日期的年月日是否一样
 *
 * @param one 指定日期
 * @param two 指定日期
 */
function dateIsEquals(one, two, format) {
	if (one instanceof Date && two instanceof Date && Object.prototype.toString.call(format) === "[object String]") {
		throw "参数类型不合法！";
	}
	if (!format) {
		format = "yyyy-MM-dd";
	}
	return one.Format(format) == two.Format(format);
}

/**
 * 判断日期一是否小于日期二
 *
 * @param one 指定日期一
 * @param two 指定日期二
 * @param format 比较格式，默认比较到日
 */
function dateIsLessThan(one, two) {
	if (!(one instanceof Date) || !(two instanceof Date)) {
		throw "参数类型不合法！";
	}
	var d1 = new Date(one.getFullYear(), one.getMonth(), one.getDate());
	var d2 = new Date(two.getFullYear(), two.getMonth(), two.getDate());
	return d1.getTime() < d2.getTime();
}

/**
 * 对分组数据进行合并
 * @param groupArray 分组后的数据
 * @returns {Array}
 */

function mergeBySn(groupArray) {
	var mergeArray = [];
	for (var key in groupArray) {
		var groupList = groupArray[key]; // 当前分组数据
		var groupLen = groupList.length;
		var mergeObj = {
			goodsSn: groupList[0].goodsSn,
			goodName: groupList[0].goodName,
			colorName: groupList[0].colorName,
			sizeName: groupList[0].sizeName,
			unit: groupList[0].unit,
			quantity: 0,
			truePrice: 0.0,
			trueAmount: 0.0 // 第一个元素的信息赋值到合并对象中
		};for (var j = 0; j < groupLen; j++) {
			mergeObj.quantity += groupList[j].quantity;
			mergeObj.truePrice += groupList[j].truePrice;
			mergeObj.trueAmount += groupList[j].trueAmount;
		}
		mergeArray.push(mergeObj);
	}

	return mergeArray;
}

/**
 * 对数组对象按某个属性进行分组
 * @param oriArray 源数组
 * @param groupKeys 分组属性keys,以数组的形式传
 * @returns {{}}
 */
function group(oriArray, groupKeys) {
	var groupArray = {}; // 分组存放数组
	var len = oriArray.length;
	for (var i = 0; i < len; i++) {
		var oriObj = oriArray[i]; // 原始对象
		var strGroupKey = ""; // 分组key值
		for (var j = 0; j < groupKeys.length; j++) {
			strGroupKey += oriObj[groupKeys[j]] + "-";
		}
		if (groupArray[strGroupKey] == undefined) {
			var list = [];
			list.push(oriObj);
			groupArray[strGroupKey] = list;
		} else {
			groupArray[strGroupKey].push(oriObj);
		}
	}
	return groupArray;
}

/**
 * 对数组进行排序
 * @param arr
 * @param attribute
 * @returns {Array}
 */
function sortFunction(arr, attribute) {
	var array = [];
	for (var objectKey in arr) {
		array.push(arr[objectKey]);
	}

	array.sort(function (a, b) {
		return a[attribute] > b[attribute] ? 1 : -1;
	});
	return array;
}

function htmlDecode(value) {
	if (value && (value === "&nbsp;" || value === "&#160;" || value.length === 1 && value.charCodeAt(0) === 160)) {
		return "";
	}
	return !value ? value : String(value).replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&quot;/g, '"').replace(/&amp;/g, "&");
}

function htmlEncode(value) {
	return !value ? value : String(value).replace(/&/g, "&amp;").replace(/\"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * 检查是否为空或者为undefined
 */
function isBlank(str) {
	if (str == undefined || trim(str) == "") {
		return true;
	}
	return false;
}

/**
 * 删除左右两端的空格
 * @param str
 * @returns
 */
function trim(str) {
	//
	return str.replace(/(^\s*)|(\s*$)/g, "");
}

/**
 * 删除左边的空格
 * @param str
 * @returns
 */
function ltrim(str) {
	//
	return str.replace(/(^\s*)/g, "");
}

/**
 * 删除右边的空格
 * @param str
 * @returns
 */
function rtrim(str) {
	//
	return str.replace(/(\s*$)/g, "");
}

/* IE兼容问题解决*/

function stopEvent(e) {
	if (!e) var e = window.event;

	// e.cancelBubble is supported by IE -
	// this will kill the bubbling process.
	e.cancelBubble = true;
	e.returnValue = false;

	// e.stopPropagation works only in Firefox.
	if (e.stopPropagation) e.stopPropagation();
	if (e.preventDefault) e.preventDefault();

	return false;
}

Array.prototype._indexOf = function (n) {
	if ("indexOf" in this) {
		return this["indexOf"](n);
	}
	for (var i = 0; i < this.length; i++) {
		if (n === this[i]) {
			return i;
		}
	}
	return -1;
};

if (!Array.prototype.indexOf) {
	Array.prototype.indexOf = function (val) {
		return jQuery.inArray(val, this);
	};
}

/* IE兼容问题解决 end*/

/**
 * 检测用户浏览器，如果是IE8以下，提示用户升级浏览器
 */
function showMessageIfLowLevelBrowser() {
	var browser = getWebBrowser();
	if (browser && browser.match("IE[5-8]{1}")) {
		showMessage("浏览器版本过低", "为了得到更好的浏览体验,请升级浏览器到IE9及以上。或者使用<a href='http://se.360.cn/' target='_blank' style='text-decoration:underline;'>360浏览器</a>，并开启极速模式后访问。", -1);
	}
}

/**
 *
 * @param httpServices
 * @param configKey 配置的名称
 * @param targetObj 配置依赖的对象
 * @param targetAttr 配置本身
 * @param defaultValue 配置的默认值
 * @param callback 设置配置成功后的回调函数
 * 					（应用于，获取配置之后还需要检查配置值是否有效的情况，
 * 					如开单设置默认客户时需要检查上次设置的那个客户是否停用或删除，
 * 					获取的配置值会当做这个函数的参数传入）
 * setConfig(httpServices,"checkout.manualAddNumber",$scope,'manualAddNumber',true)，这样可以设置$scope.manulAddNumber的配置。
 */
function setConfig(httpServices, configKey, targetObj, targetAttr, defaultValue, callback) {
	var userConfigsStr = window.localStorage.userConfigs;
	if (!userConfigsStr) {
		userConfigsStr = __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()([]);
	}
	var userConfigs = JSON.parse(userConfigsStr);
	var config = getObject(userConfigs, "configKey", configKey);
	if (config) {
		if (callback) {
			callback(JSON.parse(config.configValue));
		} else {
			targetObj[targetAttr] = JSON.parse(config.configValue);
		}
	} else if (!config) {
		httpServices.post(BASE_URL.webServer + "/admin/pubuser/getUserConfig.ac", {
			configKey: configKey
		}).success(function (result) {
			if (result.statusCode == 1) {
				if (result.object) {
					config = result.object;
					if (callback) {
						callback(JSON.parse(config.configValue));
					} else {
						targetObj[targetAttr] = JSON.parse(config.configValue);
					}
					removeByKey(userConfigs, "configKey", config.configKey);
					userConfigs.push(config);
					window.localStorage.userConfigs = __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()(userConfigs);
				} else {
					if (callback) {
						callback(defaultValue);
					} else {
						targetObj[targetAttr] = defaultValue;
					}
				}
			}
		}).error(function (data, status) {
			if (callback) {
				callback(defaultValue);
			} else {
				targetObj[targetAttr] = defaultValue;
			}
		});
	}
}
/** 设置用户配置*/
function saveConfig(httpServices, configKey, configValue, device) {
	var userConfigsStr = window.localStorage.userConfigs;
	if (!userConfigsStr) {
		userConfigsStr = __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()([]);
	}
	var userConfigs = JSON.parse(userConfigsStr);
	var config = getObject(userConfigs, "configKey", configKey);
	var exist = false;
	if (config) {
		config.configValue = __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()(configValue);
	} else {
		config = {
			configKey: configKey,
			configValue: __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()(configValue)
		};
	}
	config.device = !device ? 1 : device;
	httpServices.post(BASE_URL.webServer + "/admin/pubuser/saveOrUpdateUserConfigNew.ac", config, {}, httpServices.REMIND_SILENCE).success(function (result) {
		if (result.statusCode == 1) {
			if (result.object) {
				config = result.object;
				var localConfig = {
					userId: config.userId,
					configKey: config.configKey,
					configValue: config.configValue,
					device: config.device
				};
				removeByKey(userConfigs, "configKey", localConfig.configKey);
				userConfigs.push(localConfig);
				window.localStorage.userConfigs = __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()(userConfigs);
			}
		}
	});
}

function getCookie(name) {
	var arr,
	    reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
	if (arr = document.cookie.match(reg)) return unescape(arr[2]);else return null;
}
/** 得到所有的用户配置*/
function getAllConfig() {
	var oldJSESSIONID = window.localStorage.SID;
	var aLoginOld = window.localStorage.aLogin;

	var newJSESSIONID = getCookie("SID");
	var aLoginNew = getCookie("aLogin");
	if (!oldJSESSIONID || oldJSESSIONID !== newJSESSIONID || !aLoginOld || aLoginOld !== aLoginNew) {
		$.ajax({
			url: BASE_URL.webServer + "/admin/pubuser/getUserConfigs.ac",
			type: "POST",
			data: __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()({
				device: 1
			}),
			contentType: "application/json;charset=UTF-8",
			dataType: "json",
			success: function success(result) {
				if (result.statusCode == 1) {
					if (result.object) {
						userConfigs = result.object;
						window.localStorage.userConfigs = __WEBPACK_IMPORTED_MODULE_3_babel_runtime_core_js_json_stringify___default()(userConfigs);
					}
				}
			}
		});
		window.localStorage.SID = newJSESSIONID;
		window.localStorage.aLogin = aLoginNew;
	}
}
// getAllConfig()
/**
 * 适用于报表查询切换不同tab时判断查询条件是否发生了实质变化（查询条件多了、少了、条件值改变了等情况）
 * 检查searchParam和curSearchParam中的条件是否相同，存在不同条件就返回true，条件全都相同就返回false.
 *
 * @param {object} searchParam 前一页的查询参数
 * @param {object} curSearchParam 当前页的查询参数
 * @returns {boolean} 是否需要重新查询汇总数据
 */
function checkQueryParams(searchParam, curSearchParam) {
	var vCompareContainer = {};
	var vCurrentEmptyFlag = true;
	for (propertyName in curSearchParam) {
		// 循环curSearchParam，将当前查询条件中非空的参数值放入vCompareContainer
		if (curSearchParam[propertyName] != undefined && curSearchParam[propertyName] != "") {
			vCurrentEmptyFlag = false;
			vCompareContainer[propertyName] = curSearchParam[propertyName];
		}
	}
	// 循环从前一页的查询条件searchParam，如果vCompareContainer是空的，且自身的条件不为空，就返回true；
	// 如果vCompareContainer非空，从中取出参数值，和vCompareContainer中同名参数值比较，如果相等就从vCompareContainer中移除，不相等就返回true
	for (propertyName in searchParam) {
		if (vCurrentEmptyFlag) {
			if (searchParam[propertyName] != undefined && searchParam[propertyName] != "") {
				return true;
				// vCompareContainer[propertyName] = searchParam[propertyName];
				// break;
			}
		} else {
			if (searchParam[propertyName] != undefined && searchParam[propertyName] != "") {
				if (searchParam[propertyName] === vCompareContainer[propertyName]) {
					delete vCompareContainer[propertyName];
				} else {
					return true;
				}
			}
		}
	}
	// 循环结束后，如果vCompareContainer中还有属性，说明查询条件不相等，需要查询汇总数据，返回true
	var hasProp = false;
	for (prop in vCompareContainer) {
		hasProp = true;
		break;
	}
	return hasProp;
}

/**
 * 获取拼接在url后面的参数 getQueryString('param1')
 * @param name
 * @returns
 */
function getQueryString(name) {
	var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
	var r = window.location.search.substr(1).match(reg);
	if (r != null) return unescape(r[2]);
	return null;
}

// 兼容ie获取event的触发对象
function getEvtTarget() {
	return window.event ? event.target ? event.target : event.srcElement : null;
}

// 当某个连续触发（间隔为delay）某个执行后执行的方法
function debounce(func, wait, immediate) {
	var timeout = void 0;
	return function () {
		for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
			args[_key] = arguments[_key];
		}

		var context = this;
		if (timeout) {
			clearTimeout(timeout);
		}
		if (immediate) {
			var callNow = !timeout;
			timeout = setTimeout(function () {
				timeout = null;
			}, wait);
			if (callNow) {
				func.apply(context, args);
			}
		} else {
			timeout = setTimeout(function () {
				func.apply(context, args);
			}, wait);
		}
	};
}

function throttle(fn, delay) {
	var context = this,
	    timer = null,
	    remaining = 0,
	    previous = new Date();

	return function () {
		var now = new Date();
		var args = arguments;
		remaining = now - previous;
		if (remaining >= delay) {
			if (timer) {
				clearTimeout(timer);
			}
			fn.apply(context, args);
			previous = now;
		} else {
			if (!timer) {
				timer = setTimeout(function () {
					fn.apply(context, args);
					previous = new Date();
				}, delay - remaining);
			}
		}
	};
}

// 异步节流
function throttleForAsync(func) {
	var wait = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;
	var mustRun = arguments[2];

	var timeout = null;
	var startTime = new Date();
	return function () {
		var context = this;
		var args = arguments;
		var curTime = new Date();
		clearTimeout(timeout);
		// 如果达到了规定的触发时间间隔，触发 handler
		if (curTime - startTime >= mustRun) {
			func.apply(context, args);
			startTime = curTime;
			// 没达到触发间隔，重新设定定时器
		} else {
			timeout = setTimeout(func, wait);
		}
	};
}

/**
 * 判断是否拥有权限
 * @param {Array<string>} authority - 要判断的权限列表或字段
 */
var includeAuthority = function () {
	var _ref = __WEBPACK_IMPORTED_MODULE_2_babel_runtime_helpers_asyncToGenerator___default()( /*#__PURE__*/__WEBPACK_IMPORTED_MODULE_1_babel_runtime_regenerator___default.a.mark(function _callee() {
		var authority = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
		var authorityList, filterAuthorityList;
		return __WEBPACK_IMPORTED_MODULE_1_babel_runtime_regenerator___default.a.wrap(function _callee$(_context) {
			while (1) {
				switch (_context.prev = _context.next) {
					case 0:
						if (authority.length) {
							_context.next = 2;
							break;
						}

						return _context.abrupt('return', true);

					case 2:
						_context.t0 = !__WEBPACK_IMPORTED_MODULE_5__store__["a" /* default */].getters.userLoginInfo;

						if (!_context.t0) {
							_context.next = 6;
							break;
						}

						_context.next = 6;
						return __WEBPACK_IMPORTED_MODULE_5__store__["a" /* default */].dispatch("GetUserLoginInfo");

					case 6:
						authorityList = __WEBPACK_IMPORTED_MODULE_5__store__["a" /* default */].getters.userLoginInfo.accessResource;
						// 对现有权限进行判断

						if (Array.isArray(authority)) {
							_context.next = 9;
							break;
						}

						return _context.abrupt('return', authorityList.indexOf(authority) > -1);

					case 9:
						filterAuthorityList = authority.filter(function (item) {
							return authorityList.includes(item);
						});
						return _context.abrupt('return', filterAuthorityList.length === authority.length);

					case 11:
					case 'end':
						return _context.stop();
				}
			}
		}, _callee, this);
	}));

	return function includeAuthority() {
		return _ref.apply(this, arguments);
	};
}();

/**
 * 深拷贝
 *
 */
function deepCopy(obj) {
	var result = Array.isArray(obj) ? [] : {};
	for (var key in obj) {
		if (obj.hasOwnProperty(key)) {
			if (__WEBPACK_IMPORTED_MODULE_4_babel_runtime_helpers_typeof___default()(obj[key]) === 'object') {
				// 深拷贝日期类型
				if (obj[key] instanceof Date) {
					result[key] = new Date(obj[key].valueOf());
				} else {
					result[key] = deepCopy(obj[key]); // 递归复制
				}
			} else {
				result[key] = obj[key];
			}
		}
	}
	return result;
}

// 自定义深拷贝，由于考虑到 obj[key]== null 的情况，故重写了一个
function deepCopyPlus(obj) {
	var result = Array.isArray(obj) ? [] : {};
	for (var key in obj) {
		if (obj.hasOwnProperty(key)) {
			if (obj[key] === null) {
				result[key] = null;
			} else if (__WEBPACK_IMPORTED_MODULE_4_babel_runtime_helpers_typeof___default()(obj[key]) === "object") {
				// 深拷贝日期类型
				if (obj[key] instanceof Date) {
					result[key] = new Date(obj[key].valueOf());
				} else {
					result[key] = deepCopyPlus(obj[key]); // 递归复制
				}
			} else {
				result[key] = obj[key];
			}
		}
	}
	return result;
}
// 移除数组里key值为value的元素
function removeListForValue(list, key, value) {
	var arr = [];
	if (list && list.length > 0) {
		arr = deepCopyPlus(list);
	}
	var batchEnableIndex = arr.findIndex(function (item) {
		return item[key] === value;
	});
	batchEnableIndex !== -1 && arr.splice(batchEnableIndex, 1);
	return arr;
}
// 判断数字类型  NaN === 'number' 为true  要判断不是NaN
function isNumberType(n) {
	return typeof n === 'number' && !isNaN(n);
}

function isNumber(n) {
	return typeof n === 'number' || n && !isNaN(n);
}

/**
 * 上传图片文件的时候获取图片文件的宽高
 * @params 文件数据
 */
function getImageSizeFromFileData(file) {
	return new __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_promise___default.a(function (resolve, reject) {
		var reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = function (e) {
			var image = new Image();
			image.onload = function () {
				var width = this.width;
				var height = this.height;
				resolve({ width: width, height: height });
			};
			image.src = e.target.result;
		};
	});
}

/**
* 版本比较函数
*/
function compareVersion(v1, v2) {
	v1 = v1.replace('vgis.', '').replace('vis.', '').split('.');
	v2 = v2.replace('vgis.', '').replace('vis.', '').split('.');
	var len = Math.max(v1.length, v2.length);
	while (v1.length < len) {
		v1.push('0');
	}
	while (v2.length < len) {
		v2.push('0');
	}
	for (var i = 0; i < len; i++) {
		var num1 = parseInt(v1[i]);
		var num2 = parseInt(v2[i]);
		if (num1 > num2) {
			return 1;
		} else if (num1 < num2) {
			return -1;
		}
	}
	return 0;
}

/**
 * @description 对象数据的二分查找
 * @param {Array} arr 数据数组
 * @param {Number} left 左索引
 * @param {Number} right 右索引
 * @param {String} key 数据项的key
 * @param {Number} value 目标value
 */
function binarySearch(arr, left, right, key, value) {
	if (left > right || arr.length === 0) return null;
	var mid = left + right >> 1;
	if (arr[mid][key] === value) {
		return arr[mid];
	} else if (arr[mid][key] > value) {
		return binarySearch(arr, left, mid - 1, key, value);
	} else {
		return binarySearch(arr, mid + 1, right, key, value);
	}
}

//获取uuid
function getUUID(key) {
	//设置uuid
	var generateUUID = function generateUUID(len, radix) {
		var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
		var uuid = [],
		    i;
		radix = radix || chars.length;
		if (len) {
			for (i = 0; i < len; i++) {
				uuid[i] = chars[0 | Math.random() * radix];
			}
		} else {
			var r;
			uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
			uuid[14] = '4';
			for (i = 0; i < 36; i++) {
				if (!uuid[i]) {
					r = 0 | Math.random() * 16;
					uuid[i] = chars[i == 19 ? r & 0x3 | 0x8 : r];
				}
			}
		}
		return uuid.join('');
	};
	var uuid = null;
	var key = key || 'pmTrackUUID';
	if (window.sessionStorage) {
		uuid = window.sessionStorage.getItem(key);
		if (!uuid || uuid && uuid == '') {
			uuid = generateUUID(16, 16);
			window.sessionStorage.setItem(key, uuid);
		}
	} else {
		uuid = generateUUID(16, 16);
		window.sessionStorage.setItem(key, uuid);
	}
	return uuid;
}

// 获取网络类型
function getNetworkType() {
	var ua = navigator.userAgent;
	var networkStr = ua.match(/NetType\/\w+/) ? ua.match(/NetType\/\w+/)[0] : 'NetType/other';
	networkStr = networkStr.toLowerCase().replace('nettype/', '');
	var networkType;
	switch (networkStr) {
		case 'wifi':
			networkType = 'wifi';
			break;
		case '4g':
			networkType = '4g';
			break;
		case '3g':
		case '3gnet':
			networkType = '3g';
			break;
		case '2g':
			networkType = '2g';
			break;
		default:
			networkType = 'other';
	}
	return networkType;
}
// 检查文本是否包含表情
function includeEmoji(content) {
	var patt = /[\ud800-\udbff][\udc00-\udfff]/g; // 检测utf16字符正则
	return patt.test(content);
}
// 检查文本是否纯数字
function isPureNum(content) {
	var patt = /^[0-9]*$/g; // 检测纯数字
	return patt.test(content);
}
/*
 * 处理图片压缩
 * 参数 imgurl 图片地址， w 压缩到的宽， h压缩到的高，
 * alias: 别名
 * 输出能够压缩图片的链接
 */
function dealWithPic(imgurl, alias, w, h) {
	w = w || 100;
	h = h || 100;
	// 已经使用了别名的图片
	if (imgurl && imgurl.split('.')[1] && imgurl.split('.')[1].indexOf('@!') > -1) {
		return imgurl;
	}
	if (imgurl && imgurl.indexOf('.gif') > -1) {
		// auto-orient 会使gif动效失效，所以gif不进行图片处理
		return imgurl;
	}
	// 使用别名的规则进行压缩图片
	if (imgurl && imgurl.indexOf('qinsilk.com') > -1 && alias) {
		if (imgurl.indexOf('?') == -1) {
			return imgurl + '@!' + alias;
		} else {
			return imgurl;
		}
	}
	if (imgurl && imgurl.indexOf('qinsilk.com') > -1) {
		if (imgurl.indexOf('?') > -1) {
			var lastChar = imgurl.charAt(imgurl.length - 1);
			lastChar == '&' || lastChar == '?' || (imgurl += '&');
		} else {
			imgurl += '?';
		}
		return imgurl + 'x-oss-process=image/auto-orient,1/resize,m_lfit,h_' + h + ',w_' + w + '/quality,q_100';
	} else {
		return imgurl;
	}
}

function getOrderTypeBySn(ordersSn) {
	if (ordersSn) {
		//查看详细 JH:采购单、JT:采购退货、PF:销售单、TH:销售退货、LS:零售、PB:盘点、DP:调拨
		if (ordersSn.indexOf('CG') >= 0) {
			return "采购单";
		} else if (ordersSn.indexOf('CT') >= 0) {
			return "采购退货单";
		} else if (ordersSn.indexOf('XS') >= 0) {
			return "销售单";
		} else if (ordersSn.indexOf('XT') >= 0) {
			return "销售退货单";
		} else if (ordersSn.indexOf('LS') >= 0) {
			return "零售单";
		} else if (ordersSn.indexOf('PD') >= 0) {
			return "库存盘点单";
		} else if (ordersSn.indexOf('DB') >= 0) {
			return "库存调拨单";
		} else if (ordersSn.indexOf('SK') >= 0) {
			return "收款单";
		} else if (ordersSn.indexOf('FK') >= 0) {
			return "付款单";
		} else if (ordersSn.indexOf('JZ') >= 0) {
			return "记账单";
		} else if (ordersSn.indexOf('CX') >= 0) {
			return "拆卸单";
		} else if (ordersSn.indexOf('ZZ') >= 0) {
			return "组装单";
		} else if (ordersSn.indexOf('RK') >= 0) {
			return "入库单";
		} else if (ordersSn.indexOf('CK') >= 0) {
			return "出库单";
		}
	}

	return '其它';
}

// 转换为中文金额，str参数表示要转换的数值，isShowNegative表示 是否显示负值，1表示显示，0表示不显示
function number_chinese(str, isShowNegative) {
	// 判断数值为空和零的情况
	if (str === "" || str === null || parseFloat(str) === 0) {
		return "零";
	}
	if (parseFloat(str) < 0) {
		if (isShowNegative === 1) {
			return "负" + number_chinese(-1 * str);
		} else {
			str = -str;
		}
	}
	// 用 parseFloat 进行转换 可以去除首位的0
	var num = parseFloat(str) + "";
	var strOutput = "";
	var strUnit = '仟佰拾亿仟佰拾万仟佰拾元角分厘';
	// 确定小数点的位置 存在小数点 则去除小数点
	var intPos = num.indexOf('.');
	if (intPos >= 0) {
		// 这里需要注意的是 小数位只取了3位 因为钱的最小单位是厘 如果小数位不足3位 则需要进行补齐
		var decStr = num.substr(intPos + 1, 3);
		while (decStr.length < 3) {
			decStr += "0";
		}
		num = num.substring(0, intPos) + decStr;
	} else {
		// 如果没有小数点 则需要手动补齐小数位
		num += "000";
	}
	// 根据数据的长度确认最高使用的单位是哪个
	strUnit = strUnit.substr(strUnit.length - num.length);
	// 循环取出单个数字 转成大写 并匹配上对应位置的单位
	for (var i = 0; i < num.length; i++) {
		strOutput += '零壹贰叁肆伍陆柒捌玖'.substr(num.substr(i, 1), 1) + strUnit.substr(i, 1);
	}
	// 兼容小数位为 0 的情况
	strOutput = strOutput.replace(/(零角零分零厘|零分零厘|零厘)$/, '整');
	// 处理整数部分
	// 去除 零仟 零佰 零拾 替换成 零
	strOutput = strOutput.replace(/零[仟佰拾]/g, '零');
	// 去除之后 可能出现多个零的情况 需要将多个零替换成单个
	strOutput = strOutput.replace(/零{2,}/g, '零');
	// 去除 零亿 零万 直接使用 亿 万替代
	strOutput = strOutput.replace(/零([亿|万])/g, '$1');
	// 去除零元 替换成元
	strOutput = strOutput.replace(/零+元/, '元');
	// 去除特殊 万为零的情况
	strOutput = strOutput.replace(/亿零{0,3}万/, '亿');
	// 如果开头为壹拾万 或者 壹拾亿 直接去除壹
	strOutput = strOutput.replace(/^壹拾万/, '拾万');
	strOutput = strOutput.replace(/^壹拾亿/, '拾亿');

	// 处理整数部分为0的情况
	strOutput = strOutput.replace(/^元/, "零元");
	return strOutput;
}

// 保质期转换
function shelfLife(goods) {
	var shelfLife = goods.shelfLife;
	var shelfLifeType = goods.shelfLifeType;
	var shelfLifeDays = '';
	if (shelfLifeType == 1 && shelfLife) {
		shelfLifeDays = shelfLife + "小时";
	} else if (shelfLifeType == 2 && shelfLife) {
		shelfLifeDays = shelfLife / 24 + "天";
	} else if (shelfLifeType == 3 && shelfLife) {
		shelfLifeDays = shelfLife / 24 / 30 + "月";
	} else if (shelfLifeType == 4 && shelfLife) {
		shelfLifeDays = shelfLife / 24 / 365 + "年";
	}
	return shelfLifeDays;
}
/**
 * 截取数字（保留decimal位小数，且不能为负数）
 * @param number 原数字
 * @param defaultVal 默认值
 * @param decimal 小数位
 */
function getValidNum(num, defaultVal, decimal) {
	decimal = decimal > 0 ? decimal : 2;
	var re = '/([0-9]+\\.[0-9]{' + decimal + '})[0-9]*/';
	if (num || num === 0) {
		return Math.abs(parseFloat(('' + parseFloat(num)).replace(eval(re), '$1')));
	} else {
		if (defaultVal || defaultVal === 0 || defaultVal === '') {
			return defaultVal;
		} else {
			var zero = 0;
			return zero.toFixed(decimal);
		}
	}
}

/*js判断是否ean码函数*/
function isEanBarcode(barcode) {
	if (!barcode) {
		return false;
	}
	if (barcode.length == 8) {
		barcode = '00000' + barcode; //ean-8码计算校验码前边加“00000”
	}
	var c1 = 0;
	var c2 = 0;
	for (var i = 0; i < barcode.length - 1; i += 2) {
		var c = barcode.substring(i, i + 1); //字符串code中第i个位置上的字符
		c1 += parseInt(c); //累加奇数位的数字和
	}
	for (var i = 1; i < barcode.length - 1; i += 2) {
		var c = barcode.substring(i, i + 1); //字符串code中第i个位置上的字符
		c2 += parseInt(c); //累加偶数位的数字和
	}
	var cc = c1 + c2 * 3;
	var check = cc % 10;
	check = (10 - cc % 10) % 10;
	var lastCode = parseInt(barcode.substring(barcode.length - 1, barcode.length));
	return lastCode == check;
}

function validateGBCode(str) {
	if (!str) return false;
	return str.startsWith('69');
}
/* WEBPACK VAR INJECTION */}.call(__webpack_exports__, __webpack_require__("7t+N"), __webpack_require__("7t+N")))

/***/ }),

/***/ "YaEn":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";

// EXTERNAL MODULE: ./node_modules/vue/dist/vue.esm.js
var vue_esm = __webpack_require__("7+uW");

// EXTERNAL MODULE: ./node_modules/vue-router/dist/vue-router.esm.js
var vue_router_esm = __webpack_require__("/ocq");

// EXTERNAL MODULE: ./node_modules/babel-runtime/helpers/extends.js
var helpers_extends = __webpack_require__("Dd8w");
var extends_default = /*#__PURE__*/__webpack_require__.n(helpers_extends);

// EXTERNAL MODULE: ./node_modules/vuex/dist/vuex.esm.js
var vuex_esm = __webpack_require__("NYxO");

// EXTERNAL MODULE: ./src/service/common.js
var common = __webpack_require__("7S6e");

// CONCATENATED MODULE: ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib/selector.js?type=script&index=0!./src/views/layout/components/Navbar.vue

//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//





/* harmony default export */ var Navbar = ({
	props: {
		currRoute: {
			type: Object,
			default: function _default() {
				return {};
			}
		}
	},
	data: function data() {
		return {
			unReadImMsgCount: 0,
			unReadInnerMsgCount: 0,
			isActivetHome: false,
			isHiddenHoverClass: false,
			showExtraIcon1: false,
			showExtraIcon: false,
			showExtraIconData: [],
			extraIcon1Ref: "",
			extraIcon1Img: "",
			showExtraIcon2: false,
			extraIcon2Ref: "",
			extraIcon2Img: "",
			valueAddedServiceURL: BASE_URL.mgrWebServer + "/paymentservice/paymentServicesList.ac",
			dialogVisible: false,
			currentRule: {},
			isShowVipPromptBtn: false,
			isNearExprid: false,
			currentUrl: '',
			isShowVipTipsMessage: false,
			// 判断销货宝是否开启
			isWeChatShopOpen: false
		};
	},

	computed: extends_default()({}, Object(vuex_esm["c" /* mapGetters */])(["menuList", "userLoginInfo", "companyInfo", "certificationInfo"]), {
		logoImg: function logoImg() {
			var res = void 0;
			if (this.companyInfo instanceof Object) {
				res = this.companyInfo.logo;
			}
			return res || "./static/resource/images/photo-flower.jpg";
		},

		// 是否展示系统参数菜单的小红点, 没有设置行业属性则显示
		isShowSystemConfigBadge: function isShowSystemConfigBadge() {
			return !(this.certificationInfo && this.certificationInfo.merchantVO && this.certificationInfo.merchantVO.industryAttributeId);
		}
	}),
	created: function created() {
		var _this2 = this;

		if (this.menuList == null) {
			this.getUserMenuList();
		}
		if (this.userLoginInfo == null) {
			this.getUserLoginInfo();
		}
		if (this.companyInfo == null) {
			this.getCompanyInfo();
		}
		Object(common["w" /* getUnreadMsgCount */])().then(function (response) {
			_this2.unReadInnerMsgCount = response;
		});
		// 获取增值服务跳转链接
		Object(common["C" /* getValueAddedServiceURL */])().then(function (response) {
			if (response) {
				_this2.valueAddedServiceURL = response.gisurl;
			}
		});
		this.openNavActivity();
		// 在IE浏览器打开进行点击导航跳转，使用手动的push跳转
		if (this.checkIE()) {
			this.hashchange();
		}
		this.queryProfessionalEnableTime();
		// 判断销货宝是否开启
		this.getAppShopOpenInfo();
	},

	watch: {
		$route: {
			handler: function handler(val) {
				var store = this.$store;
				var _this = this;
				this.dialogVisible = false;
				var to = val;
				if (store.state.user && store.state.user.actionAccessRuleList && store.state.user.actionAccessRuleList.length !== 0) {
					this.showMenuAccToast(to.meta.title);
				} else {
					store.watch(function (state) {
						return state.user.actionAccessRuleList;
					}, function () {
						return _this.showMenuAccToast(to.meta.title);
					});
				}
			},
			immediate: true
		}
	},
	methods: {
		// 获取是否开通 vip
		queryProfessionalEnableTime: function queryProfessionalEnableTime() {
			var _this3 = this;

			Object(common["F" /* queryProfessionalEnableTime */])().then(function (result) {
				if (result && result.statusCode === 1 && result.object) {
					// 高级版到期时间
					var advancedEnableEnd = result.object.advancedEnableEnd || "";
					// 试用到期时间
					var probationalEnableEnd = result.object.probationalEnableEnd || "";
					// 专业版到期时间
					var professionalEnableEnd = result.object.professionalEnableEnd || "";

					// 当前时间
					var newTime = new Date().getTime();
					// 高级版到期时间 > 当前时间 || 专业版试用到期时间 > 当前时间 || 专业版到期时间 > 当前时间 代表非免费版
					if (advancedEnableEnd && parseInt(advancedEnableEnd) >= newTime || probationalEnableEnd && parseInt(probationalEnableEnd) >= newTime || professionalEnableEnd && parseInt(professionalEnableEnd) >= newTime) {
						_this3.isShowVipTipsMessage = false;
					} else {
						_this3.isShowVipTipsMessage = true;
					}
				} else {
					_this3.isShowVipTipsMessage = false;
				}
			});
		},
		openVipIntroducePage: function openVipIntroducePage() {
			window.open("https://cdn.qinsilk.com/res/business/activity/mobileDailyActivities/activityPage.html?dc=1640161249767&name=fedfec559da34f3f8efc931a05c6f541", "_blank ");
		},
		showMenuAccToast: function showMenuAccToast(name) {
			// 判断是否是需要判断权限的列表 true 为不需要或者有权限的 false 为无权限的
			this.rootName = name;
			var has = this.$vip.menuRouterVaServiceResource(name);
			this.currentRule = this.$vip.menuRouterVaServiceResource(name, '1');
			var includeFeature = ['物流设置', '商品分类'];
			if (!has) {
				this.dialogVisible = true;
				// 开通销货宝允许开放物流设置、商品分类功能
				if (this.isWeChatShopOpen && includeFeature.includes(name)) {
					this.dialogVisible = false;
				}
			} else {
				var _currentRule = this.currentRule,
				    _has = _currentRule.has,
				    tipsMessage = _currentRule.tipsMessage;
				// 是否临期

				var popTime = window.localStorage.mainVipTipsPopTime || 0;
				var newTime = new Date().getTime();
				if (popTime) {
					popTime = parseInt(popTime);
				}
				// 存在权限 && 存在提示语
				var isShowVipPromptBtn = window.localStorage.isShowVipPromptBtn;
				isShowVipPromptBtn = isShowVipPromptBtn && isShowVipPromptBtn === 'true';
				if (_has && tipsMessage && (!isShowVipPromptBtn || isShowVipPromptBtn && newTime - popTime > 3 * 60 * 60 * 1000)) {
					this.isNearExprid = true;
					this.dialogVisible = true;
				}
			}
		},
		getAppShopOpenInfo: function getAppShopOpenInfo() {
			var _this4 = this;

			common["o" /* getOwnAppIds */]().then(function (response) {
				if (response.includes(2)) {
					_this4.isWeChatShopOpen = true;
				}
			});
		},
		continueUse: function continueUse(type) {
			if (type === 'dump') {
				window.open(this.currentUrl, '_self');
			}
			this.dialogVisible = false;
		},
		dialogClose: function dialogClose() {
			this.dialogVisible = false;
			if (!this.currentRule.has) {
				history.back();
			}
		},
		hrefToMenu: function hrefToMenu(url, id, name) {
			this.hiddenHoverClass();
			this.currentUrl = this.getMenuUrl(url, id);
			var popTime = window.localStorage.mainVipTipsPopTime || 0;
			var newTime = new Date().getTime();
			if (popTime) {
				popTime = parseInt(popTime);
			}
			// 存在权限 && 存在提示语
			this.currentRule = this.$vip.menuRouterVaServiceResource(name, '1');
			var isShowVipPromptBtn = window.localStorage.isShowVipPromptBtn;
			isShowVipPromptBtn = isShowVipPromptBtn && isShowVipPromptBtn === 'true';
			if (this.currentRule.has && this.currentRule.tipsMessage && (!isShowVipPromptBtn || isShowVipPromptBtn && newTime - popTime > 3 * 60 * 60 * 1000)) {
				this.isNearExprid = true;
				this.dialogVisible = true;
			} else {
				this.continueUse('dump');
			}
		},
		checkedVipPromptBtn: function checkedVipPromptBtn() {
			this.isShowVipPromptBtn = !this.isShowVipPromptBtn;
			window.localStorage.mainVipTipsPopTime = String(new Date().getTime());
			window.localStorage.isShowVipPromptBtn = this.isShowVipPromptBtn ? "true" : "false";
		},
		goToBuyVip: function goToBuyVip() {
			if (this.isNearExprid) {
				this.dialogVisible = false;
			}
			window.open(this.currentRule.recommendPaymentPcUrl || "https://activity.qinsilk.com/res/business/activity/mobileDailyActivities/activityPage.html?dc=1638440463586&name=c731950e4d324cfe9b9bc3108157b406", "_blank");
		},
		noAccToast: function noAccToast(name) {
			this.isHiddenHoverClass = true;
			var rule = this.$vip.menuRouterVaServiceResource(name, '1');
			this.currentRule = rule;
			this.isNearExprid = false;
			this.dialogVisible = true;
		},
		getMenuAcc: function getMenuAcc(name) {
			return this.$vip.menuRouterVaServiceResource(name);
		},
		checkIE: function checkIE() {
			return '-ms-scroll-limit' in document.documentElement.style && '-ms-ime-align' in document.documentElement.style;
		},
		hashchange: function hashchange() {
			var _this5 = this;

			window.addEventListener('hashchange', function () {
				var currentPath = window.location.hash.slice(1).split("?").shift();
				if (_this5.$route.path !== currentPath) {
					_this5.$router.push(currentPath);
				}
			}, false);
		},
		mouseoverMenu: function mouseoverMenu() {
			// 鼠标进入顶部菜单时初始化，使hover生效
			this.isHiddenHoverClass = false;
		},
		hiddenHoverClass: function hiddenHoverClass() {
			// 利用!important使伪类hover失效
			this.isHiddenHoverClass = true;
		},

		// 获得北京时间
		datePrototypeGetBJDate: function datePrototypeGetBJDate() {
			// 获得当前运行环境时间
			var d = new Date();
			var currentDate = new Date();
			var tmpHours = currentDate.getHours();
			// 算得时区
			var time_zone = -d.getTimezoneOffset() / 60;
			// 少于0的是西区 西区应该用时区绝对值加京八区 重新设置时间（西区时间比东区时间早 所以加时区间隔）
			if (time_zone < 0) {
				time_zone = Math.abs(time_zone) + 8;
				currentDate.setHours(tmpHours + time_zone);
			} else {
				// 大于0的是东区  东区时间直接跟京八区相减
				time_zone -= 8;
				currentDate.setHours(tmpHours - time_zone);
			}
			return currentDate;
		},

		// 千人千面上报已被点击
		updateOptActivitySiteRead: function updateOptActivitySiteRead(site, optId) {
			if (!optId) return;
			Object(common["x" /* getUpdateOptActivitySiteRead */])(site, optId).then(function (response) {
				if (response.statusCode === 1) {
					console.log(response.content || '记录信息成功');
				} else {
					console.log(response.content || '记录信息失败');
				}
			});
		},

		// 处理导航栏活动图标点击
		handleExtraIconClick: function handleExtraIconClick() {
			// 点击跳转， 记录已经浏览， 埋点
			this.updateOptActivitySiteRead(17, this.showExtraIconData.id);
			// 点击后埋点
			Object(common["H" /* saveLog */])('pc_nav_activity_id_click', { log: this.showExtraIconData.optActivityPlanId });
			window.open(this.showExtraIconData.jumpLink);
		},
		openNavActivity: function openNavActivity() {
			var _this6 = this;

			/**
    * 动态加载有上角活动图标
    */
			Object(common["n" /* getOpenNavActivityData */])().then(function (result) {
				if (result.statusCode === 1 && result.object && result.object.length) {
					_this6.showExtraIcon = true;
					_this6.showExtraIconData = result.object[0];
					// 曝光埋点
					Object(common["H" /* saveLog */])('pc_nav_activity_id_pv', { log: _this6.showExtraIconData.optActivityPlanId });
				} else {
					console.log('动态加载有上角活动图标失败！');
				}
			});
		},
		getUserMenuList: function getUserMenuList() {
			this.$store.dispatch("GetUserMenuList");
		},
		getUserLoginInfo: function getUserLoginInfo() {
			this.$store.dispatch("GetUserLoginInfo");
		},
		getCompanyInfo: function getCompanyInfo() {
			this.$store.dispatch("GetCompanyConfigJsonOnlyOnce");
		},

		// 首页跳转
		goMain: function goMain() {
			window.location.href = BASE_URL.webServer + "/admin/main.ac";
		},

		// 退出
		logout: function logout(url) {
			if (location.hostname == "ex.qinsilk.com") {
				window.location.href = BASE_URL.webServer + "/admin/loginOut.ac";
			} else {
				window.location.href = BASE_URL.webServer + url;
			}
		},

		// 链接特殊处理
		getMenuUrl: function getMenuUrl(url, firstItemId) {
			// 完整路径的直接返回，不需要拼接
			var isFullPath = url && (url.startsWith('http://') || url.startsWith('https://'));
			// 如果链接中帮助文档直接跳转
			if (url && (url.indexOf('http://www.qinsilk.com/mms/') != -1 || url.indexOf('https://www.qinsilk.com/mms/') != -1) || isFullPath) {
				return url;
			}
			// 如果链接中已经带了参数，则不进行拼接一级菜单的id
			if (url && url.indexOf('?') === -1) {
				url = url + '?mid=' + firstItemId;
			}
			var base = BASE_URL.webServer;
			if (url && this.stringStartWith(url, "/admin/ecommerce/")) {
				base = BASE_URL.esService;
			} else if (url && this.stringStartWith(url, "/paymentservice/")) {
				base = BASE_URL.mgrWebServer;
			}
			return base + url;
		},
		stringStartWith: function stringStartWith(str, start) {
			var reg = new RegExp("^" + start);
			return reg.test(str);
		},

		// 判断是否当前模块选中
		isCurrSelected: function isCurrSelected(firstItem) {
			if (this.$route.query.mid === "SPA" || this.$route.query.mid === undefined) {
				if (this.$route.name !== "home") {
					this.isActivetHome = false;
					return this.currRoute.iconNav === firstItem.pTableVO.cssClass;
				}
				this.isActivetHome = true;
			} else {
				this.isActivetHome = false;
				return parseInt(this.$route.query.mid) === firstItem.pTableVO.id;
			}
		},
		toMyInfo: function toMyInfo() {
			this.$router.push({ name: "personalInfo" });
		}
	}
});
// CONCATENATED MODULE: ./node_modules/vue-loader/lib/template-compiler?{"id":"data-v-2b19e5ca","hasScoped":true,"transformToRequire":{"video":["src","poster"],"source":"src","img":"src","image":"xlink:href"},"buble":{"transforms":{}}}!./node_modules/vue-loader/lib/selector.js?type=template&index=0!./src/views/layout/components/Navbar.vue
var render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"nav-bar-container clearfix"},[_c('a',{staticClass:"nav-logo fl",attrs:{"href":"//www.qinsilk.com","target":"_blank","title":"秦丝官网"}}),_vm._v(" "),_c('ul',{staticClass:"nav-menu-wrap fl clearfix",on:{"mouseover":_vm.mouseoverMenu}},[_c('a',{staticClass:"nav-menu-first fl",attrs:{"href":_vm.BASE_URL.webServer + '/admin/main.ac'},on:{"click":_vm.goMain}},[_c('div',{staticClass:"nav-menu-item",class:{'active':_vm.isActivetHome}},[_c('i',{staticClass:"nav-menu-icon icon-home"}),_vm._v(" "),_c('span',{staticClass:"nav-menu-text f16"},[_vm._v("首页")])])]),_vm._v(" "),_vm._l((_vm.menuList),function(firstItem){return _c('li',{key:firstItem.pTableVO.id,staticClass:"nav-menu-first fl pr"},[_c('div',{staticClass:"nav-menu-item",class:{'active':_vm.isCurrSelected(firstItem)}},[_c('i',{staticClass:"nav-menu-icon",class:firstItem.pTableVO.cssClass}),_vm._v(" "),_c('span',{staticClass:"nav-menu-text f16"},[_vm._v("\n\t\t\t\t\t\t"+_vm._s(firstItem.pTableVO.name)+"\n\t\t\t\t\t")])]),_vm._v(" "),_c('div',{class:['nav-menu-second', 'pa', 'clearfix', {'display-none': _vm.isHiddenHoverClass}]},[_c('div',{staticClass:"nav-menu-second-bg"}),_vm._v(" "),_vm._l((firstItem.lstSubHierarchyVO),function(secondItem){return _c('div',{key:secondItem.pTableVO.id,staticClass:"nav-menu-second-item fl"},[_c('div',{staticClass:"nav-menu-third-title f16",domProps:{"textContent":_vm._s(secondItem.pTableVO.name)}}),_vm._v(" "),_vm._l((secondItem.lstSubHierarchyVO),function(thirdItem){return _c('div',{key:thirdItem.pTableVO.id,staticClass:"nav-menu-third-item"},[_c('span',[_c('a',{staticClass:"f16 pr",attrs:{"href":_vm.getMenuUrl(thirdItem.pTableVO.url, firstItem.pTableVO.id),"target":thirdItem.pTableVO.showType},on:{"click":_vm.hiddenHoverClass}},[_vm._v("\n\t\t\t\t\t\t\t\t\t"+_vm._s(thirdItem.pTableVO.name)+"\n\t\t\t\t\t\t\t\t\t"),(_vm.isShowSystemConfigBadge && thirdItem.pTableVO.name === '系统参数')?_c('sup',{staticClass:"dot-badge"}):_vm._e()])]),_vm._v(" "),(false)?_c('span',{staticClass:"sub-menu-tip"},[_vm._v("new")]):_vm._e(),_vm._v(" "),(!_vm.getMenuAcc(thirdItem.pTableVO.name))?_c('img',{staticStyle:{"height":"18px"},attrs:{"src":_vm.$vip.menuVipIcon(thirdItem.pTableVO.name)}}):_vm._e()])})],2)})],2)])})],2),_vm._v(" "),_c('ul',{staticClass:"nav-right-wrap fr clearfix",on:{"mouseover":_vm.mouseoverMenu}},[(_vm.showExtraIcon)?_c('li',{staticClass:"nav-activity fl w120",on:{"click":_vm.handleExtraIconClick}},[_c('img',{staticClass:"nav-activity_pic w",attrs:{"src":_vm.showExtraIconData.phoneUrl}})]):_vm._e(),_vm._v(" "),_c('a',{attrs:{"href":_vm.valueAddedServiceURL,"target":"_blank"}},[_c('li',{staticClass:"nav-pay-service fl"})]),_vm._v(" "),_c('li',{staticClass:"nav-message fl nav-menu-first pr"},[(_vm.unReadInnerMsgCount || _vm.unReadImMsgCount)?_c('span',{staticClass:"nav-message-num",staticStyle:{"line-height":"1.1"},domProps:{"textContent":_vm._s(_vm.unReadInnerMsgCount + _vm.unReadImMsgCount)}}):_vm._e(),_vm._v(" "),_c('div',{class:['nav-menu-second', 'pa', {'display-none': _vm.isHiddenHoverClass}]},[_c('div',{staticClass:"nav-menu-second-bg"}),_vm._v(" "),_c('dl',{staticClass:"nav-menu-second-item"},[_c('dd',{staticClass:"nav-menu-third-item"},[_c('a',{staticClass:"f16",attrs:{"href":_vm.BASE_URL.webServer + '/admin/system/message/messageMap.ac'}},[_vm._v("系统消息")]),_vm._v(" "),(_vm.unReadInnerMsgCount)?_c('sup',{staticClass:"msg-sup-tips",domProps:{"textContent":_vm._s(_vm.unReadInnerMsgCount)}}):_vm._e()]),_vm._v(" "),_c('dd',{staticClass:"nav-menu-third-item",on:{"click":function($event){_vm.goAccountPage()}}},[_c('a',{staticClass:"f16",attrs:{"href":((_vm.BASE_URL.webServer) + "/static/view#/onlineStore/gsm/shopConfiguration/openTimWorkstation"),"target":"_blank"},on:{"click":_vm.hiddenHoverClass}},[_vm._v("客服消息")]),_vm._v(" "),(_vm.unReadImMsgCount)?_c('sup',{staticClass:"msg-sup-tips",domProps:{"textContent":_vm._s(_vm.unReadImMsgCount)}}):_vm._e()])])])]),_vm._v(" "),_c('li',{staticClass:"nav-mine-info-wrap fl nav-menu-first pr"},[_c('a',{attrs:{"href":((_vm.BASE_URL.webServer) + "/static/view#/setting/system/systemConfig?mid=SPA")}},[_c('div',{staticClass:"nav-mine-info ellipsis"},[_c('img',{staticClass:"nav-mine-img",attrs:{"src":_vm.logoImg}}),_vm._v(" "),_c('div',{staticClass:"name-box"},[_c('span',{staticClass:"realname-box",domProps:{"textContent":_vm._s(_vm.userLoginInfo && _vm.userLoginInfo.userVO ? _vm.userLoginInfo.userVO.realName : '')}}),_vm._v(" "),(_vm.isShowVipTipsMessage)?_c('div',{staticClass:"vip-box"},[_vm._v("免费版")]):_vm._e()])])]),_vm._v(" "),_c('div',{staticClass:"nav-menu-second pa"},[_c('div',{staticClass:"nav-menu-second-bg"}),_vm._v(" "),(_vm.isShowVipTipsMessage)?_c('div',{staticClass:"vip-tips-message",on:{"click":function($event){_vm.openVipIntroducePage()}}},[_vm._v("升级到专业版")]):_vm._e(),_vm._v(" "),_c('dl',{staticClass:"nav-menu-second-item"},[_c('dd',{staticClass:"nav-menu-third-item"},[_c('a',{staticClass:"f16",on:{"click":_vm.toMyInfo}},[_vm._v("个人信息")])]),_vm._v(" "),_c('dd',{staticClass:"nav-menu-third-item",on:{"click":function($event){_vm.goAccountPage()}}},[_c('a',{staticClass:"f16",attrs:{"href":((_vm.BASE_URL.mgrWebServer) + "/account/account.ac")}},[_vm._v("秦丝账户")])]),_vm._v(" "),_c('dd',{staticClass:"nav-menu-third-item f16",on:{"click":function($event){_vm.logout('/admin/loginOut.ac')}}},[_vm._v("退出")])])])])]),_vm._v(" "),_c('el-dialog',{staticStyle:{"margin-top":"25vh"},attrs:{"title":"提示","visible":_vm.dialogVisible,"close-on-click-modal":_vm.currentRule.has,"close-on-press-escape":_vm.currentRule.has,"before-close":_vm.dialogClose,"width":"30%"},on:{"update:visible":function($event){_vm.dialogVisible=$event}}},[_c('div',{staticClass:"dialog-bodyer",domProps:{"innerHTML":_vm._s(_vm.currentRule.tipsMessage)}}),_vm._v(" "),(_vm.isNearExprid)?_c('div',{staticStyle:{"display":"flex","align-items":"center","height":"30px"},on:{"click":function($event){_vm.checkedVipPromptBtn()}}},[(!_vm.isShowVipPromptBtn)?_c('div',{staticClass:"lb-main-vip-pop-box-redio-nochecked"}):_vm._e(),_vm._v(" "),(_vm.isShowVipPromptBtn)?_c('div',{staticClass:"lb-main-vip-pop-box-redio-checked"},[_vm._v("√")]):_vm._e(),_vm._v(" "),_c('div',[_vm._v("近期不再提示")])]):_vm._e(),_vm._v(" "),_c('span',{staticClass:"dialog-footer",attrs:{"slot":"footer"},slot:"footer"},[(!_vm.currentRule.has)?_c('el-button',{on:{"click":_vm.dialogClose}},[_vm._v("关闭")]):_vm._e(),_vm._v(" "),(_vm.currentRule.has)?_c('el-button',{on:{"click":function($event){_vm.continueUse()}}},[_vm._v("继续使用")]):_vm._e(),_vm._v(" "),_c('el-button',{attrs:{"type":"primary"},on:{"click":function($event){_vm.goToBuyVip()}}},[_vm._v("前往"+_vm._s(_vm.isNearExprid ? '续期' : '了解'))])],1)])],1)}
var staticRenderFns = []
var esExports = { render: render, staticRenderFns: staticRenderFns }
/* harmony default export */ var components_Navbar = (esExports);
// CONCATENATED MODULE: ./src/views/layout/components/Navbar.vue
function injectStyle (ssrContext) {
  __webpack_require__("I+UZ")
}
var normalizeComponent = __webpack_require__("VU/8")
/* script */

/* template */

/* template functional */
var __vue_template_functional__ = false
/* styles */
var __vue_styles__ = injectStyle
/* scopeId */
var __vue_scopeId__ = "data-v-2b19e5ca"
/* moduleIdentifier (server only) */
var __vue_module_identifier__ = null
var Component = normalizeComponent(
  Navbar,
  components_Navbar,
  __vue_template_functional__,
  __vue_styles__,
  __vue_scopeId__,
  __vue_module_identifier__
)

/* harmony default export */ var layout_components_Navbar = (Component.exports);

// EXTERNAL MODULE: ./node_modules/babel-runtime/regenerator/index.js
var regenerator = __webpack_require__("Xxa5");
var regenerator_default = /*#__PURE__*/__webpack_require__.n(regenerator);

// EXTERNAL MODULE: ./node_modules/babel-runtime/helpers/asyncToGenerator.js
var asyncToGenerator = __webpack_require__("exGp");
var asyncToGenerator_default = /*#__PURE__*/__webpack_require__.n(asyncToGenerator);

// EXTERNAL MODULE: ./src/utils/common.js
var utils_common = __webpack_require__("X2Oc");

// EXTERNAL MODULE: ./src/service/request.js
var request = __webpack_require__("R/2u");

// EXTERNAL MODULE: ./src/service/setting/system/systemConfig.js
var systemConfig = __webpack_require__("UxW6");

// CONCATENATED MODULE: ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib/selector.js?type=script&index=0!./src/components/common/side-help.vue



//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//






/* harmony default export */ var side_help = ({
	props: ['isAutoShow', 'isOpenSideHelp'],
	data: function data() {
		return {
			helpTitle: '',
			helpUrlKey: '',
			helpUrl: '',
			searchKeyword: '',
			questionList: [],
			customerServiceQQ: '',
			customerServiceQQUrl: '',
			customerServiceQQTimer: null,
			wrapHei: 700,
			wechatBarcodeFlag: 0,
			// 是否是公海用户
			mareLiberumInfo: {
				init: false,
				isMareLiberum: false,
				visible: false
			}
		};
	},

	watch: {
		$route: function $route(to, from) {
			this.getHelpInfo();
		}
	},
	computed: extends_default()({}, Object(vuex_esm["c" /* mapGetters */])(['userLoginInfo'])),
	mounted: function mounted() {
		this.getHelpInfo();
		this.getWrapHei();
		this.getWechatBarcode();
	},

	methods: {
		logGetBrowserVersion: function logGetBrowserVersion() {
			var browser = {};
			var userAgent = navigator.userAgent.toLowerCase();
			var s;
			(s = userAgent.match(/msie ([\d.]+)/)) ? browser.ie = s[1] : (s = userAgent.match(/firefox\/([\d.]+)/)) ? browser.firefox = s[1] : (s = userAgent.match(/chrome\/([\d.]+)/)) ? browser.chrome = s[1] : (s = userAgent.match(/opera.([\d.]+)/)) ? browser.opera = s[1] : (s = userAgent.match(/version\/([\d.]+).*safari/)) ? browser.safari = s[1] : 0;
			var version = "";
			if (browser.ie) {
				version = 'msie '
				/* + browser.ie*/;
			} else if (browser.firefox) {
				version = 'firefox '
				/* + browser.firefox*/;
			} else if (browser.chrome) {
				version = 'chrome '
				/* + browser.chrome*/;
			} else if (browser.opera) {
				version = 'opera '
				/* + browser.opera*/;
			} else if (browser.safari) {
				version = 'safari '
				/* + browser.safari*/;
			} else {
				version = '未知的浏览器类型';
			}
			return version;
		},
		saveLog: function saveLog(log) {
			if (log) {
				Object(request["a" /* default */])({
					url: "//qinsilk-log.cn-hangzhou.log.aliyuncs.com/logstores/log_store_tracking/track",
					params: {
						'APIVersion': '0.6.0',
						'topic': 'helpDocument',
						'client': 'gispc',
						'log': log,
						'qsr': window.location.href,
						'agent': this.logGetBrowserVersion(),
						'userid': Object(utils_common["t" /* getCookie */])("qs_uid") || 0,
						'cid': Object(utils_common["t" /* getCookie */])("qs_cid") || 0
					},
					method: "get",
					withCredentials: false
				});
			}
		},
		getWrapHei: function getWrapHei() {
			var winH = window.innerHeight || Math.max(document.body.offsetHeight, document.documentElement.offsetHeight);
			// 窗口高度减去顶部栏的高度
			this.wrapHei = parseInt(winH - 136);
		},
		getHelpInfo: function getHelpInfo() {
			var meta = this.$route.meta;
			this.helpTitle = meta.help_title;
			this.helpUrlKey = meta.help_url_key;
			// 如果有帮助文档关键词则进行匹配快速进入的链接及常见问题列表，没有则需要重置链接和问题列表，防止跳转到其他页面后保留了之前的数据
			if (this.helpUrlKey) {
				var helpUrlTemp = window.GL_CONS.HELP_URL[this.helpUrlKey];
				if (helpUrlTemp) {
					this.helpUrl = helpUrlTemp;
				}
				this.getQuestionList();
			} else {
				this.helpUrl = '';
				this.questionList = [];
			}
			this.getCustomerServicePhone();
		},
		handleNavigateToHelp: function handleNavigateToHelp() {
			if (this.helpUrl.indexOf("?") != -1) {
				window.open(this.helpUrl + "&qsr=right-help-doc");
			} else {
				window.open(this.helpUrl + "?qsr=right-help-doc");
			}
		},
		handleNavigateToIndexHelp: function handleNavigateToIndexHelp() {
			window.open("https://www.qinsilk.com/mms/front/help/gis/help-id0.html?qsr=right-help-doc", "_blank");
		},
		handleNavigateToOnlineHelp: function handleNavigateToOnlineHelp() {
			this.saveLog("right-help-go-online-service");
			// 初始化
			if (!this.mareLiberumInfo.init) {
				this.getUserAffiliation();
				this.mareLiberumInfo.init = true;
				return;
			}
			if (this.mareLiberumInfo.isMareLiberum) {
				this.mareLiberumInfo.visible = true;
			} else {
				window.open('https://web.qinsilk.com/customerService/index.html?source=2&kfid=wk3XtzBwAArYB7HO4YZNUEhv6u69Nagg');
			}
		},
		handleNavigateToHelpList: function handleNavigateToHelpList(item) {
			window.open('https://www.qinsilk.com/mms/front/help/gis/question-id' + item.id + '.html?qsr=right-help-doc');
		},
		handleNavigateToHelpSearch: function handleNavigateToHelpSearch() {
			this.saveLog("right-help-search-" + this.searchKeyword);
			window.open('https://www.qinsilk.com/mms/front/help/gis/searchCollegeList.html?searchAppIds=qinsilk_gis_help&clientType=0&page=1&keyword=' + this.searchKeyword);
		},
		getQuestionList: function getQuestionList() {
			var _this = this;

			Object(common["t" /* getQuestionList */])(this.helpUrlKey).then(function (data) {
				if (data.length) {
					_this.questionList = data;
				}
			});
		},
		getCustomerServicePhone: function getCustomerServicePhone() {
			var _this2 = this;

			var scriptEl = document.createElement('script');
			scriptEl.src = 'https://cdn.qinsilk.com/res/business/commonConfig/qinsilkInfo.js';
			document.body.appendChild(scriptEl);
			this.customerServiceQQTimer = setInterval(function () {
				if (window.qinsilkCommonInfo) {
					_this2.customerServiceQQ = window.qinsilkCommonInfo.gisQqQun;
					_this2.customerServiceQQUrl = window.qinsilkCommonInfo.gisQqQunLink && window.qinsilkCommonInfo.gisQqQunLink.match(/href=\"(.*)\"/)[1];
					clearInterval(_this2.customerServiceQQTimer);
				}
			}, 100);
		},
		getWechatBarcode: function getWechatBarcode() {
			var _this3 = this;

			return asyncToGenerator_default()( /*#__PURE__*/regenerator_default.a.mark(function _callee() {
				var time, timeFlag, clientTime;
				return regenerator_default.a.wrap(function _callee$(_context) {
					while (1) {
						switch (_context.prev = _context.next) {
							case 0:
								// 以2021年11月26日9点为分界线 以前为老用户 以后为新用户 转化为时间戳
								time = new Date("2021-11-26 9:00:00");
								timeFlag = time.getTime();
								// 客户注册时间

								_context.t0 = !_this3.userLoginInfo;

								if (!_context.t0) {
									_context.next = 6;
									break;
								}

								_context.next = 6;
								return _this3.$store.dispatch("GetUserLoginInfo");

							case 6:
								if (_this3.userLoginInfo.userVO) {
									clientTime = _this3.userLoginInfo.userVO.createTime;

									if (clientTime < timeFlag) {
										_this3.wechatBarcodeFlag = 0;
									} else {
										_this3.wechatBarcodeFlag = 1;
									}
								}

							case 7:
							case 'end':
								return _context.stop();
						}
					}
				}, _callee, _this3);
			}))();
		},
		handleToggleAutoShow: function handleToggleAutoShow(value) {
			this.$emit('toggleAutoShow', value);
		},

		// 查询用户是否为公海
		getUserAffiliation: function getUserAffiliation() {
			var _this4 = this;

			Object(systemConfig["l" /* getUserCounselorAndGroup */])().then(function (res) {
				if (res.statusCode == 1) {
					if (res.object && res.object.counselorId == null && res.object.groupId == null) {
						_this4.mareLiberumInfo.isMareLiberum = true;
						_this4.mareLiberumInfo.visible = true;
						return;
					}
				}
				window.open('https://web.qinsilk.com/customerService/index.html?source=2&kfid=wk3XtzBwAArYB7HO4YZNUEhv6u69Nagg');
			}).catch(function (error) {
				console.error("getUserCounselorAndGroup,err:", error);
				window.open('https://web.qinsilk.com/customerService/index.html?source=2&kfid=wk3XtzBwAArYB7HO4YZNUEhv6u69Nagg');
			}).finally(function () {
				_this4.mareLiberumInfo.init = true;
			});
		}
	}
});
// CONCATENATED MODULE: ./node_modules/vue-loader/lib/template-compiler?{"id":"data-v-6e00e3a1","hasScoped":true,"transformToRequire":{"video":["src","poster"],"source":"src","img":"src","image":"xlink:href"},"buble":{"transforms":{}}}!./node_modules/vue-loader/lib/selector.js?type=template&index=0!./src/components/common/side-help.vue
var side_help_render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[_c('div',{staticClass:"side-help",style:({height: (_vm.isOpenSideHelp ? _vm.wrapHei + 'px' : 0), width: (_vm.isOpenSideHelp ? '200px' : 0)})},[_c('div',{staticClass:"doc-index",on:{"click":_vm.handleNavigateToIndexHelp}},[_c('div',{staticClass:"doc-index-title"},[_vm._v("帮助中心")]),_vm._v(" "),_vm._m(0),_vm._v(" "),_c('div',{staticClass:"go-doc-index-logo"},[_vm._v(" > ")])]),_vm._v(" "),(_vm.helpTitle || _vm.helpUrl)?_c('div',{staticClass:"side-help-top"},[_c('div',{staticClass:"side-help-top-wrapper"},[_c('div',{staticClass:"side-help-title"},[_vm._v(_vm._s(_vm.helpTitle))]),_vm._v(" "),(_vm.helpUrl)?_c('div',{staticClass:"side-help-link",on:{"click":_vm.handleNavigateToHelp}},[_vm._v("进入 >")]):_vm._e()])]):_vm._e(),_vm._v(" "),_c('div',{staticClass:"side-help-bd"},[_c('div',{staticClass:"bd-search"},[_c('div',{staticClass:"bd-search__input"},[_c('el-input',{staticClass:"bd-search__input-bd",attrs:{"placeholder":"有问题,马上搜答案"},nativeOn:{"keyup":function($event){if(!('button' in $event)&&_vm._k($event.keyCode,"enter",13,$event.key)){ return null; }_vm.handleNavigateToHelpSearch($event)}},model:{value:(_vm.searchKeyword),callback:function ($$v) {_vm.searchKeyword=$$v},expression:"searchKeyword"}},[_c('el-button',{staticClass:"bd-search__input-append",attrs:{"slot":"append"},on:{"click":_vm.handleNavigateToHelpSearch},slot:"append"})],1)],1),_vm._v(" "),_c('ul',{staticClass:"bd-search__list"},_vm._l((_vm.questionList),function(item,index){return _c('li',{key:item.id,staticClass:"bd-search__item",on:{"click":function($event){_vm.handleNavigateToHelpList(item)}}},[_c('div',{staticClass:"bd-search__item-icon"},[_vm._v(_vm._s(index))]),_vm._v(_vm._s(item.title))])}))]),_vm._v(" "),_c('div',{staticClass:"bd-adviser"},[_vm._m(1),_vm._v(" "),_c('div',{staticClass:"bd-adviser-online",on:{"click":_vm.handleNavigateToOnlineHelp}},[_c('div',{staticClass:"bd-adviser-online__icon"}),_vm._v(" "),_c('div',{staticClass:"bd-adviser-online__text"},[_vm._v("在线咨询")])]),_vm._v(" "),_c('div',{staticClass:"bd-adviser-wechat"},[_c('div',{class:['wechat-barcode', _vm.wechatBarcodeFlag == 0 ? 'wechat-barcode--old' : 'wechat-barcode--new']}),_vm._v(" "),_c('div',{staticClass:"wechat-title"},[_vm._v("企业微信群")])]),_vm._v(" "),_c('div',{staticClass:"bd-adviser-operate"},[_c('div',{staticClass:"operate-wrapper"},[_c('el-checkbox',{staticClass:"operate__checkout",attrs:{"checked":_vm.isAutoShow},on:{"change":_vm.handleToggleAutoShow}},[_vm._v("不再自动展示帮助侧栏")])],1)])])])]),_vm._v(" "),(_vm.mareLiberumInfo.visible)?_c('div',{staticClass:"mareLiberum-service-mask",on:{"click":function($event){_vm.mareLiberumInfo.visible=false}}},[_c('div',{staticClass:"mareLiberum-service-modal",on:{"click":function($event){$event.stopPropagation();}}},[_c('i',{staticClass:"el-icon-circle-close close",on:{"click":function($event){_vm.mareLiberumInfo.visible=false}}}),_vm._v(" "),_c('img',{attrs:{"src":"https://cdn.qinsilk.com/img/information/mare_liberum_service_qrcode.jpg"}})])]):_vm._e()])}
var side_help_staticRenderFns = [function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"doc-index-smmary"},[_vm._v("1000"),_c('small',[_vm._v("+")]),_vm._v("帮助教程")])},function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"bd-adviser-title-wrapper"},[_c('div',{staticClass:"bd-adviser-title"},[_vm._v("秦丝专属顾问")])])}]
var side_help_esExports = { render: side_help_render, staticRenderFns: side_help_staticRenderFns }
/* harmony default export */ var common_side_help = (side_help_esExports);
// CONCATENATED MODULE: ./src/components/common/side-help.vue
function side_help_injectStyle (ssrContext) {
  __webpack_require__("9x2J")
  __webpack_require__("jwP4")
}
var side_help_normalizeComponent = __webpack_require__("VU/8")
/* script */

/* template */

/* template functional */
var side_help___vue_template_functional__ = false
/* styles */
var side_help___vue_styles__ = side_help_injectStyle
/* scopeId */
var side_help___vue_scopeId__ = "data-v-6e00e3a1"
/* moduleIdentifier (server only) */
var side_help___vue_module_identifier__ = null
var side_help_Component = side_help_normalizeComponent(
  side_help,
  common_side_help,
  side_help___vue_template_functional__,
  side_help___vue_styles__,
  side_help___vue_scopeId__,
  side_help___vue_module_identifier__
)

/* harmony default export */ var components_common_side_help = (side_help_Component.exports);

// CONCATENATED MODULE: ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib/selector.js?type=script&index=0!./src/views/layout/components/AppMain.vue
//
//
//
//
//
//
//
//
//
//


/* harmony default export */ var AppMain = ({
	name: "AppMain",
	components: {
		'side-help': components_common_side_help
	},
	props: ['isAutoShow', 'isOpenSideHelp'],
	data: function data() {
		return {
			isShow: false,
			hasCustomPointEnable: false, // 是否购买了客户积分
			companyInfo: null
		};
	},

	methods: {
		handleToggleAutoShow: function handleToggleAutoShow(value) {
			this.$emit('toggleAutoShow', value);
		}
	}
});
// CONCATENATED MODULE: ./node_modules/vue-loader/lib/template-compiler?{"id":"data-v-1d9f3736","hasScoped":true,"transformToRequire":{"video":["src","poster"],"source":"src","img":"src","image":"xlink:href"},"buble":{"transforms":{}}}!./node_modules/vue-loader/lib/selector.js?type=template&index=0!./src/views/layout/components/AppMain.vue
var AppMain_render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',{staticClass:"app-main"},[_c('div',{staticClass:"main-bd"},[_c('router-view')],1),_vm._v(" "),_c('side-help',{attrs:{"isAutoShow":_vm.isAutoShow,"isOpenSideHelp":_vm.isOpenSideHelp},on:{"toggleAutoShow":_vm.handleToggleAutoShow}})],1)}
var AppMain_staticRenderFns = []
var AppMain_esExports = { render: AppMain_render, staticRenderFns: AppMain_staticRenderFns }
/* harmony default export */ var components_AppMain = (AppMain_esExports);
// CONCATENATED MODULE: ./src/views/layout/components/AppMain.vue
function AppMain_injectStyle (ssrContext) {
  __webpack_require__("eEQt")
}
var AppMain_normalizeComponent = __webpack_require__("VU/8")
/* script */

/* template */

/* template functional */
var AppMain___vue_template_functional__ = false
/* styles */
var AppMain___vue_styles__ = AppMain_injectStyle
/* scopeId */
var AppMain___vue_scopeId__ = "data-v-1d9f3736"
/* moduleIdentifier (server only) */
var AppMain___vue_module_identifier__ = null
var AppMain_Component = AppMain_normalizeComponent(
  AppMain,
  components_AppMain,
  AppMain___vue_template_functional__,
  AppMain___vue_styles__,
  AppMain___vue_scopeId__,
  AppMain___vue_module_identifier__
)

/* harmony default export */ var layout_components_AppMain = (AppMain_Component.exports);

// CONCATENATED MODULE: ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib/selector.js?type=script&index=0!./src/views/layout/components/Breadcrumb.vue
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//




/* harmony default export */ var Breadcrumb = ({
	name: "breadcrumb",
	props: {
		currRoute: {
			type: Object,
			default: function _default() {
				return {};
			}
		},
		isOpenSideHelp: {
			type: Boolean
		}
	},
	computed: {
		showList: function showList() {
			return this.currRoute.list || [];
		}
	},
	methods: {
		logGetBrowserVersion: function logGetBrowserVersion() {
			var browser = {};
			var userAgent = navigator.userAgent.toLowerCase();
			var s;
			(s = userAgent.match(/msie ([\d.]+)/)) ? browser.ie = s[1] : (s = userAgent.match(/firefox\/([\d.]+)/)) ? browser.firefox = s[1] : (s = userAgent.match(/chrome\/([\d.]+)/)) ? browser.chrome = s[1] : (s = userAgent.match(/opera.([\d.]+)/)) ? browser.opera = s[1] : (s = userAgent.match(/version\/([\d.]+).*safari/)) ? browser.safari = s[1] : 0;
			var version = "";
			if (browser.ie) {
				version = 'msie '
				/* + browser.ie*/;
			} else if (browser.firefox) {
				version = 'firefox '
				/* + browser.firefox*/;
			} else if (browser.chrome) {
				version = 'chrome '
				/* + browser.chrome*/;
			} else if (browser.opera) {
				version = 'opera '
				/* + browser.opera*/;
			} else if (browser.safari) {
				version = 'safari '
				/* + browser.safari*/;
			} else {
				version = '未知的浏览器类型';
			}
			return version;
		},
		saveLog: function saveLog(log) {
			if (log) {
				Object(request["a" /* default */])({
					url: "//qinsilk-log.cn-hangzhou.log.aliyuncs.com/logstores/log_store_tracking/track",
					params: {
						'APIVersion': '0.6.0',
						'topic': 'helpDocument',
						'client': 'gispc',
						'log': log,
						'qsr': window.location.href,
						'agent': this.logGetBrowserVersion(),
						'userid': Object(utils_common["t" /* getCookie */])("qs_uid") || 0,
						'cid': Object(utils_common["t" /* getCookie */])("qs_cid") || 0
					},
					method: "get",
					withCredentials: false
				});
			}
		},
		handleToggleSideHelp: function handleToggleSideHelp() {
			this.saveLog("icon-help-click");
			this.$emit('toggleSideHelp', !this.isOpenSideHelp);
		}
	}
});
// CONCATENATED MODULE: ./node_modules/vue-loader/lib/template-compiler?{"id":"data-v-01b57a48","hasScoped":true,"transformToRequire":{"video":["src","poster"],"source":"src","img":"src","image":"xlink:href"},"buble":{"transforms":{}}}!./node_modules/vue-loader/lib/selector.js?type=template&index=0!./src/views/layout/components/Breadcrumb.vue
var Breadcrumb_render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"nav-breadcrumb"},[_c('el-breadcrumb',{attrs:{"separator-class":"el-icon-arrow-right"}},[_c('el-breadcrumb-item',[_c('div',{staticClass:"breadcrumb-icon",class:_vm.currRoute.breadcrumbIcon})]),_vm._v(" "),_vm._l((_vm.currRoute.list),function(item,index){return _c('el-breadcrumb-item',{directives:[{name:"show",rawName:"v-show",value:(!item.isTop || _vm.showList.length == 1),expression:"!item.isTop || showList.length == 1"}],key:index},[(item.redirect === 'noredirect' || index == _vm.currRoute.list.length - 1 || (typeof item.redirect === 'function' && item.redirect(_vm.currRoute.list) === 'noredirect'))?_c('span',[_vm._v(_vm._s(item.title))]):_c('router-link',{class:{'active': _vm.currRoute.list[index+1] && _vm.currRoute.list[index+1].breadcrumbLight },attrs:{"to":item.redirect ? typeof item.redirect === 'function' ? item.redirect(_vm.currRoute.list) : item.redirect : item.path}},[_vm._v(_vm._s(item.title))])],1)})],2),_vm._v(" "),_c('div',{class:['right-help-doc-icon',_vm.isOpenSideHelp?'open-right-help':''],on:{"click":_vm.handleToggleSideHelp}})],1)}
var Breadcrumb_staticRenderFns = []
var Breadcrumb_esExports = { render: Breadcrumb_render, staticRenderFns: Breadcrumb_staticRenderFns }
/* harmony default export */ var components_Breadcrumb = (Breadcrumb_esExports);
// CONCATENATED MODULE: ./src/views/layout/components/Breadcrumb.vue
function Breadcrumb_injectStyle (ssrContext) {
  __webpack_require__("i0am")
}
var Breadcrumb_normalizeComponent = __webpack_require__("VU/8")
/* script */

/* template */

/* template functional */
var Breadcrumb___vue_template_functional__ = false
/* styles */
var Breadcrumb___vue_styles__ = Breadcrumb_injectStyle
/* scopeId */
var Breadcrumb___vue_scopeId__ = "data-v-01b57a48"
/* moduleIdentifier (server only) */
var Breadcrumb___vue_module_identifier__ = null
var Breadcrumb_Component = Breadcrumb_normalizeComponent(
  Breadcrumb,
  components_Breadcrumb,
  Breadcrumb___vue_template_functional__,
  Breadcrumb___vue_styles__,
  Breadcrumb___vue_scopeId__,
  Breadcrumb___vue_module_identifier__
)

/* harmony default export */ var layout_components_Breadcrumb = (Breadcrumb_Component.exports);

// CONCATENATED MODULE: ./src/views/layout/components/index.js



// CONCATENATED MODULE: ./node_modules/babel-loader/lib!./node_modules/vue-loader/lib/selector.js?type=script&index=0!./src/views/layout/Layout.vue
//
//
//
//
//
//
//
//



/* harmony default export */ var Layout = ({
	name: "layout",
	components: {
		Navbar: layout_components_Navbar,
		Breadcrumb: layout_components_Breadcrumb,
		AppMain: layout_components_AppMain
	},
	data: function data() {
		return {
			// 当前路由的信息
			currRoute: {
				list: [],
				iconNav: "",
				breadcrumbIcon: ""
			},
			isOpenSideHelp: true,
			isAutoShow: false
		};
	},

	watch: {
		"$route.path": function $routePath(v) {
			this.initCurrRoute();
		}
	},
	created: function created() {
		this.initCurrRoute();
		var rightDocExpanded = window.localStorage.getItem('rightDocExpanded');
		if (typeof rightDocExpanded != 'undefined') {
			if (rightDocExpanded == 'true') {
				rightDocExpanded = true;
			} else {
				rightDocExpanded = false;
			}
			this.isAutoShow = !rightDocExpanded;
			this.isOpenSideHelp = rightDocExpanded;
		}
	},

	methods: {
		initCurrRoute: function initCurrRoute() {
			var list = this.$router.currentRoute.matched || [];
			var showList = [];
			var breadcrumbIcon = "";
			var iconNav = "";
			list.forEach(function (item, index) {
				if (item.meta.title) {
					showList.push({
						title: item.meta.title,
						isTop: item.meta.isBreadCrumbTop,
						breadcrumbLight: item.meta.breadcrumbLight,
						redirect: item.redirect,
						path: item.path
					});
				}
				if (item.meta.iconBreadcrumb) {
					breadcrumbIcon = item.meta.iconBreadcrumb;
				}
				if (item.meta.iconNavClass) {
					iconNav = item.meta.iconNavClass;
					breadcrumbIcon = iconNav + "-gray";
				}
			});
			this.$set(this, "currRoute", {
				list: showList,
				breadcrumbIcon: breadcrumbIcon,
				iconNav: iconNav
			});
		},
		updateBreadcrumb: function updateBreadcrumb(cls, b) {
			console.log(cls);
			console.log(b);
		},
		handleToggleSideHelp: function handleToggleSideHelp(isOpenSideHelp) {
			this.isOpenSideHelp = isOpenSideHelp;
		},
		handleToggleAutoShow: function handleToggleAutoShow(value) {
			this.isAutoShow = value;
			this.isOpenSideHelp = !value;
			window.localStorage.setItem('rightDocExpanded', !value);
		}
	}
});
// CONCATENATED MODULE: ./node_modules/vue-loader/lib/template-compiler?{"id":"data-v-86a42cd4","hasScoped":true,"transformToRequire":{"video":["src","poster"],"source":"src","img":"src","image":"xlink:href"},"buble":{"transforms":{}}}!./node_modules/vue-loader/lib/selector.js?type=template&index=0!./src/views/layout/Layout.vue
var Layout_render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"main-container"},[_c('navbar',{attrs:{"curr-route":_vm.currRoute}}),_vm._v(" "),_c('breadcrumb',{attrs:{"curr-route":_vm.currRoute,"isOpenSideHelp":_vm.isOpenSideHelp},on:{"update-breadcrumb":_vm.updateBreadcrumb,"toggleSideHelp":_vm.handleToggleSideHelp}}),_vm._v(" "),_c('app-main',{attrs:{"isAutoShow":_vm.isAutoShow,"isOpenSideHelp":_vm.isOpenSideHelp},on:{"toggleAutoShow":_vm.handleToggleAutoShow}})],1)}
var Layout_staticRenderFns = []
var Layout_esExports = { render: Layout_render, staticRenderFns: Layout_staticRenderFns }
/* harmony default export */ var layout_Layout = (Layout_esExports);
// CONCATENATED MODULE: ./src/views/layout/Layout.vue
function Layout_injectStyle (ssrContext) {
  __webpack_require__("jeTm")
}
var Layout_normalizeComponent = __webpack_require__("VU/8")
/* script */

/* template */

/* template functional */
var Layout___vue_template_functional__ = false
/* styles */
var Layout___vue_styles__ = Layout_injectStyle
/* scopeId */
var Layout___vue_scopeId__ = "data-v-86a42cd4"
/* moduleIdentifier (server only) */
var Layout___vue_module_identifier__ = null
var Layout_Component = Layout_normalizeComponent(
  Layout,
  layout_Layout,
  Layout___vue_template_functional__,
  Layout___vue_styles__,
  Layout___vue_scopeId__,
  Layout___vue_module_identifier__
)

/* harmony default export */ var views_layout_Layout = (Layout_Component.exports);

// CONCATENATED MODULE: ./src/router/index.js
/* unused harmony export constantRouterMap */



vue_esm["default"].use(vue_router_esm["a" /* default */]);

/* Layout，包括顶部菜单 */

// import store from "@/store";
// import { getObject } from "@/utils/common";
// import { getCompanyConfigJson } from "@/service/common";
/**
 * redirect: noredirect           if `redirect:noredirect` will no redirct in the breadcrumb
 * breadcrumbLight: true or false  如果是true则他的父级路由高亮蓝色显示
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 **/
var constantRouterMap = [{ path: "/404", component: function component() {
		return __webpack_require__.e/* import() */(59).then(__webpack_require__.bind(null, "+H76"));
	} },

// 首页，默认跳转到首页
{
	path: "/",
	component: views_layout_Layout,
	redirect: "/home",
	meta: {
		title: "首页",
		isBreadCrumbTop: true,
		iconNavClass: "icon-home"
	},
	children: [
	// 首页
	{
		path: "home",
		name: "home",
		component: function component() {
			return __webpack_require__.e/* import() */(79).then(__webpack_require__.bind(null, "KR8f"));
		}
	},
	// 销售
	{
		path: "sale",
		redirect: function redirect(list) {
			if (list && list.length > 0) {
				var obj = list[list.length - 1];
				if (obj) {
					var index = obj.path ? obj.path.indexOf('/saleOrder/') : -1;
					if (index > -1) {
						return 'noredirect';
					}
				}
			}
			return '/sale/client';
		},
		meta: {
			title: "销售",
			iconNavClass: "icon-sale"
		},
		component: function component() {
			return __webpack_require__.e/* import() */(4/* duplicate */).then(__webpack_require__.bind(null, "cKD0"));
		},
		children: [
		// 客户
		{
			path: "client",
			name: "redirect-orderProcess",
			redirect: "/sale/client/info",
			meta: {
				title: "客户"
			},
			component: function component() {
				return __webpack_require__.e/* import() */(100).then(__webpack_require__.bind(null, "HrWI"));
			},
			children: [{
				path: "info",
				name: "clientInfo",
				meta: {
					title: "客户管理",
					help_title: '客户管理介绍',
					help_url_key: "clientListHelp",
					authority: ["clientView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(28)]).then(__webpack_require__.bind(null, "XvUu"));
				}
			}, {
				path: "detail",
				name: "clientDetail",
				meta: {
					breadcrumbLight: true,
					title: "客户编辑"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(3)]).then(__webpack_require__.bind(null, "fP9L"));
				}
			}, {
				path: "addNew",
				name: "addNewClient",
				meta: {
					breadcrumbLight: true,
					title: "新增客户"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(3)]).then(__webpack_require__.bind(null, "fP9L"));
				}
			}, {
				path: "clientClassifyItem",
				name: "clientClassifyItem",
				meta: {
					title: "客户分类",
					help_title: '客户分类介绍',
					help_url_key: "clientItemList",
					authority: ["clientItemView"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(54).then(__webpack_require__.bind(null, "JDwc"));
				}
			}, {
				path: "clientLabel",
				name: "clientLabel",
				meta: {
					title: "客户标签",
					help_title: '客户标签介绍',
					help_url_key: 'clientLabelHelp',
					authority: ["clientTagView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(61)]).then(__webpack_require__.bind(null, "ZoEe"));
				}
			}]
		}, {
			path: "saleOrder",
			redirect: "noredirect",
			meta: {
				title: "销售单据"
			},
			component: function component() {
				return __webpack_require__.e/* import() */(4/* duplicate */).then(__webpack_require__.bind(null, "cKD0"));
			},
			children: [
			// 报价单
			{
				path: "quotation",
				name: "quotation",
				meta: {
					title: "报价单",
					help_title: '报价单介绍',
					help_url_key: "quotation"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(1)]).then(__webpack_require__.bind(null, "UU+v"));
				}
			},
			// 新增报价单
			{
				path: "quotation/add",
				name: "quotationAdd",
				meta: {
					title: "新增报价单",
					help_title: '报价单介绍',
					help_url_key: "quotation"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(1)]).then(__webpack_require__.bind(null, "UU+v"));
				}
			},
			// 编辑报价单
			{
				path: "quotation/update",
				name: "quotationUpdate",
				meta: {
					title: "编辑报价单",
					help_title: '报价单介绍',
					help_url_key: "quotation"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(1)]).then(__webpack_require__.bind(null, "UU+v"));
				}
			},
			// 报价单详情
			{
				path: "quotation/detail",
				name: "quotationDetail",
				meta: {
					title: "报价单详情",
					help_title: '报价单介绍',
					help_url_key: "quotation"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(1)]).then(__webpack_require__.bind(null, "UU+v"));
				}
			}]
		}]
	},
	// 营销
	{
		path: "marketing",
		redirect: "noredirect",
		meta: {
			title: "营销",
			// iconBreadcrumb: "icon-sms-gray",
			iconNavClass: "icon-marketing"
		},
		component: { template: "<router-view></router-view>" },
		children: [{
			path: "subMarketing",
			name: "subMarketing",
			meta: { title: "营销" },
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(111)]).then(__webpack_require__.bind(null, "rKI5"));
			},
			children: [
			// 客户积分
			{
				path: "clientPoint",
				name: "clientPoint",
				meta: {
					title: "客户积分",
					help_title: '客户积分介绍',
					help_url_key: "clientPointHelp"
				},
				component: function component() {
					return __webpack_require__.e/* import() */(22).then(__webpack_require__.bind(null, "rk+N"));
				}
			},
			// 会员卡
			{
				path: "memberCard",
				name: "memberCard",
				meta: {
					title: "会员卡",
					help_title: '会员卡介绍',
					help_url_key: "memberCardHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(47)]).then(__webpack_require__.bind(null, "MjvR"));
				}
			},
			// 微信会员卡
			{
				path: "wxVipCard",
				name: "wxVipCard",
				meta: {
					title: "微信会员卡",
					help_title: '微信会员卡介绍',
					help_url_key: "wechatMemberCardHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(85)]).then(__webpack_require__.bind(null, "FdtI"));
				}
			},
			// 充值
			{
				path: "recharge",
				name: "recharge",
				meta: {
					title: "充值",
					help_title: '充值介绍',
					help_url_key: "memberCardHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(96)]).then(__webpack_require__.bind(null, "tPa4"));
				}
			},
			// 专属品牌小程序
			{
				path: "wechatProgram",
				name: 'wechatProgram',
				meta: {
					title: "专属品牌小程序",
					help_title: '专属品牌小程序',
					help_url_key: "wechatProgramHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(90)]).then(__webpack_require__.bind(null, "DAeH"));
				}
			},
			// 短信服务
			{ // 重定向至智能发送
				path: "smsService/",
				name: "redirect-send",
				redirect: "/marketing/subMarketing/smsService/send"
			},
			// 智能发送
			{
				path: "smsService/send",
				name: "smsServiceSend",
				meta: {
					title: "智能发送",
					help_title: '短信服务介绍',
					help_url_key: "smsServiceHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(31)]).then(__webpack_require__.bind(null, "iXzQ"));
				}
			},
			// 活动营销
			{
				path: "smsService/activity",
				name: "smsServiceActivity",
				meta: {
					title: "活动营销",
					help_title: '短信服务介绍',
					help_url_key: "smsServiceHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(13)]).then(__webpack_require__.bind(null, "ZS2y"));
				}
			},
			// 模版管理
			{
				path: "smsService/model",
				name: "smsServiceModel",
				meta: {
					title: "模版管理",
					help_title: '短信服务介绍',
					help_url_key: "smsServiceHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(77)]).then(__webpack_require__.bind(null, "ZMri"));
				}
			},
			// 发送记录
			{
				path: "smsService/record",
				name: "smsServiceRecord",
				meta: {
					title: "发送记录",
					help_title: '短信服务介绍',
					help_url_key: "smsServiceHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(17)]).then(__webpack_require__.bind(null, "e7TN"));
				}
			},
			// 定时短信
			{
				path: "smsService/timing",
				name: "smsServiceTiming",
				meta: {
					title: "定时短信",
					help_title: '短信服务介绍',
					help_url_key: "smsServiceHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(18)]).then(__webpack_require__.bind(null, "h8PN"));
				}
			}]
		},
		// 分销
		{
			path: "distributeRule",
			name: "redirect-distributeRule",
			redirect: "/marketing/distributeRule/index",
			meta: {
				title: "分销",
				iconNavClass: "icon-marketing"
			},
			component: function component() {
				return __webpack_require__.e/* import() */(94).then(__webpack_require__.bind(null, "A4yN"));
			},
			children: [{
				path: "index",
				name: "distributeRuleIndex",
				meta: {
					title: "分销规则",
					help_title: '分销功能介绍',
					help_url_key: "distributionHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(16)]).then(__webpack_require__.bind(null, "+bon"));
				}
			}, {
				path: "list",
				name: "distributeRuleList",
				meta: {
					title: "分销列表",
					help_title: '分销功能介绍',
					help_url_key: "distributionHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(43)]).then(__webpack_require__.bind(null, "VtVd"));
				}
			}, {
				path: "total",
				name: "distributeRuleTotal",
				meta: {
					title: "分佣统计",
					help_title: '分销功能介绍',
					help_url_key: "distributionHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(46)]).then(__webpack_require__.bind(null, "VIkp"));
				}
			}]
		}]
	},
	// 财务
	{
		path: "finance",
		meta: {
			title: '财务',
			iconNavClass: "icon-finance"
		},
		redirect: "noredirect",
		component: function component() {
			return __webpack_require__.e/* import() */(87).then(__webpack_require__.bind(null, "qDpw"));
		},
		children: [{
			path: "account",
			name: "account",
			meta: {
				title: "账户管理"
			},
			redirect: "noredirect",
			component: function component() {
				return __webpack_require__.e/* import() */(88).then(__webpack_require__.bind(null, "TkUL"));
			},
			children: [
			// 结算账户
			{
				path: "accountList",
				name: "accountList",
				meta: {
					title: "结算账户",
					help_title: "结算账户介绍",
					help_url_key: "accountList"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(58)]).then(__webpack_require__.bind(null, "2OTs"));
				}
			},
			// 账目类型
			{
				path: "accountItemList",
				name: "accountItemList",
				meta: {
					title: "账目类型",
					help_title: "账目类型介绍",
					help_url_key: "accountItemList"
				},
				component: function component() {
					return __webpack_require__.e/* import() */(53).then(__webpack_require__.bind(null, "7a+O"));
				}
			}]
		}, {
			path: "record",
			name: "record",
			meta: { title: "资金往来" },
			redirect: "noredirect",
			component: function component() {
				return __webpack_require__.e/* import() */(95).then(__webpack_require__.bind(null, "/IVe"));
			},
			children: [
			// 收款流水(微信/支付宝)
			{
				path: "salePayRecordList",
				name: "salePayRecordList",
				meta: {
					title: "收款流水(微信/支付宝)",
					help_title: "收款流水(微信/支付宝)介绍",
					help_url_key: "salePayRecordListHelp",
					authority: ["salePayRecord"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(107)]).then(__webpack_require__.bind(null, "HInx"));
				}
			}, {
				path: "accountRecordCompanyList",
				name: "accountRecordCompanyList",
				meta: {
					title: "账户流水及记账",
					help_title: "账户流水介绍",
					help_url_key: "accountRecordCompanyList",
					authority: ["financeMan"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(56)]).then(__webpack_require__.bind(null, "m+HK"));
				}
			}, {
				path: "accountRecordClientList",
				name: "accountRecordClientList",
				meta: {
					title: "客户对账及收款"
				},
				redirect: "/finance/record/accountRecordClientList/clientDebtList",
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(102)]).then(__webpack_require__.bind(null, "NN8Z"));
				},
				children: [{
					path: "clientDebtList",
					name: "clientDebtList",
					meta: {
						title: "对账汇总",
						help_title: "客户对账及收款介绍",
						help_url_key: "accountRecordClientList",
						authority: ["clientFinanceManView"]
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(68)]).then(__webpack_require__.bind(null, "tl4z"));
					}
				}, {
					path: "clientAccountRecord",
					name: "clientAccountRecord",
					meta: {
						title: "客户对账单",
						help_title: "客户对账及收款介绍",
						help_url_key: "accountRecordClientList",
						authority: ["clientFinanceManView"]
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(33)]).then(__webpack_require__.bind(null, "5fXl"));
					}
				}, {
					path: "clientOrderDebtDetails",
					name: "clientOrderDebtDetails",
					meta: {
						title: "单据欠款明细",
						help_title: "单据欠款明细介绍",
						help_url_key: "clientOrderDebtDetailsHelp",
						authority: ["clientFinanceManView"]
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(25)]).then(__webpack_require__.bind(null, "KKFx"));
					}
				}, {
					path: "previewClientRecordMail",
					name: "previewClientRecordMail",
					meta: {
						title: "发送邮件",
						help_title: "发送邮件介绍",
						help_url_key: "sendMailHelp",
						authority: ["clientFinanceManView"]
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(89)]).then(__webpack_require__.bind(null, "yy1c"));
					}
				}]
			}, {
				path: "clientDebtListExport",
				name: "clientDebtListExport",
				meta: {
					title: "对账汇总导出页面"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(67)]).then(__webpack_require__.bind(null, "tqHb"));
				}
			}]
		}]
	},
	// 设置
	{
		path: "setting",
		meta: {
			title: "设置",
			iconNavClass: "icon-system"
		},
		redirect: "noredirect",
		component: function component() {
			return __webpack_require__.e/* import() */(93).then(__webpack_require__.bind(null, "VlR1"));
		},
		children: [{
			path: "goods",
			name: "goods",
			meta: {
				title: "商品"
			},
			redirect: "noredirect",
			component: function component() {
				return __webpack_require__.e/* import() */(97).then(__webpack_require__.bind(null, "cv2e"));
			},
			children: [
			// 商品管理
			{
				path: "goodsList",
				name: "goodsList",
				meta: {
					title: "商品管理",
					help_title: '商品管理介绍',
					help_url_key: "goodsList",
					authority: ['goodsManView']
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(9)]).then(__webpack_require__.bind(null, "H0K3"));
				}
			}, {
				path: "goodsListExport",
				name: "goodsListExport",
				meta: {
					title: "商品列表导出页面"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(69)]).then(__webpack_require__.bind(null, "X8Wk"));
				}
			},
			// 条码打印
			{
				path: "printBarcodeList",
				name: "printBarcodeList",
				meta: {
					title: "条码打印",
					help_title: '条码打印介绍',
					help_url_key: "printBarcodeListHelp",
					authority: ['goodsManPrint']
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(21)]).then(__webpack_require__.bind(null, "lKSk"));
				}
			},
			// 序列号查询
			{
				path: "goodsSnList",
				name: "goodsSnList",
				meta: {
					title: "序列号查询",
					help_title: '序列号查询介绍',
					help_url_key: "goodsSnList"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(44)]).then(__webpack_require__.bind(null, "tR+J"));
				}
			},
			// 商品导入
			{
				path: "goodsImport",
				redirect: "/setting/goods/goodsImport/goodsImport",
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(98)]).then(__webpack_require__.bind(null, "/ghj"));
				},
				children: [{
					path: "goodsImport",
					name: "goodsImport",
					meta: {
						title: "数据导入",
						help_title: '数据导入介绍',
						help_url_key: "goodsListHelp",
						authority: ['goodsManImport']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(38)]).then(__webpack_require__.bind(null, "F8o+"));
					}
				}, {
					path: "clientItemPriceImport",
					name: "clientItemPriceImport",
					meta: {
						title: "数据导入",
						help_title: '数据导入介绍',
						help_url_key: "goodsListHelp",
						authority: ['goodsManImport']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(45)]).then(__webpack_require__.bind(null, "ceqC"));
					}
				}, {
					path: "unitGoodsImport",
					name: "unitGoodsImport",
					meta: {
						title: "数据导入",
						help_title: '数据导入介绍',
						help_url_key: "goodsListHelp",
						authority: ['goodsManImport']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(51)]).then(__webpack_require__.bind(null, "1gMG"));
					}
				}, {
					path: "fullGoodsImport",
					name: "fullGoodsImport",
					meta: {
						title: "新导入模版(全量信息)",
						help_title: '数据导入介绍',
						help_url_key: "goodsListHelp",
						authority: ['goodsManImport']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(48)]).then(__webpack_require__.bind(null, "IJWJ"));
					}
				}]
			},
			// 商品分类
			{
				path: "categoryList",
				name: "categoryList",
				meta: {
					title: "商品分类",
					help_title: '商品分类介绍',
					help_url_key: "categoryListHelp",
					authority: ["categoryView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(35)]).then(__webpack_require__.bind(null, "MgR/"));
				}
			},
			// 品牌管理
			{
				path: "brandList",
				name: "brandList",
				meta: {
					title: "品牌管理",
					help_title: '品牌管理介绍',
					help_url_key: "blandListHelp",
					authority: ["blandView"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(75).then(__webpack_require__.bind(null, "cMZ7"));
				}
			},
			// 单位管理
			{
				path: "unitList",
				name: "unitList",
				meta: {
					title: "单位管理",
					help_title: '单位管理介绍',
					help_url_key: "unitListHelp",
					authority: ["unitView"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(23).then(__webpack_require__.bind(null, "9cvs"));
				}
			},
			// 条码管理
			{
				path: "barcodeConfigPage",
				name: "barcodeConfigPage",
				meta: {
					title: "条码管理",
					help_title: '条码管理介绍',
					help_url_key: "barcodeConfigPage",
					authority: ["barcodeConfigView"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(66).then(__webpack_require__.bind(null, "8yQT"));
				}
			},
			// 规格管理
			{
				path: "specManage",
				name: "specManage",
				meta: {
					title: "规格管理",
					help_title: '规格管理介绍',
					help_url_key: "specManage",
					authority: ["goodsManView"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(74).then(__webpack_require__.bind(null, "7dje"));
				}
			},
			// 自定义属性管理
			{
				path: "customAttribute",
				name: "customAttribute",
				meta: {
					title: "自定义属性管理",
					help_title: '自定义属性管理',
					help_url_key: "customAttributeHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(65)]).then(__webpack_require__.bind(null, "TcDq"));
				}
			}]
		}, {
			path: "system",
			name: "system",
			meta: {
				title: "系统"
			},
			redirect: "noredirect",
			component: function component() {
				return __webpack_require__.e/* import() */(92).then(__webpack_require__.bind(null, "1q6H"));
			},
			children: [
			// 个人信息
			{
				path: "personalInfo",
				name: "personalInfo",
				meta: {
					title: "个人信息",
					help_title: "个人信息介绍",
					help_url_key: "personalInfo",
					authority: ["myInfoView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(6)]).then(__webpack_require__.bind(null, "mrta"));
				}
			},
			// 门店与员工
			{
				path: "shopManagement",
				name: "shopManagement",
				meta: {
					title: "门店与员工",
					help_title: "门店与员工介绍",
					help_url_key: "comStoreListHelp",
					authority: ["userManView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(10)]).then(__webpack_require__.bind(null, "m4Bv"));
				}
			},
			// 角色管理
			{
				path: "roleManagement",
				name: "roleManagement",
				meta: {
					title: "角色管理",
					help_title: "角色管理介绍",
					help_url_key: "roleListHelp",
					authority: ["roleManView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(110)]).then(__webpack_require__.bind(null, "m+Ro"));
				}
			},
			// 系统公告
			{
				path: "bulletin",
				name: "bulletin",
				meta: {
					title: "公司公告",
					help_title: "系统公告介绍",
					help_url_key: "bulletinInnerListHelp",
					authority: ["bulletinView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(84)]).then(__webpack_require__.bind(null, "BOQO"));
				}
			},
			// 物流设置
			{
				path: "logistics",
				name: "logistics",
				meta: {
					title: "物流设置",
					help_title: "物流设置介绍",
					help_url_key: "deliveryCompanyListHelp",
					authority: ["deliveryView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(34)]).then(__webpack_require__.bind(null, "zNes"));
				}
			},
			// 物流设置-发件信息
			{
				path: "logisticsDelivery",
				name: "logisticsDelivery",
				meta: {
					title: "发件信息管理"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(37)]).then(__webpack_require__.bind(null, "KRva"));
				}
			},
			// 系统参数
			{
				path: "systemConfig",
				name: "systemConfig",
				meta: {
					title: "系统参数",
					help_title: "系统参数介绍",
					help_url_key: "companyConfigHelp",
					authority: ["companyConfigView"]
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(11)]).then(__webpack_require__.bind(null, "asck"));
				}
			},
			// 系统日志
			{
				path: "operateLogList",
				name: "operateLogList",
				meta: {
					title: "系统日志",
					help_title: "系统日志介绍",
					help_url_key: "operateLogList",
					authority: ["systemLogView"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(101).then(__webpack_require__.bind(null, "wr21"));
				}
			},
			// 存储空间
			{
				path: "storageSpace",
				name: "storageSpace",
				meta: {
					title: "存储空间",
					authority: ["storageSpaceView"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(64).then(__webpack_require__.bind(null, "duv6"));
				}
			},
			// 系统重置
			{
				path: "resetPage",
				name: "resetPage",
				meta: {
					title: "系统重置",
					help_title: "系统重置介绍",
					help_url_key: "resetPage",
					authority: ["systemResetEdit"]
				},
				component: function component() {
					return __webpack_require__.e/* import() */(63).then(__webpack_require__.bind(null, "odKI"));
				}
			},
			// 员工排班
			{
				path: "employeeScheduling",
				name: "employeeScheduling",
				meta: {
					title: "员工排班"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(55)]).then(__webpack_require__.bind(null, "ODtA"));
				}
			}]
		}]
	},
	// 网店
	{
		path: "onlineStore",
		meta: {
			title: "网店",
			iconNavClass: "icon-shop"
		},
		redirect: "noredirect",
		component: function component() {
			return __webpack_require__.e/* import() */(2/* duplicate */).then(__webpack_require__.bind(null, "QxYx"));
		},
		children: [{
			path: "gsm",
			meta: {
				title: "销货宝"
			},
			redirect: "noredirect",
			component: function component() {
				return __webpack_require__.e/* import() */(2/* duplicate */).then(__webpack_require__.bind(null, "QxYx"));
			},
			children: [
			// 上架商品
			{
				path: "commodity",
				name: "commodity",
				meta: {
					title: "上架商品"
				},
				component: function component() {
					return __webpack_require__.e/* import() */(2/* duplicate */).then(__webpack_require__.bind(null, "QxYx"));
				},
				children: [{
					path: "/",
					name: "redirect-commodityList",
					redirect: "/onlineStore/gsm/commodity/commodityList"
				}, {
					path: "commodityList",
					name: "commodityList",
					meta: {
						title: "上架商品列表",
						help_title: '上架商品介绍',
						help_url_key: "wechatCommodityListHelp",
						authority: ['commodityManView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(26)]).then(__webpack_require__.bind(null, "0SGs"));
					}
				},
				// 商品详情编辑
				{
					path: "edit",
					name: "commodityEdit",
					meta: {
						title: "商品编辑",
						authority: ['commodityManView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(91)]).then(__webpack_require__.bind(null, "QiHP"));
					},
					children: [
					// 重定向至基本信息
					{
						path: "/",
						name: "redirect-basic",
						redirect: "/onlineStore/gsm/commodity/edit/commodityBasic"
					},
					// 基本信息
					{
						path: "commodityBasic",
						name: "commodityBasic",
						meta: {
							title: "基本信息",
							authority: ['commodityManView']
						},
						component: function component() {
							return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(82)]).then(__webpack_require__.bind(null, "VtZz"));
						}
					},
					// 价格/规格
					{
						path: "commoditySale",
						name: "commoditySale",
						meta: {
							title: "价格/规格",
							authority: ['commodityManView']
						},
						component: function component() {
							return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(108)]).then(__webpack_require__.bind(null, "BzMA"));
						}
					},
					// 商品相册
					{
						path: "commodityAlbum",
						name: "commodityAlbum",
						meta: {
							title: "商品相册",
							authority: ['commodityManView']
						},
						component: function component() {
							return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(20)]).then(__webpack_require__.bind(null, "wtc3"));
						}
					},
					// 图文详情
					{
						path: "commodityDetail",
						name: "commodityDetail",
						meta: {
							title: "图文详情",
							authority: ['commodityManView']
						},
						component: function component() {
							return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(105)]).then(__webpack_require__.bind(null, "J4jM"));
						}
					}]
				}]
			},
			// 订单处理
			{
				path: "order/orderProcess",
				name: "orderProcess",
				meta: {
					title: "订单处理",
					help_title: '订单处理介绍',
					help_url_key: "wechatOrderListHelp"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(19)]).then(__webpack_require__.bind(null, "5cDk"));
				}
			},
			// 销货宝订单详情
			{
				path: "order/orderDetail/:ordersSn",
				name: "orderDetail",
				// redirect: "/commodityEdit/info/basic",
				meta: {
					title: "销货宝订单详情"
				},
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(14)]).then(__webpack_require__.bind(null, "N1Rw"));
				}
			},
			// 店铺装修
			{
				path: "decoration",
				name: "redirect-decoration",
				redirect: { name: 'decorationList' },
				meta: {
					title: "店铺装修",
					iconNavClass: "icon-shop"
				},
				component: function component() {
					return __webpack_require__.e/* import() */(2/* duplicate */).then(__webpack_require__.bind(null, "QxYx"));
				},
				children: [
				// 模板列表
				{
					path: "decorationList",
					name: "decorationList",
					meta: {
						title: "模板列表",
						help_title: '店铺装修介绍',
						help_url_key: "shopDecorationHelp",
						authority: ['shopDecorate']
					},
					component: function component() {
						return __webpack_require__.e/* import() */(30).then(__webpack_require__.bind(null, "O/Dc"));
					}
				},
				// 编辑样式
				{
					path: "editingStyle",
					name: "editingStyle",
					meta: {
						title: "编辑样式",
						help_title: '店铺装修介绍',
						help_url_key: "shopDecorationHelp",
						authority: ['shopDecorate']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(7)]).then(__webpack_require__.bind(null, "qya5"));
					}
				},
				// 分类页装修
				{
					path: "classificationPageStyle",
					name: "classificationPageStyle",
					meta: {
						title: "分类页装修",
						authority: ['shopDecorate']
					},
					component: function component() {
						return __webpack_require__.e/* import() */(104).then(__webpack_require__.bind(null, "quLO"));
					}
				}]
			},
			// 店铺设置
			{
				path: "shopConfiguration",
				name: "shopConfiguration",
				meta: {
					title: "店铺设置"
				},
				redirect: { name: 'basicSetting' },
				component: function component() {
					return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(78)]).then(__webpack_require__.bind(null, "2VUr"));
				},
				children: [{
					path: "basicSetting",
					name: "basicSetting",
					meta: {
						title: "店铺概况",
						help_title: '店铺概况介绍',
						help_url_key: "wechatShopHelp",
						authority: ['shop', 'shopConfigView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(36)]).then(__webpack_require__.bind(null, "uOYT"));
					}
				}, {
					path: "putCommodityOnShelves",
					name: "putCommodityOnShelves",
					meta: {
						title: "店铺配置",
						authority: ['shop', 'shopConfigView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(24)]).then(__webpack_require__.bind(null, "bscM"));
					}
				}, {
					path: "freightSetting",
					name: "freightSetting",
					meta: {
						title: "运费设置",
						authority: ['shop', 'shopConfigView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(81)]).then(__webpack_require__.bind(null, "R0eV"));
					}
				}, {
					path: "paymentChannel",
					name: "paymentChannel",
					meta: {
						title: "支付渠道",
						help_title: '支付渠道介绍',
						help_url_key: "wechatPaySettingHelp",
						authority: ['shop', 'shopConfigView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(50)]).then(__webpack_require__.bind(null, "rQmu"));
					}
				}, {
					path: "storefrontManage",
					name: "storefrontManage",
					meta: {
						title: "店面管理",
						help_title: '店面管理介绍',
						help_url_key: "wechatFrontManagerHelp"
					},
					component: function component() {
						return __webpack_require__.e/* import() */(112).then(__webpack_require__.bind(null, "fMiy"));
					}
				}, {
					path: "openTimfrontManage",
					name: "openTimfrontManage",
					meta: {
						title: "客服管理",
						help_title: '客服管理介绍',
						authority: ['shop', 'shopConfigView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(70)]).then(__webpack_require__.bind(null, "Nh+X"));
					}
				}, {
					path: "openTimWorkstation",
					name: "openTimWorkstation",
					meta: {
						title: "客服工作台",
						help_title: '客服工作台介绍',
						authority: ['shop', 'shopConfigView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(8)]).then(__webpack_require__.bind(null, "TlOf"));
					}
				}, {
					path: "createApplet",
					name: "createApplet",
					meta: {
						title: "申请小程序",
						help_title: '申请小程序介绍'
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(99)]).then(__webpack_require__.bind(null, "SHlR"));
					}
				}, {
					path: "setShopNotices",
					name: "setShopNotices",
					meta: {
						title: "店铺公告",
						help_title: '店铺公告介绍',
						help_url_key: "shopNoticesHelp",
						authority: ['shop', 'wechatShopNoticeView']
					},
					component: function component() {
						return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(109)]).then(__webpack_require__.bind(null, "QylT"));
					}
				}]
			}]
		}]
	},
	// 报表
	{
		path: "report",
		meta: {
			title: '报表',
			iconNavClass: "icon-report"
		},
		redirect: "noredirect",
		component: function component() {
			return __webpack_require__.e/* import() */(86).then(__webpack_require__.bind(null, "31uc"));
		},
		children: [{
			path: "clientActiveReport",
			name: "clientActiveReport",
			meta: {
				title: "客户活跃分析",
				help_title: '客户活跃介绍',
				help_url_key: "clientActiveReportHelp",
				authority: 'clientSaleStatisticsView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(76)]).then(__webpack_require__.bind(null, "iV3/"));
			}
		}, {
			path: "purchaseReport",
			name: "purchaseReport",
			meta: {
				title: "采购报表",
				help_title: '采购报表介绍',
				help_url_key: "purchaseReport",
				authority: 'purchaseReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(15)]).then(__webpack_require__.bind(null, "RkgD"));
			}
		}, {
			path: "saleReport",
			name: "saleReport",
			meta: {
				title: "销售报表",
				help_title: '销售报表介绍',
				help_url_key: "saleReport",
				authority: 'saleReportView'
			},
			component: function component() {
				// try {
				// 	let companyConfigList = store.getters.companyConfigList;
				// 	if (!companyConfigList) {
				// 		const res = await getCompanyConfigJson();
				// 		if (res.statusCode == 1 && res.object) {
				// 			store.dispatch("getCertificationInfo", res.object.company.comName);
				// 			store.commit("SET_COMPANY_CONFIG", res.object);
				// 		}
				// 	}
				// 	companyConfigList = store.getters.companyConfigList;
				// 	const saleReportNewObj = getObject(companyConfigList, "configKey", "saleReportNew");
				// 	if (saleReportNewObj) {
				// 		if (saleReportNewObj.configValue == 1) {
				// 			return import("@/views/report/sale/saleReportNew");
				// 		} else {
				// 			return import("@/views/report/sale/saleReport");
				// 		}
				// 	} else {
				// 		const cid = store.getters.cid;
				// 		if (cid && /[1-7]$/.test(String(cid))) {
				// 			return import("@/views/report/sale/saleReportNew");
				// 		} else {
				// 			return import("@/views/report/sale/saleReport");
				// 		}
				// 	}
				// } catch (error) {
				// 	return import("@/views/report/sale/saleReport");
				// }
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(12)]).then(__webpack_require__.bind(null, "zknr"));
			}
		}, {
			path: "trainReconciliation",
			name: "trainReconciliation",
			meta: {
				title: "车次对账"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(42)]).then(__webpack_require__.bind(null, "DYrw"));
			}
		}, {
			path: "clientSaleReport",
			name: "clientSaleReport",
			meta: {
				title: "客户销量",
				help_title: '客户销量排行介绍',
				help_url_key: "clientSaleReport",
				authority: 'clientSaleReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(106)]).then(__webpack_require__.bind(null, "KCCw"));
			}
		}, {
			path: "saleReportByGoods",
			name: "saleReportByGoods",
			meta: {
				title: "商品销量",
				help_title: '商品销量排行介绍',
				help_url_key: "saleReportByGoods",
				authority: 'goodsSaleReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(83)]).then(__webpack_require__.bind(null, "ibpP"));
			}
		}, {
			path: "storeReport",
			name: "storeReport",
			meta: {
				title: "盘点报表",
				help_title: '盘点报表介绍',
				help_url_key: "storeReport",
				authority: 'storeReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(49)]).then(__webpack_require__.bind(null, "PW0s"));
			}
		}, {
			path: "transfersReport",
			name: "transfersReport",
			meta: {
				title: "调拨报表",
				help_title: '调拨报表介绍',
				help_url_key: "transfersReport",
				authority: 'tranfersReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(60)]).then(__webpack_require__.bind(null, "qM1m"));
			}
		}, {
			path: "inStoreReport",
			name: "inStoreReport",
			meta: {
				title: "入库报表",
				help_title: '入库报表介绍',
				help_url_key: "inStoreReport",
				authority: 'inStoreReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(52)]).then(__webpack_require__.bind(null, "E3DN"));
			}
		}, {
			path: "outStoreReport",
			name: "outStoreReport",
			meta: {
				title: "出库报表",
				help_title: '出库报表介绍',
				help_url_key: "outStoreReport",
				authority: 'outStoreReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(41)]).then(__webpack_require__.bind(null, "y28J"));
			}
		}, {
			path: "achievementReport",
			name: "achievementReport",
			meta: {
				title: "业绩增长分析",
				help_title: '业绩增长分析介绍',
				help_url_key: "achievementReport",
				authority: 'achievementReportView'
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(29)]).then(__webpack_require__.bind(null, "Ll3d"));
			}
		}, {
			path: "reportExport",
			name: "reportExport",
			meta: {
				title: "报表导出页"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(39)]).then(__webpack_require__.bind(null, "DjLL"));
			}
		}]
	},
	// 仓库
	{
		path: "storehouse",
		meta: {
			title: '仓库',
			iconNavClass: "icon-storehouse"
		},
		redirect: "noredirect",
		component: function component() {
			return __webpack_require__.e/* import() */(103).then(__webpack_require__.bind(null, "uAmG"));
		},
		children: [
		// 仓库管理
		{
			path: "warehouse",
			name: "warehouse",
			meta: {
				title: "仓库管理",
				help_title: "仓库管理介绍",
				help_url_key: "storehouseList"
			},
			component: function component() {
				return __webpack_require__.e/* import() */(71).then(__webpack_require__.bind(null, "grNX"));
			}
		},
		// 顺誉库存查询
		{
			path: "syInventoryQuery",
			name: "syInventoryQuery",
			meta: {
				title: "顺誉库存查询"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(80)]).then(__webpack_require__.bind(null, "95zR"));
			}
		},
		// 库存流水
		{
			path: "goodsStoredRecord",
			name: "goodsStoredRecord",
			meta: {
				title: "库存流水",
				help_title: "库存流水介绍",
				help_url_key: "goodsStoredRecordList"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(27)]).then(__webpack_require__.bind(null, "iq4M"));
			}
		},
		// 批次查询
		{
			path: "batchQuery",
			name: "batchQuery",
			meta: {
				title: "批次查询",
				help_title: "批次查询介绍",
				help_url_key: "batchGoodsStoredListHelp"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(72)]).then(__webpack_require__.bind(null, "TRpK"));
			}
		},
		// 批次流水
		{
			path: "batchFlow",
			name: "batchFlow",
			meta: {
				title: "批次流水",
				help_title: "批次流水介绍",
				help_url_key: "batchGoodsStoredListHelp"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(73)]).then(__webpack_require__.bind(null, "oU6H"));
			}
		}, {
			path: "storageLocationManage",
			name: "storageLocationManage",
			meta: {
				title: "库位管理",
				help_title: "库位管理介绍",
				help_url_key: "storageLocationManageListHelp"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(40)]).then(__webpack_require__.bind(null, "SskK"));
			}
		}, {
			path: "handlingAbnormalReporting",
			name: "handlingAbnormalReporting",
			meta: {
				title: "异常提报处理"
			},
			component: function component() {
				return Promise.all/* import() */([__webpack_require__.e(0), __webpack_require__.e(57)]).then(__webpack_require__.bind(null, "moag"));
			}
		}, {
			path: "locationImport",
			name: "locationImport",
			meta: {
				title: "库位导入",
				help_title: "库位导入介绍",
				help_url_key: "storageLocationManageListHelp"
			},
			component: function component() {
				return __webpack_require__.e/* import() */(32).then(__webpack_require__.bind(null, "BKWX"));
			}
		}]
	},
	// 无页面菜单中转页
	{
		path: "emptypage",
		meta: {
			title: "跳转"
		},
		component: function component() {
			return __webpack_require__.e/* import() */(5/* duplicate */).then(__webpack_require__.bind(null, "WdZ/"));
		},
		children: [{
			path: "redirect",
			name: "redirect",
			meta: {
				title: "页面中转",
				help_title: "页面中转"
			},
			component: function component() {
				return __webpack_require__.e/* import() */(5/* duplicate */).then(__webpack_require__.bind(null, "WdZ/"));
			}
		}]
	}, {
		path: "sysProfessionPurches",
		name: "sysProfessionPurches",
		meta: {
			title: "版本、子账号购买续费",
			help_title: '版本、子账号购买续费'
		},
		component: function component() {
			return __webpack_require__.e/* import() */(62).then(__webpack_require__.bind(null, "MBxU"));
		}
	}]
}, { path: "*", redirect: "/404", hidden: true }];

/* harmony default export */ var router = __webpack_exports__["a"] = (new vue_router_esm["a" /* default */]({
	// mode: 'history', //后端支持可开
	scrollBehavior: function scrollBehavior() {
		return { y: 0 };
	},
	routes: constantRouterMap
}));

/***/ }),

/***/ "Yhou":
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__.p + "static/img/operate.393801b.png";

/***/ }),

/***/ "eEQt":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "i0am":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "jeTm":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "jwP4":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "k8iF":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony export (immutable) */ __webpack_exports__["getCommodityJSONList"] = getCommodityJSONList;
/* harmony export (immutable) */ __webpack_exports__["getCategoryList"] = getCategoryList;
/* harmony export (immutable) */ __webpack_exports__["getOneShopStyle"] = getOneShopStyle;
/* harmony export (immutable) */ __webpack_exports__["saveShopStyle"] = saveShopStyle;
/* harmony export (immutable) */ __webpack_exports__["getCommoditystByGoodsSns"] = getCommoditystByGoodsSns;
/* harmony export (immutable) */ __webpack_exports__["getCommoditystBySpuIds"] = getCommoditystBySpuIds;
/* harmony export (immutable) */ __webpack_exports__["getFunctionsState"] = getFunctionsState;
/* harmony export (immutable) */ __webpack_exports__["updateUseState"] = updateUseState;
/* harmony export (immutable) */ __webpack_exports__["getStyleJson"] = getStyleJson;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__service_request__ = __webpack_require__("R/2u");

// import qs from 'qs';

// 获取商品列表
function getCommodityJSONList(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/shop/wechat/commodity/commodityListJSON.ac?goodsUnion=y",
		method: "post",
		params: params
	});
}

// 获取分类列表
function getCategoryList() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/shop/wechat/commodity/getCategoryListForOnSale.ac',
		method: 'get'
	});
}

// 从oss获取一个样式文件
function getOneShopStyle(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/bms/gis/shopdecorate/style/getOneShopStyle.ac',
		method: 'post',
		params: params
	});
}

// 保存/更新样式json信息到oss
function saveShopStyle(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/bms/gis/shopdecorate/style/saveShopStyle.ac',
		method: 'post',
		data: data
	});
}

// 通过id组获得商品组信息
function getCommoditystByGoodsSns(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/shop/wechat/commodity/getCommoditystByGoodsSns.ac',
		method: 'post',
		data: data
	});
}

// 通过spuIds数组获得商品组信息
function getCommoditystBySpuIds(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/shop/wechat/commodity/getCommoditystBySpuIds.ac',
		method: 'post',
		data: data
	});
}

// 通过id组获得商品组信息
function getFunctionsState() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/shop/wechat/wechatShop/getFunctionsState.ac',
		method: 'post'
	});
}

// 更新样式使用状态
function updateUseState(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/bms/gis/shopdecorate/style/updateUseState.ac",
		method: "post",
		data: data
	});
}

// 获取json
function getStyleJson(url) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: url,
		withCredentials: false,
		method: "get"
	});
}

/***/ }),

/***/ "lHsg":
/***/ (function(module, exports) {

module.exports = "data:image/png;base64,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"

/***/ }),

/***/ "mGB5":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (immutable) */ __webpack_exports__["r"] = getSmsAccountInfo;
/* harmony export (immutable) */ __webpack_exports__["A"] = saveSmsAccountInfo;
/* harmony export (immutable) */ __webpack_exports__["n"] = getOwnAppIds;
/* harmony export (immutable) */ __webpack_exports__["g"] = getAllClientItems;
/* harmony export (immutable) */ __webpack_exports__["e"] = clientListConfigPageSizeJSON;
/* harmony export (immutable) */ __webpack_exports__["o"] = getRecentSmClientPhone;
/* harmony export (immutable) */ __webpack_exports__["s"] = getSmsBill;
/* harmony export (immutable) */ __webpack_exports__["u"] = getSmsBillForSearch;
/* harmony export (immutable) */ __webpack_exports__["D"] = userCategoryListJSON;
/* harmony export (immutable) */ __webpack_exports__["C"] = selectTemplateList;
/* harmony export (immutable) */ __webpack_exports__["x"] = getUserCategory;
/* harmony export (immutable) */ __webpack_exports__["B"] = saveUserCategory;
/* harmony export (immutable) */ __webpack_exports__["d"] = changeUsingState;
/* harmony export (immutable) */ __webpack_exports__["f"] = deleteCategoryTemplate;
/* harmony export (immutable) */ __webpack_exports__["h"] = getAllTemplateList;
/* harmony export (immutable) */ __webpack_exports__["p"] = getSchedulePlan;
/* harmony export (immutable) */ __webpack_exports__["q"] = getSchedulePlanDetail;
/* harmony export (immutable) */ __webpack_exports__["z"] = saveSchedulePlan;
/* harmony export (immutable) */ __webpack_exports__["c"] = cancelSchedulePlan;
/* harmony export (immutable) */ __webpack_exports__["w"] = getSuccessCountInDay;
/* harmony export (immutable) */ __webpack_exports__["j"] = getClientByClientItems;
/* harmony export (immutable) */ __webpack_exports__["a"] = applyForSmTemplate;
/* harmony export (immutable) */ __webpack_exports__["k"] = getExistTemplateByName;
/* harmony export (immutable) */ __webpack_exports__["v"] = getSmsSendBillCount;
/* harmony export (immutable) */ __webpack_exports__["t"] = getSmsBillDetail;
/* harmony export (immutable) */ __webpack_exports__["b"] = batchSendSms;
/* harmony export (immutable) */ __webpack_exports__["l"] = getListConfigJSONData;
/* harmony export (immutable) */ __webpack_exports__["i"] = getCategoryJSON;
/* harmony export (immutable) */ __webpack_exports__["m"] = getModuleVariJSON;
/* harmony export (immutable) */ __webpack_exports__["y"] = judgeOldSmsIsOpen;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__service_request__ = __webpack_require__("R/2u");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_qs__ = __webpack_require__("mw3O");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_qs___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_qs__);



// 获取短信服务账号信息
function getSmsAccountInfo() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/gis/getSmsAccountInfo.ac",
		method: "post",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		}
	});
}

// 保存短信服务账号信息
function saveSmsAccountInfo(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/gis/saveSmsAccountInfo.ac",
		method: "post",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		data: __WEBPACK_IMPORTED_MODULE_1_qs___default.a.stringify(data)
	});
}

// 获取用户是否开通某服务
function getOwnAppIds(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubmenu/getOwnAppIds.ac",
		method: "post",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		data: __WEBPACK_IMPORTED_MODULE_1_qs___default.a.stringify(data)
	});
}

// 获取客户分类列表
function getAllClientItems() {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/item/getAllClientItems.ac",
		method: "post"
	});
}

// 获取客户列表
function clientListConfigPageSizeJSON(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientListConfigPageSizeJSON.ac",
		method: "post",
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		data: __WEBPACK_IMPORTED_MODULE_1_qs___default.a.stringify(data)
	});
}

// 获取客户列表-过滤天数
function getRecentSmClientPhone(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/gis/getRecentSmClientPhone.ac",
		method: "post",
		params: data
	});
}

// 短信记录查询接口（不带客户信息、和查询结果的查询条件）
function getSmsBill(data, params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getSmsBill.ac",
		method: "post",
		data: data,
		params: params
	});
}

// 查询短信记录的第二个接口
function getSmsBillForSearch(data, params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getSmsBillForSearch.ac",
		method: "post",
		data: data,
		params: params
	});
}

// 获取所有短信分类信息
function userCategoryListJSON(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/userCategoryListJSON.ac",
		method: "post",
		data: data
	});
}

// 根据模块和分类查询所有短信模板(不分页)
function selectTemplateList(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/selectTemplateList.ac",
		method: "post",
		data: data
	});
}

// 获取某个短信分类信息
function getUserCategory(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getUserCategory.ac",
		method: "post",
		data: data
	});
}

// 保存短信分类信息
function saveUserCategory(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/saveUserCategory.ac",
		method: "post",
		data: data
	});
}

// 保存使用短信模版信息
function changeUsingState(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/changeUsingState.ac",
		method: "post",
		data: data
	});
}

// 删除某个短信模版
function deleteCategoryTemplate(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/deleteCategoryTemplate.ac",
		method: "post",
		data: data
	});
}

// 分页查询短信模板
function getAllTemplateList(data, params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getAllTemplateList.ac",
		method: "post",
		data: data,
		params: params
	});
}

// 获取定时任务列表
function getSchedulePlan(data, params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getSchedulePlan.ac",
		method: "post",
		data: data,
		params: params
	});
}

// 查看定时任务明细
function getSchedulePlanDetail(data, params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getSchedulePlanDetail.ac",
		method: "post",
		data: data,
		params: params
	});
}

// 保存定时发送任务
function saveSchedulePlan(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/saveSchedulePlan.ac",
		method: "post",
		data: data
	});
}

// 取消定时任务
function cancelSchedulePlan(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/cancelSchedulePlan.ac",
		method: "post",
		data: data
	});
}

// 查询当天短信成功发送的总数
function getSuccessCountInDay(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getSuccessCountInDay.ac",
		method: "post",
		data: data
	});
}

// 快速查询
function getClientByClientItems(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/getClientByClientItems.ac",
		method: "post",
		data: data
	});
}

// 新增/编辑模版
function applyForSmTemplate(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/applyForSmTemplate.ac",
		method: "post",
		data: data
	});
}

// 查询是否存在相同名称的模板
function getExistTemplateByName(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getExistTemplateByName.ac",
		method: "post",
		data: data
	});
}

// 获取发送记录的tag信息
function getSmsSendBillCount(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getSmsSendBillCount.ac",
		method: "post",
		data: data
	});
}

// 获取发送记录的详细信息
function getSmsBillDetail(data, params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/getSmsBillDetail.ac",
		method: "post",
		data: data,
		params: params
	});
}

// 立即发送短信信息
function batchSendSms(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/batchSendSms.ac",
		method: "post",
		data: data
	});
}

// 根据条件获取所有客户信息
function getListConfigJSONData(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/getListConfigJSONData.ac",
		method: "post",
		data: data
	});
}

// 获取短信分类列表
function getCategoryJSON(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: "./static/resource/json/constant.json",
		method: "get",
		data: data
	});
}

// 获取模块变量列表
function getModuleVariJSON(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: "./static/resource/json/module-variables.json",
		method: "get",
		data: data
	});
}

// 获取原短信模块是否开启
function judgeOldSmsIsOpen(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_0__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/sms/v2/gis/judgeOldSmsIsOpen.ac",
		method: "post",
		params: params
	});
}

/***/ }),

/***/ "oVfb":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_tim_js_sdk__ = __webpack_require__("B5T/");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_tim_js_sdk___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_tim_js_sdk__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_cos_js_sdk_v5__ = __webpack_require__("6qJD");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1_cos_js_sdk_v5___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_1_cos_js_sdk_v5__);


var tim = __WEBPACK_IMPORTED_MODULE_0_tim_js_sdk___default.a.create({
	SDKAppID: 1400053075
});
window.setLogLevel = tim.setLogLevel;

tim.registerPlugin({ "cos-js-sdk": __WEBPACK_IMPORTED_MODULE_1_cos_js_sdk_v5___default.a });
tim.setLogLevel(1);
/* harmony default export */ __webpack_exports__["a"] = (tim);

/***/ }),

/***/ "tvR6":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "uMhA":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ }),

/***/ "wjXq":
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* harmony export (immutable) */ __webpack_exports__["w"] = getClientItems;
/* harmony export (immutable) */ __webpack_exports__["o"] = clientListJSONWithTotalBalance;
/* harmony export (immutable) */ __webpack_exports__["n"] = clientListJSONExcludeTotalBalance;
/* harmony export (immutable) */ __webpack_exports__["q"] = clientTotalBalance;
/* harmony export (immutable) */ __webpack_exports__["l"] = clientGet;
/* harmony export (immutable) */ __webpack_exports__["G"] = targetInfoGet;
/* harmony export (immutable) */ __webpack_exports__["j"] = clientDeliveryGet;
/* harmony export (immutable) */ __webpack_exports__["i"] = clientDelete;
/* harmony export (immutable) */ __webpack_exports__["A"] = getPointRule;
/* harmony export (immutable) */ __webpack_exports__["a"] = allDeliveryCompanys;
/* harmony export (immutable) */ __webpack_exports__["H"] = targetInfoSaveOrUpdate;
/* harmony export (immutable) */ __webpack_exports__["k"] = clientDeliverySaveOrUpdate;
/* harmony export (immutable) */ __webpack_exports__["h"] = clientBaseInfoEdit;
/* harmony export (immutable) */ __webpack_exports__["g"] = clientBaseInfoAdd;
/* harmony export (immutable) */ __webpack_exports__["D"] = memberClientListJSON;
/* harmony export (immutable) */ __webpack_exports__["m"] = clientIsUnique;
/* harmony export (immutable) */ __webpack_exports__["t"] = deliveryCompanyListJSON;
/* harmony export (immutable) */ __webpack_exports__["u"] = deliveryCompanysSelectJSON;
/* harmony export (immutable) */ __webpack_exports__["e"] = changeBindMemberClient;
/* harmony export (immutable) */ __webpack_exports__["z"] = getMemberWithClientInfo;
/* harmony export (immutable) */ __webpack_exports__["p"] = clientPhoneIsUnique;
/* harmony export (immutable) */ __webpack_exports__["B"] = getSalerInfo;
/* harmony export (immutable) */ __webpack_exports__["C"] = getStoreInfo;
/* harmony export (immutable) */ __webpack_exports__["c"] = batchUpdateClientShopVisible;
/* harmony export (immutable) */ __webpack_exports__["d"] = batchUpdateClientTag;
/* harmony export (immutable) */ __webpack_exports__["b"] = batchUpdateClientItem;
/* harmony export (immutable) */ __webpack_exports__["v"] = getClientAlbumUploadUrl;
/* harmony export (immutable) */ __webpack_exports__["s"] = deleteClientAlbum;
/* harmony export (immutable) */ __webpack_exports__["r"] = deleteAvatar;
/* harmony export (immutable) */ __webpack_exports__["x"] = getClientMemberCard;
/* harmony export (immutable) */ __webpack_exports__["f"] = changeMemberCard;
/* harmony export (immutable) */ __webpack_exports__["y"] = getInvitationToTry;
/* harmony export (immutable) */ __webpack_exports__["F"] = saveUserCategoryForAllFreeSms;
/* harmony export (immutable) */ __webpack_exports__["E"] = outInvitationToTry;
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify__ = __webpack_require__("mvHQ");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify__);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__service_request__ = __webpack_require__("R/2u");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_querystring__ = __webpack_require__("1nuA");
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_2_querystring___default = __webpack_require__.n(__WEBPACK_IMPORTED_MODULE_2_querystring__);




// 获取所有客户分类
function getClientItems() {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/item/getAllClientItems.ac",
		method: "post"
	});
}
// 获取客户列表信息和价格
function clientListJSONWithTotalBalance(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientListJSONWithTotalBalance.ac",
		method: "get",
		params: params
	});
}
// 查询取客户列表信息
function clientListJSONExcludeTotalBalance(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientListJSONExcludeTotalBalance.ac",
		method: "get",
		params: params
	});
}
// 获取客户欠款
function clientTotalBalance(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientTotalBalance.ac",
		method: "get",
		params: params
	});
}

// 获取客户详情？id=3302297
function clientGet(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientGet.ac",
		method: "get",
		params: params
	});
}

// 获取客户昵称？clientId=3302297
function targetInfoGet(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/target/gis/targetInfoGet.ac",
		method: "get",
		params: params
	});
}

// 获取客户物流?clientId=3302297
function clientDeliveryGet(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/delivery/clientDeliveryGet.ac",
		method: "get",
		params: params
	});
}

// 删除客户id=3302297
function clientDelete(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientDelete.ac",
		method: "post",
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
		data: data
	});
}

// 获取客户积分
function getPointRule(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/item/getPointRule.ac",
		method: "post",
		params: params
	});
}

// 获取物流公司
function allDeliveryCompanys() {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/delivery/allDeliveryCompanys.ac",
		method: "post"
	});
}

// 保存客户昵称
function targetInfoSaveOrUpdate(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + "/push/mss/target/gis/targetInfoSaveOrUpdate.ac?",
		method: "post",
		headers: {
			'Content-Type': 'application/json'
		},
		data: __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify___default()(data)
	});
}

// 保存客户物流信息
function clientDeliverySaveOrUpdate(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/delivery/clientDeliverySaveOrUpdate.ac",
		method: "post",
		headers: {
			'Content-Type': 'application/json'
		},
		data: __WEBPACK_IMPORTED_MODULE_0_babel_runtime_core_js_json_stringify___default()(data)
	});
}

// 编辑保存客户信息
function clientBaseInfoEdit(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientBaseInfoEdit.ac",
		method: "post",
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
		data: __WEBPACK_IMPORTED_MODULE_2_querystring___default.a.stringify(data)
	});
}

// 新建保存客户信息
function clientBaseInfoAdd(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientBaseInfoAdd.ac",
		method: "post",
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
		data: __WEBPACK_IMPORTED_MODULE_2_querystring___default.a.stringify(data)
	});
}

// 查询会员列表
function memberClientListJSON(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/shop/wechat/memberclient/memberClientListJSON.ac",
		method: "post",
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded'
		},
		data: data
	});
}

// 查询客户名是否存在
function clientIsUnique(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientIsUnique.ac?",
		method: "post",
		params: params
	});
}

// 获取物流公司分页请求
function deliveryCompanyListJSON(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/delivery/getDeliveryCompanys.ac",
		method: "post",
		params: params
	});
}

// 获取物流公司分页请求
function deliveryCompanysSelectJSON(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/delivery/deliveryCompanysSelectJSON.ac",
		method: "post",
		params: params
	});
}

// 更换客户绑定会员
function changeBindMemberClient(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/shop/wechat/memberclient/changeBindMemberClient.ac",
		method: "post",
		params: params
	});
}

// 获取会员及客户绑定会员卡信息
function getMemberWithClientInfo(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/shop/wechat/member/getMemberWithClientInfo.ac",
		method: "get",
		params: params
	});
}

// 检查客户手机号码是否重复
function clientPhoneIsUnique(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/clientPhoneIsUnique.ac?",
		method: "post",
		params: params
	});
}

// 获取销售员信息
function getSalerInfo(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/pubuser/userSelectJSONFilterComStore.ac",
		method: "get",
		params: params
	});
}

// 获取门店信息
function getStoreInfo(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/comstore/comStoreSelectListJSON.ac",
		method: "get",
		params: params
	});
}

// 批量编辑客户访问商城权限
function batchUpdateClientShopVisible(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/batchUpdateClientShopVisible.ac",
		method: "post",
		data: data
	});
}

// 批量修改客户标签
function batchUpdateClientTag(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/batchUpdateClientTag.ac",
		method: "post",
		data: data
	});
}

// 批量编辑客户分类
function batchUpdateClientItem(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + "/admin/inner/client/batchUpdateClientItem.ac",
		method: "post",
		data: data
	});
}
// 客户附图上传
function getClientAlbumUploadUrl(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/file/img/getClientAlbumUploadUrl.ac',
		method: 'post',
		params: params
	});
}
// 从历史图库中删除客户附图
function deleteClientAlbum(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/inner/client/deleteClientAlbum.ac',
		method: 'post',
		data: data
	});
}
// 删除头像
function deleteAvatar(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/inner/client/deleteClientHeadImg.ac',
		method: 'post',
		data: data
	});
}

// 获取会员卡号信息
function getClientMemberCard(params) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/inner/client/member/card/getClientMemberCard.ac',
		method: 'post',
		params: params
	});
}

// 更换卡号
function changeMemberCard(data) {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.webServer + '/admin/inner/client/member/card/changeMemberCard.ac',
		method: 'post',
		data: data
	});
}

// 获取短信模板提示弹窗
function getInvitationToTry() {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/push/mss/sms/v2/gis/v2/invitationToTry.ac?scene=addClient',
		method: 'post'
	});
}

// 获取短信模板提示弹窗立即使用lient/clientEdit.vue
function saveUserCategoryForAllFreeSms() {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/push/mss/sms/v2/gis/saveUserCategoryForAllFreeSms.ac',
		method: 'post'
	});
}

// 获取短信模板提示弹窗立即使用
function outInvitationToTry() {
	return Object(__WEBPACK_IMPORTED_MODULE_1__service_request__["a" /* default */])({
		url: BASE_URL.cloudServer + '/push/mss/sms/v2/gis/v2/outInvitationToTry.ac?scene=addClient',
		method: 'post'
	});
}

/***/ }),

/***/ "yh13":
/***/ (function(module, exports) {

// removed by extract-text-webpack-plugin

/***/ })

},["NHnr"]);