am4core.ready(function () {

// Themes begin
    am4core.useTheme(am4themes_animated);
// Themes end

    am4core.options.minPolylineStep = 5;

// Create chart
    var chart = am4core.create("ohlc-div", am4charts.XYChart);

// Load data
    chart.dateFormatter.inputDateFormat = "YYYY-MM-DDTHH:mm:ss.sssZ";
    chart.dateFormatter.timezoneOffset = 0;

    // the following line makes value axes to be arranged vertically.
    chart.leftAxesContainer.layout = "vertical";

    var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
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

    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
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

    var series = chart.series.push(new am4charts.CandlestickSeries());
    series.dataFields.dateX = "time";
    series.dataFields.valueY = "close";
    series.dataFields.openValueY = "open";
    series.dataFields.lowValueY = "low";
    series.dataFields.highValueY = "high";
    series.simplifiedProcessing = true;
    series.tooltipText = "Open:${openValueY.value}\nLow:${lowValueY.value}\nHigh:${highValueY.value}\nClose:${valueY.value}";

    chart.cursor = new am4charts.XYCursor();
    chart.cursor.behavior = "none";

    var valueAxis2 = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis2.tooltip.disabled = true;
    // height of axis
    valueAxis2.height = am4core.percent(20);
    valueAxis2.zIndex = 3
    // this makes gap between panels
    valueAxis2.marginTop = 30;
    valueAxis2.renderer.baseGrid.disabled = true;
    valueAxis2.renderer.inside = true;
    valueAxis2.renderer.labels.template.verticalCenter = "bottom";
    valueAxis2.renderer.labels.template.padding(2, 2, 2, 2);
    //valueAxis.renderer.maxLabelPosition = 0.95;
    valueAxis2.renderer.fontSize = "0.8em"

    valueAxis2.renderer.gridContainer.background.fill = am4core.color("#000000");
    valueAxis2.renderer.gridContainer.background.fillOpacity = 0.05;

    var valueAxis3 = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis3.tooltip.disabled = true;
    // height of axis
    valueAxis3.height = am4core.percent(20);
    valueAxis3.zIndex = 5
    // this makes gap between panels
    valueAxis3.marginTop = 30;
    valueAxis3.renderer.baseGrid.disabled = true;
    valueAxis3.renderer.inside = true;
    valueAxis3.renderer.labels.template.verticalCenter = "bottom";
    valueAxis3.renderer.labels.template.padding(2, 2, 2, 2);
    //valueAxis.renderer.maxLabelPosition = 0.95;
    valueAxis3.renderer.fontSize = "0.8em"

    valueAxis3.renderer.gridContainer.background.fill = am4core.color("#000000");
    valueAxis3.renderer.gridContainer.background.fillOpacity = 0.05;

    var scrollbarX = new am4charts.XYChartScrollbar();

    var sbSeries = chart.series.push(new am4charts.LineSeries());
    sbSeries.dataFields.valueY = "close";
    sbSeries.dataFields.dateX = "time";
    scrollbarX.series.push(sbSeries);
    sbSeries.disabled = true;
    scrollbarX.marginBottom = 20;
    chart.scrollbarX = scrollbarX;
    scrollbarX.scrollbarChart.xAxes.getIndex(0).minHeight = undefined;

    var volume = chart.series.push(new am4charts.ColumnSeries());
    volume.dataFields.valueY = "volume";
    volume.dataFields.dateX = "time";
    volume.yAxis = valueAxis3;
    volume.clustered = false;
    volume.groupFields.valueY = "sum";

    var keltnerHBand = chart.series.push(new am4charts.LineSeries());
    keltnerHBand.dataFields.valueY = "KELTNER_HBAND";
    keltnerHBand.dataFields.dateX = "time";
    keltnerHBand.yAxis = valueAxis;
    keltnerHBand.cursorTooltipEnabled = false;
    keltnerHBand.stroke = am4core.color("blue").lighten(0.5);

    var keltnerMBand = chart.series.push(new am4charts.LineSeries());
    keltnerMBand.dataFields.valueY = "KELTNER_MBAND";
    keltnerMBand.dataFields.dateX = "time";
    keltnerMBand.yAxis = valueAxis;
    keltnerMBand.cursorTooltipEnabled = false;
    keltnerMBand.strokeDasharray = "8,4,2,4";
    keltnerMBand.stroke = am4core.color("blue").lighten(0.5);

    var keltnerLBand = chart.series.push(new am4charts.LineSeries());
    keltnerLBand.dataFields.valueY = "KELTNER_LBAND";
    keltnerLBand.dataFields.dateX = "time";
    keltnerLBand.yAxis = valueAxis;
    keltnerLBand.cursorTooltipEnabled = false;
    keltnerLBand.stroke = am4core.color("blue").lighten(0.5);

    var macd = chart.series.push(new am4charts.LineSeries());
    macd.dataFields.valueY = "MACD";
    macd.dataFields.dateX = "time";
    macd.yAxis = valueAxis2;
    macd.cursorTooltipEnabled = false;
    macd.stroke = am4core.color("blue").lighten(0.5);

    var macdSignal = chart.series.push(new am4charts.LineSeries());
    macdSignal.dataFields.valueY = "MACD_SIGNAL";
    macdSignal.dataFields.dateX = "time";
    macdSignal.yAxis = valueAxis2;
    macdSignal.cursorTooltipEnabled = false;
    macdSignal.strokeDasharray = "8,4,2,4";
    macdSignal.stroke = am4core.color("blue").lighten(0.5);

    var tradingRange = chart.series.push(new am4charts.LineSeries());
    tradingRange.dataFields.valueY = "STOP_LOSS";
    tradingRange.dataFields.openValueY = "TAKE_PROFIT";
    tradingRange.dataFields.dateX = "time";
    tradingRange.yAxis = valueAxis;
    tradingRange.fill = am4core.color("gray").lighten(0.5);
    tradingRange.fillOpacity = 0.3;
    tradingRange.cursorTooltipEnabled = false;
    tradingRange.stroke = am4core.color("gray").lighten(0.5);
    tradingRange.strokeOpacity = 0.3;

    $.getJSON("/ticker.json?interval=60min", function (data) {
        chart.data = data;
    });

    $("#pills-15min-tab").click(function () {
        if (!$("#pills-15min-tab").hasClass("active")) {
            $("#pills-15min-tab").toggleClass("active");
            $("#pills-1h-tab").removeClass("active");
            $("#pills-1d-tab").removeClass("active");
        }

        $.getJSON("/ticker.json?interval=15min", function (data) {
            if (!_.isEqual(chart.data, data)) {
                chart.data = data;
            }
        });
    });

    $("#pills-1h-tab").click(function () {
        if (!$("pills-1h-tab").hasClass("active")) {
            $("#pills-15min-tab").removeClass("active");
            $("#pills-1h-tab").toggleClass("active");
            $("#pills-1d-tab").removeClass("active");
        }

        $.getJSON("/ticker.json?interval=60min", function (data) {
            if (!_.isEqual(chart.data, data)) {
                chart.data = data;
            }
        });
    });

    $("#pills-1d-tab").click(function () {
        if (!$("pills-1d-tab").hasClass("active")) {
            $("#pills-15min-tab").removeClass("active");
            $("#pills-1h-tab").removeClass("active");
            $("#pills-1d-tab").toggleClass("active");
        }

        $.getJSON("/ticker.json?interval=1d", function (data) {
            if (!_.isEqual(chart.data, data)) {
                chart.data = data;
            }
        });
    });

    $("#pills-right-tab").click(function () {
        if (!$("#pills-1h-tab").hasClass("active")) {
            $("#pills-15min-tab").removeClass("active");
            $("#pills-1h-tab").toggleClass("active");
            $("#pills-1d-tab").removeClass("active");
        }

        $.getJSON("/ticker.json?interval=60min&next=true", function (data) {
            if (!_.isEqual(chart.data, data)) {
                chart.data = data;
            }
        });
    });

    $("#place-order-form").on('submit', function (e) {
        e.preventDefault();

        order = {
            "order_type": $("#order_type").val(),
            "price": $("#price").val(),
            "order_size": $("#order_size").val(),
            "take_profit": $("#take_profit").val(),
            "stop_loss": $("#stop_loss").val(),
        };

        $.post("/place-order", order)
            .done(function (r) {
                $("#ok-submit-msg").text(r.message);
                $("#ok-submit").show();
                $("#error-submit").hide();

                $.getJSON("/ticker.json?interval=60min&next=true", function (data) {
                    if (!_.isEqual(chart.data, data)) {
                        chart.data = data;
                    }
                });
            })
            .fail(function (r) {
                $("#error-submit-msg").text(r.responseJSON.message);
                $("#ok-submit").hide();
                $("#error-submit").show();
            });

        if (!$("#pills-1h-tab").hasClass("active")) {
            $("#pills-15min-tab").removeClass("active");
            $("#pills-1h-tab").toggleClass("active");
            $("#pills-1d-tab").removeClass("active");
        }
    });

    $("select[id='order_type']").on("change", function () {
        if ($(this).val() === "SHORT") {
            $("input[id='price']").prop("disabled", true);
        } else {
            $("input[id='price']").prop("disabled", false);
        }
    });

    $("#exit-trade").click(function () {
        $.getJSON("/exit-trade")
            .done(function (r) {
                $("#ok-submit-msg").text(r.message);
                $("#ok-submit").show();
                $("#error-submit").hide();
            })
            .fail(function (r) {
                $("#error-submit-msg").text(r.responseJSON.message);
                $("#ok-submit").hide();
                $("#error-submit").show();
            });
    });
});