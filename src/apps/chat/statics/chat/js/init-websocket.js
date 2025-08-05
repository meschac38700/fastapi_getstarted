(() => {
    window.ws = null
    const wsURL = document.currentScript.dataset.wsUrl
    function initWSConnection(){
        window.ws = new WebSocket(wsURL)

        window.ws.onmessage = function (event) {
            const messages = document.getElementById("room-conversation")
            const message = window.createMessage(JSON.parse(JSON.parse(event.data)))
            messages.innerHTML += message
            window.scrollToBottom(messages)
        }
    }
    initWSConnection()
})()
