am4core.useTheme(am4themes_animated);
am4core.options.minPolylineStep = 5;

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
            .get("/ticker-info.json")
            .then(response => {
                this.tickerInfoOverview = response.data.overview;
                this.tickerInfoNews = response.data.news;

                this.ratiosChart = createRatiosChart(this.tickerInfoOverview);
            })

        axios
            .get("/ticker.json?interval=" + this.interval)
            .then(response => {
                this.ohlcChart = createOhlcChart(response.data);
            })
    },

    beforeUnmount() {
        if (this.ratiosChart) {
            this.ratiosChart.dispose();
        }
    }
})

app.mount("#ticker");
