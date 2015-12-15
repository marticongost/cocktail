/*-----------------------------------------------------------------------------


@author:        Martí Congost
@contact:       marti.congost@whads.com
@organization:  Whads/Accent SL
@since:         December 2015
-----------------------------------------------------------------------------*/

(function () {

    cocktail.YouTubeUpload = function () {};

    cocktail.YouTubeUpload.prototype = {

        metadata: null,
        file: null,
        accessToken: null,
        videoId: null,
        processingStatus: null,
        uploadStatus: null,
        statusPollingInterval: 5000,
        uploadServiceURL: "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=PARTS",
        serviceURL: "https://www.googleapis.com/youtube/v3/videos",

        upload: function () {

            var upload = this;
            var parts = [];

            for (var key in this.metadata) {
                parts.push(key);
            }

            var url = this.uploadServiceURL.replace("PARTS", parts.join(","));

            jQuery.ajax({
                url: url,
                method: "POST",
                contentType: "application/json",
                headers: {
                    "Authorization": "Bearer " + this.accessToken,
                    "x-upload-content-length": this.file.size,
                    "x-upload-content-type": this.file.type
                },
                data: JSON.stringify(this.metadata)
            }).done(function (data, textStatus, xhr) {
                upload._resumableUpload({
                    url: xhr.getResponseHeader("Location"),
                    start: 0
                });
            });
        },

        _resumableUpload: function (params) {
            var upload = this;
            jQuery.ajax({
                url: params.url,
                method: "PUT",
                contentType: this.file.type,
                headers: {
                    "Content-Range": "bytes " + params.start + "-" + (this.file.size - 1) + "/" + this.file.size
                },
                xhr: function() {

                    var xhr = jQuery.ajaxSettings.xhr();

                    if (xhr.upload) {
                        xhr.upload.addEventListener("progress", function (e) {
                            if (e.lengthComputable) {
                                jQuery(upload).trigger({
                                    type: "progress",
                                    loaded: e.loaded,
                                    total: e.total
                                });
                            }
                        }, false);
                    }

                    return xhr;
                },
                processData: false,
                data: this.file
            })
                .done(function (response) {
                    upload.videoId = response.id;
                    jQuery(upload).trigger("uploadComplete");
                    upload._checkVideoStatus();
                })
                .fail(function () {
                    jQuery(upload).trigger("error");
                });
        },

        _checkVideoStatus: function () {

            var upload = this;

            jQuery.ajax({
                url: this.serviceURL,
                method: "GET",
                headers: {
                   Authorization: "Bearer " + upload.accessToken
                },
                data: {
                    part: "status,processingDetails",
                    id: upload.videoId
                }
            })
                .done(function (response) {
                    upload.processingStatus = response.items[0].processingDetails.processingStatus;
                    upload.uploadStatus = response.items[0].status.uploadStatus;

                    if (upload.processingStatus == "processing") {
                        setTimeout(
                            function () { upload._checkVideoStatus(); },
                            upload.statusPollingInterval
                        );
                    }
                    else if (upload.processingStatus == "succeeded") {
                        jQuery(upload).trigger("load");
                    }
                    else {
                        jQuery(upload).trigger("error");
                    }
                })
                .fail(function () {
                    jQuery(upload).trigger("error");
                });
        }
    }
})();

