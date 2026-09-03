<script setup>
import { computed, ref, watch } from 'vue'

import Button from '@/components/atoms/Button.vue'
import Input from '@/components/atoms/Input.vue'
import ModalBackdrop from '@/components/atoms/modal/ModalBackdrop.vue'
import ModalCard from '@/components/atoms/modal/ModalCard.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false,
  },
  field: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'select'])
const query = ref('')

const filteredOptions = computed(() => {
  const normalizedQuery = query.value.trim().toLowerCase()
  const options = Array.isArray(props.field?.options) ? props.field.options : []
  if (!normalizedQuery) {
    return options
  }
  return options.filter((option) => String(option?.label || '').toLowerCase().includes(normalizedQuery))
})

const selectOption = (option) => {
  emit('select', option?.value)
  emit('close')
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      query.value = ''
    }
  },
)
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center px-4" @click.self="emit('close')">
    <ModalBackdrop />
    <ModalCard class="relative max-w-lg">
      <header class="mb-4 flex items-center justify-between gap-3">
        <h2 class="text-lg font-semibold text-slate-900">{{ field?.label }} 검색</h2>
        <Button size="sm" variant="secondary" @click="emit('close')">닫기</Button>
      </header>

      <Input v-model="query" size="sm" :placeholder="`${field?.label || ''} 검색`" />

      <ul class="mt-3 max-h-72 overflow-y-auto rounded-lg border border-slate-200">
        <li v-for="option in filteredOptions" :key="option.value" class="border-b border-slate-100 last:border-b-0">
          <button
            type="button"
            class="w-full px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
            @click="selectOption(option)"
          >
            {{ option.label }}
          </button>
        </li>
        <li v-if="filteredOptions.length === 0" class="px-3 py-6 text-center text-sm text-slate-500">
          검색 결과가 없습니다.
        </li>
      </ul>
    </ModalCard>
  </div>
</template>