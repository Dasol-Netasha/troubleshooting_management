import { computed, ref } from 'vue'

import { optionService } from '@/services/optionService'

export const useDropdownOptionManager = () => {
  const loading = ref(false)
  const saving = ref(false)
  const errorMessage = ref('')

  const sources = ref([])
  const selectedSource = ref('')
  const items = ref([])

  const newLabel = ref('')
  const editingId = ref(null)
  const editingLabel = ref('')

  const selectedSourceLabel = computed(() => {
    const source = sources.value.find((item) => item.key === selectedSource.value)
    return source?.label || '-'
  })

  const sortedItems = computed(() => {
    return [...items.value].sort((a, b) => String(a?.label || '').localeCompare(String(b?.label || '')))
  })

  const canSubmitNew = computed(() => newLabel.value.trim().length > 0)

  const loadSources = async () => {
    loading.value = true
    errorMessage.value = ''

    try {
      const data = await optionService.getSources()
      const nextSources = Array.isArray(data?.sources) ? data.sources : []
      sources.value = nextSources

      if (!selectedSource.value || !nextSources.some((source) => source.key === selectedSource.value)) {
        selectedSource.value = nextSources[0]?.key || ''
      }

      await loadItems()
    } catch {
      errorMessage.value = '옵션 목록을 불러오지 못했습니다.'
      items.value = []
    } finally {
      loading.value = false
    }
  }

  const loadItems = async () => {
    if (!selectedSource.value) {
      items.value = []
      return
    }

    loading.value = true
    errorMessage.value = ''

    try {
      const data = await optionService.getItems(selectedSource.value)
      items.value = Array.isArray(data?.items) ? data.items : []
    } catch {
      errorMessage.value = '선택한 옵션 데이터를 불러오지 못했습니다.'
      items.value = []
    } finally {
      loading.value = false
    }
  }

  const changeSource = async (sourceKey) => {
    selectedSource.value = String(sourceKey || '')
    editingId.value = null
    editingLabel.value = ''
    await loadItems()
  }

  const createItem = async () => {
    const trimmed = newLabel.value.trim()
    if (!selectedSource.value || !trimmed) {
      return
    }

    saving.value = true
    errorMessage.value = ''

    try {
      await optionService.createItem(selectedSource.value, trimmed)
      newLabel.value = ''
      await loadItems()
    } catch (error) {
      errorMessage.value = error?.response?.data?.detail || '옵션 추가에 실패했습니다.'
    } finally {
      saving.value = false
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
    if (!selectedSource.value || !trimmed) {
      return
    }

    saving.value = true
    errorMessage.value = ''

    try {
      await optionService.updateItem(selectedSource.value, Number(itemId), trimmed)
      cancelEdit()
      await loadItems()
    } catch (error) {
      errorMessage.value = error?.response?.data?.detail || '옵션 수정에 실패했습니다.'
    } finally {
      saving.value = false
    }
  }

  const deleteItem = async (itemId) => {
    if (!selectedSource.value) {
      return
    }

    saving.value = true
    errorMessage.value = ''

    try {
      await optionService.deleteItem(selectedSource.value, Number(itemId))
      await loadItems()
    } catch (error) {
      errorMessage.value = error?.response?.data?.detail || '옵션 삭제에 실패했습니다.'
    } finally {
      saving.value = false
    }
  }

  return {
    loading,
    saving,
    errorMessage,
    sources,
    selectedSource,
    selectedSourceLabel,
    items,
    sortedItems,
    newLabel,
    editingId,
    editingLabel,
    canSubmitNew,
    loadSources,
    loadItems,
    changeSource,
    createItem,
    startEdit,
    cancelEdit,
    saveEdit,
    deleteItem,
  }
}
