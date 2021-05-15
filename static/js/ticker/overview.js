function createRatiosChart(tickerInfoOverview) {
    let ratiosChart = am4core.create("ratios", am4charts.XYChart);
    // Increase contrast by taking evey second color
    ratiosChart.colors.step = 2;

    // Create axes
    var dateAxis = ratiosChart.xAxes.push(new am4charts.DateAxis());
    var valueAxis = ratiosChart.yAxes.push(new am4charts.ValueAxis());

    var ratioSeries = ratiosChart.series.push(new am4charts.LineSeries());
    ratioSeries.dataFields.valueY = "currentRatio";
    ratioSeries.dataFields.dateX = "date";
    ratioSeries.strokeWidth = 2;
    ratioSeries.yAxis = valueAxis;
    ratioSeries.name = "Curent ratio";
    ratioSeries.tooltipText = "Curent ratio: [bold]{valueY}[/]";
    ratioSeries.tensionX = 0.8;

    // Add legend
    ratiosChart.legend = new am4charts.Legend();

    // Add cursor
    ratiosChart.cursor = new am4charts.XYCursor();

    var ratios = [];
    var quarterlyData = _.map(
        _.zip(
            tickerInfoOverview.balanceSheet.quarterlyReports,
            tickerInfoOverview.cashFlow.quarterlyReports,
            tickerInfoOverview.incomeStatement.quarterlyReports
        ),
        function (item) {
            return _.extend(item[0], item[1], item[2]);
        }
    );

    _.each(quarterlyData, function (item) {
            if (item !== undefined && item.fiscalDateEnding !== "None") {
                var formatter = new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: item.reportedCurrency,
                });

                ratios.push({
                    date: new Date(item.fiscalDateEnding),
                    currentRatio: currentRatio(item),
                    cashConversionCycle: cashConversionCycle(item),
                    debtRatio: debtRatio(item),
                    interestCoverage: interestCoverage(item),
                    returnOnAssets: returnOnAssets(item),
                    returnOnEquity: returnOnEquity(item),
                });
            }
        }
    );

    ratios = _.sortBy(ratios, ["date"])
    ratiosChart.data = ratios;

    return ratiosChart;
}

function updateRatiosChart(ratiosChart, ratio) {
    let ratioSeries = ratiosChart.series.getIndex(0)

    if (ratio === "currentRatio") {
        ratioSeries.dataFields.valueY = "currentRatio";
        ratioSeries.name = "Current ratio";
        ratioSeries.tooltipText = "Current ratio: [bold]{valueY}[/]";
    } else if (ratio === "cashConversionCycle") {
        ratioSeries.dataFields.valueY = "cashConversionCycle";
        ratioSeries.name = "Cash conversion cycle";
        ratioSeries.tooltipText = "Cash conversion cycle: [bold]{valueY}[/]";
    } else if (ratio === "debtRatio") {
        ratioSeries.dataFields.valueY = "debtRatio";
        ratioSeries.name = "Debt ratio";
        ratioSeries.tooltipText = "Debt ratio: [bold]{valueY}[/]";
    } else if (ratio === "interestCoverage") {
        ratioSeries.dataFields.valueY = "interestCoverage";
        ratioSeries.name = "Interest Coverage";
        ratioSeries.tooltipText = "Interest Coverage: [bold]{valueY}[/]";
    } else if (ratio === "returnOnAssets") {
        ratioSeries.dataFields.valueY = "returnOnAssets";
        ratioSeries.name = "Return on assets";
        ratioSeries.tooltipText = "Return on assets: [bold]{valueY}[/]";
    } else if (ratio === "returnOnEquity") {
        ratioSeries.dataFields.valueY = "returnOnEquity";
        ratioSeries.name = "Return on equity";
        ratioSeries.tooltipText = "Return on equity: [bold]{valueY}[/]";
    }

    ratiosChart.validateData();
}

function currentRatio(item) {
    if (
        item.totalCurrentAssets !== "None" &&
        item.totalCurrentLiabilities !== "None"
    ) {
        return parseInt(item.totalCurrentAssets) / parseInt(item.totalCurrentLiabilities);
    }

    return null;
}

function cashConversionCycle(item) {
    if (
        item.inventory !== "None" &&
        item.changeInInventory !== "None" &&
        item.costofGoodsAndServicesSold !== "None" &&
        item.currentNetReceivables !== "None" &&
        item.changeInReceivables !== "None" &&
        item.totalRevenue !== "None"
    ) {
        let daysInventoryOutstanding = (
            (
                0.5 * (parseInt(item.inventory) + parseInt(item.inventory) + parseInt(item.changeInInventory))
            ) / parseInt(item.costofGoodsAndServicesSold)
        ) * 90;

        let daysSalesOutstanding = (
            (
                0.5 * (parseInt(item.currentNetReceivables) + parseInt(item.currentNetReceivables) + parseInt(item.changeInReceivables))
            ) / parseInt(item.totalRevenue)
        ) * 90;

        let daysPayablesOutstanding = (
            parseInt(item.currentAccountsPayable) / parseInt(item.costofGoodsAndServicesSold)
        ) * 90;

        return daysInventoryOutstanding + daysSalesOutstanding - daysPayablesOutstanding;
    }

    return null;
}

function debtRatio(item) {
    if (
        item.totalLiabilities !== "None" &&
        item.totalAssets !== "None"
    ) {
        return parseInt(item.totalLiabilities) / parseInt(item.totalAssets);
    }

    return null;
}

function interestCoverage(item) {
    if (
        item.ebit !== "None" &&
        item.interestExpense !== "None"
    ) {
        return parseInt(item.ebit) / parseInt(item.interestExpense);
    }

    return null;
}

function returnOnAssets(item) {
    if (
        item.netIncome !== "None" &&
        item.totalAssets !== "None"
    ) {
        return parseInt(item.netIncome) / parseInt(item.totalAssets);
    }

    return null;
}

function returnOnEquity(item) {
    if (
        item.netIncome !== "None" &&
        item.totalShareholderEquity !== "None"
    ) {
        return parseInt(item.netIncome) / parseInt(item.totalShareholderEquity);
    }

    return null;
}

function formatNews(news) {
    keys = ["Date", "Title", "Link"]

    return _.reduce(
        _.pairs(news),
        function (memo, item) {
            if (!keys.includes(item[0]) && item[1] !== null) {
                return memo + "" + item[0] + ": " + item[1] + ", ";
            } else {
                return memo;
            }
        },
        "")
}