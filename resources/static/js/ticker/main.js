am4core.useTheme(am4themes_animated);
am4core.options.minPolylineStep = 5;
am4core.options.queue = true;

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
        return {
            tickerInfoOverview: null,
            tickerInfoNews: null,
            selectedRatio: "currentRatio",
            interval: "60min",
            order: {
                "orderType": "",
                "price": "",
                "orderSize": "",
                "takeProfit": "",
                "stopLoss": "",
            },
            orderActive: false,
        }
    },

    methods: {
        showOrderActions() {
            $("#order-actions").modal("show")
        },
        showTickerInfo() {
            $("#ticker-info").modal("show")
        },
        formatDate(timestamp) {
            return new Date(timestamp).toDateString()
        },
        formatNews(news) {
            return formatNews(news);
        },
        updateRatiosChart(event) {
            this.selectedRatio = event.target.value;
            updateRatiosChart(this.ratiosChart, event.target.value);
        },
        updateOhlcChart(interval, next) {
            updateOhlcChart(this.ohlcChart, interval, next);

            let lastElement = this.ohlcChart.data[this.ohlcChart.data.length -1];
            this.orderActive = lastElement["TAKE_PROFIT"] != null && lastElement["STOP_LOSS"] != null;
        },
        placeOrder() {
            placeOrder(this.ohlcChart, this.order);
        },
        exitTrade() {
            exitTrade();
        },
        newTicker() {
            exitTrade();
            location.href = "/new-ticker";
        },
        onOrderTypeChange(event) {
            if(event.target.value === "SHORT") {
                $("#price").prop( "disabled", true );
            } else {
                $("#price").prop( "disabled", false );
            }
        }
    },

    mounted() {
        axios
            .get("/ticker-info.json")
            .then(response => {
                if (response.request.responseURL.includes("login")) {
                    location.reload();
                }

                this.tickerInfoOverview = response.data.overview;
                this.tickerInfoNews = response.data.news;

                this.ratiosChart = createRatiosChart(this.tickerInfoOverview);
            })
            .catch(function (error) {
                // handle error
                console.log(error);
            })

        axios
            .get("/ticker.json?interval=" + this.interval)
            .then(response => {
                if (response.request.responseURL.includes("login")) {
                    location.reload();
                }

                let lastElement = response.data[response.data.length -1];
                this.orderActive = lastElement["TAKE_PROFIT"] != null && lastElement["STOP_LOSS"] != null;

                this.ohlcChart = createOhlcChart(response.data);
            })
            .catch(function (error) {
                // handle error
                console.log(error);
            })
    },

    beforeUnmount() {
        if (this.ratiosChart) {
            this.ratiosChart.dispose();
        }
    }
})

app.mount("#ticker");
