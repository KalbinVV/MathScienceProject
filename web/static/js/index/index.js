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
            success: function(response) {
                let titleOfModal = null
                let contentOfModal = null

                if (response.status == false) {
                    titleOfModal = 'Не удалось загрузить файл!'
                    contentOfModal = response.reason
                } else {
                    titleOfModal = 'Отчет загружен!'
                    contentOfModal = `Доступ к отчету можно получить, перейдя по ссылке:
                    <a href="reports/${response.href}">Ссылка</a>`
                }

                const modal = initModal()

                modal.setAttributes(titleOfModal, contentOfModal)
                modal.show()
            },
            error: function(jqXHR, textStatus, errorThrown) {
                const modal = initModal()

                modal.setAttributes('Не удалось загрузить файл!', 'Ошибка сети')
                modal.show()
            }
        })
    })
})