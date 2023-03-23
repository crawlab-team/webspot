const {ref, computed, watch} = Vue;
const {useStore} = Vuex;
const {ElMessage} = ElementPlus;

export const useBaseForm = () => {
  const store = useStore();

  const activeTabName = ref(store.state.activeResultTabName);
  watch(() => store.state.activeResultTabName, () => {
    activeTabName.value = store.state.activeResultTabName;
  });
  const onTabChange = (value) => {
    store.commit('setActiveResultTabName', value);
  };

  const result = computed(() => store.state.activeResult);

  const selectorType = ref('css');

  const onCopy = async (text) => {
    await navigator.clipboard.writeText(text);
    await ElMessage({message: 'Copied to clipboard', duration: 1000});
  };


  return {
    activeTabName,
    onTabChange,
    result,
    selectorType,
    onCopy,
  };
};

export default {
  name: 'BaseForm',
  setup() {
    return useBaseForm();
  },
  template: `
<el-tabs v-model="activeTabName" @tab-change="onTabChange">
  <slot></slot>
</el-tabs>
`
};
