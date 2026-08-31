<script setup>
import IconButton from '@/components/atoms/IconButton.vue'
import BackIcon from '@/components/atoms/icons/BackIcon.vue'

defineProps({
  ariaLabel: {
    type: String,
    default: '뒤로 가기',
  },
})

const emit = defineEmits(['click'])
</script>

<template>
  <IconButton variant="ghost" rounded outlined :aria-label="ariaLabel" @click="emit('click', $event)">
    <BackIcon />
  </IconButton>
</template>