<template>
  <div class="container" id="colors">
    <img class="the-map" src="@/assets/map.png" alt="map of Providence, RI"/>
    <canvas id="yoink"></canvas>
  </div>
</template>

<script>
export default{
  props: ['isdrawing', 'graph'],
  data() {
    return {
    }
  },
  watch: {
    isdrawing: function() {
      const d = document.getElementById("colors")
      // d.style.backgroundColor = this.isdrawing ? "var(--red)" : "var(--blue)"
    }
  },
  methods: {
    drawLine(x1, y1, x2, y2) {
        let ctx = this.canvas;
        ctx.beginPath();
        ctx.strokeStyle = 'black';
        ctx.lineWidth = 1;
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.closePath();
    },
    drawpoint(x, y) {
        const ctx = this.canvas
        const old_style = ctx.fillStyle
        ctx.fillStyle = "#FF0000"
        ctx.fillRect(x-2, y-2, 5, 5)
        ctx.fillStyle = old_style
    },
    plot_graph() {
        this.graph.map(p => this.drawLine(p[0][0], p[0][1], p[1][0], p[1][1]))
    },
  },
  mounted() {
    const c = document.getElementById("yoink")
    // c.style.width = `600px`
    // c.width = 600
    // c.style.height = `300px`
    // c.height = 300
    this.canvas = c.getContext("2d")

    this.plot_graph()
  }
}
</script>

<style scoped>
.container {
    max-height: 100%;
    width: 100%;
    z-index: -1;
    overflow: hidden;

    display: grid;
    place-items: center;
    grid-template: 1fr / 1fr;
    height: 100%;
    width: 100%;
}
.container > * {
  grid-column: 1 / 1;
  grid-row: 1 / 1;
}
img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
}
#yoink {
    height: 100%;
    width: 100%;
}
</style>
