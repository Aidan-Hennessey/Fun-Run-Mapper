<template>
  <div class="container">
    <div class="intermediate">
        <mybutton @click="tryplay" text="Step" :icon="play" :isactive="!canplay"/>
        <mybutton @click="$emit('draw_state_change')" :text="mytext" :icon="myicon"/>
    </div>
    <div class="intermediate">
        <h1>Miles: -.-</h1>
        <h1 id="loss">Loss: {{Math.round(loss * 1e9) / 100}}</h1>
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
  props: ["loss", "canplay", "isdrawing"],
  emits: ["draw_state_change", "play_button_press"],
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
    nyi() {
      alert("not implemented")
    },
    tryplay() {
      if (canplay) {
        this.$emit('play_button_press')
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
