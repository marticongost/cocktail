/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2012
-----------------------------------------------------------------------------*/

cocktail.bind(".VimeoPlayer.scriptable_video_player", function ($player) {

    var playerReady = false;
    var ctl = Froogaloop(this);

    ctl.addEvent("ready", function () {

        ctl.addEvent("play", function () {
            $player.addClass("prevent_autoplay");
        });

        ctl.addEvent("finish", function () {
            $player.removeClass("prevent_autoplay");
        });

        playerReady = true;
        $player.trigger("playerReady");
    });

    this.vimeoAPI = function (callback) {
        if (playerReady) {
            callback(ctl);
        }
        else {
            $player.one("playerReady", function () { callback(ctl); });
        }
    }

    this.vimeoCommand = function () {
        var args = arguments;
        this.vimeoAPI(function (ctl) {
            ctl.api.apply(ctl, args);
        });
    }

    this.play = function () {
        this.vimeoCommand("play");
    }

    this.pause = function () {
        this.vimeoCommand("pause");
    }

    this.stop = function () {
        this.vimeoAPI(function (ctl) {
            ctl.api("seekTo", 0);
            ctl.api("pause");
        });
    }

    this.seekTo = function (seconds) {
        this.vimeoCommand("seekTo", seconds);
    }
});

