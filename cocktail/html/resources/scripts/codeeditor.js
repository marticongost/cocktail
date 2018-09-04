/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".CodeEditor", function ($editor) {

    // Toggle fullscreen
    if (!this.codeMirrorSettings.extraKeys) {
        this.codeMirrorSettings.extraKeys = {};
    }

    if (!this.codeMirrorSettings.extraKeys.F11) {
        this.codeMirrorSettings.extraKeys.F11 = function (cm) {
            cm.setOption("fullScreen", !cm.getOption("fullScreen"));
        }
    }

    if (!this.codeMirrorSettings.extraKeys.Esc) {
        this.codeMirrorSettings.extraKeys.Esc = function (cm) {
            if (cm.getOption("fullScreen")) {
                cm.setOption("fullScreen", false);
            }
        }
    }

    // Initialize CodeMirror
    var $container = $editor.parent();
    var editor = CodeMirror.fromTextArea(this, this.codeMirrorSettings);

    // Fix a bug in CodeMirror that prevents the editor from displaying its
    // contents until focused if it starts out hidden.
    (function refresh() {
        if ($container.is(":visible")) {
            editor.refresh();
        }
        else {
            setTimeout(function () {
                refresh();
            }, 50);
        }
    })();
});

