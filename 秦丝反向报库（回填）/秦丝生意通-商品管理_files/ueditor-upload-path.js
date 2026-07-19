/**
 * 修改文件上传路径
 * Date: 2014-4-29
 **/
window.UE.Editor.prototype._bkGetActionUrl = window.UE.Editor.prototype.getActionUrl;
window.UE.Editor.prototype.getActionUrl = function(action) {
	if (action == 'uploadimage' || action == 'uploadscrawl') {
		return BASE_URL.webServer + '/admin/file/img/uploadForUe.ac';
	} else if (action == 'listimage') {
		return BASE_URL.webServer + '/admin/file/img/listImgForUe.ac';
	} else {
		return this._bkGetActionUrl.call(this, action);
	}
};
