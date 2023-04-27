<template>
  <div class="container">
    <div class="intermediate">
        <mybutton @click="$emit('play_button_press')" text="▶ Play"/>
        <mybutton @click="$emit('draw_state_change')" text="➕ New"/>
    </div>
    <div class="intermediate">
        <h1>Miles: -.-</h1>
        <h1>Loss: {{loss}}</h1>
    </div>
    <div class="intermediate">
        <button @click="nyi">Share</button>
        <button @click="nyi">?</button>
    </div>
  </div>
</template>

<script>
import mybutton from "../mybutton.vue"

export default{
  props: ["loss"],
  emits: ["draw_state_change", "play_button_press"],
  components: {mybutton},
  data() {
    return {
    }
  },
  methods: {
    nyi() {
      alert("not implemented")
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
</style>
