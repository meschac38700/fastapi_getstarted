(() => {
    const currentUserId = +document.currentScript.dataset.currentUserId
    window.lastMessageAuthor = null

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

    const form = document.getElementById("message-form")
    form.addEventListener("submit", function(e){
        e.preventDefault()
        e.stopPropagation()

        const messageInput = this.querySelector("#message")
        const newMessage = messageInput.value.trim()
        if(newMessage){
            const payload = {
                message: newMessage,
                action: "send",
                room_id: window.currentRoomId
            }
            window.ws.send(JSON.stringify(payload))
        }
        messageInput.value = ""
    })
})()
