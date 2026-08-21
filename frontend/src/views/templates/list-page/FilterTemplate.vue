<script setup>
import { computed } from 'vue'

import Button from '@/components/atoms/Button.vue'
import BooleanInputField from '@/components/molecules/inputs/BooleanInputField.vue'
import DateInputField from '@/components/molecules/inputs/DateInputField.vue'
import DropdownInputField from '@/components/molecules/inputs/DropdownInputField.vue'
import NumberInputField from '@/components/molecules/inputs/NumberInputField.vue'
import TextInputField from '@/components/molecules/inputs/TextInputField.vue'

const props = defineProps({
  fields: {
    type: Array,
    default: () => [],
  },
  optionsMap: {
    type: Object,
    default: () => ({}),
  },
  modelValue: {
    type: Object,
    default: () => ({}),
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const sortedFields = computed(() => {
  return [...props.fields].sort((a, b) => Number(a?.list_order ?? 9999) - Number(b?.list_order ?? 9999))
})

const resolveInputComponent = (inputType) => {
  if (inputType === 'dropdown') {
    return DropdownInputField
  }
  if (inputType === 'number') {
    return NumberInputField
  }
  if (inputType === 'date') {
    return DateInputField
  }
  if (inputType === 'boolean') {
    return BooleanInputField
  }
  return TextInputField
}

const updateFieldValue = (fieldKey, value) => {
  emit('update:modelValue', {
    ...(props.modelValue || {}),
    [fieldKey]: value,
  })
}

const getOptions = (field) => {
  if (Array.isArray(field?.options) && field.options.length > 0) {
    return field.options
  }

  const source = field?.option_source
  if (!source) {
    return []
  }
  return props.optionsMap[source] || []
}
</script>

<template>
  <section class="space-y-3 rounded-xl border border-slate-200 bg-white p-4">
    <header class="flex items-center justify-between gap-3">
      <h2 class="text-sm font-semibold text-slate-800">검색 필터</h2>
      <div class="flex items-center gap-2">
        <Button size="sm" variant="secondary" :disabled="loading" @click="emit('reset')">
          초기화
        </Button>
        <Button size="sm" :disabled="loading" @click="emit('search')">
          조회
        </Button>
      </div>
    </header>

    <div class="grid grid-cols-1 gap-3 md:grid-cols-3 lg:grid-cols-5">
      <component
        :is="resolveInputComponent(field.input_type)"
        v-for="field in sortedFields"
        :key="field.field_key"
        :label="field.label"
        :model-value="modelValue?.[field.field_key]"
        :options="field.input_type === 'dropdown' ? getOptions(field) : undefined"
        :placeholder="field.input_type === 'dropdown' ? '전체' : undefined"
        @update:model-value="updateFieldValue(field.field_key, $event)"
      />
    </div>
  </section>
</template>