function _createForOfIteratorHelper(o) { if (typeof Symbol === "undefined" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (o = _unsupportedIterableToArray(o))) { var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var it, normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it.return != null) it.return(); } finally { if (didErr) throw err; } } }; }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(n); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && Symbol.iterator in Object(iter)) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _objectWithoutProperties(source, excluded) { if (source == null) return {}; var target = _objectWithoutPropertiesLoose(source, excluded); var key, i; if (Object.getOwnPropertySymbols) { var sourceSymbolKeys = Object.getOwnPropertySymbols(source); for (i = 0; i < sourceSymbolKeys.length; i++) { key = sourceSymbolKeys[i]; if (excluded.indexOf(key) >= 0) continue; if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue; target[key] = source[key]; } } return target; }

function _objectWithoutPropertiesLoose(source, excluded) { if (source == null) return {}; var target = {}; var sourceKeys = Object.keys(source); var key, i; for (i = 0; i < sourceKeys.length; i++) { key = sourceKeys[i]; if (excluded.indexOf(key) >= 0) continue; target[key] = source[key]; } return target; }
window.addressJson = window.addressJson || [];
// 获取省会
function getProvinces(addressJson) {
  var provinces = addressJson.reduce(function (per, cur) {
    var children = cur.children,
        others = _objectWithoutProperties(cur, ["children"]);
  
    return per.concat(others);
  }, []);
  return provinces;
}
// 获取城市
function getCities(addressJson) {
  var cities = addressJson.reduce(function (per, cur) {
    return per.concat(cur.children ? cur.children.map(function (_ref) {
      var children = _ref.children,
          others = _objectWithoutProperties(_ref, ["children"]);
  
      return { ...others,
        provinceCode: cur.code
      };
    }) : []);
  }, []);
  return cities;
}
// 获取地区
function getAreas(addressJson) {
  var areas = addressJson.reduce(function (per, cur) {
    var provinceCode = cur.code;
    return per.concat(cur.children ? cur.children.reduce(function (p, c) {
      var cityCode = c.code;
      return p.concat(c.children ? c.children.map(function (_ref2) {
        var children = _ref2.children,
            others = _objectWithoutProperties(_ref2, ["children"]);
  
        return { ...others,
          cityCode: cityCode,
          provinceCode: provinceCode
        };
      }) : []);
    }, []) : []);
  }, []);
  return areas
}
/**
 * 需要解析的地址，type是解析的方式，默认是正则匹配
 * @param address
 * @param options?：type： 0:正则，1：树查找, textFilter： 清洗的字段
 * @returns {{}|({area: Array, province: Array, phone: string, city: Array, name: string, detail: Array} & {area: (*|string), province: (*|string), city: (*|string), detail: (Array|boolean|string|string)})}
 * @constructor
 */

var AddressParse = function AddressParse(address, options) {
  var _ref3 = _typeof(options) === 'object' ? options : typeof options === 'number' ? {
    type: options
  } : {},
      _ref3$type = _ref3.type,
      type = _ref3$type === void 0 ? 0 : _ref3$type,
      _ref3$textFilter = _ref3.textFilter,
      textFilter = _ref3$textFilter === void 0 ? [] : _ref3$textFilter,
      _ref3$nameMaxLength = _ref3.nameMaxLength,
      nameMaxLength = _ref3$nameMaxLength === void 0 ? 4 : _ref3$nameMaxLength;

  if (!address) {
    return {};
  }

  var parseResult = {
    phone: '',
    province: [],
    city: [],
    area: [],
    detail: [],
    name: ''
  };
  address = cleanAddress(address, textFilter);

  var resultPhone = filterPhone(address);
  address = resultPhone.address;
  parseResult.phone = resultPhone.phone;
  var resultCode = filterPostalCode(address);
  address = resultCode.address;
  parseResult.postalCode = resultCode.postalCode;

  var splitAddress = address.split(' ').filter(function (item) {
    return item;
  }).map(function (item) {
    return item.trim();
  });
  var d1 = new Date().getTime(); // 找省市区和详细地址

  splitAddress.forEach(function (item, index) {
    // 识别地址
    if (!parseResult.province[0] || !parseResult.city[0] || !parseResult.area[0]) {
      // 两个方法都可以解析，正则和树查找
      var parse = {};
      type === 1 && (parse = parseRegion(item, parseResult));
      type === 0 && (parse = parseRegionWithRegexp(item, parseResult));
      var _parse = parse,
          _province = _parse.province,
          _city = _parse.city,
          _area = _parse.area,
          _detail = _parse.detail;
      parseResult.province = _province || [];
      parseResult.area = _area || [];
      parseResult.city = _city || [];
      parseResult.detail = parseResult.detail.concat(_detail || []);
    } else {
      parseResult.detail.push(item);
    }
  });
  var d2 = new Date().getTime();
  var province = parseResult.province[0];
  var city = parseResult.city[0];
  var area = parseResult.area[0];
  var detail = parseResult.detail; // 地址都解析完了，姓名应该是在详细地址里面

  if (detail && detail.length > 0) {
    var copyDetail = _toConsumableArray(detail);

    copyDetail.sort(function (a, b) {
      return a.length - b.length;
    });

    var index = copyDetail.findIndex(function (item) {
      return judgeFragmentIsName(item, nameMaxLength);
    });
    var name = '';

    if (index !== -1) {
      name = copyDetail[index];
    } else if (copyDetail[0].length <= nameMaxLength && /[\u4E00-\u9FA5]/.test(copyDetail[0])) {
      name = copyDetail[0];
    } // 找到了名字就从详细地址里面删除它


    if (name) {
      parseResult.name = name;
      detail.splice(detail.findIndex(function (item) {
        return item === name;
      }), 1);
    }
  }

  return Object.assign(parseResult, {
    province: province && province.name || '',
    city: city && city.name || '',
    area: area && area.name || '',
    detail: detail && detail.length > 0 && detail.join('') || ''
  });
};
/**
 * 利用正则表达式解析
 * @param fragment
 * @param hasParseResult
 * @returns {{area: (Array|*|string), province: (Array|*|string), city: (Array|*|string|string), detail: (*|Array)}}
 */


