<template>
  <div class="container" id="colors">
    <img id="the-map" src="@/assets/map.png" alt="map of Providence, RI"/>
    <div id="hi"></div>
    <canvas id="yoink"></canvas>
  </div>
</template>

<script>
export default{
  props: ['isdrawing', 'vertices', 'edges'],
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
        ctx.fillRect(x-1.5, y-1.5, 3, 3)
        ctx.fillStyle = old_style
    },
    gps2pixels(gps) {
            // if you ever want to nicely recompute ly, lx, hx, hy
            /* const mx = -71.3921 */
            /* const my = 41.83326 */

            /* const dx = 0.081 */
            /* const dy = 0.0405 */

            /* const hy = my + dy/2 */
            /* const ly = my - dy/2 */
            /* const hx = mx + dx/2 */
            /* const lx = mx - dx/2 */
            /* console.log(`const ly = ${ly}`) */
            /* console.log(`const lx = ${lx}`) */
            /* console.log(`const hx = ${hx}`) */
            /* console.log(`const hy = ${hy}`) */


            // (hy, lx)
            // |---------|
            // |         }
            // |         }
            // |         }
            // |         }
            // ----------- (ly, hx)
            const ly = 41.813010000000006
            const lx = -71.4326
            const hx = -71.3516
            const hy = 41.85351

            const c = document.getElementById("yoink")
            const canvas_width = c.width
            const canvas_height = c.height

            const img_width = hx-lx
            const img_height = hy-ly
            const y = gps[0]
            const x = gps[1]
            const py = (hy - y) * (canvas_height/img_height)
            const px = (x - lx) * (canvas_width/img_width)
            return [px, py]
    },
    plot_graph() {
        this.vertices.forEach((gps) => {
            const p = this.gps2pixels(gps)
            this.drawpoint(p[0],p[1])
        })
        this.edges.forEach((edge) => {
            const p = this.gps2pixels(edge.slice(0,2))
            const q = this.gps2pixels(edge.slice(2,4))
            this.drawLine(p[0], p[1], q[0], q[1])
        })
    },
  },
  mounted() {
    const c = document.getElementById("yoink")
    const img = document.getElementById("the-map")
    const rect = c.getBoundingClientRect()

    const width = img.clientWidth
    const height = img.clientHeight

    c.width = width
    c.height = height
    c.style.width = width
    c.style.height = height

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

    position: relative;
    height: 100%;
    width: 100%;
}
.container > * {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
}
img {
    width: 100%;
    height: 100%;
    object-fit: fill;
}
canvas {
    height: 100%;
    width: 100%;
}
#hi {
    height: 100%;
    width: 100%;
}
</style>
