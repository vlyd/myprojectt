<!-- components/AppCard.vue -->
<template>
  <div :class="['card', { 'card-center': center }]">
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'AppCard',
  props: {
    center: {
      type: Boolean,
      default: true
    }
  }
}
</script>
