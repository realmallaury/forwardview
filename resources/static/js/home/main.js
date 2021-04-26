am4core.useTheme(am4themes_animated);
am4core.options.minPolylineStep = 5;

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data() {
        return {}
    },

    methods: {},

    mounted() {

    },

    beforeUnmount() {

    }
})

app.mount("#home");
