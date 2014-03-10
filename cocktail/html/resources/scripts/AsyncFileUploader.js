/*-----------------------------------------------------------------------------


@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2011
-----------------------------------------------------------------------------*/

cocktail.bind(".AsyncFileUploader", function ($asyncFileUploader) {

    $asyncFileUploader.find(".UploadInfo .remove_button").click(function () {
        jQuery(this).closest(".UploadInfo").remove();
    });
        
    var uploaderElement = cocktail.instantiate("cocktail.html.AsyncFileUploader.uploader");
    this.appendChild(uploaderElement);

    var $progressBar = $asyncFileUploader.find(".progress_bar");
    var $progressLabel = $asyncFileUploader.find(".progress_label");
        
    this.uploader = new qq.FileUploaderBasic({
        element: uploaderElement,
        action: this.asyncUploadUrl,
        name: "upload",
        multiple: false,
        button: $asyncFileUploader.find(".button").get(0),
        onSubmit: function () {
            $asyncFileUploader.addClass("uploading");
        },
        onProgress: function (id, fileName, loaded, total) {
            $asyncFileUploader.trigger("progres", {fileName: fileName, loaded: loaded, total: total});
            var percent = Math.round(loaded / total * 100) + "%";
            var size = $asyncFileUploader.get(0).uploader._formatSize(loaded);
            $progressBar.css("width", percent);
            $progressLabel.html(size + " (" + percent + ")");
        },
        onComplete: function (id, fileName, json) {
            $asyncFileUploader.removeClass("uploading");
            
            if (!$asyncFileUploader.get(0).multipleFiles) {
                $asyncFileUploader.find(".UploadInfo").remove();
            }

            $asyncFileUploader.get(0).addUpload(json);
        }
    });

    this.addUpload = function (upload) {
        var $uploadInfo = jQuery(cocktail.instantiate("cocktail.html.AsyncFileUploader.upload_info"))
            .appendTo($asyncFileUploader.find(".uploaded_files"));

        $uploadInfo.find(".file_name_label").html(upload.filename);
        $uploadInfo.find(".type_label").html(upload.type);
        $uploadInfo.find(".size_label").html(upload.size);

        $uploadInfo.find("input[type=hidden]")
            .val($asyncFileUploader.get(0).asyncPrefix + upload.id);

        $uploadInfo.find(".remove_button").click(function () {
            jQuery(this).closest(".UploadInfo").remove();
        });
    }

    if (this.uploads) {
        for (var i = 0; i < this.uploads.length; i++) {
            this.addUpload(this.uploads[i]);
        }
    }

    function hideDropAreas() {
        jQuery(document.body).removeClass("drag");
        jQuery(".AsyncFileUploader").removeClass("dragOver");
    }
    
    var uploader = this.uploader;

    var dz = new qq.UploadDropZone({
        element: jQuery(this).find(".drop_area").get(0),
        onEnter: function(e){
            $asyncFileUploader.addClass("dragOver");
            e.stopPropagation();
        },
        onLeave: function(e){
            e.stopPropagation();
        },
        onLeaveNotDescendants: function (e) {
            $asyncFileUploader.removeClass("dragOver");
        },
        onDrop: function (e) {
            hideDropAreas();
            uploader._uploadFileList(e.dataTransfer.files);
        }
    });

    qq.attach(document, "dragenter", function (e) {
        if (!dz._isValidFileDrag(e)) return;
        jQuery(document.body).addClass("drag");
    });

    qq.attach(document, "dragleave", function (e) {
        if (!dz._isValidFileDrag(e)) return;

        var relatedTarget = document.elementFromPoint(e.clientX, e.clientY);
        // only fire when leaving document out
        if (!relatedTarget || relatedTarget.nodeName == "HTML") {
            hideDropAreas();
        }
    });
});

