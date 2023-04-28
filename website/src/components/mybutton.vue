<template>
    <button :style="mystyle"><img v-if="icon" :src="icon"/> {{text}}</button>
</template>

<script>
import path from "path-browserify";

export default {
    props: ['text', 'icon', 'isactive'],
    computed: {
      mystyle() {
        return !this.isactive ? "" : "opacity: 50%"
      }
    }
}
</script>

<style scoped>
button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.3em 0.9em;
  font-size: 1em;
  font-weight: 500;
  background-color: #f9f9f9;
  cursor: pointer;
  transition: border-color 0.25s;
  font-family: inherit;
}
button:hover {
  border-color: #646cff;
}
button:focus,
button:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
}
img {
  height: 12px;
}
</style>
