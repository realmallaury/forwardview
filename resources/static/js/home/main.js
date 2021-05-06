am4core.useTheme(am4themes_animated);
am4core.options.minPolylineStep = 5;

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
        return {
            orders: null,
            chartType: "accountTotal",
        }
    },

    methods: {
        updateOverviewChart(event) {
            this.chartType = event.target.value;
            updateOverviewChart(this.overviewChart, this.chartType);
        },
    },

    mounted() {
        axios
            .get("/order-history.json")
            .then(response => {
                if (response.request.responseURL.includes("login")) {
                    location.reload();
                }

                this.orders = response.data.orders;

                this.overviewChart = createOverviewChart(this.orders);
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

function createOverviewChart(orders) {
    let overviewChart = am4core.create("orders", am4charts.XYChart);

    var xAxis = overviewChart.xAxes.push(new am4charts.ValueAxis());
    xAxis.renderer.labels.template.disabled = true;
    xAxis.title.text = "Orders over time";

    var yAxis = overviewChart.yAxes.push(new am4charts.ValueAxis());
    yAxis.title.text = "Total account amount ($)";

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

    series.tooltip.getFillFromObject = false;
    series.tooltip.adapter.add("x", (x, target)=>{
        if(series.tooltip.tooltipDataItem.valueY < 0){
            series.tooltip.background.fill = overviewChart.colors.getIndex(4);
        }
        else{
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
        overviewChart.yAxes.getIndex(0).title.text = "Total account amount after each trade ($)";
    } else if (chartType === "profitLoss") {
        overviewChart.series.getIndex(0).dataFields.valueY = "profit_loss";
        overviewChart.yAxes.getIndex(0).title.text = "Profit / loss on each trade ($)";
    }

    overviewChart.validateData();
}