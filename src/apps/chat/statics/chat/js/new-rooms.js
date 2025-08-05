(() => {
    const currentScript = document.currentScript
    const apiURL = currentScript.dataset.apiUrl


    const roomForm = document.getElementById("new-room-form")

    const newRoomButton = document.getElementById("new-room")
    newRoomButton.addEventListener("click", function(e){
        e.preventDefault();
        e.stopPropagation();
        // show form
        roomForm.classList.add("active")
    })

    roomForm.addEventListener("reset", async function(e){
        this.classList.remove("active")
    })

    roomForm.addEventListener("submit", async function(e){
        e.preventDefault();
        e.stopPropagation();

        const roomName = this.querySelector("#room-name").value.trim()
        if (!roomName)
            return


        const submitter = this.querySelector("[type=submit]")
        const formData = new FormData(this, submitter)

        // normalize visibility value
        const visibilityValue = formData.get("visibility")?.toLowerCase() === "on"? "public": "private"
        formData.set("visibility", visibilityValue)

        const body = JSON.stringify(Object.fromEntries(formData.entries()))
        const response = await fetch(apiURL, {
            method: "POST",
            credentials: "same-origin",
            body,
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            }
        })
        const room = await response.json()
        // create new room HTML
        document.querySelector(".rooms").appendChild(createRoomHTML(room))
        // reset form and hide it
        this.reset()
        this.classList.remove("active")
    })

    /**
    * @params {String} dateTime
    **/
    function formatDatetime(dateTime){
        const currentDt = new Date(dateTime)
        const dtParts = currentDt.toISOString().split('T')
        const date = dtParts[0]
        const hours = dtParts[1].replace(/\.\w+/, "")
        return `${date} ${hours}`
    }

    function createRoomHTML(room){
        const roomHTML = document.createElement("DIV")
        roomHTML.setAttribute("class", "room")
        roomHTML.dataset.name = room.name
        roomHTML.dataset.id = room.id
        roomHTML.innerHTML =  `
            <div class="photo room-icon">
                <i class="fa-solid fa-users-viewfinder"></i>
            </div>
            <div class="desc-contact">
                <p class="name">${ room.name }</p>
                <p class="message"></p>
            </div>
            <div class="timer">${ formatDatetime(room.created_at) }</div>
            ${
                room.visibility === "public" ?
                '<i class="bi bi-unlock-fill visibility" title="This room is public"></i>':
                '<i class="bi bi-lock-fill visibility" title="This room is private"></i>'
            }
        `
        window.addRoomListeners(roomHTML)
        return roomHTML
    }
    window.createRoomHTML = createRoomHTML
})()
