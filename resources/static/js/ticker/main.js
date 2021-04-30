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
        },
        placeOrder() {
            placeOrder(this.ohlcChart, this.order);
        },
        exitTrade() {
            exitTrade();
        }
    },

    mounted() {
        axios
            .get(window.location.origin + "/ticker-info.json")
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
            .get(window.location.origin + "/ticker.json?interval=" + this.interval)
            .then(response => {
                if (response.request.responseURL.includes("login")) {
                    location.reload();
                }

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
