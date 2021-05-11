am4core.useTheme(am4themes_animated);
am4core.options.minPolylineStep = 5;

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
        return {
            orders: null,
            chartType: "accountTotal",
            currentPage: 1,
            pages: [],
        }
    },

    methods: {
        updateOverviewChart(event) {
            this.chartType = event.target.value;
            updateOverviewChart(this.overviewChart, this.chartType);
        },
        updateCurrentPage(page) {
            this.currentPage = page;
            axios
                .get("/order-history.json?page=" + page)
                .then(response => {
                    if (response.request.responseURL.includes("login")) {
                        location.reload();
                    }

                    this.overviewChart.data = response.data.orders;
                    this.orders = response.data.orders.reverse();
                })
                .catch(function (error) {
                    // handle error
                    console.log(error);
                })
        }
    },

    mounted() {
        axios
            .get("/order-history.json")
            .then(response => {
                if (response.request.responseURL.includes("login")) {
                    location.reload();
                }

                this.currentPage = response.data.page;
                let totalPages = Math.ceil(parseInt(response.data.total) / parseInt(response.data.per_page));
                this.pages = Array.from({length: totalPages}, (x, i) => i + 1);

                this.overviewChart = createOverviewChart(response.data.orders);
                this.orders = response.data.orders.reverse();
            })
            .catch(function (error) {
                // handle error
                console.log(error);
            })
    },

    beforeUnmount() {

    }
})

app.mount("#home");

app.config.globalProperties.$filters = {
    formatNumber(value) {
        return Number(value).toFixed(2);
    },
    formatDate(value, format) {
        return moment(value).format(format);
    }
}

function createOverviewChart(orders) {
    let overviewChart = am4core.create("orders", am4charts.XYChart);
    overviewChart.numberFormatter.numberFormat = "$#,###";

    var xAxis = overviewChart.xAxes.push(new am4charts.ValueAxis());
    xAxis.renderer.labels.template.disabled = true;
    xAxis.title.text = "From older to recent orders";
    xAxis.integersOnly = true;
    xAxis.cursorTooltipEnabled = false;
    xAxis.renderer.grid.template.disabled = true;

    var yAxis = overviewChart.yAxes.push(new am4charts.ValueAxis());
    yAxis.renderer.gridContainer.background.fill = am4core.color("#000000");
    yAxis.renderer.gridContainer.background.fillOpacity = 0.05;
    yAxis.renderer.inside = true;
    yAxis.renderer.labels.template.verticalCenter = "bottom";

    var series = overviewChart.series.push(new am4charts.LineSeries());
    series.dataFields.valueY = "account_total";
    series.dataFields.valueX = "index";
    series.strokeWidth = 3;
    series.tooltipText = "{valueY.value}";
    series.fillOpacity = 0.1;

    var range = yAxis.createSeriesRange(series);
    range.value = 0;
    range.endValue = -1000;
    range.contents.stroke = overviewChart.colors.getIndex(4);
    range.contents.fill = range.contents.stroke;
    range.contents.strokeOpacity = 0.7;
    range.contents.fillOpacity = 0.1;

    overviewChart.cursor = new am4charts.XYCursor();
    overviewChart.cursor.xAxis = xAxis;

    overviewChart.scrollbarX = new am4core.Scrollbar();
    overviewChart.scrollbarX.disabled = true;

    series.tooltip.getFillFromObject = false;
    series.tooltip.adapter.add("x", (x, target) => {
        if (series.tooltip.tooltipDataItem.valueY < 0) {
            series.tooltip.background.fill = overviewChart.colors.getIndex(4);
        } else {
            series.tooltip.background.fill = overviewChart.colors.getIndex(0);
        }
        return x;
    });

    overviewChart.data = orders;

    return overviewChart;
}

function updateOverviewChart(overviewChart, chartType) {
    if (chartType === "accountTotal") {
        overviewChart.series.getIndex(0).dataFields.valueY = "account_total";
        overviewChart.yAxes.getIndex(0).numberFormatter.numberFormat = "$#,###";
    } else if (chartType === "profitLoss") {
        overviewChart.series.getIndex(0).dataFields.valueY = "profit_loss";
        overviewChart.numberFormatter.numberFormat = "$#,###";
    } else if (chartType === "profitLossPtc") {
        overviewChart.series.getIndex(0).dataFields.valueY = "profit_loss_as_percentage_of_account";
        overviewChart.numberFormatter.numberFormat = "#'%'";
    } else if (chartType === "riskPtc") {
        overviewChart.series.getIndex(0).dataFields.valueY = "risk_as_percentage_of_account";
        overviewChart.numberFormatter.numberFormat = "#'%'";
    }

    overviewChart.validateData();
}