const {ref, watch, onBeforeMount, h} = Vue;
const {useStore} = Vuex;
const {ElMessageBox} = ElementPlus;

export default {
  name: 'TopNavbar',
  setup() {
    const store = useStore();

    const requestForm = ref({});

    const setRequestForm = () => {
      requestForm.value = {...store.getters['requestForm']};
    };

    onBeforeMount(setRequestForm);
    watch(() => JSON.stringify(store.getters['requestForm']), setRequestForm);

    const updateRequestForm = () => {
      store.commit('setRequestForm', {...requestForm.value});
    };

    const onClickNewRequest = async () => {
      const res = await ElMessageBox.prompt('Please enter the URL to request', 'Request', {
        type: 'info',
        icon: h('i', {class: 'fa fa-paper-plane', style: 'font-size: 16px'}),
        customStyle: {
          maxWidth: '640px',
        },
        inputPlaceholder: 'Request URL',
        confirmButtonText: 'Submit',
      });
      await store.dispatch('postRequest', {url: res.value});
    };

    return {
      requestForm,
      updateRequestForm,
      onClickNewRequest,
    };
  },
  template: `<div class="top-navbar">
  <div class="logo-wrapper">
    <img src="/static/img/logo.svg">
  </div>
  <div class="new-request-wrapper">
    <el-button type="primary" icon="plus" @click="onClickNewRequest">
      New Request
    </el-button>
  </div>
  <div class="config-wrapper">
    <el-tooltip content="Request Method" placement="bottom">
      <el-icon size="12px" style="margin-right: 12px">
        <i class="fa fa-paper-plane"></i>
      </el-icon>
    </el-tooltip>
    <el-select v-model="requestForm.method" @change="updateRequestForm" style="width: 150px">
      <el-option label="Request" value="request"/>
      <el-option label="Rod (Browser)" value="rod"/>
    </el-select>
  </div>
</div>`
};
