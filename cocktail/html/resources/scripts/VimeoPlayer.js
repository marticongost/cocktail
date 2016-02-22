/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2012
-----------------------------------------------------------------------------*/

(function () {

    jQuery(window).on("message", function (e) {

        e = e.originalEvent;

        try {
            var data = JSON.parse(e.data);
            var messageType = data.event || data.method;
        }
        catch (error)  {}

        if (!(/^https?:\/\/player.vimeo.com/).test(e.origin)) {
            return false;
        }

        var $player = jQuery("#" + data.player_id);

        if (messageType == "ready") {
            if (!$player.data("vimeoPlayerReady")) {
                $player
                    .data("vimeoPlayerReady", true)
                    .trigger("playerReady");
            }
            else {
                return false;
            }
        }
        else if (messageType == "play") {
            $player.trigger("playing");
        }
        else if (messageType == "pause") {
            $player.trigger("pause");
        }
        else if (messageType == "finish") {
            $player.trigger("ended");
        }
    });
})();

cocktail.bind(".VimeoPlayer.scriptable_video_player", function ($player) {

    cocktail.requireId(this);

    $player.on("playerReady", function () {
        postMessage("addEventListener", "play");
        postMessage("addEventListener", "pause");
        postMessage("addEventListener", "finish");
    });

    $player.on("playing", function () {
        $player.addClass("prevent_autoplay");
    });

    $player.on("ended", function () {
        $player.removeClass("prevent_autoplay");
    });

    function whenPlayerReady(callback) {
        if ($player.data("vimeoPlayerReady")) {
            callback();
        }
        else {
            $player.one("playerReady", callback);
        }
    }

    function postMessage(method, value /* = null */) {
        var data = JSON.stringify({
            method: method,
            value: value === undefined ? null : value
        });
        $player[0].contentWindow.postMessage(data, "*");
    }

    this.play = function () {
        whenPlayerReady(function () { postMessage("play"); });
    }

    this.pause = function () {
        whenPlayerReady(function () { postMessage("pause"); });
    }

    this.stop = function () {
        whenPlayerReady(function () {
            postMessage("seekTo", 0);
            postMessage("pause");
        });
    }

    this.seekTo = function (seconds) {
        whenPlayerReady(function () {
            postMessage("seekTo", seconds);
        });
    }
});

