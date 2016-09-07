/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2012
-----------------------------------------------------------------------------*/

cocktail.bind(".VimeoPlayer.scriptable_video_player", function ($player) {

    this.vimeoPlayer = new Vimeo.Player($player);

    this.play = function () {
        console.log("PLAY");
        this.vimeoPlayer.play();
    }

    this.pause = function () {
        this.vimeoPlayer.pause();
    }

    this.stop = function () {
        console.log("STOP");
        this.vimeoPlayer.setCurrentTime(0);
        this.vimeoPlayer.pause();
    }

    this.seekTo = function (seconds) {
        this.vimeoPlayer.setCurrentTime(seconds);
    }

    $player.on("playing", function () {
        $player.addClass("prevent_autoplay");
    });

    $player.on("ended", function () {
        $player.removeClass("prevent_autoplay");
    });
});

