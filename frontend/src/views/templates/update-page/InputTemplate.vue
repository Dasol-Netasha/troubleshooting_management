<script setup>
import { computed } from 'vue'
import BooleanInputField from '@/components/molecules/inputs/BooleanInputField.vue'
import DateInputField from '@/components/molecules/inputs/DateInputField.vue'
import DropdownInputField from '@/components/molecules/inputs/DropdownInputField.vue'
import MultiDropdownInputField from '@/components/molecules/inputs/MultiDropdownInputField.vue'
import NumberInputField from '@/components/molecules/inputs/NumberInputField.vue'
import TextInputField from '@/components/molecules/inputs/TextInputField.vue'

const props = defineProps({
  fields: {
    type: Array,
    default: () => [],
  },
  values: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update-field', 'open-search'])

const sortedFields = computed(() => {
  return [...(props.fields || [])].sort((a, b) => {
    const left = Number(a?.detail_order ?? 9999)
    const right = Number(b?.detail_order ?? 9999)
    if (left !== right) {
      return left - right
    }
    return String(a?.key).localeCompare(String(b?.key))
  })
})

const normalizeInputType = (inputType) => String(inputType || 'text').trim().toLowerCase()

const resolveInputComponent = (inputType) => {
  if (inputType === 'dropdown') {
    return DropdownInputField
  }
  if (inputType === 'multi_dropdown') {
    return MultiDropdownInputField
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

const getOptions = (field) => {
  return Array.isArray(field?.options) ? field.options : []
}

const getDisplayValue = (field) => {
  const value = props.values[field.key]
  if (normalizeInputType(field.input_type) !== 'search') {
    return value
  }

  const selectedOption = getOptions(field).find((option) => String(option?.value) === String(value))
  return selectedOption?.label ?? value
}
</script>

<template>
  <section class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
    <component
      :is="resolveInputComponent(field.input_type)"
      v-for="field in sortedFields"
      :key="field.key"
      :label="field.label"
      :required="field.required === true"
      :model-value="getDisplayValue(field)"
      :options="['dropdown', 'multi_dropdown', 'search'].includes(normalizeInputType(field.input_type)) ? getOptions(field) : undefined"
      :placeholder="normalizeInputType(field.input_type) === 'dropdown' ? '선택' : normalizeInputType(field.input_type) === 'search' ? '클릭하여 검색' : undefined"
      :readonly="normalizeInputType(field.input_type) === 'search'"
      @update:model-value="emit('update-field', field.key, $event)"
      @open="normalizeInputType(field.input_type) === 'search' && emit('open-search', field)"
    />
  </section>
</template>
