function createOhlcChart(tickerOhlc) {
    let ohlcChart = am4core.create("ohlc", am4charts.XYChart);

    ohlcChart.dateFormatter.inputDateFormat = "YYYY-MM-DDTHH:mm:ss.sssZ";
    ohlcChart.dateFormatter.timezoneOffset = 0;

    // the following line makes value axes to be arranged vertically.
    ohlcChart.leftAxesContainer.layout = "vertical";

    var dateAxis = ohlcChart.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.grid.template.location = 0;
    dateAxis.baseInterval = {
        count: 15,
        timeUnit: "minute"
    }
    dateAxis.dateFormats.setKey("minute", "yyyy-MM-dd HH:mm:ss");
    dateAxis.skipEmptyPeriods = true;
    dateAxis.renderer.grid.template.location = 0;
    dateAxis.renderer.ticks.template.length = 8;
    dateAxis.renderer.ticks.template.strokeOpacity = 0.1;
    dateAxis.renderer.grid.template.disabled = true;
    dateAxis.renderer.ticks.template.disabled = false;
    dateAxis.renderer.ticks.template.strokeOpacity = 0.2;
    dateAxis.renderer.minLabelPosition = 0.01;
    dateAxis.renderer.maxLabelPosition = 0.99;
    dateAxis.keepSelection = true;
    dateAxis.minHeight = 30;

    var valueAxis = ohlcChart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.tooltip.disabled = true;
    valueAxis.zIndex = 1;
    valueAxis.renderer.baseGrid.disabled = true;
    // height of axis
    valueAxis.height = am4core.percent(65);

    valueAxis.renderer.gridContainer.background.fill = am4core.color("#000000");
    valueAxis.renderer.gridContainer.background.fillOpacity = 0.05;
    valueAxis.renderer.inside = true;
    valueAxis.renderer.labels.template.verticalCenter = "bottom";
    valueAxis.title.text = "Price ($)";

    //valueAxis.renderer.maxLabelPosition = 0.95;
    valueAxis.renderer.fontSize = "0.8em"

    var series = ohlcChart.series.push(new am4charts.CandlestickSeries());
    series.dataFields.dateX = "time";
    series.dataFields.valueY = "close";
    series.dataFields.openValueY = "open";
    series.dataFields.lowValueY = "low";
    series.dataFields.highValueY = "high";
    series.simplifiedProcessing = true;
    series.tooltipText = "Open:${openValueY.value}\nLow:${lowValueY.value}\nHigh:${highValueY.value}\nClose:${valueY.value}";

    ohlcChart.cursor = new am4charts.XYCursor();
    ohlcChart.cursor.behavior = "none";

    var valueAxis2 = ohlcChart.yAxes.push(new am4charts.ValueAxis());
    valueAxis2.tooltip.disabled = true;
    // height of axis
    valueAxis2.height = am4core.percent(20);
    valueAxis2.zIndex = 3
    // this makes gap between panels
    valueAxis2.marginTop = 30;
    valueAxis2.renderer.baseGrid.disabled = true;
    valueAxis2.renderer.inside = true;
    valueAxis2.renderer.labels.template.verticalCenter = "bottom";
    // valueAxis2.renderer.labels.template.padding(2, 2, 2, 2);
    // valueAxis.renderer.maxLabelPosition = 0.95;
    valueAxis2.renderer.fontSize = "0.8em"

    valueAxis2.renderer.gridContainer.background.fill = am4core.color("#000000");
    valueAxis2.renderer.gridContainer.background.fillOpacity = 0.05;
    valueAxis2.title.text = "MACD";

    var valueAxis3 = ohlcChart.yAxes.push(new am4charts.ValueAxis());
    valueAxis3.tooltip.disabled = true;
    // height of axis
    valueAxis3.height = am4core.percent(20);
    valueAxis3.zIndex = 5
    // this makes gap between panels
    valueAxis3.marginTop = 30;
    valueAxis3.renderer.baseGrid.disabled = true;
    valueAxis3.renderer.inside = true;
    valueAxis3.renderer.labels.template.verticalCenter = "bottom";
    // valueAxis3.renderer.labels.template.padding(2, 2, 2, 2);
    //valueAxis.renderer.maxLabelPosition = 0.95;
    valueAxis3.renderer.fontSize = "0.8em"

    valueAxis3.renderer.gridContainer.background.fill = am4core.color("#000000");
    valueAxis3.renderer.gridContainer.background.fillOpacity = 0.05;
    valueAxis3.title.text = "Volume";

    var scrollbarX = new am4charts.XYChartScrollbar();

    var sbSeries = ohlcChart.series.push(new am4charts.LineSeries());
    sbSeries.dataFields.valueY = "close";
    sbSeries.dataFields.dateX = "time";
    scrollbarX.series.push(sbSeries);
    sbSeries.disabled = true;
    scrollbarX.marginBottom = 20;
    ohlcChart.scrollbarX = scrollbarX;
    scrollbarX.scrollbarChart.xAxes.getIndex(0).minHeight = undefined;

    var volume = ohlcChart.series.push(new am4charts.ColumnSeries());
    volume.dataFields.valueY = "volume";
    volume.dataFields.dateX = "time";
    volume.yAxis = valueAxis3;
    volume.clustered = false;
    volume.groupFields.valueY = "sum";

    var keltnerHBand = ohlcChart.series.push(new am4charts.LineSeries());
    keltnerHBand.dataFields.valueY = "KELTNER_HBAND";
    keltnerHBand.dataFields.dateX = "time";
    keltnerHBand.yAxis = valueAxis;
    keltnerHBand.cursorTooltipEnabled = false;
    keltnerHBand.stroke = am4core.color("blue").lighten(0.5);

    var keltnerMBand = ohlcChart.series.push(new am4charts.LineSeries());
    keltnerMBand.dataFields.valueY = "KELTNER_MBAND";
    keltnerMBand.dataFields.dateX = "time";
    keltnerMBand.yAxis = valueAxis;
    keltnerMBand.cursorTooltipEnabled = false;
    keltnerMBand.strokeDasharray = "8,4,2,4";
    keltnerMBand.stroke = am4core.color("blue").lighten(0.5);

    var keltnerLBand = ohlcChart.series.push(new am4charts.LineSeries());
    keltnerLBand.dataFields.valueY = "KELTNER_LBAND";
    keltnerLBand.dataFields.dateX = "time";
    keltnerLBand.yAxis = valueAxis;
    keltnerLBand.cursorTooltipEnabled = false;
    keltnerLBand.stroke = am4core.color("blue").lighten(0.5);

    var macd = ohlcChart.series.push(new am4charts.LineSeries());
    macd.dataFields.valueY = "MACD";
    macd.dataFields.dateX = "time";
    macd.yAxis = valueAxis2;
    macd.cursorTooltipEnabled = false;
    macd.stroke = am4core.color("blue").lighten(0.5);

    var macdSignal = ohlcChart.series.push(new am4charts.LineSeries());
    macdSignal.dataFields.valueY = "MACD_SIGNAL";
    macdSignal.dataFields.dateX = "time";
    macdSignal.yAxis = valueAxis2;
    macdSignal.cursorTooltipEnabled = false;
    macdSignal.strokeDasharray = "8,4,2,4";
    macdSignal.stroke = am4core.color("blue").lighten(0.5);

    var tradingRange = ohlcChart.series.push(new am4charts.LineSeries());
    tradingRange.dataFields.valueY = "STOP_LOSS";
    tradingRange.dataFields.openValueY = "TAKE_PROFIT";
    tradingRange.dataFields.dateX = "time";
    tradingRange.yAxis = valueAxis;
    tradingRange.fill = am4core.color("gray").lighten(0.5);
    tradingRange.fillOpacity = 0.3;
    tradingRange.cursorTooltipEnabled = false;
    tradingRange.stroke = am4core.color("gray").lighten(0.5);
    tradingRange.strokeOpacity = 0.3;

    ohlcChart.data = tickerOhlc;

    showIndicator(ohlcChart);
    ohlcChart.events.on("ready", function(ev){
	    hideIndicator();
    });

    return ohlcChart;
}

