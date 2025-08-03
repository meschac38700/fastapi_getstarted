(() => {
    const wsURL = document.currentScript.dataset.wsUrl
    const currentUserId = +document.currentScript.dataset.currentUserId

    function createMessage(message){
        let msg = ""
        let msgClass = ""
        if (message.author_id === currentUserId)
            msgClass = "own"

        if (message.author_id !== window.lastMessageAuthor)
            msg = `
                <div class="message ${msgClass}">
                    <div class="photo" style="background-image: url(https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80);">
                        <div class="online"></div>
                    </div>
                    <p class="text">${ message.content }</p>
                </div>
            `
        else
            msg = `
                <div class="message text-only ${msgClass}">
                    <p class="text">${ message.content }</p>
                </div>
            `
        window.lastMessageAuthor = message.author_id
        return msg
    }

    window.createMessage = createMessage

    function initWSConnection(roomID){
        const WSUrl = wsURL.replace("/-1/", `/${roomID}/`)
        const ws = new WebSocket(WSUrl)

        ws.onmessage = function (event) {
            const messages = document.getElementById("room-conversation")
            const message = window.createMessage(JSON.parse(JSON.parse(event.data)))
            messages.innerHTML += message
            window.scrollToBottom(messages)
        }

        const form = document.getElementById("ws-form")
        form.addEventListener("submit", function(e){
            e.preventDefault()
            e.stopPropagation()

            const messageInput = this.querySelector("#message")
            const newMessage = messageInput.value.trim()
            if(newMessage)
                ws.send(newMessage)

            messageInput.value = ""
        })
    }
    window.initWSConnection = initWSConnection


})()
