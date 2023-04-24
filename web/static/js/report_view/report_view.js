$(document).ready(function(){
    const correlationPleiadesConfiguration = {
        canvasWidth: 800,
        canvasHeight: 600,
        circleRadius: 200,
        pointWidth: 5,
        pointHeight: 5
    }

    function renderTable(tableContentSelector, data, is_correlation_table=false) {
        const tableContent = document.querySelector(tableContentSelector)

        tableContent.innerHTML = ''

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
                    const filtersCodes = ['strong', 'average', 'moderate', 'weak', 'very_weak']

                    let filters = []

                    filtersCodes.forEach(filterCode => {
                        filters.push(getFilter(filterCode))
                    })

                    for(let filter of filters) {
                        if (filter.inRange(Math.abs(value))) {
                            className = filter.getClassName()
                            break
                        }
                    }

                    td.classList.add(className)
                }
                td.innerHTML = value

                tr.appendChild(td)
            })

            tableContent.appendChild(tr)
        }
    }

    let covarValue = null

    function loadTable(tableSelector, tableType, shouldRender = true) {
        $.ajax({
            url: '/get_table',
            method: 'get',
            data: {file: FILE_NAME, type: tableType, covar: covarValue},
            success: function(response) {
                if (response.status == true) {
                    if(shouldRender) {
                        renderTable(tableSelector, response.data, tableType == 'correlation' || tableType == 'partial_correlation' ? true : false)
                    }

                    return response.data
                } else {
                    const modal = initModal()

                    modal.setAttributes('Не удалось загрузить таблицу!', response.reason)
                    modal.show()
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                const modal = initModal()

                modal.setAttributes('Не удалось загрузить таблицу!', 'Ошибка сети')
                modal.show()
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
                    const modal = initModal()

                    modal.setAttributes('Не удалось загрузить графы!', response.reason)
                    modal.show()
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                const modal = initModal()

                modal.setAttributes('Не удалось загрузить графы!', 'Ошибка сети')
                modal.show()
            }
        })
    }

    function loadAvailableColumns() {
        const selectList = document.querySelector('#available_columns')

        selectList.onchange = (event) => {
            covarValue = event.target.value
        }

        $.ajax({
            url: '/get_columns',
            data: {file: FILE_NAME},
            success: function(response) {
                const options = response.data

                options.forEach(option => {
                    const optionElement = document.createElement('option')
                    optionElement.innerHTML = option
                    selectList.appendChild(optionElement)
                })
            }
        })

    }

    loadAvailableColumns()

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

    $('#partial_correlation_table_button').click(event => {
        loadTable('#partial_correlation_table_content', 'partial_correlation')
    })

    $('#charts_button').click(event => {
        event.currentTarget.style.display = 'none'
        loadCharts()
    })

    function getPointsToFormCircle(amountOfPoints, radius, center) {
        const points = []

        const slice = 2 * Math.PI / amountOfPoints

        for(let i = 0; i < amountOfPoints; i++) {
            const angle = slice * i

            const x = center.x + radius * Math.cos(angle)
            const y = center.y + radius * Math.sin(angle)

            points.push({x: x, y: y})
        }

        return points
    }


    function showCorrelationPleiades(filtersCodes) {
        let filters = []

        filtersCodes.forEach(filterCode => {
            filters.push(getFilter(filterCode))
        })

        const canvas = document.getElementById('correlation_pleiades_canvas')
        const ctx = canvas.getContext('2d');

        canvas.style.display = 'block'

        canvas.setAttribute('width', correlationPleiadesConfiguration.canvasWidth)
        canvas.setAttribute('height', correlationPleiadesConfiguration.canvasHeight)

        ctx.fillStyle = 'white'
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        const centerPoint = {
                x: correlationPleiadesConfiguration.canvasWidth / 2,
                y: correlationPleiadesConfiguration.canvasHeight / 2
        }

        $.ajax({
            url: '/get_table',
            method: 'get',
            data: {file: FILE_NAME, type: 'correlation'},
            success: function(response) {
                if (response.status == true) {
                    const correlationData = response.data

                    console.log(correlationData)

                    const points = getPointsToFormCircle(correlationData.size, correlationPleiadesConfiguration.circleRadius, centerPoint)

                    ctx.fillStyle = 'black'
                    ctx.font = "12px serif";

                    let i = 1

                    let pointsDictionary = {}

                    points.forEach(point => {
                        ctx.fillRect(point.x, point.y, correlationPleiadesConfiguration.pointWidth, correlationPleiadesConfiguration.pointHeight)

                        const columnName = correlationData.columns[i]

                        pointsDictionary[columnName] = {x: point.x, y: point.y}

                        i += 1
                    })

                    correlationData.columns.forEach(column => {
                        if(column == ' ') return

                        const point = pointsDictionary[column]

                        let i = 1
                        correlationData[column].forEach(data => {
                            const anotherPoint = pointsDictionary[correlationData.columns[i]]

                            ctx.beginPath()
                            ctx.moveTo(point.x, point.y)
                            ctx.lineTo(anotherPoint.x, anotherPoint.y)

                            let strokeColor = 'white'

                            for(let filter of filters) {
                                if (filter.inRange(Math.abs(data))) {
                                    console.log(filter.getName(), Math.abs(data))
                                    strokeColor = filter.getColor()
                                    break
                                }
                            }

                            ctx.strokeStyle = strokeColor
                            ctx.stroke()

                            i += 1
                        })

                        i = 1

                        points.forEach(point => {
                            ctx.fillText(correlationData.columns[i], point.x + 5, point.y + 10)

                            i += 1
                        })
                    })
                } else {
                    const modal = initModal()

                    modal.setAttributes('Не удалось корреляционные плеяды!', response.reason)
                    modal.show()
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                const modal = initModal()

                modal.setAttributes('Не удалось загрузить корреляционные плеяды!', 'Ошибка сети')
                modal.show()
            }
        })
    }

    $('#show_correlation_pleiades_button').click(event => {
        event.currentTarget.style.display = 'none'
        showCorrelationPleiades(['strong', 'average', 'moderate', 'weak', 'very_weak'])
    })

    $("#correlation_all_bindings_button").click(event => {
        showCorrelationPleiades(['strong', 'average', 'moderate', 'weak', 'very_weak'])
    })

    $("#correlation_weak_bindings_button").click(event => {
        showCorrelationPleiades(['weak', 'very_weak'])
    })

    $("#correlation_average_bindings_button").click(event => {
        showCorrelationPleiades(['average', 'moderate'])
    })

    $("#correlation_strong_bindings_button").click(event => {
        showCorrelationPleiades(['strong'])
    })

})