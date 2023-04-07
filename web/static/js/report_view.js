$(document).ready(function(){
    function renderTable(tableContentSelector, data) {
        const tableContent = document.querySelector(tableContentSelector)

        const thRow = document.createElement('tr')

        data.columns.forEach(column => {
            const th = document.createElement('th')
            th.innerHTML = column
            thRow.appendChild(th)
        })

        tableContent.appendChild(thRow)

        for(let i = 0; i < data.size; i++) {
            const tr = document.createElement('tr')

            data.columns.forEach(column => {
                const td = document.createElement('td')

                const value = data[column][i]

                if(isNaN(value)) {
                    td.innerHTML = value
                } else {
                    td.innerHTML = value.toFixed(2)
                }
                tr.appendChild(td)
            })

            tableContent.appendChild(tr)
        }
    }

    function loadTable(tableSelector, tableType) {
        $.ajax({
            url: '/get_table',
            method: 'get',
            dataType: 'json',
            data: {file: FILE_NAME, type: tableType},
            success: function(response) {
                renderTable(tableSelector, response)
            }
        })
    }

    loadTable('#source_table_content', 'source')
    loadTable('#normalized_table_content', 'normalized')
    loadTable('#statistic_table_content', 'statistic')
    loadTable('#chi_square_table_content', 'chi_square')

})