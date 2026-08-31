import { computed, ref } from 'vue'

import { optionService } from '@/services/optionService'
import { useOptionCardContext } from '@/composables/option-page/useOptionCardContext'

export const useAddMenu = () => {
  const { sourceKey, requestRefresh } = useOptionCardContext()

  const newLabel = ref('')
  const saving = ref(false)
  const errorMessage = ref('')

  const canSubmit = computed(() => newLabel.value.trim().length > 0)

  const submit = async () => {
    const trimmed = newLabel.value.trim()
    if (!trimmed) {
      return
    }

    saving.value = true
    errorMessage.value = ''

    try {
      await optionService.createItem(sourceKey.value, trimmed)
      newLabel.value = ''
      requestRefresh()
    } catch (error) {
      errorMessage.value = error?.response?.data?.detail || '옵션 추가에 실패했습니다.'
    } finally {
      saving.value = false
    }
  }

  return {
    newLabel,
    saving,
    errorMessage,
    canSubmit,
    submit,
  }
}