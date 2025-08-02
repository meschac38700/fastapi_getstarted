(function (){
    const roomConversationBaseURL = document.currentScript.dataset.roomConversation;

    const roomElements = document.querySelectorAll(".rooms .room");
    roomElements.forEach(roomElement => {
        roomElement.addEventListener("click", async function(){
            if(this.classList.contains("active"))
                return;

            const roomID = this.dataset.id;
            const url = roomConversationBaseURL.replace("-1", roomID)
            const rooms = await fetchRoomMessages(url)

            const roomConversationContainer = document.getElementById("room-conversation")
            roomConversationContainer.innerHTML = renderRoomConversationHTML(rooms)

            toggleHTMLClass(roomElements, this)
            window.initWSConnection(roomID)
        })
    })

    async function fetchRoomMessages(url){
        const response = await fetch(url, {method: 'GET', credentials: "same-origin"})
        const roomMessages = await response.json()
        return roomMessages?.items
    }

    /**
    * @params {Object[]} rooms
    * @returns undefined
    **/
    function renderRoomConversationHTML(roomMessages){
        return roomMessages.map(roomMessage => window.createMessage(roomMessage)).join("")
    }

    function toggleHTMLClass(roomElements, self){
        roomElements.forEach(roomElement => {
            if(!roomElement.isEqualNode(self))
                roomElement.classList.remove("active");
        });
        self.classList.toggle('active');
        document.querySelector(".chat").classList.toggle("active");
    }
})()
