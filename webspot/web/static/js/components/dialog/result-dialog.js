const {ref, computed} = Vue;
const {useStore} = Vuex;

import PlainListForm from '../form/plain-list-form.js';
import PaginationForm from '../form/pagination-form.js';

export default {
  name: 'ResultDialog',
  components: {
    PlainListForm,
    PaginationForm,
  },
  setup() {
    const store = useStore();

    const activeTabName = ref('overview');


    const dialogVisible = computed(() => store.state.activeResultDialogVisible);

    const detectorName = computed(() => store.getters['activeResultDetector']);

    const resultName = computed(() => store.getters['activeResultName']);

    const onDialogClose = () => {
      store.commit('resetActiveResult');
      store.commit('resetActiveResultTabName');
      store.commit('setActiveResultDialogVisible', false);
    };

    return {
      dialogVisible,
      detectorName,
      resultName,
      onDialogClose,
      activeTabName,
    };
  },
  template: `
<el-dialog
  :title="resultName"
   v-model="dialogVisible"
   @close="onDialogClose"
   width="80%"
>
  <plain-list-form
    v-if="detectorName === 'plain_list'"
  />
  <pagination-form
    v-else-if="detectorName === 'pagination'"
  />
</el-dialog>
`
};
