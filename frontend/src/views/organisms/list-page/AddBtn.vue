<script setup>
import { useRouter } from 'vue-router'
import PlusIconBtn from '@/components/molecules/buttons/PlusIconBtn.vue'

const router = useRouter()

const onClick = (event) => {
  event?.stopPropagation?.()
  router.push('/update')
}
</script>

<template>
  <PlusIconBtn aria-label="신규 등록" size="sm" @click="onClick" />
</template>
