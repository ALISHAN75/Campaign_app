(function(factory) {
    'use strict';

    if (typeof define === 'function' && define.amd) {
        define(['jquery'], factory);
    } else if (typeof module === 'object' && typeof module.exports === 'object') {
        factory(require('jquery'));
    } else {
        factory(jQuery);
    }
})(function($) {

    'use strict';

    var defaults = {
        scrollStyle: 'scroll',
        onScrolled: function() {}
    };

    var methods = {
        init: function(options) {
            var settings = $.extend({}, defaults, options);
            return this.each(function() {
                var $this = $(this),
                    $wrap = $this.wrap('<div class=\"scrollWrap\"/>').closest('.scrollWrap');
                $this.addClass('scroll-content');
                $wrap.append('<div class="loader"></div>');
                $wrap.css({
                    'position': 'relative',
                    'height': settings.height ? (typeof settings.height === 'number' ? settings.height + 'px' : settings.height) : '100%',
                    'max-height': $this[0].scrollHeight + 'px',
                    'overflow-y': settings.scrollStyle
                });
                $wrap.scroll(function() {
                    // When we have scrolled to the bottom of our content, call the onScrolled handler.  We subtract a pixel below to account for rounding.
                    if ($wrap.scrollTop() >= $wrap[0].scrollHeight - $wrap.height() - 1) {
                        settings.onScrolled.call($this);
                    }
                });
            });
        },
        showLoader: function() {
            var $wrap = $(this).closest('.scrollWrap');
            $('.loader', $wrap).show();
            return this;
        },
        hideLoader: function() {
            var $wrap = $(this).closest('.scrollWrap');
            $('.loader', $wrap).hide();
            return this;
        },
        scrollTo: function(offset) {
            var $wrap = $(this).closest('.scrollWrap');
            $wrap.scrollTop(offset - $wrap.offset().top + $wrap.scrollTop());
            return this;
        }
    };

    $.fn.evScrollLoader = function(method) {
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        } else if (typeof method === 'object' || !method) {
            return methods.init.apply(this, arguments);
        }
    };

});
