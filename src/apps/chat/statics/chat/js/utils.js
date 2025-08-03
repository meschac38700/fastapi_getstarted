(()=> {
    function scrollToBottom(element){
        element.scrollTo(0, element.scrollHeight)
    }
    window.scrollToBottom = scrollToBottom
})()
