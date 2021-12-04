function nodeListToArray(nodelist) {
    return Array.prototype.slice.call(nodelist)
}


function sendClickEvent(el) {
    let clickEvent = document.createEvent('HTMLEvents');
    clickEvent.initEvent('click', true, false);
    el.dispatchEvent(clickEvent);
};


function getElementWidth(el) {
    const positionInfo = el.getBoundingClientRect();
    return positionInfo.width;
}


function getElementHeight(el) {
    const positionInfo = el.getBoundingClientRect();
    return positionInfo.height;
}


function getLeftPadding(el) {
    return parseFloat(getComputedStyle(el, null).getPropertyValue('padding-left').replace("px", ""));
}


function getRightPadding(el) {
    return parseFloat(getComputedStyle(el, null).getPropertyValue('padding-right').replace("px", ""));
}


function getLeftMargin(el) {
    return parseFloat(getComputedStyle(el, null).getPropertyValue('margin-left').replace("px", ""));
}


function getRightMargin(el) {
    return parseFloat(getComputedStyle(el, null).getPropertyValue('margin-right').replace("px", ""));
}


// Возвращает функцию, которая не будет срабатывать, пока продолжает вызываться.
// Она сработает только один раз через N миллисекунд после последнего вызова.
// Если ей передан аргумент `immediate`, то она будет вызвана один раз сразу после
// первого запуска.
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};


function drawPrice(source, withRuble=true) {
    let intPrice = parseInt(Math.floor(source));
    let residue = Math.round((parseFloat(source) - intPrice) * 100);
    let strPrice = intPrice.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");

    let priceData = {
        'source': source,
        'intValue': intPrice,
        'intResidue': residue,
        'strResidue': residue.toString().length == 1 && '0' + residue.toString() || residue.toString(),
        'digits': strPrice.split(' ')
    }

    priceData.intResidue = priceData.intValue >= 1000 && 0 || priceData.intResidue;

    let digitCount = priceData.digits.length;
    let result = '';

    priceData.digits.forEach(function (value, index) {
        let counter = index + 1;
        let className = 'price-row__digit price-row__digit_' + counter;

        if (counter == digitCount) {
            className += ' price-row__digit_last';

            if (priceData.intResidue > 0) {
                className += ' price-row__digit_before-cents';
            } else {
                className += ' price-row__digit_before-ruble';
            }
        }

        result += '<span class="' + className + '">' + value + '</span>';
    });

    if (priceData.intResidue > 0) {
        result += '<span class="price-row__digit price-row__digit_cents price-row__digit_before-ruble">,' + priceData.strResidue + '</span>';
    }

    if (withRuble) {
        result += '<span class="price-row__ruble">₽</span>';
    }

    return '<span class="price-row">' + result + '</span>';
}