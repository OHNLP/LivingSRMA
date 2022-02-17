function resize_iframe( iFrame ) {
    iFrame.height = iFrame.contentWindow.document.body.scrollHeight + "px";
    console.log('* resize iframe#'+iFrame.id+' height to ' + iFrame.height);
}

function resize_iframes() {
    $('iframe').each(function(idx) {
        if ($(this).is('[resize_by_content]')) {
            resize_iframe(this);
        }
    });
}