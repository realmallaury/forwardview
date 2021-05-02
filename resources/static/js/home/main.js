am4core.useTheme(am4themes_animated);
am4core.options.minPolylineStep = 5;

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
        return {
            orders: null,
            summary: null,
        }
    },

    methods: {},

    mounted() {
        axios
            .get("/order-history.json")
            .then(response => {
                if (response.request.responseURL.includes("login")) {
                    location.reload();
                }

                this.orders = response.data.orders;
                this.summary = response.data.summary;

                this.ordersChart = createOrdersChart(this.orders);
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

function createOrdersChart(orders) {
    let ordersChart = am4core.create("orders", am4charts.XYChart);

    var xAxis = ordersChart.xAxes.push(new am4charts.ValueAxis());
    xAxis.renderer.labels.template.disabled = true;
    xAxis.title.text = "Orders over time";

    var yAxis = ordersChart.yAxes.push(new am4charts.ValueAxis());
    yAxis.title.text = "Amount ($)";

    var series = ordersChart.series.push(new am4charts.LineSeries());
    series.dataFields.valueY = "account_total";
    series.dataFields.valueX = "index";
    series.strokeWidth = 3;
    series.tooltipText = "{valueY.value}";
    series.fillOpacity = 0.1;

    var range = yAxis.createSeriesRange(series);
    range.value = 0;
    range.endValue = -1000;
    range.contents.stroke = ordersChart.colors.getIndex(4);
    range.contents.fill = range.contents.stroke;
    range.contents.strokeOpacity = 0.7;
    range.contents.fillOpacity = 0.1;

    ordersChart.cursor = new am4charts.XYCursor();
    ordersChart.cursor.xAxis = xAxis;
    ordersChart.scrollbarX = new am4core.Scrollbar();

    series.tooltip.getFillFromObject = false;
    series.tooltip.adapter.add("x", (x, target)=>{
        if(series.tooltip.tooltipDataItem.valueY < 0){
            series.tooltip.background.fill = ordersChart.colors.getIndex(4);
        }
        else{
            series.tooltip.background.fill = ordersChart.colors.getIndex(0);
        }
        return x;
    });

    ordersChart.data = orders;

    return ordersChart;
}
