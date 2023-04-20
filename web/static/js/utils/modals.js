// Singleton function for modal
function initModal(){
    let modal = null

    const getModal = () => {
        if(modal != null) {
            return modal
        }

        // Selectors of certain elements
        const domElement = {
            body: document.querySelector('.popup'),
            title: document.querySelector('.popup_title'),
            content: document.querySelector('.popup_content'),
            cover: document.querySelector('.cover')
        }

        const show = () => {
            domElement.body.style.display = 'block'
            domElement.cover.style.display = 'block'
        }

        const setAttributes = (title, content) => {
            domElement.title.innerHTML = title
            domElement.content.innerHTML = content
        }

        modal = {
            show: show,
            setAttributes: setAttributes
        }

        return modal
    }

    return getModal()
}