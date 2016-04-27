/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         April 2016
-----------------------------------------------------------------------------*/

cocktail.bind(".CodeEditor", function ($editor) {

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

