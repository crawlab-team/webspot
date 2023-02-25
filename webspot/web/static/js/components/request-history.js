const {ref, computed} = Vue;
const {useStore} = Vuex;
const {ElMessageBox} = ElementPlus;

export default {
  setup() {
    const store = useStore();

    const requests = computed(() => store.state.requests);

    const isCollapsed = ref(false);

    const onClickNewRequest = async () => {
      const res = await ElMessageBox.prompt('Please enter the URL to request');
      await store.dispatch('postRequest', {url: res.value});
    };

    const getRequestDataByStatus = (request) => {
      switch (request.status) {
        case 'pending':
          return {
            icon: 'fa fa-spinner fa-spin',
            color: 'var(--color-orange)',
          };
        case 'success':
          return {
            icon: 'fa fa-check',
            color: 'var(--color-green)',
          };
        case 'error':
          return {
            icon: 'fa fa-times',
            color: 'var(--color-red)',
          };
      }
    };

    const activeRequestId = computed(() => store.state.activeRequestId);

    const onClickRequest = (request) => {
      store.commit('setActiveRequestId', request._id);
    };

    return {
      requests,
      isCollapsed,
      getRequestDataByStatus,
      onClickNewRequest,
      activeRequestId,
      onClickRequest,
    };
  },
  template: `
<div class="request-history" style="flex: 0 0 240px">
  <el-menu :default-active="activeRequestId" v-model="" style="height: 100%">
    <el-menu-item class="new-request" style="background: inherit">
      <el-button type="primary" @click="onClickNewRequest">
        New Request
      </el-button>
    </el-menu-item>
    <el-menu-item v-for="(request, $index) in requests" :key="$index" :index="request._id" @click="() => onClickRequest(request)">
      <el-icon size="12">
        <i :class="getRequestDataByStatus(request).icon" :style="{color: getRequestDataByStatus(request).color}"></i>
      </el-icon>
      <el-tooltip :content="'URL: ' + request.url" placement="right">
        <span>{{ request.url }}</span>
      </el-tooltip>
    </el-menu-item>
  </el-menu>
</div>
`
};