var parseRegionWithRegexp = function parseRegionWithRegexp(fragment, hasParseResult) {
  var provinceString = JSON.stringify(getProvinces(window.addressJson));
  var cityString = JSON.stringify(getCities(window.addressJson));
  var areaString = JSON.stringify(getAreas(window.addressJson));
  var province = hasParseResult.province || [],
      city = hasParseResult.city || [],
      area = hasParseResult.area || [],
      detail = [];
  var matchStr = '';

  if (province.length === 0) {
    for (var i = 1; i < fragment.length; i++) {
      var str = fragment.substring(0, i + 1);
      var regexProvince = new RegExp("{\"code\":\"[0-9]{1,6}\",\"name\":\"".concat(str, "[\u4E00-\u9FA5]*?\"}"), 'g');
      var matchProvince = provinceString.match(regexProvince);

      if (matchProvince) {
        var provinceObj = JSON.parse(matchProvince[0]);

        if (matchProvince.length === 1) {
          province = [];
          matchStr = str;
          province.push(provinceObj);
        }
      } else {
        break;
      }
    }

    if (province[0]) {
      fragment = fragment.replace(new RegExp(matchStr, 'g'), '');
    }
  }

  if (city.length === 0) {
    for (var _i = 1; _i < fragment.length; _i++) {
      var _str = fragment.substring(0, _i + 1);

      var regexCity = new RegExp("{\"code\":\"[0-9]{1,6}\",\"name\":\"".concat(_str, "[\u4E00-\u9FA5]*?\",\"provinceCode\":\"").concat(province[0] ? "".concat(province[0].code) : '[0-9]{1,6}', "\"}"), 'g');
      var matchCity = cityString.match(regexCity);

      if (matchCity) {
        var cityObj = JSON.parse(matchCity[0]);

        if (matchCity.length === 1) {
          city = [];
          matchStr = _str;
          city.push(cityObj);
        }
      } else {
        break;
      }
    }

    if (city[0]) {
      var provinceCode = city[0].provinceCode;
      fragment = fragment.replace(new RegExp(matchStr, 'g'), '');

      if (province.length === 0) {
        var _regexProvince = new RegExp("{\"code\":\"".concat(provinceCode, "\",\"name\":\"[\u4E00-\u9FA5]+?\"}"), 'g');

        var _matchProvince = provinceString.match(_regexProvince);

        province.push(JSON.parse(_matchProvince[0]));
      }
    }
  }

  if (area.length === 0) {
    for (var _i2 = 1; _i2 < fragment.length; _i2++) {
      var _str2 = fragment.substring(0, _i2 + 1);

      var regexArea = new RegExp("{\"code\":\"[0-9]{1,6}\",\"name\":\"".concat(_str2, "[\u4E00-\u9FA5]*?\",\"cityCode\":\"").concat(city[0] ? city[0].code : '[0-9]{1,6}', "\",\"provinceCode\":\"").concat(province[0] ? "".concat(province[0].code) : '[0-9]{1,6}', "\"}"), 'g');
      var matchArea = areaString.match(regexArea);

      if (matchArea) {
        var areaObj = JSON.parse(matchArea[0]);

        if (matchArea.length === 1) {
          area = [];
          matchStr = _str2;
          area.push(areaObj);
        }
      } else {
        break;
      }
    }

    if (area[0]) {
      var _area$ = area[0],
          _provinceCode = _area$.provinceCode,
          cityCode = _area$.cityCode;
      fragment = fragment.replace(matchStr, '');

      if (province.length === 0) {
        var _regexProvince2 = new RegExp("{\"code\":\"".concat(_provinceCode, "\",\"name\":\"[\u4E00-\u9FA5]+?\"}"), 'g');

        var _matchProvince2 = provinceString.match(_regexProvince2);

        province.push(JSON.parse(_matchProvince2[0]));
      }

      if (city.length === 0) {
        var _regexCity = new RegExp("{\"code\":\"".concat(cityCode, "\",\"name\":\"[\u4E00-\u9FA5]+?\",\"provinceCode\":\"").concat(_provinceCode, "\"}"), 'g');

        var _matchCity = cityString.match(_regexCity);

        city.push(JSON.parse(_matchCity[0]));
      }
    }
  } // 解析完省市区如果还存在地址，则默认为详细地址


  if (fragment.length > 0) {
    detail.push(fragment);
  }

  return {
    province: province,
    city: city,
    area: area,
    detail: detail
  };
};
/**
 * 利用树向下查找解析
 * @param fragment
 * @param hasParseResult
 * @returns {{area: Array, province: Array, city: Array, detail: Array}}
 */


