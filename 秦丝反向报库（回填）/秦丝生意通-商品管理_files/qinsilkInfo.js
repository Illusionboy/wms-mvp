var qinsilkCommonInfo={
	gisQqQun:"1063687438",//生意通交流群
	gisQqQunLink:'<a target="_blank" href="https://jq.qq.com/?_wv=1027&k=5KQhWsd">1063687438</a>',
	gisQqQunIcon:'<a target="_blank" href="https://jq.qq.com/?_wv=1027&k=5KQhWsd"><img border="0" src="//pub.idqqimg.com/wpa/images/group.png" alt="生意通经营管理群8" title="生意通经营管理群8"></a>',
	isQqQun:"1063701081",//进销存交流群
	isQqQunLink:'<a target="_blank" href="https://jq.qq.com/?_wv=1027&k=5J1MRsj">1063701081</a>',
	isQqQunIcon:'<a target="_blank" href="https://jq.qq.com/?_wv=1027&k=5J1MRsj"><img border="0" src="//pub.idqqimg.com/wpa/images/group.png" alt="秦丝进销存交流群8" title="秦丝进销存交流群8"></a>',
	csQQ:"2843487716",//客服qq
	csMailbox:"service@qinsilk.com",//客服邮箱
	csTelephone:"400-184-5682",//客服电话
	copyRightYear:"2014-2025",
	address:"深圳市南山区深圳湾科技生态园7栋B座西区15层"
}

function injectInnerHtmlByClass(vClass, vText) { //根据class获取元素
    var nodes = document.getElementsByClassName(vClass);
    for (i = 0; i < nodes.length; i++) {
    	 nodes[i].innerHTML = vText;
    }
}

for(var i in qinsilkCommonInfo){
	injectInnerHtmlByClass(i,qinsilkCommonInfo[i]);
}


