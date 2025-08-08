(function (){
    const roomConversationBaseURL = document.currentScript.dataset.roomConversation;
    const roomConversationContainer = document.getElementById("room-conversation")

    const roomElements = document.querySelectorAll(".rooms .room");
    roomElements.forEach(roomElement => {
        addRoomListeners(roomElement)
    })

    async function fetchRoomMessages(){
        const url = roomConversationBaseURL.replace("-1", window.currentRoomId)
        const response = await fetch(url, {method: 'GET', credentials: "same-origin"})
        const roomMessages = await response.json()

        if(response.status === 403){
            roomConversationContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                  ${roomMessages.detail}
                </div>
            `
        }

        return roomMessages?.items
    }

    /**
    * @params {Object[]} roomMessages
    * @returns undefined
    **/
    function renderRoomConversationHTML(roomMessages){
        roomConversationContainer.innerHTML = roomMessages.map(
            roomMessage => window.createMessage(roomMessage)
        ).join("")
    }
    function toggleHTMLClass(roomElements, self){
        roomElements.forEach(roomElement => {
            if(!roomElement.isEqualNode(self))
                roomElement.classList.remove("active");
        });
        return self.classList.toggle('active');
    }

    function getToken(form){
        const metaCSRFToken = document.querySelector("meta[name=csrf_token]").getAttribute("content")
        const inputCSRFToken = form.querySelector("input[name=csrf_token]")?.value
        return inputCSRFToken || metaCSRFToken
    }
    window.showLoader = function(parentElement){
        parentElement.innerHTML= `<div class="loader"></div>`
    }
    async function handleClick(e){
        e.preventDefault();
        e.stopPropagation();

        if(this.classList.contains("active"))
            document.querySelector(".chat").classList.remove("active");
        else
            document.querySelector(".chat").classList.add("active");

        const show = toggleHTMLClass(roomElements, this)
        if(show){
            window.lastMessageAuthor = null
            window.showLoader(roomConversationContainer)
            // update room name
            document.querySelector(".header-chat .name").innerText = this.dataset.name

            window.currentRoomId = this.dataset.id;
            const rooms = await fetchRoomMessages()

            if (!rooms) return

            if(!rooms.length){
                roomConversationContainer.innerHTML = `
                    <div class="alert alert-warning" role="alert">
                        No content to show
                    </div>
                `
            }else
                renderRoomConversationHTML(rooms)

            switchWebSocketRoom()
            window.scrollToBottom(roomConversationContainer)
        }
    }
    async function handleDelete(roomHTMLElement){
        const formElement = roomHTMLElement.querySelector("#room-delete-form")
        if (!formElement) // the current user is not allowed to delete this room
            return

        const submitButton = formElement.querySelector("[type=submit]")

        // Show confirmation modal
        const url = formElement.getAttribute("action")
        submitButton.addEventListener("click", async (e) => {
            e.preventDefault()
            e.stopPropagation()

            if (!confirm("Are you sure?"))
                window.location.reload()

            const response = await fetch(url, {
                method: "DELETE",
                credentials: "same-origin",
                headers: {
                    Accept: "application/json",
                    "Content-Type": "application/json",
                    "X-CSRF-Token": getToken(formElement),
                }
            })

            if(response.status !== 204){
                // Show alert message
                console.log(response)
            }
            // Reload the page to renew the csrf token
            window.location.reload()
        })

    }
    async function handleRoomSubscription(roomHTMLElement){
        const formElement = roomHTMLElement.querySelector("#room-subscription-form")
        if( !formElement ) // the current user is already member of this room or admin or owner
            return

        const subscriptionURL = formElement.getAttribute("action")

        const submitButton = formElement.querySelector("[type=submit]")
        submitButton.addEventListener("click", async (e) => {
            e.preventDefault()
            e.stopPropagation()

            const response = await fetch(subscriptionURL, {
                method: "PATCH",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": getToken(formElement)
                }
            })

            if(response.status !== 200) // show error message
                console.log(response)

            // show success message
            window.location.reload()

        })
    }

    /**
    * Switch subscription to another room, let's the server manage cancel and new subscription.
    **/
    function switchWebSocketRoom(){
        const payload = {
            action: "change_room",
            room_id: window.currentRoomId
        }
        window.ws.send(JSON.stringify(payload))
    }

    function addRoomListeners(roomHTMLElement){
        roomHTMLElement.addEventListener("click", handleClick)
        handleDelete(roomHTMLElement)
        handleRoomSubscription(roomHTMLElement)
    }
    window.addRoomListeners = addRoomListeners
})()
