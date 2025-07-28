(function (){
    const roomConversationBaseURL = document.currentScript.dataset.roomConversation;

    console.log(roomConversationBaseURL)

    const roomConversation = document.getElementById("room-conversation");
    const roomsElements = document.querySelectorAll(".rooms .room");
    roomsElements.forEach(roomElement => {
        roomElement.addEventListener("click", async function(){
            if(this.classList.contains("active"))
                return;

            const roomID = this.dataset.id;
            const url = roomConversationBaseURL.replace("-1", roomID)
            const rooms = await fetchRoomMessages(url)

            const roomConversationContainer = document.getElementById("room-conversation")
            roomConversationContainer.innerHTML(renderRoomConversationHTML(rooms))

            toggleHTMLClass(roomElements, this)
        })
    })

    async function fetchRoomMessages(url){
        const response = await fetch(url)
        const roomMessages = await response.json()
        debugger
        return roomMessages.items
    }

    /**
    * @params {Object[]} rooms
    * @returns undefined
    **/
    function renderRoomConversationHTML(roomMessages){
        let previousAuthorId = ""
        let roomConversationHTML = ""
        roomMessages.forEach(roomMessage => {
            if(room.author_id !== previousAuthorId)
                 roomConversationHTML += `
                    <div class="message">
                        <div class="photo" style="background-image: url(https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80);">
                            <div class="online"></div>
                        </div>
                        <p class="text">{{ roomMessage.content }}</p>
                    </div>
                `
            else
                roomConversationHTML += `
                    <div class="message text-only">
                        <p class="text">{{ roomMessage.content }}</p>
                    </div>
                `
        })
        return roomConversationHTML
    }

    function toggleHTMLClass(roomElements, self){
        roomElements.forEach(room => {
            if(!roomElement.isEqualNode(self))
                roomElement.classList.remove("active");
        });
        this.classList.toggle('active');
        document.querySelector(".chat").classList.toggle("active");
    }


})()
