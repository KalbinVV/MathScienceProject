$(document).ready(function(){
    const popup = {
        body: document.querySelector('.popup'),
        title: document.querySelector('.popup_title'),
        content: document.querySelector('.popup_content'),
        cover: document.querySelector('.cover')
    }

    function renderTable(tableContentSelector, data, is_correlation_table=false) {
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

                let value = data[column][i]

                let className = null

                if(!isNaN(value)) {
                    value = Number(value.toFixed(2))
                }

                if(is_correlation_table && !isNaN(value)) {
                    if(value > 0.7) {
                        className = 'strong_binding'
                    } else if (value > 0.5) {
                        className = 'average_binding'
                    } else if (value > 0.3) {
                        className = 'moderate_binding'
                    } else if (value > 0.2) {
                        className = 'weak_binding'
                    } else {
                        className = 'very_weak_binding'
                    }

                    td.classList.add(className)
                }
                td.innerHTML = value

                tr.appendChild(td)
            })

            tableContent.appendChild(tr)
        }
    }

    function loadTable(tableSelector, tableType) {
        $.ajax({
            url: '/get_table',
            method: 'get',
            data: {file: FILE_NAME, type: tableType},
            success: function(response) {
                if (response.status == true) {
                    renderTable(tableSelector, response.data, tableType == 'correlation' ? true : false)
                } else {
                    popup.body.style.display = 'block'
                    popup.cover.style.display = 'block'

                    popup.title.innerHTML = 'Не удалось загрузить таблицу!'
                    popup.content.innerHTML = response.reason
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                popup.body.style.display = 'block'
                popup.cover.style.display = 'block'

                popup.title.innerHTML = 'Не удалось загрузить таблицу!'
                popup.content.innerHTML = textStatus
            }
        })
    }

    const charts = document.querySelector('#charts')
    const anchors = document.querySelector('#anchors')

    function drawChart(chartData, i) {
        const title = chartData[0] + CHART_PREFIX
        const x = chartData[1]
        const interpolated_x = chartData[2]
        const interpolated_y = chartData[3]

        const histogram = {
            x: x,
            xbins: {
                start: 0,
                end: 1,
                size: 0.2
            },
            opacity: 0.8,
            marker: {
                color: 'green'
            },
            type: 'histogram',
            name: 'Гистограмма'
        }

        const lines = {
            x: interpolated_x,
            y: interpolated_y,
            mode: 'lines',
            type: 'scatter',
            name: 'Функция'
        }

        const data = [histogram, lines]

        const chartContainer = document.createElement('div')
        chartContainer.classList.add('chart_container')

        const chartHeader = document.createElement('a')
        chartHeader.classList.add('chart_header')
        chartHeader.name = title
        chartHeader.innerHTML = title

        const chartAnchorListElement = document.createElement('li')

        const chartAnchor = document.createElement('a')
        chartAnchor.innerHTML = title
        chartAnchor.href = '#' + title

        chartAnchorListElement.appendChild(chartAnchor)
        anchors.appendChild(chartAnchorListElement)

        chartContainer.appendChild(chartHeader)

        const chart = document.createElement('div')
        const chartId = 'graph' + i
        chart.id = chartId

        chartContainer.appendChild(chart)

        charts.appendChild(chartContainer)

        Plotly.newPlot(chartId, data);
    }

    function loadCharts() {
        $.ajax({
            url: '/get_intervals',
            method: 'get',
            data: {file: FILE_NAME},
            success: function(response) {
                if (response.status == true) {
                    response.data.forEach((chartData, i) => {
                        drawChart(chartData, i)
                    })
                } else {
                    popup.body.style.display = 'block'
                    popup.cover.style.display = 'block'

                    popup.title.innerHTML = 'Не удалось загрузить графы!'
                    popup.content.innerHTML = response.reason
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                popup.body.style.display = 'block'
                popup.cover.style.display = 'block'

                popup.title.innerHTML = 'Не удалось загрузить графы!'
                popup.content.innerHTML = textStatus
            }
        })
    }

    $('#source_table_button').click(event => {
        event.currentTarget.style.display = 'none'
        loadTable('#source_table_content', 'source')
    })

    $('#normalized_table_button').click(event => {
        event.currentTarget.style.display = 'none'
        loadTable('#normalized_table_content', 'normalized')
    })

    $('#statistic_table_button').click(event => {
        event.currentTarget.style.display = 'none'
        loadTable('#statistic_table_content', 'statistic')
    })

    $('#chi_square_table_button').click(event => {
        event.currentTarget.style.display = 'none'
        loadTable('#chi_square_table_content', 'chi_square')
    })

    $('#correlation_table_button').click(event => {
        event.currentTarget.style.display = 'none'
        loadTable('#correlation_table_content', 'correlation')
    })

    $('#charts_button').click(event => {
        event.currentTarget.style.display = 'none'
        loadCharts()
    })

})