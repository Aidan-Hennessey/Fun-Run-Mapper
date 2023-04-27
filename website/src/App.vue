<template>
    <div class="main-content">
        <drawarea v-if="drawing" v-on:draw_state_change="this.drawing = !this.drawing" v-on:points="recieve_points"/>
        <div class="diagonal" v-if="drawing"></div>
        <streets :isdrawing="drawing" :vertices="graph" :edges="edges"/>
    </div>
    <toolbar v-on:draw_state_change="this.drawing = !this.drawing"/>
</template>

<script>
import mybutton from "./components/mybutton.vue"
import drawarea from "./components/drawarea/index.vue"
import streets from "./components/streets/index.vue"
import toolbar from "./components/toolbar/index.vue"

import large_arrays from "./assets/arr.js"

export default{
  components: {mybutton,drawarea,streets,toolbar},
  data() {
    return {
      drawing: false,
      edges: large_arrays.edges,
      graph: large_arrays.verts,
      points: null,
    }
  },
  methods: {
    recieve_points(v) {
      this.points = v
      const request = {
        headers: {'content-type': 'application/x-www-form-urlencoded'},
        body: 'full_data=' + encodeURIComponent("loss\n2\n0.1232132 9.932432\n2.432432 0.32432423\n1\n0.123123 43.2342 9.2342323 0.32423\n0.32432\n1.32423\n34.32432\n1.231\n0.9823"),
        method: 'POST',
      }
      console.log("here")
      fetch(this.$host, request)
        .then(res => res.json())
        .then(res => console.log(res))
    }
  }
}
</script>

<style>
:root {
  --background-grey: #E6E8EB;
  --text-grey: #9FA2A9;
  --blue: #639AF8;
  --yellow: #ffcc00;
  --green: #98c379;
  --yellow: #e5c07b;
  --dark-yellow: #d19a66;
  --purple: #c678dd;
  --aqua: #56b6c2;
  --red: #E06C75;
  --black: #000;
  --white: #fff;
  --icon-grey: #A1A2A3;
}
*{
  box-sizing: inherit;
}
html, body{
  margin: 0;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
}
#app{
  padding-top: calc(env(safe-area-inset-top) + var(--vert-padding));
  padding-bottom: calc(env(safe-area-inset-bottom) + var(--vert-padding));
  padding-left: calc(env(safe-area-inset-left) + var(--horizontal-padding));
  padding-right: calc(env(safe-area-inset-right) + var(--horizontal-padding));
  margin: 0;
  height: 100%;
  width: 100%;
}
.main-content {
  display: grid;
  place-items: center;
  grid-template: 1fr / 1fr;
  height: 100%;
  width: 100%;
}
.main-content> * {
  grid-column: 1 / 1;
  grid-row: 1 / 1;
}
.diagonal {
  height: 100%;
  width: 100%;
  /* taken from: https://codepen.io/geebru/pen/EveKYr */
  background-image: repeating-linear-gradient(-45deg, 
    #bbb 10px,
    #bbb 12px,
    transparent 12px,
    transparent 20px);
    z-index: 0;
}
</style>
