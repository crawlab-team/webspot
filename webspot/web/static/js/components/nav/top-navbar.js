const {ref, watch, onBeforeMount, h, computed} = Vue;
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

    const activeRequest = computed(() => store.getters['activeRequest']);

    const onClickRetry = async () => {
      await ElMessageBox.confirm('Are you sure to retry?', 'Retry');
      store.dispatch('postRequest', {
        url: store.getters['activeRequest'].url,
      });
    };

    const mode = ref('highlight');
    onBeforeMount(() => {
      mode.value = store.getters.previewMode;
    });
    watch(() => mode.value, () => {
      store.commit('setPreviewMode', mode.value);
    });

    return {
      requestForm,
      updateRequestForm,
      onClickNewRequest,
      activeRequest,
      onClickRetry,
      mode,
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
  <div class="config-wrapper" style="display: none;">
    <el-tooltip content="Request Method" placement="bottom">
      <el-icon size="12px" style="margin-right: 12px">
        <i class="fa fa-paper-plane"></i>
      </el-icon>
    </el-tooltip>
    <el-select v-model="requestForm.method" @change="updateRequestForm" style="width: 150px;">
      <el-option label="Request" value="request"/>
      <el-option label="Rod (Browser)" value="rod"/>
    </el-select>
  </div>
  <el-button type="warning" style="margin-left: 6px" icon="refresh" @click="onClickRetry" :disabled="!activeRequest">
    Retry
  </el-button>
  <el-radio-group v-model="mode" style="margin-left: 12px; display: none">
    <el-radio-button label="highlight">Highlight</el-radio-button>
    <el-radio-button label="annotate">Annotate</el-radio-button>
  </el-radio-group>
</div>`
};
