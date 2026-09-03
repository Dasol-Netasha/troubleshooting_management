<script setup>
import Button from '@/components/atoms/Button.vue'
import Input from '@/components/atoms/Input.vue'
import DeleteIconBtn from '@/components/molecules/buttons/DeleteIconBtn.vue'
import EditIconBtn from '@/components/molecules/buttons/EditIconBtn.vue'
import DataTable from '@/components/organisms/table/DataTable.vue'
import { useMenuTable } from '@/composables/option-page/useMenuTable'

const {
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
} = useMenuTable()
</script>

<template>
  <p v-if="errorMessage" class="mb-2 rounded-md border border-rose-200 bg-rose-50 px-2 py-1 text-xs text-rose-700">
    {{ errorMessage }}
  </p>

  <DataTable
    row-key="id"
    :columns="columns"
    :rows="sortedItems"
    :loading="loading"
    empty-text="등록된 옵션이 없습니다."
  >
    <template #cell-label="{ row, value }">
      <div v-if="editingId === Number(row.id)" class="max-w-lg">
        <Input :model-value="editingLabel" @update:model-value="editingLabel = $event" />
      </div>
      <span v-else class="text-sm text-slate-800">{{ value }}</span>
    </template>

    <template #cell-actions="{ row }">
      <div class="flex flex-wrap items-center gap-2">
        <template v-if="editingId === Number(row.id)">
          <Button size="sm" :disabled="saving || loading || !editingLabel.trim()" @click="saveEdit(row.id)">저장</Button>
          <Button size="sm" variant="secondary" :disabled="saving" @click="cancelEdit">취소</Button>
        </template>

        <template v-else>
          <EditIconBtn size="sm" :disabled="saving || loading" @click="startEdit(row)" />
          <DeleteIconBtn size="sm" outlined :disabled="saving || loading" @click="deleteItem(row)" />
        </template>
      </div>
    </template>
  </DataTable>
</template>
