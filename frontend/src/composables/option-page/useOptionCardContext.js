import { inject, provide, ref } from 'vue'

const OPTION_CARD_CONTEXT_KEY = Symbol('option-card-context')

export const provideOptionCardContext = ({ sourceKey, sourceLabel }) => {
  const refreshToken = ref(0)

  const requestRefresh = () => {
    refreshToken.value += 1
  }

  provide(OPTION_CARD_CONTEXT_KEY, {
    sourceKey,
    sourceLabel,
    refreshToken,
    requestRefresh,
  })
}

export const useOptionCardContext = () => {
  const context = inject(OPTION_CARD_CONTEXT_KEY, null)
  if (!context) {
    throw new Error('Option card context is not provided')
  }
  return context
}