function updateOhlcChart(ohlcChart, interval, next) {
    let tabs = ["#pills-tab-15min", "#pills-tab-60min", "#pills-tab-1d"]
    let url = "/ticker.json?interval=" + interval;
    if (next === "true") {
        url = url + "&next=true";
    }

    axios
        .get(url)
        .then(response => {
            if (response.request.responseURL.includes("login")) {
                location.reload();
            }

            if (!_.isEqual(ohlcChart.data, response.data)) {
                ohlcChart.data = response.data;
                // ohlcChart.validateData();

                if (interval === "15min") {
                    ohlcChart.xAxes._values[0].baseInterval = {
                        count: 15,
                        timeUnit: "minute"
                    }
                } else if (interval === "60min") {
                    ohlcChart.xAxes._values[0].baseInterval = {
                        count: 60,
                        timeUnit: "minute"
                    }
                } else if (interval === "1d") {
                    ohlcChart.xAxes._values[0].baseInterval = {
                        count: 1,
                        timeUnit: "day"
                    }
                }

                _.each(tabs, function (item) {
                    $(item).removeClass("active");
                    if ("#pills-tab-" + interval === item) {
                        $(item).toggleClass("active");
                    }
                });
            } else {
                $("#pills-tab-right").prop( "disabled", true );
            }
        });
}

function placeOrder(ohlcChart, order) {
    axios
        .post("/place-order", order)
        .then(response => {
            if (response.request.responseURL.includes("login")) {
                location.reload();
            }

            $("#ok-submit-msg").text(response.data.message);
            $("#ok-submit").show();
            $("#error-submit").hide();

            updateOhlcChart(ohlcChart, "60min", "true");
        })
        .catch(function (error) {
            if (error.response) {
                $("#error-submit-msg").text(error.response.data.message);
                $("#ok-submit").hide();
                $("#error-submit").show();
            }
        });
}

function exitTrade(ohlcChart, order) {
    axios
        .get("/exit-trade", order)
        .then(response => {
            if (response.request.responseURL.includes("login")) {
                location.reload();
            }

            $("#ok-submit-msg").text(response.data.message);
            $("#ok-submit").show();
            $("#error-submit").hide();
        })
        .catch(function (error) {
            if (error.response) {
                $("#error-submit-msg").text(error.response.data.message);
                $("#ok-submit").hide();
                $("#error-submit").show();
            }
        });
}

let indicator;
let indicatorInterval;

function showIndicator(ohlcChart) {
  if (!indicator) {
    indicator = ohlcChart.tooltipContainer.createChild(am4core.Container);
    indicator.background.fill = am4core.color("#fff");
    indicator.width = am4core.percent(100);
    indicator.height = am4core.percent(100);

    var indicatorLabel = indicator.createChild(am4core.Label);
    indicatorLabel.text = "Loading ticker data...";
    indicatorLabel.align = "center";
    indicatorLabel.valign = "top";
    indicatorLabel.dy = 50;
  }

  indicator.hide(0);
  indicator.show();

  clearInterval(indicatorInterval);
}

function hideIndicator() {
  indicator.hide();
  clearInterval(indicatorInterval);
}