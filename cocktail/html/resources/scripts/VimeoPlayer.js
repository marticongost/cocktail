/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2012
-----------------------------------------------------------------------------*/

cocktail.bind(".VimeoPlayer.scriptable_video_player", function ($player) {
    
    var ctl = null;
    var playerReady = false;
    
    this.vimeoAPI = function (callback) {
        if (playerReady) {
            callback(ctl);
        }
        else {
            if (!ctl) {
                ctl = Froogaloop(this);
            }
            ctl.addEvent("ready", function () {
                playerReady = true;
                callback(ctl);
            });
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

