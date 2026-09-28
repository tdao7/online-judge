/**
 * VCODER Design System — Live Contest Workspace Controller (Mockup docs/5.png)
 * Handles Ace editor, countdown timer, console tabs, and submission execution.
 */

(function () {
    'use strict';

    let editor = null;

    document.addEventListener('DOMContentLoaded', function () {
        initContestCountdown();
        initAceEditor();
        initConsoleTabs();
        initClarificationsToggle();
        initBookmarkStar();
    });

    /**
     * 1. Top Bar Contest Countdown Timer
     */
    function initContestCountdown() {
        const timerEl = document.getElementById('contest-countdown-display');
        if (!timerEl) return;

        const targetTimeStr = timerEl.getAttribute('data-target-time');
        if (!targetTimeStr) return;

        const targetDate = new Date(targetTimeStr).getTime();

        function updateCountdown() {
            const now = new Date().getTime();
            const diff = targetDate - now;

            if (diff <= 0) {
                timerEl.textContent = '00:00:00';
                return;
            }

            const totalHours = Math.floor(diff / (1000 * 60 * 60));
            const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const secs = Math.floor((diff % (1000 * 60)) / 1000);

            timerEl.textContent =
                String(totalHours).padStart(2, '0') + ':' +
                String(mins).padStart(2, '0') + ':' +
                String(secs).padStart(2, '0');
        }

        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    /**
     * 2. Ace Code Editor Setup
     */
    function initAceEditor() {
        const editorContainer = document.getElementById('contest-ace-editor');
        if (!editorContainer || typeof ace === 'undefined') return;

        editor = ace.edit('contest-ace-editor');
        editor.setTheme('ace/theme/textmate');
        editor.setFontSize(14);
        editor.setShowPrintMargin(false);
        editor.session.setTabSize(4);
        editor.session.setUseSoftTabs(true);

        const langSelect = document.getElementById('contest-language-select');
        const langInput = document.getElementById('form-language-input');
        const sourceTextarea = document.getElementById('form-source-textarea');
        const submitBtn = document.getElementById('btn-contest-submit');
        const submitForm = document.getElementById('contest-submit-form');

        const starterTemplates = {
            'c_cpp': `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // TODO: implement solution

    return 0;
}`,
            'python': `import sys

def main():
    input = sys.stdin.read
    # TODO: implement solution
    pass

if __name__ == '__main__':
    main()`,
            'java': `import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        // TODO: implement solution
    }
}`
        };

        function updateEditorMode() {
            if (!langSelect) return;
            const selectedOpt = langSelect.options[langSelect.selectedIndex];
            const aceMode = selectedOpt ? (selectedOpt.getAttribute('data-ace') || 'python') : 'python';
            editor.session.setMode('ace/mode/' + aceMode);

            if (langInput && selectedOpt) {
                langInput.value = selectedOpt.value;
            }

            // Restore from localStorage or set starter
            const storageKey = 'contest_code_' + window.location.pathname + '_' + (selectedOpt ? selectedOpt.value : 'default');
            const saved = localStorage.getItem(storageKey);
            if (saved) {
                editor.setValue(saved, -1);
            } else {
                const template = starterTemplates[aceMode] || starterTemplates['c_cpp'];
                editor.setValue(template, -1);
            }
        }

        if (langSelect) {
            updateEditorMode();
            langSelect.addEventListener('change', updateEditorMode);
        }

        // Autosave on change
        editor.on('change', function () {
            if (!langSelect) return;
            const selectedOpt = langSelect.options[langSelect.selectedIndex];
            const storageKey = 'contest_code_' + window.location.pathname + '_' + (selectedOpt ? selectedOpt.value : 'default');
            localStorage.setItem(storageKey, editor.getValue());
        });

        // Submit action
        function doSubmit() {
            if (!editor || !submitForm) return;
            const code = editor.getValue().trim();
            if (!code) {
                alert('Please write code before submitting.');
                return;
            }
            if (sourceTextarea) {
                sourceTextarea.value = code;
            }
            submitForm.submit();
        }

        if (submitBtn) {
            submitBtn.addEventListener('click', doSubmit);
        }

        // Keyboard Shortcut: Ctrl+Enter / Cmd+Enter
        editor.commands.addCommand({
            name: 'submitCode',
            bindKey: { win: 'Ctrl-Enter', mac: 'Command-Enter' },
            exec: function () {
                doSubmit();
            }
        });
    }

    /**
     * 3. Console Tabs Switching
     */
    function initConsoleTabs() {
        const drawer = document.getElementById('editor-console-drawer');
        if (!drawer) return;

        const tabButtons = drawer.querySelectorAll('.console-tab-item');
        const panels = drawer.querySelectorAll('.console-panel');

        tabButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                tabButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                const targetTab = this.getAttribute('data-tab');
                panels.forEach(p => {
                    if (p.id === 'panel-' + targetTab) {
                        p.style.display = '';
                        p.classList.add('active');
                    } else {
                        p.style.display = 'none';
                        p.classList.remove('active');
                    }
                });
            });
        });
    }

    /**
     * 4. Clarifications & Discussion Panel Toggle
     */
    function initClarificationsToggle() {
        const btnClarifications = document.getElementById('btn-tab-clarifications');
        const btnProblems = document.getElementById('btn-tab-problems');
        const panel = document.getElementById('contest-clarifications-panel');
        const workspaceMain = document.getElementById('contest-workspace-main');
        const btnClose = document.getElementById('btn-close-clarifications');

        if (!btnClarifications || !panel) return;

        btnClarifications.addEventListener('click', function () {
            panel.style.display = '';
            if (workspaceMain) workspaceMain.style.display = 'none';
            btnClarifications.classList.add('active');
            if (btnProblems) btnProblems.classList.remove('active');
        });

        function showWorkspace() {
            panel.style.display = 'none';
            if (workspaceMain) workspaceMain.style.display = '';
            if (btnProblems) btnProblems.classList.add('active');
            btnClarifications.classList.remove('active');
        }

        if (btnProblems) {
            btnProblems.addEventListener('click', showWorkspace);
        }
        if (btnClose) {
            btnClose.addEventListener('click', showWorkspace);
        }
    }

    /**
     * 5. Problem Bookmark Star Button
     */
    function initBookmarkStar() {
        const starBtn = document.getElementById('btn-star-bookmark');
        if (!starBtn) return;

        const storageKey = 'contest_bookmark_' + window.location.pathname + window.location.search;
        if (localStorage.getItem(storageKey) === 'true') {
            starBtn.classList.add('bookmarked');
            const icon = starBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-star-o');
                icon.classList.add('fa-star');
            }
        }

        starBtn.addEventListener('click', function () {
            const isBookmarked = this.classList.toggle('bookmarked');
            localStorage.setItem(storageKey, isBookmarked ? 'true' : 'false');
            const icon = this.querySelector('i');
            if (icon) {
                if (isBookmarked) {
                    icon.classList.remove('fa-star-o');
                    icon.classList.add('fa-star');
                } else {
                    icon.classList.remove('fa-star');
                    icon.classList.add('fa-star-o');
                }
            }
        });
    }

})();