var parseRegion = function parseRegion(fragment, hasParseResult) {
  var provinces = getProvinces(window.addressJson)
  var cities = getCities(window.addressJson)
  var areas = getAreas(window.addressJson);
  var province = [],
      city = [],
      area = [],
      detail = [];

  if (hasParseResult.province[0]) {
    province = hasParseResult.province;
  } else {
    // 从省开始查找
    var _iterator = _createForOfIteratorHelper(provinces),
        _step;

    try {
      for (_iterator.s(); !(_step = _iterator.n()).done;) {
        var tempProvince = _step.value;
        var name = tempProvince.name;
        var replaceName = '';

        for (var i = name.length; i > 1; i--) {
          var temp = name.substring(0, i);

          if (fragment.indexOf(temp) === 0) {
            replaceName = temp;
            break;
          }
        }

        if (replaceName) {
          province.push(tempProvince);
          fragment = fragment.replace(new RegExp(replaceName, 'g'), '');
          break;
        }
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
  }

  if (hasParseResult.city[0]) {
    city = hasParseResult.city;
  } else {
    // 从市区开始查找
    var _iterator2 = _createForOfIteratorHelper(cities),
        _step2;

    try {
      var _loop = function _loop() {
        var tempCity = _step2.value;
        var name = tempCity.name,
            provinceCode = tempCity.provinceCode;
        var currentProvince = province[0]; // 有省

        if (currentProvince) {
          if (currentProvince.code === provinceCode) {
            var _replaceName = '';

            for (var _i3 = name.length; _i3 > 1; _i3--) {
              var _temp = name.substring(0, _i3);

              if (fragment.indexOf(_temp) === 0) {
                _replaceName = _temp;
                break;
              }
            }

            if (_replaceName) {
              city.push(tempCity);
              fragment = fragment.replace(new RegExp(_replaceName, 'g'), '');
              return "break";
            }
          }
        } else {
          // 没有省，市不可能重名
          for (var _i4 = name.length; _i4 > 1; _i4--) {
            var _replaceName2 = name.substring(0, _i4);

            if (fragment.indexOf(_replaceName2) === 0) {
              city.push(tempCity);
              province.push(provinces.find(function (item) {
                return item.code === provinceCode;
              }));
              fragment = fragment.replace(_replaceName2, '');
              break;
            }
          }

          if (city.length > 0) {
            return "break";
          }
        }
      };

      for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
        var _ret = _loop();

        if (_ret === "break") break;
      }
    } catch (err) {
      _iterator2.e(err);
    } finally {
      _iterator2.f();
    }
  } // 从区市县开始查找


  var _iterator3 = _createForOfIteratorHelper(areas),
      _step3;

  try {
    var _loop2 = function _loop2() {
      var tempArea = _step3.value;
      var name = tempArea.name,
          provinceCode = tempArea.provinceCode,
          cityCode = tempArea.cityCode;
      var currentProvince = province[0];
      var currentCity = city[0]; // 有省或者市

      if (currentProvince || currentCity) {
        if (currentProvince && currentProvince.code === provinceCode || (currentCity && currentCity.code) === cityCode) {
          var _replaceName3 = '';

          for (var _i5 = name.length; _i5 > 1; _i5--) {
            var _temp2 = name.substring(0, _i5);

            if (fragment.indexOf(_temp2) === 0) {
              _replaceName3 = _temp2;
              break;
            }
          }

          if (_replaceName3) {
            area.push(tempArea);
            !currentCity && city.push(cities.find(function (item) {
              return item.code === cityCode;
            }));
            !currentProvince && province.push(provinces.find(function (item) {
              return item.code === provinceCode;
            }));
            fragment = fragment.replace(_replaceName3, '');
            return "break";
          }
        }
      } else {
        // 没有省市，区县市有可能重名，这里暂时不处理，因为概率极低，可以根据添加市解决
        for (var _i6 = name.length; _i6 > 1; _i6--) {
          var _replaceName4 = name.substring(0, _i6);

          if (fragment.indexOf(_replaceName4) === 0) {
            area.push(tempArea);
            city.push(cities.find(function (item) {
              return item.code === cityCode;
            }));
            province.push(provinces.find(function (item) {
              return item.code === provinceCode;
            }));
            fragment = fragment.replace(_replaceName4, '');
            break;
          }
        }

        if (area.length > 0) {
          return "break";
        }
      }
    };

    for (_iterator3.s(); !(_step3 = _iterator3.n()).done;) {
      var _ret2 = _loop2();

      if (_ret2 === "break") break;
    } // 解析完省市区如果还存在地址，则默认为详细地址

  } catch (err) {
    _iterator3.e(err);
  } finally {
    _iterator3.f();
  }

  if (fragment.length > 0) {
    detail.push(fragment);
  }

  return {
    province: province,
    city: city,
    area: area,
    detail: detail
  };
};
/**
 * 判断是否是名字
 * @param fragment
 * @returns {string}
 */


var judgeFragmentIsName = function judgeFragmentIsName(fragment, nameMaxLength) {
  if (!fragment || !/[\u4E00-\u9FA5]/.test(fragment)) {
    return '';
  } // 如果包含下列称呼，则认为是名字，可自行添加


  var nameCall = ['先生', '小姐', '同志', '哥哥', '姐姐', '妹妹', '弟弟', '妈妈', '爸爸', '爷爷', '奶奶', '姑姑', '舅舅'];

  if (nameCall.find(function (item) {
    return fragment.indexOf(item) !== -1;
  })) {
    return fragment;
  } // 如果百家姓里面能找到这个姓，并且长度在1-5之间


  var nameFirst = fragment.substring(0, 1);

  if (fragment.length <= nameMaxLength && fragment.length > 1 && zhCnNames.indexOf(nameFirst) !== -1) {
    return fragment;
  }

  return '';
};
/**
 * 匹配电话
 * @param address
 * @returns {{address: *, phone: string}}
 */


var filterPhone = function filterPhone(address) {
  var phone = ''; // 整理电话格式

  address = address.replace(/(\d{3})-(\d{4})-(\d{4})/g, '$1$2$3');
  address = address.replace(/(\d{3}) (\d{4}) (\d{4})/g, '$1$2$3');
  address = address.replace(/(\d{4}) \d{4} \d{4}/g, '$1$2$3');
  address = address.replace(/(\d{4})/g, '$1');
  var mobileReg = /(\d{7,12})|(\d{3,4}-\d{6,8})|(86-[1][0-9]{10})|(86[1][0-9]{10})|([1][0-9]{10})/g;
  var mobile = mobileReg.exec(address);

  if (mobile) {
    phone = mobile[0];
    address = address.replace(mobile[0], ' ');
  }

  return {
    address: address,
    phone: phone
  };
};
/**
 * 匹配邮编
 * @param address
 * @returns {{address: *, postalCode: string}}
 */


var filterPostalCode = function filterPostalCode(address) {
  var postalCode = '';
  var postalCodeReg = /\d{6}/g;
  var code = postalCodeReg.exec(address);

  if (code) {
    postalCode = code[0];
    address = address.replace(code[0], ' ');
  }

  return {
    address: address,
    postalCode: postalCode
  };
};
/**
 * 地址清洗
 * @param address
 * @returns {*}
 */


var cleanAddress = function cleanAddress(address) {
  var textFilter = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
  // 去换行等
  address = address.replace(/\r\n/g, ' ').replace(/\n/g, ' ').replace(/\t/g, ' '); // 自定义去除关键字，可自行添加

  var search = ['详细地址', '收货地址', '收件地址', '地址', '所在地区', '地区', '姓名', '收货人', '收件人', '联系人', '收', '邮编', '联系电话', '电话', '联系人手机号码', '手机号码', '手机号'].concat(textFilter);
  search.forEach(function (str) {
    address = address.replace(new RegExp(str, 'g'), ' ');
  });
  var pattern = new RegExp("[`~!@#$^&*()=|{}':;',\\[\\]\.<>/?~！@#￥……&*（）——|{}【】‘；：”“’。，、？]", 'g');
  address = address.replace(pattern, ' '); // 多个空格replace为一个

  address = address.replace(/ {2,}/g, ' ');
  return address;
};