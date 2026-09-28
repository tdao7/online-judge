/**
 * VCODER Online Judge — Problem Statement Progressive Enhancements
 * Milestone 3: KaTeX Math, Sample I/O Card Parsing, Copy Clipboard & Bookmark
 */
(function ($) {
    'use strict';

    window.problemSamples = [];

    /**
     * Escape raw HTML helper
     */
    function escapeHtml(str) {
        return (str || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Copy text to clipboard with fallback
     */
    function copyTextToClipboard(text, callback) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(function () {
                if (callback) callback(true);
            }).catch(function () {
                fallbackCopy(text, callback);
            });
        } else {
            fallbackCopy(text, callback);
        }
    }

    function fallbackCopy(text, callback) {
        var textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            var successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            if (callback) callback(successful);
        } catch (err) {
            document.body.removeChild(textArea);
            if (callback) callback(false);
        }
    }

    /**
     * Progressively transforms standard DMOJ markdown sample headings + code blocks
     * into modern macOS sample cards with one-click copy buttons and visual feedback.
     */
    function enhanceSampleTestcases(containerSelector) {
        var $root = $(containerSelector || '#statement-content');
        if (!$root.length) $root = $('#statement-pane');
        var samplesMap = {};

        $root.find('h1, h2, h3, h4, h5, h6').each(function () {
            var $heading = $(this);
            var text = $heading.text().trim();
            var inMatch = text.match(/Sample\s+Input\s*(\d*)/i);
            var outMatch = text.match(/Sample\s+Output\s*(\d*)/i);

            if (inMatch || outMatch) {
                var isInput = !!inMatch;
                var sampleNum = (inMatch ? inMatch[1] : outMatch[1]) || '1';
                var label = isInput ? ('Sample Input ' + sampleNum).trim() : ('Sample Output ' + sampleNum).trim();

                var $next = $heading.next();
                var $pre = null;
                if ($next.is('pre')) {
                    $pre = $next;
                } else if ($next.find('pre').length) {
                    $pre = $next.find('pre').first();
                }

                if ($pre && $pre.length) {
                    var codeText = $pre.find('code').length ? $pre.find('code').text() : $pre.text();
                    var cardId = 'sample-' + (isInput ? 'in' : 'out') + '-' + sampleNum + '-' + Math.random().toString(36).substr(2, 5);

                    // Track sample pairs for test runner
                    if (!samplesMap[sampleNum]) samplesMap[sampleNum] = { num: sampleNum, input: '', output: '' };
                    if (isInput) samplesMap[sampleNum].input = codeText;
                    else samplesMap[sampleNum].output = codeText;

                    var $card = $(
                        '<div class="sample-testcase-card ' + (isInput ? 'sample-input-card' : 'sample-output-card') + '">' +
                            '<div class="sample-card-header">' +
                                '<span class="sample-card-title">' + escapeHtml(label) + '</span>' +
                                '<button type="button" class="sample-copy-btn" data-clipboard-target="#' + cardId + '" aria-label="Copy ' + escapeHtml(label) + '">' +
                                    '<i class="fa fa-clone copy-icon" aria-hidden="true"></i>' +
                                    '<span class="copy-text">Copy</span>' +
                                '</button>' +
                            '</div>' +
                            '<div class="sample-card-body">' +
                                '<pre id="' + cardId + '" class="sample-box-code"><code>' + escapeHtml(codeText) + '</code></pre>' +
                            '</div>' +
                        '</div>'
                    );

                    $card.insertAfter($heading);
                    $pre.remove();
                    $heading.remove();
                }
            }
        });

        // Store structured samples for the Right Pane test runner
        window.problemSamples = Object.keys(samplesMap).sort(function (a, b) {
            return parseInt(a, 10) - parseInt(b, 10);
        }).map(function (k) {
            return samplesMap[k];
        });

        // Trigger an event so the test runner can update its cards if desired
        $(document).trigger('problem_samples_ready', [window.problemSamples]);
    }

    /**
     * Bind Copy Button Visual Feedback
     */
    function initCopyButtons() {
        $(document).on('click', '.sample-copy-btn', function (e) {
            e.preventDefault();
            var $btn = $(this);
            var targetId = $btn.data('clipboard-target');
            var text = '';

            if (targetId && $(targetId).length) {
                text = $(targetId).text();
            } else {
                text = $btn.closest('.sample-testcase-card').find('.sample-box-code').text();
            }

            copyTextToClipboard(text, function (success) {
                if (success) {
                    var originalHtml = $btn.html();
                    $btn.addClass('copied');
                    $btn.html('<i class="fa fa-check" aria-hidden="true"></i> <span class="copy-text">Copied!</span>');

                    setTimeout(function () {
                        $btn.removeClass('copied');
                        $btn.html(originalHtml);
                    }, 2000);
                }
            });
        });
    }

    /**
     * Bookmark Toggle Handler in Header
     */
    function initBookmark() {
        var key = 'vcoder_bookmarked_problems';
        var $star = $('#problem-bookmark-star');
        if (!$star.length) return;

        var code = $star.data('problem-code');
        var bookmarks = JSON.parse(localStorage.getItem(key) || '[]');

        if (bookmarks.indexOf(code) !== -1) {
            $star.addClass('active').find('i').removeClass('fa-star-o').addClass('fa-star');
        }

        $star.on('click', function () {
            bookmarks = JSON.parse(localStorage.getItem(key) || '[]');
            var idx = bookmarks.indexOf(code);
            if (idx !== -1) {
                bookmarks.splice(idx, 1);
                $star.removeClass('active').find('i').removeClass('fa-star').addClass('fa-star-o');
            } else {
                bookmarks.push(code);
                $star.addClass('active').find('i').removeClass('fa-star-o').addClass('fa-star');
            }
            localStorage.setItem(key, JSON.stringify(bookmarks));
        });
    }

    /**
     * Tab Switcher (Statement vs Comments Drawer)
     */
    function initTabs() {
        $('#tab-statement').on('click', function () {
            $('.statement-tab-item').removeClass('active');
            $(this).addClass('active');
            $('#panel-statement').show();
            $('#panel-comments').hide();
        });

        $('#tab-comments').on('click', function () {
            $('.statement-tab-item').removeClass('active');
            $(this).addClass('active');
            $('#panel-statement').hide();
            $('#panel-comments').show();
        });

        $('#btn-close-comments').on('click', function () {
            $('#tab-statement').trigger('click');
        });
    }

    /**
     * KaTeX Math rendering with auto-render delimiters
     */
    function initKaTeXMath() {
        if (typeof renderMathInElement === 'function') {
            var target = document.getElementById('statement-pane') || document.body;
            renderMathInElement(target, {
                delimiters: [
                    { left: "$$", right: "$$", display: true },
                    { left: "\\[", right: "\\]", display: true },
                    { left: "$", right: "$", display: false },
                    { left: "\\(", right: "\\)", display: false },
                    { left: "~", right: "~", display: false }
                ],
                ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
                ignoredClasses: ["ace_editor", "sample-box-code"],
                throwOnError: false
            });
        }
    }

    // Auto-initialize on DOM Ready
    $(function () {
        initKaTeXMath();
        enhanceSampleTestcases('#statement-content');
        initCopyButtons();
        initBookmark();
        initTabs();
    });

})(window.jQuery || window.$);
