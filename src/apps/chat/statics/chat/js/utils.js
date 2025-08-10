(()=> {
    function scrollToBottom(element){
        element.scrollTo(0, element.scrollHeight)
    }
    window.scrollToBottom = scrollToBottom
    function stripHtml(html)
    {
       let tmp = document.createElement("DIV");
       tmp.innerHTML = html;
       return tmp.textContent || tmp.innerText || "";
    }
    window.stripHtml = stripHtml
})()
