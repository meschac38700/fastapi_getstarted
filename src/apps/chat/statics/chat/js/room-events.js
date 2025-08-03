(function (){
    const roomConversationBaseURL = document.currentScript.dataset.roomConversation;
    const roomConversationContainer = document.getElementById("room-conversation")

    const roomElements = document.querySelectorAll(".rooms .room");
    roomElements.forEach(roomElement => {
        addRoomListeners(roomElement)
    })

    async function fetchRoomMessages(roomID){
        const url = roomConversationBaseURL.replace("-1", roomID)
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
        self.classList.toggle('active');

    }

     async function handleClick(e){
        e.preventDefault();
        e.stopPropagation();
        if(this.classList.contains("active"))
            document.querySelector(".chat").classList.remove("active");
        else
            document.querySelector(".chat").classList.add("active");

        if(!this.classList.contains("active")){
            const roomID = this.dataset.id;
            const rooms = await fetchRoomMessages(roomID)

            renderRoomConversationHTML(rooms)
            window.initWSConnection(roomID)
            window.scrollToBottom(roomConversationContainer)
        }
        toggleHTMLClass(roomElements, this)
    }

    function addRoomListeners(roomHTMLElement){
        roomHTMLElement.addEventListener("click", handleClick)
    }
    window.initEvents = addRoomListeners
})()
