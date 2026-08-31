import { computed, ref, watch } from 'vue'

import { optionService } from '@/services/optionService'
import { useOptionCardContext } from '@/composables/option-page/useOptionCardContext'

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'label', label: '값', sortable: true },
  { key: 'actions', label: '작업', sortable: false },
]

export const useMenuTable = () => {
  const { sourceKey, refreshToken, requestRefresh } = useOptionCardContext()

  const loading = ref(false)
  const saving = ref(false)
  const errorMessage = ref('')

  const items = ref([])
  const editingId = ref(null)
  const editingLabel = ref('')

  const sortedItems = computed(() => {
    return [...items.value].sort((a, b) => String(a?.label || '').localeCompare(String(b?.label || '')))
  })

  const loadItems = async () => {
    loading.value = true
    errorMessage.value = ''

    try {
      const data = await optionService.getItems(sourceKey.value)
      items.value = Array.isArray(data?.items) ? data.items : []
    } catch {
      items.value = []
      errorMessage.value = '옵션 데이터를 불러오지 못했습니다.'
    } finally {
      loading.value = false
    }
  }

  const startEdit = (item) => {
    editingId.value = Number(item?.id)
    editingLabel.value = String(item?.label || '')
  }

  const cancelEdit = () => {
    editingId.value = null
    editingLabel.value = ''
  }

  const saveEdit = async (itemId) => {
    const trimmed = editingLabel.value.trim()
    if (!trimmed) {
      return
    }

    saving.value = true
    errorMessage.value = ''

    try {
      await optionService.updateItem(sourceKey.value, Number(itemId), trimmed)
      cancelEdit()
      requestRefresh()
    } catch (error) {
      errorMessage.value = error?.response?.data?.detail || '옵션 수정에 실패했습니다.'
    } finally {
      saving.value = false
    }
  }

  const deleteItem = async (item) => {
    const ok = window.confirm(`'${item.label}' 항목을 삭제할까요?`)
    if (!ok) {
      return
    }

    saving.value = true
    errorMessage.value = ''

    try {
      await optionService.deleteItem(sourceKey.value, Number(item.id))
      requestRefresh()
    } catch (error) {
      errorMessage.value = error?.response?.data?.detail || '옵션 삭제에 실패했습니다.'
    } finally {
      saving.value = false
    }
  }

  watch(
    () => [sourceKey.value, refreshToken.value],
    async () => {
      await loadItems()
    },
    { immediate: true }
  )

  return {
    columns,
    loading,
    saving,
    errorMessage,
    sortedItems,
    editingId,
    editingLabel,
    startEdit,
    cancelEdit,
    saveEdit,
    deleteItem,
  }
}