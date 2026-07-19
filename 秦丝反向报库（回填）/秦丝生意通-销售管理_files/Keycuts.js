;(function (window, document) {
  if (!window || !document) return
  /**
   * mapping of special keycodes to their corresponding keys
   *
   * everything in this dictionary cannot use keypress events
   * so it has to be here to map to the correct keycodes for
   * keyup/keydown events
   *
   * @type {Object}
   */
  var _MAP = {
    8: 'backspace',
    9: 'tab',
    13: 'enter',
    16: 'shift',
    17: 'ctrl',
    18: 'alt',
    20: 'capslock',
    27: 'esc',
    32: 'space',
    33: 'pageup',
    34: 'pagedown',
    35: 'end',
    36: 'home',
    37: 'left',
    38: 'up',
    39: 'right',
    40: 'down',
    45: 'ins',
    46: 'del',
    91: 'meta',
    93: 'meta',
    224: 'meta',
  }
  /**
   * mapping for special characters so they can support
   *
   * this dictionary is only used incase you want to bind a
   * keyup or keydown event to one of these keys
   *
   * @type {Object}
   */
  var _KEYCODE_MAP = {
    106: '*',
    107: '+',
    109: '-',
    110: '.',
    111: '/',
    186: ';',
    187: '=',
    188: ',',
    189: '-',
    190: '.',
    191: '/',
    192: '`',
    219: '[',
    220: '\\',
    221: ']',
    222: "'",
  }
  /**
   * this is a list of special strings you can use to map
   * to modifier keys when you specify your keyboard shortcuts
   * this is a list of mac devices keypad trans
   * @type {Object}
   */
  var _SPECIAL_ALIASES = {
    option: 'alt',
    command: 'meta',
    return: 'enter',
    escape: 'esc',
    plus: '+',
    mod: /Mac|iPod|iPhone|iPad/.test(navigator.platform) ? 'meta' : 'ctrl',
  }
  /**
   * this is a mapping of keys that require shift on a US keypad
   * back to the non shift equivelents
   *
   * this is so you can use keyup events with these keys
   *
   * note that this will only work reliably on US keyboards
   *
   * @type {Object}
   */
  var _SHIFT_MAP = {
    '~': '`',
    '!': '1',
    '@': '2',
    '#': '3',
    $: '4',
    '%': '5',
    '^': '6',
    '&': '7',
    '*': '8',
    '(': '9',
    ')': '0',
    _: '-',
    '+': '=',
    ':': ';',
    '"': "'",
    '<': ',',
    '>': '.',
    '?': '/',
    '|': '\\',
  }
  /**
   * loop through the f keys, f1 to f19 and add them to the map
   * programatically
   */

  for (var i = 1; i < 20; ++i) {
    _MAP[111 + i] = 'f' + i
  }

  /**
   * takes a key event and figures out what the modifiers are
   *
   * @param {Event} e
   * @returns {Array}
   */
  function _eventModifiers(e) {
    var modifiers = []

    if (e.shiftKey) {
      modifiers.push('shift')
    }

    if (e.altKey) {
      modifiers.push('alt')
    }

    if (e.ctrlKey) {
      modifiers.push('ctrl')
    }

    if (e.metaKey) {
      modifiers.push('meta')
    }

    return modifiers
  }
  /**
   * determines if the keycode specified is a modifier key or not
   *
   * @param {string} key
   * @returns {boolean}
   */
  function _isModifier(key) {
    return key == 'shift' || key == 'ctrl' || key == 'alt' || key == 'meta'
  }
  /**
   * checks if two arrays are equal
   *
   * @param {Array} modifiers1
   * @param {Array} modifiers2
   * @returns {boolean}
   */
  function _modifiersMatch(modifiers1, modifiers2) {
    return modifiers1.sort().join(',') === modifiers2.sort().join(',')
  }

  Keycuts.prototype._parseKeysToKeyMap = function (combination, callback) {
    if (combination === '+') {
      return ['+']
    }

    var keys = combination.split('+')
    var key
    var modifiers = []
    for (var index = 0; index < keys.length; index++) {
      key = keys[index]
      if (_SPECIAL_ALIASES[key]) {
        key = _SPECIAL_ALIASES[key]
      }
      if (_SHIFT_MAP[key]) {
        modifiers.push('shift') // to press shift map
        key = _SHIFT_MAP[key]
      }
      if (_isModifier(key)) {
        modifiers.push(key) // tranform unicode
      }
    }

    if (!key) throw new Error('参数一输入格式有误')
    let hasBindKeyIndex = -1
    for (let index = 0; index < this._bindKeyArr.length; index++) {
      if (this._bindKeyArr[index].key == key) {
        hasBindKeyIndex = index
        break
      }
    }
    if(hasBindKeyIndex != -1) {
      this._bindKeyArr[hasBindKeyIndex] = {
        key: key,
        modifiers: modifiers,
        callback: callback,
        combination: combination,
      }
    } else {
      this._bindKeyArr.push({
        key: key,
        modifiers: modifiers,
        callback: callback,
        combination: combination,
      })
    }
  }

  Keycuts.prototype._getCharacterFromEvent = function (e) {
    if (typeof e.which !== 'number') {
      e.which = e.keyCode
    }
    var unicodeStr = e.which

    if (_MAP[unicodeStr]) {
      return _MAP[unicodeStr]
    }

    if (_KEYCODE_MAP[unicodeStr]) {
      return _KEYCODE_MAP[unicodeStr]
    }

    return String.fromCharCode(unicodeStr).toLowerCase()
  }

  Keycuts.prototype._eventHandler = function (e) {
    var character = this._getCharacterFromEvent(e)
    var modifiers = _eventModifiers(e)
    this._fireEvent(character, modifiers, e)
  }

  //  trigger event function
  Keycuts.prototype._fireEvent = function (char, modifiers, e) {
    for (var index = 0; index < this._bindKeyArr.length; index++) {
      var obj = this._bindKeyArr[index]
      if (_modifiersMatch(modifiers, obj.modifiers) && char === obj.key) {
        if (obj.callback(e, obj.combination) === false) {
          e.preventDefault()
          e.stopPropagation()
          return
        }
      }
    }
  }
  /**
   * 
   * @param {Array} queryArr ['mod+f', 'mod+g']
   */
  Keycuts.prototype.unBindElemsShortCuts = function (queryArr) {
    for (var index = 0; index < queryArr.length; index++) {
      this.unbindKey(queryArr[index])
    }
  }
  /**
   * 
   * @param {Array} elemProps  item { cmdStr: String, content?: String}
   * 
   */
  Keycuts.prototype.bindElemsShortCuts = function (elemProps) {
    if (Object.prototype.toString.call(elemProps) === '[object Array]') {
      for (var index = 0; index < elemProps.length; index++) {
        var elementPropsObj = elemProps[index];
        this._bindElemShortCuts(elementPropsObj.cmdStr, elementPropsObj.querySelect, elementPropsObj.content)
      }
    } else if (Object.prototype.toString.call(elemProps) === '[object Object]') {
      this._bindElemShortCuts(elemProps.cmdStr, elemProps.querySelect, elemProps.content)
    } else {
      throw new Error('参数非法，必须为对象或者数组!')
    }
  }

  Keycuts.prototype._bindElemShortCuts = function (cmdStr,querySelect, content) {
    var el = document.querySelector(querySelect)
    if (!el) {
      throw new Error(querySelect + "元素不存在")
    }
    if (content != null) {
      el.innerHTML = content
    }
    this.bindKey(cmdStr, function(){
      getComputedStyle(el).display != 'none' && el.click()
      return false;
    })
  }

  /**
   *
   * @param {string} cmdStr for example 'ctrl+k'
   * @param {function} callback
   */
  Keycuts.prototype.bindKey = function (cmdStr, callback) {
    if (!callback) throw new Error('参数二回调函数必须传入')
    this._parseKeysToKeyMap(cmdStr, callback) // {{ key: 'k', modifier: ['ctrl'], fn: callback, combination: 'ctrl+k'}}
  }

  Keycuts.prototype.unbindKey = function (cmdStr) {
    this.bindKey(cmdStr, function () {})
  }
  /**
   * expose startWith '_' function through this method
   */
  Keycuts.init = function () {
    var realKeyCutsObj = Keycuts()
    // method 方法必须要用返回闭包函数的形式， for循环同步代码跟回调函数用一起有坑..
    for (var method in realKeyCutsObj) {
    if (method.charAt(0) != '_') {
      Keycuts[method] = (function (method) {
        return function () {
          realKeyCutsObj[method].apply(
            realKeyCutsObj,
            Array.prototype.slice.call(arguments)
          )
        }
      })(method)
      }
    }
  }

  function Keycuts(targetElement) {
    var self = this
    targetElement = targetElement || document
    if (!(self instanceof Keycuts)) {
      return new Keycuts(targetElement)
    }
    self._bindKeyArr = []

    targetElement.addEventListener('keydown', self._eventHandler.bind(self))
  }

  Keycuts.init()

  if (typeof define === 'function' && define.amd) {
    // expose Keycuts as an AMD module
    define(function () {
      return Keycuts
    })
  } else if (typeof module !== 'undefined' && module.exports) {
    // expose as a common js module
    module.exports = Keycuts
  } else {
    // expose Keycuts to the global object
    window.Keycuts = Keycuts
  }
})(window, document)
