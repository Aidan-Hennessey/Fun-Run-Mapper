<template>
  <div class="container">
    <canvas @mousedown="beginDrawing" @mousemove="keepDrawing" @mouseup="stopDrawing" id="drawing-board"></canvas>
    <mybutton @click="rec_button_clicked" text="🔴 REC"></mybutton>
</div>
</template>

<script>
import mybutton from "../mybutton.vue"

export default{
  emits: ["draw_state_change", "points"],
  components: {mybutton},
  data() {
    return {
      list_of_points: Array(),
      x: 0,
      y: 0,
      canvas: null,
      isPainting: false,
    }
  },
  // code from https://codepen.io/reiallenramos/pen/MWaEmpw
  // looked at https://www.youtube.com/watch?v=mRDo-QXVUv8&ab_channel=JavaScriptAcademy
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
    beginDrawing(e) {
      this.x = e.offsetX;
      this.y = e.offsetY;
      this.isPainting = true;
    },
    keepDrawing(e) {
      if (this.isPainting === true) {
        this.drawLine(this.x, this.y, e.offsetX, e.offsetY);
        this.x = e.offsetX;
        this.y = e.offsetY;
        // draw points
        if (Math.random() < 0.5) {
            const c = document.getElementById("drawing-board")
            const width = c.width
            const height = c.height
            this.list_of_points.push([this.x/width, this.y/height])

            this.drawpoint(this.x, this.y)
        }
      }
    },
    stopDrawing(e) {
      if (this.isPainting === true) {
        this.drawLine(this.x, this.y, e.offsetX, e.offsetY);
        this.x = 0;
        this.y = 0;
        this.isPainting = false;
      }
    },
    rec_button_clicked() {
        this.$emit('draw_state_change')
        this.$emit('points', this.list_of_points)
    }
  },
  mounted() {
    const c = document.getElementById("drawing-board")
    c.style.width = `600px`
    c.width = 600
    c.style.height = `300px`
    c.height = 300
    this.canvas = c.getContext("2d")
  }
}
</script>

<style scoped>
.container{
  display: flex;
  flex-direction: column;
  row-gap: 5px;
  align-items: center;
  justify-content: center;
  z-index: 1;
}
canvas {
    border: 5px solid var(--blue);
    background-color: #fff;
}
</style>
