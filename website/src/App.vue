<template>
    <div class="main-content">
        <drawarea v-if="drawing" v-on:draw_state_change="this.drawing = !this.drawing" v-on:points="recieve_points"/>
        <div class="diagonal" v-if="drawing"></div>
        <streets :isdrawing="drawing" :vertices="graph" :edges="edges" :points="embeded_points" :subgraph="chosen_subgraph"/>
    </div>
    <toolbar v-on:play_button_press="play_button_press" v-on:draw_state_change="this.drawing = !this.drawing" :loss="loss" :canplay="!drawing && points && curr_params" :isdrawing="drawing"/>
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
      drawing: true,
      edges: large_arrays.edges,
      graph: large_arrays.verts,
      points: null,
      loss: null,
      embeded_points: null,
      chosen_subgraph: null,
      curr_params: null,
    }
  },
  methods: {
    edges2str() {
        let str = `${this.edges.length}\n`
        this.edges.forEach(e => {
            str += `${e[0]} ${e[1]} ${e[2]} ${e[3]}\n`
        })
        return str
    },
    points2str() {
      if (this.$api_v == 1) {
        let str = `${this.points.length}\n`
        this.points.forEach(p => {
            str += `${p[0]} ${p[1]}\n`
        })
        return str
      } else if (this.$api_v == 2) {
        let str = ''
        this.points.forEach(points => {
          str += `${points.length}\n`
          points.forEach(p => {
            str += `${p[0]} ${p[1]}\n`
          })
          return str
        })
      }
    },
    buildrequest(string) {
      return {
        headers: {'content-type': 'application/x-www-form-urlencoded'},
        body: 'full_data=' + encodeURIComponent(string),
        method: 'POST',
      }
    },
    str2arr(string) {
      let arr = string.split("\n")
      let n = parseFloat(arr[0])
      for (let i = 1; i < arr.length-1; i++) {
        arr[i-1] = arr[i].split(" ").map(parseFloat)
      }
      arr.pop() // for the 1st element that was overwritten
      arr.pop() // remove blank line from last \n
      if (n != arr.length) {
        console.error("bad things")
      }
      return arr
    },
    async recieve_points(v) {
      this.points = v

      if (this.$api_v == 1) {
        this.shared_code(params)
        let result = await fetch(this.$host, this.buildrequest("get_init"));
        const params = await result.text()
        this.curr_params = params
      } else {
        this.doapi2()
      }
    },
    async doapi2() {
      const pts = this.points2str()
      
    },
    // plot things that depend on params
    async shared_code(params) {
      const pts = this.points2str()
      const edges = this.edges2str() 

      let str = 'loss\n' + pts + edges + params
      fetch(this.$host, this.buildrequest(str))
        .then(res => res.text())
        .then(res => this.loss = res)

      str = 'embed_points\n' + pts + '0\n' + params
      let result = await fetch(this.$host, this.buildrequest(str))
      this.embeded_points = this.str2arr(await result.text())

      str = 'subgraph\n' + pts + edges + params
      result = await fetch(this.$host, this.buildrequest(str))
      this.chosen_subgraph = this.str2arr(await result.text())
    },
    async play_button_press() {
      const pts = this.points2str()
      const edges = this.edges2str()
      let str = 'GD_iter\n' + pts + edges + this.curr_params
      let result = await fetch(this.$host, this.buildrequest(str))
      const params = await result.text()
      this.curr_params = params
      this.shared_code(params)
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
