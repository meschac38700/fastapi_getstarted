(() => {
    let alreadyFiltered = false

    const apiURl = document.currentScript.dataset.apiUrl
    const filterInput = document.getElementById("room-search")
    const roomsContainer = document.querySelector(".side-section .rooms")
    filterInput.addEventListener("keyup", async function(e){
        if (e.key.toLowerCase() !== "enter")
            return

        const roomNameTerm = this.value.trim()
        if(!roomNameTerm && !alreadyFiltered)
            return

        const roomsFound = await fetchRooms(roomNameTerm)
        const roomElements = roomsFound.map(room => window.createRoomHTML(room))

        roomsContainer.innerHTML = ""
        roomsContainer.append(...roomElements)

        alreadyFiltered = !!roomNameTerm
    })

    async function fetchRooms(roomNameTerm){
        let url = (roomNameTerm)? apiURl + `?room_name=${roomNameTerm}`: apiURl

        const response = await fetch(url, {
            credentials: "same-origin",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
            }
        })
        return await response.json()
    }

})()
