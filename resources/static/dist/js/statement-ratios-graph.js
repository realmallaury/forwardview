am4core.ready(function () {

// Themes begin
    am4core.useTheme(am4themes_animated);
// Themes end

// Create chart instance
    var chart = am4core.create("ratios-div", am4charts.XYChart);

    // Increase contrast by taking evey second color
    chart.colors.step = 2;

    // Create axes
    var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

    var grossMargin = chart.series.push(new am4charts.LineSeries());
    grossMargin.dataFields.valueY = "cashflowRatio";
    grossMargin.dataFields.dateX = "date";
    grossMargin.strokeWidth = 2;
    grossMargin.yAxis = valueAxis;
    grossMargin.name = "Cash flow ratio";
    grossMargin.tooltipText = "Cash flow ratio: [bold]{valueY}[/]";
    grossMargin.tensionX = 0.8;

    // Add legend
    chart.legend = new am4charts.Legend();

    // Add cursor
    chart.cursor = new am4charts.XYCursor();

    $.getJSON("/ticker-info.json", function (data) {
        var ratios = [];
        var quarterlyData = _.map(
            _.zip(
                data.overview.balanceSheet.quarterlyReports,
                data.overview.cashFlow.quarterlyReports,
                data.overview.incomeStatement.quarterlyReports
            ),
            function (item) {
                return _.extend(item[0], item[1], item[2]);
            });

        _.each(quarterlyData, function (item) {
            if (item !== undefined) {
                var formatter = new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: item.reportedCurrency,
                });

                ratios.push({
                    date: new Date(item.fiscalDateEnding),
                    grossMargin: item.grossProfit / item.totalRevenue,
                    profitMargin: item.netIncome / item.totalRevenue,
                    cashflowRatio: item.operatingCashflow / item.totalCurrentLiabilities,
                });
            }
        });

        ratios = _.sortBy(ratios, ["date"])
        chart.data = ratios;
    });

    $("#pills-right-tab").click(function () {
        getTickerInfo();
    });

    getTickerInfo();
});

function getTickerInfo() {
    $.getJSON("/ticker-info.json", function (data) {
        var news = "";
        _.each(data.news, function (item) {
            li = "<ul><li>" + new Date(item.Date).toDateString() + "<br>"
            delete item.Date

            if (item.Link !== null) {
                li = li + "<a href=\"" + item.Link + "\" target=\"_blank\">" + item.Title + "</a><br>"
            }
            delete item.Title
            delete item.Link

            li = li + _.reduce(
                _.pairs(item),
                function (memo, item) {
                    if (item[1] !== null) {
                        return memo + "" + item[0] + ": " + item[1] + ", ";
                    } else {
                        return memo;
                    }
                },
                "")
            li = li.slice(0, -2);
            news = news + li + "</li></ul>"
        });

        if(news.length > 0) {
            $("#news-body").append(news);
            $("#news-card").show();
        }

        if (data.overview.overview.Name !== undefined) {
            overview = "<h5 class='card-title'>" + data.overview.overview.Name + "</h5>";
            overview = overview + "<div>Sector: " + data.overview.overview.Sector + ", Industry: " + data.overview.overview.Industry + ", " + data.overview.overview.Description + "</div><br>";
            $("#overview-body").html(overview);

            $("#overview-card").show();
        }
    });
}