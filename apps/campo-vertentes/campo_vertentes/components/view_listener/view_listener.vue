<template>
  <div :style="style">
    <jupyter-widget
      v-for="child in children"
      :key="child"
      :widget="child"
    ></jupyter-widget>
  </div>
</template>

<script>
module.exports = {
  created() {
    this.resizeObserver = new ResizeObserver((entries) => {
      this._updateViewData();
    });
  },
  mounted() {
    this.resizeObserver.observe(this.$el);
    this._updateViewData();
  },
  destroyed() {
    this.resizeObserver.unobserve(this.$el);
  },
  methods: {
    _updateViewData() {
      const view_data = {
        width: this.$el.clientWidth,
        height: this.$el.clientHeight,
      };
      this.view_data = view_data;
    },
  },
};
</script>

<style id="viewlistener"></style>
