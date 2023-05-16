<template>
    <div class="main-content">
        <drawarea v-if="drawing" v-on:draw_state_change="this.drawing = !this.drawing" v-on:points="recieve_points"/>
        <div class="diagonal" v-if="drawing"></div>
        <streets 
          :isdrawing="drawing" 
          :vertices="graph" 
          :edges="edges" 
          :points="embeded_points" 
          :subgraph="chosen_subgraph" 
          :generation="generation"/>
    </div>
    <toolbar 
      v-on:play1_button_press="play_button_press" 
      v-on:play2_button_press="doapi2" 
      v-on:draw_state_change="this.drawing = !this.drawing" 
      :loss="loss" 
      :canplay1="!drawing && points && curr_params" 
      :canplay2="!drawing && points" 
      :miles="calc_miles()" 
      :isdrawing="drawing"/>
</template>

<script>
import mybutton from "./components/mybutton.vue"
import drawarea from "./components/drawarea/index.vue"
import streets from "./components/streets/index.vue"
import toolbar from "./components/toolbar/index.vue"

import raw_verts from "./assets/verts.txt" // using raw-loader on .txt files
import raw_edges from "./assets/edge_list.txt" // using raw-loader on .txt files
import { getTransitionRawChildren } from "vue"

export default{
  components: {mybutton,drawarea,streets,toolbar},
  data() {
    return {
      drawing: true,
      edges: this.raw_to_arr(raw_edges),
      graph: this.raw_to_arr(raw_verts),
      points: null,
      loss: null,
      embeded_points: null,
      chosen_subgraph: null,
      curr_params: null,
      generation: 0,
    }
  },
  methods: {
    raw_to_arr(raw) {
      let arr = raw.split("\n").map(x => x.split(" ").map(parseFloat))
      return arr
    },
    gps_dist(lat1, lon1, lat2, lon2) {
      // https://www.movable-type.co.uk/scripts/latlong.html?from=49.1715000,-121.7493500&to=49.18258,-121.75441
      const R = 6371e3; // metres
      const φ1 = lat1 * Math.PI/180; // φ, λ in radians
      const φ2 = lat2 * Math.PI/180;
      const Δφ = (lat2-lat1) * Math.PI/180;
      const Δλ = (lon2-lon1) * Math.PI/180;

      const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                Math.cos(φ1) * Math.cos(φ2) *
                Math.sin(Δλ/2) * Math.sin(Δλ/2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

      const d = R * c;
      return d / 1609
    },
    calc_miles() {
      if (this.chosen_subgraph) {
        return this.chosen_subgraph.reduce((acc, e) =>
          acc + this.gps_dist(e[0], e[1], e[2], e[3]),
          0
        )
      } else {
        return null
      }
    },
    edges2str() {
        let str = `${this.edges.length}\n`
        this.edges.forEach(e => {
            str += `${e[0]} ${e[1]} ${e[2]} ${e[3]}\n`
        })
        return str
    },
    points2str(api) {
      if (api == 1) {
        const len = this.points.reduce((acc, val) => acc + val.length, 0)
        let str = `${len}\n`
        str += this.points.reduce((acc, l) =>
            acc + l.reduce((acc, p) => acc + `${p[0]} ${p[1]}\n`, "")
        , "")
        return str
      } else if (api == 2) {
        const str = this.points.reduce((acc, l) =>
          acc + `${l.length}\n` + l.reduce((acc, p) =>
            acc + `${p[0]*2} ${p[1]}\n`
          , "")
        , "")
        return str
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
      arr.pop() // for the 1st element (length) that was overwritten
      arr.pop() // remove blank line from last \n
      if (n != arr.length) {
        console.error(`the length specified by backend, ${n} not equal to the length recieved ${arr.length}`)
      }
      return arr
    },
    async recieve_points(v) {
      this.generation += 1
      this.points = v
      let result = await fetch(this.$hostv1, this.buildrequest("get_init"))
      const params = await result.text()
      this.curr_params = params

      this.doapi1()
    },
    async doapi2() {
      this.generation += 1
      const pts = this.points2str(2)
      console.log("sending to api2:")
      console.log(pts)
      fetch(this.$hostv2, this.buildrequest(pts))
        .then(res => res.text())
        .catch(e => {console.error("v2 api failed on input:"); console.log(pts)})
        .then(res => {this.chosen_subgraph = this.str2arr(res)})
    },
    // plot things that depend on params
    async doapi1() {
      const params = this.curr_params
      const pts = this.points2str(1)
      const edges = this.edges2str() 

      const lossstr = 'loss\n' + pts + edges + params
      fetch(this.$hostv1, this.buildrequest(lossstr))
        .then(res => res.text())
        .then(res => this.loss = res)

      const ptsstr = 'embed_points\n' + pts + '0\n' + params
      fetch(this.$hostv1, this.buildrequest(ptsstr))
        .then(res => res.text())
        .then(res => this.embeded_points = this.str2arr(res))

      const substr = 'subgraph\n' + pts + edges + params
      fetch(this.$hostv1, this.buildrequest(substr))
        .then(res => res.text())
        .then(res => this.chosen_subgraph = this.str2arr(res))
    },
    async play_button_press() {
      this.generation += 1
      const pts = this.points2str(1)
      const edges = this.edges2str()
      let str = 'GD_iter\n' + pts + edges + this.curr_params
      let result = await fetch(this.$hostv1, this.buildrequest(str))
      const params = await result.text()
      this.curr_params = params
      this.doapi1(params)
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
