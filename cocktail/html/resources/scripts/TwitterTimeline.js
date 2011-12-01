/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".TwitterTimeline", function ($timeline) {
    
    this.loadTweets = function () {
        
        var $tweets = $timeline.find(".tweets");
        $tweets.hide();
        $tweets.empty();
        $timeline.addClass("loading");
        
        var url = "http://twitter.com/statuses/user_timeline/" + this.account + ".json?callback=?";

        jQuery.getJSON(url, {count: this.maxTweets}, function (tweets) {
            
            var timeline = $timeline.get(0);

            for (var i = 0; i < tweets.length; i++) {
                var entry = timeline.createEntry(tweets[i]);
                $tweets.append(entry);
            }
            
            $tweets.show();
            $timeline.removeClass("loading");
        });
    }

    this.createEntry = function (tweet) {

        var body = tweet.text;
        body = linkURLs(body);
        body = linkUsers(body);

        var relDate = relativeTime(tweet.created_at);

        var $entry = jQuery(cocktail.instantiate("cocktail.html.TwitterTimeline.entry"));
        $entry.find(".tweet_body").html(body);
        $entry.find(".tweet_date").html(relDate);
        return $entry;
    }

    var urlRegex = /((https?|s?ftp|ssh)\:\/\/[^"\s\<\>]*[^.,;'">\:\s\<\>\)\]\!])/g;

    function linkURLs(text) {
        return text.replace(urlRegex, function (url) {
            return '<a target="_blank" href="' + url + '">' + url + '</a>';
        });
    }

    var userRegex = /\B@([_a-z0-9]+)/ig;

    function linkUsers(text) {
        return text.replace(userRegex, function (user) {
            return user.charAt(0) + '<a class="userLink" target="_blank" href="http://twitter.com/' + user.substring(1) + '">' + user.substring(1) + '</a>';
        });
    }

    function relativeTime(time, base) {

        var base = base || new Date();        
        
        var values = time.split(" ");
        var parsedDate = Date.parse(
              values[1] + " " 
            + values[2] + ", " 
            + values[5] + " " 
            + values[3]
        );
        
        var delta = parseInt((base.getTime() - parsedDate) / 1000);
        delta = delta + base.getTimezoneOffset() * 60;

        if (delta < 60) {
            return cocktail.translate("cocktail.html.TwitterTimeline.seconds")
        }
        else if (delta < 120) {
            return cocktail.translate("cocktail.html.TwitterTimeline.minute")
        }
        else if (delta < 60 * 60) {
            return cocktail.translate("cocktail.html.TwitterTimeline.minutes", {
                minutes: parseInt(delta / 60)
            });
        }
        else if (delta < 120 * 60) {
            return cocktail.translate("cocktail.html.TwitterTimeline.hour");
        }
        else if (delta < 24 * 60 * 60) {
            return cocktail.translate("cocktail.html.TwitterTimeline.hours", {
                hours: parseInt(delta / 3600)
            });
        }
        else if (delta < 48 * 60 * 60) {
            return cocktail.translate("cocktail.html.TwitterTimeline.day");
        }
        else {
            return cocktail.translate("cocktail.html.TwitterTimeline.days", {
                days: parseInt(delta / 86400)
            });
        }
    }

    this.loadTweets();
});
