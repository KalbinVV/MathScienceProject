$(document).ready(function(){
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
            success: function(json_response) {
                const popup = document.querySelector('.popup')
                const popupTitle = document.querySelector('.popup_title')
                const popupContent = document.querySelector('.popup_content')

                const cover = document.querySelector('.cover')

                const responseData = JSON.parse(json_response)

                if (responseData.status == false) {
                    popupTitle.innerHTML = 'Не удалось загрузить файл!'
                    popupContent.innerHTML = responseData.reason
                } else {
                    popupTitle.innerHTML = 'Отчет загружен!'
                    popupContent.innerHTML = `Доступ к отчету можно получить, перейдя по ссылке:
                    <a href="reports/${responseData.href}">Ссылка</a>`
                }

                cover.style.display = 'block'
                popup.style.display = 'block'
            }
        })
    })
})