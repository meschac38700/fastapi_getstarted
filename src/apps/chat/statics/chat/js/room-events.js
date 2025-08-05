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

     async function handleClick(e){
        e.preventDefault();
        e.stopPropagation();

        if(this.classList.contains("active"))
            document.querySelector(".chat").classList.remove("active");
        else
            document.querySelector(".chat").classList.add("active");

        const show = toggleHTMLClass(roomElements, this)
        if(show){
            // update room name
            document.querySelector(".header-chat .name").innerText = this.dataset.name

            window.currentRoomId = this.dataset.id;
            const rooms = await fetchRoomMessages()

            renderRoomConversationHTML(rooms)
            switchWebSocketRoom()
            window.scrollToBottom(roomConversationContainer)
        }
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
    }
    window.addRoomListeners = addRoomListeners
})()
