<template>
  <div class="container" id="colors">
</div>
</template>

<script>
export default{
  props: ['isdrawing'],
  data() {
    return {
    }
  },
  watch: {
    isdrawing: function() {
      const d = document.getElementById("colors")
      d.style.backgroundColor = this.isdrawing ? "var(--red)" : "var(--blue)"
    }
  },
}
</script>

<style scoped>
.myclass {
    background-color: var(--blue);
}
.container {
    background-color: var(--red);
    height: 100%;
    width: 100%;
    z-index: -1;
}
</style>
