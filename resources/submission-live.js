/**
 * VCODER macOS Design System — Screen 3: Live WebSocket Updates Engine
 * Milestone 4 — Real-time grading animations for Submissions Catalog & Detail Drawer
 * Mockup docs/3.png
 */
(function (window, document, $) {
  'use strict';

  var LiveGrading = {
    activeSecretReceiver: null,
    activeSubId: null,
    pollTimer: null,

    /**
     * Map DMOJ status/result codes to CSS verdict badge classes and display labels
     */
    verdictMap: {
      AC: { label: 'Accepted', cls: 'badge-verdict-ac', icon: 'fa-check' },
      WA: { label: 'Wrong Answer', cls: 'badge-verdict-wa', icon: 'fa-times' },
      TLE: { label: 'Time Limit Exceeded', cls: 'badge-verdict-tle', icon: 'fa-clock-o' },
      MLE: { label: 'Memory Limit Exceeded', cls: 'badge-verdict-mle', icon: 'fa-database' },
      OLE: { label: 'Output Limit Exceeded', cls: 'badge-verdict-ole', icon: 'fa-exclamation' },
      IR: { label: 'Invalid Return', cls: 'badge-verdict-rte', icon: 'fa-bolt' },
      RTE: { label: 'Runtime Error', cls: 'badge-verdict-rte', icon: 'fa-bolt' },
      CE: { label: 'Compilation Error', cls: 'badge-verdict-ce', icon: 'fa-exclamation-triangle' },
      IE: { label: 'Internal Error', cls: 'badge-verdict-ie', icon: 'fa-question-circle' },
      QU: { label: 'Queued', cls: 'badge-verdict-qu', icon: 'fa-hourglass-start' },
      P: { label: 'Processing', cls: 'badge-verdict-p', icon: 'fa-spinner fa-spin' },
      G: { label: 'Grading', cls: 'badge-verdict-g', icon: 'fa-circle-o-notch fa-spin' },
    },

    /**
     * 1. Update Submissions Catalog Table Row dynamically
     */
    updateTableRow: function (message) {
      var subId = message.id || message.submission;
      if (!subId) return;

      var selector = '[data-submission-id="' + subId + '"], #sub-' + subId + ', #' + subId;
      var row = document.querySelector(selector);
      if (!row) return;

      var verdictCell = row.querySelector('.col-verdict, .cell-verdict');
      if (!verdictCell) return;

      if (message.type === 'update-submission') {
        var state = message.state || message.status;
        if (state === 'processing' || state === 'P') {
          verdictCell.innerHTML =
            '<span class="badge-verdict badge-verdict-p">' +
              '<span class="spinner-dot" aria-hidden="true"></span> Processing' +
            '</span>';
        } else if (state === 'grading-begin' || state === 'G') {
          verdictCell.innerHTML =
            '<span class="badge-verdict badge-verdict-g">' +
              '<span class="pulse-dot" aria-hidden="true"></span> Grading...' +
            '</span>';
        } else if (state === 'test-case') {
          var caseNum = message.current_testcase || message.case || message.testcase;
          var label = caseNum ? 'Grading #' + caseNum : 'Grading...';
          verdictCell.innerHTML =
            '<span class="badge-verdict badge-verdict-g">' +
              '<span class="pulse-dot" aria-hidden="true"></span> ' + label +
            '</span>';
        }
      } else if (message.type === 'done-submission') {
        // Fetch fresh row snippet via AJAX single_submission endpoint
        if (window.jQuery && typeof window.jQuery.ajax === 'function') {
          window.jQuery.ajax({
            url: '/widgets/single_submission',
            data: { id: subId },
            success: function (html) {
              row.innerHTML = html;
              row.classList.add('row-just-finished');
              setTimeout(function () {
                row.classList.remove('row-just-finished');
              }, 2500);
            },
          });
        }
      }
    },

    /**
     * 2. Subscribe Detail Drawer to submission-specific WebSocket channel
     */
    subscribeDrawer: function (submissionId, idSecret) {
      var self = this;
      self.unsubscribeDrawer();
      self.activeSubId = submissionId;

      if (!idSecret) return;

      // Check if EventReceiver is available and daemon enabled
      if (typeof window.EventReceiver === 'function' && window.EVENT_DAEMON_LOCATION) {
        try {
          var channel = 'sub_' + idSecret;
          self.activeSecretReceiver = new window.EventReceiver(
            window.EVENT_DAEMON_LOCATION,
            window.EVENT_DAEMON_POLL_LOCATION || '/channels/',
            [channel],
            window.last_msg || 0,
            function (msg) {
              self.handleDrawerEvent(msg);
            }
          );
        } catch (e) {
          console.warn('[LiveGrading] WebSocket connection failed; activating polling fallback:', e);
          self.startPollingFallback(submissionId);
        }
      } else {
        // Start polling fallback if WebSocket is disabled
        self.startPollingFallback(submissionId);
      }
    },

    /**
     * 3. Handle live grading event inside open Detail Drawer
     */
    handleDrawerEvent: function (msg) {
      var self = this;
      if (!msg || !msg.type) return;

      var type = msg.type;
      var bannerEl = document.querySelector('.drawer-verdict-banner');
      var counterEl = document.getElementById('testcases-counter');

      switch (type) {
        case 'processing':
          if (bannerEl) {
            bannerEl.className = 'drawer-verdict-banner banner-processing';
            bannerEl.innerHTML =
              '<div class="banner-icon"><i class="fa fa-spinner fa-spin"></i></div>' +
              '<div class="banner-text">' +
                '<h3 class="banner-title">Processing</h3>' +
                '<p class="banner-subtext">Waiting for judge response...</p>' +
              '</div>';
          }
          break;

        case 'grading-begin':
          if (bannerEl) {
            bannerEl.className = 'drawer-verdict-banner banner-grading';
            bannerEl.innerHTML =
              '<div class="banner-icon"><i class="fa fa-circle-o-notch fa-spin"></i></div>' +
              '<div class="banner-text">' +
                '<h3 class="banner-title">Grading</h3>' +
                '<p class="banner-subtext">Evaluating test cases...</p>' +
              '</div>';
          }
          // Highlight first testcase dot
          self.setTestcaseEvaluating(1);
          break;

        case 'test-case':
          var caseId = msg.id || msg.case;
          if (caseId) {
            self.completeTestcaseDot(caseId);
            self.setTestcaseEvaluating(caseId + 1);
            if (counterEl) {
              counterEl.textContent = 'Grading #' + caseId + '...';
            }
          }
          break;

        case 'grading-end':
          self.finalizeDrawerGrading(msg);
          self.unsubscribeDrawer();
          break;

        case 'compile-error':
          if (bannerEl) {
            bannerEl.className = 'drawer-verdict-banner banner-ce';
            bannerEl.innerHTML =
              '<div class="banner-icon"><i class="fa fa-exclamation-triangle"></i></div>' +
              '<div class="banner-text">' +
                '<h3 class="banner-title">Compilation Error</h3>' +
                '<p class="banner-subtext">Source code failed to compile.</p>' +
              '</div>';
          }
          // Automatically switch to Compile Log tab
          self.activateCompileLog(msg.log);
          self.unsubscribeDrawer();
          break;

        case 'aborted':
        case 'internal-error':
          if (bannerEl) {
            bannerEl.className = 'drawer-verdict-banner banner-aborted';
            bannerEl.innerHTML =
              '<div class="banner-icon"><i class="fa fa-exclamation-circle"></i></div>' +
              '<div class="banner-text">' +
                '<h3 class="banner-title">' + (type === 'aborted' ? 'Aborted' : 'Internal Error') + '</h3>' +
                '<p class="banner-subtext">' + (type === 'aborted' ? 'Submission was cancelled.' : 'Judge server error.') + '</p>' +
              '</div>';
          }
          self.unsubscribeDrawer();
          break;
      }
    },

    /**
     * Mark testcase dot as currently evaluating (pulsing ring animation)
     */
    setTestcaseEvaluating: function (caseNum) {
      var dot = document.querySelector('.testcase-item[data-case-number="' + caseNum + '"]');
      if (dot) {
        dot.classList.add('evaluating');
      }
    },

    /**
     * Complete a testcase dot with pop-in scale animation
     */
    completeTestcaseDot: function (caseNum) {
      var dot = document.querySelector('.testcase-item[data-case-number="' + caseNum + '"]');
      if (dot) {
        dot.classList.remove('evaluating');
        dot.classList.add('pop-in');
        var badge = dot.querySelector('.testcase-badge');
        if (badge) {
          badge.classList.remove('testcase-pending');
          badge.classList.add('testcase-ac');
          badge.innerHTML =
            '<svg viewBox="0 0 20 20" fill="currentColor" class="badge-svg">' +
              '<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />' +
            '</svg>';
        }
        setTimeout(function () {
          dot.classList.remove('pop-in');
        }, 400);
      }
    },

    /**
     * Finalize drawer presentation upon grading-end
     */
    finalizeDrawerGrading: function (data) {
      // Re-fetch complete drawer content or apply metadata patch
      if (window.SubmissionDrawer && typeof window.SubmissionDrawer.open === 'function') {
        window.SubmissionDrawer.open(this.activeSubId);
      }
    },

    /**
     * Automatically switch to Compile Log tab and render compiler output
     */
    activateCompileLog: function (logText) {
      var compileTabBtn = document.getElementById('tab-compile-btn');
      if (compileTabBtn) {
        compileTabBtn.click();
      }
      var compilePre = document.querySelector('.compile-log-pre code');
      if (compilePre && logText) {
        compilePre.textContent = logText;
      }
    },

    /**
     * Polling fallback engine for environments without live WebSocket daemon
     */
    startPollingFallback: function (submissionId) {
      var self = this;
      self.stopPollingFallback();

      self.pollTimer = setInterval(function () {
        if (!self.activeSubId || self.activeSubId !== submissionId) {
          self.stopPollingFallback();
          return;
        }

        if (window.jQuery && typeof window.jQuery.ajax === 'function') {
          window.jQuery.ajax({
            url: '/widgets/submission_drawer',
            data: { id: submissionId, format: 'json' },
            dataType: 'json',
            success: function (data) {
              if (data && data.is_graded) {
                self.stopPollingFallback();
                if (window.SubmissionDrawer && typeof window.SubmissionDrawer.open === 'function') {
                  window.SubmissionDrawer.open(submissionId);
                }
              }
            },
            error: function () {
              self.stopPollingFallback();
            },
          });
        }
      }, 1500);
    },

    stopPollingFallback: function () {
      if (this.pollTimer) {
        clearInterval(this.pollTimer);
        this.pollTimer = null;
      }
    },

    unsubscribeDrawer: function () {
      this.stopPollingFallback();
      if (this.activeSecretReceiver) {
        if (this.activeSecretReceiver.websocket) {
          try {
            this.activeSecretReceiver.websocket.close();
          } catch (e) {}
        }
        this.activeSecretReceiver = null;
      }
      this.activeSubId = null;
    },
  };

  window.LiveGrading = LiveGrading;
})(window, document, window.jQuery || null);
