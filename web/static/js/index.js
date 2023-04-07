$(document).ready(function(){
    const popup = {
        body: document.querySelector('.popup'),
        title: document.querySelector('.popup_title'),
        content: document.querySelector('.popup_content'),
        cover: document.querySelector('.cover')
    }

    $('#file_input').change((event) => {
        let formData = new FormData()

        const file = event.target.files[0]

        formData.append('file', file)

        $.ajax({
            url: 'upload_report',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status == false) {
                    popup.title.innerHTML = 'Не удалось загрузить файл!'
                    popup.content.innerHTML = response.reason
                } else {
                    popup.title.innerHTML = 'Отчет загружен!'
                    popup.content.innerHTML = `Доступ к отчету можно получить, перейдя по ссылке:
                    <a href="reports/${response.href}">Ссылка</a>`
                }

                popup.cover.style.display = 'block'
                popup.body.style.display = 'block'
            }
        })
    })
})