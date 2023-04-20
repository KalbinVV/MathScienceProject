function initModal(){
    // Selectors of certain elements
    const domElement = {
        body: document.querySelector('.popup'),
        title: document.querySelector('.popup_title'),
        content: document.querySelector('.popup_content'),
        cover: document.querySelector('.cover')
    }

    return {
        show: () => {
            domElement.body.style.display = 'block'
            domElement.cover.style.display = 'block'
        },
        setAttributes: (title, content) => {
            domElement.title.innerHTML = title
            domElement.content.innerHTML = content
        }
    }
}