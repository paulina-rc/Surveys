function createChart(chartId, labels, data) {

    const ctx = document.getElementById(chartId);

    new Chart(ctx, {

        type: 'bar',

        data: {

            labels: labels,

            datasets: [{

                label: 'Votos',

                data: data,

                borderWidth: 1

            }]
        }
    });
}