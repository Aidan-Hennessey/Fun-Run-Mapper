<template>
  <div class="container">
    <div class="intermediate">
        <mybutton @click="tryplay1" text="Algorithm 1" :icon="play" :isactive="!canplay1"/>
        <mybutton @click="tryplay2" text="Algorithm 2" :icon="play" :isactive="!canplay2"/>
        <mybutton @click="$emit('draw_state_change')" :text="mytext" :icon="myicon"/>
    </div>
    <div class="intermediate">
        <h1>Miles: {{calc_miles()}}</h1>
        <h1 id="loss">Loss: {{calc_loss()}}</h1>
    </div>
    <div class="intermediate">
        <mybutton @click="nyi" text="Share" :icon="share"/>
        <button @click="nyi">?</button>
    </div>
  </div>
</template>

<script>
import mybutton from "../mybutton.vue"
import play from "@/assets/play.svg"
import plus from "@/assets/plus.svg"
import map from "@/assets/map.svg"
import share from "@/assets/share.svg"

export default{
  props: ["loss", "canplay1", "canplay2", "isdrawing", "miles"],
  emits: ["draw_state_change", "play_button_press", "v2_button_press"],
  components: {mybutton},
  data() {
    return {
      play: play,
      plus: plus,
      map: map,
      share: share,
    }
  },
  computed: {
    mytext() {
      return this.isdrawing ? 'Map' : 'New'
    },
    myicon() {
      return this.isdrawing ? map : plus
    }
  },
  methods: {
    calc_loss() {
      if (this.loss) {
        return Math.round(this.loss * 1e9) / 100
      } else {
        return '-.-'
      }
    },
    calc_miles() {
      if (this.miles) {
        return Math.round(this.miles * 100) / 100
      } else {
        return '-.-'
      }
    },
    nyi() {
      alert("not implemented")
    },
    tryplay2() {
      if (this.canplay2) {
        this.$emit('play2_button_press')
      }
    },
    tryplay1() {
      if (this.canplay1) {
        this.$emit('play1_button_press')
      }
    }
  },
}
</script>

<style scoped>
.container {
    background-color: var(--aqua);
    position: fixed;
    bottom: 0;
    height: 50px;
    width: 100%;
    display: flex;
    justify-content: space-around;
    align-items: center;
}
.intermediate {
    display: flex;
    justify-content: space-around;
    column-gap: 10px;
    align-items: center;
}
h1 {
    font-size: 18px;
    font-family: inherit;
}
#loss {
    width: 120px;
}
</style>
